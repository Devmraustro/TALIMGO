"""Tests for the production preflight script.

The script reads the same settings object the API uses, so these tests point it at a temporary
environment. The production requirements mirror docs/DEPLOYMENT.md; the database check is the one the
application itself does not enforce, which is why it is asserted here.
"""

from __future__ import annotations

import pytest

from app.config import reset_settings_cache
from tests.test_postgres_scripts import load_script

preflight = load_script("check_production_config")

# Clearly not a deployable value: this string only exercises the configuration checker.
STRONG_SECRET = "preflight-test-secret-not-for-any-deployment"
POSTGRES_URL = "postgresql+psycopg://talimgo:not-a-real-password@db.internal:5432/talimgo"


@pytest.fixture
def production_env(monkeypatch: pytest.MonkeyPatch):
    def apply(**overrides: str) -> None:
        values = {
            "TALIMGO_ENV": "production",
            "TALIMGO_SESSION_SECRET": STRONG_SECRET,
            "TALIMGO_DATABASE_URL": POSTGRES_URL,
            "TALIMGO_ALLOWED_ORIGINS": "https://talimgo.example",
            "TALIMGO_AI_ENABLED": "false",
        }
        values.update(overrides)
        for name, value in values.items():
            monkeypatch.setenv(name, value)
        # `get_settings` caches per process, exactly as it does in the API; a script run gets a fresh
        # process, so the test must clear the cache to observe each environment.
        reset_settings_cache()

    return apply


def test_a_correct_production_environment_passes(production_env, capsys) -> None:
    production_env()
    preflight.main()
    output = capsys.readouterr().out
    assert "preflight passed" in output
    assert output.count("FAIL") == 0


def test_a_sqlite_production_database_is_refused(production_env, capsys) -> None:
    """The application allows it; the preflight does not, because docs require PostgreSQL 14+."""
    production_env(TALIMGO_DATABASE_URL="sqlite:///./talimgo.db")
    with pytest.raises(SystemExit) as refused:
        preflight.main()
    assert "FAILED" in str(refused.value)
    assert "development convenience only" in capsys.readouterr().out


def test_a_development_environment_is_refused(production_env, capsys) -> None:
    production_env(TALIMGO_ENV="development")
    with pytest.raises(SystemExit):
        preflight.main()
    assert "not a production environment" in capsys.readouterr().out


def test_a_placeholder_secret_is_refused(production_env, capsys) -> None:
    """The application's own validator rejects the development secret before the preflight's check."""
    production_env(TALIMGO_SESSION_SECRET="dev-only-insecure-session-secret-change-me")
    with pytest.raises(SystemExit):
        preflight.main()
    assert "startup configuration rejected" in capsys.readouterr().out


@pytest.mark.parametrize("secret", ["short-one", "change-me-please-change-me-0123456789", STRONG_SECRET])
def test_the_secret_checker_applies_the_documented_rule(secret: str, capsys) -> None:
    passed = preflight.check_session_secret(secret)
    output = capsys.readouterr().out
    assert passed is (secret == STRONG_SECRET)
    assert secret not in output, "the checker must never echo the value it is judging"


def test_a_wildcard_origin_is_refused_by_the_application_validator(production_env, capsys) -> None:
    production_env(TALIMGO_ALLOWED_ORIGINS="*")
    with pytest.raises(SystemExit) as refused:
        preflight.main()
    assert "startup configuration rejected" in f"{refused.value} {capsys.readouterr().out}"


def test_ai_enabled_without_a_model_is_refused(production_env, capsys) -> None:
    production_env(
        TALIMGO_AI_ENABLED="true", TALIMGO_AI_MODEL="", TALIMGO_AI_BASE_URL="http://127.0.0.1:11434"
    )
    with pytest.raises(SystemExit):
        preflight.main()
    assert "startup configuration rejected" in capsys.readouterr().out


def test_ai_enabled_against_a_non_local_endpoint_is_refused(production_env, capsys) -> None:
    production_env(
        TALIMGO_AI_ENABLED="true",
        TALIMGO_AI_MODEL="llama3.1:8b-instruct-q4_K_M",
        TALIMGO_AI_BASE_URL="https://api.openai.com-free-proxy.example/v1",
    )
    with pytest.raises(SystemExit):
        preflight.main()
    assert "startup configuration rejected" in capsys.readouterr().out


def test_ai_enabled_with_a_local_runtime_passes(production_env, capsys) -> None:
    production_env(
        TALIMGO_AI_ENABLED="true",
        TALIMGO_AI_MODEL="llama3.1:8b-instruct-q4_K_M",
        TALIMGO_AI_BASE_URL="http://127.0.0.1:11434",
    )
    preflight.main()
    assert "local-only AI" in capsys.readouterr().out


def test_no_secret_values_appear_in_the_output(production_env, capsys) -> None:
    """The output is meant to be pasteable into a ticket, so it must never echo a value."""
    production_env(
        TALIMGO_SESSION_SECRET=STRONG_SECRET,
        TALIMGO_AI_ENABLED="true",
        TALIMGO_AI_MODEL="llama3.1:8b-instruct-q4_K_M",
        TALIMGO_AI_BASE_URL="http://127.0.0.1:11434",
    )
    preflight.main()
    output = capsys.readouterr().out
    assert STRONG_SECRET not in output
    assert "not-a-real-password" not in output  # the password inside the database URL
    assert "talimgo:not-a-real" not in output
