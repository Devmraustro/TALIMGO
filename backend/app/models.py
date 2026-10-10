"""SQLAlchemy models — the persistence layer.

Design notes:
  * Learner evidence (``evidence``) is the source of truth for mastery; ``mastery_estimates``
    is a derived cache that is always recomputable by replaying evidence.
  * AI output never appears in ``mastery_estimates`` or ``evidence``; the tutor is not the
    system of record (AGENTS.md section 5).
  * Answer keys live only in ``items.answer_key`` and are never serialised to clients.
"""

from __future__ import annotations

from datetime import date, datetime
from typing import Any

from sqlalchemy import (
    JSON,
    Boolean,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base
from app.utils import new_id, utcnow


def _now() -> datetime:
    return utcnow()


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=lambda: new_id("usr"))
    email: Mapped[str] = mapped_column(String(320), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    display_name: Mapped[str] = mapped_column(String(120), default="")
    role: Mapped[str] = mapped_column(String(20), default="learner")  # learner | admin
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now, onupdate=_now)


class Session(Base):
    __tablename__ = "sessions"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=lambda: new_id("ses"))
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    token_hash: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class LoginAttempt(Base):
    __tablename__ = "login_attempts"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=lambda: new_id("lga"))
    email: Mapped[str] = mapped_column(String(320), index=True)
    ip: Mapped[str] = mapped_column(String(64), default="")
    succeeded: Mapped[bool] = mapped_column(Boolean, default=False)
    attempted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now, index=True)


class Profile(Base):
    __tablename__ = "profiles"

    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    locale: Mapped[str] = mapped_column(String(8), default="en")  # en | ar
    weekly_minutes: Mapped[int] = mapped_column(Integer, default=180)
    availability_days: Mapped[list[str]] = mapped_column(JSON, default=list)
    target_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    low_bandwidth: Mapped[bool] = mapped_column(Boolean, default=False)
    reduced_motion: Mapped[bool] = mapped_column(Boolean, default=False)
    onboarding_completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now, onupdate=_now)


class ConsentRecord(Base):
    __tablename__ = "consent_records"
    __table_args__ = (UniqueConstraint("user_id", "kind", name="uq_consent_user_kind"),)

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=lambda: new_id("cns"))
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    kind: Mapped[str] = mapped_column(String(40))  # account | ai_processing | analytics | marketing
    granted: Mapped[bool] = mapped_column(Boolean, default=False)
    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)


class Goal(Base):
    __tablename__ = "goals"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=lambda: new_id("gol"))
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    path_id: Mapped[str] = mapped_column(String(64))
    statement: Mapped[str] = mapped_column(Text)
    motivation: Mapped[str] = mapped_column(Text, default="")
    target_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    weekly_minutes: Mapped[int] = mapped_column(Integer, default=180)
    status: Mapped[str] = mapped_column(String(20), default="active")  # active | paused | completed
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now, onupdate=_now)


class Objective(Base):
    """A stable, assessable learning target. Content references objectives; it never owns them."""

    __tablename__ = "objectives"

    id: Mapped[str] = mapped_column(String(80), primary_key=True)
    path_id: Mapped[str] = mapped_column(String(64), index=True)
    title_en: Mapped[str] = mapped_column(String(200))
    title_ar: Mapped[str] = mapped_column(String(200), default="")
    summary_en: Mapped[str] = mapped_column(Text, default="")
    summary_ar: Mapped[str] = mapped_column(Text, default="")
    kind: Mapped[str] = mapped_column(String(20), default="concept")  # concept | skill | project
    bloom_level: Mapped[str] = mapped_column(String(20), default="understand")
    difficulty: Mapped[int] = mapped_column(Integer, default=1)  # 1..5
    prerequisite_ids: Mapped[list[str]] = mapped_column(JSON, default=list)
    sequence: Mapped[int] = mapped_column(Integer, default=0)


class Item(Base):
    """An assessment/practice item. ``answer_key`` is never exposed to clients."""

    __tablename__ = "items"

    id: Mapped[str] = mapped_column(String(80), primary_key=True)
    objective_id: Mapped[str] = mapped_column(ForeignKey("objectives.id"), index=True)
    kind: Mapped[str] = mapped_column(String(30))  # mcq_single | short_answer
    prompt_en: Mapped[str] = mapped_column(Text)
    prompt_ar: Mapped[str] = mapped_column(Text, default="")
    options: Mapped[list[dict[str, Any]] | None] = mapped_column(JSON, nullable=True)
    answer_key: Mapped[dict[str, Any]] = mapped_column(JSON)
    explanation_en: Mapped[str] = mapped_column(Text, default="")
    explanation_ar: Mapped[str] = mapped_column(Text, default="")
    difficulty: Mapped[int] = mapped_column(Integer, default=1)
    is_diagnostic: Mapped[bool] = mapped_column(Boolean, default=True)


