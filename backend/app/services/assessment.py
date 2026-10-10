"""Diagnostic placement and practice sessions — all grading deterministic.

Item selection here is deliberate and simple: difficulty follows the learner's running performance
inside the diagnostic and the mastery phase during practice, and the tie-breaks are stable, so the
same state always produces the same next item. Adaptive bandit-style selection is recorded as FUTURE
in the implementation plan because it needs calibration data we do not have.
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session as DbSession

from app.curriculum.registry import localised
from app.learning.grading import grade
from app.learning.types import GradeResult
from app.models import (
    DiagnosticAttempt,
    DiagnosticResponse,
    Goal,
    Item,
    Objective,
    PracticeResponse,
    PracticeSession,
    User,
)
from app.services.progress import load_estimates, recompute_mastery, record_evidence
from app.utils import utcnow

DIAGNOSTIC_MAX_ITEMS = 12
DIAGNOSTIC_START_DIFFICULTY = 2


class AssessmentError(RuntimeError):
    pass


# --------------------------------------------------------------------------------------
# Diagnostic
# --------------------------------------------------------------------------------------


def start_diagnostic(
    db: DbSession, user: User, goal: Goal, *, now: datetime | None = None
) -> DiagnosticAttempt:
    existing = db.scalar(
        select(DiagnosticAttempt)
        .where(
            DiagnosticAttempt.user_id == user.id,
            DiagnosticAttempt.goal_id == goal.id,
            DiagnosticAttempt.status == "in_progress",
        )
        .limit(1)
    )
    if existing is not None:
        return existing

    attempt = DiagnosticAttempt(
        user_id=user.id,
        goal_id=goal.id,
        status="in_progress",
        item_ids=[],
        cursor=0,
        started_at=now or utcnow(),
    )
    db.add(attempt)
    db.flush()
    return attempt


def _answered_objectives(db: DbSession, attempt: DiagnosticAttempt) -> set[str]:
    return set(
        db.scalars(
            select(DiagnosticResponse.objective_id).where(DiagnosticResponse.attempt_id == attempt.id)
        ).all()
    )


def _target_difficulty(db: DbSession, attempt: DiagnosticAttempt) -> int:
    responses = list(
        db.scalars(
            select(DiagnosticResponse)
            .where(DiagnosticResponse.attempt_id == attempt.id)
            .order_by(DiagnosticResponse.answered_at, DiagnosticResponse.id)
        )
    )
    target = DIAGNOSTIC_START_DIFFICULTY
    for response in responses:
        target = min(5, target + 1) if response.is_correct else max(1, target - 1)
    return target


def next_diagnostic_item(db: DbSession, attempt: DiagnosticAttempt, path_id: str) -> Item | None:
    """Deterministic adaptive selection: nearest difficulty to the running target, unseen objective first."""
    answered = set(attempt.item_ids or [])
    if len(answered) >= DIAGNOSTIC_MAX_ITEMS:
        return None

    assessed_objectives = _answered_objectives(db, attempt)
    target = _target_difficulty(db, attempt)

    candidates = list(
        db.scalars(
            select(Item)
            .join(Objective, Item.objective_id == Objective.id)
            .where(Objective.path_id == path_id, Item.is_diagnostic.is_(True))
        )
    )
    candidates = [item for item in candidates if item.id not in answered]
    if not candidates:
        return None

    objective_sequence = {
        row.id: row.sequence for row in db.scalars(select(Objective).where(Objective.path_id == path_id))
    }

    def sort_key(item: Item) -> tuple:
        already = item.objective_id in assessed_objectives
        return (
            already,  # finish assessing new objectives before re-testing one
            abs(item.difficulty - target),
            objective_sequence.get(item.objective_id, 0),
            item.id,
        )

    candidates.sort(key=sort_key)
    return candidates[0]


def answer_diagnostic(
    db: DbSession,
    user: User,
    attempt: DiagnosticAttempt,
    *,
    item_id: str,
    response: dict,
    confidence: str = "unsure",
    now: datetime | None = None,
) -> dict:
    if attempt.status != "in_progress":
        raise AssessmentError("This diagnostic has already been completed.")

    item = db.get(Item, item_id)
    if item is None:
        raise AssessmentError("Unknown item.")
    if item.id in set(attempt.item_ids or []):
        raise AssessmentError("That item was already answered in this diagnostic.")

    outcome: GradeResult = grade(item.kind, item.answer_key, response)
    moment = now or utcnow()

    db.add(
        DiagnosticResponse(
            attempt_id=attempt.id,
            item_id=item.id,
            objective_id=item.objective_id,
            response=response,
            is_correct=outcome.is_correct,
            difficulty=item.difficulty,
            answered_at=moment,
        )
    )
    attempt.item_ids = [*(attempt.item_ids or []), item.id]
    attempt.cursor = len(attempt.item_ids)

    # Self-reported confidence is recorded but never changes placement (ADR 0004).
    record_evidence(
        db,
        user_id=user.id,
        objective_id=item.objective_id,
        outcome="success" if outcome.is_correct else "failure",
        assisted=False,
        kind="diagnostic",
        source_ref=item.id,
        occurred_at=moment,
        meta={"confidence": confidence, "difficulty": item.difficulty},
    )
    recompute_mastery(db, user.id, objective_id=item.objective_id)

    objective = db.get(Objective, item.objective_id)
    feedback = {
        "is_correct": outcome.is_correct,
        "correct_answer": _canonical_answer(item, outcome),
        "explanation": localised(
            {"explanation_en": item.explanation_en, "explanation_ar": item.explanation_ar},
            "explanation",
            "en",
        ),
        "objective_id": item.objective_id,
        "objective_title": objective.title_en if objective else item.objective_id,
    }

    goal = db.get(Goal, attempt.goal_id)
    path_id = goal.path_id if goal else ""
    upcoming = next_diagnostic_item(db, attempt, path_id)
    completed = upcoming is None
    if completed:
        attempt.status = "completed"
        attempt.completed_at = moment
        attempt.placement = _placement(db, attempt)
    db.flush()

    return {"feedback": feedback, "completed": completed, "placement": attempt.placement}


def _canonical_answer(item: Item, outcome: GradeResult) -> str:
    if item.kind == "mcq_single":
        key = item.answer_key or {}
        option_id = key.get("option_id")
        for option in item.options or []:
            if option.get("id") == option_id:
                return localised(option, "", "en") or str(option.get("en", ""))
        return str(option_id or "")
    if outcome.canonical_answer:
        return outcome.canonical_answer
    accepted = (item.answer_key or {}).get("accepted") or []
    return str(accepted[0]) if accepted else ""


def _placement(db: DbSession, attempt: DiagnosticAttempt) -> dict:
    responses = list(
        db.scalars(
            select(DiagnosticResponse)
            .where(DiagnosticResponse.attempt_id == attempt.id)
            .order_by(DiagnosticResponse.answered_at, DiagnosticResponse.id)
        )
    )
    per_objective: dict[str, dict] = {}
    for response in responses:
        entry = per_objective.setdefault(
            response.objective_id,
            {"status": "needs_work", "confidence": "low", "difficulty": response.difficulty},
        )
        if response.is_correct:
            entry["status"] = "assumed_known" if response.difficulty >= 3 else "likely_known"
            entry["confidence"] = "high" if response.difficulty >= 4 else "medium"
            entry["difficulty"] = max(entry["difficulty"], response.difficulty)
    summary = {
        "assumed_known": sum(1 for entry in per_objective.values() if entry["status"] == "assumed_known"),
        "likely_known": sum(1 for entry in per_objective.values() if entry["status"] == "likely_known"),
        "needs_work": sum(1 for entry in per_objective.values() if entry["status"] == "needs_work"),
    }
    return {
        "objectives": per_objective,
        "summary": summary,
        "note": (
            "Placement is provisional: it reflects one short check and will be revised by your "
            "practice evidence."
        ),
    }


# --------------------------------------------------------------------------------------
# Practice
# --------------------------------------------------------------------------------------


def _difficulty_band(db: DbSession, user_id: str, objective_id: str) -> int:
    estimates = load_estimates(db, user_id)
    estimate = estimates.get(objective_id)
    if estimate is None:
        return 1
    if estimate.phase == "retaining":
        return 4
    return min(5, 2 + estimate.unassisted_successes)


def start_practice(
    db: DbSession,
    user: User,
    *,
    objective_id: str,
    size: int = 5,
    goal_id: str | None = None,
    plan_item_id: str | None = None,
    now: datetime | None = None,
) -> PracticeSession:
    objective = db.get(Objective, objective_id)
    if objective is None:
        raise AssessmentError("Unknown objective.")
    session = PracticeSession(
        user_id=user.id,
        goal_id=goal_id,
        plan_item_id=plan_item_id,
        objective_id=objective_id,
        status="in_progress",
        started_at=now or utcnow(),
    )
    db.add(session)
    db.flush()
    return session


def practice_items(db: DbSession, session: PracticeSession, *, size: int = 5) -> list[Item]:
    """Choose items nearest the learner's current difficulty band, stable order, no repeats."""
    answered = set(
        db.scalars(select(PracticeResponse.item_id).where(PracticeResponse.session_id == session.id)).all()
    )
    band = _difficulty_band(db, session.user_id, session.objective_id)
    candidates = [
        item
        for item in db.scalars(select(Item).where(Item.objective_id == session.objective_id))
        if item.id not in answered
    ]
    candidates.sort(key=lambda item: (abs(item.difficulty - band), item.difficulty, item.id))
    return candidates[:size]


