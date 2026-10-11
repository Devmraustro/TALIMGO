"""FastAPI dependencies: authentication, authorisation, client identity.

Authorisation rule: the learner identity used by every endpoint comes from the server-side
session, never from the request body, query string or headers. Endpoints that take an object ID
re-query that object *scoped by the session's user id*, so a guessed ID from another account
returns 404 rather than data.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Annotated

from fastapi import Depends, Header, HTTPException, Query, Request, status
from sqlalchemy.orm import Session as DbSession

from app.config import Settings, get_settings
from app.db import get_db
from app.i18n import normalise_locale, request_locale
from app.models import Profile, Session, User
from app.security import hash_session_token, session_is_active
from app.utils import ensure_aware, utcnow

SESSION_COOKIE_NAME = "talimgo_session"


def client_ip(request: Request) -> str:
    """Best-effort client address, truncated. Never trusted for authorisation."""
    if request.client and request.client.host:
        return request.client.host[:64]
    return "unknown"


def _token_from_request(request: Request, authorization: str | None) -> str | None:
    cookie_token = request.cookies.get(SESSION_COOKIE_NAME)
    if cookie_token:
        return cookie_token
    if authorization and authorization.lower().startswith("bearer "):
        return authorization[7:].strip()
    return None


def get_optional_user(
    request: Request,
    db: Annotated[DbSession, Depends(get_db)],
    authorization: Annotated[str | None, Header()] = None,
) -> User | None:
    token = _token_from_request(request, authorization)
    if not token:
        return None
    row = db.query(Session).filter(Session.token_hash == hash_session_token(token)).one_or_none()
    if row is None:
        return None
    if not session_is_active(row.expires_at, row.revoked_at, utcnow()):
        return None
    user = db.get(User, row.user_id)
    if user is None or not user.is_active:
        return None
    return user


def get_current_user(
    user: Annotated[User | None, Depends(get_optional_user)],
) -> User:
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required.")
    return user


def get_admin_user(
    user: Annotated[User, Depends(get_current_user)],
) -> User:
    if user.role != "admin":
        # 404 rather than 403: an unauthorised caller learns nothing about what exists here.
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found.")
    return user


def get_current_locale(
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[DbSession, Depends(get_db)],
) -> str:
    """The learner's saved locale, defaulting to English for unknown values."""
    profile = db.get(Profile, user.id)
    return normalise_locale(profile.locale if profile is not None else None) or "en"


def get_content_locale(
    db: Annotated[DbSession, Depends(get_db)],
    user: Annotated[User | None, Depends(get_optional_user)],
    locale: Annotated[str | None, Query()] = None,
    accept_language: Annotated[str | None, Header()] = None,
) -> str:
    """Locale for content routes that are readable without a session.

    A signed-in learner's saved locale wins (Arabic must not require a query parameter); otherwise
    the request's ``?locale=`` then ``Accept-Language`` are used, then English.
    """
    if user is not None:
        profile = db.get(Profile, user.id)
        saved = normalise_locale(profile.locale if profile is not None else None)
        if saved is not None:
            return saved
    return request_locale(locale, accept_language)


CurrentUser = Annotated[User, Depends(get_current_user)]
AdminUser = Annotated[User, Depends(get_admin_user)]
Db = Annotated[DbSession, Depends(get_db)]
AppSettings = Annotated[Settings, Depends(get_settings)]
CurrentLocale = Annotated[str, Depends(get_current_locale)]
ContentLocale = Annotated[str, Depends(get_content_locale)]


def session_expiry(settings: Settings) -> datetime:
    """Absolute expiry for a newly created session."""
    return ensure_aware(utcnow()) + timedelta(hours=settings.session_ttl_hours)
