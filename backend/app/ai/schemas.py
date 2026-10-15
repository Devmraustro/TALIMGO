"""Validation of model output before it can affect product state or reach a learner.

Two gates:
  1. **Structure** — the reply must parse and satisfy a schema.
  2. **Policy** — prohibited claims (guarantees of jobs, income, certification or mastery) are
     rejected, and any citation must resolve to material that was actually in the context.
"""

from __future__ import annotations

import json
import re
from typing import Any, Literal

from pydantic import BaseModel, Field, ValidationError, field_validator


class TutorOutputRejected(ValueError):
    """The model's output failed validation and must not be shown."""


class TutorReply(BaseModel):
    reply: str = Field(min_length=2, max_length=6000)
    hint_level: int = Field(ge=0, le=3, default=1)
    citations: list[str] = Field(default_factory=list, max_length=6)
    confidence: Literal["low", "medium", "high"] = "medium"
    follow_up_question: str | None = Field(default=None, max_length=300)

    @field_validator("citations")
    @classmethod
    def _clean_citations(cls, value: list[str]) -> list[str]:
        return [citation.strip() for citation in value if citation and citation.strip()]


# Claims TALIMGO must never make (master reference section 11.1.1). Matched case-insensitively on
# word boundaries so ordinary words like "guarantee" inside code samples do not pass silently.
_PROHIBITED_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"\bguarantee(d|s)?\b", re.IGNORECASE),
    re.compile(r"\b(we|i)\s+(promise|ensure)\b.{0,40}\b(job|salary|income|hired|certificat)", re.IGNORECASE),
    re.compile(r"\b(job|employment|salary|income)\s+(is\s+)?guaranteed\b", re.IGNORECASE),
    re.compile(r"\bwill\s+(definitely\s+)?(get|find)\s+you\s+a\s+(job|position)\b", re.IGNORECASE),
    re.compile(
        r"\bofficial(ly)?\s+(recognised|recognized|certified)\s+(certificate|diploma|degree)\b", re.IGNORECASE
    ),
    re.compile(r"\byou\s+will\s+master\b", re.IGNORECASE),
    re.compile(r"\b100%\s+(success|guaranteed|score)\b", re.IGNORECASE),
)


def _strip_code_fences(raw: str) -> str:
    text = raw.strip()
    if text.startswith("```"):
        text = re.sub(r"^```[a-zA-Z]*\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    return text.strip()


def parse_model_json(raw: str) -> dict[str, Any]:
    """Parse the model's JSON, tolerating a fenced block but never guessing at content."""
    candidate = _strip_code_fences(raw)
    try:
        parsed = json.loads(candidate)
    except json.JSONDecodeError:
        start, end = candidate.find("{"), candidate.rfind("}")
        if start == -1 or end <= start:
            raise TutorOutputRejected("Model output was not JSON.") from None
        try:
            parsed = json.loads(candidate[start : end + 1])
        except json.JSONDecodeError as exc:
            raise TutorOutputRejected("Model output was not valid JSON.") from exc
    if not isinstance(parsed, dict):
        raise TutorOutputRejected("Model output was JSON but not an object.")
    return parsed


def validate_tutor_reply(raw: str, *, allowed_citations: set[str]) -> TutorReply:
    """Validate structure and policy. Raises :class:`TutorOutputRejected` on any failure."""
    data = parse_model_json(raw)
    try:
        reply = TutorReply.model_validate(data)
    except ValidationError as exc:
        raise TutorOutputRejected(
            f"Model output did not match the tutor schema: {exc.error_count()} issue(s)."
        ) from exc

    unknown = [citation for citation in reply.citations if citation not in allowed_citations]
    if unknown:
        raise TutorOutputRejected(
            "Model cited material that was not in the provided context: " + ", ".join(sorted(unknown))
        )

    for pattern in _PROHIBITED_PATTERNS:
        match = pattern.search(reply.reply)
        if match:
            raise TutorOutputRejected(
                f"Model output contained a prohibited claim ({match.group(0)!r}); it was not shown."
            )
    return reply


def find_prohibited_claims(text: str) -> list[str]:
    """Utility used by the claim filter's own tests."""
    return [match.group(0) for pattern in _PROHIBITED_PATTERNS if (match := pattern.search(text))]
