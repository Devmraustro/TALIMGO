"""Application configuration, validated at startup.

Fail-closed rules (AGENTS.md section 6):
  * In production the session secret must be set and long enough.
  * The AI endpoint must be local (validated by :mod:`app.ai.policy`) whenever AI is enabled.
  * Unknown values raise rather than silently defaulting.
"""

from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.ai.policy import assert_local_endpoint

_ENV_FILE = ".env"
_MIN_PRODUCTION_SECRET_LENGTH = 32


class Settings(BaseSettings):
    """Environment-backed settings. Prefix: ``TALIMGO_``."""

    model_config = SettingsConfigDict(
        env_file=_ENV_FILE, env_prefix="TALIMGO_", extra="ignore", case_sensitive=False
    )

    env: Literal["development", "test", "production"] = "development"
    session_secret: str = "dev-only-insecure-session-secret-change-me"
    allowed_origins: str = "http://localhost:5173"

    database_url: str = "sqlite:///./talimgo.db"

    # --- Authentication policy ---
    session_ttl_hours: int = Field(default=24 * 14, ge=1, le=24 * 90)
    max_login_attempts: int = Field(default=8, ge=3, le=100)
    login_lockout_minutes: int = Field(default=15, ge=1, le=1440)
    min_password_length: int = Field(default=10, ge=8, le=128)

    # --- Local AI (never a hosted provider) ---
    ai_enabled: bool = False
    ai_base_url: str = "http://127.0.0.1:11434"
    ai_dialect: Literal["ollama", "openai_compatible"] = "ollama"
    ai_model: str = ""
    ai_strict: bool = True
    ai_timeout_seconds: float = Field(default=60.0, gt=0, le=600)
    ai_max_output_tokens: int = Field(default=800, ge=64, le=8192)
    ai_daily_requests_per_learner: int = Field(default=100, ge=0, le=10_000)

    seed_on_startup: bool = False

    @field_validator("allowed_origins")
    @classmethod
    def _no_wildcard_origins(cls, value: str) -> str:
        if "*" in value:
            raise ValueError(
                "Wildcard origins are not allowed: they would let any site drive the API with "
                "credentials. List explicit origins."
            )
        return value

    @model_validator(mode="after")
    def _validate_environment(self) -> Settings:
        if self.env == "production":
            if len(self.session_secret) < _MIN_PRODUCTION_SECRET_LENGTH:
                raise ValueError(
                    "TALIMGO_SESSION_SECRET must be at least "
                    f"{_MIN_PRODUCTION_SECRET_LENGTH} characters in production."
                )
            if "dev-only" in self.session_secret:
                raise ValueError("The development session secret must not be used in production.")
        if self.ai_enabled:
            if not self.ai_model.strip():
                raise ValueError("TALIMGO_AI_MODEL must name the local model when AI is enabled.")
            try:
                object.__setattr__(self, "ai_base_url", assert_local_endpoint(self.ai_base_url))
            except Exception as exc:
                if self.ai_strict:
                    raise
                raise ValueError(f"AI endpoint rejected: {exc}") from exc
        return self

    @property
    def origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.allowed_origins.split(",") if origin.strip()]

    @property
    def is_test(self) -> bool:
        return self.env == "test"


@lru_cache
def get_settings() -> Settings:
    return Settings()


def reset_settings_cache() -> None:
    """Testing helper: forces the next :func:`get_settings` call to re-read the environment."""
    get_settings.cache_clear()
