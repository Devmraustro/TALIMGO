"""Spaced-review services: the review queue and flashcards (ADR 0009).

* The **review queue** is a projection of the mastery estimates (``app.learning.review``):
  nothing new is stored, and starting a review is an ordinary practice session in ``review``
  mode, so its answers are ordinary practice evidence.
* **Flashcards** are a study aid over items the learner has *already answered* (in practice or
  the starting check). Restricting cards to seen items keeps the diagnostic honest: a learner
  cannot memorise unseen keys through the study deck before being placed by them. Rating a
  card schedules it (``FlashcardState``) and records **no evidence** — a self-rating is not a
  demonstration of capability, so it must never move mastery (ADR 0006 boundary).
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session as DbSession

from app.curriculum.registry import localised
from app.learning.review import next_card_state, review_candidates
from app.learning.types import GradeResult
from app.models import (
    DiagnosticAttempt,
    DiagnosticResponse,
    FlashcardState,
    Item,
    Objective,
    PracticeResponse,
    PracticeSession,
    User,
)
from app.services.assessment import AssessmentError, _canonical_answer
from app.services.progress import load_estimates, objective_title
from app.utils import ensure_aware, utcnow


def build_review_queue(db: DbSession, user: User, *, locale: str, now: datetime | None = None) -> dict:
    moment = now or utcnow()
    estimates = load_estimates(db, user.id)
    candidates = review_candidates(estimates, moment)
    objectives = {row.id: row for row in db.scalars(select(Objective)).all()}
    return {
        "items": [
            {
                "objective_id": candidate.objective_id,
                "objective_title": objective_title(
                    objectives.get(candidate.objective_id), locale, candidate.objective_id
                ),
                "reason": candidate.reason,
                "retrievability": candidate.retrievability,
                "phase": estimates[candidate.objective_id].phase
                if candidate.objective_id in estimates
                else "acquiring",
                "last_evidence_at": candidate.last_evidence_at,
            }
            for candidate in candidates
        ],
        "due_count": len(candidates),
    }


def _seen_item_ids(db: DbSession, user_id: str) -> set[str]:
    """Items this learner has already answered somewhere — the only honest flashcard pool."""
    practice_items = db.scalars(
        select(PracticeResponse.item_id)
        .join(PracticeSession, PracticeResponse.session_id == PracticeSession.id)
        .where(PracticeSession.user_id == user_id)
    ).all()
    diagnostic_items = db.scalars(
        select(DiagnosticResponse.item_id)
        .join(DiagnosticAttempt, DiagnosticResponse.attempt_id == DiagnosticAttempt.id)
        .where(DiagnosticAttempt.user_id == user_id)
    ).all()
    return set(practice_items) | set(diagnostic_items)


def _card_answer(item: Item, locale: str) -> str:
    """The back of the card: the same canonical answer shown in post-answer feedback."""
    if item.kind == "numeric":
        value = (item.answer_key or {}).get("value")
        try:
            number = float(value)  # type: ignore[arg-type]
        except (TypeError, ValueError):
            return str(value or "")
        return str(int(number)) if number == int(number) else repr(number)
    return _canonical_answer(item, GradeResult(is_correct=True, canonical_answer=""), locale)


def flashcards_for(
    db: DbSession,
    user: User,
    *,
    locale: str,
    objective_id: str | None = None,
    limit: int = 50,
    now: datetime | None = None,
) -> dict:
    moment = now or utcnow()
    seen = _seen_item_ids(db, user.id)
    if not seen:
        return {"cards": [], "due_count": 0}
    query = select(Item).where(Item.id.in_(sorted(seen)))
    if objective_id:
        query = query.where(Item.objective_id == objective_id)
    items = list(db.scalars(query).all())
    states = {
        row.item_id: row
        for row in db.scalars(select(FlashcardState).where(FlashcardState.user_id == user.id)).all()
    }
    objectives = {row.id: row for row in db.scalars(select(Objective)).all()}

    def _due_at(item: Item) -> datetime:
        state = states.get(item.id)
        return ensure_aware(state.due_at) if state is not None else moment

    items.sort(key=lambda item: (_due_at(item), item.id))
    cards = []
    due_count = 0
    for item in items:
        state = states.get(item.id)
        is_due = state is None or ensure_aware(state.due_at) <= moment
        due_count += 1 if is_due else 0
        cards.append(
            {
                "item_id": item.id,
                "objective_id": item.objective_id,
                "objective_title": objective_title(
                    objectives.get(item.objective_id), locale, item.objective_id
                ),
                "prompt": localised(
                    {"prompt_en": item.prompt_en, "prompt_ar": item.prompt_ar}, "prompt", locale
                ),
                "answer": _card_answer(item, locale),
                "explanation": localised(
                    {"explanation_en": item.explanation_en, "explanation_ar": item.explanation_ar},
                    "explanation",
                    locale,
                ),
                "repetitions": state.repetitions if state is not None else 0,
                "due_at": ensure_aware(state.due_at) if state is not None else moment,
                "is_due": is_due,
            }
        )
    return {"cards": cards[: max(1, min(limit, 200))], "due_count": due_count}


def rate_flashcard(
    db: DbSession,
    user: User,
    *,
    item_id: str,
    rating: str,
    now: datetime | None = None,
) -> FlashcardState:
    """Schedule a card after a self-rating. Records no evidence by design (ADR 0009)."""
    if rating not in {"again", "good"}:
        raise AssessmentError("Unknown flashcard rating.")
    item = db.get(Item, item_id)
    if item is None or item.id not in _seen_item_ids(db, user.id):
        # Unseen items are indistinguishable from unknown ones: the deck reveals nothing new.
        raise AssessmentError("Unknown flashcard.")
    moment = now or utcnow()
    state = db.scalar(
        select(FlashcardState).where(FlashcardState.user_id == user.id, FlashcardState.item_id == item.id)
    )
    if state is None:
        # Explicit values: column defaults apply at flush, but the scheduler reads the current
        # repetition count before any write happens.
        state = FlashcardState(
            user_id=user.id,
            item_id=item.id,
            objective_id=item.objective_id,
            repetitions=0,
            interval_days=0.0,
            due_at=moment,
            last_rating="",
        )
        db.add(state)
    scheduled = next_card_state(repetitions=state.repetitions, rating=rating, now=moment)  # type: ignore[arg-type]
    state.repetitions = scheduled.repetitions
    state.interval_days = scheduled.interval_days
    state.due_at = scheduled.due_at
    state.last_rating = rating
    state.updated_at = moment
    db.flush()
    return state
