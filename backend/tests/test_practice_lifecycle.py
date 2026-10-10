"""Practice sessions have an explicit completion target.

Regression: `complete` marked the roadmap item done even for a session with zero answers (the UI's
"Back" button called it), and `PracticeStartIn.size` was applied per request, so the session's
effective length changed from call to call.
"""

from __future__ import annotations

from fastapi.testclient import TestClient

from app.curriculum.registry import item_index
from tests.conftest import _correct_response, _wrong_response, create_goal, register

PATH = "python-foundations"


def _plan_item_for_practice(client: TestClient) -> dict:
    """A learner with a goal and a published plan, plus the learner's current plan item."""
    register(client)
    goal = create_goal(client)
    generated = client.post(f"/api/plans/goals/{goal['id']}")
    assert generated.status_code in (200, 201), generated.text
    body = generated.json()
    item = body["plan"]["weeks"][0]["items"][0]
    assert item["lesson_id"] is None or item["kind"] in {"learn", "practice", "assess"}
    return item


def _start(client: TestClient, item: dict, *, size: int = 5) -> dict:
    created = client.post(
        "/api/practice/sessions",
        json={
            "objective_id": item["objective_id"],
            "plan_item_id": item["id"],
            "size": size,
        },
    )
    assert created.status_code == 201, created.text
    return created.json()


def _answer(client: TestClient, session_id: str, item: dict, *, correct: bool = True) -> dict:
    payload = _correct_response(item) if correct else _wrong_response(item)
    response = client.post(
        f"/api/practice/sessions/{session_id}/answers",
        json={"item_id": item["id"], "response": payload, "used_hint": False},
    )
    assert response.status_code == 200, response.text
    return response.json()


def _answer_everything(client: TestClient, session: dict) -> dict:
    current = session
    while current["item"] is not None:
        current = _answer(client, current["session_id"], current["item"])
    return current


def _plan_item_status(client: TestClient, plan_item_id: str) -> str:
    active = client.get("/api/plans/active")
    assert active.status_code == 200, active.text
    body = active.json()
    plan = body.get("plan", body)
    for week in plan["weeks"]:
        for item in week["items"]:
            if item["id"] == plan_item_id:
                return item["status"]
    raise AssertionError(f"plan item {plan_item_id} disappeared from the active plan")


# --------------------------------------------------------------------------------------
# Target persistence and stability
# --------------------------------------------------------------------------------------


def test_the_session_target_is_persisted_and_does_not_change_between_requests(
    client: TestClient,
) -> None:
    item = _plan_item_for_practice(client)

    created = _start(client, item, size=2)
    assert created["total"] == 2, "the requested target must be honoured when the pool allows it"
    assert created["target_items"] == 2
    assert created["answered"] == 0
    assert created["status"] == "in_progress"

    # A later read must not apply a different default (the old code used size=5 on GET).
    fetched = client.get(f"/api/practice/sessions/{created['session_id']}")
    assert fetched.status_code == 200, fetched.text
    assert fetched.json()["total"] == 2
    assert fetched.json()["item"]["id"] == created["item"]["id"], "the next item must be stable"

    answered = _answer(client, created["session_id"], created["item"])
    assert answered["answered"] == 1
    assert answered["total"] == 2
    assert answered["item"] is not None

    fetched_again = client.get(f"/api/practice/sessions/{created['session_id']}").json()
    assert fetched_again["total"] == 2
    assert fetched_again["answered"] == 1
    assert fetched_again["item"]["id"] == answered["item"]["id"]


def test_a_target_larger_than_the_item_pool_is_clamped_to_the_pool(client: TestClient) -> None:
    item = _plan_item_for_practice(client)
    pool = [row for row in item_index(PATH).values() if row["objective_id"] == item["objective_id"]]
    assert pool, "the objective under test must have authored items"

    created = _start(client, item, size=20)
    assert created["target_items"] == len(pool)
    assert created["total"] == len(pool)

    answered = _answer_everything(client, created)
    assert answered["answered"] == len(pool)
    assert answered["item"] is None, "the pool is exhausted, not silently extended"


def test_answering_an_item_outside_the_session_plan_is_rejected(client: TestClient) -> None:
    item = _plan_item_for_practice(client)
    created = _start(client, item, size=1)
    planned = created["item"]["id"]

    other = next(
        row["id"]
        for row in item_index(PATH).values()
        if row["objective_id"] == item["objective_id"] and row["id"] != planned
    )
    response = client.post(
        f"/api/practice/sessions/{created['session_id']}/answers",
        json={"item_id": other, "response": {"text": "anything"}, "used_hint": False},
    )
    assert response.status_code == 409, response.text

    state = client.get(f"/api/practice/sessions/{created['session_id']}").json()
    assert state["answered"] == 0, "a rejected answer must not be recorded"


# --------------------------------------------------------------------------------------
# Completion semantics
# --------------------------------------------------------------------------------------


