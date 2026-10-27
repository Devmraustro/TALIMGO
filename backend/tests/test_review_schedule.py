"""Pure spaced-review scheduling: the queue derivation and the flashcard ladder (ADR 0009)."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest

from app.learning.mastery import MODEL_VERSION
from app.learning.review import next_card_state, review_candidates
from app.learning.types import KnowledgeEstimate

NOW = datetime(2026, 10, 27, 12, 0, tzinfo=UTC)


def _estimate(**overrides) -> KnowledgeEstimate:
    base = {
        "objective_id": "py:values",
        "phase": "retaining",
        "model_version": MODEL_VERSION,
        "unassisted_successes": 4,
        "has_delayed_success": True,
        "stability_days": 10.0,
        "last_evidence_at": NOW - timedelta(days=1),
    }
    base.update(overrides)
    return KnowledgeEstimate(**base)


def test_faded_confirmed_objective_is_due_for_review() -> None:
    # stability 1 day, last seen 5 days ago → recall e^-5 ≈ 0.7% — far below the 90% target.
    estimates = {"py:values": _estimate(stability_days=1.0, last_evidence_at=NOW - timedelta(days=5))}
    (candidate,) = review_candidates(estimates, NOW)
    assert candidate.reason == "recall_below_target"
    assert candidate.retrievability is not None and candidate.retrievability < 0.9


def test_fresh_confirmed_objective_is_not_due() -> None:
    estimates = {"py:values": _estimate()}  # recall e^-0.1 ≈ 90.5% — above target
    assert review_candidates(estimates, NOW) == []


def test_unconfirmed_objective_becomes_a_spaced_confirmation_after_the_gap() -> None:
    base = _estimate(
        phase="acquiring",
        unassisted_successes=2,
        has_delayed_success=False,
        stability_days=None,
        last_evidence_at=NOW - timedelta(days=2),
    )
    assert review_candidates({"py:values": base}, NOW) == [], "gap not reached yet"
    due = _estimate(
        phase="acquiring",
        unassisted_successes=2,
        has_delayed_success=False,
        stability_days=None,
        last_evidence_at=NOW - timedelta(days=4),
    )
    (candidate,) = review_candidates({"py:values": due}, NOW)
    assert candidate.reason == "spaced_confirmation_due"


def test_never_succeeded_objective_is_not_a_review_candidate() -> None:
    estimates = {
        "py:values": _estimate(
            phase="acquiring",
            unassisted_successes=0,
            has_delayed_success=False,
            stability_days=None,
            last_evidence_at=NOW - timedelta(days=30),
        )
    }
    assert review_candidates(estimates, NOW) == []


def test_fading_outranks_pending_confirmation() -> None:
    estimates = {
        "py:strings": _estimate(
            objective_id="py:strings",
            phase="acquiring",
            unassisted_successes=1,
            has_delayed_success=False,
            stability_days=None,
            last_evidence_at=NOW - timedelta(days=9),
        ),
        "py:values": _estimate(stability_days=2.0, last_evidence_at=NOW - timedelta(days=6)),
    }
    queue = review_candidates(estimates, NOW)
    assert [candidate.objective_id for candidate in queue] == ["py:values", "py:strings"]


def test_flashcard_ladder_climbs_and_caps() -> None:
    first = next_card_state(repetitions=0, rating="good", now=NOW)
    assert (first.repetitions, first.interval_days) == (1, 1.0)
    assert first.due_at == NOW + timedelta(days=1)
    third = next_card_state(repetitions=2, rating="good", now=NOW)
    assert (third.repetitions, third.interval_days) == (3, 7.0)
    beyond = next_card_state(repetitions=9, rating="good", now=NOW)
    assert beyond.interval_days == 35.0, "the ladder caps at its last rung"


def test_flashcard_again_returns_inside_the_session() -> None:
    again = next_card_state(repetitions=4, rating="again", now=NOW)
    assert again.repetitions == 0
    assert again.due_at == NOW + timedelta(minutes=10)


def test_unknown_flashcard_rating_is_refused() -> None:
    with pytest.raises(ValueError):
        next_card_state(repetitions=0, rating="easy", now=NOW)  # type: ignore[arg-type]
