"""Baseline security behaviours that must not regress."""

from __future__ import annotations

import re
from pathlib import Path

import pytest
from pydantic import ValidationError

from app.config import Settings
from app.security import hash_password, password_problems, verify_password

REPO_ROOT = Path(__file__).resolve().parents[2]
BACKEND_ROOT = REPO_ROOT / "backend"


@pytest.fixture(autouse=True)
def _no_ambient_env(monkeypatch):
    for key in [key for key in __import__("os").environ if key.startswith("TALIMGO_")]:
        monkeypatch.delenv(key, raising=False)


# --- passwords -----------------------------------------------------------------------


def test_passwords_are_hashed_with_bcrypt_and_salted() -> None:
    first = hash_password("a-long-password")
    second = hash_password("a-long-password")
    assert first != second, "the same password must not hash identically twice"
    assert first.startswith("$2"), "bcrypt hash format expected"
    assert "a-long-password" not in first
    assert verify_password("a-long-password", first) is True
    assert verify_password("a-long-passwerd", first) is False


def test_verify_password_never_raises_on_a_malformed_hash() -> None:
    assert verify_password("anything", "not-a-hash") is False
    assert verify_password("anything", "") is False


def test_password_policy_reports_actionable_problems() -> None:
    settings = Settings(env="test", _env_file=None)
    assert password_problems("short", settings)
    assert password_problems("password", settings)
    assert password_problems(" leading-and-trailing ", settings)
    assert password_problems("a-perfectly-fine-passphrase", settings) == []


# --- configuration -------------------------------------------------------------------


def test_production_requires_a_strong_session_secret() -> None:
    with pytest.raises(ValidationError) as excinfo:
        Settings(
            env="production", session_secret="dev-only-insecure-session-secret-change-me", _env_file=None
        )
    assert "session_secret" in str(excinfo.value).lower() or "secret" in str(excinfo.value).lower()


def test_production_accepts_a_long_secret() -> None:
    settings = Settings(env="production", session_secret="x" * 48, _env_file=None)
    assert settings.env == "production"


def test_wildcard_cors_origin_is_refused() -> None:
    with pytest.raises(ValidationError):
        Settings(env="test", allowed_origins="*", _env_file=None)


def test_cors_allows_only_configured_origins(client) -> None:
    allowed = client.options(
        "/api/health",
        headers={"Origin": "http://localhost:5173", "Access-Control-Request-Method": "GET"},
    )
    assert allowed.headers.get("access-control-allow-origin") == "http://localhost:5173"

    disallowed = client.options(
        "/api/health",
        headers={"Origin": "https://evil.example", "Access-Control-Request-Method": "GET"},
    )
    assert disallowed.headers.get("access-control-allow-origin") is None


# --- responses and logs --------------------------------------------------------------


def test_validation_errors_name_fields_but_never_echo_values(client) -> None:
    secret = "super-secret-value-1234567890"
    response = client.post(
        "/api/auth/register",
        json={"email": "not-an-email", "password": secret, "display_name": "x", "accept_terms": True},
    )
    assert response.status_code == 422
    assert secret not in response.text
    assert "email" in response.text


def test_unauthenticated_errors_do_not_leak_internal_details(client) -> None:
    response = client.get("/api/auth/me")
    assert response.status_code == 401
    assert "Traceback" not in response.text
    assert "sqlalchemy" not in response.text.lower()


def test_docs_are_available_in_development(client) -> None:
    assert client.get("/api/openapi.json").status_code == 200


def test_security_headers_are_not_missing_silently(client) -> None:
    """Documents current behaviour: the API does not yet send hardening headers.

    This test fails as soon as headers are added, forcing the documentation to be updated with it.
    """
    response = client.get("/api/health")
    assert response.headers.get("x-content-type-options") is None
    assert response.status_code == 200


# --- repository hygiene ----------------------------------------------------------------

SECRET_PATTERNS = [
    re.compile(r"sk-[A-Za-z0-9]{20,}"),  # generic API keys
    re.compile(r"AKIA[0-9A-Z]{16}"),  # AWS access key id
    re.compile(r"-----BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    re.compile(r"ghp_[A-Za-z0-9]{20,}"),  # GitHub tokens
]

TEXT_SUFFIXES = {
    ".py",
    ".ts",
    ".tsx",
    ".js",
    ".json",
    ".yml",
    ".yaml",
    ".toml",
    ".md",
    ".html",
    ".css",
    ".env",
}


def test_no_credential_shaped_strings_are_committed() -> None:
    offenders: list[str] = []
    for path in REPO_ROOT.rglob("*"):
        if not path.is_file() or path.suffix not in TEXT_SUFFIXES:
            continue
        if any(part in {".git", "node_modules", ".venv", "dist", "build"} for part in path.parts):
            continue
        if path.name == "test_security_basics.py":
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        for pattern in SECRET_PATTERNS:
            if pattern.search(text):
                offenders.append(f"{path.relative_to(REPO_ROOT)}: {pattern.pattern}")
    assert offenders == [], f"credential-shaped strings found: {offenders}"


def test_gitignore_covers_secrets_and_local_data() -> None:
    text = (REPO_ROOT / ".gitignore").read_text(encoding="utf-8")
    for entry in (".env", "*.db", "node_modules/", ".venv/"):
        assert entry in text


def test_error_responses_are_json_with_a_detail_field(client) -> None:
    response = client.get("/api/plans/active")
    assert response.status_code == 401
    assert isinstance(response.json().get("detail"), str)


def test_health_endpoint_exposes_no_configuration(client) -> None:
    body = client.get("/api/health").json()
    assert set(body) == {"status", "version"}


def test_ai_health_reports_policy_without_secrets(client) -> None:
    body = client.get("/api/health/ai").json()
    assert body["policy"] == "local-only"
    assert "ai_base_url" not in body and "endpoint" not in body
    assert body["ai_enabled"] is False
