"""Export and deletion, end to end, across every category of learner data.

Deletion is the promise that matters most and the easiest to get subtly wrong: a learner who deletes
their account expects their work to be gone, the shared curriculum to survive, and the audit trail to
stop naming them. These tests walk a learner through a full journey first, so "deleted" is asserted
against data that actually exists rather than against empty tables.
"""

from __future__ import annotations

import json

import httpx
import pytest
from fastapi.testclient import TestClient

from app.ai.adapter import LocalModelClient
from app.db import session_scope
from app.models import (
    AuditLog,
    ConsentRecord,
    DiagnosticAttempt,
    DiagnosticResponse,
    Evidence,
    Goal,
    Item,
    Lesson,
    MasteryEstimate,
    Objective,
    Plan,
    PlanItem,
    PlanWeek,
    PracticeResponse,
    PracticeSession,
    Profile,
    Session,
    TutorMessage,
    TutorThread,
    User,
)
from tests.conftest import answer_diagnostic_until_done, create_goal, register

VALID_REPLY = {
    "reply": "In Python 3, 7 / 2 is 3.5; int(7 / 2) drops the fraction.",
    "hint_level": 1,
    "citations": ["objective:py:values"],
    "confidence": "high",
    "follow_up_question": "What does 7 // 2 give?",
}


PASSWORD = "lifecycle-password-123"


def _build_a_learner_with_history(ai_client_factory, monkeypatch) -> tuple[TestClient, dict]:
    """A learner with a diagnostic, a plan, a completed practice session and a tutor thread.

    The tutor runs the real code path with a mocked *local* transport, so no model download is needed
    while the policy, payload building, validation and persistence are all exercised.
    """
    from app.ai import tutor as tutor_module

    client = ai_client_factory(TALIMGO_AI_MODEL="local-test-model")
    monkeypatch.setattr(
        tutor_module,
        "LocalModelClient",
        lambda settings: LocalModelClient(
            settings,
            transport=httpx.MockTransport(
                lambda request: httpx.Response(
                    200,
                    json={
                        "model": "local-test-model",
                        "message": {"content": json.dumps(VALID_REPLY)},
                    },
                )
            ),
        ),
    )

    me = register(client, email="lifecycle@example.com", password=PASSWORD)
    client.patch("/api/me/profile", json={"locale": "ar", "weekly_minutes": 180})
    client.post("/api/me/consents", json={"kind": "ai_processing", "granted": True})
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
    from app.curriculum.registry import item_index

    index = item_index("python-foundations")
    while session["item"] is not None:
        current = session["item"]
        key = index[current["id"]]["answer_key"]
        payload = (
            {"option_id": key["option_id"]}
            if current["kind"] == "mcq_single"
            else {"text": key["accepted"][0]}
        )
        session = client.post(
            f"/api/practice/sessions/{session['session_id']}/answers",
            json={"item_id": current["id"], "response": payload},
        ).json()
    client.post(f"/api/practice/sessions/{session['session_id']}/complete")

    reply = client.post(
        "/api/tutor/ask",
        json={
            "objective_id": item["objective_id"],
            "lesson_id": item["lesson_id"],
            "question": "Why is 7 / 2 a float?",
        },
    )
    assert reply.status_code == 200, reply.text
    return client, {"me": me, "goal": goal, "plan": plan, "item": item, "session": session}


def _counts(user_id: str) -> dict[str, int]:
    with session_scope() as db:
        plan_ids = [row.id for row in db.query(Plan.id).filter(Plan.user_id == user_id).all()]
        thread_ids = [row.id for row in db.query(TutorThread.id).filter(TutorThread.user_id == user_id).all()]
        practice_ids = [
            row.id for row in db.query(PracticeSession.id).filter(PracticeSession.user_id == user_id).all()
        ]
        attempt_ids = [
            row.id
            for row in db.query(DiagnosticAttempt.id).filter(DiagnosticAttempt.user_id == user_id).all()
        ]
        return {
            "profiles": db.query(Profile).filter(Profile.user_id == user_id).count(),
            "consents": db.query(ConsentRecord).filter(ConsentRecord.user_id == user_id).count(),
            "goals": db.query(Goal).filter(Goal.user_id == user_id).count(),
            "evidence": db.query(Evidence).filter(Evidence.user_id == user_id).count(),
            "mastery": db.query(MasteryEstimate).filter(MasteryEstimate.user_id == user_id).count(),
            "plans": len(plan_ids),
            "plan_weeks": db.query(PlanWeek).filter(PlanWeek.plan_id.in_(plan_ids or [""])).count(),
            "plan_items": db.query(PlanItem).filter(PlanItem.plan_id.in_(plan_ids or [""])).count(),
            "threads": len(thread_ids),
            "tutor_messages": db.query(TutorMessage)
            .filter(TutorMessage.thread_id.in_(thread_ids or [""]))
            .count(),
            "practice_sessions": len(practice_ids),
            "practice_responses": db.query(PracticeResponse)
            .filter(PracticeResponse.session_id.in_(practice_ids or [""]))
            .count(),
            "diagnostic_attempts": len(attempt_ids),
            "diagnostic_responses": db.query(DiagnosticResponse)
            .filter(DiagnosticResponse.attempt_id.in_(attempt_ids or [""]))
            .count(),
            "sessions": db.query(Session).filter(Session.user_id == user_id).count(),
            "users": db.query(User).filter(User.id == user_id).count(),
            "audit_naming_user": db.query(AuditLog).filter(AuditLog.actor_user_id == user_id).count(),
        }


