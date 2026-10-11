"""Roadmap generation and retrieval. Validation happens before anything is stored."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select

from app.deps import CurrentLocale, CurrentUser, Db
from app.learning.roadmap import PlanningError
from app.models import AuditLog, Goal, Objective, Plan, PlanItem, PlanWeek
from app.schemas import PlanGenerateOut, PlanOut
from app.serializers import plan_public
from app.services.plans import (
    PlanValidationFailed,
    generate_roadmap,
    reschedule_plan,
    schedule_payload,
)

router = APIRouter(prefix="/api/plans", tags=["planning"])


def _plan_payload(db: Db, plan: Plan, locale: str = "en") -> PlanOut:
    weeks = list(
        db.scalars(select(PlanWeek).where(PlanWeek.plan_id == plan.id).order_by(PlanWeek.week_number)).all()
    )
    items = list(
        db.scalars(select(PlanItem).where(PlanItem.plan_id == plan.id).order_by(PlanItem.order_index)).all()
    )
    items_by_week: dict[str, list[PlanItem]] = {}
    for item in items:
        items_by_week.setdefault(item.week_id, []).append(item)
    objectives = {row.id: row for row in db.scalars(select(Objective)).all()}
    return PlanOut(**plan_public(plan, weeks, items_by_week, objectives, locale))


@router.post("/goals/{goal_id}", response_model=PlanGenerateOut)
def generate(goal_id: str, user: CurrentUser, db: Db, locale: CurrentLocale) -> PlanGenerateOut:
    goal = db.get(Goal, goal_id)
    if goal is None or goal.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found.")
    try:
        result = generate_roadmap(db, user, goal)
    except PlanValidationFailed as exc:
        # The plan is rejected, not stored, and the reasons are returned for the caller to fix.
        raise HTTPException(status_code=422, detail=exc.report) from exc
    except PlanningError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    db.commit()
    plan = db.get(Plan, result["plan_id"])
    if plan is None:  # the plan was created in this transaction; this would be a programming error
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="The plan was validated but could not be read back.",
        )
    return PlanGenerateOut(
        plan=_plan_payload(db, plan, locale),
        skipped_objectives=result["skipped"],
        validation=result["validation"],
    )


@router.get("/active", response_model=PlanOut | None)
def active_plan(user: CurrentUser, db: Db, locale: CurrentLocale) -> PlanOut | None:
    plan = db.scalar(
        select(Plan)
        .where(Plan.user_id == user.id, Plan.status == "active")
        .order_by(Plan.created_at.desc())
        .limit(1)
    )
    return _plan_payload(db, plan, locale) if plan else None


@router.get("/active/schedule")
def active_schedule(user: CurrentUser, db: Db, locale: CurrentLocale) -> dict:
    """The active plan as dated work, with today's missions and how the plan is going.

    Dates are derived from the plan's ``starts_on`` and each item's day offset, so they are stable
    across requests and only change when the learner re-plans (or a new plan supersedes this one).
    """
    plan = db.scalar(
        select(Plan)
        .where(Plan.user_id == user.id, Plan.status == "active")
        .order_by(Plan.created_at.desc())
        .limit(1)
    )
    if plan is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No active plan.")
    return schedule_payload(db, plan, locale=locale)


@router.post("/active/reschedule")
def reschedule(user: CurrentUser, db: Db, locale: CurrentLocale) -> dict:
    """Re-place unfinished work from today. Completed work keeps its date; nothing is deleted."""
    plan = db.scalar(
        select(Plan)
        .where(Plan.user_id == user.id, Plan.status == "active")
        .order_by(Plan.created_at.desc())
        .limit(1)
    )
    if plan is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No active plan.")
    result = reschedule_plan(db, plan)
    db.add(AuditLog(actor_user_id=user.id, action="plan.reschedule", detail=result))
    db.commit()
    return {**result, "schedule": schedule_payload(db, plan, locale=locale)}


@router.get("/{plan_id}", response_model=PlanOut)
def get_plan(plan_id: str, user: CurrentUser, db: Db, locale: CurrentLocale) -> PlanOut:
    plan = db.get(Plan, plan_id)
    if plan is None or plan.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found.")
    return _plan_payload(db, plan, locale)
