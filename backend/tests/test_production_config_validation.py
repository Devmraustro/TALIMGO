"""Production configuration must fail closed before the database engine is constructed."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from app.config import Settings

_STRONG_TEST_SECRET = "test-only-session-secret-not-for-any-deployment"
_POSTGRES_URL = "postgresql+psycopg://talimgo:not-a-real-password@db.internal:5432/talimgo"


def _production_settings(**overrides: str) -> Settings:
    values: dict[str, str] = {
        "env": "production",
        "session_secret": _STRONG_TEST_SECRET,
        "database_url": _POSTGRES_URL,
        "allowed_origins": "https://talimgo.example",
    }
    values.update(overrides)
    return Settings(_env_file=None, **values)


def test_production_accepts_a_postgresql_database(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("VERCEL_ENV", raising=False)
    settings = _production_settings()
    assert settings.env == "production"
    assert settings.database_url == _POSTGRES_URL


@pytest.mark.parametrize("database_url", ["sqlite:///./talimgo.db", "not a valid database URL"])
def test_production_rejects_non_postgresql_database_urls(
    monkeypatch: pytest.MonkeyPatch, database_url: str
) -> None:
    monkeypatch.delenv("VERCEL_ENV", raising=False)
    with pytest.raises(ValidationError, match="TALIMGO_DATABASE_URL"):
        _production_settings(database_url=database_url)


def test_vercel_production_requires_explicit_talimgo_production_mode(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("VERCEL_ENV", "production")
    with pytest.raises(ValidationError, match="TALIMGO_ENV must be explicitly set to production"):
        Settings(_env_file=None, env="development")


def test_vercel_preview_can_use_the_isolated_development_database(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("VERCEL_ENV", "preview")
    settings = Settings(_env_file=None, env="development", database_url="sqlite:///./preview.db")
    assert settings.env == "development"
    assert settings.database_url == "sqlite:///./preview.db"
