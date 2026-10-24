"""Small shared helpers."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime


def new_id(prefix: str) -> str:
    """Opaque, non-guessable identifier with a readable prefix."""
    return f"{prefix}_{uuid.uuid4().hex}"


def utcnow() -> datetime:
    """Timezone-aware UTC now. Learning code receives this as an argument, never imports it."""
    return datetime.now(UTC)


def ensure_aware(value: datetime) -> datetime:
    """Normalise a datetime read back from the database to timezone-aware UTC."""
    if value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value.astimezone(UTC)
