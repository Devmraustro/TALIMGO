"""Diagnostic placement and practice sessions — all grading deterministic.

Item selection here is deliberate and simple: difficulty follows the learner's running performance
inside the diagnostic and the mastery phase during practice, and the tie-breaks are stable, so the
same state always produces the same next item. Adaptive bandit-style selection is recorded as FUTURE
in the implementation plan because it needs calibration data we do not have.

Placement rule (explicit and deterministic — see ``aggregate_placement``):
  * every answer about an objective is counted; an incorrect answer is never discarded because an
    earlier answer was correct;
  * any incorrect answer leaves the objective at ``needs_work`` for this check — a demonstrated
    failure is decisive inside one short placement, and the roadmap will teach the objective properly;
  * if every answer was correct, the objective is ``assumed_known`` when the hardest correct answer was
    difficulty >= 3, and ``likely_known`` when only easy items were answered;
  * placement is always provisional: mastery still requires unassisted, spaced success (ADR 0004).
"""

from __future__ import annotations

from collections.abc import Sequence
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
    Plan,
    PlanItem,
    PracticeResponse,
    PracticeSession,
    User,
)
from app.services.progress import load_estimates, recompute_mastery, record_evidence
from app.utils import utcnow

DIAGNOSTIC_MAX_ITEMS = 12
DIAGNOSTIC_START_DIFFICULTY = 2


class AssessmentError(RuntimeError):
    """The requested object is unknown, or belongs to somebody else (reported as 404)."""


class AssessmentConflict(AssessmentError):
    """The request is well-formed but contradicts recorded state (reported as 409)."""


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

    # Everything below is validated *before* anything is graded or written, so a rejected request
    # leaves no response row, no evidence and no cursor movement.
    goal = db.get(Goal, attempt.goal_id)
    path_id = goal.path_id if goal else ""
    if not path_id:
        raise AssessmentError("This diagnostic is not linked to a learning path.")

    objective = db.get(Objective, item.objective_id)
    if objective is None or objective.path_id != path_id:
        raise AssessmentError("That item does not belong to this learning path.")
    if not item.is_diagnostic:
        raise AssessmentError("That item is not part of the starting check.")

    expected = next_diagnostic_item(db, attempt, path_id)
    if expected is None:
        raise AssessmentError("This check has no further items to answer.")
    if expected.id != item.id:
        raise AssessmentError(
            "That is not the next item in this check. Answer only the item that was presented."
        )

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


PLACEMENT_RULE = (
    "Each answer is counted. Any incorrect answer leaves the objective at needs_work for this check; "
    "with only correct answers it is assumed_known when the hardest correct item was difficulty 3 or "
    "more, and likely_known when every answered item was easy."
)
HARD_ITEM_DIFFICULTY = 3


def aggregate_placement(responses: Sequence[tuple[str, bool, int]]) -> dict[str, dict]:
    """Combine ``(objective_id, is_correct, difficulty)`` records into one placement per objective.

    Pure and order-independent for the *counts*; the caller supplies records in answer order so the
    result is reproducible and explainable.
    """
    per_objective: dict[str, dict] = {}
    for objective_id, is_correct, difficulty in responses:
        entry = per_objective.setdefault(
            objective_id,
            {"difficulty": difficulty, "correct": 0, "incorrect": 0, "hardest_correct": 0},
        )
        entry["difficulty"] = max(entry["difficulty"], difficulty)
        if is_correct:
            entry["correct"] += 1
            entry["hardest_correct"] = max(entry["hardest_correct"], difficulty)
        else:
            entry["incorrect"] += 1

    for entry in per_objective.values():
        if entry["incorrect"] > 0:
            entry["status"] = "needs_work"
            entry["confidence"] = "low"
        elif entry["hardest_correct"] >= HARD_ITEM_DIFFICULTY:
            entry["status"] = "assumed_known"
            entry["confidence"] = "high" if entry["hardest_correct"] >= 4 else "medium"
        else:
            entry["status"] = "likely_known"
            entry["confidence"] = "medium"
    return per_objective


