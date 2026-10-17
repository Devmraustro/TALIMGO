"""Evidence, mastery projection and the dashboard.

Evidence is written first and mastery is derived from it. The projection stored in
``mastery_estimates`` is a cache: if it is missing or carries a stale model version it is rebuilt
by replaying evidence, never patched.
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session as DbSession

from app.i18n import translate
from app.learning import mastery
from app.learning.selection import NextAction, PlannedItem, choose_next_action
from app.learning.types import EvidenceRecord, KnowledgeEstimate
from app.models import (
    Evidence,
    Goal,
    MasteryEstimate,
    Objective,
    Plan,
    PlanItem,
    PlanWeek,
    Profile,
    User,
)
from app.utils import ensure_aware, utcnow


def record_evidence(
    db: DbSession,
    *,
    user_id: str,
    objective_id: str,
    outcome: str,
    assisted: bool = False,
    kind: str = "practice",
    source_ref: str = "",
    occurred_at: datetime | None = None,
    meta: dict | None = None,
) -> Evidence:
    if outcome not in {"success", "failure"}:
        raise ValueError(f"Unsupported outcome {outcome!r}")
    row = Evidence(
        user_id=user_id,
        objective_id=objective_id,
        outcome=outcome,
        assisted=assisted,
        kind=kind,
        source_ref=source_ref,
        occurred_at=occurred_at or utcnow(),
        meta=meta or {},
    )
    db.add(row)
    db.flush()
    return row


def _records_for(db: DbSession, user_id: str, objective_id: str | None = None) -> list[EvidenceRecord]:
    query = select(Evidence).where(Evidence.user_id == user_id)
    if objective_id is not None:
        query = query.where(Evidence.objective_id == objective_id)
    rows = db.scalars(query.order_by(Evidence.occurred_at, Evidence.id)).all()
    return [
        EvidenceRecord(
            id=row.id,
            objective_id=row.objective_id,
            outcome=row.outcome,  # type: ignore[arg-type]
            occurred_at=ensure_aware(row.occurred_at),
            assisted=row.assisted,
            kind=row.kind,  # type: ignore[arg-type]
            source_ref=row.source_ref,
        )
        for row in rows
    ]


def recompute_mastery(
    db: DbSession, user_id: str, *, objective_id: str | None = None
) -> dict[str, KnowledgeEstimate]:
    """Replay evidence and refresh the cached projection. Deterministic and repeatable.

    Rows the replay no longer produces are deleted: after the ADR 0006 evidence boundary a
    diagnostic-only objective has no estimate, and a leftover cache row must not resurrect it
    or force a rebuild on every read.
    """
    estimates = mastery.replay(_records_for(db, user_id, objective_id))

    stale_query = select(MasteryEstimate).where(MasteryEstimate.user_id == user_id)
    if objective_id is not None:
        stale_query = stale_query.where(MasteryEstimate.objective_id == objective_id)
    for row in db.scalars(stale_query).all():
        if row.objective_id not in estimates:
            db.delete(row)

    for oid, estimate in estimates.items():
        row = db.scalar(
            select(MasteryEstimate).where(
                MasteryEstimate.user_id == user_id, MasteryEstimate.objective_id == oid
            )
        )
        if row is None:
            row = MasteryEstimate(
                user_id=user_id, objective_id=oid, model_version=estimate.model_version, phase=estimate.phase
            )
            db.add(row)
        row.model_version = estimate.model_version
        row.phase = estimate.phase
        row.unassisted_successes = estimate.unassisted_successes
        row.failures_while_retaining = estimate.failures_while_retaining
        row.has_delayed_success = estimate.has_delayed_success
        row.stability_days = estimate.stability_days
        row.last_evidence_at = estimate.last_evidence_at
    db.flush()
    return estimates


def load_estimates(db: DbSession, user_id: str) -> dict[str, KnowledgeEstimate]:
    """Read the cached projection, rebuilding it if any row is stale or missing."""
    rows = list(db.scalars(select(MasteryEstimate).where(MasteryEstimate.user_id == user_id)))
    stale = any(row.model_version != mastery.MODEL_VERSION for row in rows)
    if stale:
        return recompute_mastery(db, user_id)

    estimates = {
        row.objective_id: KnowledgeEstimate(
            objective_id=row.objective_id,
            phase=row.phase,  # type: ignore[arg-type]
            model_version=row.model_version,
            unassisted_successes=row.unassisted_successes,
            failures_while_retaining=row.failures_while_retaining,
            has_delayed_success=row.has_delayed_success,
            stability_days=row.stability_days,
            last_evidence_at=ensure_aware(row.last_evidence_at) if row.last_evidence_at else None,
        )
        for row in rows
    }

    # A missing objective with *mastery-bearing* recorded evidence means the cache is incomplete:
    # rebuild. Diagnostic-only evidence produces no estimate at all (ADR 0006), so it must not
    # trigger a rebuild on every read.
    evidence_objectives = {
        objective_id
        for objective_id, kind in db.execute(
            select(Evidence.objective_id, Evidence.kind).where(Evidence.user_id == user_id)
        ).all()
        if mastery.affects_mastery(kind)
    }
    if evidence_objectives - set(estimates):
        return recompute_mastery(db, user_id)
    return estimates


def active_goal(db: DbSession, user_id: str) -> Goal | None:
    return db.scalar(
        select(Goal)
        .where(Goal.user_id == user_id, Goal.status == "active")
        .order_by(Goal.created_at.desc())
        .limit(1)
    )


def objective_title(objective: Objective | None, locale: str, fallback: str = "") -> str:
    """Objective title in the learner's locale, falling back to English then to the id."""
    if objective is None:
        return fallback
    if locale == "ar" and objective.title_ar.strip():
        return objective.title_ar
    return objective.title_en or fallback


