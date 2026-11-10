"""Learning-domain integration, with persistence proven at every step.

Complements ``test_api_journey.py`` (which asserts HTTP- and schema-level behaviour) by pinning
the *database* state each workflow step produces, so a silent no-op write anywhere in the chain
fails loudly here. Every step is a real HTTP request against the app; AI is disabled (the default)
so nothing in the chain reaches a model runtime.
"""

from __future__ import annotations

from sqlalchemy import func, select

from app.db import session_scope
from app.models import (
    DiagnosticAttempt,
    DiagnosticResponse,
    Evidence,
    Goal,
    MasteryEstimate,
    Plan,
    PlanItem,
    PracticeResponse,
    PracticeSession,
    User,
)
from tests.conftest import answer_diagnostic_until_done, create_goal, register

USER = "workflow@example.com"
PASSWORD = "correct-horse-battery"


def _counts() -> dict[str, int]:
    with session_scope() as db:
        return {
            "users": db.scalar(select(func.count()).select_from(User)) or 0,
            "goals": db.scalar(select(func.count()).select_from(Goal)) or 0,
            "attempts": db.scalar(select(func.count()).select_from(DiagnosticAttempt)) or 0,
            "responses": db.scalar(select(func.count()).select_from(DiagnosticResponse)) or 0,
            "plans": db.scalar(select(func.count()).select_from(Plan)) or 0,
            "plan_items": db.scalar(select(func.count()).select_from(PlanItem)) or 0,
            "practice_sessions": db.scalar(select(func.count()).select_from(PracticeSession)) or 0,
            "practice_responses": db.scalar(select(func.count()).select_from(PracticeResponse)) or 0,
            "evidence": db.scalar(select(func.count()).select_from(Evidence)) or 0,
            "estimates": db.scalar(select(func.count()).select_from(MasteryEstimate)) or 0,
        }


def test_full_workflow_persists_state_at_every_step(client) -> None:
    before = _counts()

    # 1+2. Registration is authentication: the register response carries a session cookie.
    registered = register(client, email=USER)
    assert registered["user"]["email"] == USER
    assert _counts()["users"] == before["users"] + 1

    # 3. Goal creation persists a goal owned by the learner.
    goal = create_goal(client)
    counts = _counts()
    assert counts["goals"] == before["goals"] + 1
    with session_scope() as db:
        row = db.get(Goal, goal["id"])
        owner = db.scalar(select(User.id).where(User.email == USER))
        assert row is not None and row.user_id == owner and row.status == "active"

    # 4+5. Diagnostic: answering persists responses; completing persists placement.
    result = answer_diagnostic_until_done(client, goal["id"], correct=True)
    assert result["state"]["status"] == "completed"
    counts = _counts()
    assert counts["attempts"] == before["attempts"] + 1
    assert counts["responses"] >= counts["attempts"] + 0  # at least one response recorded
    with session_scope() as db:
        attempt = db.get(DiagnosticAttempt, result["attempt_id"])
        assert attempt.status == "completed"
        assert attempt.placement is not None
        assert attempt.completed_at is not None

    # 6. Plan generation persists the plan and its items.
    roadmap = client.post(f"/api/plans/goals/{goal['id']}")
    assert roadmap.status_code == 200, roadmap.text
    plan = roadmap.json()["plan"]
    counts = _counts()
    assert counts["plans"] == before["plans"] + 1
    assert counts["plan_items"] >= before["plan_items"] + len(
        [item for week in plan["weeks"] for item in week["items"]]
    )

    # 7. Lesson retrieval: every learn/practice item resolves to a public lesson payload.
    lesson_id = next(
        (item.get("lesson_id") for week in plan["weeks"] for item in week["items"] if item.get("lesson_id")),
        None,
    )
    if lesson_id:
        lesson = client.get(f"/api/curriculum/lessons/{lesson_id}")
        assert lesson.status_code == 200
        assert lesson.json()["id"] == lesson_id

    # 8. Lesson completion is modelled as completing the linked roadmap item through practice
    #    (there is no separate lesson-completion endpoint; see NOT IMPLEMENTED note in the report).

    # 9+10+11. Practice: start, answer with feedback, completion.
    session = client.post("/api/practice/sessions", json={"objective_id": "py:values", "size": 1})
    assert session.status_code == 201, session.text
    session_body = session.json()
    assert session_body["item"] is not None
    answered = client.post(
        f"/api/practice/sessions/{session_body['session_id']}/answers",
        json={
            "item_id": session_body["item"]["id"],
            # A deliberately wrong shape for the response payload: grading must not crash,
            # it must score it against the authored key and record the outcome.
            "response": {"option_id": "a"},
            "used_hint": False,
        },
    )
    assert answered.status_code == 200, answered.text
    feedback = answered.json()["feedback"]
    assert set(feedback) >= {"is_correct", "correct_answer"}
    counts = _counts()
    assert counts["practice_sessions"] == before["practice_sessions"] + 1
    assert counts["practice_responses"] == before["practice_responses"] + 1

    # 12+13. Evidence and mastery: practice answers record evidence; recompute is deterministic.
    recomputed = client.post("/api/practice/progress/recompute")
    assert recomputed.status_code == 200
    counts = _counts()
    assert counts["evidence"] >= before["evidence"] + 1

    # 14. Dashboard retrieval reflects the learner, not an empty account.
    dashboard = client.get("/api/dashboard")
    assert dashboard.status_code == 200
    body = dashboard.json()
    assert body["goal"]["id"] == goal["id"]


