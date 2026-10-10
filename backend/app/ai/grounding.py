"""Retrieval for the tutor: build the smallest sufficient context, with resolvable citations.

Only authored curriculum material is retrieved — no web search, no learner documents (yet), and
nothing is fetched from outside TALIMGO. Every citation the model is allowed to use is an ID that
exists in this context, which is what makes citation validation meaningful.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from sqlalchemy.orm import Session as DbSession

from app.curriculum.registry import localised
from app.models import Lesson, Objective

MAX_CONTEXT_CHARS = 6000


@dataclass(frozen=True)
class GroundingContext:
    objective_id: str
    objective_title: str
    lesson_id: str | None
    lesson_title: str
    markdown: str
    citation_ids: set[str] = field(default_factory=set)


def _truncate(text: str, limit: int) -> str:
    if len(text) <= limit:
        return text
    return text[: limit - 20].rstrip() + "\n\n[…truncated…]"


def build_grounding(
    db: DbSession,
    *,
    objective_id: str,
    lesson_id: str | None,
    locale: str = "en",
    max_chars: int = MAX_CONTEXT_CHARS,
) -> GroundingContext:
    objective = db.get(Objective, objective_id)
    if objective is None:
        raise LookupError(f"Unknown objective {objective_id!r}")

    title = localised({"title_en": objective.title_en, "title_ar": objective.title_ar}, "title", locale)
    summary = localised(
        {"summary_en": objective.summary_en, "summary_ar": objective.summary_ar}, "summary", locale
    )

    parts: list[str] = [f"### Objective ({objective.id})\n{title}\n{summary}".strip()]
    citations: set[str] = {f"objective:{objective.id}"}

    lesson: Lesson | None = None
    if lesson_id:
        lesson = db.get(Lesson, lesson_id)
    if lesson is None:
        lesson = (
            db.query(Lesson).filter(Lesson.objective_id == objective.id).order_by(Lesson.sequence).first()
        )
    lesson_title = ""
    if lesson is not None:
        lesson_title = localised({"title_en": lesson.title_en, "title_ar": lesson.title_ar}, "title", locale)
        body = localised(
            {"body_md_en": lesson.body_md_en, "body_md_ar": lesson.body_md_ar}, "body_md", locale
        )
        parts.append(f"### Lesson ({lesson.id})\n{lesson_title}\n{_truncate(body or '', max_chars // 2)}")
        citations.add(f"lesson:{lesson.id}")

    for prereq_id in objective.prerequisite_ids or []:
        prereq = db.get(Objective, prereq_id)
        if prereq is None:
            continue
        prereq_title = localised({"title_en": prereq.title_en, "title_ar": prereq.title_ar}, "title", locale)
        parts.append(f"### Prerequisite ({prereq.id})\n{prereq_title}")
        citations.add(f"objective:{prereq.id}")

    markdown = "\n\n".join(parts)
    return GroundingContext(
        objective_id=objective.id,
        objective_title=title,
        lesson_id=lesson.id if lesson is not None else None,
        lesson_title=lesson_title,
        markdown=_truncate(markdown, max_chars),
        citation_ids=citations,
    )
