"""Roadmap generation with a publication gate.

Sequence: build curriculum nodes → replay the learner's evidence → plan deterministically →
**validate** → store only if validation passes. A plan that fails validation is never persisted
and never shown; the caller receives the report instead.
"""

from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session as DbSession

from app.curriculum.registry import get_path, lesson_index, localised
from app.learning.roadmap import PlanningError, generate_plan, validate_plan
from app.learning.schedule import (
    ScheduleEntry,
    ScheduleRow,
    adherence,
    build_schedule,
    daily_budget,
    due_today,
    scheduled_date,
    weekday_set,
)
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
    PracticeSession,
    Profile,
    User,
)
from app.services.progress import load_estimates
from app.utils import ensure_aware, utcnow


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
    available = weekday_set(profile.availability_days if profile else None)
    order = [(week.week_number, index) for week in week_plans for index in range(len(week.steps))]
    entries = [
        ScheduleEntry(key=f"{week_number}:{index}", est_minutes=step.est_minutes)
        for (week_number, index), step in zip(
            order, [step for week in week_plans for step in week.steps], strict=False
        )
    ]
    starts_on = moment.date()
    offsets = build_schedule(
        entries,
        daily_minutes=daily_budget(max(weekly_minutes, 60), profile.availability_days if profile else None),
        available_weekdays=available,
        start_weekday=starts_on.weekday(),
    )
    day_by_key = {entry.key: offset for entry, offset in zip(entries, offsets, strict=False)}

    plan_row = Plan(
        user_id=user.id,
        goal_id=goal.id,
        version=next_version,
        status="active",
        generator="deterministic-v1",
        total_estimated_minutes=total_minutes,
        validation_report=report.as_dict(),
        starts_on=starts_on,
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
            theme_en=_week_theme(week, objective_rows, "en"),
            theme_ar=_week_theme(week, objective_rows, "ar"),
        )
        db.add(week_row)
        db.flush()
        for index, step in enumerate(week.steps):
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
                    scheduled_day=day_by_key.get(f"{week.week_number}:{index}", 0),
                )
            )
    db.flush()
    result["plan_id"] = plan_row.id
    result["plan_version"] = plan_row.version
    result["total_estimated_minutes"] = total_minutes
    return result


def _week_theme(week: PlanWeekPlan, objectives: dict[str, Objective], locale: str) -> str:
    """The week's theme: the span of its steps' objective titles, in one language.

    Arabic falls back to the English title per objective when a translation is missing (the
    documented content fallback), so a partly translated plan still shows a usable theme.
    """
    titles: list[str] = []
    for step in week.steps:
        objective = objectives.get(step.objective_id)
        if objective is None:
            continue
        translated = objective.title_ar.strip() if locale == "ar" else ""
        titles.append(translated or objective.title_en)
    if not titles:
        return f"Week {week.week_number}" if locale == "en" else f"الأسبوع {week.week_number}"
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


# --------------------------------------------------------------------------------------
# The study schedule: dated view, today's missions, deterministic re-planning
# --------------------------------------------------------------------------------------


def _plan_rows(db: DbSession, plan: Plan) -> list[PlanItem]:
    return list(
        db.scalars(
            select(PlanItem).where(PlanItem.plan_id == plan.id).order_by(PlanItem.order_index, PlanItem.id)
        ).all()
    )


def _schedule_rows(plan: Plan, items: list[PlanItem]) -> list[ScheduleRow]:
    return [
        ScheduleRow(
            key=item.id,
            est_minutes=item.est_minutes,
            scheduled_day=0 if item.scheduled_day is None else item.scheduled_day,
            status=item.status,
            completed_on=item.completed_at.date() if item.completed_at else None,
        )
        for item in items
    ]


def actual_minutes(db: DbSession, plan: Plan) -> int:
    """Minutes actually spent in practice sessions attached to this plan (for calibration)."""
    sessions = db.scalars(
        select(PracticeSession).where(
            PracticeSession.plan_item_id.in_([item.id for item in _plan_rows(db, plan)] or [""])
        )
    ).all()
    total = 0.0
    for session in sessions:
        if session.completed_at is None or session.started_at is None:
            continue
        delta = (ensure_aware(session.completed_at) - ensure_aware(session.started_at)).total_seconds() / 60
        total += max(0.0, min(delta, 240.0))
    return round(total)


