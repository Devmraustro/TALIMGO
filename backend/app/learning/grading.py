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