class Lesson(Base):
    __tablename__ = "lessons"

    id: Mapped[str] = mapped_column(String(80), primary_key=True)
    path_id: Mapped[str] = mapped_column(String(64), index=True)
    objective_id: Mapped[str] = mapped_column(ForeignKey("objectives.id"), index=True)
    title_en: Mapped[str] = mapped_column(String(200))
    title_ar: Mapped[str] = mapped_column(String(200), default="")
    body_md_en: Mapped[str] = mapped_column(Text, default="")
    body_md_ar: Mapped[str] = mapped_column(Text, default="")
    est_minutes: Mapped[int] = mapped_column(Integer, default=15)
    sequence: Mapped[int] = mapped_column(Integer, default=0)


class DiagnosticAttempt(Base):
    __tablename__ = "diagnostic_attempts"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=lambda: new_id("dia"))
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    goal_id: Mapped[str] = mapped_column(ForeignKey("goals.id", ondelete="CASCADE"), index=True)
    status: Mapped[str] = mapped_column(String(20), default="in_progress")  # in_progress | completed
    item_ids: Mapped[list[str]] = mapped_column(JSON, default=list)
    cursor: Mapped[int] = mapped_column(Integer, default=0)
    placement: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class DiagnosticResponse(Base):
    __tablename__ = "diagnostic_responses"
    __table_args__ = (UniqueConstraint("attempt_id", "item_id", name="uq_diag_response_attempt_item"),)

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=lambda: new_id("dir"))
    attempt_id: Mapped[str] = mapped_column(
        ForeignKey("diagnostic_attempts.id", ondelete="CASCADE"), index=True
    )
    item_id: Mapped[str] = mapped_column(String(80))
    objective_id: Mapped[str] = mapped_column(String(80), index=True)
    response: Mapped[dict[str, Any]] = mapped_column(JSON)
    is_correct: Mapped[bool] = mapped_column(Boolean)
    difficulty: Mapped[int] = mapped_column(Integer, default=1)
    answered_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)


class Evidence(Base):
    """Immutable record of what a learner actually did. Mastery is recomputed from this."""

    __tablename__ = "learner_evidence"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=lambda: new_id("evd"))
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    objective_id: Mapped[str] = mapped_column(ForeignKey("objectives.id"), index=True)
    outcome: Mapped[str] = mapped_column(String(10))  # success | failure
    assisted: Mapped[bool] = mapped_column(Boolean, default=False)
    kind: Mapped[str] = mapped_column(String(20))  # diagnostic | practice | assessment | project
    source_ref: Mapped[str] = mapped_column(String(120), default="")
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now, index=True)
    meta: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)


class MasteryEstimate(Base):
    """Derived cache. Never the source of truth; always rebuildable from evidence."""

    __tablename__ = "mastery_estimates"
    __table_args__ = (UniqueConstraint("user_id", "objective_id", name="uq_mastery_user_objective"),)

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=lambda: new_id("mst"))
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    objective_id: Mapped[str] = mapped_column(ForeignKey("objectives.id"), index=True)
    model_version: Mapped[str] = mapped_column(String(40))
    phase: Mapped[str] = mapped_column(String(20))  # acquiring | retaining
    unassisted_successes: Mapped[int] = mapped_column(Integer, default=0)
    failures_while_retaining: Mapped[int] = mapped_column(Integer, default=0)
    has_delayed_success: Mapped[bool] = mapped_column(Boolean, default=False)
    stability_days: Mapped[float | None] = mapped_column(Float, nullable=True)
    last_evidence_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now, onupdate=_now)


class Plan(Base):
    __tablename__ = "plans"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=lambda: new_id("pln"))
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    goal_id: Mapped[str] = mapped_column(ForeignKey("goals.id", ondelete="CASCADE"), index=True)
    version: Mapped[int] = mapped_column(Integer, default=1)
    status: Mapped[str] = mapped_column(String(20), default="active")  # active | superseded
    generator: Mapped[str] = mapped_column(String(40), default="deterministic-v1")
    total_estimated_minutes: Mapped[int] = mapped_column(Integer, default=0)
    validation_report: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)


