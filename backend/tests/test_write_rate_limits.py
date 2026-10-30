"""Authenticated write-rate limiting: window boundaries, response behaviour and isolation."""

from __future__ import annotations

import threading
from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy import select

from app.db import session_scope
from app.models import User
from app.request_rate_limits import WriteRateLimitExceeded, reserve_write_request_committed
from tests.conftest import register


def test_authenticated_mutations_are_limited_but_reads_are_not(client_factory) -> None:
    client = client_factory(TALIMGO_WRITE_RATE_LIMIT_PER_MINUTE=2)
    register(client)

    assert client.get("/api/me/profile").status_code == 200
    first = client.patch("/api/me/profile", json={"locale": "ar"})
    second = client.patch("/api/me/profile", json={"weekly_minutes": 300})
    assert first.status_code == 200, first.text
    assert second.status_code == 200, second.text

    limited = client.patch("/api/me/profile", json={"weekly_minutes": 360})
    assert limited.status_code == 429, limited.text
    assert 1 <= int(limited.headers["Retry-After"]) <= 60
    assert "too quickly" in limited.json()["detail"].lower()
    # Reads remain available during a mutation window.
    assert client.get("/api/me/profile").status_code == 200


def test_write_limit_is_per_learner_not_per_browser(client_factory) -> None:
    client = client_factory(TALIMGO_WRITE_RATE_LIMIT_PER_MINUTE=1)
    register(client, email="write-limit-first@example.com")
    first_cookie = client.cookies.get("talimgo_session")
    assert first_cookie
    register(client, email="write-limit-second@example.com")
    second_cookie = client.cookies.get("talimgo_session")
    assert second_cookie and second_cookie != first_cookie

    client.cookies.clear()
    client.cookies.set("talimgo_session", first_cookie)
    assert client.patch("/api/me/profile", json={"locale": "ar"}).status_code == 200
    assert client.patch("/api/me/profile", json={"locale": "en"}).status_code == 429

    client.cookies.clear()
    client.cookies.set("talimgo_session", second_cookie)
    allowed = client.patch("/api/me/profile", json={"locale": "ar"})
    assert allowed.status_code == 200, allowed.text


def test_fixed_window_rolls_over_without_per_window_rows(client) -> None:
    register(client, email="write-window@example.com")
    with session_scope() as db:
        user_id = db.scalar(select(User.id).where(User.email == "write-window@example.com"))
    assert user_id

    moment = datetime(2026, 10, 11, 0, 0, 30, tzinfo=UTC)
    assert reserve_write_request_committed(user_id, limit=1, now=moment) == 1
    with pytest.raises(WriteRateLimitExceeded) as refused:
        reserve_write_request_committed(user_id, limit=1, now=moment + timedelta(seconds=10))
    assert refused.value.retry_after == 20

    # Crossing the UTC-minute boundary resets the counter atomically.
    assert reserve_write_request_committed(user_id, limit=1, now=moment + timedelta(seconds=30)) == 1


def test_concurrent_claims_cannot_exceed_the_per_learner_limit(client) -> None:
    """Ten independent sessions racing for three slots must not make more than three claims."""
    register(client, email="write-rate-race@example.com")
    with session_scope() as db:
        user_id = db.scalar(select(User.id).where(User.email == "write-rate-race@example.com"))
    assert user_id

    start = threading.Barrier(10)
    granted: list[int] = []
    refused: list[str] = []
    unexpected: list[str] = []
    result_lock = threading.Lock()

    def claim() -> None:
        start.wait()
        try:
            count = reserve_write_request_committed(user_id, limit=3)
            with result_lock:
                granted.append(count)
        except WriteRateLimitExceeded as exc:
            with result_lock:
                refused.append(str(exc))
        except Exception as exc:  # surfaced with type/message rather than silently counted as refusal
            with result_lock:
                unexpected.append(f"{type(exc).__name__}: {exc}")

    workers = [threading.Thread(target=claim) for _ in range(10)]
    for worker in workers:
        worker.start()
    for worker in workers:
        worker.join(timeout=20)

    assert all(not worker.is_alive() for worker in workers), "a concurrent claim did not return"
    assert not unexpected, unexpected
    assert sorted(granted) == [1, 1, 1], f"granted={granted}, refused={refused}"
    assert len(refused) == 7
    with session_scope() as db:
        row = db.get(User, user_id)
        assert row is not None
        assert row.write_rate_count == 3
