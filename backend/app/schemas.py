"""API request/response schemas.

Security-relevant rule: response schemas never carry ``answer_key``. ``ItemPublic`` is the only
shape an item is ever serialised through, and a test asserts the key cannot leak.
"""

from __future__ import annotations

from datetime import date, datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

# Canonical weekday order. A set must never drive ordering: Python randomises string hashing per
# process, so `sorted(..., key=list(some_set).index)` is stable within a run and different between
# runs — a bug that hides in test suites and shows up in production.
WEEKDAYS: tuple[str, ...] = ("mon", "tue", "wed", "thu", "fri", "sat", "sun")

# --------------------------------------------------------------------------------------
# Accounts and sessions
# --------------------------------------------------------------------------------------


class RegisterRequest(BaseModel):
    email: EmailStr
    # Length is enforced by app.security.password_problems so the minimum lives in one place
    # (TALIMGO_MIN_PASSWORD_LENGTH) and the learner gets actionable messages.
    password: str = Field(min_length=1, max_length=256)
    display_name: str = Field(default="", max_length=120)
    accept_terms: bool = Field(description="Explicit consent to the account/learning terms.")
    accept_ai_processing: bool = Field(
        default=False, description="Consent to on-device/on-premise AI processing of study content."
    )

    @field_validator("email")
    @classmethod
    def _normalise_email(cls, value: str) -> str:
        return value.strip().lower()


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=256)

    @field_validator("email")
    @classmethod
    def _normalise_email(cls, value: str) -> str:
        return value.strip().lower()


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    email: str
    display_name: str
    role: str
    created_at: datetime


class ProfileOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    locale: Literal["en", "ar"] = "en"
    weekly_minutes: int
    availability_days: list[str]
    target_date: date | None
    low_bandwidth: bool
    reduced_motion: bool
    onboarding_completed_at: datetime | None


class ProfileUpdate(BaseModel):
    locale: Literal["en", "ar"] | None = None
    weekly_minutes: int | None = Field(default=None, ge=30, le=3000)
    availability_days: list[str] | None = None
    target_date: date | None = None
    low_bandwidth: bool | None = None
    reduced_motion: bool | None = None

    @field_validator("availability_days")
    @classmethod
    def _valid_days(cls, value: list[str] | None) -> list[str] | None:
        if value is None:
            return None
        cleaned = [day.strip().lower()[:3] for day in value if day.strip()]
        unknown = [day for day in cleaned if day not in WEEKDAYS]
        if unknown:
            raise ValueError(f"Unknown weekday codes: {unknown}")
        return sorted(set(cleaned), key=WEEKDAYS.index)


class ConsentIn(BaseModel):
    kind: Literal["ai_processing", "analytics", "marketing"]
    granted: bool


class ConsentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    kind: str
    granted: bool
    recorded_at: datetime


class MeOut(BaseModel):
    user: UserOut
    profile: ProfileOut
    consents: list[ConsentOut]


# --------------------------------------------------------------------------------------
# Curriculum
# --------------------------------------------------------------------------------------


class PathSummary(BaseModel):
    id: str
    # `title`/`summary` are resolved for the requesting locale; the _en/_ar pairs are kept for
    # clients that switch language client-side.
    title: str = ""
    summary: str = ""
    title_en: str
    title_ar: str
    summary_en: str
    summary_ar: str
    objective_count: int
    estimated_hours: float


class ObjectivePublic(BaseModel):
    id: str
    path_id: str
    title: str
    summary: str
    bloom_level: str
    difficulty: int
    prerequisite_ids: list[str]


class LessonPublic(BaseModel):
    id: str
    objective_id: str
    title: str
    body_md: str
    est_minutes: int


class ItemOptionPublic(BaseModel):
    id: str
    text: str


class ItemPublic(BaseModel):
    """Safe projection of an item: prompt and options only. No answer key, no explanation."""

    id: str
    objective_id: str
    kind: str
    prompt: str
    options: list[ItemOptionPublic] | None
    difficulty: int


# --------------------------------------------------------------------------------------
# Goals
# --------------------------------------------------------------------------------------


class GoalCreate(BaseModel):
    path_id: str = Field(min_length=1, max_length=64)
    statement: str = Field(min_length=8, max_length=500)
    motivation: str = Field(default="", max_length=1000)
    target_date: date | None = None
    weekly_minutes: int = Field(default=180, ge=30, le=3000)


class GoalOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    path_id: str
    statement: str
    motivation: str
    target_date: date | None
    weekly_minutes: int
    status: str
    created_at: datetime


# --------------------------------------------------------------------------------------
# Diagnostic
# --------------------------------------------------------------------------------------


class DiagnosticOut(BaseModel):
    attempt_id: str
    goal_id: str
    status: str
    total_items: int
    answered_items: int
    current_item: ItemPublic | None
    placement: dict[str, Any] | None = None


class DiagnosticAnswerIn(BaseModel):
    item_id: str
    response: dict[str, Any]
    confidence: Literal["guessing", "unsure", "confident"] = "unsure"


class AnswerFeedback(BaseModel):
    is_correct: bool
    correct_answer: str
    explanation: str
    objective_id: str
    objective_title: str


# --------------------------------------------------------------------------------------
# Roadmap / plan
# --------------------------------------------------------------------------------------


class PlanItemOut(BaseModel):
    id: str
    order_index: int
    objective_id: str
    objective_title: str
    lesson_id: str | None
    kind: str
    est_minutes: int
    status: str
    rationale: str


