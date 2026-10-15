"""The starting check produces evidence, never mastery (ADR 0005, ADR 0006).

Regression: diagnostic evidence was folded into the mastery model, so three spaced correct
starting-check answers — or two starting-check failures — could move an objective to `retaining`
or demote one, without the learner ever practising it.
"""

from __future__ import annotations

import random
from datetime import UTC, datetime, timedelta

from fastapi.testclient import TestClient

from app.curriculum.registry import item_index
from app.learning import mastery
from app.learning.types import EvidenceRecord
from tests.conftest import create_goal, register

T0 = datetime(2026, 1, 1, 9, 0, tzinfo=UTC)


def record(day: float, outcome: str, *, kind: str = "practice", assisted: bool = False) -> EvidenceRecord:
    return EvidenceRecord(
        id=f"evd_{kind}_{int(day * 1000):06d}_{outcome}",
        objective_id="py:values",
        outcome=outcome,  # type: ignore[arg-type]
        occurred_at=T0 + timedelta(days=day),
        assisted=assisted,
        kind=kind,  # type: ignore[arg-type]
    )


def _spaced_diagnostic_successes() -> list[EvidenceRecord]:
    # Three unassisted successes with a >= 3-day gap: this promotes under the mastery fold.
    return [
        record(0, "success", kind="diagnostic"),
        record(0.5, "success", kind="diagnostic"),
        record(4, "success", kind="diagnostic"),
    ]


# --------------------------------------------------------------------------------------
# Pure model boundary
# --------------------------------------------------------------------------------------


def test_the_mastery_evidence_boundary_is_declared_explicitly() -> None:
    assert {"practice", "assessment", "project"} == mastery.MASTERY_EVIDENCE_KINDS
    assert mastery.affects_mastery("practice") is True
    assert mastery.affects_mastery("assessment") is True
    assert mastery.affects_mastery("project") is True
    assert mastery.affects_mastery("diagnostic") is False
    assert mastery.affects_mastery("something-unknown") is False


def test_three_spaced_diagnostic_successes_do_not_promote_to_retaining() -> None:
    records = _spaced_diagnostic_successes()
    assert mastery.replay([]) == {}, "control: the fold itself is not creating estimates from nothing"

    estimates = mastery.replay(records)
    assert estimates == {}, "diagnostic-only evidence must not create a mastery estimate"
    assert mastery.phase_for(estimates.get("py:values")) == "unseen"


def test_diagnostic_evidence_is_excluded_from_the_fold_entirely() -> None:
    records = [
        record(0, "success", kind="practice"),
        record(1, "success", kind="diagnostic"),
        record(4, "success", kind="practice"),
        record(5, "failure", kind="diagnostic"),
        record(9, "success", kind="practice"),
        record(30, "failure", kind="practice"),
    ]
    mixed = mastery.replay(records)
    without_diagnostics = mastery.replay([r for r in records if r.kind != "diagnostic"])

    assert mixed == without_diagnostics
    estimate = mixed["py:values"]
    assert estimate.unassisted_successes == 3
    assert estimate.phase == "retaining"
    assert estimate.failures_while_retaining == 1
    assert estimate.last_evidence_at == T0 + timedelta(days=30)


def test_diagnostic_failures_cannot_demote_a_retaining_objective() -> None:
    practice = [record(0, "success"), record(4, "success"), record(9, "success")]
    retaining = mastery.replay(practice)["py:values"]
    assert retaining.phase == "retaining"

    with_diagnostics = mastery.replay(
        [*practice, record(30, "failure", kind="diagnostic"), record(31, "failure", kind="diagnostic")]
    )["py:values"]
    assert with_diagnostics == retaining


def test_diagnostic_success_cannot_extend_stability_or_reset_review() -> None:
    practice = [record(0, "success"), record(4, "success"), record(9, "success")]
    estimate = mastery.replay(practice)["py:values"]
    later = mastery.replay([*practice, record(200, "success", kind="diagnostic")])["py:values"]

    assert later.stability_days == estimate.stability_days
    assert later.last_evidence_at == estimate.last_evidence_at
    moment = T0 + timedelta(days=400)
    assert mastery.retrievability(later, moment) == mastery.retrievability(estimate, moment)


def test_mixed_evidence_replay_is_deterministic_and_order_independent() -> None:
    records = [
        record(0, "success"),
        record(1, "failure", kind="diagnostic"),
        record(4, "success"),
        record(5, "success", assisted=True, kind="assessment"),
        record(9, "success"),
        record(12, "success", kind="project"),
        record(40, "failure"),
    ]
    first = mastery.replay(records)
    shuffled = records[:]
    random.Random(11).shuffle(shuffled)

    assert mastery.replay(records) == first
    assert mastery.replay(shuffled) == first
    assert first["py:values"].unassisted_successes == 4


# --------------------------------------------------------------------------------------
# Service boundary: cached estimates
# --------------------------------------------------------------------------------------


