"""Authentication primitives: password hashing, session tokens, login rate limiting.

Decisions (see docs/SECURITY_THREAT_MODEL.md):
  * Passwords: bcrypt cost 12 over a SHA-256 pre-hash. The pre-hash removes bcrypt's 72-byte
    truncation problem for long passphrases without weakening the work factor.
  * Session tokens: 256-bit random values, stored only as SHA-256 hashes. A database leak does
    not yield usable session tokens.
  * Login attempts are recorded and counted per email and per IP; both lock out temporarily.
  * Registration attempts are counted per IP inside a rolling hour, so one address cannot mass-
    create accounts (threat T15); the counting works across workers because it is in the database,
    and the per-IP guard row makes concurrent decisions serialise instead of overshooting.
"""

from __future__ import annotations

import hashlib
import hmac
import secrets
from datetime import datetime, timedelta

import bcrypt
from sqlalchemy import func, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session as DbSession

from app.config import Settings
from app.models import LoginAttempt, RegistrationAttempt, RegistrationIpGuard
from app.utils import ensure_aware, utcnow

BCRYPT_ROUNDS = 12
SESSION_TOKEN_BYTES = 32
REGISTRATION_WINDOW_MINUTES = 60


def _prehash(password: str) -> bytes:
    return hashlib.sha256(password.encode("utf-8")).digest()


def hash_password(password: str) -> str:
    return bcrypt.hashpw(_prehash(password), bcrypt.gensalt(rounds=BCRYPT_ROUNDS)).decode("ascii")


def verify_password(password: str, password_hash: str) -> bool:
    try:
        return bcrypt.checkpw(_prehash(password), password_hash.encode("ascii"))
    except (ValueError, TypeError):
        # A malformed stored hash must never authenticate anyone.
        return False


def new_session_token() -> tuple[str, str]:
    """Return ``(token, token_hash)``. Only the hash is persisted."""
    token = secrets.token_urlsafe(SESSION_TOKEN_BYTES)
    return token, hash_session_token(token)


def hash_session_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def constant_time_equals(left: str, right: str) -> bool:
    return hmac.compare_digest(left.encode("utf-8"), right.encode("utf-8"))


def password_problems(password: str, settings: Settings) -> list[str]:
    """Return human-readable reasons the password is unacceptable (empty list = accepted)."""
    problems: list[str] = []
    if len(password) < settings.min_password_length:
        problems.append(f"Password must be at least {settings.min_password_length} characters.")
    if password.lower() in {"password", "password123", "12345678", "qwertyuiop", "talimgo123"}:
        problems.append("Password is too common.")
    if password.strip() != password:
        problems.append("Password must not start or end with whitespace.")
    return problems


def record_login_attempt(db: DbSession, *, email: str, ip: str, succeeded: bool) -> None:
    db.add(LoginAttempt(email=email.lower().strip(), ip=ip[:64], succeeded=succeeded))
    db.flush()


def login_locked(db: DbSession, *, email: str, ip: str, settings: Settings, now: datetime) -> bool:
    """True when recent failed attempts exceed the configured threshold for this email or IP."""
    since = now - timedelta(minutes=settings.login_lockout_minutes)
    threshold = settings.max_login_attempts
    for column, value in ((LoginAttempt.email, email.lower().strip()), (LoginAttempt.ip, ip)):
        if not value:
            continue
        failures = db.scalar(
            select(func.count())
            .select_from(LoginAttempt)
            .where(
                column == value,
                LoginAttempt.succeeded.is_(False),
                LoginAttempt.attempted_at >= since,
            )
        )
        if (failures or 0) >= threshold:
            return True
    return False


