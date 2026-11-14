"""Cross-user authorisation matrix — learner-owned resources.

Every route that takes an identifier for stored learner-owned state is exercised with two
independently authenticated clients sharing one database. The guarantee under test:

  * the owner can read/update their resources;
  * another learner gets 404 (never 403, never data) for the same identifiers;
  * the foreign attempt mutates nothing — verified by direct SQL inspection afterwards;
  * unknown and foreign identifiers are indistinguishable (consistent non-disclosure);
  * the owner's own reads keep working after the foreign attempts (the D.7 regression).

Two clients on the same app instance keep independent cookie jars, so identities cannot blur;
``tests/test_auth_regression.py`` covers the session layer the same way.
"""

from __future__ import annotations

from fastapi.testclient import TestClient
from sqlalchemy import func, select

from app.db import session_scope
from app.models import (
    DiagnosticAttempt,
    Evidence,
    FlashcardState,
    Goal,
    MasteryEstimate,
    Plan,
    PlanItem,
    PracticeSession,
    ProjectSubmission,
)
from tests.conftest import answer_diagnostic_until_done, create_goal, register

USER_A = "user-a@example.com"
USER_B = "user-b@example.com"
PASSWORD = "correct-horse-battery"


def _other_client(client) -> TestClient:
    """A second, independent client on the same app+database with its own cookie jar."""
    other = TestClient(client.app)
    register(other, email=USER_B)
    return other


def _start_practice(client) -> dict:
    response = client.post("/api/practice/sessions", json={"objective_id": "py:values", "size": 2})
    assert response.status_code == 201, response.text
    return response.json()


def _owner_with_plan(client) -> tuple[dict, dict]:
    """Register user A and give them a completed diagnostic plus a generated plan."""
    register(client, email=USER_A)
    goal = create_goal(client)
    answer_diagnostic_until_done(client, goal["id"], correct=True)
    roadmap = client.post(f"/api/plans/goals/{goal['id']}")
    assert roadmap.status_code == 200, roadmap.text
    return goal, roadmap.json()["plan"]


def _plan_item_ids(plan: dict) -> list[str]:
    return [item["id"] for week in plan["weeks"] for item in week["items"]]


def _db_counts() -> dict[str, int]:
    with session_scope() as db:
        return {
            "goals": db.scalar(select(func.count()).select_from(Goal)) or 0,
            "plans": db.scalar(select(func.count()).select_from(Plan)) or 0,
            "plan_items": db.scalar(select(func.count()).select_from(PlanItem)) or 0,
            "diagnostic_attempts": db.scalar(select(func.count()).select_from(DiagnosticAttempt)) or 0,
            "practice_sessions": db.scalar(select(func.count()).select_from(PracticeSession)) or 0,
            "project_submissions": db.scalar(select(func.count()).select_from(ProjectSubmission)) or 0,
            "evidence": db.scalar(select(func.count()).select_from(Evidence)) or 0,
            "mastery_estimates": db.scalar(select(func.count()).select_from(MasteryEstimate)) or 0,
            "flashcard_states": db.scalar(select(func.count()).select_from(FlashcardState)) or 0,
        }


# --------------------------------------------------------------------------------------
# Goals: the D.7 isolation scenario, mapped onto this API's goal-owned resources
# --------------------------------------------------------------------------------------


def test_goal_list_and_active_are_scoped_to_the_owner(client) -> None:
    register(client, email=USER_A)
    goal = create_goal(client)
    other = _other_client(client)

    assert [row["id"] for row in client.get("/api/goals").json()] == [goal["id"]]
    assert client.get("/api/goals/active").json()["id"] == goal["id"]

    assert other.get("/api/goals").json() == []
    assert other.get("/api/goals/active").json() is None