def _learner_with_completed_diagnostic(client: TestClient) -> tuple[str, dict]:
    user = register(client)
    goal = create_goal(client)
    from tests.conftest import answer_diagnostic_until_done

    answer_diagnostic_until_done(client, goal["id"], correct=True)
    return user["user"]["id"], goal


def test_a_diagnostic_only_learner_has_no_mastery_estimate(client: TestClient) -> None:
    _learner_with_completed_diagnostic(client)

    listed = client.get("/api/practice/progress/mastery")
    assert listed.status_code == 200, listed.text
    assert listed.json() == [], "a completed starting check must not produce mastery"

    dashboard = client.get("/api/dashboard")
    assert dashboard.status_code == 200, dashboard.text
    summary = dashboard.json()["mastery_summary"]
    assert summary["retaining"] == 0
    assert summary["acquiring"] == 0

    evidence = client.get("/api/practice/progress/evidence")
    assert evidence.status_code == 200
    kinds = {row["kind"] for row in evidence.json()}
    assert kinds == {"diagnostic"}, "diagnostic evidence must still be recorded and reported"


def test_provisional_confirmation_check_survives_without_mastery(client: TestClient) -> None:
    _user_id, goal = _learner_with_completed_diagnostic(client)

    generated = client.post(f"/api/plans/goals/{goal['id']}")
    assert generated.status_code in (200, 201), generated.text
    steps = [item for week in generated.json()["plan"]["weeks"] for item in week["items"]]
    provisional = [step for step in steps if step["kind"] == "assess"]

    assert provisional, "a hard correct diagnostic answer must still become a confirmation check"
    assert all(step["lesson_id"] is None for step in provisional), "E_ASSESS_WITH_LESSON"

    listed = client.get("/api/practice/progress/mastery").json()
    assert all(entry["phase"] != "retaining" for entry in listed)


def test_cached_estimates_from_the_old_fold_are_rebuilt_and_pruned(client: TestClient) -> None:
    from app.db import session_scope
    from app.models import MasteryEstimate

    user_id, _goal = _learner_with_completed_diagnostic(client)

    with session_scope() as db:
        db.add(
            MasteryEstimate(
                user_id=user_id,
                objective_id="py:values",
                model_version="mastery-v1",
                phase="retaining",
                unassisted_successes=3,
                has_delayed_success=True,
                stability_days=12.0,
                last_evidence_at=T0,
            )
        )
        db.commit()

    listed = client.get("/api/practice/progress/mastery")
    assert listed.status_code == 200, listed.text
    assert listed.json() == [], "a stale v1 estimate must be rebuilt from evidence, not trusted"

    # The read path rebuilds in memory; persisting the rebuild is the documented maintenance call.
    recomputed = client.post("/api/practice/progress/recompute")
    assert recomputed.status_code == 200, recomputed.text

    with session_scope() as db:
        rows = db.query(MasteryEstimate).filter(MasteryEstimate.user_id == user_id).all()
        assert rows == [], "the cache row the new fold no longer produces must be pruned"


def test_practice_backed_estimates_are_restamped_with_the_new_version(client: TestClient) -> None:
    from app.db import session_scope
    from app.models import MasteryEstimate

    user_id = register(client)["user"]["id"]
    objective_id = "py:values"

    started = client.post("/api/practice/sessions", json={"objective_id": objective_id, "size": 1})
    assert started.status_code == 201, started.text
    item = started.json()["item"]
    key = item_index("python-foundations")[item["id"]]["answer_key"]
    if item["kind"] == "mcq_single":
        payload = {"option_id": key["option_id"]}
    else:
        payload = {"text": key["accepted"][0]}
    answered = client.post(
        f"/api/practice/sessions/{started.json()['session_id']}/answers",
        json={"item_id": item["id"], "response": payload},
    )
    assert answered.status_code == 200, answered.text

    listed = client.get("/api/practice/progress/mastery").json()
    entry = next(row for row in listed if row["objective_id"] == objective_id)
    assert entry["phase"] == "acquiring"
    assert entry["unassisted_successes"] == 1

    with session_scope() as db:
        row = (
            db.query(MasteryEstimate)
            .filter(MasteryEstimate.user_id == user_id, MasteryEstimate.objective_id == objective_id)
            .one()
        )
        row.model_version = "mastery-v1"
        row.phase = "retaining"
        row.unassisted_successes = 9
        db.commit()

    rebuilt = client.get("/api/practice/progress/mastery").json()
    entry = next(row for row in rebuilt if row["objective_id"] == objective_id)
    assert entry["phase"] == "acquiring"
    assert entry["unassisted_successes"] == 1

    persisted = client.post("/api/practice/progress/recompute")
    assert persisted.status_code == 200, persisted.text

    with session_scope() as db:
        row = (
            db.query(MasteryEstimate)
            .filter(MasteryEstimate.user_id == user_id, MasteryEstimate.objective_id == objective_id)
            .one()
        )
        assert row.model_version == mastery.MODEL_VERSION
        assert row.phase == "acquiring"
        assert row.unassisted_successes == 1
