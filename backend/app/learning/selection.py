"""Next-action selection — deterministic, explainable, and never delegated to a model.

Priority order (documented so the behaviour can be reviewed and tested):

1. No goal yet           → invite the learner to define one.
2. Goal but no diagnostic → run the diagnostic.
3. An in-progress plan item → continue it.
4. Review that is due     → short review of a confirmed objective whose recall has decayed.
5. The next pending plan item → lesson if new, practice if in progress.
6. Nothing left pending   → suggest the next project/milestone, or idle.

Every returned action carries the evidence it is based on, so the UI can justify itself.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from app.learning.mastery import explain, needs_review, phase_for, retrievability
from app.learning.types import KnowledgeEstimate


@dataclass(frozen=True)
class PlannedItem:
    id: str
    objective_id: str
    objective_title: str
    kind: str
    est_minutes: int
    status: str
    week_number: int
    order_index: int
    lesson_id: str | None = None


@dataclass(frozen=True)
class NextAction:
    kind: str
    title: str
    rationale: str
    evidence_basis: str
    est_minutes: int = 10
    objective_id: str | None = None
    lesson_id: str | None = None
    plan_item_id: str | None = None


def choose_next_action(
    *,
    now: datetime,
    has_goal: bool,
    diagnostic_complete: bool,
    planned_items: list[PlannedItem],
    estimates: dict[str, KnowledgeEstimate],
    titles: dict[str, str],
    plan_ready: bool,
) -> NextAction:
    if not has_goal:
        return NextAction(
            kind="idle",
            title="Define your learning goal",
            rationale="TALIMGO plans from a goal: tell it what you want to be able to do.",
            evidence_basis="No active goal on this account.",
            est_minutes=3,
        )

    if not diagnostic_complete:
        return NextAction(
            kind="diagnostic",
            title="Take the starting check",
            rationale=(
                "A short adaptive check places you correctly and keeps you from re-learning what "
                "you already know."
            ),
            evidence_basis="No diagnostic evidence recorded for this goal yet.",
            est_minutes=12,
        )

    if not plan_ready:
        return NextAction(
            kind="idle",
            title="Generate your roadmap",
            rationale="Your placement is recorded; the next step is a plan built from it.",
            evidence_basis="Diagnostic complete, no active plan.",
            est_minutes=1,
        )

    ordered = sorted(planned_items, key=lambda item: (item.week_number, item.order_index))

    for item in ordered:
        if item.status == "in_progress":
            return _from_plan_item(item, estimates, now, reason="This is the task you started.")

    for item in ordered:
        estimate = estimates.get(item.objective_id)
        if phase_for(estimate) == "retaining" and estimate is not None and needs_review(estimate, now):
            return NextAction(
                kind="review",
                title=f"Review: {item.objective_title}",
                rationale="You confirmed this earlier and recall has faded — a short review keeps it.",
                evidence_basis=explain(estimate, now, item.objective_title),
                est_minutes=max(6, item.est_minutes // 2),
                objective_id=item.objective_id,
                lesson_id=item.lesson_id,
                plan_item_id=item.id,
            )

    for item in ordered:
        if item.status == "pending":
            return _from_plan_item(
                item, estimates, now, reason="It is the next unfinished step in your plan."
            )

    due_reviews = [
        (estimate, objective_id)
        for objective_id, estimate in estimates.items()
        if needs_review(estimate, now)
    ]
    if due_reviews:
        estimate, objective_id = sorted(due_reviews, key=lambda pair: pair[1])[0]
        title = titles.get(objective_id, objective_id)
        return NextAction(
            kind="review",
            title=f"Review: {title}",
            rationale="Everything in your plan is done; this confirmed objective is due for review.",
            evidence_basis=explain(estimate, now, title),
            est_minutes=8,
            objective_id=objective_id,
        )

    return NextAction(
        kind="idle",
        title="Your plan is complete",
        rationale=("Every planned step is finished. Measure again, or set a harder goal to continue."),
        evidence_basis=f"{len(estimates)} objective(s) with recorded evidence.",
        est_minutes=5,
    )


def _from_plan_item(
    item: PlannedItem, estimates: dict[str, KnowledgeEstimate], now: datetime, *, reason: str
) -> NextAction:
    estimate = estimates.get(item.objective_id)
    state = phase_for(estimate)
    if item.kind == "learn" and state != "unseen":
        kind = "practice"
    else:
        kind = item.kind if item.kind in {"learn", "practice", "assess", "review", "build"} else "practice"

    if estimate is None:
        basis = "No evidence recorded for this objective yet."
    else:
        value = retrievability(estimate, now)
        basis = explain(estimate, now, item.objective_title)
        if value is not None:
            basis += f" Current estimated recall: {round(value * 100)}%."

    return NextAction(
        kind=kind,
        title=item.objective_title,
        rationale=reason,
        evidence_basis=basis,
        est_minutes=item.est_minutes,
        objective_id=item.objective_id,
        lesson_id=item.lesson_id,
        plan_item_id=item.id,
    )
