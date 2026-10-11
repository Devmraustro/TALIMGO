"""Curriculum browsing. Content is public; learner state is not."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select

from app.curriculum.registry import get_path, list_path_summaries
from app.deps import ContentLocale, Db
from app.i18n import DEFAULT_LOCALE
from app.models import Lesson, Objective
from app.schemas import LessonPublic, ObjectivePublic, PathSummary
from app.serializers import lesson_public, objective_public

router = APIRouter(prefix="/api/curriculum", tags=["curriculum"])


def _localised_path_summary(summary: dict, locale: str) -> dict:
    """Paths carry both languages; `title`/`summary` resolve them for the requesting locale."""
    arabic = locale == "ar" and bool((summary.get("title_ar") or "").strip())
    return {
        **summary,
        "title": (summary.get("title_ar") if arabic else summary.get("title_en")) or "",
        "summary": (summary.get("summary_ar") if arabic else summary.get("summary_en")) or "",
    }


@router.get("/paths", response_model=list[PathSummary])
def list_paths(locale: ContentLocale) -> list[PathSummary]:
    return [PathSummary(**_localised_path_summary(summary, locale)) for summary in list_path_summaries()]


@router.get("/paths/{path_id}/objectives", response_model=list[ObjectivePublic])
def list_objectives(path_id: str, db: Db, locale: ContentLocale) -> list[ObjectivePublic]:
    try:
        get_path(path_id)
    except KeyError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Unknown learning path.") from None
    rows = db.scalars(
        select(Objective).where(Objective.path_id == path_id).order_by(Objective.sequence, Objective.id)
    ).all()
    if not rows:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Unknown learning path.")
    return [ObjectivePublic(**objective_public(row, locale)) for row in rows]


@router.get("/lessons/{lesson_id}", response_model=LessonPublic)
def get_lesson(lesson_id: str, db: Db, locale: ContentLocale) -> LessonPublic:
    lesson = db.get(Lesson, lesson_id)
    if lesson is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Unknown lesson.")
    return LessonPublic(**lesson_public(lesson, locale or DEFAULT_LOCALE))
