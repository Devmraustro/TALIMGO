"""Goals: the entry point of the learning cycle."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select

from app.curriculum.registry import UnknownPathError, get_path
from app.deps import CurrentUser, Db
from app.models import Goal
from app.schemas import GoalCreate, GoalOut
from app.utils import utcnow

router = APIRouter(prefix="/api/goals", tags=["goals"])

MAX_ACTIVE_GOALS = 3


@router.post("", response_model=GoalOut, status_code=status.HTTP_201_CREATED)
def create_goal(payload: GoalCreate, user: CurrentUser, db: Db) -> GoalOut:
    try:
        get_path(payload.path_id)
    except UnknownPathError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Unknown learning path.") from exc

    if payload.target_date is not None and payload.target_date < utcnow().date():
        raise HTTPException(
            status_code=422,
            detail="Target date must be in the future.",
        )

    active = db.scalars(select(Goal).where(Goal.user_id == user.id, Goal.status == "active")).all()
    if len(active) >= MAX_ACTIVE_GOALS:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"You already have {MAX_ACTIVE_GOALS} active goals. Finish or pause one first.",
        )

    goal = Goal(
        user_id=user.id,
        path_id=payload.path_id,
        statement=payload.statement.strip(),
        motivation=payload.motivation.strip(),
        target_date=payload.target_date,
        weekly_minutes=payload.weekly_minutes,
    )
    db.add(goal)
    db.commit()
    return GoalOut.model_validate(goal)


@router.get("", response_model=list[GoalOut])
def list_goals(user: CurrentUser, db: Db) -> list[GoalOut]:
    rows = db.scalars(select(Goal).where(Goal.user_id == user.id).order_by(Goal.created_at.desc())).all()
    return [GoalOut.model_validate(row) for row in rows]


@router.get("/active", response_model=GoalOut | None)
def active_goal(user: CurrentUser, db: Db) -> GoalOut | None:
    row = db.scalar(
        select(Goal)
        .where(Goal.user_id == user.id, Goal.status == "active")
        .order_by(Goal.created_at.desc())
        .limit(1)
    )
    return GoalOut.model_validate(row) if row else None