def planned_items(db: DbSession, plan: Plan | None, locale: str = "en") -> list[PlannedItem]:
    if plan is None:
        return []
    rows = db.execute(
        select(PlanItem, PlanWeek.week_number, Objective)
        .join(PlanWeek, PlanItem.week_id == PlanWeek.id)
        .join(Objective, PlanItem.objective_id == Objective.id)
        .where(PlanItem.plan_id == plan.id)
        .order_by(PlanWeek.week_number, PlanItem.order_index)
    ).all()
    return [
        PlannedItem(
            id=item.id,
            objective_id=item.objective_id,
            objective_title=objective_title(objective, locale, item.objective_id),
            kind=item.kind,
            est_minutes=item.est_minutes,
            status=item.status,
            week_number=week_number,
            order_index=item.order_index,
            lesson_id=item.lesson_id,
        )
        for item, week_number, objective in rows
    ]


def latest_plan(db: DbSession, user_id: str, goal_id: str | None = None) -> Plan | None:
    query = select(Plan).where(Plan.user_id == user_id, Plan.status == "active")
    if goal_id:
        query = query.where(Plan.goal_id == goal_id)
    return db.scalar(query.order_by(Plan.created_at.desc()).limit(1))


def _evidence_basis(estimate: KnowledgeEstimate | None, locale: str, title: str, now: datetime) -> str:
    """The evidence behind an estimate, composed in the learner's locale.

    Mirrors ``app.learning.mastery.explain`` sentence-for-sentence so the English text a learner
    sees is the same as before, while Arabic gets its own template rather than a translation miss.
    """
    if estimate is None:
        return translate("evidence.none", locale)
    if estimate.phase == "acquiring":
        if estimate.unassisted_successes == 0:
            return translate("evidence.no_unassisted", locale, title=title)
        missing: list[str] = []
        if estimate.unassisted_successes < mastery.PROMOTION_UNASSISTED_SUCCESSES:
            missing.append(
                translate(
                    "evidence.missing_successes",
                    locale,
                    n=mastery.PROMOTION_UNASSISTED_SUCCESSES - estimate.unassisted_successes,
                )
            )
        if not estimate.has_delayed_success:
            missing.append(translate("evidence.missing_delayed", locale))
        joiner = " و" if locale == "ar" else " and "
        return translate("evidence.acquiring", locale, title=title, missing=joiner.join(missing))
    value = mastery.retrievability(estimate, now)
    percent = round((value or 0.0) * 100)
    below = (value or 0.0) < mastery.RETRIEVABILITY_TARGET
    key = "evidence.retaining_below" if below else "evidence.retaining_ok"
    return translate(key, locale, title=title, n=estimate.unassisted_successes, percent=percent)


def localise_next_action(
    action: NextAction, locale: str, *, estimate: KnowledgeEstimate | None, now: datetime
) -> NextAction:
    """Render the chosen action's sentences in ``locale`` using its stable reason code."""
    from dataclasses import replace

    code = action.reason_code
    title = action.title
    if code in {"no_goal", "diagnostic", "generate_plan", "all_done"}:
        title = translate(f"action.{code}.title", locale)
    elif code in {"review_due", "review_unplanned"}:
        title = translate("action.review.title", locale, title=action.title.removeprefix("Review: "))

    if code == "all_done":
        rationale = translate("action.all_done.rationale", locale)
    else:
        rationale = translate(f"action.{code}.rationale", locale)

    basis = _evidence_basis(estimate, locale, action.title, now)
    return replace(action, title=title, rationale=rationale, evidence_basis=basis)


def build_dashboard(db: DbSession, user: User, *, now: datetime | None = None, locale: str = "en") -> dict:
    moment = now or utcnow()
    profile = db.get(Profile, user.id)
    goal = active_goal(db, user.id)
    estimates = load_estimates(db, user.id)
    plan = latest_plan(db, user.id, goal.id if goal else None)
    items = planned_items(db, plan, locale)

    objectives = {objective.id: objective for objective in db.scalars(select(Objective)).all()}
    titles = {
        objective_id: objective_title(row, locale, objective_id) for objective_id, row in objectives.items()
    }

    from app.models import DiagnosticAttempt

    diagnostic_done = (
        db.scalar(
            select(DiagnosticAttempt)
            .where(DiagnosticAttempt.user_id == user.id, DiagnosticAttempt.status == "completed")
            .limit(1)
        )
        is not None
    )

    action = choose_next_action(
        now=moment,
        has_goal=goal is not None,
        diagnostic_complete=diagnostic_done,
        planned_items=items,
        estimates=estimates,
        titles=titles,
        plan_ready=plan is not None,
    )
    action = localise_next_action(
        action,
        locale,
        estimate=estimates.get(action.objective_id) if action.objective_id else None,
        now=moment,
    )

    blockers: list[str] = []
    if plan is None and diagnostic_done:
        blockers.append(translate("blocker.no_plan", locale))
    if profile is not None and profile.weekly_minutes < 60:
        blockers.append(translate("blocker.low_budget", locale))

    recent = db.scalars(
        select(Evidence).where(Evidence.user_id == user.id).order_by(Evidence.occurred_at.desc()).limit(8)
    ).all()

    return {
        "goal": goal,
        "next_action": action,
        "mastery_summary": {
            **mastery.summary(estimates, moment),
            "recorded": len(estimates),
        },
        "recent_evidence": [
            {
                "objective_id": row.objective_id,
                "objective_title": titles.get(row.objective_id, row.objective_id),
                "outcome": row.outcome,
                "assisted": row.assisted,
                "kind": row.kind,
                "occurred_at": ensure_aware(row.occurred_at),
            }
            for row in recent
        ],
        "blockers": blockers,
    }
