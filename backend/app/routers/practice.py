"""Practice sessions and progress read-outs."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select

from app.deps import CurrentUser, Db
from app.learning.mastery import RETRIEVABILITY_TARGET, retrievability
from app.models import Evidence, Objective, PlanItem, PracticeResponse, PracticeSession
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
from app.services.progress import load_estimates, recompute_mastery
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
    db: Db,
    session: PracticeSession,
    *,
    size: int = DEFAULT_SESSION_SIZE,
    feedback: dict | None = None,
) -> PracticeSessionOut:
    answered = _answered_count(db, session)
    remaining = assessment.practice_items(db, session, size=size) if session.status == "in_progress" else []
    item = remaining[0] if remaining else None
    return PracticeSessionOut(
        session_id=session.id,
        objective_id=session.objective_id,
        item=ItemPublic(**item_public(item)) if item is not None else None,
        answered=answered,
        total=answered + len(remaining),
        feedback=AnswerFeedback(**feedback) if feedback else None,
    )


@router.post("/sessions", response_model=PracticeSessionOut, status_code=status.HTTP_201_CREATED)
def start_session(payload: PracticeStartIn, user: CurrentUser, db: Db) -> PracticeSessionOut:
    try:
        session = assessment.start_practice(
            db,
            user,
            objective_id=payload.objective_id,
            goal_id=payload.goal_id,
            plan_item_id=payload.plan_item_id,
        )
    except assessment.AssessmentError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    db.commit()
    return _state(db, session, size=payload.size)


@router.get("/sessions/{session_id}", response_model=PracticeSessionOut)
def get_session(session_id: str, user: CurrentUser, db: Db) -> PracticeSessionOut:
    return _state(db, _session_for_user(db, session_id, user.id))


@router.post("/sessions/{session_id}/answers", response_model=PracticeSessionOut)
def answer(session_id: str, payload: PracticeAnswerIn, user: CurrentUser, db: Db) -> PracticeSessionOut:
    session = _session_for_user(db, session_id, user.id)
    try:
        result = assessment.answer_practice(
            db,
            user,
            session,
            item_id=payload.item_id,
            response=payload.response,
            used_hint=payload.used_hint,
        )
    except assessment.AssessmentError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    db.commit()
    return _state(db, session, feedback=result["feedback"])


@router.post("/sessions/{session_id}/complete", response_model=PracticeSessionOut)
def complete_session(session_id: str, user: CurrentUser, db: Db) -> PracticeSessionOut:
    session = _session_for_user(db, session_id, user.id)
    if session.status == "in_progress":
        session.status = "completed"
        session.completed_at = utcnow()
        if session.plan_item_id:
            plan_item = db.get(PlanItem, session.plan_item_id)
            if plan_item is not None and plan_item.status != "completed":
                plan_item.status = "completed"
        db.commit()
    return _state(db, session)


@router.get("/progress/mastery", response_model=list[MasteryOut])
def mastery(user: CurrentUser, db: Db) -> list[MasteryOut]:
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
                title=objective.title_en if objective else objective_id,
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
def evidence_log(user: CurrentUser, db: Db, limit: int = 50) -> list[dict]:
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
            "objective_title": objectives[row.objective_id].title_en
            if row.objective_id in objectives
            else row.objective_id,
            "outcome": row.outcome,
            "assisted": row.assisted,
            "kind": row.kind,
            "occurred_at": row.occurred_at,
        }
        for row in rows
    ]


@router.post("/progress/recompute", response_model=list[MasteryOut])
def recompute(user: CurrentUser, db: Db) -> list[MasteryOut]:
    """Rebuild the mastery projection from evidence. Deterministic and safe to call anytime."""
    recompute_mastery(db, user.id)
    db.commit()
    return mastery(user, db)
