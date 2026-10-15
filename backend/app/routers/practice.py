"""Practice sessions and progress read-outs."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select

from app.deps import CurrentLocale, CurrentUser, Db
from app.learning.mastery import RETRIEVABILITY_TARGET, retrievability
from app.models import Evidence, Objective, PracticeResponse, PracticeSession
from app.schemas import (
    AnswerFeedback,
    ItemPublic,
    MasteryOut,
    PracticeAnswerIn,
    PracticeSessionOut,
    PracticeStartIn,
)
from app.serializers import item_public
from app.services import assessment
from app.services.progress import load_estimates, objective_title, recompute_mastery
from app.utils import utcnow

router = APIRouter(prefix="/api/practice", tags=["practice"])

DEFAULT_SESSION_SIZE = 5


def _session_for_user(db: Db, session_id: str, user_id: str) -> PracticeSession:
    session = db.get(PracticeSession, session_id)
    if session is None or session.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found.")
    return session


def _answered_count(db: Db, session: PracticeSession) -> int:
    return len(db.scalars(select(PracticeResponse.id).where(PracticeResponse.session_id == session.id)).all())


def _state(
    db: Db, session: PracticeSession, *, feedback: dict | None = None, locale: str = "en"
) -> PracticeSessionOut:
    answered, target = assessment.practice_progress(db, session)
    item = assessment.next_practice_item(db, session)
    return PracticeSessionOut(
        session_id=session.id,
        objective_id=session.objective_id,
        status=session.status,
        item=ItemPublic(**item_public(item, locale)) if item is not None else None,
        answered=answered,
        target_items=target,
        total=target,
        feedback=AnswerFeedback(**feedback) if feedback else None,
    )


@router.post("/sessions", response_model=PracticeSessionOut, status_code=status.HTTP_201_CREATED)
def start_session(
    payload: PracticeStartIn, user: CurrentUser, db: Db, locale: CurrentLocale
) -> PracticeSessionOut:
    try:
        session = assessment.start_practice(
            db,
            user,
            objective_id=payload.objective_id,
            size=payload.size,
            goal_id=payload.goal_id,
            plan_item_id=payload.plan_item_id,
        )
    except assessment.AssessmentConflict as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    except assessment.AssessmentError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    db.commit()
    return _state(db, session, locale=locale)


@router.get("/sessions/{session_id}", response_model=PracticeSessionOut)
def get_session(session_id: str, user: CurrentUser, db: Db, locale: CurrentLocale) -> PracticeSessionOut:
    return _state(db, _session_for_user(db, session_id, user.id), locale=locale)


@router.post("/sessions/{session_id}/answers", response_model=PracticeSessionOut)
def answer(
    session_id: str, payload: PracticeAnswerIn, user: CurrentUser, db: Db, locale: CurrentLocale
) -> PracticeSessionOut:
    session = _session_for_user(db, session_id, user.id)
    try:
        result = assessment.answer_practice(
            db,
            user,
            session,
            item_id=payload.item_id,
            response=payload.response,
            used_hint=payload.used_hint,
            locale=locale,
        )
    except assessment.AssessmentConflict as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    except assessment.AssessmentError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    db.commit()
    return _state(db, session, feedback=result["feedback"], locale=locale)


@router.post("/sessions/{session_id}/complete", response_model=PracticeSessionOut)
def complete_session(session_id: str, user: CurrentUser, db: Db, locale: CurrentLocale) -> PracticeSessionOut:
    """Complete a session that has answered every planned question.

    Completion is what marks the linked roadmap item done, so it is validated server-side: an
    untouched or partially answered session is refused (409) and the roadmap item stays pending.
    """
    session = _session_for_user(db, session_id, user.id)
    try:
        assessment.complete_practice(db, session)
    except assessment.AssessmentConflict as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    if session.plan_item_id:
        # Ownership is verified at the point of the write: a session row pointing at another
        # learner's plan item must never tick it off. Nothing is repaired silently.
        plan_item = assessment.plan_item_for_user(db, session.plan_item_id, user.id)
        if plan_item is not None and plan_item.status != "completed":
            plan_item.status = "completed"
            # Recorded so schedule adherence can say whether work was finished on the day it was
            # planned for (app/learning/schedule.adherence).
            plan_item.completed_at = utcnow()
    db.commit()
    return _state(db, session, locale=locale)


@router.post("/sessions/{session_id}/abandon", response_model=PracticeSessionOut)
def abandon_session(session_id: str, user: CurrentUser, db: Db, locale: CurrentLocale) -> PracticeSessionOut:
    """Leave a session without losing recorded answers.

    Distinct from completion: the roadmap item stays pending and the session can never be completed
    or answered again. This is what the interface's "leave" action calls.
    """
    session = _session_for_user(db, session_id, user.id)
    try:
        assessment.abandon_practice(db, session)
    except assessment.AssessmentConflict as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    db.commit()
    return _state(db, session, locale=locale)


@router.get("/progress/mastery", response_model=list[MasteryOut])
def mastery(user: CurrentUser, db: Db, locale: CurrentLocale) -> list[MasteryOut]:
    now = utcnow()
    estimates = load_estimates(db, user.id)
    objectives = {row.id: row for row in db.scalars(select(Objective)).all()}
    evidence_counts: dict[str, int] = {}
    for objective_id in db.scalars(select(Evidence.objective_id).where(Evidence.user_id == user.id)).all():
        evidence_counts[objective_id] = evidence_counts.get(objective_id, 0) + 1

    ordered = sorted(
        estimates.items(),
        key=lambda pair: (objectives[pair[0]].sequence if pair[0] in objectives else 0, pair[0]),
    )
    output: list[MasteryOut] = []
    for objective_id, estimate in ordered:
        objective = objectives.get(objective_id)
        value = retrievability(estimate, now) if estimate.phase == "retaining" else None
        output.append(
            MasteryOut(
                objective_id=objective_id,
                title=objective_title(objective, locale, objective_id),
                phase=estimate.phase,
                unassisted_successes=estimate.unassisted_successes,
                retrievability=value,
                stability_days=estimate.stability_days,
                needs_review=bool(value is not None and value < RETRIEVABILITY_TARGET),
                last_evidence_at=estimate.last_evidence_at,
                evidence_count=evidence_counts.get(objective_id, 0),
            )
        )
    return output


@router.get("/progress/evidence")
def evidence_log(user: CurrentUser, db: Db, locale: CurrentLocale, limit: int = 50) -> list[dict]:
    rows = db.scalars(
        select(Evidence)
        .where(Evidence.user_id == user.id)
        .order_by(Evidence.occurred_at.desc())
        .limit(min(max(limit, 1), 200))
    ).all()
    objectives = {row.id: row for row in db.scalars(select(Objective)).all()}
    return [
        {
            "id": row.id,
            "objective_id": row.objective_id,
            "objective_title": objective_title(objectives.get(row.objective_id), locale, row.objective_id),
            "outcome": row.outcome,
            "assisted": row.assisted,
            "kind": row.kind,
            "occurred_at": row.occurred_at,
        }
        for row in rows
    ]


@router.post("/progress/recompute", response_model=list[MasteryOut])
def recompute(user: CurrentUser, db: Db, locale: CurrentLocale) -> list[MasteryOut]:
    """Rebuild the mastery projection from evidence. Deterministic and safe to call anytime."""
    recompute_mastery(db, user.id)
    db.commit()
    return mastery(user, db, locale)
