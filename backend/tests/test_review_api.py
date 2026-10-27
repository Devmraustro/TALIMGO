"""Spaced-review API: queue projection, review-mode sessions, flashcards (ADR 0009)."""

from __future__ import annotations

from tests.conftest import _correct_response, register


def _answer_one_practice_item(client) -> dict:
    """Start practice on py:values and answer its first item correctly."""
    created = client.post("/api/practice/sessions", json={"objective_id": "py:values", "size": 1})
    assert created.status_code == 201, created.text
    session = created.json()
    item = session["item"]
    assert item is not None
    answered = client.post(
        f"/api/practice/sessions/{session['session_id']}/answers",
        json={"item_id": item["id"], "response": _correct_response(item), "used_hint": False},
    )
    assert answered.status_code == 200, answered.text
    return item


def test_review_queue_is_empty_without_evidence(client) -> None:
    register(client)
    assert client.get("/api/practice/review-queue").json() == {"items": [], "due_count": 0}


def test_review_mode_session_is_stored_and_echoed(client) -> None:
    register(client)
    created = client.post(
        "/api/practice/sessions",
        json={"objective_id": "py:values", "size": 2, "mode": "review"},
    )
    assert created.status_code == 201, created.text
    assert created.json()["mode"] == "review"
    plain = client.post("/api/practice/sessions", json={"objective_id": "py:values", "size": 1})
    assert plain.json()["mode"] == "practice"


def test_flashcards_cover_only_seen_items_and_rating_records_no_evidence(client) -> None:
    register(client)
    item = _answer_one_practice_item(client)

    deck = client.get("/api/practice/flashcards").json()
    assert deck["due_count"] == 1
    (card,) = deck["cards"]
    assert card["item_id"] == item["id"]
    assert card["answer"], "the back of the card must carry the canonical answer"
    assert card["is_due"] is True

    rated = client.post(f"/api/practice/flashcards/{item['id']}/rate", json={"rating": "good"})
    assert rated.status_code == 200, rated.text
    assert rated.json()["repetitions"] == 1
    assert rated.json()["interval_days"] == 1.0

    # The card is scheduled out; nothing about the rating became evidence or mastery.
    assert client.get("/api/practice/flashcards").json()["due_count"] == 0
    evidence = client.get("/api/practice/progress/evidence").json()
    assert len(evidence) == 1, "only the practice answer itself is evidence"
    assert evidence[0]["kind"] == "practice"


def test_unseen_item_cannot_be_rated(client) -> None:
    register(client)
    response = client.post("/api/practice/flashcards/py:values:q1/rate", json={"rating": "good"})
    assert response.status_code == 404


def test_again_rating_brings_the_card_back(client) -> None:
    register(client)
    item = _answer_one_practice_item(client)
    client.post(f"/api/practice/flashcards/{item['id']}/rate", json={"rating": "good"})
    assert client.get("/api/practice/flashcards").json()["due_count"] == 0
    again = client.post(f"/api/practice/flashcards/{item['id']}/rate", json={"rating": "again"})
    assert again.json()["repetitions"] == 0
