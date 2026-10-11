"""Focused PostgreSQL runtime smoke test for CI.

Run after Alembic has applied the complete schema to TALIMGO_DATABASE_URL.
This is not a replacement for the isolated SQLite API test suite or production rehearsal.
"""

from __future__ import annotations

import os
from uuid import uuid4

from fastapi.testclient import TestClient


def main() -> None:
    database_url = os.environ.get("TALIMGO_DATABASE_URL", "")
    if not database_url.startswith("postgresql+psycopg://"):
        raise SystemExit("Refusing to run: TALIMGO_DATABASE_URL must target PostgreSQL via psycopg.")

    os.environ.setdefault("TALIMGO_ENV", "test")
    os.environ.setdefault("TALIMGO_SESSION_SECRET", "postgres-ci-session-secret-change-this")
    os.environ.setdefault("TALIMGO_AI_ENABLED", "false")

    from app.config import reset_settings_cache
    from app.db import reset_engine
    from app.main import create_app

    reset_settings_cache()
    reset_engine()

    email = f"postgres-smoke-{uuid4().hex[:12]}@example.com"
    with TestClient(create_app()) as client:
        health = client.get("/api/health")
        if health.status_code != 200 or health.json().get("status") != "ok":
            raise AssertionError("PostgreSQL-backed API health check failed.")

        registered = client.post(
            "/api/auth/register",
            json={
                "email": email,
                "password": "ci-postgres-smoke-password",
                "display_name": "PostgreSQL CI",
                "accept_terms": True,
                "accept_ai_processing": False,
            },
        )
        if registered.status_code != 201:
            raise AssertionError(
                f"PostgreSQL account registration failed with HTTP {registered.status_code}."
            )

        me = client.get("/api/auth/me")
        if me.status_code != 200 or me.json().get("user", {}).get("email") != email:
            raise AssertionError("PostgreSQL session read-back failed.")

        goal = client.post(
            "/api/goals",
            json={
                "path_id": "python-foundations",
                "statement": "Verify PostgreSQL persistence",
                "motivation": "CI integration smoke test",
                "weekly_minutes": 240,
            },
        )
        if goal.status_code != 201:
            raise AssertionError(f"PostgreSQL goal creation failed with HTTP {goal.status_code}.")
        goal_id = goal.json().get("id")
        listed = client.get("/api/goals")
        if listed.status_code != 200 or not any(
            row.get("id") == goal_id for row in listed.json()
        ):
            raise AssertionError("PostgreSQL goal write/read-back failed.")

    print("PostgreSQL smoke passed: health, registration, session read-back and goal persistence.")


if __name__ == "__main__":
    main()