def test_d7_full_sequence_foreign_access_then_owner_reads(client) -> None:
    """D.7 regression: B attacks A's resources; A's own access must survive unchanged."""
    register(client, email=USER_A)
    goal = create_goal(client)
    before = _db_counts()

    other = _other_client(client)
    foreign_attempts = [
        other.post(f"/api/diagnostic/goals/{goal['id']}"),
        other.post(f"/api/plans/goals/{goal['id']}"),
        other.post(
            "/api/practice/sessions",
            json={"objective_id": "py:values", "goal_id": goal["id"], "size": 1},
        ),
        other.post(
            "/api/projects/py:project:wordcount/submissions",
            json={
                "artifact_text": "x" * 400,
                "reflection_text": "y" * 80,
                "rubric_checks": {},
                "goal_id": goal["id"],
            },
        ),
    ]
    assert [response.status_code for response in foreign_attempts] == [404, 404, 404, 404]
    assert _db_counts() == before, "a foreign attempt must not create rows"

    # Same client, unchanged identity.
    listed = client.get("/api/goals")
    assert listed.status_code == 200
    assert [row["id"] for row in listed.json()] == [goal["id"]]
    assert client.get("/api/goals/active").json()["id"] == goal["id"]

    # A newly authenticated client for the same account (D.7 scenario F).
    fresh = TestClient(client.app)
    login = fresh.post("/api/auth/login", json={"email": USER_A, "password": PASSWORD})
    assert login.status_code == 200
    assert [row["id"] for row in fresh.get("/api/goals").json()] == [goal["id"]]

    # Direct SQL: the row exists and is still owned by A (D.7 scenario H).
    owner_id = client.get("/api/auth/me").json()["user"]["id"]
    with session_scope() as db:
        row = db.get(Goal, goal["id"])
        assert row is not None
        assert row.user_id == owner_id


def test_dashboard_never_shows_another_learners_goal(client) -> None:
    register(client, email=USER_A)
    create_goal(client)
    other = _other_client(client)
    assert other.get("/api/dashboard").json()["goal"] is None


# --------------------------------------------------------------------------------------
# Plans
# --------------------------------------------------------------------------------------


def test_plan_get_is_owner_only_and_foreign_reads_do_not_mutate(client) -> None:
    _goal, plan = _owner_with_plan(client)
    plan_id = plan["id"]
    before_items = _db_counts()["plan_items"]

    other = _other_client(client)
    assert other.get(f"/api/plans/{plan_id}").status_code == 404
    assert other.get(f"/api/plans/{plan_id}").json() == {"detail": "Not found."}

    with session_scope() as db:
        row = db.get(Plan, plan_id)
        assert row is not None
        assert row.status == "active"
        owner_id = client.get("/api/auth/me").json()["user"]["id"]
        assert row.user_id == owner_id
    assert _db_counts()["plan_items"] == before_items

    # The owner still reads the plan afterwards.
    assert client.get(f"/api/plans/{plan_id}").status_code == 200


def test_plan_active_schedule_and_reschedule_are_scoped(client) -> None:
    _owner_with_plan(client)
    other = _other_client(client)

    assert other.get("/api/plans/active").json() is None
    assert other.get("/api/plans/active/schedule").status_code == 404
    assert other.post("/api/plans/active/reschedule").status_code == 404


def test_plan_generation_for_a_foreign_goal_creates_no_plan(client) -> None:
    register(client, email=USER_A)
    goal = create_goal(client)
    before = _db_counts()["plans"]

    other = _other_client(client)
    assert other.post(f"/api/plans/goals/{goal['id']}").status_code == 404
    assert _db_counts()["plans"] == before


# --------------------------------------------------------------------------------------
# Diagnostic attempts
# --------------------------------------------------------------------------------------


def test_diagnostic_attempt_access_is_owner_only(client) -> None:
    register(client, email=USER_A)
    goal = create_goal(client)
    attempt = client.post(f"/api/diagnostic/goals/{goal['id']}")
    assert attempt.status_code == 201
    attempt_id = attempt.json()["attempt_id"]

    other = _other_client(client)
    assert other.get(f"/api/diagnostic/{attempt_id}").status_code == 404
    answered = other.post(
        f"/api/diagnostic/{attempt_id}/answers",
        json={"item_id": "py:values:q1", "response": {"option_id": "a"}, "confidence": "unsure"},
    )
    assert answered.status_code == 404

    # The attempt is untouched: still in progress, nothing answered.
    state = client.get(f"/api/diagnostic/{attempt_id}").json()
    assert state["status"] == "in_progress"
    assert state["answered_items"] == 0
    with session_scope() as db:
        row = db.get(DiagnosticAttempt, attempt_id)
        assert row is not None and row.cursor == 0


def test_diagnostic_start_for_a_foreign_goal_creates_no_attempt(client) -> None:
    register(client, email=USER_A)
    goal = create_goal(client)
    before = _db_counts()["diagnostic_attempts"]

    other = _other_client(client)
    assert other.post(f"/api/diagnostic/goals/{goal['id']}").status_code == 404
    assert _db_counts()["diagnostic_attempts"] == before


