"""The starting check must accept only the item it actually asked for.

Code-review finding: ``answer_diagnostic()`` verified the attempt was in progress, that the item
existed and that it had not been answered before — but not that it was the *next expected* item, that
it belonged to the path of the attempt's goal, or that it was eligible for diagnostic use. A caller
could therefore submit any item, in any order, from anywhere, and have it graded, recorded as
evidence and (potentially) counted in placement.

Every rejection must leave the database exactly as it was: no response row, no evidence, no cursor
movement. The tests below check both the status code and the unchanged state.
"""

from __future__ import annotations

from fastapi.testclient import TestClient
from sqlalchemy import select

from tests.conftest import _correct_response, create_goal, register

LEARNER = "diagnostic-integrity@example.com"


def _snapshot(attempt_id: str) -> tuple[int, int, str, int]:
    """(responses, evidence rows, attempt status, answered items) straight from the database."""
    from app.db import session_scope
    from app.models import DiagnosticAttempt, DiagnosticResponse, Evidence, User

    with session_scope() as db:
        attempt = db.get(DiagnosticAttempt, attempt_id)
        assert attempt is not None
        user = db.get(User, attempt.user_id)
        responses = len(
            db.scalars(select(DiagnosticResponse.id).where(DiagnosticResponse.attempt_id == attempt_id)).all()
        )
        evidence = len(db.scalars(select(Evidence.id).where(Evidence.user_id == user.id)).all())
        return responses, evidence, attempt.status, len(attempt.item_ids or [])


def _start(client: TestClient) -> dict:
    register(client, email=LEARNER)
    goal = create_goal(client)
    response = client.post(f"/api/diagnostic/goals/{goal['id']}")
    assert response.status_code == 201, response.text
    return {"goal": goal, "state": response.json()}


def _answer(client: TestClient, attempt_id: str, item: dict, response: dict) -> object:
    return client.post(
        f"/api/diagnostic/{attempt_id}/answers",
        json={"item_id": item["id"], "response": response, "confidence": "unsure"},
    )


def _other_diagnostic_item(client: TestClient, *, exclude: set[str], path_id: str = "python-foundations"):
    from app.db import session_scope
    from app.models import Item, Objective

    with session_scope() as db:
        rows = db.execute(
            select(Item)
            .join(Objective, Item.objective_id == Objective.id)
            .where(Objective.path_id == path_id, Item.is_diagnostic.is_(True))
        ).scalars()
        for item in rows:
            if item.id not in exclude:
                return {"id": item.id, "objective_id": item.objective_id, "kind": item.kind}
    raise AssertionError("no other diagnostic item available")


def _non_diagnostic_item(path_id: str = "python-foundations"):
    from app.db import session_scope
    from app.models import Item, Objective

    with session_scope() as db:
        item = db.scalar(
            select(Item)
            .join(Objective, Item.objective_id == Objective.id)
            .where(Objective.path_id == path_id, Item.is_diagnostic.is_(False))
            .limit(1)
        )
        assert item is not None, "the curriculum must contain items that are not diagnostic"
        return {"id": item.id, "objective_id": item.objective_id, "kind": item.kind}


def test_diagnostic_rejects_an_out_of_order_item_without_recording_evidence(client) -> None:
    started = _start(client)
    attempt_id = started["state"]["attempt_id"]
    expected = started["state"]["current_item"]

    intruder_item = _other_diagnostic_item(client, exclude={expected["id"]})
    before = _snapshot(attempt_id)

    response = _answer(client, attempt_id, intruder_item, _correct_response(intruder_item))
    assert response.status_code == 409, response.text
    assert "next" in response.json()["detail"].lower() or "order" in response.json()["detail"].lower()
    assert _snapshot(attempt_id) == before, "a rejected answer must not touch the database"

    # The correct item still works afterwards: the rejection did not break the attempt.
    accepted = _answer(client, attempt_id, expected, _correct_response(expected))
    assert accepted.status_code == 200, accepted.text
    assert _snapshot(attempt_id)[0] == 1


def test_diagnostic_rejects_an_item_that_is_not_eligible_for_diagnostics(client) -> None:
    started = _start(client)
    attempt_id = started["state"]["attempt_id"]

    practice_only = _non_diagnostic_item()
    before = _snapshot(attempt_id)

    response = _answer(client, attempt_id, practice_only, {"text": "anything"})
    assert response.status_code == 409, response.text
    assert _snapshot(attempt_id) == before


def test_diagnostic_rejects_an_item_from_another_path(client) -> None:
    started = _start(client)
    attempt_id = started["state"]["attempt_id"]
    before = _snapshot(attempt_id)

    from app.db import session_scope
    from app.models import Item, Objective

    with session_scope() as db:
        db.add(
            Objective(
                id="other:objective",
                path_id="other-path",
                title_en="Something else entirely",
                summary_en="",
                sequence=1,
            )
        )
        db.flush()  # items reference objectives; without this the insert order is not guaranteed
        db.add(
            Item(
                id="other:item",
                objective_id="other:objective",
                kind="short_answer",
                prompt_en="Not part of your path",
                answer_key={"accepted": ["anything"]},
                difficulty=2,
                is_diagnostic=True,
            )
        )
        db.commit()

    response = _answer(client, attempt_id, {"id": "other:item", "kind": "short_answer"}, {"text": "anything"})
    assert response.status_code == 409, response.text
    assert _snapshot(attempt_id) == before


def test_diagnostic_rejects_a_repeated_item_without_recording_more_evidence(client) -> None:
    started = _start(client)
    attempt_id = started["state"]["attempt_id"]
    item = started["state"]["current_item"]

    assert _answer(client, attempt_id, item, _correct_response(item)).status_code == 200
    after_first = _snapshot(attempt_id)
    assert after_first[0] == 1 and after_first[1] == 1

    replay = _answer(client, attempt_id, item, _correct_response(item))
    assert replay.status_code == 409, replay.text
    assert _snapshot(attempt_id) == after_first, "a replay must not add evidence"


def test_diagnostic_rejects_unknown_and_arbitrary_item_ids(client) -> None:
    started = _start(client)
    attempt_id = started["state"]["attempt_id"]
    before = _snapshot(attempt_id)

    for item_id in ("does-not-exist", "", "py:values:q1-something-made-up"):
        response = client.post(
            f"/api/diagnostic/{attempt_id}/answers",
            json={"item_id": item_id, "response": {"text": "x"}, "confidence": "unsure"},
        )
        assert response.status_code == 409, (item_id, response.text)
    assert _snapshot(attempt_id) == before


def test_diagnostic_rejects_every_answer_after_completion(client) -> None:
    started = _start(client)
    attempt_id = started["state"]["attempt_id"]
    item = started["state"]["current_item"]

    answered = _answer(client, attempt_id, item, _correct_response(item))
    assert answered.status_code == 200
    # Finish the check by following the sequence the API itself offered.
    state = answered.json()
    guard = 0
    while not state["completed"] and guard < 20:
        guard += 1
        nxt = state["next_item"]
        assert nxt is not None
        response = _answer(client, attempt_id, nxt, _correct_response(nxt))
        assert response.status_code == 200, response.text
        state = response.json()
    assert state["completed"] is True

    before = _snapshot(attempt_id)
    late = _answer(client, attempt_id, item, _correct_response(item))
    assert late.status_code == 409, late.text
    assert _snapshot(attempt_id) == before
