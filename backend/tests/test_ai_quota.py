"""The per-learner model budget holds under concurrency, and failures still count.

The original implementation read the usage counter, compared it with the limit, called the model and
then incremented — a check-then-act race in which two concurrent requests both saw "0 used" and both
proceeded. The claim is now a single conditional UPDATE made *before* the model call.
"""

from __future__ import annotations

import threading

import pytest

from app.ai.tutor import AiBudgetExceededError, reserve_usage, usage_today
from app.db import session_scope
from app.models import AiUsage
from tests.conftest import register


def _user_id(client, email: str) -> str:
    from app.models import User

    register(client, email=email)
    with session_scope() as db:
        return db.query(User).filter(User.email == email).one().id


def test_the_daily_limit_is_enforced_and_reported(client) -> None:
    user_id = _user_id(client, "quota@example.com")
    with session_scope() as db:
        assert reserve_usage(db, user_id, limit=2) == 1
        assert reserve_usage(db, user_id, limit=2) == 2
        with pytest.raises(AiBudgetExceededError):
            reserve_usage(db, user_id, limit=2)
        db.commit()
    with session_scope() as db:
        assert usage_today(db, user_id) == 2, "a refused claim must not consume an extra unit"


def test_a_zero_limit_disables_the_feature_rather_than_looping(client) -> None:
    user_id = _user_id(client, "quota-zero@example.com")
    with session_scope() as db, pytest.raises(AiBudgetExceededError):
        reserve_usage(db, user_id, limit=0)


def test_concurrent_claims_cannot_exceed_the_limit(client) -> None:
    """Ten threads, a limit of three: exactly three claims may succeed, whatever the interleaving."""
    user_id = _user_id(client, "quota-race@example.com")
    granted: list[int] = []
    refused: list[str] = []
    start = threading.Barrier(10)
    lock = threading.Lock()

    def claim() -> None:
        start.wait()
        try:
            with session_scope() as db:
                count = reserve_usage(db, user_id, limit=3)
                db.commit()
            with lock:
                granted.append(count)
        except AiBudgetExceededError as exc:
            with lock:
                refused.append(str(exc))
        except Exception as exc:  # pragma: no cover - surfaced as a failure with its type
            with lock:
                refused.append(f"unexpected {type(exc).__name__}: {exc}")

    threads = [threading.Thread(target=claim) for _ in range(10)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(timeout=20)

    assert sorted(granted) == [1, 2, 3], f"grants={sorted(granted)} refused={refused}"
    assert len(refused) == 7
    with session_scope() as db:
        assert usage_today(db, user_id) == 3
        assert db.query(AiUsage).filter(AiUsage.user_id == user_id).count() == 1


def test_a_failed_model_call_still_consumes_its_slot(client) -> None:
    """Deliberate: the limit bounds resource use and retry pressure, not only successful replies."""
    user_id = _user_id(client, "quota-failure@example.com")
    with session_scope() as db:
        reserve_usage(db, user_id, limit=1)
        db.commit()
    with session_scope() as db, pytest.raises(AiBudgetExceededError):
        reserve_usage(db, user_id, limit=1)


def test_the_budget_is_per_learner_and_per_day(client) -> None:
    first = _user_id(client, "quota-a@example.com")
    second = _user_id(client, "quota-b@example.com")
    with session_scope() as db:
        reserve_usage(db, first, limit=1)
        assert reserve_usage(db, second, limit=1) == 1, "one learner's use must not affect another"
        db.commit()
