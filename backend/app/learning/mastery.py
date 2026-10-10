"""Mastery model v1 — deterministic, pure, replayable.

Specification: ``docs/adr/0004-mastery-model-v1.md``.
Invariants:
  * Evidence is the source of truth; estimates are derived and disposable.
  * One active model version. An estimate carrying another version is stale input and is
    rejected rather than mixed.
  * No I/O, no clock, no randomness: ``now`` is always an argument.
"""

from __future__ import annotations

import math
from dataclasses import replace
from datetime import datetime
from typing import Literal

from app.learning.types import EvidenceRecord, KnowledgeEstimate, Phase

MODEL_VERSION = "mastery-v1"

# Model parameters. These are PLACEHOLDERS to be validated against recorded learner evidence;
# changing any of them is a model-version change (ADR 0004).
PROMOTION_UNASSISTED_SUCCESSES = 3
DELAYED_SUCCESS_GAP_DAYS = 3.0
RETRIEVABILITY_TARGET = 0.9
STABILITY_GROWTH = 1.5
STABILITY_SHRINK = 0.5
MIN_STABILITY_DAYS = 0.5
MAX_STABILITY_DAYS = 365.0
DEMOTION_FAILURES = 2
SECONDS_PER_DAY = 86_400.0


class StaleModelVersionError(ValueError):
    """Raised when an estimate produced by another model version is used as input."""


def _elapsed_days(start: datetime, end: datetime) -> float:
    return max(0.0, (end - start).total_seconds() / SECONDS_PER_DAY)


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def check_version(estimate: KnowledgeEstimate) -> None:
    """Reject an estimate that another model version produced."""
    if estimate.model_version != MODEL_VERSION:
        raise StaleModelVersionError(
            f"Estimate for {estimate.objective_id!r} carries model version "
            f"{estimate.model_version!r}; the active version is {MODEL_VERSION!r}. "
            "Recompute it by replaying the learner's evidence."
        )


def replay(records: list[EvidenceRecord]) -> dict[str, KnowledgeEstimate]:
    """Fold evidence into estimates, per objective.

    Ordering is ``(occurred_at, id)`` so the result never depends on arrival order and late
    evidence is absorbed correctly.
    """
    grouped: dict[str, list[EvidenceRecord]] = {}
    for record in records:
        grouped.setdefault(record.objective_id, []).append(record)

    estimates: dict[str, KnowledgeEstimate] = {}
    for objective_id, items in grouped.items():
        ordered = sorted(items, key=lambda r: (r.occurred_at, r.id))
        estimates[objective_id] = _fold_objective(objective_id, ordered)
    return estimates


def _fold_objective(objective_id: str, ordered: list[EvidenceRecord]) -> KnowledgeEstimate:
    phase: Phase = "acquiring"
    successes = 0
    failures_retaining = 0
    delayed = False
    stability: float | None = None
    last_unassisted_success_at: datetime | None = None
    last_evidence_at: datetime | None = None

    for record in ordered:
        last_evidence_at = record.occurred_at
        if record.outcome == "success":
            if record.assisted:
                # Assisted success proves exposure, not capability: it never promotes and never
                # extends stability. It is still recorded and shown to the learner.
                continue
            gap_days = (
                _elapsed_days(last_unassisted_success_at, record.occurred_at)
                if last_unassisted_success_at is not None
                else None
            )
            if gap_days is not None and gap_days >= DELAYED_SUCCESS_GAP_DAYS:
                delayed = True
            successes += 1
            if phase == "retaining":
                base = stability if stability is not None else MIN_STABILITY_DAYS
                grown = max(base, gap_days if gap_days is not None else base) * STABILITY_GROWTH
                stability = _clamp(grown, MIN_STABILITY_DAYS, MAX_STABILITY_DAYS)
                failures_retaining = 0
            elif successes >= PROMOTION_UNASSISTED_SUCCESSES and delayed:
                phase = "retaining"
                # Initial stability follows the spacing actually observed between successes.
                stability = _clamp(
                    gap_days if gap_days is not None else MIN_STABILITY_DAYS,
                    MIN_STABILITY_DAYS,
                    MAX_STABILITY_DAYS,
                )
            last_unassisted_success_at = record.occurred_at
        else:  # failure
            if phase == "retaining":
                base = stability if stability is not None else MIN_STABILITY_DAYS
                stability = max(MIN_STABILITY_DAYS, base * STABILITY_SHRINK)
                failures_retaining += 1
                if failures_retaining >= DEMOTION_FAILURES:
                    phase = "acquiring"
                    stability = None
                    failures_retaining = 0
            # A failure while acquiring means "not learned yet"; it is not a lapse.

    return KnowledgeEstimate(
        objective_id=objective_id,
        phase=phase,
        model_version=MODEL_VERSION,
        unassisted_successes=successes,
        failures_while_retaining=failures_retaining,
        has_delayed_success=delayed,
        stability_days=stability,
        last_evidence_at=last_evidence_at,
    )


