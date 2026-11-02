"""Synchronise authored curriculum into an already-migrated database.

Run deliberately after ``alembic upgrade head`` during a release:

    python scripts/load_curriculum.py

The loader upserts stable content identifiers and does not delete learner data. This command never
creates or upgrades schema: a database that is not at the repository's Alembic head is refused.
Output contains content counts only, never configuration values or database credentials.
"""

from __future__ import annotations

from pathlib import Path

from alembic.config import Config
from alembic.migration import MigrationContext
from alembic.script import ScriptDirectory
from sqlalchemy.engine import Engine

BACKEND = Path(__file__).resolve().parents[1]
SCHEMA_REFUSAL = (
    "Refusing to load curriculum: the database is not at the repository's Alembic head. "
    "Run `alembic upgrade head` against the verified TALIMGO database first."
)


def _repository_heads() -> set[str]:
    config = Config(str(BACKEND / "alembic.ini"))
    config.set_main_option("script_location", str(BACKEND / "migrations"))
    return set(ScriptDirectory.from_config(config).get_heads())


def require_current_schema(engine: Engine) -> None:
    """Refuse empty, manually-created, stale, or otherwise non-head schemas."""
    with engine.connect() as connection:
        current_heads = set(MigrationContext.configure(connection).get_current_heads())
    if not current_heads or current_heads != _repository_heads():
        raise SystemExit(SCHEMA_REFUSAL)


def main() -> None:
    from app.curriculum.loader import load_all
    from app.db import get_engine, session_scope

    require_current_schema(get_engine())
    with session_scope() as db:
        counts = load_all(db)

    summary = " ".join(
        f"{name}={counts[name]}" for name in ("paths", "objectives", "lessons", "items", "projects")
    )
    print(f"Curriculum load complete: {summary}")


if __name__ == "__main__":
    main()
