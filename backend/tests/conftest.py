"""Shared fixtures.

Isolation rules:
  * Every test gets its own SQLite database file, so tests never share learner state.
  * Settings are re-read from the environment for each app instance, and the engine cache is reset
    around every test, so no fixture leaks configuration into another.
  * `client` runs with AI **disabled** (the default). `ai_client` enables it against a localhost
    endpoint; tests that need model traffic monkeypatch the transport.
"""

from __future__ import annotations

import os
import uuid
from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

TEST_SESSION_SECRET = "test-session-secret-0123456789abcdef"


def _apply_env(tmp_path, monkeypatch, *, ai_enabled: bool = False, extra: dict | None = None) -> None:
    monkeypatch.setenv("TALIMGO_ENV", "test")
    monkeypatch.setenv("TALIMGO_DATABASE_URL", f"sqlite:///{tmp_path / 'talimgo-test.db'}")
    monkeypatch.setenv("TALIMGO_SESSION_SECRET", TEST_SESSION_SECRET)
    monkeypatch.setenv("TALIMGO_ALLOWED_ORIGINS", "http://localhost:5173")
    monkeypatch.setenv("TALIMGO_AI_ENABLED", "true" if ai_enabled else "false")
    monkeypatch.setenv("TALIMGO_AI_BASE_URL", "http://127.0.0.1:11434")
    monkeypatch.setenv("TALIMGO_AI_DIALECT", "ollama")
    monkeypatch.setenv("TALIMGO_AI_MODEL", "local-test-model" if ai_enabled else "")
    for key, value in (extra or {}).items():
        monkeypatch.setenv(key, str(value))


def _build_client(
    tmp_path, monkeypatch, *, ai_enabled: bool = False, extra: dict | None = None
) -> TestClient:
    from app.config import reset_settings_cache
    from app.db import reset_engine

    _apply_env(tmp_path, monkeypatch, ai_enabled=ai_enabled, extra=extra)
    reset_settings_cache()
    reset_engine()
    from app.main import create_app

    app = create_app()
    return TestClient(app)


def _teardown() -> None:
    from app.config import reset_settings_cache
    from app.db import reset_engine

    reset_settings_cache()
    reset_engine()


@pytest.fixture()
def client(tmp_path, monkeypatch) -> Iterator[TestClient]:
    with _build_client(tmp_path, monkeypatch) as test_client:
        yield test_client
    _teardown()


@pytest.fixture()
def client_factory(tmp_path, monkeypatch):
    """Builds app clients with arbitrary environment overrides (AI stays off unless asked)."""

    created: list[TestClient] = []

    def factory(**extra) -> TestClient:
        enabled = str(extra.pop("ai_enabled", "false")).lower() == "true"
        test_client = _build_client(tmp_path, monkeypatch, ai_enabled=enabled, extra=extra)
        test_client.__enter__()
        created.append(test_client)
        return test_client

    yield factory
    for test_client in created:
        test_client.__exit__(None, None, None)


@pytest.fixture()
def ai_client_factory(tmp_path, monkeypatch):
    """Builds app clients with AI enabled; the caller supplies extra env overrides."""

    created: list[TestClient] = []

    def factory(**extra) -> TestClient:
        test_client = _build_client(tmp_path, monkeypatch, ai_enabled=True, extra=extra)
        test_client.__enter__()
        created.append(test_client)
        return test_client

    yield factory
    for test_client in created:
        test_client.__exit__(None, None, None)
    _teardown()


# --------------------------------------------------------------------------------------
# Helpers used across test modules
# --------------------------------------------------------------------------------------


def register(
    client: TestClient,
    *,
    email: str | None = None,
    password: str = "correct-horse-battery",
    ai_consent: bool = True,
    display_name: str = "Test Learner",
) -> dict:
    unique = uuid.uuid4().hex[:10]
    response = client.post(
        "/api/auth/register",
        json={
            "email": email or f"learner-{unique}@example.com",
            "password": password,
            "display_name": display_name,
            "accept_terms": True,
            "accept_ai_processing": ai_consent,
        },
    )
    assert response.status_code == 201, response.text
    return response.json()


def create_goal(
    client: TestClient, *, path_id: str = "python-foundations", weekly_minutes: int = 240
) -> dict:
    response = client.post(
        "/api/goals",
        json={
            "path_id": path_id,
            "statement": "I want to write small Python tools confidently",
            "motivation": "Automate repetitive work at my job",
            "weekly_minutes": weekly_minutes,
        },
    )
    assert response.status_code == 201, response.text
    return response.json()


def answer_diagnostic_until_done(client: TestClient, goal_id: str, *, correct: bool = True) -> dict:
    """Start or resume a diagnostic and answer every presented item."""
    start = client.post(f"/api/diagnostic/goals/{goal_id}")
    assert start.status_code in (200, 201), start.text
    state = start.json()
    attempt_id = state["attempt_id"]

    while state["status"] == "in_progress" and state["current_item"] is not None:
        item = state["current_item"]
        payload = _correct_response(item) if correct else _wrong_response(item)
        response = client.post(
            f"/api/diagnostic/{attempt_id}/answers",
            json={"item_id": item["id"], "response": payload, "confidence": "unsure"},
        )
        assert response.status_code == 200, response.text
        body = response.json()
        state = {
            "attempt_id": attempt_id,
            "status": "completed" if body["completed"] else "in_progress",
            "current_item": body["next_item"],
        }
    return {"attempt_id": attempt_id, "state": state}


def _authored_item(item_id: str) -> dict:
    """The authored item (with its key) from whichever path defines it."""
    from app.curriculum.registry import PATHS, item_index

    for path_id in PATHS:
        index = item_index(path_id)
        if item_id in index:
            return index[item_id]
    raise KeyError(f"no authored item {item_id!r}")


def _correct_response(item: dict) -> dict:
    """Answer correctly using the authored key (tests may read keys; clients never do)."""
    key = _authored_item(item["id"])["answer_key"]
    if item["kind"] == "mcq_single":
        return {"option_id": key["option_id"]}
    if item["kind"] in {"mcq_multi", "ordering"}:
        return {"option_ids": list(key["option_ids"])}
    if item["kind"] == "numeric":
        return {"text": str(key["value"])}
    if item["kind"] == "true_false":
        return {"value": bool(key["value"])}
    return {"text": key["accepted"][0]}


def _wrong_response(item: dict) -> dict:
    key = _authored_item(item["id"])["answer_key"]
    if item["kind"] == "mcq_single":
        option_ids = [option["id"] for option in item["options"] or []]
        wrong = [candidate for candidate in option_ids if candidate != key["option_id"]]
        return {"option_id": wrong[0] if wrong else "z"}
    if item["kind"] == "mcq_multi":
        return {"option_ids": []}
    if item["kind"] == "ordering":
        return {"option_ids": list(reversed(key["option_ids"]))}
    if item["kind"] == "numeric":
        return {"text": str(float(key["value"]) + 1)}
    if item["kind"] == "true_false":
        return {"value": not bool(key["value"])}
    return {"text": "definitely-not-the-answer"}


@pytest.fixture()
def clean_env() -> Iterator[None]:
    """Guarantees no ambient TALIMGO_* variable leaks into a test that reads settings directly."""
    saved = {key: os.environ[key] for key in list(os.environ) if key.startswith("TALIMGO_")}
    for key in saved:
        os.environ.pop(key)
    yield
    os.environ.update(saved)