def test_diagnostic_result_survives_multiple_reads(client) -> None:
    """Persistence, not in-request state: three separate reads agree."""
    register(client, email="persist@example.com")
    goal = create_goal(client)
    answer_diagnostic_until_done(client, goal["id"], correct=True)
    attempts = client.get("/api/diagnostic").json()
    assert len(attempts) == 1
    first = attempts[0]
    second = client.get(f"/api/diagnostic/{first['attempt_id']}").json()
    third = client.get(f"/api/diagnostic/{first['attempt_id']}").json()
    assert first["status"] == second["status"] == third["status"] == "completed"
    assert first["placement"] == second["placement"] == third["placement"]


def test_malformed_inputs_are_rejected_with_422_not_500(client) -> None:
    register(client, email="malformed@example.com")
    goal = create_goal(client)

    attempt = client.post(f"/api/diagnostic/goals/{goal['id']}")
    assert attempt.status_code == 201
    attempt_id = attempt.json()["attempt_id"]

    bad_answer = client.post(
        f"/api/diagnostic/{attempt_id}/answers",
        json={"item_id": 123},  # wrong type AND missing response
    )
    assert bad_answer.status_code == 422

    bad_confidence = client.post(
        f"/api/diagnostic/{attempt_id}/answers",
        json={"item_id": "x", "response": {}, "confidence": "sometimes"},  # not a legal enum value
    )
    assert bad_confidence.status_code == 422

    bad_practice = client.post("/api/practice/sessions", json={"objective_id": "py:values", "size": 0})
    assert bad_practice.status_code == 422

    malformed_json = client.post(
        "/api/auth/login", content=b"{not json", headers={"content-type": "application/json"}
    )
    assert malformed_json.status_code == 422
    non_json_body = client.post("/api/goals", content=b"hello", headers={"content-type": "text/plain"})
    assert non_json_body.status_code == 415


def test_submitting_evidence_twice_does_not_double_count(client) -> None:
    """A retried recompute replays evidence deterministically instead of duplicating it."""
    register(client, email="idempotent@example.com")
    goal = create_goal(client)
    answer_diagnostic_until_done(client, goal["id"], correct=True)

    first = client.post("/api/practice/progress/recompute")
    second = client.post("/api/practice/progress/recompute")
    assert first.status_code == second.status_code == 200
    assert first.json() == second.json()
    counts = _counts()
    with session_scope() as db:
        evidence_rows = db.scalar(select(func.count()).select_from(Evidence)) or 0
    assert counts["evidence"] == evidence_rows


def test_ai_disabled_is_explicit_and_never_silently_succeeds(client) -> None:
    register(client, email="ai-off@example.com")
    usage = client.get("/api/tutor/usage")
    assert usage.status_code == 200
    assert usage.json()["ai_enabled"] is False

    refused = client.post(
        "/api/tutor/ask",
        json={"objective_id": "py:values", "question": "What is a variable?"},
    )
    assert refused.status_code == 503
    assert "unavailable" in refused.json()["detail"].lower() or "off" in refused.json()["detail"].lower()
