"""Practice sessions must never reach into another learner's roadmap.

Code-review finding: ``start_practice()`` accepted ``goal_id`` and ``plan_item_id`` without checking
ownership or consistency, and ``POST /api/practice/sessions/{id}/complete`` marks the referenced plan
item completed. Learner B could therefore name learner A's plan item and have A's roadmap silently
tick itself off — and could even attach a session to A's goal.

These tests fail before the fix and pin the behaviour afterwards.
"""

from __future__ import annotations

from fastapi.testclient import TestClient
from sqlalchemy import select

from app.curriculum.registry import item_index
from tests.conftest import _correct_response, answer_diagnostic_until_done, create_goal, register

OWNER = "owner@example.com"
INTRUDER = "intruder@example.com"


def _plan_with_first_item(client: TestClient, goal_id: str) -> tuple[dict, dict]:
    response = client.post(f"/api/plans/goals/{goal_id}")
    assert response.status_code == 200, response.text
    plan = response.json()["plan"]
    return plan, plan["weeks"][0]["items"][0]


def _first_item_status(client: TestClient, plan_id: str) -> str:
    body = client.get(f"/api/plans/{plan_id}")
    assert body.status_code == 200, body.text
    return body.json()["weeks"][0]["items"][0]["status"]


def _two_learners_with_plans(client: TestClient) -> dict:
    """Owner and intruder each have a goal, a finished diagnostic and a published plan."""
    register(client, email=OWNER)
    owner_goal = create_goal(client)
    answer_diagnostic_until_done(client, owner_goal["id"])
    owner_plan, owner_item = _plan_with_first_item(client, owner_goal["id"])

    intruder = TestClient(client.app)
    register(intruder, email=INTRUDER)
    intruder_goal = create_goal(intruder)
    answer_diagnostic_until_done(intruder, intruder_goal["id"])
    intruder_plan, intruder_item = _plan_with_first_item(intruder, intruder_goal["id"])

    return {
        "owner_client": client,
        "owner_goal": owner_goal,
        "owner_plan": owner_plan,
        "owner_item": owner_item,
        "intruder_client": intruder,
        "intruder_goal": intruder_goal,
        "intruder_plan": intruder_plan,
        "intruder_item": intruder_item,
    }


def test_practice_session_cannot_reference_another_learners_plan_item(client) -> None:
    world = _two_learners_with_plans(client)
    intruder: TestClient = world["intruder_client"]

    response = intruder.post(
        "/api/practice/sessions",
        json={
            "objective_id": world["owner_item"]["objective_id"],
            "plan_item_id": world["owner_item"]["id"],
        },
    )
    assert response.status_code == 404, response.text
    detail = response.json()["detail"].lower()
    assert "plan item" in detail and world["owner_item"]["id"].lower() not in detail

    # Nothing changed: neither roadmap item was ticked off by the attempt.
    assert _first_item_status(world["owner_client"], world["owner_plan"]["id"]) == "pending"
    assert _first_item_status(intruder, world["intruder_plan"]["id"]) == "pending"


def test_practice_session_cannot_reference_another_learners_goal(client) -> None:
    world = _two_learners_with_plans(client)
    intruder: TestClient = world["intruder_client"]

    # The intruder uses their own objective, but the owner's goal id.
    response = intruder.post(
        "/api/practice/sessions",
        json={
            "objective_id": world["intruder_item"]["objective_id"],
            "goal_id": world["owner_goal"]["id"],
        },
    )
    assert response.status_code == 404, response.text


def test_practice_session_rejects_a_plan_item_that_belongs_to_another_objective(client) -> None:
    """Even a plan item the learner owns may not be used for a different objective."""
    register(client, email=OWNER)
    goal = create_goal(client)
    answer_diagnostic_until_done(client, goal["id"])
    plan, item = _plan_with_first_item(client, goal["id"])

    other_objective = next(
        objective_id
        for objective_id in (
            "py:strings",
            "py:conditionals",
            "py:loops",
            "py:lists",
            "py:dicts",
            "py:functions",
            "py:modules",
            "py:errors",
        )
        if objective_id != item["objective_id"]
    )
    response = client.post(
        "/api/practice/sessions",
        json={"objective_id": other_objective, "plan_item_id": item["id"]},
    )
    assert response.status_code == 409, response.text
    assert _first_item_status(client, plan["id"]) == "pending"


def test_owner_can_still_complete_their_own_plan_item(client) -> None:
    """Positive control: the legitimate path keeps working — and only after the target is met."""
    register(client, email=OWNER)
    goal = create_goal(client)
    answer_diagnostic_until_done(client, goal["id"])
    plan, item = _plan_with_first_item(client, goal["id"])

    created = client.post(
        "/api/practice/sessions",
        json={
            "objective_id": item["objective_id"],
            "plan_item_id": item["id"],
            "goal_id": goal["id"],
            "size": 2,
        },
    )
    assert created.status_code == 201, created.text
    session = created.json()
    session_id = session["session_id"]
    assert session["total"] == 2

    while session["item"] is not None:
        payload = _correct_response(session["item"])
        answered = client.post(
            f"/api/practice/sessions/{session_id}/answers",
            json={"item_id": session["item"]["id"], "response": payload},
        )
        assert answered.status_code == 200, answered.text
        session = answered.json()

    completed = client.post(f"/api/practice/sessions/{session_id}/complete")
    assert completed.status_code == 200, completed.text
    assert completed.json()["status"] == "completed"
    assert _first_item_status(client, plan["id"]) == "completed"


def test_completing_a_session_cannot_complete_another_learners_plan_item(client) -> None:
    """Defence in depth: even a pre-existing session pointing at a foreign item changes nothing."""
    world = _two_learners_with_plans(client)
    intruder: TestClient = world["intruder_client"]

    from app.db import session_scope
    from app.models import PracticeSession, User

    with session_scope() as db:
        from app.models import PracticeResponse

        intruder_user = db.scalar(select(User).where(User.email == INTRUDER))
        assert intruder_user is not None
        objective_id = world["intruder_item"]["objective_id"]
        planned = [
            row["id"]
            for row in item_index("python-foundations").values()
            if row["objective_id"] == objective_id
        ]
        assert planned, "the objective under test must have authored items"
        session_row = PracticeSession(
            user_id=intruder_user.id,
            goal_id=world["intruder_goal"]["id"],
            plan_item_id=world["owner_item"]["id"],  # written by a bug or an older build
            objective_id=objective_id,
            status="in_progress",
            target_items=len(planned),
            item_ids=planned,
        )
        db.add(session_row)
        db.flush()
        # The completion condition is met, so the ownership check is the only thing standing
        # between this request and another learner's roadmap item.
        for item_id in planned:
            db.add(
                PracticeResponse(
                    session_id=session_row.id,
                    item_id=item_id,
                    objective_id=objective_id,
                    response={"text": "answered"},
                    is_correct=True,
                )
            )
        db.commit()
        session_id = session_row.id

    completed = intruder.post(f"/api/practice/sessions/{session_id}/complete")
    assert completed.status_code == 200, completed.text
    assert completed.json()["status"] == "completed"

    assert _first_item_status(world["owner_client"], world["owner_plan"]["id"]) == "pending", (
        "completing a session must never mark another learner's plan item as completed"
    )
    assert _first_item_status(intruder, world["intruder_plan"]["id"]) == "pending"
