"""Data maintenance: bounded growth for the tables that only ever accumulate.

Three tables grow without a learner ever asking them to: ``login_attempts`` (one row per attempt,
successful or not), ``registration_attempts`` (one row per accepted registration request) and
``sessions`` (one row per sign-in, kept after it expires or is revoked so the audit trail and
"signed-in devices" style features stay possible). None is interesting after a while, so retention
is explicit, documented and enforceable from one command:

    # See what would happen, change nothing
    python -m app.maintenance --dry-run

    # Apply it (safe to run from cron; idempotent)
    python -m app.maintenance

Retention defaults, and why:

* **Login attempts: 30 days.** Long enough to investigate a brute-force campaign across a month of
  logs, short enough that the table stays proportional to recent activity rather than to uptime.
* **Registration attempts: 30 days.** Same reasoning as login attempts: the per-IP guard reads only
  the last hour, and the rows exist for investigating registration campaigns.
* **Sessions: 30 days after expiry or revocation.** A session that expired yesterday may still be
  needed to answer "was that me?"; one that expired last month is noise.

Audit records (``audit_log``) are deliberately **not** pruned here: they are the accountability trail
for account deletion and admin actions, and their retention is a policy decision for the owner
(documented in docs/DEPLOYMENT.md) rather than a default this module should silently apply.
"""

from __future__ import annotations

import argparse
import logging
from dataclasses import dataclass
from datetime import timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session as DbSession

from app.db import session_scope
from app.models import Session
from app.security import (
    prune_login_attempts,
    prune_registration_attempts,
    prune_registration_ip_guards,
)
from app.utils import ensure_aware, utcnow

logger = logging.getLogger("talimgo.maintenance")

LOGIN_ATTEMPT_RETENTION_DAYS = 30
REGISTRATION_ATTEMPT_RETENTION_DAYS = 30
SESSION_RETENTION_DAYS_AFTER_EXPIRY = 30


@dataclass(frozen=True)
class MaintenanceReport:
    login_attempts_pruned: int
    registration_attempts_pruned: int
    registration_ip_guards_pruned: int
    sessions_pruned: int
    dry_run: bool

    def as_dict(self) -> dict[str, int | bool]:
        return {
            "login_attempts_pruned": self.login_attempts_pruned,
            "registration_attempts_pruned": self.registration_attempts_pruned,
            "registration_ip_guards_pruned": self.registration_ip_guards_pruned,
            "sessions_pruned": self.sessions_pruned,
            "dry_run": self.dry_run,
        }


def prune_sessions(
    db: DbSession,
    *,
    older_than_days: int = SESSION_RETENTION_DAYS_AFTER_EXPIRY,
    now=None,
) -> int:
    """Delete sessions that expired (or were revoked) more than ``older_than_days`` ago."""
    moment = now or utcnow()
    cutoff = moment - timedelta(days=older_than_days)
    rows = db.scalars(
        select(Session).where(
            Session.expires_at < cutoff,
            (Session.revoked_at.is_(None)) | (Session.revoked_at < cutoff),
        )
    ).all()
    for row in rows:
        db.delete(row)
    return len(rows)


def run_maintenance(
    db: DbSession,
    *,
    dry_run: bool = False,
    login_attempt_retention_days: int = LOGIN_ATTEMPT_RETENTION_DAYS,
    registration_attempt_retention_days: int = REGISTRATION_ATTEMPT_RETENTION_DAYS,
    session_retention_days: int = SESSION_RETENTION_DAYS_AFTER_EXPIRY,
    now=None,
) -> MaintenanceReport:
    """Count (and, unless ``dry_run``, delete) stale rows. Never commits: the caller decides."""
    moment = ensure_aware(now) if now is not None else utcnow()
    attempts = prune_login_attempts(db, older_than_days=login_attempt_retention_days, now=moment)
    registrations = prune_registration_attempts(
        db, older_than_days=registration_attempt_retention_days, now=moment
    )
    # The per-IP guard rows share the registration retention: they are recreated on demand, so
    # dropping addresses that have not tried to register for a month costs nothing.
    guards = prune_registration_ip_guards(db, older_than_days=registration_attempt_retention_days, now=moment)
    sessions = prune_sessions(db, older_than_days=session_retention_days, now=moment)
    if dry_run:
        db.rollback()
    return MaintenanceReport(
        login_attempts_pruned=attempts,
        registration_attempts_pruned=registrations,
        registration_ip_guards_pruned=guards,
        sessions_pruned=sessions,
        dry_run=dry_run,
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="TALIMGO data maintenance")
    parser.add_argument("--dry-run", action="store_true", help="report what would be deleted")
    parser.add_argument(
        "--login-attempt-days", type=int, default=LOGIN_ATTEMPT_RETENTION_DAYS, help="retention"
    )
    parser.add_argument(
        "--registration-attempt-days",
        type=int,
        default=REGISTRATION_ATTEMPT_RETENTION_DAYS,
        help="retention",
    )
    parser.add_argument(
        "--session-days", type=int, default=SESSION_RETENTION_DAYS_AFTER_EXPIRY, help="retention"
    )
    args = parser.parse_args(argv)

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    with session_scope() as db:
        report = run_maintenance(
            db,
            dry_run=args.dry_run,
            login_attempt_retention_days=args.login_attempt_days,
            registration_attempt_retention_days=args.registration_attempt_days,
            session_retention_days=args.session_days,
        )
    logger.info("maintenance finished: %s", report.as_dict())
    return 0


if __name__ == "__main__":  # pragma: no cover - exercised through main() in tests
    raise SystemExit(main())
