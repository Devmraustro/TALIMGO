"""Roadmap planning and the publication gate.

The product rule under test: a plan is never stored or shown unless it passes validation.
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest

from app.learning import roadmap
from app.learning.mastery import MODEL_VERSION
from app.learning.types import CurriculumNode, KnowledgeEstimate, PlanStep, PlanWeekPlan

NOW = datetime(2026, 3, 1, 12, 0, tzinfo=UTC)


def nodes() -> dict[str, CurriculumNode]:
    """a → b → c , with d independent."""
    return {
        "a": CurriculumNode(id="a", title="A", est_minutes=30, sequence=10, lesson_id="lesson-a"),
        "b": CurriculumNode(
            id="b", title="B", prerequisite_ids=("a",), est_minutes=30, sequence=20, lesson_id="lesson-b"
        ),
        "c": CurriculumNode(
            id="c", title="C", prerequisite_ids=("b",), est_minutes=40, sequence=30, lesson_id="lesson-c"
        ),
        "d": CurriculumNode(id="d", title="D", est_minutes=20, sequence=15, lesson_id="lesson-d"),
    }


LESSONS = {"lesson-a", "lesson-b", "lesson-c", "lesson-d"}


def retaining(objective_id: str, *, days_since: float, stability: float) -> KnowledgeEstimate:
    return KnowledgeEstimate(
        objective_id=objective_id,
        phase="retaining",
        model_version=MODEL_VERSION,
        unassisted_successes=4,
        has_delayed_success=True,
        stability_days=stability,
        last_evidence_at=NOW - timedelta(days=days_since),
    )


def test_plan_respects_prerequisite_order() -> None:
    weeks, _ = roadmap.generate_plan(nodes(), estimates={}, now=NOW, weekly_minutes=120)
    order = [step.objective_id for week in weeks for step in week.steps]
    assert order.index("a") < order.index("b") < order.index("c")


def test_plan_is_deterministic() -> None:
    first, _ = roadmap.generate_plan(nodes(), estimates={}, now=NOW, weekly_minutes=120)
    second, _ = roadmap.generate_plan(nodes(), estimates={}, now=NOW, weekly_minutes=120)
    assert first == second


def test_confirmed_and_not_due_objective_is_skipped() -> None:
    estimates = {"a": retaining("a", days_since=0.1, stability=30.0)}
    weeks, skipped = roadmap.generate_plan(nodes(), estimates=estimates, now=NOW, weekly_minutes=120)
    order = [step.objective_id for week in weeks for step in week.steps]
    assert "a" not in order
    assert any(entry["objective_id"] == "a" for entry in skipped)


def test_confirmed_but_due_objective_becomes_a_review() -> None:
    estimates = {"a": retaining("a", days_since=40, stability=2.0)}
    weeks, _ = roadmap.generate_plan(nodes(), estimates=estimates, now=NOW, weekly_minutes=120)
    steps = {step.objective_id: step for week in weeks for step in week.steps}
    assert steps["a"].kind == "review"
    assert steps["a"].est_minutes <= 10


def test_weeks_respect_the_time_budget() -> None:
    weeks, _ = roadmap.generate_plan(nodes(), estimates={}, now=NOW, weekly_minutes=60)
    assert len(weeks) >= 2
    for week in weeks[:-1]:
        assert week.total_minutes <= 60


def test_cycle_in_the_graph_is_a_planning_error() -> None:
    cyclic = nodes()
    cyclic["a"] = CurriculumNode(
        id="a", title="A", prerequisite_ids=("c",), sequence=10, lesson_id="lesson-a"
    )
    with pytest.raises(roadmap.PlanningError):
        roadmap.generate_plan(cyclic, estimates={}, now=NOW, weekly_minutes=120)


def test_unknown_prerequisite_is_a_planning_error() -> None:
    broken = nodes()
    broken["b"] = CurriculumNode(
        id="b", title="B", prerequisite_ids=("does-not-exist",), est_minutes=30, sequence=20
    )
    with pytest.raises(roadmap.PlanningError):
        roadmap.generate_plan(broken, estimates={}, now=NOW, weekly_minutes=120)


def valid_weeks() -> list[PlanWeekPlan]:
    steps = (
        PlanStep(objective_id="a", kind="learn", est_minutes=30, order_index=0, lesson_id="lesson-a"),
        PlanStep(objective_id="b", kind="learn", est_minutes=30, order_index=1, lesson_id="lesson-b"),
        PlanStep(objective_id="c", kind="learn", est_minutes=40, order_index=2, lesson_id="lesson-c"),
    )
    return [PlanWeekPlan(week_number=1, steps=steps)]


def test_valid_plan_passes_validation() -> None:
    report = roadmap.validate_plan(valid_weeks(), nodes(), weekly_minutes=120, lesson_ids=LESSONS)
    assert report.ok, report.as_dict()
    assert "prerequisite_order" in report.checked


def test_prerequisite_order_violation_is_an_error() -> None:
    weeks = valid_weeks()
    reversed_steps = tuple(reversed(weeks[0].steps))
    report = roadmap.validate_plan(
        [PlanWeekPlan(week_number=1, steps=reversed_steps)], nodes(), weekly_minutes=120, lesson_ids=LESSONS
    )
    assert not report.ok
    assert any(issue.code == "E_PREREQ_ORDER" for issue in report.errors)


def test_duplicate_objective_is_an_error() -> None:
    steps = (
        PlanStep(objective_id="a", kind="learn", est_minutes=30, order_index=0, lesson_id="lesson-a"),
        PlanStep(objective_id="a", kind="review", est_minutes=10, order_index=1, lesson_id="lesson-a"),
    )
    report = roadmap.validate_plan(
        [PlanWeekPlan(week_number=1, steps=steps)], nodes(), weekly_minutes=120, lesson_ids=LESSONS
    )
    assert any(issue.code == "E_DUPLICATE_OBJECTIVE" for issue in report.errors)


def test_unknown_objective_and_unknown_lesson_are_errors() -> None:
    steps = (
        PlanStep(objective_id="ghost", kind="learn", est_minutes=30, order_index=0, lesson_id="lesson-a"),
        PlanStep(objective_id="a", kind="learn", est_minutes=30, order_index=1, lesson_id="lesson-ghost"),
    )
    report = roadmap.validate_plan(
        [PlanWeekPlan(week_number=1, steps=steps)], nodes(), weekly_minutes=120, lesson_ids=LESSONS
    )
    codes = {issue.code for issue in report.errors}
    assert "E_UNKNOWN_OBJECTIVE" in codes
    assert "E_UNKNOWN_LESSON" in codes


def test_implausible_duration_is_an_error() -> None:
    steps = (PlanStep(objective_id="a", kind="learn", est_minutes=0, order_index=0, lesson_id="lesson-a"),)
    report = roadmap.validate_plan(
        [PlanWeekPlan(week_number=1, steps=steps)], nodes(), weekly_minutes=120, lesson_ids=LESSONS
    )
    assert any(issue.code == "E_DURATION" for issue in report.errors)


def test_week_over_budget_is_an_error() -> None:
    steps = tuple(
        PlanStep(
            objective_id=objective_id,
            kind="learn",
            est_minutes=100,
            order_index=index,
            lesson_id=f"lesson-{objective_id}",
        )
        for index, objective_id in enumerate(("a", "b", "c"))
    )
    report = roadmap.validate_plan(
        [PlanWeekPlan(week_number=1, steps=steps)], nodes(), weekly_minutes=60, lesson_ids=LESSONS
    )
    assert any(issue.code == "E_WEEK_BUDGET" for issue in report.errors)


def test_empty_plan_is_an_error() -> None:
    report = roadmap.validate_plan([], nodes(), weekly_minutes=120, lesson_ids=LESSONS)
    assert any(issue.code == "E_PLAN_EMPTY" for issue in report.errors)


def test_missing_lesson_is_a_warning_not_a_failure() -> None:
    steps = (PlanStep(objective_id="a", kind="learn", est_minutes=30, order_index=0, lesson_id=None),)
    report = roadmap.validate_plan(
        [PlanWeekPlan(week_number=1, steps=steps)], nodes(), weekly_minutes=120, lesson_ids=LESSONS
    )
    assert report.ok
    assert any(issue.code == "W_NO_LESSON" for issue in report.warnings)


def test_cyclic_curriculum_fails_validation_even_if_steps_look_ordered() -> None:
    cyclic = nodes()
    cyclic["a"] = CurriculumNode(
        id="a", title="A", prerequisite_ids=("c",), sequence=10, lesson_id="lesson-a"
    )
    steps = (
        PlanStep(objective_id="a", kind="learn", est_minutes=30, order_index=0, lesson_id="lesson-a"),
        PlanStep(objective_id="c", kind="learn", est_minutes=30, order_index=1, lesson_id="lesson-c"),
    )
    report = roadmap.validate_plan(
        [PlanWeekPlan(week_number=1, steps=steps)], cyclic, weekly_minutes=120, lesson_ids=LESSONS
    )
    assert any(issue.code == "E_CURRICULUM_CYCLE" for issue in report.errors)

def test_provisionally_known_objectives_become_confirmation_checks() -> None:
    """A hard diagnostic item answered correctly must not produce a full first-time lesson."""
    from app.learning.roadmap import generate_plan
    from app.services.plans import curriculum_nodes

    nodes = curriculum_nodes("python-foundations")
    estimates = {}  # nobody has any evidence yet
    weeks, _skipped = generate_plan(
        nodes,
        estimates=estimates,
        now=datetime(2026, 1, 1, tzinfo=UTC),
        weekly_minutes=240,
        provisional_known=frozenset({"py:values", "py:strings"}),
    )
    steps = [step for week in weeks for step in week.steps]
    known = {step.objective_id: step for step in steps if step.objective_id in {"py:values", "py:strings"}}
    assert set(known) == {"py:values", "py:strings"}, "known objectives must stay in the plan"
    for step in known.values():
        assert step.kind == "assess", f"{step.objective_id} should be a confirmation check"
        assert step.est_minutes <= 10
        assert step.lesson_id is None, "a confirmation check must not carry the lesson text"
    others = [step for step in steps if step.objective_id not in known]
    assert all(step.kind in {"learn", "practice", "assess", "review", "build"} for step in others)
    assert any(step.kind == "learn" for step in others), "unknown objectives still start with a lesson"
