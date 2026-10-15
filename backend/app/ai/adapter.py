"""The single interface between TALIMGO and a language model.

Supported dialects are both **local** wire formats:
  * ``ollama``            → ``POST {base}/api/chat``
  * ``openai_compatible`` → ``POST {base}/v1/chat/completions`` (vLLM, llama.cpp server)

Every request re-validates the endpoint through :func:`app.ai.policy.assert_local_endpoint`, so a
configuration change cannot route learner content to a remote host. If the local runtime is not
answering, the call raises :class:`LocalModelUnavailable` and the caller must surface an explicit
error. There is deliberately no fallback path, and no provider SDK is imported anywhere.
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from typing import Any, Literal

import httpx

from app.ai.policy import assert_local_endpoint
from app.config import Settings

# Telemetry switches for local runtimes that expose one. Documented in
# docs/LOCAL_AI_ARCHITECTURE.md: optional usage reporting is off.
OLLAMA_TELEMETRY_HEADER = {"x-ollama-telemetry": "disabled"}


class LocalModelError(RuntimeError):
    """Base class for local inference failures."""


class LocalModelUnavailable(LocalModelError):
    """The configured local runtime could not be reached or did not answer in time."""


class LocalModelResponseError(LocalModelError):
    """The runtime answered, but not with a usable response."""


@dataclass(frozen=True)
class ModelMessage:
    role: Literal["system", "user", "assistant"]
    content: str


@dataclass(frozen=True)
class ModelRequest:
    messages: list[ModelMessage]
    max_tokens: int = 800
    temperature: float = 0.2
    json_mode: bool = False


@dataclass(frozen=True)
class ModelResponse:
    text: str
    model: str
    duration_ms: int
    usage: dict[str, Any] = field(default_factory=dict)


class LocalModelClient:
    """Talks to exactly one configured local endpoint."""

    def __init__(self, settings: Settings, *, transport: httpx.BaseTransport | None = None) -> None:
        self._settings = settings
        # Validate at construction time; also re-validated on every call below.
        self._endpoint = assert_local_endpoint(settings.ai_base_url)
        self._dialect = settings.ai_dialect
        self._model = settings.ai_model
        self._timeout = settings.ai_timeout_seconds
        self._transport = transport

    @property
    def endpoint(self) -> str:
        return self._endpoint

    @property
    def model(self) -> str:
        return self._model

    # -- public API -------------------------------------------------------------------

    def generate(self, request: ModelRequest) -> ModelResponse:
        # Re-validate on every call: configuration is re-read, never cached as trusted.
        endpoint = assert_local_endpoint(self._endpoint)
        payload = self._build_payload(request)
        url = (
            f"{endpoint}/v1/chat/completions"
            if self._dialect == "openai_compatible"
            else f"{endpoint}/api/chat"
        )
        headers = {"content-type": "application/json", **OLLAMA_TELEMETRY_HEADER}

        started = time.perf_counter()
        try:
            with httpx.Client(timeout=self._timeout, transport=self._transport) as client:
                response = client.post(url, json=payload, headers=headers)
        except httpx.TimeoutException as exc:
            raise LocalModelUnavailable(
                f"The local model at {endpoint} did not answer within {self._timeout:.0f}s."
            ) from exc
        except httpx.HTTPError as exc:
            raise LocalModelUnavailable(
                f"The local model at {endpoint} is not reachable ({exc.__class__.__name__}). "
                "Start the local runtime or disable tutoring."
            ) from exc
        duration_ms = int((time.perf_counter() - started) * 1000)

        if response.status_code >= 400:
            raise LocalModelResponseError(
                f"The local model returned HTTP {response.status_code} for model {self._model!r}."
            )
        try:
            body = response.json()
        except json.JSONDecodeError as exc:
            raise LocalModelResponseError("The local model returned a non-JSON response.") from exc

        text = self._extract_text(body)
        if not text.strip():
            raise LocalModelResponseError("The local model returned an empty completion.")
        return ModelResponse(
            text=text,
            model=str(body.get("model") or self._model),
            duration_ms=duration_ms,
            usage=self._extract_usage(body),
        )

    # -- payload handling -------------------------------------------------------------

    def _build_payload(self, request: ModelRequest) -> dict[str, Any]:
        messages = [{"role": message.role, "content": message.content} for message in request.messages]
        if self._dialect == "openai_compatible":
            payload: dict[str, Any] = {
                "model": self._model,
                "messages": messages,
                "max_tokens": request.max_tokens,
                "temperature": request.temperature,
            }
            if request.json_mode:
                payload["response_format"] = {"type": "json_object"}
            return payload
        payload = {
            "model": self._model,
            "messages": messages,
            "stream": False,
            "options": {"num_predict": request.max_tokens, "temperature": request.temperature},
        }
        if request.json_mode:
            payload["format"] = "json"
        return payload

    @staticmethod
    def _extract_text(body: dict[str, Any]) -> str:
        if "message" in body and isinstance(body["message"], dict):  # ollama
            return str(body["message"].get("content", ""))
        choices = body.get("choices")
        if isinstance(choices, list) and choices:  # openai-compatible
            first = choices[0]
            if isinstance(first, dict):
                message = first.get("message") or {}
                if isinstance(message, dict):
                    return str(message.get("content", ""))
        return ""

    @staticmethod
    def _extract_usage(body: dict[str, Any]) -> dict[str, Any]:
        usage: dict[str, Any] = {}
        for key in ("prompt_eval_count", "eval_count", "total_duration"):
            if key in body:
                usage[key] = body[key]
        if isinstance(body.get("usage"), dict):
            usage.update(body["usage"])
        return usage
