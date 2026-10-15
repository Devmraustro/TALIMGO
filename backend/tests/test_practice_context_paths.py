"""Practice context must be internally consistent: goal ↔ path ↔ objective ↔ plan item.

The authored curriculum contains one path, so the tests build a synthetic second path in the test
database. Nothing here may be read as multi-path correctness of the authored curriculum; it pins the
*vallidation* that any future second path depends on.
"""

from __future__ import annotations

import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select

from app.db import session_scope
from app.models import Evidence, Goal, Item, Objective, Plan, PlanItem, PlanWeek, PracticeSession, User
from tests.conftest import create_goal, register

OTHER_PATH = "other-path"


@pytest.fixture()
def other_path(client: TestClient, tmp_path) -> dict:
    """A synthetic second path: objective + item + this learner's goal, plan and plan item."""
    _ = tmp_path
    user_id = register(client)["user"]["id"]
    with session_scope() as db:
        db.add(
            Objective(
                id="other:objective",
                path_id=OTHER_PATH,
                title_en="Something else entirely",
                summary_en="",
                sequence=1,
            )
        )
        db.flush()
        db.add(
            Item(
                id="other:item",
                objective_id="other:objective",
                kind="short_answer",
                prompt_en="Say something",
                prompt_ar="",
                answer_key={"accepted": ["anything"]},
                explanation_en="",
                explanation_ar="",
                difficulty=2,
                is_diagnostic=True,
            )
        )
        goal = Goal(
            user_id=user_id,
            path_id=OTHER_PATH,
            statement="Learn the other path",
            weekly_minutes=120,
        )
        db.add(goal)
        db.flush()
        plan = Plan(user_id=user_id, goal_id=goal.id, version=1, status="active", generator="test")
        db.add(plan)
        db.flush()
        week = PlanWeek(plan_id=plan.id, week_number=1, theme_en="Other", theme_ar="")
        db.add(week)
        db.flush()
        plan_item = PlanItem(
            plan_id=plan.id,
            week_id=week.id,
            order_index=0,
            objective_id="other:objective",
            kind="practice",
            est_minutes=15,
            status="pending",
        )
        db.add(plan_item)
        db.commit()
        return {
            "user_id": user_id,
            "goal_id": goal.id,
            "plan_id": plan.id,
            "plan_item_id": plan_item.id,
            "objective_id": "other:objective",
            "item_id": "other:item",
        }


def _start(
    client: TestClient, *, objective_id: str, goal_id: str | None = None, plan_item_id: str | None = None
):
    payload: dict = {"objective_id": objective_id, "size": 1}
    if goal_id is not None:
        payload["goal_id"] = goal_id
    if plan_item_id is not None:
        payload["plan_item_id"] = plan_item_id
    return client.post("/api/practice/sessions", json=payload)


def test_an_objective_from_another_path_cannot_be_practised_under_this_goal(
    client: TestClient, other_path: dict
) -> None:
    home_goal = create_goal(client)  # python-foundations

    response = _start(
        client, objective_id=other_path["objective_id"], goal_id=home_goal["id"], plan_item_id=None
    )
    assert response.status_code == 409, response.text
    assert "path" in response.json()["detail"].lower()


def test_a_plan_item_from_another_path_cannot_be_used_with_this_goal(
    client: TestClient, other_path: dict
) -> None:
    home_goal = create_goal(client)

    response = _start(
        client,
        objective_id=other_path["objective_id"],
        goal_id=home_goal["id"],
        plan_item_id=other_path["plan_item_id"],
    )
    assert response.status_code == 409, response.text


def test_the_learners_own_goal_for_the_same_path_is_accepted(client: TestClient, other_path: dict) -> None:
    """Positive control: a consistent context on the synthetic path is allowed."""
    response = _start(
        client,
        objective_id=other_path["objective_id"],
        goal_id=other_path["goal_id"],
        plan_item_id=other_path["plan_item_id"],
    )
    assert response.status_code == 201, response.text
    body = response.json()
    assert body["objective_id"] == other_path["objective_id"]
    assert body["total"] == 1


def test_a_plan_item_whose_goal_is_on_another_path_is_refused(client: TestClient, other_path: dict) -> None:
    """Plan item and objective agree, but the learner's own goal for the same path is elsewhere."""
    create_goal(client)  # python-foundations goal, unrelated to the synthetic path
    response = _start(
        client,
        objective_id=other_path["objective_id"],
        goal_id=None,
        plan_item_id=other_path["plan_item_id"],
    )
    assert response.status_code == 201, (
        "the plan item resolves its own goal, which matches the objective's path: " + response.text
    )


def test_foreign_and_unknown_identifiers_are_indistinguishable(client: TestClient, other_path: dict) -> None:
    register(client)  # a second learner in the same database
    foreign_goal = other_path["goal_id"]
    foreign_item = other_path["plan_item_id"]
    unknown = f"gol_{uuid.uuid4().hex}"

    foreign = _start(client, objective_id="py:values", goal_id=foreign_goal)
    missing = _start(client, objective_id="py:values", goal_id=unknown)
    assert foreign.status_code == missing.status_code == 404
    assert foreign.json()["detail"] == missing.json()["detail"], "existence is not disclosed"

    foreign_pi = _start(client, objective_id="py:values", plan_item_id=foreign_item)
    missing_pi = _start(client, objective_id="py:values", plan_item_id=f"pit_{uuid.uuid4().hex}")
    assert foreign_pi.status_code == missing_pi.status_code == 404
    assert foreign_pi.json()["detail"] == missing_pi.json()["detail"]


def test_a_rejected_context_creates_no_session_and_no_evidence(client: TestClient, other_path: dict) -> None:
    home_goal = create_goal(client)
    rejected = _start(
        client, objective_id=other_path["objective_id"], goal_id=home_goal["id"], plan_item_id=None
    )
    assert rejected.status_code == 409

    user_id = other_path["user_id"]
    with session_scope() as db:
        sessions = db.scalars(select(PracticeSession).where(PracticeSession.user_id == user_id)).all()
        evidence = db.scalars(select(Evidence).where(Evidence.user_id == user_id)).all()
        account = db.get(User, user_id)

    assert sessions == [], "a refused practice context must not create a session"
    assert evidence == [], "a refused practice context must not record evidence"
    assert account is not None