def test_diagnostic_history_lists_only_own_attempts(client) -> None:
    register(client, email=USER_A)
    goal = create_goal(client)
    client.post(f"/api/diagnostic/goals/{goal['id']}")
    other = _other_client(client)
    assert other.get("/api/diagnostic").json() == []


# --------------------------------------------------------------------------------------
# Practice sessions
# --------------------------------------------------------------------------------------


def test_practice_session_get_answer_complete_abandon_are_owner_only(client) -> None:
    register(client, email=USER_A)
    session = _start_practice(client)
    other = _other_client(client)

    assert other.get(f"/api/practice/sessions/{session['session_id']}").status_code == 404
    answered = other.post(
        f"/api/practice/sessions/{session['session_id']}/answers",
        json={"item_id": session["item"]["id"], "response": {"option_id": "a"}, "used_hint": False},
    )
    assert answered.status_code == 404
    assert other.post(f"/api/practice/sessions/{session['session_id']}/complete").status_code == 404
    assert other.post(f"/api/practice/sessions/{session['session_id']}/abandon").status_code == 404

    # Untouched and still usable by the owner.
    state = client.get(f"/api/practice/sessions/{session['session_id']}").json()
    assert state["status"] == "in_progress"
    assert state["answered"] == 0


def test_practice_session_with_a_foreign_goal_or_plan_item_is_rejected(client) -> None:
    _goal, plan = _owner_with_plan(client)
    plan_item_id = _plan_item_ids(plan)[0]
    goal = client.get("/api/goals").json()[0]

    other = _other_client(client)
    before = _db_counts()["practice_sessions"]
    with_goal = other.post(
        "/api/practice/sessions",
        json={"objective_id": "py:values", "goal_id": goal["id"], "size": 1},
    )
    with_plan_item = other.post(
        "/api/practice/sessions",
        json={"objective_id": "py:values", "plan_item_id": plan_item_id, "size": 1},
    )
    assert with_goal.status_code == 404
    assert with_plan_item.status_code == 404
    assert _db_counts()["practice_sessions"] == before


def test_practice_progress_and_evidence_are_scoped(client) -> None:
    register(client, email=USER_A)
    _start_practice(client)
    other = _other_client(client)
    assert other.get("/api/practice/progress/mastery").json() == []
    assert other.get("/api/practice/progress/evidence").json() == []


def test_flashcards_require_the_learner_to_have_seen_the_item(client) -> None:
    register(client, email=USER_A)
    session = _start_practice(client)
    answered = client.post(
        f"/api/practice/sessions/{session['session_id']}/answers",
        json={"item_id": session["item"]["id"], "response": {"option_id": "a"}, "used_hint": False},
    )
    assert answered.status_code == 200, answered.text

    owner_id = client.get("/api/auth/me").json()["user"]["id"]
    other = _other_client(client)
    # Same item id, but B has never seen it: indistinguishable from unknown.
    rate = other.post(f"/api/practice/flashcards/{session['item']['id']}/rate", json={"rating": "good"})
    assert rate.status_code == 404
    assert other.get("/api/practice/flashcards").json()["cards"] == []
    with session_scope() as db:
        rows = db.scalars(select(FlashcardState).where(FlashcardState.item_id == session["item"]["id"])).all()
        assert all(row.user_id == owner_id for row in rows)


# --------------------------------------------------------------------------------------
# Projects
# --------------------------------------------------------------------------------------


def test_project_submission_with_foreign_context_is_rejected(client) -> None:
    _goal, plan = _owner_with_plan(client)
    plan_item_id = _plan_item_ids(plan)[0]
    goal = client.get("/api/goals").json()[0]

    other = _other_client(client)
    before = _db_counts()["project_submissions"]
    payload = {
        "artifact_text": "x" * 400,
        "reflection_text": "y" * 80,
        "rubric_checks": {},
    }
    with_goal = other.post(
        "/api/projects/py:project:wordcount/submissions", json={**payload, "goal_id": goal["id"]}
    )
    with_plan_item = other.post(
        "/api/projects/py:project:wordcount/submissions",
        json={**payload, "plan_item_id": plan_item_id},
    )
    assert with_goal.status_code == 404
    assert with_plan_item.status_code == 404
    assert _db_counts()["project_submissions"] == before