def answer_practice(
    db: DbSession,
    user: User,
    session: PracticeSession,
    *,
    item_id: str,
    response: dict,
    used_hint: bool = False,
    now: datetime | None = None,
) -> dict:
    if session.status != "in_progress":
        raise AssessmentError("This practice session is already complete.")
    item = db.get(Item, item_id)
    if item is None or item.objective_id != session.objective_id:
        raise AssessmentError("Unknown item for this practice session.")

    already = db.scalar(
        select(PracticeResponse).where(
            PracticeResponse.session_id == session.id, PracticeResponse.item_id == item.id
        )
    )
    if already is not None:
        raise AssessmentError("That item was already answered in this session.")

    outcome = grade(item.kind, item.answer_key, response)
    moment = now or utcnow()
    db.add(
        PracticeResponse(
            session_id=session.id,
            item_id=item.id,
            objective_id=item.objective_id,
            response=response,
            is_correct=outcome.is_correct,
            assisted=used_hint,
            answered_at=moment,
        )
    )

    record_evidence(
        db,
        user_id=user.id,
        objective_id=item.objective_id,
        outcome="success" if outcome.is_correct else "failure",
        assisted=used_hint,
        kind="practice",
        source_ref=item.id,
        occurred_at=moment,
        meta={"session_id": session.id},
    )
    recompute_mastery(db, user.id, objective_id=item.objective_id)

    objective = db.get(Objective, item.objective_id)
    feedback = {
        "is_correct": outcome.is_correct,
        "correct_answer": _canonical_answer(item, outcome),
        "explanation": localised(
            {"explanation_en": item.explanation_en, "explanation_ar": item.explanation_ar},
            "explanation",
            "en",
        ),
        "objective_id": item.objective_id,
        "objective_title": objective.title_en if objective else item.objective_id,
    }

    remaining = practice_items(db, session)
    if not remaining:
        session.status = "completed"
        session.completed_at = moment
    db.flush()

    return {
        "feedback": feedback,
        "next_item": remaining[0] if remaining else None,
        "remaining": len(remaining),
    }
