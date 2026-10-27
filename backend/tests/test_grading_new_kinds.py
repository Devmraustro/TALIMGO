"""The four item kinds added to the deterministic grader (§7.26).

The boundary contract is unchanged from ``test_grading.py``: grading is boolean, malformed input
is incorrect (never an exception), and the canonical answer is what the learner is shown.
"""

from __future__ import annotations

from types import SimpleNamespace

from app.learning.grading import grade
from app.serializers import item_public


def test_mcq_multi_requires_all_and_only_the_keyed_options() -> None:
    key = {"option_ids": ["a", "c"]}
    assert grade("mcq_multi", key, {"option_ids": ["c", "a"]}).is_correct
    assert not grade("mcq_multi", key, {"option_ids": ["a"]}).is_correct
    assert not grade("mcq_multi", key, {"option_ids": ["a", "b", "c"]}).is_correct
    assert not grade("mcq_multi", key, {"option_ids": []}).is_correct
    assert grade("mcq_multi", key, {"option_ids": ["a", "c"]}).canonical_answer == "a, c"


def test_mcq_multi_malformed_shapes_are_incorrect_not_errors() -> None:
    assert grade("mcq_multi", {"option_ids": ["a"]}, {"option_ids": "a"}).malformed
    assert grade("mcq_multi", {"option_ids": ["a"]}, {"option_ids": [{"id": "a"}]}).malformed
    assert grade("mcq_multi", {}, {"option_ids": ["a"]}).malformed


def test_ordering_requires_the_exact_sequence() -> None:
    key = {"option_ids": ["b", "a", "c"]}
    assert grade("ordering", key, {"option_ids": ["b", "a", "c"]}).is_correct
    assert not grade("ordering", key, {"option_ids": ["a", "b", "c"]}).is_correct
    assert not grade("ordering", key, {"option_ids": ["b", "a"]}).is_correct


def test_numeric_accepts_value_text_and_arabic_indic_digits() -> None:
    key = {"value": 15}
    assert grade("numeric", key, {"text": "15"}).is_correct
    assert grade("numeric", key, {"value": 15.0}).is_correct
    assert grade("numeric", key, {"text": " ١٥ "}).is_correct  # Arabic-Indic "15"
    assert grade("numeric", key, {"text": "1,5"}).is_correct  # comma is grouping: "1,5" parses as 15
    assert grade("numeric", {"value": 1.5}, {"text": "١٫٥"}).is_correct  # Arabic decimal separator
    assert grade("numeric", {"value": 1200}, {"text": "1,200"}).is_correct
    assert grade("numeric", key, {"text": "fifteen"}).malformed
    assert grade("numeric", key, {"text": "15"}).canonical_answer == "15"


def test_numeric_tolerance_is_bounded_and_signed_values_work() -> None:
    key = {"value": 3.14, "tolerance": 0.01}
    assert grade("numeric", key, {"text": "3.145"}).is_correct
    assert not grade("numeric", key, {"text": "3.16"}).is_correct
    assert grade("numeric", {"value": -4}, {"text": "-4"}).is_correct
    assert not grade("numeric", {"value": -4}, {"text": "4"}).is_correct


def test_true_false_grades_booleans_and_tolerates_the_literal_word() -> None:
    assert grade("true_false", {"value": True}, {"value": True}).is_correct
    assert grade("true_false", {"value": False}, {"value": "False"}).is_correct
    assert not grade("true_false", {"value": True}, {"value": False}).is_correct
    assert grade("true_false", {"value": True}, {"value": "yes"}).malformed
    assert grade("true_false", {"value": "true"}, {"value": True}).malformed


def test_ordering_options_are_never_served_in_the_authored_order() -> None:
    # The authored order of an ordering item IS the answer key; the public projection must
    # scramble it deterministically (same every request, never the authored sequence).
    item = SimpleNamespace(
        id="fe:css:q9",
        objective_id="fe:css",
        kind="ordering",
        prompt_en="Order the boxes",
        prompt_ar="رتّب الصناديق",
        options=[
            {"id": "a", "en": "content", "ar": "المحتوى"},
            {"id": "b", "en": "padding", "ar": "الحشو"},
            {"id": "c", "en": "border", "ar": "الحد"},
            {"id": "d", "en": "margin", "ar": "الهامش"},
        ],
        difficulty=2,
    )
    first = [option["id"] for option in item_public(item)["options"]]
    second = [option["id"] for option in item_public(item)["options"]]
    assert first == second, "presentation order must be stable across requests"
    assert first != ["a", "b", "c", "d"], "authored order would leak the key"
    assert sorted(first) == ["a", "b", "c", "d"]


def test_choice_options_keep_authored_order_for_other_kinds() -> None:
    item = SimpleNamespace(
        id="py:values:q1",
        objective_id="py:values",
        kind="mcq_single",
        prompt_en="?",
        prompt_ar="؟",
        options=[{"id": "a", "en": "x", "ar": "x"}, {"id": "b", "en": "y", "ar": "y"}],
        difficulty=1,
    )
    assert [option["id"] for option in item_public(item)["options"]] == ["a", "b"]