def _placement(db: DbSession, attempt: DiagnosticAttempt) -> dict:
    responses = list(
        db.scalars(
            select(DiagnosticResponse)
            .where(DiagnosticResponse.attempt_id == attempt.id)
            .order_by(DiagnosticResponse.answered_at, DiagnosticResponse.id)
        )
    )
    per_objective = aggregate_placement(
        [
            (response.objective_id, bool(response.is_correct), int(response.difficulty))
            for response in responses
        ]
    )
    summary = {
        "assumed_known": sum(1 for entry in per_objective.values() if entry["status"] == "assumed_known"),
        "likely_known": sum(1 for entry in per_objective.values() if entry["status"] == "likely_known"),
        "needs_work": sum(1 for entry in per_objective.values() if entry["status"] == "needs_work"),
    }
    return {
        "objectives": per_objective,
        "summary": summary,
        "rule": PLACEMENT_RULE,
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


def _resolve_practice_context(
    db: DbSession,
    user: User,
    *,
    objective: Objective,
    goal_id: str | None,
    plan_item_id: str | None,
) -> str | None:
    """Validate that the learner may practise this objective in this context.

    The whole chain has to agree: the goal is the learner's own and on the objective's path, and the
    plan item belongs to the learner's plan, to that goal and to the objective being practised.
    References to anything else are reported as unknown (404) with one message per kind, so another
    learner's identifiers are never confirmed to exist; inconsistencies inside the learner's own data
    are conflicts (409). Every check runs before the session row is created.

    Returns the goal id the session belongs to (derived from the plan item when not supplied).
    """
    resolved_goal_id: str | None = None
    if goal_id is not None:
        goal = db.get(Goal, goal_id)
        if goal is None or goal.user_id != user.id:
            raise AssessmentError("Unknown goal.")
        if goal.path_id != objective.path_id:
            raise AssessmentConflict("That goal is for a different learning path.")
        resolved_goal_id = goal.id

    if plan_item_id is not None:
        plan_item = db.get(PlanItem, plan_item_id)
        plan = db.get(Plan, plan_item.plan_id) if plan_item is not None else None
        if plan_item is None or plan is None or plan.user_id != user.id:
            # Deliberately the same message as an unknown id: existence is not disclosed.
            raise AssessmentError("Unknown plan item.")
        if plan_item.objective_id != objective.id:
            raise AssessmentConflict("That plan item belongs to a different objective.")
        plan_goal = db.get(Goal, plan.goal_id)
        if plan_goal is None:
            raise AssessmentError("Unknown plan item.")
        if plan_goal.path_id != objective.path_id:
            raise AssessmentConflict("That plan item is for a different learning path.")
        if resolved_goal_id is not None and plan.goal_id != resolved_goal_id:
            raise AssessmentConflict("That plan item belongs to a different goal.")
        resolved_goal_id = plan_goal.id

    return resolved_goal_id


def plan_item_for_user(db: DbSession, plan_item_id: str, user_id: str) -> PlanItem | None:
    """Fetch a plan item only if it belongs to this learner's own plan."""
    plan_item = db.get(PlanItem, plan_item_id)
    if plan_item is None:
        return None
    plan = db.get(Plan, plan_item.plan_id)
    if plan is None or plan.user_id != user_id:
        return None
    return plan_item


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

    resolved_goal_id = _resolve_practice_context(
        db, user, objective=objective, goal_id=goal_id, plan_item_id=plan_item_id
    )

    pool = list(db.scalars(select(Item).where(Item.objective_id == objective_id)).all())
    if not pool:
        raise AssessmentConflict("This objective has no practice questions yet.")
    band = _difficulty_band(db, user.id, objective_id)
    pool.sort(key=lambda row: (abs(row.difficulty - band), row.difficulty, row.id))
    target = max(1, min(size, len(pool)))

    session = PracticeSession(
        user_id=user.id,
        goal_id=resolved_goal_id,
        plan_item_id=plan_item_id,
        objective_id=objective_id,
        status="in_progress",
        target_items=target,
        item_ids=[row.id for row in pool[:target]],
        started_at=now or utcnow(),
    )
    db.add(session)
    db.flush()
    return session


def next_practice_item(db: DbSession, session: PracticeSession) -> Item | None:
    """The next unanswered question of the session's frozen plan, or ``None`` when it is done.

    The plan (``session.item_ids``) was resolved once, when the session was created, so the session
    length and the question order cannot change between requests, and the difficulty band moving
    after a correct answer cannot silently extend the session.
    """
    if session.status != "in_progress":
        return None
    answered = set(
        db.scalars(select(PracticeResponse.item_id).where(PracticeResponse.session_id == session.id)).all()
    )
    for item_id in session.item_ids or []:
        if item_id in answered:
            continue
        item = db.get(Item, item_id)
        if item is not None:
            return item
    return None


def practice_items(db: DbSession, session: PracticeSession) -> list[Item]:
    """Backwards-compatible view of :func:`next_practice_item` as a 0-or-1 element list."""
    item = next_practice_item(db, session)
    return [item] if item is not None else []


def practice_progress(db: DbSession, session: PracticeSession) -> tuple[int, int]:
    """``(answered, target)`` for the session, from persisted state only."""
    answered = len(
        db.scalars(select(PracticeResponse.id).where(PracticeResponse.session_id == session.id)).all()
    )
    return answered, len(session.item_ids or [])


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
        raise AssessmentConflict("This practice session is already finished; start a new one.")
    item = db.get(Item, item_id)
    if item is None or item.objective_id != session.objective_id:
        raise AssessmentError("Unknown item for this practice session.")
    if item.id not in set(session.item_ids or []):
        raise AssessmentConflict("That question is not part of this practice session.")

    already = db.scalar(
        select(PracticeResponse).where(
            PracticeResponse.session_id == session.id, PracticeResponse.item_id == item.id
        )
    )
    if already is not None:
        raise AssessmentConflict("That item was already answered in this session.")
    expected = next_practice_item(db, session)
    if expected is None or expected.id != item.id:
        raise AssessmentConflict("That is not the next question in this session.")

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

    db.flush()

    # Answering the last question does **not** complete the session: completion is an explicit,
    # validated action (``complete_practice``), because it is what ticks the roadmap item off.
    following = next_practice_item(db, session)
    answered, target = practice_progress(db, session)
    return {
        "feedback": feedback,
        "next_item": following,
        "remaining": max(0, target - answered),
    }


def complete_practice(db: DbSession, session: PracticeSession, *, now: datetime | None = None) -> None:
    """Complete a session that has answered every planned question.

    Raises ``AssessmentConflict`` (409) for an already-finished session or one whose completion
    condition is not met, so a client can never mark roadmap progress it did not earn.
    """
    if session.status == "completed":
        raise AssessmentConflict("This practice session is already complete.")
    if session.status == "abandoned":
        raise AssessmentConflict("This practice session was left and cannot be completed.")
    answered, target = practice_progress(db, session)
    if target == 0:
        raise AssessmentConflict("This practice session has no questions to complete.")
    if answered < target:
        raise AssessmentConflict(
            f"Answer all {target} questions before completing this session ({answered} answered)."
        )
    session.status = "completed"
    session.completed_at = now or utcnow()


def abandon_practice(db: DbSession, session: PracticeSession, *, now: datetime | None = None) -> None:
    """Leave a session without losing recorded answers; it can never be completed afterwards."""
    if session.status != "in_progress":
        raise AssessmentConflict("Only a session in progress can be left.")
    session.status = "abandoned"
    session.abandoned_at = now or utcnow()
