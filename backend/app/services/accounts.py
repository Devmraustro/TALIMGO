"""Accounts: registration, authentication, sessions, profile, consents, export and deletion."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session as DbSession

from app.config import Settings
from app.deps import session_expiry
from app.models import (
    AiUsage,
    AuditLog,
    ConsentRecord,
    DiagnosticAttempt,
    DiagnosticResponse,
    Evidence,
    Goal,
    LoginAttempt,
    MasteryEstimate,
    Plan,
    PlanItem,
    PlanWeek,
    PracticeResponse,
    PracticeSession,
    Profile,
    Session,
    TutorMessage,
    TutorThread,
    User,
)
from app.security import (
    claim_registration_slot,
    hash_password,
    hash_session_token,
    password_problems,
    verify_password,
)
from app.utils import utcnow


class AccountError(RuntimeError):
    """Base class for account failures that map to 4xx responses."""


class EmailAlreadyRegistered(AccountError):
    pass


class WeakPasswordError(AccountError):
    def __init__(self, problems: list[str]) -> None:
        super().__init__(" ".join(problems))
        self.problems = problems


class InvalidCredentials(AccountError):
    pass


class AccountLocked(AccountError):
    pass


class RegistrationRateLimited(AccountError):
    """This connection has exhausted its registration allowance for the rolling hour."""

    def __init__(self, retry_after: int) -> None:
        self.retry_after = max(1, retry_after)
        super().__init__("Too many accounts have been created from this connection.")


def register_user(
    db: DbSession,
    settings: Settings,
    *,
    ip: str,
    email: str,
    password: str,
    display_name: str,
    accept_terms: bool,
    accept_ai_processing: bool,
    now: datetime | None = None,
) -> User:
    moment = now or utcnow()
    # Serialised per IP by the guard row, so the decision is taken against settled state and
    # concurrent requests cannot overshoot the rolling-hour allowance. The attempt is counted even
    # when the registration itself is refused, so repeated failures cannot probe the endpoint for
    # free. Committed now, never rolled back with the request.
    retry_after = claim_registration_slot(db, ip=ip, settings=settings, now=moment)
    if retry_after is not None:
        raise RegistrationRateLimited(retry_after)
    db.commit()

    if not accept_terms:
        raise AccountError("You must accept the terms to create an account.")
    problems = password_problems(password, settings)
    if problems:
        raise WeakPasswordError(problems)

    existing = db.scalar(select(User).where(User.email == email))
    if existing is not None:
        raise EmailAlreadyRegistered("That email address is already registered.")

    user = User(
        email=email,
        password_hash=hash_password(password),
        display_name=display_name.strip() or email.split("@")[0],
    )
    db.add(user)
    db.flush()

    db.add(Profile(user_id=user.id))
    db.add(ConsentRecord(user_id=user.id, kind="account", granted=True, recorded_at=utcnow()))
    db.add(
        ConsentRecord(
            user_id=user.id, kind="ai_processing", granted=bool(accept_ai_processing), recorded_at=utcnow()
        )
    )
    db.add(AuditLog(actor_user_id=user.id, action="account.register", target=user.id))
    db.commit()
    return user


def create_session(db: DbSession, settings: Settings, user: User) -> str:
    from app.security import new_session_token

    token, token_hash = new_session_token()
    db.add(
        Session(
            user_id=user.id,
            token_hash=token_hash,
            expires_at=session_expiry(settings),
        )
    )
    db.commit()
    return token


def authenticate(
    db: DbSession, settings: Settings, *, email: str, password: str, ip: str, now: datetime | None = None
) -> User:
    from app.security import login_locked, record_login_attempt

    moment = now or utcnow()
    if login_locked(db, email=email, ip=ip, settings=settings, now=moment):
        raise AccountLocked("Too many failed attempts. Try again later.")

    user = db.scalar(select(User).where(User.email == email))
    if user is None or not user.is_active or not verify_password(password, user.password_hash):
        record_login_attempt(db, email=email, ip=ip, succeeded=False)
        db.commit()
        raise InvalidCredentials("Email or password is incorrect.")

    record_login_attempt(db, email=email, ip=ip, succeeded=True)
    db.commit()
    return user


def revoke_session(db: DbSession, token: str) -> None:
    row = db.scalar(select(Session).where(Session.token_hash == hash_session_token(token)))
    if row is not None and row.revoked_at is None:
        row.revoked_at = utcnow()
        db.commit()


def get_profile(db: DbSession, user: User) -> Profile:
    profile = db.get(Profile, user.id)
    if profile is None:
        profile = Profile(user_id=user.id)
        db.add(profile)
        db.commit()
    return profile


def list_consents(db: DbSession, user: User) -> list[ConsentRecord]:
    return list(
        db.scalars(select(ConsentRecord).where(ConsentRecord.user_id == user.id).order_by(ConsentRecord.kind))
    )


def set_consent(db: DbSession, user: User, kind: str, granted: bool) -> ConsentRecord:
    row = db.scalar(select(ConsentRecord).where(ConsentRecord.user_id == user.id, ConsentRecord.kind == kind))
    if row is None:
        row = ConsentRecord(user_id=user.id, kind=kind, granted=granted, recorded_at=utcnow())
        db.add(row)
    else:
        row.granted = granted
        row.recorded_at = utcnow()
    db.add(AuditLog(actor_user_id=user.id, action=f"consent.{kind}", detail={"granted": granted}))
    db.commit()
    return row


def export_account(db: DbSession, user: User) -> dict:
    """Machine-readable copy of everything TALIMGO holds about this learner."""
    profile = get_profile(db, user)
    goals = list(db.scalars(select(Goal).where(Goal.user_id == user.id)))
    evidence = list(db.scalars(select(Evidence).where(Evidence.user_id == user.id)))
    estimates = list(db.scalars(select(MasteryEstimate).where(MasteryEstimate.user_id == user.id)))
    plans = list(db.scalars(select(Plan).where(Plan.user_id == user.id)))
    threads = list(db.scalars(select(TutorThread).where(TutorThread.user_id == user.id)))
    messages = (
        list(
            db.scalars(
                select(TutorMessage)
                .where(TutorMessage.thread_id.in_([thread.id for thread in threads]))
                .order_by(TutorMessage.created_at)
            )
        )
        if threads
        else []
    )
    sessions = list(db.scalars(select(Session).where(Session.user_id == user.id)))
    diagnostic_attempts = list(
        db.scalars(select(DiagnosticAttempt).where(DiagnosticAttempt.user_id == user.id))
    )
    diagnostic_responses = (
        list(
            db.scalars(
                select(DiagnosticResponse)
                .where(DiagnosticResponse.attempt_id.in_([row.id for row in diagnostic_attempts]))
                .order_by(DiagnosticResponse.answered_at)
            )
        )
        if diagnostic_attempts
        else []
    )
    practice_sessions = list(db.scalars(select(PracticeSession).where(PracticeSession.user_id == user.id)))
    practice_responses = (
        list(
            db.scalars(
                select(PracticeResponse)
                .where(PracticeResponse.session_id.in_([row.id for row in practice_sessions]))
                .order_by(PracticeResponse.answered_at)
            )
        )
        if practice_sessions
        else []
    )
    plan_weeks = (
        list(db.scalars(select(PlanWeek).where(PlanWeek.plan_id.in_([plan.id for plan in plans]))))
        if plans
        else []
    )
    plan_items = (
        list(db.scalars(select(PlanItem).where(PlanItem.plan_id.in_([plan.id for plan in plans]))))
        if plans
        else []
    )
    ai_usage = list(db.scalars(select(AiUsage).where(AiUsage.user_id == user.id)))

    return {
        "account": {
            "id": user.id,
            "email": user.email,
            "display_name": user.display_name,
            "role": user.role,
            "created_at": user.created_at.isoformat(),
        },
        "profile": {
            "locale": profile.locale,
            "weekly_minutes": profile.weekly_minutes,
            "availability_days": profile.availability_days,
            "target_date": profile.target_date.isoformat() if profile.target_date else None,
            "low_bandwidth": profile.low_bandwidth,
            "reduced_motion": profile.reduced_motion,
        },
        "consents": [
            {"kind": row.kind, "granted": row.granted, "recorded_at": row.recorded_at.isoformat()}
            for row in list_consents(db, user)
        ],
        "goals": [
            {
                "id": goal.id,
                "path_id": goal.path_id,
                "statement": goal.statement,
                "status": goal.status,
                "created_at": goal.created_at.isoformat(),
            }
            for goal in goals
        ],
        "evidence": [
            {
                "id": row.id,
                "objective_id": row.objective_id,
                "outcome": row.outcome,
                "assisted": row.assisted,
                "kind": row.kind,
                "occurred_at": row.occurred_at.isoformat(),
            }
            for row in evidence
        ],
        "mastery_estimates": [
            {
                "objective_id": row.objective_id,
                "model_version": row.model_version,
                "phase": row.phase,
                "unassisted_successes": row.unassisted_successes,
                "stability_days": row.stability_days,
                "last_evidence_at": row.last_evidence_at.isoformat() if row.last_evidence_at else None,
            }
            for row in estimates
        ],
        "plans": [
            {"id": plan.id, "goal_id": plan.goal_id, "version": plan.version, "status": plan.status}
            for plan in plans
        ],
        "plan_weeks": [
            {
                "id": week.id,
                "plan_id": week.plan_id,
                "week_number": week.week_number,
                "theme_en": week.theme_en,
                "theme_ar": week.theme_ar,
            }
            for week in plan_weeks
        ],
        "plan_items": [
            {
                "id": item.id,
                "plan_id": item.plan_id,
                "week_id": item.week_id,
                "order_index": item.order_index,
                "objective_id": item.objective_id,
                "lesson_id": item.lesson_id,
                "kind": item.kind,
                "est_minutes": item.est_minutes,
                "status": item.status,
                "rationale_en": item.rationale_en,
                "rationale_ar": item.rationale_ar,
            }
            for item in plan_items
        ],
        "diagnostic_attempts": [
            {
                "id": row.id,
                "goal_id": row.goal_id,
                "status": row.status,
                "item_ids": row.item_ids,
                "cursor": row.cursor,
                "placement": row.placement,
                "started_at": row.started_at.isoformat(),
                "completed_at": row.completed_at.isoformat() if row.completed_at else None,
            }
            for row in diagnostic_attempts
        ],
        "diagnostic_responses": [
            {
                "attempt_id": row.attempt_id,
                "item_id": row.item_id,
                "objective_id": row.objective_id,
                "response": row.response,
                "is_correct": row.is_correct,
                "difficulty": row.difficulty,
                "answered_at": row.answered_at.isoformat(),
            }
            for row in diagnostic_responses
        ],
        "practice_sessions": [
            {
                "id": row.id,
                "goal_id": row.goal_id,
                "plan_item_id": row.plan_item_id,
                "objective_id": row.objective_id,
                "status": row.status,
                "target_items": row.target_items,
                "item_ids": row.item_ids,
                "started_at": row.started_at.isoformat(),
                "completed_at": row.completed_at.isoformat() if row.completed_at else None,
                "abandoned_at": row.abandoned_at.isoformat() if row.abandoned_at else None,
            }
            for row in practice_sessions
        ],
        "practice_responses": [
            {
                "session_id": row.session_id,
                "item_id": row.item_id,
                "objective_id": row.objective_id,
                "response": row.response,
                "is_correct": row.is_correct,
                "assisted": row.assisted,
                "answered_at": row.answered_at.isoformat(),
            }
            for row in practice_responses
        ],
        "ai_usage": [{"day": row.day, "count": row.count} for row in ai_usage],
        "tutor_messages": [
            {
                "thread_id": message.thread_id,
                "role": message.role,
                "content": message.content,
                "created_at": message.created_at.isoformat(),
            }
            for message in messages
        ],
        "sessions": [
            {"id": row.id, "created_at": row.created_at.isoformat(), "expires_at": row.expires_at.isoformat()}
            for row in sessions
        ],
    }


def delete_account(db: DbSession, user: User, *, password: str) -> None:
    """Delete the account and the learner data it owns.

    Order matters: children are removed before parents so no foreign key is left dangling on
    databases without cascades. Audit rows are kept (they contain no learner content) but are
    anonymised, which is documented behaviour rather than a silent exception. Login-attempt rows
    are keyed by the learner's email address, so they are deleted with the account rather than
    left behind until routine pruning; only the address identifies the learner in them.
    """
    if not verify_password(password, user.password_hash):
        raise InvalidCredentials("Password is incorrect; the account was not deleted.")

    user_id = user.id
    email = user.email

    # NB: selecting a single column yields the ids themselves; selecting `.id` again raised
    # AttributeError, so deleting an account that had ever used the tutor failed with a 500.
    thread_ids = list(db.scalars(select(TutorThread.id).where(TutorThread.user_id == user_id)))
    if thread_ids:
        db.query(TutorMessage).filter(TutorMessage.thread_id.in_(thread_ids)).delete(
            synchronize_session=False
        )
        db.query(TutorThread).filter(TutorThread.id.in_(thread_ids)).delete(synchronize_session=False)

    practice_ids = list(db.scalars(select(PracticeSession.id).where(PracticeSession.user_id == user_id)))
    if practice_ids:
        db.query(PracticeResponse).filter(PracticeResponse.session_id.in_(practice_ids)).delete(
            synchronize_session=False
        )
        db.query(PracticeSession).filter(PracticeSession.id.in_(practice_ids)).delete(
            synchronize_session=False
        )

    attempt_ids = list(db.scalars(select(DiagnosticAttempt.id).where(DiagnosticAttempt.user_id == user_id)))
    if attempt_ids:
        db.query(DiagnosticResponse).filter(DiagnosticResponse.attempt_id.in_(attempt_ids)).delete(
            synchronize_session=False
        )
        db.query(DiagnosticAttempt).filter(DiagnosticAttempt.id.in_(attempt_ids)).delete(
            synchronize_session=False
        )

    db.query(Evidence).filter(Evidence.user_id == user_id).delete(synchronize_session=False)
    db.query(MasteryEstimate).filter(MasteryEstimate.user_id == user_id).delete(synchronize_session=False)

    plan_ids = list(db.scalars(select(Plan.id).where(Plan.user_id == user_id)))
    if plan_ids:
        db.query(PlanItem).filter(PlanItem.plan_id.in_(plan_ids)).delete(synchronize_session=False)
        db.query(PlanWeek).filter(PlanWeek.plan_id.in_(plan_ids)).delete(synchronize_session=False)
        db.query(Plan).filter(Plan.id.in_(plan_ids)).delete(synchronize_session=False)

    db.query(Goal).filter(Goal.user_id == user_id).delete(synchronize_session=False)
    db.query(AiUsage).filter(AiUsage.user_id == user_id).delete(synchronize_session=False)
    db.query(Profile).filter(Profile.user_id == user_id).delete(synchronize_session=False)
    db.query(ConsentRecord).filter(ConsentRecord.user_id == user_id).delete(synchronize_session=False)
    db.query(Session).filter(Session.user_id == user_id).delete(synchronize_session=False)
    db.query(AuditLog).filter(AuditLog.actor_user_id == user_id).update(
        {"actor_user_id": None, "target": "deleted-account"}, synchronize_session=False
    )
    db.query(LoginAttempt).filter(LoginAttempt.email == email).delete(synchronize_session=False)
    db.query(User).filter(User.id == user_id).delete(synchronize_session=False)
    db.commit()