def schedule_payload(db: DbSession, plan: Plan, *, locale: str = "en", today: date | None = None) -> dict:
    """The plan as a calendar: dates per item, today's missions, and how it is actually going."""
    moment = today or utcnow().date()
    profile = db.get(Profile, plan.user_id)
    items = _plan_rows(db, plan)
    rows = _schedule_rows(plan, items)
    by_id = {row.key: row for row in rows}

    weeks: dict[str, dict] = {}
    for week in db.scalars(
        select(PlanWeek).where(PlanWeek.plan_id == plan.id).order_by(PlanWeek.week_number)
    ).all():
        weeks[week.id] = {
            "week_number": week.week_number,
            "theme": localised({"theme_en": week.theme_en, "theme_ar": week.theme_ar}, "theme", locale)
            or f"Week {week.week_number}",
            "items": [],
        }

    objectives = {row.id: row for row in db.scalars(select(Objective)).all()}
    for item in items:
        row = by_id[item.id]
        week = weeks.get(item.week_id)
        if week is None:
            continue
        objective = objectives.get(item.objective_id)
        week["items"].append(
            {
                "id": item.id,
                "order_index": item.order_index,
                "objective_id": item.objective_id,
                "objective_title": localised(
                    {
                        "title_en": objective.title_en if objective else item.objective_id,
                        "title_ar": objective.title_ar if objective else "",
                    },
                    "title",
                    locale,
                ),
                "kind": item.kind,
                "lesson_id": item.lesson_id,
                "est_minutes": item.est_minutes,
                "status": item.status,
                "scheduled_day": row.scheduled_day,
                "scheduled_for": scheduled_date(plan.starts_on, row.scheduled_day).isoformat(),
                "completed_at": item.completed_at,
                "rationale": localised(
                    {"rationale_en": item.rationale_en, "rationale_ar": item.rationale_ar},
                    "rationale",
                    locale,
                ),
            }
        )

    today_keys = due_today(rows, starts_on=plan.starts_on, today=moment)
    today_items = [entry for key in today_keys for entry in _find(weeks, key)]
    report = adherence(rows, starts_on=plan.starts_on, today=moment)
    report["minutes"]["actual"] = actual_minutes(db, plan)

    return {
        "plan_id": plan.id,
        "version": plan.version,
        "starts_on": plan.starts_on.isoformat(),
        "daily_minutes": daily_budget(
            profile.weekly_minutes if profile else 180,
            profile.availability_days if profile else None,
        ),
        "total_estimated_minutes": plan.total_estimated_minutes,
        "weeks": [weeks[key] for key in weeks],
        "today": {
            "date": moment.isoformat(),
            "items": today_items,
            "minutes_planned": sum(entry["est_minutes"] for entry in today_items),
        },
        "adherence": report,
    }


def _find(weeks: dict[str, dict], item_id: str) -> list[dict]:
    for week in weeks.values():
        for entry in week["items"]:
            if entry["id"] == item_id:
                return [entry]
    return []


def reschedule_plan(db: DbSession, plan: Plan, *, today: date | None = None) -> dict:
    """Re-place unfinished work from today, keeping everything already done where it was.

    Deterministic: the same completed set, availability and date produce the same result, so calling
    this twice in a row does not shift dates twice.
    """
    moment = today or utcnow().date()
    profile = db.get(Profile, plan.user_id)
    items = _plan_rows(db, plan)
    pending = [item for item in items if item.status != "completed"]
    completed = [item for item in items if item.status == "completed"]

    earliest = max(0, (moment - plan.starts_on).days)
    offsets = build_schedule(
        [ScheduleEntry(key=item.id, est_minutes=item.est_minutes) for item in pending],
        daily_minutes=daily_budget(
            profile.weekly_minutes if profile else 180,
            profile.availability_days if profile else None,
        ),
        available_weekdays=weekday_set(profile.availability_days if profile else None),
        earliest_day=earliest,
        start_weekday=plan.starts_on.weekday(),
    )

    moved = 0
    for item, offset in zip(pending, offsets, strict=False):
        if item.scheduled_day != offset:
            item.scheduled_day = offset
            moved += 1
    db.flush()
    return {
        "moved": moved,
        "completed_untouched": len(completed),
        "starts_on": plan.starts_on.isoformat(),
    }
