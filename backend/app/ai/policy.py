"""Endpoint policy for local model inference.

TALIMGO runs generative AI only on infrastructure it controls (AGENTS.md section 2,
docs/adr/0002-local-ai-only.md). This module is the single enforcement point: every
AI request passes through :func:`assert_local_endpoint`, and configuration validation
calls it at startup so a non-local endpoint cannot be used at all.

Nothing here knows about any hosted provider SDK, and none may be added.
"""

from __future__ import annotations

import ipaddress
from urllib.parse import urlparse

__all__ = [
    "FORBIDDEN_HOST_SUFFIXES",
    "NonLocalEndpointError",
    "assert_local_endpoint",
    "is_local_host",
]


class NonLocalEndpointError(ValueError):
    """Raised when an AI endpoint is not on a local/private network address."""


# Hosts that must never be used for inference, regardless of configuration. Kept as
# suffixes so that any subdomain of a hosted provider is also refused.
FORBIDDEN_HOST_SUFFIXES: tuple[str, ...] = (
    "openai.com",
    "openai.azure.com",
    "anthropic.com",
    "claude.ai",
    "googleapis.com",
    "google.com",
    "vertexai.googleapis.com",
    "cohere.ai",
    "mistral.ai",
    "groq.com",
    "together.xyz",
    "replicate.com",
    "replicate.delivery",
    "huggingface.co",
    "fireworks.ai",
    "perplexity.ai",
    "deepinfra.com",
    "amazonaws.com",
    "cloudflare.com",
    "azure.com",
    "ollama.ai",
)

_LOOPBACK_NAMES = frozenset({"localhost", "localhost.localdomain"})


def is_local_host(host: str) -> bool:
    """Return True only for loopback or RFC1918/site-local addresses and names."""
    if not host:
        return False
    candidate = host.strip().strip("[]").lower().rstrip(".")
    if candidate in _LOOPBACK_NAMES:
        return True
    try:
        ip = ipaddress.ip_address(candidate)
    except ValueError:
        return False
    return ip.is_loopback or ip.is_private or ip.is_link_local


def assert_local_endpoint(base_url: str, *, allow_extra_hosts: tuple[str, ...] = ()) -> str:
    """Validate that ``base_url`` points at a local inference runtime.

    Returns the normalised base URL (no trailing slash) so callers can use the result.

    Raises:
        NonLocalEndpointError: if the host is a known hosted provider, is not a local or
            private address, or the URL is malformed. Fails closed: an unparseable URL is
            treated as invalid rather than assumed safe.
    """
    raw = (base_url or "").strip()
    if not raw:
        raise NonLocalEndpointError("TALIMGO_AI_BASE_URL is empty; a local endpoint is required.")

    parsed = urlparse(raw)
    if parsed.scheme not in {"http", "https"}:
        raise NonLocalEndpointError(
            f"AI endpoint scheme {parsed.scheme!r} is not allowed; use http on a local address."
        )
    host = (parsed.hostname or "").lower()
    if not host:
        raise NonLocalEndpointError(f"AI endpoint {raw!r} has no host component.")

    for suffix in FORBIDDEN_HOST_SUFFIXES:
        if host == suffix or host.endswith("." + suffix):
            raise NonLocalEndpointError(
                f"AI endpoint host {host!r} is a hosted provider and is prohibited by TALIMGO's "
                "local-only AI policy (AGENTS.md section 2)."
            )

    extra = {h.strip().lower() for h in allow_extra_hosts if h.strip()}
    if host in extra and is_local_host(host):
        pass
    if not (is_local_host(host) or host in extra):
        raise NonLocalEndpointError(
            f"AI endpoint host {host!r} is not a loopback or private address. TALIMGO refuses to "
            "send learner content to any non-local host (docs/LOCAL_AI_ARCHITECTURE.md)."
        )

    normalised = raw.rstrip("/")
    return normalised