def test_an_untouched_session_cannot_complete_its_plan_item(client: TestClient) -> None:
    item = _plan_item_for_practice(client)
    created = _start(client, item, size=3)

    completed = client.post(f"/api/practice/sessions/{created['session_id']}/complete")
    assert completed.status_code == 409, completed.text
    assert _plan_item_status(client, item["id"]) == "pending"

    state = client.get(f"/api/practice/sessions/{created['session_id']}").json()
    assert state["status"] == "in_progress"


def test_a_partially_answered_session_cannot_complete_its_plan_item(client: TestClient) -> None:
    item = _plan_item_for_practice(client)
    created = _start(client, item, size=3)
    answered = _answer(client, created["session_id"], created["item"])
    assert answered["answered"] == 1

    completed = client.post(f"/api/practice/sessions/{created['session_id']}/complete")
    assert completed.status_code == 409, completed.text
    assert _plan_item_status(client, item["id"]) == "pending"

    state = client.get(f"/api/practice/sessions/{created['session_id']}").json()
    assert state["status"] == "in_progress"
    assert state["answered"] == 1, "the recorded answer is preserved when completion is refused"

    evidence = client.get("/api/practice/progress/evidence").json()
    assert any(row["kind"] == "practice" for row in evidence)


def test_a_fully_answered_session_completes_the_plan_item_once(client: TestClient) -> None:
    item = _plan_item_for_practice(client)
    created = _start(client, item, size=3)
    _answer_everything(client, created)

    completed = client.post(f"/api/practice/sessions/{created['session_id']}/complete")
    assert completed.status_code == 200, completed.text
    body = completed.json()
    assert body["status"] == "completed"
    assert body["item"] is None
    assert _plan_item_status(client, item["id"]) == "completed"

    # Repeating the request must not change anything, and must not be reported as success.
    repeated = client.post(f"/api/practice/sessions/{created['session_id']}/complete")
    assert repeated.status_code == 409, repeated.text
    assert _plan_item_status(client, item["id"]) == "completed"


def test_completing_a_session_does_not_establish_mastery(client: TestClient) -> None:
    item = _plan_item_for_practice(client)
    created = _start(client, item, size=3)
    _answer_everything(client, created)
    completed = client.post(f"/api/practice/sessions/{created['session_id']}/complete")
    assert completed.status_code == 200, completed.text

    mastery = client.get("/api/practice/progress/mastery").json()
    entry = next(row for row in mastery if row["objective_id"] == item["objective_id"])
    assert entry["phase"] == "acquiring", "an activity is not mastery"
    assert entry["unassisted_successes"] == 3
    assert entry["retrievability"] is None
    assert entry["needs_review"] is False


# --------------------------------------------------------------------------------------
# Leaving a session
# --------------------------------------------------------------------------------------


def test_abandoning_keeps_the_answers_and_leaves_the_plan_item_pending(client: TestClient) -> None:
    item = _plan_item_for_practice(client)
    created = _start(client, item, size=3)
    _answer(client, created["session_id"], created["item"], correct=False)

    abandoned = client.post(f"/api/practice/sessions/{created['session_id']}/abandon")
    assert abandoned.status_code == 200, abandoned.text
    body = abandoned.json()
    assert body["status"] == "abandoned"
    assert body["item"] is None
    assert _plan_item_status(client, item["id"]) == "pending"

    state = client.get(f"/api/practice/sessions/{created['session_id']}").json()
    assert state["answered"] == 1, "leaving must not discard recorded answers"
    evidence = client.get("/api/practice/progress/evidence").json()
    assert any(row["kind"] == "practice" and row["outcome"] == "failure" for row in evidence)

    # Nothing may move an abandoned session any more.
    further = client.post(
        f"/api/practice/sessions/{created['session_id']}/answers",
        json={"item_id": created["item"]["id"], "response": _correct_response(created["item"])},
    )
    assert further.status_code == 409, further.text
    again = client.post(f"/api/practice/sessions/{created['session_id']}/abandon")
    assert again.status_code == 409, again.text
    completed = client.post(f"/api/practice/sessions/{created['session_id']}/complete")
    assert completed.status_code == 409, completed.text
    assert _plan_item_status(client, item["id"]) == "pending"


def test_a_completed_session_cannot_be_abandoned_or_answered(client: TestClient) -> None:
    item = _plan_item_for_practice(client)
    created = _start(client, item, size=3)
    _answer_everything(client, created)
    assert client.post(f"/api/practice/sessions/{created['session_id']}/complete").status_code == 200

    abandoned = client.post(f"/api/practice/sessions/{created['session_id']}/abandon")
    assert abandoned.status_code == 409, abandoned.text
    answered = client.post(
        f"/api/practice/sessions/{created['session_id']}/answers",
        json={"item_id": created["item"]["id"], "response": _correct_response(created["item"])},
    )
    assert answered.status_code == 409, answered.text
    assert _plan_item_status(client, item["id"]) == "completed"