class PlanWeekOut(BaseModel):
    week_number: int
    theme: str
    items: list[PlanItemOut]
    total_minutes: int


class PlanOut(BaseModel):
    id: str
    goal_id: str
    version: int
    status: str
    generator: str
    total_estimated_minutes: int
    validation_report: dict[str, Any]
    created_at: datetime
    weeks: list[PlanWeekOut]


class PlanGenerateOut(BaseModel):
    plan: PlanOut
    skipped_objectives: list[dict[str, str]]
    validation: dict[str, Any]


# --------------------------------------------------------------------------------------
# Dashboard / progress
# --------------------------------------------------------------------------------------


class NextActionOut(BaseModel):
    kind: Literal["learn", "practice", "assess", "review", "build", "diagnostic", "idle"]
    title: str
    objective_id: str | None = None
    lesson_id: str | None = None
    plan_item_id: str | None = None
    est_minutes: int = 10
    rationale: str
    evidence_basis: str


class MasteryOut(BaseModel):
    objective_id: str
    title: str
    phase: str  # unseen | acquiring | retaining
    unassisted_successes: int
    retrievability: float | None
    stability_days: float | None
    needs_review: bool
    last_evidence_at: datetime | None
    evidence_count: int


class DashboardOut(BaseModel):
    goal: GoalOut | None
    next_action: NextActionOut
    mastery_summary: dict[str, int]
    recent_evidence: list[dict[str, Any]]
    blockers: list[str]


# --------------------------------------------------------------------------------------
# Practice
# --------------------------------------------------------------------------------------


class PracticeStartIn(BaseModel):
    objective_id: str
    plan_item_id: str | None = None
    goal_id: str | None = None
    size: int = Field(default=5, ge=1, le=20)
    # `review` sessions come from the spaced-review queue; grading and evidence are identical.
    mode: Literal["practice", "review"] = "practice"


class PracticeSessionOut(BaseModel):
    session_id: str
    objective_id: str
    mode: str = "practice"
    status: str
    item: ItemPublic | None
    answered: int
    # `target_items` is the frozen completion target and `total` its display alias; both are
    # persisted on the session so they cannot change between requests.
    target_items: int
    total: int
    feedback: AnswerFeedback | None = None


class PracticeAnswerIn(BaseModel):
    item_id: str
    response: dict[str, Any]
    used_hint: bool = False


class EvidenceOut(BaseModel):
    id: str
    objective_id: str
    outcome: str
    assisted: bool
    kind: str
    occurred_at: datetime


# --------------------------------------------------------------------------------------
# Projects (the BUILD step)
# --------------------------------------------------------------------------------------


class ProjectCriterionOut(BaseModel):
    id: str
    label: str
    required: bool


class ProjectOut(BaseModel):
    id: str
    path_id: str
    objective_id: str
    objective_title: str
    title: str
    brief_md: str
    rubric: list[ProjectCriterionOut]
    min_artifact_chars: int
    min_reflection_chars: int
    est_minutes: int
    my_status: str | None = None
    attempts: int = 0


class ProjectSubmissionIn(BaseModel):
    # Bounds keep a submission well inside the deployment request-size guard while leaving room
    # for a real small program or page source as the artifact.
    artifact_text: str = Field(min_length=1, max_length=60000)
    reflection_text: str = Field(default="", max_length=5000)
    rubric_checks: dict[str, bool] = Field(default_factory=dict)
    goal_id: str | None = None
    plan_item_id: str | None = None


class ProjectSubmissionOut(BaseModel):
    id: str
    project_id: str
    objective_id: str
    goal_id: str | None
    plan_item_id: str | None
    status: str
    met_criteria: list[str]
    missing_criteria: list[str]
    artifact_text: str
    reflection_text: str
    evidence_recorded: bool
    submitted_at: datetime


# --------------------------------------------------------------------------------------
# Spaced review: queue + flashcards
# --------------------------------------------------------------------------------------


class ReviewQueueItemOut(BaseModel):
    objective_id: str
    objective_title: str
    reason: Literal["recall_below_target", "spaced_confirmation_due"]
    retrievability: float | None
    phase: str
    last_evidence_at: datetime | None


class ReviewQueueOut(BaseModel):
    items: list[ReviewQueueItemOut]
    due_count: int


class FlashcardOut(BaseModel):
    item_id: str
    objective_id: str
    objective_title: str
    prompt: str
    answer: str
    explanation: str
    repetitions: int
    due_at: datetime
    is_due: bool


class FlashcardsOut(BaseModel):
    cards: list[FlashcardOut]
    due_count: int


class FlashcardRateIn(BaseModel):
    rating: Literal["again", "good"]


class FlashcardStateOut(BaseModel):
    item_id: str
    repetitions: int
    interval_days: float
    due_at: datetime
    last_rating: str


# --------------------------------------------------------------------------------------
# Tutor
# --------------------------------------------------------------------------------------


class TutorAskIn(BaseModel):
    objective_id: str
    lesson_id: str | None = None
    question: str = Field(min_length=2, max_length=2000)


class TutorReplyOut(BaseModel):
    thread_id: str
    reply: str
    hint_level: int
    citations: list[str]
    model: str
    duration_ms: int
    validation: dict[str, Any]


# --------------------------------------------------------------------------------------
# Account data controls
# --------------------------------------------------------------------------------------


class DataExportOut(BaseModel):
    exported_at: datetime
    account: dict[str, Any]
    notice: str


class DeleteAccountIn(BaseModel):
    password: str = Field(min_length=1)
    confirmation: Literal["DELETE"]
