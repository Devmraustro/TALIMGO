"""Value types for the deterministic learning engine.

These are plain frozen dataclasses on purpose: the engine is pure, has no I/O, and must be
usable from tests, scripts and replay jobs without a database or web framework. It also never
imports the ORM, the AI layer or the web layer (enforced by ``tests/test_learning_purity.py``).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Literal

Outcome = Literal["success", "failure"]
EvidenceKind = Literal["diagnostic", "practice", "assessment", "project"]
Phase = Literal["acquiring", "retaining"]


@dataclass(frozen=True)
class EvidenceRecord:
    """One thing that actually happened, as recorded at the grading boundary."""

    id: str
    objective_id: str
    outcome: Outcome
    occurred_at: datetime
    assisted: bool = False
    kind: EvidenceKind = "practice"
    source_ref: str = ""


@dataclass(frozen=True)
class KnowledgeEstimate:
    """Derived state per (learner, objective). Always recomputable from evidence."""

    objective_id: str
    phase: Phase
    model_version: str
    unassisted_successes: int = 0
    failures_while_retaining: int = 0
    has_delayed_success: bool = False
    stability_days: float | None = None
    last_evidence_at: datetime | None = None


@dataclass(frozen=True)
class CurriculumNode:
    """A planning input: what an objective needs, and what it costs to attempt."""

    id: str
    title: str
    prerequisite_ids: tuple[str, ...] = ()
    difficulty: int = 1
    est_minutes: int = 25
    sequence: int = 0
    leaf_kind: Literal["learn", "practice", "assess", "review", "build"] = "learn"
    lesson_id: str | None = None


@dataclass(frozen=True)
class PlanStep:
    """One planned action. A roadmap is an ordered list of these, grouped into weeks."""

    objective_id: str
    kind: Literal["learn", "practice", "assess", "review", "build"]
    est_minutes: int
    order_index: int
    lesson_id: str | None = None
    rationale: str = ""


@dataclass(frozen=True)
class PlanWeekPlan:
    week_number: int
    steps: tuple[PlanStep, ...]

    @property
    def total_minutes(self) -> int:
        return sum(step.est_minutes for step in self.steps)


@dataclass(frozen=True)
class ValidationIssue:
    code: str
    message: str
    severity: Literal["error", "warning"] = "error"
    objective_id: str | None = None


@dataclass(frozen=True)
class ValidationReport:
    errors: tuple[ValidationIssue, ...] = ()
    warnings: tuple[ValidationIssue, ...] = ()
    checked: tuple[str, ...] = field(default_factory=tuple)

    @property
    def ok(self) -> bool:
        return not self.errors

    def as_dict(self) -> dict[str, object]:
        return {
            "ok": self.ok,
            "errors": [issue.__dict__ for issue in self.errors],
            "warnings": [issue.__dict__ for issue in self.warnings],
            "checked": list(self.checked),
        }


@dataclass(frozen=True)
class GradeResult:
    is_correct: bool
    canonical_answer: str
    malformed: bool = False