def registration_retry_after(db: DbSession, *, ip: str, settings: Settings, now: datetime) -> int | None:
    """Seconds until this IP may register again, or None when it is under the cap.

    Like :func:`login_locked`, the count is plain database rows, so concurrent workers share one
    allowance. Call this only while holding the per-IP guard (see :func:`claim_registration_slot`);
    on its own, a plain check-then-insert would let every concurrently in-flight request from one
    address read the same below-cap count and each record an attempt.
    """
    since = now - timedelta(minutes=REGISTRATION_WINDOW_MINUTES)
    attempts = db.scalar(
        select(func.count())
        .select_from(RegistrationAttempt)
        .where(RegistrationAttempt.ip == ip[:64], RegistrationAttempt.attempted_at >= since)
    )
    if (attempts or 0) < settings.registrations_per_ip_per_hour:
        return None
    oldest = db.scalar(
        select(func.min(RegistrationAttempt.attempted_at)).where(
            RegistrationAttempt.ip == ip[:64], RegistrationAttempt.attempted_at >= since
        )
    )
    if oldest is None:
        return 1
    exit_at = ensure_aware(oldest) + timedelta(minutes=REGISTRATION_WINDOW_MINUTES)
    return max(1, int((exit_at - ensure_aware(now)).total_seconds()) + 1)


def claim_registration_slot(db: DbSession, *, ip: str, settings: Settings, now: datetime) -> int | None:
    """Serialise same-IP decisions, then record the attempt or report when the cap is reached.

    Returns None when the attempt row has been recorded (the caller commits), or the Retry-After
    seconds when this IP is over the rolling-hour cap (nothing is recorded, and the caller raises).

    The guard row makes the decision safe under concurrency the same way the per-user write limit
    and the AI quota are safe: a write on one known row. Every request from one address updates
    that address's single ``registration_ip_guards`` row first; on both SQLite and PostgreSQL a
    concurrent update on the same row blocks until the holder commits or rolls back, so the
    rolling-window count that follows is taken against settled state and the cap is exact.
    """
    key = ip[:64]
    for _ in range(3):
        touched = db.execute(
            update(RegistrationIpGuard).where(RegistrationIpGuard.ip == key).values(updated_at=now)
        ).rowcount
        if touched:
            break
        try:
            with db.begin_nested():
                db.add(RegistrationIpGuard(ip=key, updated_at=now))
            db.flush()
            break
        except IntegrityError:
            continue  # another request created the guard row first; retry the update
    else:
        raise RuntimeError("could not serialise the registration decision for this address")

    retry_after = registration_retry_after(db, ip=key, settings=settings, now=now)
    if retry_after is None:
        record_registration_attempt(db, ip=key)
    return retry_after


def record_registration_attempt(db: DbSession, *, ip: str) -> None:
    db.add(RegistrationAttempt(ip=ip[:64]))
    db.flush()


def prune_login_attempts(db: DbSession, *, older_than_days: int = 30, now: datetime | None = None) -> int:
    """Housekeeping: drop stale attempt rows so the table cannot grow without bound."""
    cutoff = (now or utcnow()) - timedelta(days=older_than_days)
    stale = db.scalars(select(LoginAttempt).where(LoginAttempt.attempted_at < cutoff)).all()
    for row in stale:
        db.delete(row)
    return len(stale)


def prune_registration_attempts(
    db: DbSession, *, older_than_days: int = 30, now: datetime | None = None
) -> int:
    """Housekeeping: registration attempts only matter inside the recent abuse window."""
    cutoff = (now or utcnow()) - timedelta(days=older_than_days)
    stale = db.scalars(select(RegistrationAttempt).where(RegistrationAttempt.attempted_at < cutoff)).all()
    for row in stale:
        db.delete(row)
    return len(stale)


def prune_registration_ip_guards(
    db: DbSession, *, older_than_days: int = 30, now: datetime | None = None
) -> int:
    """Housekeeping: guard rows are recreated on demand, so stale addresses cost nothing to drop."""
    cutoff = (now or utcnow()) - timedelta(days=older_than_days)
    stale = db.scalars(select(RegistrationIpGuard).where(RegistrationIpGuard.updated_at < cutoff)).all()
    for row in stale:
        db.delete(row)
    return len(stale)


def session_is_active(expires_at: datetime, revoked_at: datetime | None, now: datetime) -> bool:
    if revoked_at is not None:
        return False
    return ensure_aware(expires_at) > ensure_aware(now)
