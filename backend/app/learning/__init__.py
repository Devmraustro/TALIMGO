"""Deterministic learning engine.

Pure functions only: no I/O, no clock, no database, no AI. Everything here is testable in isolation
and is the system of record for mastery, grading and planning decisions.
"""

from app.learning.grading import grade
from app.learning.mastery import (
    MODEL_VERSION,
    StaleModelVersionError,
    explain,
    needs_review,
    phase_for,
    replay,
    retrievability,
    summary,
)
from app.learning.roadmap import (
    PlanningError,
    build_weeks,
    generate_plan,
    topological_order,
    validate_plan,
)
from app.learning.selection import NextAction, PlannedItem, choose_next_action
from app.learning.types import (
    CurriculumNode,
    EvidenceRecord,
    GradeResult,
    KnowledgeEstimate,
    PlanStep,
    PlanWeekPlan,
    ValidationIssue,
    ValidationReport,
)

__all__ = [
    "MODEL_VERSION",
    "CurriculumNode",
    "EvidenceRecord",
    "GradeResult",
    "KnowledgeEstimate",
    "NextAction",
    "PlanStep",
    "PlanWeekPlan",
    "PlannedItem",
    "PlanningError",
    "StaleModelVersionError",
    "ValidationIssue",
    "ValidationReport",
    "build_weeks",
    "choose_next_action",
    "explain",
    "generate_plan",
    "grade",
    "needs_review",
    "phase_for",
    "replay",
    "retrievability",
    "summary",
    "topological_order",
    "validate_plan",
]
