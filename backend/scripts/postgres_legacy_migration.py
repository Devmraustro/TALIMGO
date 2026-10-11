"""Rehearse the populated-plan migration against PostgreSQL in CI.

The target database must be empty. The script intentionally builds the previous schema, seeds one
valid legacy learning plan, upgrades to head, and verifies the backfill and preserved rows.
"""

from __future__ import annotations

import os
import subprocess
import sys
from datetime import UTC, datetime

from sqlalchemy import create_engine, text

LEGACY_REVISION = "8f1c2d4e6a70"
USER_ID = "usr_legacy_migration_check"
GOAL_ID = "gol_legacy_migration_check"
OBJECTIVE_ID = "obj_legacy_migration_check"
PLAN_ID = "pln_legacy_migration_check"
WEEK_ID = "pwk_legacy_migration_check"
ITEM_ID = "pit_legacy_migration_check"


def run_alembic(env: dict[str, str], *arguments: str) -> None:
    subprocess.run([sys.executable, "-m", "alembic", *arguments], check=True, env=env)


def main() -> None:
    database_url = os.environ.get("TALIMGO_DATABASE_URL", "")
    if not database_url.startswith("postgresql+psycopg://"):
        raise SystemExit("Refusing to run: TALIMGO_DATABASE_URL must target PostgreSQL via psycopg.")

    env = os.environ.copy()
    env.setdefault("TALIMGO_ENV", "test")
    env.setdefault("TALIMGO_SESSION_SECRET", "postgres-ci-session-secret-change-this")
    env["TALIMGO_DATABASE_URL"] = database_url

    # CI provides a fresh, disposable database. Upgrading directly to the previous revision creates
    # the legacy shape without the schedule columns added by 9b2e4f6a8c10.
    run_alembic(env, "upgrade", LEGACY_REVISION)
    engine = create_engine(database_url, pool_pre_ping=True)
    now = datetime.now(UTC)

    try:
        with engine.begin() as connection:
            connection.execute(
                text(
                    "INSERT INTO users "
                    "(id, email, password_hash, display_name, role, is_active, created_at, updated_at) "
                    "VALUES (:id, :email, :password_hash, :display_name, :role, :is_active, "
                    ":created_at, :updated_at)"
                ),
                {
                    "id": USER_ID,
                    "email": "legacy-plan-migration@example.com",
                    "password_hash": "test-only-not-a-real-password-hash",
                    "display_name": "Legacy Migration Check",
                    "role": "learner",
                    "is_active": True,
                    "created_at": now,
                    "updated_at": now,
                },
            )
            connection.execute(
                text(
                    "INSERT INTO goals "
                    "(id, user_id, path_id, statement, motivation, target_date, weekly_minutes, "
                    "status, created_at, updated_at) VALUES "
                    "(:id, :user_id, :path_id, :statement, :motivation, NULL, :weekly_minutes, "
                    ":status, :created_at, :updated_at)"
                ),
                {
                    "id": GOAL_ID,
                    "user_id": USER_ID,
                    "path_id": "python-foundations",
                    "statement": "Preserve a plan during migration",
                    "motivation": "Migration regression test",
                    "weekly_minutes": 240,
                    "status": "active",
                    "created_at": now,
                    "updated_at": now,
                },
            )
            connection.execute(
                text(
                    "INSERT INTO objectives "
                    "(id, path_id, title_en, title_ar, summary_en, summary_ar, kind, bloom_level, "
                    "difficulty, prerequisite_ids, sequence) VALUES "
                    "(:id, :path_id, :title_en, :title_ar, :summary_en, :summary_ar, :kind, "
                    ":bloom_level, :difficulty, CAST(:prerequisite_ids AS json), :sequence)"
                ),
                {
                    "id": OBJECTIVE_ID,
                    "path_id": "python-foundations",
                    "title_en": "Legacy migration objective",
                    "title_ar": "هدف الترحيل القديم",
                    "summary_en": "Temporary objective used only by the CI migration check.",
                    "summary_ar": "هدف مؤقت لفحص الترحيل في CI.",
                    "kind": "concept",
                    "bloom_level": "understand",
                    "difficulty": 1,
                    "prerequisite_ids": "[]",
                    "sequence": 999,
                },
            )
            connection.execute(
                text(
                    "INSERT INTO plans "
                    "(id, user_id, goal_id, version, status, generator, total_estimated_minutes, "
                    "validation_report, created_at) VALUES "
                    "(:id, :user_id, :goal_id, :version, :status, :generator, :minutes, "
                    "CAST(:validation_report AS json), :created_at)"
                ),
                {
                    "id": PLAN_ID,
                    "user_id": USER_ID,
                    "goal_id": GOAL_ID,
                    "version": 1,
                    "status": "active",
                    "generator": "deterministic-v1",
                    "minutes": 45,
                    "validation_report": '{"valid": true, "source": "legacy-migration-ci"}',
                    "created_at": now,
                },
            )
            connection.execute(
                text(
                    "INSERT INTO plan_weeks (id, plan_id, week_number, theme_en, theme_ar) "
                    "VALUES (:id, :plan_id, :week_number, :theme_en, :theme_ar)"
                ),
                {
                    "id": WEEK_ID,
                    "plan_id": PLAN_ID,
                    "week_number": 1,
                    "theme_en": "Migration verification",
                    "theme_ar": "التحقق من الترحيل",
                },
            )
            connection.execute(
                text(
                    "INSERT INTO plan_items "
                    "(id, plan_id, week_id, order_index, objective_id, lesson_id, kind, est_minutes, "
                    "status, rationale_en, rationale_ar) VALUES "
                    "(:id, :plan_id, :week_id, :order_index, :objective_id, NULL, :kind, "
                    ":minutes, :status, :rationale_en, :rationale_ar)"
                ),
                {
                    "id": ITEM_ID,
                    "plan_id": PLAN_ID,
                    "week_id": WEEK_ID,
                    "order_index": 1,
                    "objective_id": OBJECTIVE_ID,
                    "kind": "learn",
                    "minutes": 15,
                    "status": "pending",
                    "rationale_en": "Legacy plan item must be preserved.",
                    "rationale_ar": "يجب الحفاظ على عنصر الخطة القديم.",
                },
            )

        run_alembic(env, "upgrade", "head")
        run_alembic(env, "check")

        with engine.connect() as connection:
            plan = (
                connection.execute(
                    text(
                        "SELECT id, starts_on, starts_on = CURRENT_DATE AS starts_today, "
                        "validation_report->>'source' AS source FROM plans WHERE id = :id"
                    ),
                    {"id": PLAN_ID},
                )
                .mappings()
                .one_or_none()
            )
            if plan is None:
                raise AssertionError("Legacy plan was lost during the migration.")
            if not plan["starts_today"] or plan["source"] != "legacy-migration-ci":
                raise AssertionError("Legacy plan backfill or existing JSON data did not survive.")

            nullability = connection.execute(
                text(
                    "SELECT is_nullable FROM information_schema.columns "
                    "WHERE table_schema = current_schema() AND table_name = 'plans' "
                    "AND column_name = 'starts_on'"
                )
            ).scalar_one_or_none()
            if nullability != "NO":
                raise AssertionError("plans.starts_on must be NOT NULL after the migration.")

            item = (
                connection.execute(
                    text("SELECT id, status, scheduled_day, completed_at FROM plan_items WHERE id = :id"),
                    {"id": ITEM_ID},
                )
                .mappings()
                .one_or_none()
            )
            if item is None:
                raise AssertionError("Legacy plan item was lost during the migration.")
            if item["status"] != "pending" or item["scheduled_day"] is not None:
                raise AssertionError("Legacy plan-item state was not preserved.")
            if item["completed_at"] is not None:
                raise AssertionError("Legacy plan item's optional completion timestamp must remain null.")

    finally:
        engine.dispose()

    print(
        "PostgreSQL legacy migration passed: existing plan/item preserved, starts_on backfilled "
        "and NOT NULL, schedule fields safely null, alembic check clean."
    )


if __name__ == "__main__":
    main()
