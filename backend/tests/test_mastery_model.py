"""Unit tests for the deterministic mastery model (ADR 0004).

These tests are the specification: if the model changes behaviour, they must change deliberately.
"""

from __future__ import annotations

import random
from datetime import UTC, datetime, timedelta

import pytest

from app.learning import mastery
from app.learning.types import EvidenceRecord, KnowledgeEstimate

T0 = datetime(2026, 1, 1, 9, 0, tzinfo=UTC)


def record(day: float, outcome: str, *, assisted: bool = False, suffix: str = "") -> EvidenceRecord:
    return EvidenceRecord(
        id=f"evd_{int(day * 1000):06d}{suffix}",
        objective_id="py:values",
        outcome=outcome,  # type: ignore[arg-type]
        occurred_at=T0 + timedelta(days=day),
        assisted=assisted,
    )


def test_replay_is_order_independent() -> None:
    records = [record(0, "success"), record(1, "failure"), record(4, "success"), record(9, "success")]
    first = mastery.replay(records)
    shuffled = records[:]
    random.Random(7).shuffle(shuffled)
    second = mastery.replay(shuffled)
    assert first == second


def test_failure_first_does_not_create_decaying_memory() -> None:
    estimate = mastery.replay([record(0, "failure")])["py:values"]
    assert estimate.phase == "acquiring"
    assert estimate.stability_days is None
    assert mastery.retrievability(estimate, T0 + timedelta(days=30)) is None


def test_promotion_requires_three_unassisted_successes_and_a_delayed_one() -> None:
    quick = mastery.replay([record(0, "success"), record(0.1, "success"), record(0.2, "success")])[
        "py:values"
    ]
    assert quick.phase == "acquiring", "three successes on the same day are not spaced evidence"
    assert quick.has_delayed_success is False

    spaced = mastery.replay([record(0, "success"), record(0.5, "success"), record(4, "success")])["py:values"]
    assert spaced.phase == "retaining"
    assert spaced.stability_days is not None and spaced.stability_days >= 3.5


def test_assisted_success_never_promotes() -> None:
    records = [
        record(0, "success", assisted=True),
        record(1, "success", assisted=True),
        record(5, "success", assisted=True),
        record(12, "success", assisted=True),
    ]
    estimate = mastery.replay(records)["py:values"]
    assert estimate.phase == "acquiring"
    assert estimate.unassisted_successes == 0
    assert estimate.stability_days is None


def test_two_failures_while_retaining_demote_to_acquiring() -> None:
    base = [record(0, "success"), record(4, "success"), record(9, "success")]
    after_one = mastery.replay([*base, record(20, "failure")])["py:values"]
    assert after_one.phase == "retaining"
    assert after_one.failures_while_retaining == 1
    assert after_one.stability_days is not None

    after_two = mastery.replay([*base, record(20, "failure"), record(24, "failure")])["py:values"]
    assert after_two.phase == "acquiring"
    assert after_two.stability_days is None


def test_success_while_retaining_resets_the_demotion_counter() -> None:
    """A success after a lapse clears the counter, so demotion needs two consecutive failures."""
    records = [
        record(0, "success"),
        record(4, "success"),
        record(9, "success"),
        record(20, "failure"),  # counter = 1
        record(24, "success"),  # counter resets
        record(30, "failure"),  # counter = 1 again
    ]
    estimate = mastery.replay(records)["py:values"]
    assert estimate.phase == "retaining"
    assert estimate.failures_while_retaining == 1


def test_two_consecutive_failures_while_retaining_demote() -> None:
    records = [record(0, "success"), record(4, "success"), record(9, "success"), record(30, "failure")]
    assert mastery.replay(records)["py:values"].phase == "retaining"
    demoted = mastery.replay([*records, record(34, "failure")])["py:values"]
    assert demoted.phase == "acquiring"
    assert demoted.stability_days is None


def test_stability_grows_on_spaced_success_and_stays_within_bounds() -> None:
    records = [record(0, "success"), record(4, "success"), record(9, "success")]
    estimate = mastery.replay(records)["py:values"]
    baseline = estimate.stability_days
    assert baseline is not None

    extended = mastery.replay([*records, record(9 + 40, "success")])["py:values"]
    assert extended.stability_days is not None
    assert extended.stability_days > baseline
    assert extended.stability_days <= mastery.MAX_STABILITY_DAYS


def test_retrievability_decays_as_designed() -> None:
    estimate = mastery.replay([record(0, "success"), record(4, "success"), record(9, "success")])["py:values"]
    last = estimate.last_evidence_at
    assert last is not None
    assert mastery.retrievability(estimate, last) == pytest.approx(1.0, abs=1e-9)

    one_stability_later = last + timedelta(days=estimate.stability_days or 1)
    value = mastery.retrievability(estimate, one_stability_later)
    assert value is not None
    assert value == pytest.approx(0.368, abs=0.01), "exp(-1) after one stability period"

    assert mastery.needs_review(estimate, last) is False
    assert mastery.needs_review(estimate, last + timedelta(days=365)) is True


def test_stale_model_version_is_rejected() -> None:
    stale = KnowledgeEstimate(
        objective_id="py:values",
        phase="retaining",
        model_version="mastery-v0",
        stability_days=5.0,
        last_evidence_at=T0,
    )
    with pytest.raises(mastery.StaleModelVersionError):
        mastery.retrievability(stale, T0 + timedelta(days=1))
    with pytest.raises(mastery.StaleModelVersionError):
        mastery.check_version(stale)


def test_summary_counts_states() -> None:
    estimates = {
        "a": KnowledgeEstimate(objective_id="a", phase="acquiring", model_version=mastery.MODEL_VERSION),
        "b": KnowledgeEstimate(
            objective_id="b",
            phase="retaining",
            model_version=mastery.MODEL_VERSION,
            stability_days=1.0,
            last_evidence_at=T0,
        ),
    }
    counts = mastery.summary(estimates, T0 + timedelta(days=30))
    assert counts["acquiring"] == 1
    assert counts["retaining"] == 1
    assert counts["needs_review"] == 1


def test_explain_is_plain_language_and_mentions_missing_evidence() -> None:
    estimate = mastery.replay([record(0, "success")])["py:values"]
    message = mastery.explain(estimate, T0 + timedelta(days=1), "Variables")
    assert "2 more unassisted correct answer(s)" in message
    assert "3 days later" in message


def test_replay_groups_by_objective() -> None:
    other = EvidenceRecord(
        id="evd_x",
        objective_id="py:strings",
        outcome="success",
        occurred_at=T0,
    )
    estimates = mastery.replay([record(0, "success"), other])
    assert set(estimates) == {"py:values", "py:strings"}