def test_the_journey_created_data_to_delete(ai_client_factory, monkeypatch) -> None:
    """Guards the tests below it: deletion is only meaningful if there is something to delete."""
    _client, created = _build_a_learner_with_history(ai_client_factory, monkeypatch)
    counts = _counts(created["me"]["user"]["id"])
    for key in (
        "profiles",
        "consents",
        "goals",
        "evidence",
        "plans",
        "plan_weeks",
        "plan_items",
        "threads",
        "tutor_messages",
        "practice_sessions",
        "practice_responses",
        "diagnostic_attempts",
        "diagnostic_responses",
        "sessions",
    ):
        assert counts[key] >= 1, f"expected the journey to create {key}: {counts}"


def test_export_contains_every_category_before_deletion(ai_client_factory, monkeypatch) -> None:
    client, created = _build_a_learner_with_history(ai_client_factory, monkeypatch)
    export = client.get("/api/me/export")
    assert export.status_code == 200
    body = export.json()["account"]

    assert body["account"]["email"] == "lifecycle@example.com"
    assert body["profile"]["locale"] == "ar"
    assert body["goals"] and body["plans"] and body["evidence"]
    assert body["tutor_messages"] and any(message["role"] == "tutor" for message in body["tutor_messages"])
    assert body["sessions"]
    assert json.dumps(body), "the export must be machine-readable JSON, not a repr"
    assert created["me"]["user"]["id"]


def test_deletion_removes_learner_data_and_anonymises_audit(ai_client_factory, monkeypatch) -> None:
    client, created = _build_a_learner_with_history(ai_client_factory, monkeypatch)
    user_id = created["me"]["user"]["id"]
    assert _counts(user_id)["audit_naming_user"] >= 1

    with session_scope() as db:
        audit_total = db.query(AuditLog).count()
    deleted = client.post("/api/me/delete", json={"password": PASSWORD, "confirmation": "DELETE"})
    assert deleted.status_code == 204, deleted.text

    counts = _counts(user_id)
    for key, value in counts.items():
        if key == "audit_naming_user":
            continue
        assert value == 0, f"{key} still holds learner data: {counts}"

    with session_scope() as db:
        assert db.query(AuditLog).count() == audit_total, "audit rows are kept, not deleted"
        anonymised = (
            db.query(AuditLog)
            .filter(AuditLog.target == "deleted-account", AuditLog.actor_user_id.is_(None))
            .count()
        )
    assert anonymised >= 1, "audit rows must stop naming the deleted learner"


def test_public_curriculum_survives_an_account_deletion(ai_client_factory, monkeypatch) -> None:
    client, _created = _build_a_learner_with_history(ai_client_factory, monkeypatch)
    with session_scope() as db:
        before = (db.query(Objective).count(), db.query(Lesson).count(), db.query(Item).count())

    client.post("/api/me/delete", json={"password": PASSWORD, "confirmation": "DELETE"})

    with session_scope() as db:
        after = (db.query(Objective).count(), db.query(Lesson).count(), db.query(Item).count())
    assert after == before, "curriculum rows are shared and must never be deleted with a learner"

    public = TestClient(client.app).get("/api/curriculum/paths")
    assert public.status_code == 200, "the curriculum stays readable without any session"
    assert public.json(), "the surviving curriculum must still be served"


def test_a_deleted_account_cannot_sign_in_or_reuse_the_session(ai_client_factory, monkeypatch) -> None:
    client, _created = _build_a_learner_with_history(ai_client_factory, monkeypatch)
    cookies = dict(client.cookies)
    client.post("/api/me/delete", json={"password": PASSWORD, "confirmation": "DELETE"})

    login = client.post(
        "/api/auth/login",
        json={"email": "lifecycle@example.com", "password": PASSWORD},
    )
    assert login.status_code in {401, 403, 422}

    # The deleted learner's cookie must not open a session even if a client replays it.
    replayer = TestClient(client.app)
    replayer.cookies.update(cookies)
    assert replayer.get("/api/auth/me").status_code == 401


@pytest.mark.parametrize("confirmation", ["delete", "", "DELETE ME"])
def test_deletion_requires_the_exact_confirmation_phrase(
    ai_client_factory, monkeypatch, confirmation: str
) -> None:
    client, _created = _build_a_learner_with_history(ai_client_factory, monkeypatch)
    response = client.post("/api/me/delete", json={"password": PASSWORD, "confirmation": confirmation})
    assert response.status_code in {400, 409, 422}
    assert client.get("/api/auth/me").status_code == 200, "a refused deletion must change nothing"