def test_project_portfolio_and_history_are_scoped(client) -> None:
    register(client, email=USER_A)
    other = _other_client(client)
    assert other.get("/api/projects/submissions/mine").json() == []


# --------------------------------------------------------------------------------------
# Account surface
# --------------------------------------------------------------------------------------


def test_export_and_consents_contain_only_the_callers_data(client) -> None:
    register(client, email=USER_A)
    goal = create_goal(client)
    other = _other_client(client)

    exported = other.get("/api/me/export").json()
    # DataExportOut wraps the service payload: {"exported_at", "account": {...nested...}, "notice"}.
    # The nested shape is the implemented schema (documented in the report); assert ownership, not style.
    assert exported["account"]["account"]["email"] == USER_B
    blob = str(exported)
    assert goal["statement"] not in blob
    assert USER_A not in blob

    consents = other.get("/api/me/consents").json()
    assert {row["kind"] for row in consents} <= {"account", "ai_processing", "analytics", "marketing"}


def test_tutor_threads_are_scoped_to_the_caller(client) -> None:
    register(client, email=USER_A)
    other = _other_client(client)
    assert other.get("/api/tutor/threads").json() == []
    assert other.get("/api/tutor/usage").json()["used_today"] == 0


# --------------------------------------------------------------------------------------
# Consistent non-disclosure: foreign and missing identifiers look identical
# --------------------------------------------------------------------------------------


def test_foreign_and_missing_plan_ids_return_identical_404(client) -> None:
    _goal, plan = _owner_with_plan(client)
    other = _other_client(client)

    foreign = other.get(f"/api/plans/{plan['id']}")
    missing = other.get("/api/plans/pln_doesnotexist0000000000")
    assert foreign.status_code == missing.status_code == 404
    assert foreign.json() == missing.json()


def test_foreign_and_missing_diagnostic_attempts_return_identical_404(client) -> None:
    register(client, email=USER_A)
    goal = create_goal(client)
    attempt = client.post(f"/api/diagnostic/goals/{goal['id']}")
    attempt_id = attempt.json()["attempt_id"]
    other = _other_client(client)

    foreign = other.get(f"/api/diagnostic/{attempt_id}")
    missing = other.get("/api/diagnostic/dia_doesnotexist0000000000")
    assert foreign.status_code == missing.status_code == 404
    assert foreign.json() == missing.json()


def test_foreign_and_missing_practice_sessions_return_identical_404(client) -> None:
    register(client, email=USER_A)
    session = _start_practice(client)
    other = _other_client(client)

    foreign = other.get(f"/api/practice/sessions/{session['session_id']}")
    missing = other.get("/api/practice/sessions/prs_doesnotexist0000000000")
    assert foreign.status_code == missing.status_code == 404
    assert foreign.json() == missing.json()


def test_error_bodies_never_echo_foreign_identifiers(client) -> None:
    register(client, email=USER_A)
    goal = create_goal(client)
    other = _other_client(client)
    for response in (
        other.post(f"/api/plans/goals/{goal['id']}"),
        other.post(f"/api/diagnostic/goals/{goal['id']}"),
        other.post(
            "/api/practice/sessions",
            json={"objective_id": "py:values", "goal_id": goal["id"], "size": 1},
        ),
    ):
        assert response.status_code == 404
        body = response.text
        assert goal["id"] not in body
        assert USER_A not in body
        assert goal["statement"] not in body


# --------------------------------------------------------------------------------------
# Admin surface: learners get 404, never 403, and never data
# --------------------------------------------------------------------------------------


def test_admin_routes_are_invisible_to_learners(client) -> None:
    register(client, email=USER_A)
    for path in ("/api/admin/stats", "/api/admin/audit-log", "/api/admin/curriculum/inventory"):
        assert client.get(path).status_code == 404
    assert client.post("/api/admin/curriculum/reload").status_code == 404


def test_admin_routes_are_visible_to_admins(client) -> None:
    register(client, email=USER_A)
    with session_scope() as db:
        from app.models import User

        me = db.scalar(select(User.id).where(User.email == USER_A))
        user = db.get(User, me)
        user.role = "admin"
        db.commit()

    response = client.get("/api/admin/stats")
    assert response.status_code == 200
    assert set(response.json()) == {"learners", "evidence_records"}
