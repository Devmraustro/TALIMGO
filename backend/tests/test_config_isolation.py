"""Test-only configuration must not leak into production — and vice versa.

Pinned guarantees:

  * the documented production defaults are what an unmodified production configuration yields;
  * values above the schema's hard ceiling (the kind used to make tests fast) are refused outright,
    so a mis-scoped test override cannot silently become a production limit;
  * the test environment loads test configuration (``is_test``); development/production never do;
  * settings caching really is reset by ``reset_settings_cache``;
  * the 429 contract and the 401 contract hold under a tightened test configuration.
"""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from app.config import Settings, get_settings, reset_settings_cache

_PROD = {
    "env": "production",
    "session_secret": "prod-secret-0123456789abcdef0123456789abcdef",
    "database_url": "postgresql+psycopg://talimgo:x@127.0.0.1:5432/talimgo",
    "allowed_origins": "https://talimgo.example",
}


def _settings(**overrides) -> Settings:
    # ``_env_file=None`` and kwargs keep repo files and ambient env out of these assertions;
    # init kwargs also outrank any ambient TALIMGO_* the runner may export.
    return Settings(_env_file=None, **{**_PROD, **overrides})


def test_production_defaults_are_intact(clean_env, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("VERCEL_ENV", raising=False)
    settings = _settings()
    assert settings.write_rate_limit_per_minute == 120
    assert settings.registrations_per_ip_per_hour == 10
    assert settings.session_ttl_hours == 336
    assert settings.max_login_attempts == 8
    assert settings.login_lockout_minutes == 15
    assert settings.min_password_length == 10
    assert settings.ai_enabled is False, "AI must default to off"
    assert settings.max_request_bytes == 131_072
    assert settings.is_test is False


def test_schema_hard_ceiling_refuses_test_grade_overrides(clean_env, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("VERCEL_ENV", raising=False)
    with pytest.raises(ValidationError):
        _settings(write_rate_limit_per_minute=100_000)
    with pytest.raises(ValidationError):
        _settings(registrations_per_ip_per_hour=100_000)


def test_elevated_test_values_are_accepted_only_in_the_test_environment(
    clean_env, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.delenv("VERCEL_ENV", raising=False)
    test_settings = Settings(
        _env_file=None, env="test", write_rate_limit_per_minute=1000, registrations_per_ip_per_hour=1000
    )
    assert test_settings.is_test is True
    assert test_settings.write_rate_limit_per_minute == 1000
    # And production validation still refuses a SQLite database even with test values absent.
    with pytest.raises(ValidationError):
        _settings(database_url="sqlite:///./talimgo.db")


def test_development_and_production_are_never_marked_as_test(
    clean_env, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.delenv("VERCEL_ENV", raising=False)
    assert _settings(env="development", session_secret="x" * 33).is_test is False
    assert _settings().is_test is False


def test_settings_cache_is_reset_by_reset_settings_cache(clean_env, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("VERCEL_ENV", raising=False)
    monkeypatch.setenv("TALIMGO_WRITE_RATE_LIMIT_PER_MINUTE", "2")
    reset_settings_cache()
    try:
        first = get_settings()
        assert first.write_rate_limit_per_minute == 2
        monkeypatch.setenv("TALIMGO_WRITE_RATE_LIMIT_PER_MINUTE", "3")
        assert get_settings().write_rate_limit_per_minute == 2, "cached instance must be returned as-is"
        reset_settings_cache()
        assert get_settings().write_rate_limit_per_minute == 3
    finally:
        reset_settings_cache()


def test_low_write_limit_returns_429_and_invalid_auth_stays_401(client_factory) -> None:
    client = client_factory(TALIMGO_WRITE_RATE_LIMIT_PER_MINUTE=1)
    assert (
        client.post(
            "/api/auth/login", json={"email": "nobody@example.com", "password": "whatever-password"}
        ).status_code
        == 401
    )

    register_response = client.post(
        "/api/auth/register",
        json={
            "email": "tight@example.com",
            "password": "correct-horse-battery",
            "display_name": "Tight",
            "accept_terms": True,
            "accept_ai_processing": False,
        },
    )
    assert register_response.status_code == 201
    assert client.patch("/api/me/profile", json={"locale": "ar"}).status_code == 200
    limited = client.patch("/api/me/profile", json={"locale": "en"})
    assert limited.status_code == 429
    assert "retry-after" in {name.lower() for name in limited.headers}
    # The 429 body is the documented JSON shape; nothing about the resource is disclosed.
    assert limited.json() == {
        "detail": "You are sending changes too quickly. Please wait before trying again."
    }
    # Reads still work while writes are limited; invalid credentials still rejected.
    assert client.get("/api/me/profile").status_code == 200
    assert (
        client.post(
            "/api/auth/login", json={"email": "tight@example.com", "password": "wrong-password-xx"}
        ).status_code
        == 401
    )
