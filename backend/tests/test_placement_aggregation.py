"""Placement must combine several answers about one objective by an explicit, deterministic rule.

Code-review finding: ``_placement()`` only ever *upgraded* an objective's status. An incorrect answer
that arrived after a correct one was silently discarded, so a learner who answered a hard item
correctly and then missed an easier one was still placed as if they knew the material.

Rule under test (recorded in the module docstring of ``app/services/assessment.py``):
  * any incorrect answer about an objective leaves it at ``needs_work`` — a demonstrated failure is
    decisive inside one short check, and the roadmap will teach it properly;
  * otherwise the objective is ``assumed_known`` if the hardest correct answer was difficulty >= 3,
    and ``likely_known`` if everything answered was easy;
  * counts and the hardest difficulty are reported so the placement is explainable.
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

from fastapi.testclient import TestClient

from tests.conftest import create_goal, register

LEARNER_LOCAL_PART = "placement"


def _attempt_id(client: TestClient) -> str:
    """A fresh learner each call: registration is once per email, and tests may need several."""
    import uuid

    register(client, email=f"{LEARNER_LOCAL_PART}-{uuid.uuid4().hex[:8]}@example.com")
    goal = create_goal(client)
    response = client.post(f"/api/diagnostic/goals/{goal['id']}")
    assert response.status_code == 201, response.text
    return response.json()["attempt_id"]


def _placement_for(client: TestClient, rows: list[tuple[str, bool, int]]) -> dict:
    """Insert diagnostic responses in order, then compute placement through the service."""
    attempt_id = _attempt_id(client)

    from app.db import session_scope
    from app.models import DiagnosticAttempt, DiagnosticResponse
    from app.services.assessment import _placement

    base = datetime(2026, 3, 1, 12, 0, tzinfo=UTC)
    with session_scope() as db:
        attempt = db.get(DiagnosticAttempt, attempt_id)
        assert attempt is not None
        for index, (objective_id, is_correct, difficulty) in enumerate(rows):
            db.add(
                DiagnosticResponse(
                    attempt_id=attempt_id,
                    item_id=f"synthetic-{index}",
                    objective_id=objective_id,
                    response={"text": "x"},
                    is_correct=is_correct,
                    difficulty=difficulty,
                    answered_at=base + timedelta(minutes=index),
                )
            )
        db.commit()
        db.refresh(attempt)
        return _placement(db, attempt)


def test_all_correct_easy_answers_are_likely_known(client) -> None:
    placement = _placement_for(client, [("py:values", True, 1), ("py:values", True, 2)])
    entry = placement["objectives"]["py:values"]
    assert entry["status"] == "likely_known"
    assert entry["correct"] == 2 and entry["incorrect"] == 0
    assert entry["difficulty"] == 2


def test_a_hard_correct_answer_is_assumed_known(client) -> None:
    placement = _placement_for(client, [("py:values", True, 4)])
    entry = placement["objectives"]["py:values"]
    assert entry["status"] == "assumed_known"
    assert entry["confidence"] == "high"


def test_correct_then_incorrect_is_not_silently_ignored(client) -> None:
    placement = _placement_for(client, [("py:values", True, 4), ("py:values", False, 2)])
    entry = placement["objectives"]["py:values"]
    assert entry["status"] == "needs_work", "a later incorrect answer must change the placement"
    assert entry["incorrect"] == 1 and entry["correct"] == 1
    assert placement["summary"]["assumed_known"] == 0


def test_incorrect_then_correct_stays_needs_work(client) -> None:
    placement = _placement_for(client, [("py:values", False, 1), ("py:values", True, 4)])
    entry = placement["objectives"]["py:values"]
    assert entry["status"] == "needs_work"
    assert entry["difficulty"] == 4, "the hardest item presented is still reported"


def test_mixed_difficulty_correct_answers_use_the_hardest(client) -> None:
    placement = _placement_for(client, [("py:values", True, 1), ("py:values", True, 4)])
    entry = placement["objectives"]["py:values"]
    assert entry["status"] == "assumed_known"
    assert entry["difficulty"] == 4 and entry["correct"] == 2


def test_objectives_are_aggregated_independently(client) -> None:
    placement = _placement_for(
        client,
        [
            ("py:values", True, 4),
            ("py:strings", False, 2),
            ("py:strings", True, 1),
            ("py:loops", True, 3),
        ],
    )
    assert placement["objectives"]["py:values"]["status"] == "assumed_known"
    assert placement["objectives"]["py:strings"]["status"] == "needs_work"
    assert placement["objectives"]["py:loops"]["status"] == "assumed_known"
    assert placement["summary"] == {"assumed_known": 2, "likely_known": 0, "needs_work": 1}


def test_placement_is_deterministic_regardless_of_insertion_bookkeeping(client) -> None:
    first = _placement_for(client, [("py:values", True, 3), ("py:values", False, 3)])
    second = _placement_for(client, [("py:values", True, 3), ("py:values", False, 3)])
    assert first["objectives"] == second["objectives"]
    assert first["summary"] == second["summary"]


def test_the_attempt_records_the_same_rule_when_it_completes(client) -> None:
    """The stored attempt placement (written by answer_diagnostic) uses the same aggregation."""
    register(client, email="placement-complete@example.com")
    goal = create_goal(client)
    from tests.conftest import _correct_response

    start = client.post(f"/api/diagnostic/goals/{goal['id']}").json()
    attempt_id = start["attempt_id"]
    state = {"current_item": start["current_item"], "completed": False}
    guard = 0
    while not state["completed"] and guard < 20:
        guard += 1
        item = state["current_item"]
        assert item is not None
        response = client.post(
            f"/api/diagnostic/{attempt_id}/answers",
            json={"item_id": item["id"], "response": _correct_response(item), "confidence": "unsure"},
        )
        assert response.status_code == 200, response.text
        body = response.json()
        state = {"current_item": body["next_item"], "completed": body["completed"]}

    stored = client.get(f"/api/diagnostic/{attempt_id}").json()["placement"]
    assert stored["summary"]["needs_work"] == 0
    for entry in stored["objectives"].values():
        assert entry["incorrect"] == 0
        assert entry["correct"] >= 1
        assert entry["status"] in {"assumed_known", "likely_known"}


def test_placement_rows_are_read_from_the_database_not_the_request(client) -> None:
    """Guards against an aggregation that reads only the latest *or* only the first response."""
    placement = _placement_for(
        client, [("py:values", True, 2), ("py:values", False, 2), ("py:values", True, 2)]
    )
    entry = placement["objectives"]["py:values"]
    assert entry["correct"] == 2 and entry["incorrect"] == 1
    assert entry["status"] == "needs_work"
