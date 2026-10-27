"""Roadmap planning and validation — deterministic, pure, testable.

The product rule (master reference section 6.4, implementation directive item 4) is explicit:
a plan is never published just because it is well-formed. Before anything is stored or shown,
:func:`validate_plan` checks prerequisite order, completeness, time budgets, durations, the
referenced lessons and the curriculum graph itself. A plan with errors is rejected.
"""

from __future__ import annotations

from datetime import UTC, datetime

from app.learning.mastery import needs_review, phase_for
from app.learning.types import (
    CurriculumNode,
    KnowledgeEstimate,
    PlanStep,
    PlanWeekPlan,
    ValidationIssue,
    ValidationReport,
)

WEEK_BUDGET_TOLERANCE = 1.25
MAX_STEPS = 400


class PlanningError(ValueError):
    """The curriculum or the request cannot produce a valid plan."""


def _state(node_id: str, estimates: dict[str, KnowledgeEstimate]) -> str:
    return phase_for(estimates.get(node_id))


def topological_order(
    nodes: dict[str, CurriculumNode],
    *,
    estimates: dict[str, KnowledgeEstimate],
    now: datetime,
    include_review: bool = True,
) -> list[CurriculumNode]:
    """Kahn's algorithm with a stable, explainable tie-break.

    Nodes already *retaining* are skipped unless they are due for review, in which case they are
    planned as a short review instead of a full lesson.
    """
    indegree: dict[str, int] = dict.fromkeys(nodes, 0)
    dependents: dict[str, list[str]] = {node_id: [] for node_id in nodes}
    for node in nodes.values():
        for prereq in node.prerequisite_ids:
            if prereq not in nodes:
                raise PlanningError(
                    f"Objective {node.id!r} lists unknown prerequisite {prereq!r}; "
                    "the curriculum graph is inconsistent."
                )
            indegree[node.id] += 1
            dependents[prereq].append(node.id)

    ready = sorted(
        [node_id for node_id, count in indegree.items() if count == 0],
        key=lambda node_id: (nodes[node_id].sequence, node_id),
    )
    ordered: list[CurriculumNode] = []
    while ready:
        node_id = ready.pop(0)
        ordered.append(nodes[node_id])
        newly_ready = []
        for dependent in dependents[node_id]:
            indegree[dependent] -= 1
            if indegree[dependent] == 0:
                newly_ready.append(dependent)
        if newly_ready:
            ready.extend(newly_ready)
            ready.sort(key=lambda nid: (nodes[nid].sequence, nid))

    if len(ordered) != len(nodes):
        unresolved = sorted(set(nodes) - {node.id for node in ordered})
        raise PlanningError(
            "The curriculum graph contains a cycle (or unreachable prerequisites) involving: "
            + ", ".join(unresolved)
        )

    result: list[CurriculumNode] = []
    for node in ordered:
        state = _state(node.id, estimates)
        if state == "retaining":
            if include_review and needs_review(estimates[node.id], now):
                result.append(node)
            continue
        result.append(node)
    return result


