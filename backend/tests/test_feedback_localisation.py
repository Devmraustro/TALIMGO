"""Feedback must be localised down to the correct answer, not just the question.

The bug this locks out: ``_canonical_answer()`` asked the serialiser for the option label with a
hard-coded ``"en"``, so an Arabic learner read an Arabic prompt, Arabic options and an Arabic
explanation — and then an English "the correct answer is `float`" line.

The authored curriculum's choice labels happen to be code literals (``int``/``float``) that are the
same in both languages, which is exactly why the defect was invisible. These tests replace the labels
of the item that is about to be presented with clearly distinct Arabic and English strings, so the
assertion can only pass if the locale actually reaches the feedback.
"""

from __future__ import annotations

import re

import pytest
from fastapi.testclient import TestClient

from app.curriculum.registry import item_index
from app.db import session_scope
from app.learning.types import GradeResult
from app.models import Item
from app.services.assessment import _canonical_answer
from tests.conftest import create_goal, register

ARABIC = re.compile(r"[\u0600-\u06ff]")
OBJECTIVE_ID = "py:values"

# Deliberately distinct per language, and not transliterations of each other.
DISTINCT_OPTIONS = [
    {"id": "a", "en": "a whole number", "ar": "عدد صحيح"},
    {"id": "b", "en": "a decimal number", "ar": "عدد عشري"},
    {"id": "c", "en": "a piece of text", "ar": "نصّ"},
    {"id": "d", "en": "true or false", "ar": "صواب أو خطأ"},
]
CORRECT_OPTION_ID = "b"


def _relabel_item(item_id: str) -> None:
    """Give the item the same shape as the authored data, with labels that differ by language."""
    with session_scope() as db:
        item = db.get(Item, item_id)
        assert item is not None, item_id
        item.options = [dict(option) for option in DISTINCT_OPTIONS]
        item.answer_key = {"option_id": CORRECT_OPTION_ID}
        db.commit()


def _learner(client: TestClient, locale: str) -> dict:
    register(client)
    assert client.patch("/api/me/profile", json={"locale": locale}).status_code == 200
    return create_goal(client)


def _expected(locale: str) -> str:
    return next(option[locale] for option in DISTINCT_OPTIONS if option["id"] == CORRECT_OPTION_ID)


# --------------------------------------------------------------------------------------
# Unit level: the value itself, both languages
# --------------------------------------------------------------------------------------


def test_the_canonical_choice_label_follows_the_locale() -> None:
    item = Item(
        id="synth:mcq",
        objective_id=OBJECTIVE_ID,
        kind="mcq_single",
        prompt_en="prompt",
        prompt_ar="سؤال",
        options=DISTINCT_OPTIONS,
        answer_key={"option_id": CORRECT_OPTION_ID},
        difficulty=1,
    )
    outcome = GradeResult(is_correct=True, canonical_answer="")

    assert _canonical_answer(item, outcome, "en") == "a decimal number"
    assert _canonical_answer(item, outcome, "ar") == "عدد عشري"


def test_a_missing_translation_falls_back_to_english_rather_than_empty() -> None:
    item = Item(
        id="synth:mcq",
        objective_id=OBJECTIVE_ID,
        kind="mcq_single",
        prompt_en="prompt",
        prompt_ar="",
        options=[{"id": "b", "en": "a decimal number", "ar": ""}],
        answer_key={"option_id": "b"},
        difficulty=1,
    )
    outcome = GradeResult(is_correct=True, canonical_answer="")

    assert _canonical_answer(item, outcome, "ar") == "a decimal number"


def test_a_literal_code_label_is_returned_unchanged_in_both_locales() -> None:
    """`float` is a token the learner must type; it is never translated."""
    item = Item(
        id="synth:mcq",
        objective_id=OBJECTIVE_ID,
        kind="mcq_single",
        prompt_en="prompt",
        prompt_ar="سؤال",
        options=[{"id": "b", "en": "float", "ar": "float"}],
        answer_key={"option_id": "b"},
        difficulty=1,
    )
    outcome = GradeResult(is_correct=True, canonical_answer="")

    assert _canonical_answer(item, outcome, "en") == "float"
    assert _canonical_answer(item, outcome, "ar") == "float"


@pytest.mark.parametrize("locale", ["ar", "en"])
def test_a_canonical_short_answer_is_never_translated(locale: str) -> None:
    item = Item(
        id="synth:short",
        objective_id=OBJECTIVE_ID,
        kind="short_answer",
        prompt_en="What is 12 + 3?",
        prompt_ar="ما ناتج 12 + 3؟",
        options=None,
        answer_key={"accepted": ["15"]},
        difficulty=1,
    )
    outcome = GradeResult(is_correct=True, canonical_answer="15")

    assert _canonical_answer(item, outcome, locale) == "15"


