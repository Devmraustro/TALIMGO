"""Spaced review: what is due, and when a flashcard comes back.

Two deterministic jobs live here, both pure (no I/O, no clock — ``now`` is an argument):

1. **The review queue** (:func:`review_candidates`) derives what deserves review from the
   mastery estimates the learner already has: confirmed objectives whose estimated recall fell
   below the review threshold, and objectives started but never confirmed with a *spaced* success
   whose confirmation is now due (ADR 0004 requires a correct answer at least
   ``DELAYED_SUCCESS_GAP_DAYS`` later). It introduces no second model of memory — retrievability
   is the mastery model's own.

2. **The flashcard ladder** (:func:`next_card_state`) schedules study cards. Flashcards are a
   study aid, not assessment: rating a card never records evidence and never moves mastery
   (ADR 0009). The ladder is deliberately a small fixed sequence rather than a fitted model such
   as FSRS: there is no calibration data to fit FSRS weights to, and the reuse audit records the
   decision to defer adoption until review-log data exists (``docs/OPEN_SOURCE_REUSE_AUDIT.md``).
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Literal

from app.learning.mastery import (
    DELAYED_SUCCESS_GAP_DAYS,
    RETRIEVABILITY_TARGET,
    retrievability,
)
from app.learning.types import KnowledgeEstimate

ReviewReason = Literal["recall_below_target", "spaced_confirmation_due"]
CardRating = Literal["again", "good"]

# Days until a "good"-rated card is due again, by consecutive-good count (capped at the last rung).
INTERVAL_LADDER_DAYS = (1.0, 3.0, 7.0, 16.0, 35.0)
# An "again" card returns inside the same study session, not tomorrow.
AGAIN_DELAY_MINUTES = 10


@dataclass(frozen=True)
class ReviewCandidate:
    objective_id: str
    reason: ReviewReason
    retrievability: float | None
    last_evidence_at: datetime | None


def review_candidates(estimates: dict[str, KnowledgeEstimate], now: datetime) -> list[ReviewCandidate]:
    """What deserves review now, most urgent first.

    Fading confirmed knowledge outranks pending confirmations (losing what was proven costs more
    than delaying a confirmation); inside each group, lowest recall / oldest evidence first.
    """
    fading: list[ReviewCandidate] = []
    confirmations: list[ReviewCandidate] = []
    for estimate in estimates.values():
        if estimate.phase == "retaining":
            value = retrievability(estimate, now)
            if value is not None and value < RETRIEVABILITY_TARGET:
                fading.append(
                    ReviewCandidate(
                        objective_id=estimate.objective_id,
                        reason="recall_below_target",
                        retrievability=value,
                        last_evidence_at=estimate.last_evidence_at,
                    )
                )
        elif (
            estimate.unassisted_successes >= 1
            and not estimate.has_delayed_success
            and estimate.last_evidence_at is not None
            and (now - estimate.last_evidence_at) >= timedelta(days=DELAYED_SUCCESS_GAP_DAYS)
        ):
            # A correct answer now would count as the spaced success mastery requires.
            confirmations.append(
                ReviewCandidate(
                    objective_id=estimate.objective_id,
                    reason="spaced_confirmation_due",
                    retrievability=None,
                    last_evidence_at=estimate.last_evidence_at,
                )
            )
    fading.sort(key=lambda candidate: (candidate.retrievability or 0.0, candidate.objective_id))
    confirmations.sort(key=lambda candidate: (candidate.last_evidence_at or now, candidate.objective_id))
    return fading + confirmations


@dataclass(frozen=True)
class CardSchedule:
    repetitions: int
    interval_days: float
    due_at: datetime


def next_card_state(*, repetitions: int, rating: CardRating, now: datetime) -> CardSchedule:
    """Schedule one card after a self-rating. Unknown ratings are refused, not guessed."""
    if rating == "again":
        return CardSchedule(
            repetitions=0,
            interval_days=0.0,
            due_at=now + timedelta(minutes=AGAIN_DELAY_MINUTES),
        )
    if rating == "good":
        next_repetitions = max(0, repetitions) + 1
        rung = INTERVAL_LADDER_DAYS[min(next_repetitions, len(INTERVAL_LADDER_DAYS)) - 1]
        return CardSchedule(
            repetitions=next_repetitions,
            interval_days=rung,
            due_at=now + timedelta(days=rung),
        )
    raise ValueError(f"Unsupported card rating {rating!r}")
