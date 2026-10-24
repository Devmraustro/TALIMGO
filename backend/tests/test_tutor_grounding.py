"""Grounding integrity: the tutor must never read a lesson that belongs to another objective.

Code-review finding: ``build_grounding()`` accepted any ``lesson_id`` the caller supplied and put the
lesson body into the model prompt without checking that the lesson belongs to the requested
objective. A caller could therefore get one objective's material answered under another objective's
name, which also corrupts the citation allow-list: the citation attached to the prompt would name a
lesson the learner never asked about.

The fix refuses the mismatch before any prompt is built, so the local model is never called.
"""

from __future__ import annotations

import json

import httpx
import pytest
from sqlalchemy import select

from app.ai.grounding import build_grounding
from app.ai.tutor import answer
from app.config import get_settings
from tests.conftest import register

EMAIL = "grounding@example.com"
VALUES_LESSON = "py:values:lesson"
STRINGS_LESSON = "py:strings:lesson"  # belongs to py:strings, not py:values


def _mock_client(handler):
    def factory(settings):
        from app.ai.adapter import LocalModelClient

        return LocalModelClient(settings, transport=httpx.MockTransport(handler))

    return factory


# --------------------------------------------------------------------------------------
# Service level
# --------------------------------------------------------------------------------------


def test_build_grounding_accepts_a_lesson_of_the_same_objective(ai_client_factory) -> None:
    client = ai_client_factory()
    register(client, email=EMAIL)

    from app.db import session_scope

    with session_scope() as db:
        context = build_grounding(db, objective_id="py:values", lesson_id=VALUES_LESSON)

    assert context.lesson_id == VALUES_LESSON
    assert f"lesson:{VALUES_LESSON}" in context.citation_ids
    assert STRINGS_LESSON not in context.markdown


def test_build_grounding_rejects_a_lesson_of_another_objective(ai_client_factory) -> None:
    client = ai_client_factory()
    register(client, email=EMAIL)

    from app.db import session_scope

    with session_scope() as db, pytest.raises(LookupError):
        build_grounding(db, objective_id="py:values", lesson_id=STRINGS_LESSON)


def test_service_level_guard_runs_before_the_model_client_is_constructed(ai_client_factory) -> None:
    client = ai_client_factory()
    register(client, email=EMAIL)
    settings = get_settings()

    def exploding_factory(_settings):
        raise AssertionError("the model client must not be constructed for a mismatched lesson")

    from app.db import session_scope
    from app.models import User

    with session_scope() as db:
        user = db.scalar(select(User).where(User.email == EMAIL))
        assert user is not None
        with pytest.raises(LookupError):
            answer(
                db,
                settings,
                user=user,
                objective_id="py:values",
                lesson_id=STRINGS_LESSON,
                question="Explain this",
                client_factory=exploding_factory,
            )


# --------------------------------------------------------------------------------------
# Through the tutor endpoint, which is where a prompt would be built
# --------------------------------------------------------------------------------------


def test_mismatched_lesson_never_reaches_the_local_model(ai_client_factory, monkeypatch) -> None:
    calls: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request)
        return httpx.Response(
            200,
            json={
                "model": "local-test-model",
                "message": {
                    "content": json.dumps(
                        {
                            "reply": "should never be produced",
                            "hint_level": 0,
                            "citations": [],
                            "confidence": "low",
                            "follow_up_question": None,
                        }
                    )
                },
            },
        )

    client = ai_client_factory()
    monkeypatch.setattr("app.ai.tutor.LocalModelClient", _mock_client(handler))
    register(client, email=EMAIL)

    response = client.post(
        "/api/tutor/ask",
        json={
            "objective_id": "py:values",
            "lesson_id": STRINGS_LESSON,
            "question": "Explain this",
        },
    )
    assert response.status_code == 400, response.text
    assert calls == [], "the local model must not be called with a mismatched lesson"

    from app.db import session_scope
    from app.models import AiUsage, TutorMessage

    with session_scope() as db:
        assert db.query(TutorMessage).count() == 0, "a rejected request stores nothing"
        assert db.query(AiUsage).count() == 0, "a rejected request consumes no allowance"


def test_matching_lesson_still_reaches_the_model(ai_client_factory, monkeypatch) -> None:
    payload = {
        "reply": "Values have types, and a lesson belongs to exactly one objective.",
        "hint_level": 1,
        "citations": [f"lesson:{VALUES_LESSON}", "objective:py:values"],
        "confidence": "high",
        "follow_up_question": "Which type does 7 / 2 produce?",
    }
    seen: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(request)
        prompt = request.content.decode()
        assert STRINGS_LESSON not in prompt, "another objective's lesson leaked into the prompt"
        return httpx.Response(
            200, json={"model": "local-test-model", "message": {"content": json.dumps(payload)}}
        )

    client = ai_client_factory()
    monkeypatch.setattr("app.ai.tutor.LocalModelClient", _mock_client(handler))
    register(client, email=EMAIL)

    response = client.post(
        "/api/tutor/ask",
        json={"objective_id": "py:values", "lesson_id": VALUES_LESSON, "question": "Explain values"},
    )
    assert response.status_code == 200, response.text
    assert len(seen) == 1, "exactly one local model call"
    assert seen[0].url.host == "127.0.0.1"
    assert f"lesson:{VALUES_LESSON}" in response.json()["citations"]