# --------------------------------------------------------------------------------------
# API level: diagnostic and practice feedback
# --------------------------------------------------------------------------------------


def test_diagnostic_feedback_returns_the_arabic_correct_answer(client: TestClient) -> None:
    goal = _learner(client, "ar")
    state = client.post(f"/api/diagnostic/goals/{goal['id']}").json()
    item_id = state["current_item"]["id"]
    _relabel_item(item_id)

    answered = client.post(
        f"/api/diagnostic/{state['attempt_id']}/answers",
        json={"item_id": item_id, "response": {"option_id": CORRECT_OPTION_ID}, "confidence": "unsure"},
    )
    assert answered.status_code == 200, answered.text
    feedback = answered.json()["feedback"]

    assert feedback["is_correct"] is True
    assert feedback["correct_answer"] == _expected("ar"), feedback["correct_answer"]
    assert ARABIC.search(feedback["correct_answer"]), "the learner reads Arabic"
    assert feedback["objective_title"] and ARABIC.search(feedback["objective_title"])


def test_diagnostic_feedback_returns_the_english_correct_answer(client: TestClient) -> None:
    goal = _learner(client, "en")
    state = client.post(f"/api/diagnostic/goals/{goal['id']}").json()
    item_id = state["current_item"]["id"]
    _relabel_item(item_id)

    answered = client.post(
        f"/api/diagnostic/{state['attempt_id']}/answers",
        json={"item_id": item_id, "response": {"option_id": CORRECT_OPTION_ID}, "confidence": "unsure"},
    )
    assert answered.status_code == 200, answered.text
    feedback = answered.json()["feedback"]

    assert feedback["correct_answer"] == _expected("en"), feedback["correct_answer"]
    assert not ARABIC.search(feedback["correct_answer"])


def test_practice_feedback_returns_the_arabic_correct_answer(client: TestClient) -> None:
    _learner(client, "ar")
    session = client.post("/api/practice/sessions", json={"objective_id": OBJECTIVE_ID, "size": 1}).json()
    item_id = session["item"]["id"]
    _relabel_item(item_id)

    answered = client.post(
        f"/api/practice/sessions/{session['session_id']}/answers",
        json={"item_id": item_id, "response": {"option_id": CORRECT_OPTION_ID}},
    )
    assert answered.status_code == 200, answered.text
    feedback = answered.json()["feedback"]

    assert feedback["correct_answer"] == _expected("ar"), feedback["correct_answer"]
    assert ARABIC.search(feedback["explanation"]), "the explanation is Arabic too"


def test_practice_feedback_returns_the_english_correct_answer(client: TestClient) -> None:
    _learner(client, "en")
    session = client.post("/api/practice/sessions", json={"objective_id": OBJECTIVE_ID, "size": 1}).json()
    item_id = session["item"]["id"]
    _relabel_item(item_id)

    answered = client.post(
        f"/api/practice/sessions/{session['session_id']}/answers",
        json={"item_id": item_id, "response": {"option_id": CORRECT_OPTION_ID}},
    )
    assert answered.status_code == 200, answered.text
    assert answered.json()["feedback"]["correct_answer"] == _expected("en")


@pytest.mark.parametrize("locale", ["ar", "en"])
def test_the_option_id_is_never_revealed_as_the_learner_facing_answer(
    client: TestClient, locale: str
) -> None:
    """The canonical value is the label the learner read, never the internal option id."""
    _learner(client, locale)
    session = client.post("/api/practice/sessions", json={"objective_id": OBJECTIVE_ID, "size": 1}).json()
    item_id = session["item"]["id"]
    _relabel_item(item_id)

    answered = client.post(
        f"/api/practice/sessions/{session['session_id']}/answers",
        json={"item_id": item_id, "response": {"option_id": CORRECT_OPTION_ID}},
    ).json()
    assert answered["feedback"]["correct_answer"] not in {option["id"] for option in DISTINCT_OPTIONS}


def test_the_authored_dataset_keeps_its_literal_code_labels() -> None:
    """The real curriculum's labels are code tokens; localisation must not have altered them."""
    index = item_index("python-foundations")
    item = index["py:values:q1"]
    labels = {option["en"] for option in item["options"]}
    assert labels == {"int", "float", "str", "bool"}
    assert {option["ar"] for option in item["options"]} == labels, "code tokens stay code tokens"
