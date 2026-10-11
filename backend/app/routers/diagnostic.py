"""Diagnostic assessment: adaptive placement with deterministic grading."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select

from app.deps import CurrentLocale, CurrentUser, Db
from app.i18n import translate
from app.models import DiagnosticAttempt, Goal, Item
from app.schemas import AnswerFeedback, DiagnosticAnswerIn, DiagnosticOut, ItemPublic
from app.serializers import item_public
from app.services import assessment

router = APIRouter(prefix="/api/diagnostic", tags=["diagnostic"])


def localise_placement(placement: dict | None, locale: str) -> dict | None:
    """Re-render the placement's sentences for the reader's locale.

    The placement is computed once and stored on the attempt, together with the code of the rule it
    applied, so the same stored placement can be shown in either language without recomputation.
    """
    if not placement:
        return placement
    rendered = dict(placement)
    rendered["note"] = translate("placement.note", locale)
    rendered["rule"] = translate(placement.get("rule_code", "placement.rule"), locale)
    return rendered


def _attempt_for_user(db: Db, attempt_id: str, user_id: str) -> DiagnosticAttempt:
    attempt = db.get(DiagnosticAttempt, attempt_id)
    if attempt is None or attempt.user_id != user_id:
        # 404 rather than 403 for another learner's attempt: existence is not disclosed.
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found.")
    return attempt


def _state(db: Db, attempt: DiagnosticAttempt, locale: str = "en") -> DiagnosticOut:
    goal = db.get(Goal, attempt.goal_id)
    path_id = goal.path_id if goal else ""
    current = None
    if attempt.status == "in_progress":
        item = assessment.next_diagnostic_item(db, attempt, path_id)
        if item is not None:
            current = ItemPublic(**item_public(item, locale))
    return DiagnosticOut(
        attempt_id=attempt.id,
        goal_id=attempt.goal_id,
        status=attempt.status,
        total_items=assessment.DIAGNOSTIC_MAX_ITEMS,
        answered_items=len(attempt.item_ids or []),
        current_item=current,
        placement=localise_placement(attempt.placement, locale),
    )


@router.post("/goals/{goal_id}", response_model=DiagnosticOut, status_code=status.HTTP_201_CREATED)
def start(goal_id: str, user: CurrentUser, db: Db, locale: CurrentLocale) -> DiagnosticOut:
    goal = db.get(Goal, goal_id)
    if goal is None or goal.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found.")
    attempt = assessment.start_diagnostic(db, user, goal)
    db.commit()
    return _state(db, attempt, locale)


@router.get("/{attempt_id}", response_model=DiagnosticOut)
def state(attempt_id: str, user: CurrentUser, db: Db, locale: CurrentLocale) -> DiagnosticOut:
    return _state(db, _attempt_for_user(db, attempt_id, user.id), locale)


@router.post("/{attempt_id}/answers")
def answer(
    attempt_id: str, payload: DiagnosticAnswerIn, user: CurrentUser, db: Db, locale: CurrentLocale
) -> dict:
    attempt = _attempt_for_user(db, attempt_id, user.id)
    try:
        result = assessment.answer_diagnostic(
            db,
            user,
            attempt,
            item_id=payload.item_id,
            response=payload.response,
            confidence=payload.confidence,
            locale=locale,
        )
    except assessment.AssessmentError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    db.commit()

    goal = db.get(Goal, attempt.goal_id)
    path_id = goal.path_id if goal else ""
    next_item = None
    if attempt.status == "in_progress":
        item: Item | None = assessment.next_diagnostic_item(db, attempt, path_id)
        if item is not None:
            next_item = ItemPublic(**item_public(item, locale))

    return {
        "feedback": AnswerFeedback(**result["feedback"]),
        "completed": result["completed"],
        "placement": localise_placement(result["placement"], locale),
        "next_item": next_item,
        "answered_items": len(attempt.item_ids or []),
        "total_items": assessment.DIAGNOSTIC_MAX_ITEMS,
    }


@router.get("", response_model=list[DiagnosticOut])
def list_attempts(user: CurrentUser, db: Db, locale: CurrentLocale) -> list[DiagnosticOut]:
    rows = db.scalars(
        select(DiagnosticAttempt)
        .where(DiagnosticAttempt.user_id == user.id)
        .order_by(DiagnosticAttempt.started_at.desc())
        .limit(10)
    ).all()
    return [_state(db, row, locale) for row in rows]
