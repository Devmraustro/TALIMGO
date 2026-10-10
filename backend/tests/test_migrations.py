"""Migration and persistence checks.

Runs the documented production path — ``alembic upgrade head`` against an empty database — and then
proves the application can use the migrated schema (curriculum load + a learner round-trip). This
catches the class of bug where models and migrations drift apart.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect

BACKEND = Path(__file__).resolve().parents[1]


def _alembic_config(database_url: str) -> Config:
    config = Config(str(BACKEND / "alembic.ini"))
    config.set_main_option("script_location", str(BACKEND / "migrations"))
    config.set_main_option("sqlalchemy.url", database_url)
    return config


def test_migrations_apply_to_an_empty_database(tmp_path, monkeypatch) -> None:
    database_url = f"sqlite:///{tmp_path / 'migration.db'}"
    monkeypatch.setenv("TALIMGO_DATABASE_URL", database_url)

    from app.config import reset_settings_cache

    reset_settings_cache()
    command.upgrade(_alembic_config(database_url), "head")
    reset_settings_cache()

    tables = set(inspect(create_engine(database_url)).get_table_names())
    for expected in (
        "users",
        "sessions",
        "profiles",
        "consent_records",
        "goals",
        "objectives",
        "lessons",
        "items",
        "diagnostic_attempts",
        "diagnostic_responses",
        "learner_evidence",
        "mastery_estimates",
        "plans",
        "plan_weeks",
        "plan_items",
        "practice_sessions",
        "practice_responses",
        "tutor_threads",
        "tutor_messages",
        "ai_usage",
        "audit_log",
    ):
        assert expected in tables, f"table {expected} missing after migration"


def test_migration_is_idempotent(tmp_path, monkeypatch) -> None:
    database_url = f"sqlite:///{tmp_path / 'idempotent.db'}"
    monkeypatch.setenv("TALIMGO_DATABASE_URL", database_url)

    from app.config import reset_settings_cache

    reset_settings_cache()
    command.upgrade(_alembic_config(database_url), "head")
    command.upgrade(_alembic_config(database_url), "head")  # must be a no-op, not an error
    reset_settings_cache()


def test_migrated_database_supports_the_application(tmp_path, monkeypatch) -> None:
    """Load the authored curriculum into a migrated database and record one evidence row."""
    database_url = f"sqlite:///{tmp_path / 'used.db'}"
    monkeypatch.setenv("TALIMGO_DATABASE_URL", database_url)
    monkeypatch.setenv("TALIMGO_ENV", "test")

    from app.config import reset_settings_cache
    from app.db import get_engine, reset_engine, session_scope
    from app.models import Evidence, Item, MasteryEstimate, User

    reset_settings_cache()
    reset_engine()
    command.upgrade(_alembic_config(database_url), "head")

    from app.curriculum.loader import load_all
    from app.services.progress import recompute_mastery

    with session_scope() as db:
        counts = load_all(db)
        assert counts["objectives"] == 12
        assert counts["items"] == 36
        assert db.query(Item).count() == 36

        user = User(email="migration@example.com", password_hash="x", display_name="M")
        db.add(user)
        db.flush()
        db.add(
            Evidence(
                user_id=user.id,
                objective_id="py:values",
                outcome="success",
                assisted=False,
                kind="practice",
            )
        )
        db.flush()
        estimates = recompute_mastery(db, user.id)
        db.commit()

        assert "py:values" in estimates
        assert db.query(MasteryEstimate).count() == 1

    reset_engine()
    reset_settings_cache()
    del get_engine


def test_downgrade_and_upgrade_round_trip(tmp_path, monkeypatch) -> None:
    """A migration that cannot be reversed is a migration we cannot roll back in production."""
    database_url = f"sqlite:///{tmp_path / 'roundtrip.db'}"
    monkeypatch.setenv("TALIMGO_DATABASE_URL", database_url)

    from app.config import reset_settings_cache

    reset_settings_cache()
    config = _alembic_config(database_url)
    command.upgrade(config, "head")
    command.downgrade(config, "base")
    tables = set(inspect(create_engine(database_url)).get_table_names())
    assert "users" not in tables
    command.upgrade(config, "head")
    reset_settings_cache()


def test_alembic_cli_reports_the_head_revision(tmp_path, monkeypatch) -> None:
    """The documented command must work in a fresh shell, not only through the Python API."""
    database_url = f"sqlite:///{tmp_path / 'cli.db'}"
    env = {
        "PATH": "/usr/bin:/bin",
        "TALIMGO_ENV": "test",
        "TALIMGO_DATABASE_URL": database_url,
        "PYTHONPATH": str(BACKEND),
    }
    # Invoke Alembic through the interpreter running the tests, so this works in any environment
    # (virtualenv, system install, CI) instead of assuming a specific layout under backend/.
    completed = subprocess.run(  # fixed argv, no shell
        [sys.executable, "-m", "alembic", "upgrade", "head"],
        cwd=BACKEND,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    assert completed.returncode == 0, completed.stderr