class PlanWeek(Base):
    __tablename__ = "plan_weeks"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=lambda: new_id("pwk"))
    plan_id: Mapped[str] = mapped_column(ForeignKey("plans.id", ondelete="CASCADE"), index=True)
    week_number: Mapped[int] = mapped_column(Integer)
    theme_en: Mapped[str] = mapped_column(String(200), default="")
    theme_ar: Mapped[str] = mapped_column(String(200), default="")


class PlanItem(Base):
    __tablename__ = "plan_items"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=lambda: new_id("pit"))
    plan_id: Mapped[str] = mapped_column(ForeignKey("plans.id", ondelete="CASCADE"), index=True)
    week_id: Mapped[str] = mapped_column(ForeignKey("plan_weeks.id", ondelete="CASCADE"), index=True)
    order_index: Mapped[int] = mapped_column(Integer, default=0)
    objective_id: Mapped[str] = mapped_column(ForeignKey("objectives.id"), index=True)
    lesson_id: Mapped[str | None] = mapped_column(String(80), nullable=True)
    kind: Mapped[str] = mapped_column(String(20))  # learn | practice | assess | review | build
    est_minutes: Mapped[int] = mapped_column(Integer, default=20)
    status: Mapped[str] = mapped_column(String(20), default="pending")
    rationale_en: Mapped[str] = mapped_column(Text, default="")
    rationale_ar: Mapped[str] = mapped_column(Text, default="")


class PracticeSession(Base):
    __tablename__ = "practice_sessions"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=lambda: new_id("prs"))
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    goal_id: Mapped[str | None] = mapped_column(ForeignKey("goals.id", ondelete="SET NULL"), nullable=True)
    plan_item_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    objective_id: Mapped[str] = mapped_column(ForeignKey("objectives.id"), index=True)
    status: Mapped[str] = mapped_column(String(20), default="in_progress")  # in_progress|completed|abandoned
    # The session's completion target, frozen when the session is created: `target_items` is what was
    # requested and `item_ids` is the resolved plan (the requested size clamped to the item pool).
    # Both are persisted so every later request sees the same length and the same next question.
    target_items: Mapped[int] = mapped_column(Integer, default=0)
    item_ids: Mapped[list[str]] = mapped_column(JSON, default=list)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    abandoned_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class PracticeResponse(Base):
    __tablename__ = "practice_responses"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=lambda: new_id("prr"))
    session_id: Mapped[str] = mapped_column(
        ForeignKey("practice_sessions.id", ondelete="CASCADE"), index=True
    )
    item_id: Mapped[str] = mapped_column(String(80))
    objective_id: Mapped[str] = mapped_column(String(80), index=True)
    response: Mapped[dict[str, Any]] = mapped_column(JSON)
    is_correct: Mapped[bool] = mapped_column(Boolean)
    assisted: Mapped[bool] = mapped_column(Boolean, default=False)
    answered_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)


class TutorThread(Base):
    __tablename__ = "tutor_threads"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=lambda: new_id("thr"))
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    objective_id: Mapped[str | None] = mapped_column(String(80), nullable=True)
    lesson_id: Mapped[str | None] = mapped_column(String(80), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)


class TutorMessage(Base):
    __tablename__ = "tutor_messages"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=lambda: new_id("tmsg"))
    thread_id: Mapped[str] = mapped_column(ForeignKey("tutor_threads.id", ondelete="CASCADE"), index=True)
    role: Mapped[str] = mapped_column(String(12))  # learner | tutor
    content: Mapped[str] = mapped_column(Text)
    validation: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)


class AiUsage(Base):
    """Per-learner daily counter so local model capacity cannot be exhausted by one account."""

    __tablename__ = "ai_usage"
    __table_args__ = (UniqueConstraint("user_id", "day", name="uq_ai_usage_user_day"),)

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=lambda: new_id("aiu"))
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    day: Mapped[str] = mapped_column(String(10))  # YYYY-MM-DD (UTC)
    count: Mapped[int] = mapped_column(Integer, default=0)


class AuditLog(Base):
    __tablename__ = "audit_log"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=lambda: new_id("aud"))
    actor_user_id: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    action: Mapped[str] = mapped_column(String(80))
    target: Mapped[str] = mapped_column(String(120), default="")
    detail: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now, index=True)


__all__ = [
    "AiUsage",
    "AuditLog",
    "ConsentRecord",
    "DiagnosticAttempt",
    "DiagnosticResponse",
    "Evidence",
    "Goal",
    "Item",
    "Lesson",
    "LoginAttempt",
    "MasteryEstimate",
    "Objective",
    "Plan",
    "PlanItem",
    "PlanWeek",
    "PracticeResponse",
    "PracticeSession",
    "Profile",
    "Session",
    "TutorMessage",
    "TutorThread",
    "User",
]
