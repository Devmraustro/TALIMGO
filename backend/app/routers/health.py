"""Health and policy endpoints."""

from __future__ import annotations

import httpx
from fastapi import APIRouter

from app.ai.policy import is_local_host
from app.config import get_settings

router = APIRouter(prefix="/api", tags=["health"])

API_VERSION = "0.1.0"


@router.get("/health")
def health() -> dict:
    """Liveness only. Never exposes configuration values that could aid an attacker."""
    return {"status": "ok", "version": API_VERSION}


@router.get("/health/ai")
def ai_health() -> dict:
    """Whether tutoring is available, and whether the local model answers.

    Reports only the shape of the endpoint (host class), never credentials or full URLs.
    """
    settings = get_settings()
    info: dict = {
        "ai_enabled": settings.ai_enabled,
        "dialect": settings.ai_dialect,
        "endpoint_host_class": "local",
        "policy": "local-only",
    }
    if not settings.ai_enabled:
        info["detail"] = "Tutoring is switched off (TALIMGO_AI_ENABLED=false)."
        return info

    from urllib.parse import urlparse

    host = urlparse(settings.ai_base_url).hostname or ""
    info["endpoint_host_class"] = "local" if is_local_host(host) else "unknown"
    info["model_configured"] = bool(settings.ai_model)
    try:
        with httpx.Client(timeout=3.0) as client:
            client.get(
                f"{settings.ai_base_url}/api/tags"
                if settings.ai_dialect == "ollama"
                else f"{settings.ai_base_url}/v1/models"
            )
        info["runtime_reachable"] = True
    except httpx.HTTPError:
        info["runtime_reachable"] = False
        info["detail"] = (
            "The configured local runtime is not answering. Tutoring will fail explicitly with 503; "
            "no external provider is contacted."
        )
    return info
