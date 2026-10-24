"""Per-IP registration rate limiting: response contract, allowance accounting and window behaviour."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy import select

from app.config import get_settings
from app.db import session_scope
from app.models import RegistrationAttempt, User
from app.security import registration_retry_after
from app.services import accounts

REGISTRATION_BODY = {
    "password": "a-long-enough-password",
    "display_name": "Rate Limited",
    "accept_terms": True,
    "accept_ai_processing": False,
}


def _register(client, email: str, **overrides) -> object:
    return client.post("/api/auth/register", json={**REGISTRATION_BODY, "email": email, **overrides})


def _user_count() -> int:
    with session_scope() as db:
        return len(list(db.scalars(select(User.id))))


def test_registrations_from_one_ip_are_limited(client_factory) -> None:
    client = client_factory(TALIMGO_REGISTRATIONS_PER_IP_PER_HOUR=2)
    assert _register(client, "first@example.com").status_code == 201
    assert _register(client, "second@example.com").status_code == 201

    limited = _register(client, "third@example.com")
    assert limited.status_code == 429, limited.text
    assert 1 <= int(limited.headers["Retry-After"]) <= 3600
    assert "too many accounts" in limited.json()["detail"].lower()
    assert _user_count() == 2, "a refused registration must not create an account"


def test_refused_registrations_consume_no_extra_allowance(client_factory) -> None:
    client = client_factory(TALIMGO_REGISTRATIONS_PER_IP_PER_HOUR=1)
    assert _register(client, "first@example.com").status_code == 201
    assert _register(client, "second@example.com").status_code == 429

    with session_scope() as db:
        recorded = len(list(db.scalars(select(RegistrationAttempt.id))))
    assert recorded == 1, "the refused request itself must not be counted"


def test_failed_registration_attempts_consume_the_allowance(client_factory) -> None:
    client = client_factory(TALIMGO_REGISTRATIONS_PER_IP_PER_HOUR=1)
    refused = _register(client, "first@example.com", accept_terms=False)
    assert refused.status_code == 400

    limited = _register(client, "second@example.com")
    assert limited.status_code == 429, limited.text
    assert _user_count() == 0, "the failed attempt was counted even though no account exists"


def test_registration_limit_is_per_ip(client_factory) -> None:
    client_factory(TALIMGO_REGISTRATIONS_PER_IP_PER_HOUR=1)
    settings = get_settings()

    def attempt(ip: str, email: str) -> None:
        with session_scope() as db:
            accounts.register_user(
                db,
                settings,
                ip=ip,
                email=email,
                password="a-long-enough-password",
                display_name="Per IP",
                accept_terms=True,
                accept_ai_processing=False,
            )

    attempt("203.0.113.10", "one@example.com")
    with pytest.raises(accounts.RegistrationRateLimited):
        attempt("203.0.113.10", "two@example.com")
    attempt("198.51.100.22", "three@example.com")


def test_rolling_window_and_retry_after_are_derived_from_the_oldest_attempt(client) -> None:
    settings = get_settings()
    moment = datetime(2026, 10, 24, 12, 0, 0, tzinfo=UTC)
    with session_scope() as db:
        for _ in range(settings.registrations_per_ip_per_hour):
            db.add(RegistrationAttempt(ip="203.0.113.10", attempted_at=moment - timedelta(minutes=30)))
        db.commit()

    with session_scope() as db:
        limited = registration_retry_after(db, ip="203.0.113.10", settings=settings, now=moment)
        other = registration_retry_after(db, ip="198.51.100.22", settings=settings, now=moment)

    assert limited == 30 * 60 + 1, "Retry-After waits for the oldest attempt to leave the window"
    assert other is None, "an IP under the cap is never limited"

    with session_scope() as db:
        rolled = registration_retry_after(
            db, ip="203.0.113.10", settings=settings, now=moment + timedelta(minutes=31)
        )
    assert rolled is None, "attempts older than the window no longer count"


def test_registration_and_login_policies_stay_independent(client_factory) -> None:
    client = client_factory(TALIMGO_REGISTRATIONS_PER_IP_PER_HOUR=1)
    assert _register(client, "first@example.com").status_code == 201
    assert _register(client, "second@example.com").status_code == 429

    login = client.post(
        "/api/auth/login", json={"email": "first@example.com", "password": "a-long-enough-password"}
    )
    assert login.status_code == 200, login.text
