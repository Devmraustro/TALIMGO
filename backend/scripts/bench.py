"""Focused performance measurements for the current API and database.

This is a *measurement tool*, not a benchmark suite: it exists so claims about speed come from a run
on this machine rather than from intuition. It reports, for the seeded local database:

* median and p95 wall-clock latency for the endpoints a learner touches;
* SQL statements executed per request (the N+1 question, answered with a counter);
* database size after the journey, for the growth question.

Run it with the same interpreter the app uses:

    cd backend && .venv/bin/python scripts/bench.py

It writes nothing outside a temporary directory and prints a markdown table that can be pasted into
the implementation plan. Numbers here are single-process SQLite figures on a development machine and
must not be presented as production capacity.
"""

from __future__ import annotations

import platform
import sqlite3
import statistics
import sys
import tempfile
import time
from collections.abc import Callable
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from fastapi.testclient import TestClient


def _percentile(values: list[float], fraction: float) -> float:
    ordered = sorted(values)
    index = min(len(ordered) - 1, round(fraction * (len(ordered) - 1)))
    return ordered[index]


def _count_statements(engine) -> list[int]:
    """Attach a counter to the engine and return a one-element list holding the count."""
    from sqlalchemy import event

    counter = [0]

    @event.listens_for(engine, "before_cursor_execute")
    def _increment(_conn, _cursor, _statement, _parameters, _context, _executemany):  # pragma: no cover
        counter[0] += 1

    return counter


def main() -> int:
    import logging
    import os

    from tests.conftest import (
        answer_diagnostic_until_done,
        create_goal,
        register,
    )

    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("talimgo").setLevel(logging.WARNING)

    from app.config import reset_settings_cache
    from app.curriculum.registry import item_index
    from app.db import get_engine, reset_engine
    from app.main import create_app

    workdir = Path(tempfile.mkdtemp(prefix="talimgo-bench-"))
    database = workdir / "bench.db"
    os.environ["TALIMGO_ENV"] = "test"
    os.environ["TALIMGO_DATABASE_URL"] = f"sqlite:///{database}"
    os.environ["TALIMGO_SESSION_SECRET"] = "bench-session-secret-0123456789abcdef"
    os.environ["TALIMGO_ALLOWED_ORIGINS"] = "http://localhost:5173"
    os.environ["TALIMGO_AI_ENABLED"] = "false"
    reset_settings_cache()
    reset_engine()

    app = create_app()
    with TestClient(app) as client:
        register(client, email="bench@example.com")
        goal = create_goal(client, path_id="python-foundations")
        answer_diagnostic_until_done(client, goal["id"])
        plan = client.post(f"/api/plans/goals/{goal['id']}").json()["plan"]
        item = plan["weeks"][0]["items"][0]
        session = client.post(
            "/api/practice/sessions",
            json={
                "objective_id": item["objective_id"],
                "goal_id": goal["id"],
                "plan_item_id": item["id"],
            },
        ).json()

        engine = get_engine()
        counter = _count_statements(engine)

        calls: list[tuple[str, Callable[[], object]]] = [
            ("GET /api/dashboard", lambda: client.get("/api/dashboard")),
            ("GET /api/plans/active", lambda: client.get("/api/plans/active")),
            ("GET /api/plans/active/schedule", lambda: client.get("/api/plans/active/schedule")),
            ("GET /api/curriculum/paths", lambda: client.get("/api/curriculum/paths")),
            (
                "GET /api/curriculum/lessons/{id}",
                lambda: client.get(f"/api/curriculum/lessons/{item['lesson_id']}"),
            ),
            (
                "GET /api/practice/sessions/{id}",
                lambda: client.get(f"/api/practice/sessions/{session['session_id']}"),
            ),
            ("GET /api/practice/progress/mastery", lambda: client.get("/api/practice/progress/mastery")),
        ]

        runs = 12
        index = item_index("python-foundations")
        print(f"# TALIMGO endpoint measurements — {time.strftime('%Y-%m-%d %H:%M %Z')}")
        print(
            f"# python {platform.python_version()} · sqlite {sqlite3.sqlite_version} · "
            f"{platform.system()} {platform.machine()} · single process, TestClient (no network)"
        )
        print()
        print("| Endpoint | median ms | p95 ms | SQL statements/request |")
        print("|---|---|---|---|")
        for label, call in calls:
            timings: list[float] = []
            statements: list[int] = []
            for _ in range(runs):
                counter[0] = 0
                started = time.perf_counter()
                response = call()
                timings.append((time.perf_counter() - started) * 1000)
                statements.append(counter[0])
                assert getattr(response, "status_code", 200) == 200, (label, response)
            print(
                f"| {label} | {statistics.median(timings):.1f} | {_percentile(timings, 0.95):.1f} | "
                f"{statistics.median(statements):.0f} |"
            )

        # Answering is the hottest write path: grading, evidence, mastery refresh and plan progress.
        accepted: list[float] = []
        accepted_statements: list[int] = []
        state = session
        while state["item"] is not None:
            current = state["item"]
            key = index[current["id"]]["answer_key"]
            payload = (
                {"option_id": key["option_id"]}
                if current["kind"] == "mcq_single"
                else {"text": key["accepted"][0]}
            )
            counter[0] = 0
            started = time.perf_counter()
            response = client.post(
                f"/api/practice/sessions/{state['session_id']}/answers",
                json={"item_id": current["id"], "response": payload},
            )
            accepted.append((time.perf_counter() - started) * 1000)
            accepted_statements.append(counter[0])
            assert response.status_code == 200, response.text
            state = response.json()
            state.setdefault("session_id", session["session_id"])

        replay: list[float] = []
        replay_statements: list[int] = []
        answered_item = session["item"]["id"]
        key = index[answered_item]["answer_key"]
        for _ in range(5):
            counter[0] = 0
            started = time.perf_counter()
            response = client.post(
                f"/api/practice/sessions/{session['session_id']}/answers",
                json={
                    "item_id": answered_item,
                    "response": {"option_id": key["option_id"]}
                    if session["item"]["kind"] == "mcq_single"
                    else {"text": key["accepted"][0]},
                },
            )
            replay.append((time.perf_counter() - started) * 1000)
            replay_statements.append(counter[0])
            assert response.status_code == 409, response.text

        print()
        print("| Write path | median ms | SQL statements/request |")
        print("|---|---|---|")
        print(
            f"| POST practice answer (accepted, {len(accepted)} items) | "
            f"{statistics.median(accepted):.1f} | {statistics.median(accepted_statements):.0f} |"
        )
        print(
            f"| POST practice answer (replayed item, 409) | {statistics.median(replay):.1f} | "
            f"{statistics.median(replay_statements):.0f} |"
        )

        size_kb = database.stat().st_size / 1024 if database.exists() else 0.0
        rows = sqlite3.connect(database)
        tables = [
            name for (name,) in rows.execute("select name from sqlite_master where type='table'").fetchall()
        ]
        counts = {
            table: rows.execute(f"select count(*) from {table}").fetchone()[0]
            for table in tables
            if table != "sqlite_sequence"
        }
        rows.close()
        print()
        print(
            f"# database after one learner journey: {size_kb:.0f} KiB across {len(counts)} tables; "
            f"largest: {sorted(counts.items(), key=lambda pair: -pair[1])[:5]}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