def retrievability(estimate: KnowledgeEstimate, now: datetime) -> float | None:
    """Probability the learner can currently recall it. Derived, never stored."""
    check_version(estimate)
    if estimate.phase != "retaining" or not estimate.stability_days or estimate.last_evidence_at is None:
        return None
    elapsed = _elapsed_days(estimate.last_evidence_at, now)
    return math.exp(-elapsed / estimate.stability_days)


def needs_review(
    estimate: KnowledgeEstimate, now: datetime, threshold: float = RETRIEVABILITY_TARGET
) -> bool:
    value = retrievability(estimate, now)
    return value is not None and value < threshold


def phase_for(estimate: KnowledgeEstimate | None) -> Literal["unseen", "acquiring", "retaining"]:
    if estimate is None:
        return "unseen"
    return estimate.phase


def summary(estimates: dict[str, KnowledgeEstimate], now: datetime) -> dict[str, int]:
    """Counts by state, for the dashboard."""
    counters = {"unseen": 0, "acquiring": 0, "retaining": 0, "needs_review": 0}
    for estimate in estimates.values():
        counters[estimate.phase] += 1
        if needs_review(estimate, now):
            counters["needs_review"] += 1
    return counters


def explain(estimate: KnowledgeEstimate, now: datetime, title: str = "") -> str:
    """Plain-language account of where the estimate came from. Always shown with the state."""
    label = f"“{title}”" if title else "This objective"
    if estimate.phase == "acquiring":
        if estimate.unassisted_successes == 0:
            return f"{label} is still being learned: no unassisted correct answers yet."
        missing = []
        if estimate.unassisted_successes < PROMOTION_UNASSISTED_SUCCESSES:
            remaining = PROMOTION_UNASSISTED_SUCCESSES - estimate.unassisted_successes
            missing.append(f"{remaining} more unassisted correct answer(s)")
        if not estimate.has_delayed_success:
            missing.append("a correct answer at least 3 days later")
        needed = " and ".join(missing)
        return f"{label} is being learned. To confirm it, you still need: {needed}."
    value = retrievability(estimate, now)
    if value is None:  # cannot happen for a retaining estimate; fail loudly if it ever does
        raise StaleModelVersionError(
            f"Estimate for {estimate.objective_id!r} is in phase 'retaining' but has no retrievability."
        )
    percent = round(value * 100)
    if value < RETRIEVABILITY_TARGET:
        return (
            f"{label} was confirmed after {estimate.unassisted_successes} unassisted correct answers, "
            f"but {percent}% recall is below the review threshold — a short review is due."
        )
    return (
        f"{label} is confirmed: {estimate.unassisted_successes} unassisted correct answers, "
        f"estimated {percent}% recall right now."
    )


def promote_manually(estimate: KnowledgeEstimate, *, stability_days: float) -> KnowledgeEstimate:
    """Used only by seed/replay tooling; never by the AI layer."""
    return replace(
        estimate,
        phase="retaining",
        stability_days=_clamp(stability_days, MIN_STABILITY_DAYS, MAX_STABILITY_DAYS),
    )
