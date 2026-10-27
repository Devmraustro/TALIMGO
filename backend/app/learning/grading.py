"""Deterministic grading at the assessment boundary.

Grading is never delegated to a model (AGENTS.md section 5). The grader owns the answer key,
normalisation rules and the canonical answer text; everything downstream works with a boolean
outcome, so a future pronunciation or essay grader can be added behind the same boundary.

Answer keys are held by the caller and are not part of any response schema.
"""

from __future__ import annotations

import re
import unicodedata
from typing import Any

from app.learning.types import GradeResult

_WHITESPACE = re.compile(r"\s+")
_EDGE_PUNCTUATION = re.compile(r"^[\s\"'`.,;:!?()\[\]{}]+|[\s\"'`.,;:!?()\[\]{}]+$")
_ARABIC_DIACRITICS = re.compile(r"[\u0617-\u061A\u064B-\u0652\u0670\u06D6-\u06ED]")


def _normalise(text: str) -> str:
    """Case-, whitespace-, diacritic- and edge-punctuation-insensitive normalisation."""
    value = unicodedata.normalize("NFKC", text or "")
    value = _ARABIC_DIACRITICS.sub("", value)
    value = value.replace("\u0623", "\u0627").replace("\u0625", "\u0627").replace("\u0622", "\u0627")
    value = value.replace("\u0649", "\u064a").replace("\u0629", "\u0647")
    value = value.casefold()
    value = _EDGE_PUNCTUATION.sub("", value)
    value = _WHITESPACE.sub(" ", value)
    return value.strip()


def _numeric_equivalent(candidate: str, accepted: str) -> bool:
    try:
        return float(candidate) == float(accepted)
    except (TypeError, ValueError):
        return False


def _parse_number(value: object) -> float | None:
    """Parse a learner-typed number, tolerating Arabic-Indic digits and separators.

    Learners on Arabic keyboards type Arabic-Indic digits (U+0660..U+0669, sometimes the extended
    U+06F0..U+06F9 set), use the Arabic decimal separator (U+066B), and group thousands with the
    Arabic thousands separator (U+066C) or a comma. A comma is therefore grouping, never a decimal
    point: the decimal separators are ``.`` and U+066B. This is the same normalisation philosophy
    as :func:`_normalise` applied to numbers, so a correct numeric answer is never rejected for
    its script.
    """
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    if not isinstance(value, str):
        return None
    text = unicodedata.normalize("NFKC", value).strip()
    if not text:
        return None
    converted: list[str] = []
    for char in text:
        digit = unicodedata.digit(char, None)
        if digit is not None:
            converted.append(str(digit))
        elif char in "٫.":
            converted.append(".")
        elif char in "٬,":
            continue  # thousands grouping carries no value
        elif char in "-−":
            converted.append("-")
        elif char == " ":
            continue
        else:
            return None
    try:
        return float("".join(converted))
    except ValueError:
        return None


def _format_number(value: float) -> str:
    """``15.0`` is shown as ``15``; a genuine decimal keeps its digits."""
    if value == int(value):
        return str(int(value))
    return repr(value)


def _option_ids(container: object) -> list[str] | None:
    """A list of option ids, or ``None`` when the shape is not a list of scalars."""
    if not isinstance(container, list):
        return None
    ids: list[str] = []
    for entry in container:
        if isinstance(entry, (dict, list)):  # a nested shape is malformed, never coerced
            return None
        ids.append(str(entry).strip())
    return ids


def grade(item_kind: str, answer_key: dict[str, Any], response: dict[str, Any]) -> GradeResult:
    """Grade one response against one key. Malformed input is incorrect, never an exception."""
    if not isinstance(response, dict):
        return GradeResult(is_correct=False, canonical_answer="", malformed=True)

    if item_kind == "mcq_single":
        expected = str(answer_key.get("option_id", "")).strip()
        given = response.get("option_id")
        given_str = str(given).strip() if given is not None else ""
        canonical = ""
        options = answer_key.get("option_text")
        if isinstance(options, str):
            canonical = options
        return GradeResult(is_correct=bool(expected) and given_str == expected, canonical_answer=canonical)

    if item_kind == "mcq_multi":
        # All-and-only: a partially correct selection is not correct. Partial-credit rules would
        # need weighting decisions per item; the boundary stays boolean (see module docstring).
        expected = _option_ids(answer_key.get("option_ids"))
        given = _option_ids(response.get("option_ids"))
        if not expected or given is None:
            return GradeResult(is_correct=False, canonical_answer="", malformed=True)
        canonical = ", ".join(expected)
        return GradeResult(is_correct=set(given) == set(expected), canonical_answer=canonical)

    if item_kind == "ordering":
        expected = _option_ids(answer_key.get("option_ids"))
        given = _option_ids(response.get("option_ids"))
        if not expected or given is None:
            return GradeResult(is_correct=False, canonical_answer="", malformed=True)
        canonical = ", ".join(expected)
        return GradeResult(is_correct=given == expected, canonical_answer=canonical)

    if item_kind == "numeric":
        expected = _parse_number(answer_key.get("value"))
        if expected is None:
            return GradeResult(is_correct=False, canonical_answer="", malformed=True)
        tolerance = _parse_number(answer_key.get("tolerance"))
        tolerance = abs(tolerance) if tolerance is not None else 0.0
        canonical = _format_number(expected)
        given = _parse_number(response.get("value", response.get("text")))
        if given is None:
            return GradeResult(is_correct=False, canonical_answer=canonical, malformed=True)
        return GradeResult(is_correct=abs(given - expected) <= tolerance, canonical_answer=canonical)

    if item_kind == "true_false":
        expected = answer_key.get("value")
        if not isinstance(expected, bool):
            return GradeResult(is_correct=False, canonical_answer="", malformed=True)
        canonical = "true" if expected else "false"
        given = response.get("value")
        if isinstance(given, str):  # tolerate a client that sends the literal word
            given = {"true": True, "false": False}.get(given.strip().lower())
        if not isinstance(given, bool):
            return GradeResult(is_correct=False, canonical_answer=canonical, malformed=True)
        return GradeResult(is_correct=given is expected, canonical_answer=canonical)

    if item_kind == "short_answer":
        accepted = answer_key.get("accepted")
        if not isinstance(accepted, list) or not accepted:
            return GradeResult(is_correct=False, canonical_answer="", malformed=True)
        canonical = str(accepted[0])
        given = response.get("text")
        if given is None:
            return GradeResult(is_correct=False, canonical_answer=canonical, malformed=True)
        normalised = _normalise(str(given))
        for candidate in accepted:
            if normalised == _normalise(str(candidate)) or _numeric_equivalent(normalised, str(candidate)):
                return GradeResult(is_correct=True, canonical_answer=canonical)
        return GradeResult(is_correct=False, canonical_answer=canonical)

    # Unknown item kind: refuse rather than guess.
    return GradeResult(is_correct=False, canonical_answer="", malformed=True)
