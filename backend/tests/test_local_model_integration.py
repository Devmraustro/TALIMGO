"""Offline integration test against a real local model runtime.

This file is the only place that talks to a real model. It is marked ``local_model`` and **skips**
with an explicit reason unless the environment provides one, so ordinary CI never downloads weights:

    TALIMGO_TEST_LOCAL_MODEL=1 \
    TALIMGO_AI_ENABLED=true \
    TALIMGO_AI_BASE_URL=http://127.0.0.1:11434 \
    TALIMGO_AI_MODEL=qwen2.5:3b-instruct \
    pytest -m local_model -q -rs

What it proves that mocks cannot:
  * the configured runtime is reachable and answers;
  * a real completion passes the same schema and policy validation the product uses;
  * the request goes to a local address and nothing else.

It does **not** prove model quality. Quality evaluation against a versioned item set is a separate
milestone (docs/LOCAL_AI_ARCHITECTURE.md §4).
"""

from __future__ import annotations

import json
import os
import socket
from urllib.parse import urlparse

import pytest

from app.ai.adapter import LocalModelClient, LocalModelUnavailable, ModelMessage, ModelRequest
from app.ai.policy import assert_local_endpoint
from app.ai.schemas import TutorOutputRejected, validate_tutor_reply
from app.ai.tutor import SYSTEM_PROMPT
from app.config import Settings

pytestmark = pytest.mark.local_model

ENABLED = os.environ.get("TALIMGO_TEST_LOCAL_MODEL") == "1"


def _reachable(url: str, timeout: float = 1.5) -> bool:
    parsed = urlparse(url)
    host = parsed.hostname or ""
    port = parsed.port or (443 if parsed.scheme == "https" else 80)
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


@pytest.fixture()
def live_settings() -> Settings:
    if not ENABLED:
        pytest.skip("set TALIMGO_TEST_LOCAL_MODEL=1 and configure a local runtime to run this test")
    base_url = os.environ.get("TALIMGO_AI_BASE_URL", "http://127.0.0.1:11434")
    model = os.environ.get("TALIMGO_AI_MODEL", "")
    if not model:
        pytest.skip("TALIMGO_AI_MODEL is not set; nothing to ask")
    assert_local_endpoint(base_url)  # fail loudly if someone points this at a hosted provider
    if not _reachable(base_url):
        pytest.skip(f"no local runtime listening at {base_url}")
    return Settings(
        env="test",
        ai_enabled=True,
        ai_model=model,
        ai_base_url=base_url,
        ai_dialect=os.environ.get("TALIMGO_AI_DIALECT", "ollama"),  # type: ignore[arg-type]
        _env_file=None,
    )


def test_real_local_model_returns_a_validatable_tutor_reply(live_settings: Settings) -> None:
    client = LocalModelClient(live_settings)
    system = SYSTEM_PROMPT.format(citations="objective:py:values")
    request = ModelRequest(
        messages=[
            ModelMessage(role="system", content=system),
            ModelMessage(
                role="user",
                content=(
                    "CONTEXT\n### Objective (py:values)\nVariables, values and types\n"
                    "Values have types: int, float, str, bool.\n\n"
                    "<learner_message>\nWhy is 7 / 2 a float?\n</learner_message>\n\n"
                    "Answer as the JSON object described in the instructions."
                ),
            ),
        ],
        max_tokens=300,
        json_mode=True,
    )

    try:
        response = client.generate(request)
    except LocalModelUnavailable as exc:  # pragma: no cover - environment dependent
        pytest.skip(f"local runtime became unavailable: {exc}")

    assert response.model
    try:
        validated = validate_tutor_reply(response.text, allowed_citations={"objective:py:values"})
    except TutorOutputRejected as exc:
        pytest.fail(f"the local model produced output the product would reject: {exc}")

    assert validated.reply.strip()
    assert 0 <= validated.hint_level <= 3
    assert "http" in client.endpoint and urlparse(client.endpoint).hostname in {
        "127.0.0.1",
        "localhost",
        "::1",
    }
    print(json.dumps({"model": response.model, "reply": validated.reply[:200]}, ensure_ascii=False))


def test_no_hosted_provider_is_configured() -> None:
    for variable in ("OPENAI_API_KEY", "ANTHROPIC_API_KEY", "GOOGLE_API_KEY", "GEMINI_API_KEY"):
        assert variable not in os.environ, f"{variable} must never be required by TALIMGO"
