"""Data maintenance: retention is explicit, bounded and testable.

Growth control matters here because two tables accumulate without a learner asking: login attempts
and sessions. The retention numbers are policy; the behaviour (what is deleted, what is kept, that a
dry run changes nothing, that a second run is a no-op) is what these tests pin down.
"""

from __future__ import annotations

from datetime import timedelta

from app.db import session_scope
from app.maintenance import (
    LOGIN_ATTEMPT_RETENTION_DAYS,
    SESSION_RETENTION_DAYS_AFTER_EXPIRY,
    prune_sessions,
    run_maintenance,
)
from app.models import LoginAttempt, RegistrationAttempt, RegistrationIpGuard, Session
from app.security import (
    prune_login_attempts,
    prune_registration_attempts,
    prune_registration_ip_guards,
)
from app.utils import utcnow
from tests.conftest import register


def _seed_attempts(db, *, old: int, recent: int, now) -> None:
    for index in range(old):
        db.add(
            LoginAttempt(
                email=f"old{index}@example.com",
                ip="203.0.113.9",
                succeeded=False,
                attempted_at=now - timedelta(days=LOGIN_ATTEMPT_RETENTION_DAYS + 1 + index),
            )
        )
    for index in range(recent):
        db.add(
            LoginAttempt(
                email=f"recent{index}@example.com",
                ip="203.0.113.9",
                succeeded=False,
                attempted_at=now - timedelta(days=1 + index),
            )
        )
    db.commit()


def _seed_sessions(db, user_id: str, *, old: int, recent: int, now) -> None:
    for index in range(old):
        db.add(
            Session(
                user_id=user_id,
                token_hash=f"old-hash-{index}",
                created_at=now - timedelta(days=200 + index),
                expires_at=now - timedelta(days=SESSION_RETENTION_DAYS_AFTER_EXPIRY + 1 + index),
            )
        )
    for index in range(recent):
        db.add(
            Session(
                user_id=user_id,
                token_hash=f"recent-hash-{index}",
                created_at=now - timedelta(days=1),
                expires_at=now + timedelta(days=1 + index),
            )
        )
    db.commit()


def test_login_attempt_pruning_keeps_recent_rows_and_drops_stale_ones(client) -> None:
    register(client, email="maintenance@example.com")
    now = utcnow()
    with session_scope() as db:
        _seed_attempts(db, old=3, recent=2, now=now)
        before = db.query(LoginAttempt).count()
        pruned = prune_login_attempts(db, now=now)
        db.commit()
        after = db.query(LoginAttempt).count()

    assert before == 5 and pruned == 3 and after == 2, "retention must be exact, not approximate"


def test_session_pruning_is_scoped_to_expired_or_revoked_rows(client) -> None:
    register(client, email="session-prune@example.com")
    now = utcnow()
    with session_scope() as db:
        from app.models import User

        user_id = db.query(User).filter(User.email == "session-prune@example.com").one().id
        _seed_sessions(db, user_id, old=2, recent=2, now=now)
        pruned = prune_sessions(db, now=now)
        db.commit()
        remaining = [row.token_hash for row in db.query(Session).all()]

    assert pruned == 2
    assert "recent-hash-0" in remaining and "recent-hash-1" in remaining
    assert not [token for token in remaining if token.startswith("old-hash-")]


def test_a_dry_run_reports_without_deleting(client) -> None:
    register(client, email="dry-run@example.com")
    now = utcnow()
    with session_scope() as db:
        _seed_attempts(db, old=2, recent=1, now=now)
        report = run_maintenance(db, dry_run=True, now=now)
        db.rollback()
    with session_scope() as db:
        remaining = db.query(LoginAttempt).count()
        sessions = db.query(Session).count()

    assert report.dry_run is True
    assert report.login_attempts_pruned == 2
    assert remaining == 3, "a dry run must not delete anything"
    assert sessions >= 1, "the registering learner's session must survive a dry run"


def test_running_maintenance_twice_is_a_no_op(client) -> None:
    register(client, email="idempotent@example.com")
    now = utcnow()
    with session_scope() as db:
        _seed_attempts(db, old=2, recent=1, now=now)
        first = run_maintenance(db, now=now)
        db.commit()
    with session_scope() as db:
        second = run_maintenance(db, now=now)
        db.commit()

    assert first.login_attempts_pruned == 2
    assert second.login_attempts_pruned == 0
    assert second.sessions_pruned == 0


def test_registration_attempt_pruning_keeps_recent_rows_and_drops_stale_ones(client) -> None:
    now = utcnow()
    with session_scope() as db:
        for index in range(3):
            db.add(
                RegistrationAttempt(
                    ip="203.0.113.9",
                    attempted_at=now - timedelta(days=LOGIN_ATTEMPT_RETENTION_DAYS + 1 + index),
                )
            )
        for index in range(2):
            db.add(RegistrationAttempt(ip="203.0.113.9", attempted_at=now - timedelta(hours=1 + index)))
        db.commit()
        pruned = prune_registration_attempts(db, now=now)
        db.commit()
        remaining = db.query(RegistrationAttempt).count()

    assert pruned == 3 and remaining == 2, "retention must be exact, not approximate"


def test_registration_ip_guard_pruning_keeps_recent_addresses_and_drops_stale_ones(client) -> None:
    now = utcnow()
    with session_scope() as db:
        db.add(
            RegistrationIpGuard(
                ip="203.0.113.8", updated_at=now - timedelta(days=LOGIN_ATTEMPT_RETENTION_DAYS + 1)
            )
        )
        db.add(RegistrationIpGuard(ip="203.0.113.9", updated_at=now - timedelta(hours=1)))
        db.commit()
        pruned = prune_registration_ip_guards(db, now=now)
        db.commit()
        remaining = [row.ip for row in db.query(RegistrationIpGuard).all()]

    assert pruned == 1 and remaining == ["203.0.113.9"], "a fresh address must keep its guard row"


def test_run_maintenance_reports_and_prunes_registration_guards(client) -> None:
    now = utcnow()
    with session_scope() as db:
        db.add(RegistrationIpGuard(ip="203.0.113.8", updated_at=now - timedelta(days=40)))
        db.commit()
        report = run_maintenance(db, now=now)
        db.commit()

    assert report.registration_ip_guards_pruned == 1
    assert report.as_dict()["registration_ip_guards_pruned"] == 1
    with session_scope() as db:
        assert db.query(RegistrationIpGuard).count() == 0


def test_audit_rows_are_not_pruned_by_maintenance(client) -> None:
    """Audit retention is an owner policy decision, not something a housekeeping default decides."""
    from app.models import AuditLog

    register(client, email="audit-kept@example.com")
    with session_scope() as db:
        before = db.query(AuditLog).count()
        run_maintenance(db, now=utcnow())
        db.commit()
        after = db.query(AuditLog).count()
    assert before == after
