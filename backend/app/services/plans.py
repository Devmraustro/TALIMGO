"""Roadmap generation with a publication gate.

Sequence: build curriculum nodes → replay the learner's evidence → plan deterministically →
**validate** → store only if validation passes. A plan that fails validation is never persisted
and never shown; the caller receives the report instead.
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session as DbSession

from app.curriculum.registry import get_path, lesson_index
from app.learning.roadmap import PlanningError, generate_plan, validate_plan
from app.learning.types import CurriculumNode, PlanWeekPlan
from app.models import (
    DiagnosticAttempt,
    DiagnosticResponse,
    Goal,
    Lesson,
    Objective,
    Plan,
    PlanItem,
    PlanWeek,
    Profile,
    User,
)
from app.services.progress import load_estimates
from app.utils import utcnow


class PlanValidationFailed(RuntimeError):
    def __init__(self, report: dict) -> None:
        super().__init__("The generated plan failed validation and was not published.")
        self.report = report


def curriculum_nodes(path_id: str) -> dict[str, CurriculumNode]:
    path = get_path(path_id)
    lessons = lesson_index(path_id)
    nodes: dict[str, CurriculumNode] = {}
    for objective in path["objectives"]:
        lesson_id = (objective.get("lesson") or {}).get("id")
        kind = "build" if objective.get("kind") == "project" else "learn"
        nodes[objective["id"]] = CurriculumNode(
            id=objective["id"],
            title=objective["title_en"],
            prerequisite_ids=tuple(objective.get("prerequisites", [])),
            difficulty=int(objective.get("difficulty", 1)),
            est_minutes=int(objective.get("est_minutes", 25)),
            sequence=int(objective.get("sequence", 0)),
            leaf_kind=kind,  # type: ignore[arg-type]
            lesson_id=lesson_id if lesson_id in lessons else None,
        )
    return nodes


def _provisionally_known(db: DbSession, user_id: str) -> frozenset[str]:
    """Objectives the learner answered correctly on a *hard* diagnostic item (difficulty >= 3).

    Deliberately not "mastery": it only downgrades a full lesson to a short confirmation check.
    """
    rows = db.execute(
        select(DiagnosticResponse.objective_id)
        .join(DiagnosticAttempt, DiagnosticResponse.attempt_id == DiagnosticAttempt.id)
        .where(
            DiagnosticAttempt.user_id == user_id,
            DiagnosticResponse.is_correct.is_(True),
            DiagnosticResponse.difficulty >= 3,
        )
    ).all()
    return frozenset(row[0] for row in rows)


def _known_lesson_ids(db: DbSession, path_id: str) -> set[str]:
    authored = set(lesson_index(path_id))
    stored = set(db.scalars(select(Lesson.id).where(Lesson.path_id == path_id)).all())
    return authored | stored


def _to_weeks(week_plans: list[PlanWeekPlan]) -> list[dict]:
    return [
        {
            "week_number": week.week_number,
            "steps": [
                {
                    "objective_id": step.objective_id,
                    "kind": step.kind,
                    "est_minutes": step.est_minutes,
                    "order_index": step.order_index,
                    "lesson_id": step.lesson_id,
                    "rationale": step.rationale,
                }
                for step in week.steps
            ],
            "total_minutes": week.total_minutes,
        }
        for week in week_plans
    ]


def generate_roadmap(
    db: DbSession,
    user: User,
    goal: Goal,
    *,
    now: datetime | None = None,
    persist: bool = True,
) -> dict:
    moment = now or utcnow()
    profile = db.get(Profile, user.id)
    weekly_minutes = goal.weekly_minutes or (profile.weekly_minutes if profile else 180)

    nodes = curriculum_nodes(goal.path_id)
    if not nodes:
        raise PlanningError(f"Curriculum path {goal.path_id!r} contains no objectives.")

    estimates = load_estimates(db, user.id)
    week_plans, skipped = generate_plan(
        nodes,
        estimates=estimates,
        now=moment,
        weekly_minutes=max(weekly_minutes, 60),
        provisional_known=_provisionally_known(db, user.id),
    )
    report = validate_plan(
        week_plans,
        nodes,
        weekly_minutes=max(weekly_minutes, 60),
        lesson_ids=_known_lesson_ids(db, goal.path_id),
    )
    if not report.ok:
        raise PlanValidationFailed(report.as_dict())

    result = {
        "weeks": _to_weeks(week_plans),
        "skipped": skipped,
        "validation": report.as_dict(),
        "weekly_minutes": weekly_minutes,
    }
    if not persist:
        return result

    # Supersede the previous plan for this goal, then store the new one atomically.
    previous = db.scalars(
        select(Plan).where(Plan.user_id == user.id, Plan.goal_id == goal.id, Plan.status == "active")
    ).all()
    next_version = 1
    for plan in previous:
        next_version = max(next_version, plan.version + 1)
        plan.status = "superseded"

    total_minutes = sum(week.total_minutes for week in week_plans)
    plan_row = Plan(
        user_id=user.id,
        goal_id=goal.id,
        version=next_version,
        status="active",
        generator="deterministic-v1",
        total_estimated_minutes=total_minutes,
        validation_report=report.as_dict(),
    )
    db.add(plan_row)
    db.flush()

    objective_rows = {
        row.id: row for row in db.scalars(select(Objective).where(Objective.path_id == goal.path_id))
    }

    for week in week_plans:
        week_row = PlanWeek(
            plan_id=plan_row.id,
            week_number=week.week_number,
            theme_en=_week_theme(week, objective_rows),
            theme_ar="",
        )
        db.add(week_row)
        db.flush()
        for step in week.steps:
            objective = objective_rows.get(step.objective_id)
            db.add(
                PlanItem(
                    plan_id=plan_row.id,
                    week_id=week_row.id,
                    order_index=step.order_index,
                    objective_id=step.objective_id,
                    lesson_id=step.lesson_id,
                    kind=step.kind,
                    est_minutes=step.est_minutes,
                    status="pending",
                    rationale_en=step.rationale,
                    rationale_ar=_objective_rationale_ar(step.kind, objective.title_ar if objective else ""),
                )
            )
    db.flush()
    result["plan_id"] = plan_row.id
    result["plan_version"] = plan_row.version
    result["total_estimated_minutes"] = total_minutes
    return result


def _week_theme(week: PlanWeekPlan, objectives: dict[str, Objective]) -> str:
    titles = [
        objectives[step.objective_id].title_en for step in week.steps if step.objective_id in objectives
    ]
    if not titles:
        return f"Week {week.week_number}"
    if len(titles) == 1:
        return titles[0]
    return f"{titles[0]} → {titles[-1]}"


def _objective_rationale_ar(kind: str, title_ar: str) -> str:
    mapping = {
        "review": "هدف مؤكَّد سابقاً، والتذكّر انخفض دون الحد؛ مراجعة قصيرة مناسبة.",
        "practice": "بدأت هذا الهدف ولم يُؤكَّد بعد؛ تدريب مع تغذية راجعة.",
        "build": "مشروع تطبيقي يجمع ما تعلمته حتى الآن.",
        "assess": "قياس قبل الانتقال إلى ما بعده.",
        "learn": "هدف جديد: ابدأ بالدرس ثم التدريب الموجّه.",
    }
    base = mapping.get(kind, mapping["learn"])
    return f"{base}" if not title_ar else f"{title_ar}: {base}"
