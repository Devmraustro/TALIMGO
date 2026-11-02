"""Operator-path checks for deliberate curriculum loading after migrations."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from sqlalchemy import create_engine, func, inspect, select
from sqlalchemy.orm import Session

BACKEND = Path(__file__).resolve().parents[1]


def _environment(database_url: str) -> dict[str, str]:
    env = os.environ.copy()
    env.pop("TALIMGO_ENV_FILE", None)
    env.pop("VERCEL_ENV", None)
    env.update(
        {
            "TALIMGO_ENV": "test",
            "TALIMGO_DATABASE_URL": database_url,
            "TALIMGO_SESSION_SECRET": "curriculum-script-test-secret",
            "TALIMGO_AI_ENABLED": "false",
            "PYTHONPATH": str(BACKEND),
        }
    )
    return env


def _run(arguments: list[str], database_url: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, *arguments],
        cwd=BACKEND,
        env=_environment(database_url),
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )


def _migrate(database_url: str, *arguments: str) -> None:
    completed = _run(["-m", "alembic", *arguments], database_url)
    assert completed.returncode == 0, completed.stderr


def _load_curriculum(database_url: str) -> subprocess.CompletedProcess[str]:
    return _run(["scripts/load_curriculum.py"], database_url)


def test_load_refuses_a_database_without_migrations(tmp_path) -> None:
    database_url = f"sqlite:///{tmp_path / 'unmigrated.db'}"

    refused = _load_curriculum(database_url)

    assert refused.returncode != 0
    assert "alembic upgrade head" in refused.stderr
    engine = create_engine(database_url)
    try:
        with engine.connect() as connection:
            assert inspect(connection).get_table_names() == []
    finally:
        engine.dispose()


def test_load_refuses_a_schema_that_is_not_at_head(tmp_path) -> None:
    database_url = f"sqlite:///{tmp_path / 'stale.db'}"
    _migrate(database_url, "upgrade", "head")
    _migrate(database_url, "downgrade", "-1")

    refused = _load_curriculum(database_url)

    assert refused.returncode != 0
    assert "not at the repository's Alembic head" in refused.stderr


def test_load_is_idempotent_and_preserves_learner_evidence(tmp_path) -> None:
    from app.curriculum.registry import PATHS, all_items, all_lessons, all_objectives, all_projects
    from app.models import Evidence, Item, Lesson, Objective, Project, User

    database_url = f"sqlite:///{tmp_path / 'loaded.db'}"
    _migrate(database_url, "upgrade", "head")

    first = _load_curriculum(database_url)
    assert first.returncode == 0, first.stderr
    assert "Curriculum load complete" in first.stdout
    assert f"paths={len(PATHS)}" in first.stdout

    engine = create_engine(database_url)
    try:
        with Session(engine) as db:
            assert db.scalar(select(func.count()).select_from(Objective)) == len(all_objectives())
            assert db.scalar(select(func.count()).select_from(Lesson)) == len(all_lessons())
            assert db.scalar(select(func.count()).select_from(Item)) == len(all_items())
            assert db.scalar(select(func.count()).select_from(Project)) == len(all_projects())

            user = User(
                email="curriculum-load@example.com",
                password_hash="test-only",
                display_name="Curriculum Load",
            )
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
            objective = db.get(Objective, "py:values")
            assert objective is not None
            objective.title_en = "stale local edit"
            db.commit()
            user_id = user.id
    finally:
        engine.dispose()

    second = _load_curriculum(database_url)
    assert second.returncode == 0, second.stderr
    assert second.stdout == first.stdout

    engine = create_engine(database_url)
    try:
        with Session(engine) as db:
            assert db.scalar(select(func.count()).select_from(Objective)) == len(all_objectives())
            assert db.scalar(select(func.count()).select_from(Lesson)) == len(all_lessons())
            assert db.scalar(select(func.count()).select_from(Item)) == len(all_items())
            assert db.scalar(select(func.count()).select_from(Project)) == len(all_projects())
            assert db.scalar(select(func.count()).select_from(Evidence)) == 1
            assert db.get(User, user_id) is not None
            objective = db.get(Objective, "py:values")
            assert objective is not None
            assert objective.title_en != "stale local edit"
    finally:
        engine.dispose()
