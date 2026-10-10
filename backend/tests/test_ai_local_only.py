"""The local-only AI guarantee.

These tests exist to make the policy mechanical rather than aspirational:
  1. configuration rejects every non-local endpoint;
  2. a tutor request reaches exactly one HTTP call, and it goes to the configured local endpoint;
  3. when the local runtime is unavailable, the API fails explicitly and contacts nothing else;
  4. no forbidden provider host or SDK appears anywhere in the repository.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from urllib.parse import urlparse

import httpx
import pytest

from app.ai.adapter import LocalModelClient, LocalModelUnavailable
from app.ai.policy import FORBIDDEN_HOST_SUFFIXES, NonLocalEndpointError, assert_local_endpoint, is_local_host
from app.config import Settings

REPO_ROOT = Path(__file__).resolve().parents[2]
BACKEND_ROOT = REPO_ROOT / "backend"

LOCAL_ENDPOINTS = [
    "http://127.0.0.1:11434",
    "http://localhost:8000",
    "http://[::1]:8080",
    "http://10.1.2.3:8000",
    "http://192.168.0.42:11434",
    "http://172.16.5.9:8000",
]

HOSTED_ENDPOINTS = [
    "https://api.openai.com",
    "https://api.openai.com/v1",
    "https://api.anthropic.com",
    "https://generativelanguage.googleapis.com",
    "https://us-central1-aiplatform.googleapis.com",
    "https://api.groq.com/openai",
    "https://api.cohere.ai",
    "https://api.mistral.ai",
    "https://api.together.xyz",
    "https://api.replicate.com",
    "https://huggingface.co",
    "https://bedrock-runtime.us-east-1.amazonaws.com",
    "http://example.com:11434",
    "http://127.0.0.1.evil.example.com",
    "http://localhost.attacker.example",
]


@pytest.mark.parametrize("endpoint", LOCAL_ENDPOINTS)
def test_local_endpoints_are_accepted(endpoint: str) -> None:
    assert assert_local_endpoint(endpoint) == endpoint.rstrip("/")


@pytest.mark.parametrize("endpoint", HOSTED_ENDPOINTS)
def test_non_local_endpoints_are_rejected(endpoint: str) -> None:
    with pytest.raises(NonLocalEndpointError):
        assert_local_endpoint(endpoint)


@pytest.mark.parametrize("bad", ["", "   ", "ftp://127.0.0.1", "not-a-url", "http://", "file:///etc/passwd"])
def test_malformed_endpoints_fail_closed(bad: str) -> None:
    with pytest.raises(NonLocalEndpointError):
        assert_local_endpoint(bad)


def test_every_known_provider_suffix_is_reachable_by_the_checker() -> None:
    for suffix in FORBIDDEN_HOST_SUFFIXES:
        with pytest.raises(NonLocalEndpointError):
            assert_local_endpoint(f"https://api.{suffix}")


def test_is_local_host_classification() -> None:
    assert is_local_host("127.0.0.1")
    assert is_local_host("::1")
    assert is_local_host("10.0.0.5")
    assert is_local_host("localhost")
    assert not is_local_host("8.8.8.8")
    assert not is_local_host("api.openai.com")
    assert not is_local_host("")


def test_settings_refuse_a_hosted_endpoint_when_ai_is_enabled() -> None:
    with pytest.raises(Exception) as excinfo:
        Settings(
            env="test",
            ai_enabled=True,
            ai_model="some-model",
            ai_base_url="https://api.openai.com/v1",
            _env_file=None,
        )
    assert "prohibited" in str(excinfo.value).lower() or "local" in str(excinfo.value).lower()


def test_settings_accept_a_local_endpoint(clean_env) -> None:
    settings = Settings(
        env="test",
        ai_enabled=True,
        ai_model="local-model",
        ai_base_url="http://127.0.0.1:11434",
        _env_file=None,
    )
    assert settings.ai_base_url == "http://127.0.0.1:11434"


def test_client_rejects_an_endpoint_that_becomes_remote() -> None:
    settings = Settings(
        env="test", ai_enabled=True, ai_model="m", ai_base_url="http://127.0.0.1:11434", _env_file=None
    )
    client = LocalModelClient(settings)
    client._endpoint = "https://api.anthropic.com"  # simulate tampering with the resolved endpoint
    with pytest.raises(NonLocalEndpointError):
        client.generate(
            __import__("app.ai.adapter", fromlist=["ModelRequest"]).ModelRequest(
                messages=[
                    __import__("app.ai.adapter", fromlist=["ModelMessage"]).ModelMessage(
                        role="user", content="hi"
                    )
                ]
            )
        )


def _settings(**overrides) -> Settings:
    base = {
        "env": "test",
        "ai_enabled": True,
        "ai_model": "local-test-model",
        "ai_base_url": "http://127.0.0.1:11434",
        "ai_dialect": "ollama",
        "_env_file": None,
    }
    base.update(overrides)
    return Settings(**base)


def test_generate_calls_only_the_configured_local_endpoint() -> None:
    seen: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(request)
        return httpx.Response(
            200,
            json={
                "model": "local-test-model",
                "message": {"role": "assistant", "content": '{"reply": "ok"}'},
            },
        )

    from app.ai.adapter import ModelMessage, ModelRequest

    client = LocalModelClient(_settings(), transport=httpx.MockTransport(handler))
    response = client.generate(ModelRequest(messages=[ModelMessage(role="user", content="explain loops")]))

    assert len(seen) == 1, "exactly one request must be made"
    assert str(seen[0].url).startswith("http://127.0.0.1:11434/"), "the request must go to the local endpoint"
    assert urlparse(str(seen[0].url)).hostname == "127.0.0.1"
    assert response.text == '{"reply": "ok"}'


def test_openai_compatible_dialect_also_stays_local() -> None:
    seen: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(request)
        return httpx.Response(200, json={"choices": [{"message": {"content": "hello"}}]})

    from app.ai.adapter import ModelMessage, ModelRequest

    client = LocalModelClient(
        _settings(ai_dialect="openai_compatible"), transport=httpx.MockTransport(handler)
    )
    client.generate(ModelRequest(messages=[ModelMessage(role="user", content="hi")], json_mode=True))

    assert len(seen) == 1
    assert str(seen[0].url) == "http://127.0.0.1:11434/v1/chat/completions"
    assert seen[0].headers.get("x-ollama-telemetry") == "disabled", "optional runtime telemetry is disabled"


def test_unavailable_local_runtime_raises_and_contacts_nothing_else() -> None:
    attempts: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        attempts.append(request)
        raise httpx.ConnectError("connection refused", request=request)

    from app.ai.adapter import ModelMessage, ModelRequest

    client = LocalModelClient(_settings(), transport=httpx.MockTransport(handler))
    with pytest.raises(LocalModelUnavailable):
        client.generate(ModelRequest(messages=[ModelMessage(role="user", content="hi")]))

    assert len(attempts) == 1
    assert urlparse(str(attempts[0].url)).hostname == "127.0.0.1", "no alternative host is tried"


def test_http_error_from_runtime_is_reported_not_hidden() -> None:
    from app.ai.adapter import LocalModelResponseError, ModelMessage, ModelRequest

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(500, text="model not loaded")

    client = LocalModelClient(_settings(), transport=httpx.MockTransport(handler))
    with pytest.raises(LocalModelResponseError):
        client.generate(ModelRequest(messages=[ModelMessage(role="user", content="hi")]))


# --------------------------------------------------------------------------------------
# Repository-level prohibition
# --------------------------------------------------------------------------------------

FORBIDDEN_TOKENS = (
    "openai",
    "anthropic",
    "generativelanguage",
    "vertexai",
    "cohere",
    "mistralai",
    "groq",
    "together.xyz",
    "replicate.com",
    "huggingface_hub",
    "bedrock",
)

# Files that legitimately name the prohibited providers because they *enforce* the ban.
ALLOWED = {
    "backend/app/ai/policy.py",
    "backend/tests/test_ai_local_only.py",
    "backend/tests/conftest.py",
    ".github/workflows/ci.yml",
    "AGENTS.md",
    "docs/OPEN_SOURCE_REUSE_AUDIT.md",
    ".env.example",
}

FORBIDDEN_SDK_IMPORTS = re.compile(
    r"^\s*(?:import|from)\s+(openai|anthropic|google\.generativeai|google\.genai|cohere|mistralai|groq|replicate)\b",
    re.MULTILINE,
)


def _python_sources() -> list[Path]:
    return list((BACKEND_ROOT / "app").rglob("*.py"))


def test_no_forbidden_sdk_imports_in_application_code() -> None:
    offenders = []
    for path in _python_sources():
        text = path.read_text(encoding="utf-8")
        if FORBIDDEN_SDK_IMPORTS.search(text):
            offenders.append(str(path.relative_to(REPO_ROOT)))
    assert offenders == [], f"forbidden provider SDK imported in: {offenders}"


def _normalise_for_scan(text: str) -> str:
    """Remove legitimate references before scanning.

    `openai_compatible` is the name of a *local wire format* supported by vLLM and llama.cpp server;
    it is not a provider integration. Everything else that mentions a provider is a violation.
    """
    for allowed_phrase in ("openai_compatible", "openai-compatible", "openai compatible"):
        text = text.replace(allowed_phrase, "local_dialect")
    return text


def test_no_forbidden_hosts_in_application_code() -> None:
    offenders = []
    for path in _python_sources():
        relative = str(path.relative_to(REPO_ROOT))
        if relative in ALLOWED:
            continue
        text = _normalise_for_scan(path.read_text(encoding="utf-8").lower())
        for token in FORBIDDEN_TOKENS:
            if token in text:
                offenders.append(f"{relative}:{token}")
    assert offenders == [], f"hosted provider reference found in application code: {offenders}"


def test_dependencies_declare_no_provider_sdks() -> None:
    pyproject = (BACKEND_ROOT / "pyproject.toml").read_text(encoding="utf-8").lower()
    manifest = json.loads((REPO_ROOT / "frontend" / "package.json").read_text(encoding="utf-8"))
    frontend_deps = " ".join(
        {**manifest.get("dependencies", {}), **manifest.get("devDependencies", {})}
    ).lower()

    for token in (
        "openai",
        "anthropic",
        "google-generativeai",
        "google-genai",
        "cohere",
        "mistralai",
        "groq",
    ):
        assert token not in pyproject, f"{token} declared in backend dependencies"
        assert token not in frontend_deps, f"{token} declared in frontend dependencies"


def test_policy_module_is_the_only_place_that_lists_provider_hosts() -> None:
    """A second list of provider hosts elsewhere would be a maintenance hazard."""
    hits = []
    for path in _python_sources():
        text = path.read_text(encoding="utf-8")
        if "FORBIDDEN_HOST_SUFFIXES" in text and path.name != "policy.py":
            hits.append(path.name)
    assert hits == []


def test_api_fails_explicitly_when_ai_is_disabled(client) -> None:
    from tests.conftest import create_goal, register

    register(client)
    goal = create_goal(client)
    response = client.post(
        "/api/tutor/ask",
        json={"objective_id": "py:values", "question": "Why is 7/2 a float?"},
    )
    assert response.status_code == 503
    assert (
        "disabled" in response.json()["detail"].lower() or "switched off" in response.json()["detail"].lower()
    )
    del goal
