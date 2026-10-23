"""Grading is deterministic code, never a model."""

from __future__ import annotations

import pytest

from app.learning.grading import grade

MCQ_KEY = {"option_id": "b"}


@pytest.mark.parametrize(
    ("response", "expected"),
    [
        ({"option_id": "b"}, True),
        ({"option_id": "B "}, False),
        ({"option_id": "a"}, False),
        ({}, False),
        ({"option_id": None}, False),
    ],
)
def test_mcq_grading(response: dict, expected: bool) -> None:
    result = grade("mcq_single", MCQ_KEY, response)
    assert result.is_correct is expected


def test_mcq_malformed_response_is_incorrect_not_an_exception() -> None:
    result = grade("mcq_single", MCQ_KEY, ["not", "a", "dict"])  # type: ignore[arg-type]
    assert result.is_correct is False
    assert result.malformed is True


SHORT_KEY = {"accepted": ["15"]}


@pytest.mark.parametrize(
    "answer",
    ["15", " 15 ", "15.", "15.0", "(15)", "15!"],
)
def test_short_answer_accepts_equivalent_forms(answer: str) -> None:
    assert grade("short_answer", SHORT_KEY, {"text": answer}).is_correct is True


@pytest.mark.parametrize("answer", ["", "14", "fifteen", "150"])
def test_short_answer_rejects_wrong_forms(answer: str) -> None:
    assert grade("short_answer", SHORT_KEY, {"text": answer}).is_correct is False


def test_short_answer_is_case_and_whitespace_insensitive() -> None:
    key = {"accepted": ["import"]}
    assert grade("short_answer", key, {"text": "  IMPORT "}).is_correct is True


def test_short_answer_ignores_arabic_diacritics_and_hamza_forms() -> None:
    key = {"accepted": ["أحمد"]}
    assert grade("short_answer", key, {"text": "احمد"}).is_correct is True
    assert grade("short_answer", key, {"text": "أَحْمَد"}).is_correct is True


def test_short_answer_missing_text_is_malformed() -> None:
    result = grade("short_answer", SHORT_KEY, {})
    assert result.malformed is True
    assert result.is_correct is False


def test_mcq_answer_key_text_is_returned_for_feedback() -> None:
    result = grade("mcq_single", {"option_id": "b", "option_text": "float"}, {"option_id": "a"})
    assert result.canonical_answer == "float"


def test_unknown_item_kind_is_refused() -> None:
    result = grade("essay", {"accepted": ["x"]}, {"text": "x"})
    assert result.is_correct is False
    assert result.malformed is True


def test_grading_never_raises_on_hostile_input() -> None:
    hostile = {"text": "x" * 10_000}
    assert grade("short_answer", SHORT_KEY, hostile).is_correct is False