def _step_for(
    node: CurriculumNode,
    state: str,
    order_index: int,
    *,
    provisional_known: frozenset[str] = frozenset(),
) -> PlanStep:
    if node.leaf_kind == "build" and state != "retaining":
        # A build objective is never downgraded to a quiz — not by provisional knowledge and not
        # by partial practice evidence. Capability at building is demonstrated by an artefact
        # (ADR 0006 keeps project evidence its own kind; ADR 0008), so the step stays a build
        # until the objective is confirmed, after which ordinary review applies.
        return PlanStep(
            objective_id=node.id,
            kind="build",
            est_minutes=node.est_minutes,
            order_index=order_index,
            lesson_id=node.lesson_id,
            rationale="Project: build the artefact and submit it against the rubric.",
        )
    if node.id in provisional_known and state != "retaining":
        # The learner answered a hard item correctly on the starting check. That is evidence, not
        # proof: they get a short confirmatory check instead of a lesson or a full practice set, and
        # mastery still only follows from unassisted, spaced success (ADR 0004).
        return PlanStep(
            objective_id=node.id,
            kind="assess",
            est_minutes=10,
            order_index=order_index,
            lesson_id=None,  # a confirmation check must not come with the lesson text
            rationale=(
                "You answered this correctly on the starting check — a short check confirms it "
                "before you move on."
            ),
        )
    if state == "retaining":
        return PlanStep(
            objective_id=node.id,
            kind="review",
            est_minutes=8,
            order_index=order_index,
            lesson_id=node.lesson_id,
            rationale="Confirmed earlier, but recall has dropped below the review threshold.",
        )
    if state == "acquiring":
        return PlanStep(
            objective_id=node.id,
            kind="practice",
            est_minutes=max(10, node.est_minutes // 2),
            order_index=order_index,
            lesson_id=node.lesson_id,
            rationale="Already started, not yet confirmed: practise with feedback.",
        )
    return PlanStep(
        objective_id=node.id,
        kind=node.leaf_kind,
        est_minutes=node.est_minutes,
        order_index=order_index,
        lesson_id=node.lesson_id,
        rationale="New objective: lesson first, then guided practice.",
    )


def build_weeks(
    steps: list[PlanStep], *, weekly_minutes: int, weeks_target: int | None = None
) -> list[PlanWeekPlan]:
    """Fill weeks to the weekly time budget, preserving plan order."""
    if weekly_minutes <= 0:
        raise PlanningError("Weekly time budget must be positive.")
    weeks: list[PlanWeekPlan] = []
    current: list[PlanStep] = []
    used = 0
    for step in steps:
        remaining = weekly_minutes - used
        if (
            current
            and step.est_minutes > remaining
            and (weeks_target is None or len(weeks) + 1 < weeks_target)
        ):
            weeks.append(PlanWeekPlan(week_number=len(weeks) + 1, steps=tuple(current)))
            current = []
            used = 0
        current.append(step)
        used += step.est_minutes
    if current:
        weeks.append(PlanWeekPlan(week_number=len(weeks) + 1, steps=tuple(current)))
    return weeks


def generate_plan(
    nodes: dict[str, CurriculumNode],
    *,
    estimates: dict[str, KnowledgeEstimate],
    now: datetime,
    weekly_minutes: int,
    max_steps: int = MAX_STEPS,
    provisional_known: frozenset[str] = frozenset(),
) -> tuple[list[PlanWeekPlan], list[dict[str, str]]]:
    """Produce a deterministic roadmap plus the list of objectives deliberately skipped."""
    ordered = topological_order(nodes, estimates=estimates, now=now)
    skipped: list[dict[str, str]] = []
    for node in nodes.values():
        if node not in ordered:
            reason = (
                "Already confirmed and not yet due for review."
                if _state(node.id, estimates) == "retaining"
                else "Not reachable in this plan."
            )
            skipped.append({"objective_id": node.id, "reason": reason})

    steps = [
        _step_for(node, _state(node.id, estimates), index, provisional_known=provisional_known)
        for index, node in enumerate(ordered)
    ]
    if len(steps) > max_steps:
        steps = steps[:max_steps]
    weeks = build_weeks(steps, weekly_minutes=weekly_minutes)
    return weeks, skipped


def validate_plan(
    weeks: list[PlanWeekPlan],
    nodes: dict[str, CurriculumNode],
    *,
    weekly_minutes: int,
    lesson_ids: set[str],
) -> ValidationReport:
    """The publication gate. Any error means the plan must not be stored or shown."""
    errors: list[ValidationIssue] = []
    warnings: list[ValidationIssue] = []
    checked = (
        "non_empty",
        "known_objectives",
        "no_duplicates",
        "prerequisite_order",
        "durations",
        "week_budget",
        "lesson_references",
        "graph_acyclic",
    )

    flat: list[PlanStep] = [step for week in weeks for step in week.steps]

    if not flat:
        errors.append(ValidationIssue("E_PLAN_EMPTY", "The plan contains no steps."))

    seen: set[str] = set()
    for step in flat:
        if step.objective_id in seen:
            errors.append(
                ValidationIssue(
                    "E_DUPLICATE_OBJECTIVE",
                    f"Objective {step.objective_id} appears more than once in the plan.",
                    objective_id=step.objective_id,
                )
            )
        seen.add(step.objective_id)

    for step in flat:
        if step.objective_id not in nodes:
            errors.append(
                ValidationIssue(
                    "E_UNKNOWN_OBJECTIVE",
                    f"Step references objective {step.objective_id!r}, which is not in this curriculum.",
                    objective_id=step.objective_id,
                )
            )
        if step.est_minutes <= 0 or step.est_minutes > 240:
            errors.append(
                ValidationIssue(
                    "E_DURATION",
                    f"Step for {step.objective_id} has an implausible duration ({step.est_minutes} min).",
                    objective_id=step.objective_id,
                )
            )
        if step.kind in {"learn", "practice"} and step.lesson_id is None:
            warnings.append(
                ValidationIssue(
                    "W_NO_LESSON",
                    f"Step for {step.objective_id} has no lesson attached; the learner will see "
                    "practice only.",
                    severity="warning",
                    objective_id=step.objective_id,
                )
            )
        if step.kind == "assess" and step.lesson_id is not None:
            errors.append(
                ValidationIssue(
                    "E_ASSESS_WITH_LESSON",
                    f"Confirmation check for {step.objective_id} must not attach lesson "
                    f"{step.lesson_id!r}: the check would come with its own answer text.",
                    objective_id=step.objective_id,
                )
            )
        if step.lesson_id is not None and step.lesson_id not in lesson_ids:
            errors.append(
                ValidationIssue(
                    "E_UNKNOWN_LESSON",
                    f"Step for {step.objective_id} references lesson {step.lesson_id!r}, "
                    "which does not exist.",
                    objective_id=step.objective_id,
                )
            )

    position = {step.objective_id: index for index, step in enumerate(flat)}
    for step in flat:
        node = nodes.get(step.objective_id)
        if node is None:
            continue
        for prereq in node.prerequisite_ids:
            prereq_index = position.get(prereq)
            if prereq_index is None:
                # The prerequisite was not planned: acceptable only if it is already confirmed,
                # which the planner guarantees by construction. Flag as a warning so a reviewer
                # can see the assumption instead of trusting it.
                warnings.append(
                    ValidationIssue(
                        "W_PREREQ_NOT_PLANNED",
                        f"{step.objective_id} depends on {prereq}, which is not in this plan; "
                        "the planner assumed it is already confirmed.",
                        severity="warning",
                        objective_id=step.objective_id,
                    )
                )
            elif prereq_index > position[step.objective_id]:
                errors.append(
                    ValidationIssue(
                        "E_PREREQ_ORDER",
                        f"{step.objective_id} is planned before its prerequisite {prereq}.",
                        objective_id=step.objective_id,
                    )
                )

    for week in weeks:
        budget = weekly_minutes * WEEK_BUDGET_TOLERANCE
        if week.total_minutes > budget:
            errors.append(
                ValidationIssue(
                    "E_WEEK_BUDGET",
                    f"Week {week.week_number} needs {week.total_minutes} minutes, more than the "
                    f"allowed {int(budget)} for a {weekly_minutes}-minute week.",
                )
            )

    # The graph itself must be acyclic; a cyclic curriculum can never produce a valid plan.
    try:
        topological_order(nodes, estimates={}, now=_EPOCH)
    except PlanningError as exc:
        errors.append(ValidationIssue("E_CURRICULUM_CYCLE", str(exc)))

    return ValidationReport(errors=tuple(errors), warnings=tuple(warnings), checked=checked)


_EPOCH = datetime(1970, 1, 1, tzinfo=UTC)
