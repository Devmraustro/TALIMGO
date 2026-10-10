"""Curriculum browsing. Content is public; learner state is not."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select

from app.curriculum.registry import list_path_summaries
from app.deps import CurrentUser, Db
from app.models import Lesson, Objective
from app.schemas import LessonPublic, ObjectivePublic, PathSummary
from app.serializers import lesson_public, objective_public

router = APIRouter(prefix="/api/curriculum", tags=["curriculum"])


@router.get("/paths", response_model=list[PathSummary])
def list_paths() -> list[PathSummary]:
    return [PathSummary(**summary) for summary in list_path_summaries()]


@router.get("/paths/{path_id}/objectives", response_model=list[ObjectivePublic])
def list_objectives(path_id: str, db: Db) -> list[ObjectivePublic]:
    rows = db.scalars(
        select(Objective).where(Objective.path_id == path_id).order_by(Objective.sequence, Objective.id)
    ).all()
    if not rows:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Unknown learning path.")
    return [ObjectivePublic(**objective_public(row)) for row in rows]


@router.get("/lessons/{lesson_id}", response_model=LessonPublic)
def get_lesson(lesson_id: str, db: Db, user: CurrentUser) -> LessonPublic:
    lesson = db.get(Lesson, lesson_id)
    if lesson is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Unknown lesson.")
    return LessonPublic(**lesson_public(lesson))
