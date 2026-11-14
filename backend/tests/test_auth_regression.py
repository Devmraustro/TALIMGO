"""Authentication and session lifecycle regressions.

Pins down the behaviour the D.7 cross-user investigation kept having to re-derive:

  * independent users never share sessions;
  * invalid, tampered, expired and revoked tokens are rejected with 401;
  * logout revokes exactly the credential that was presented (cookie *or* Bearer);
  * a deactivated account's sessions stop working immediately;
  * sessions are per-request in the database — no raw token is ever stored;
  * tokens hash to the documented digest and the cookie stays HttpOnly/SameSite/Path-scoped.

These tests fail against the pre-fix code where marked (see the bearer-logout regression).
"""

from __future__ import annotations

import hashlib
from datetime import UTC, datetime, timedelta

from fastapi.testclient import TestClient
from sqlalchemy import select

from app.db import session_scope
from app.models import Session, User
from tests.conftest import register

PASSWORD = "correct-horse-battery"
SESSION_COOKIE = "talimgo_session"


def _session_rows_for(email: str) -> list[Session]:
    with session_scope() as db:
        user = db.scalar(select(User).where(User.email == email))
        assert user is not None
        return list(db.scalars(select(Session).where(Session.user_id == user.id)).all())


def _me(client: TestClient, **kwargs) -> int:
    return client.get("/api/auth/me", **kwargs).status_code


def test_independent_users_get_independent_sessions(client) -> None:
    register(client, email="first@example.com")
    first_cookie = client.cookies.get(SESSION_COOKIE)

    other = TestClient(client.app)
    register(other, email="second@example.com")
    second_cookie = other.cookies.get(SESSION_COOKIE)

    assert first_cookie and second_cookie
    assert first_cookie != second_cookie
    assert _me(client) == 200
    assert _me(other) == 200
    client.cookies.clear()
    client.cookies.set(SESSION_COOKIE, second_cookie)
    assert client.get("/api/auth/me").json()["user"]["email"] == "second@example.com"


def test_database_never_stores_the_raw_session_token(client) -> None:
    register(client, email="hashcheck@example.com")
    raw_token = client.cookies.get(SESSION_COOKIE)
    assert raw_token

    rows = _session_rows_for("hashcheck@example.com")
    assert len(rows) == 1
    digest = hashlib.sha256(raw_token.encode("utf-8")).hexdigest()
    assert rows[0].token_hash == digest
    assert raw_token not in rows[0].token_hash
    assert len(rows[0].token_hash) == 64


def test_tampered_and_garbage_tokens_are_rejected(client) -> None:
    register(client, email="tamper@example.com")
    real = client.cookies.get(SESSION_COOKIE)
    assert real

    for bad in ("", "garbage", real[:-2] + ("aa" if not real.endswith("aa") else "bb"), real + "x"):
        client.cookies.clear()
        client.cookies.set(SESSION_COOKIE, bad)
        assert _me(client) == 401

    # A syntactically fine token with no server-side session behind it is equally rejected.
    client.cookies.clear()
    client.cookies.set(SESSION_COOKIE, "a" * 43)
    assert _me(client) == 401

    client.cookies.clear()
    client.cookies.set(SESSION_COOKIE, real)
    assert _me(client) == 200


def test_wrong_authorization_scheme_is_ignored(client) -> None:
    register(client, email="scheme@example.com")
    token = client.cookies.get(SESSION_COOKIE)
    client.cookies.clear()
    assert _me(client, headers={"Authorization": f"Token {token}"}) == 401
    assert _me(client, headers={"Authorization": "bearer   "}) == 401


def test_expired_session_is_rejected(client) -> None:
    register(client, email="expired@example.com")
    with session_scope() as db:
        user = db.scalar(select(User).where(User.email == "expired@example.com"))
        session = db.scalar(select(Session).where(Session.user_id == user.id))
        session.expires_at = datetime.now(UTC) - timedelta(minutes=1)
        db.commit()
    assert _me(client) == 401


def test_session_revoked_directly_in_the_database_is_rejected(client) -> None:
    register(client, email="revoked-db@example.com")
    with session_scope() as db:
        user = db.scalar(select(User).where(User.email == "revoked-db@example.com"))
        session = db.scalar(select(Session).where(Session.user_id == user.id))
        session.revoked_at = datetime.now(UTC)
        db.commit()
    assert _me(client) == 401


def test_logout_revokes_the_bearer_credential_too(client) -> None:
    """Regression: logout used to read only the cookie, leaving Bearer sessions alive."""
    register(client, email="bearer-logout@example.com")
    token = client.cookies.get(SESSION_COOKIE)
    assert token
    client.cookies.clear()

    headers = {"Authorization": f"Bearer {token}"}
    assert _me(client, headers=headers) == 200
    assert client.post("/api/auth/logout", headers=headers).status_code == 204
    assert _me(client, headers=headers) == 401


def test_logout_revokes_only_the_callers_session(client) -> None:
    register(client, email="logout-a@example.com")
    other = TestClient(client.app)
    register(other, email="logout-b@example.com")

    assert client.post("/api/auth/logout").status_code == 204
    assert _me(client) == 401
    assert _me(other) == 200, "logging out one learner must not touch another's session"


def test_deactivated_account_session_is_rejected(client) -> None:
    register(client, email="deactivated@example.com")
    with session_scope() as db:
        user = db.scalar(select(User).where(User.email == "deactivated@example.com"))
        user.is_active = False
        db.commit()
    assert _me(client) == 401


def test_session_expiry_matches_the_configured_ttl(client, client_factory) -> None:
    register(client, email="ttl@example.com")
    rows = _session_rows_for("ttl@example.com")
    (row,) = rows
    lifetime = (
        row.expires_at.replace(tzinfo=UTC) - row.created_at.replace(tzinfo=UTC)
        if row.expires_at.tzinfo is None
        else row.expires_at - row.created_at
    )
    # Default TTL is 14 days; allow a few seconds of execution slack.
    assert timedelta(days=13, hours=23) < lifetime <= timedelta(days=14)


def test_logout_marks_the_session_row_revoked(client) -> None:
    register(client, email="revoke-row@example.com")
    client.post("/api/auth/logout")
    (row,) = _session_rows_for("revoke-row@example.com")
    assert row.revoked_at is not None


def test_logout_response_clears_the_cookie(client) -> None:
    register(client, email="clear-cookie@example.com")
    response = client.post("/api/auth/logout")
    set_cookie = response.headers.get("set-cookie", "")
    assert SESSION_COOKIE in set_cookie
    assert "Max-Age=0" in set_cookie or "Expires=Thu, 01 Jan 1970" in set_cookie


def test_session_cookie_stays_httponly_samesite_and_path_scoped(client) -> None:
    register(client, email="cookie-shape@example.com")
    # Inspect the raw Set-Cookie from a fresh login (the register response already set it).
    response = client.post(
        "/api/auth/login", json={"email": "cookie-shape@example.com", "password": PASSWORD}
    )
    set_cookie = response.headers.get("set-cookie", "")
    lowered = set_cookie.lower()
    assert "httponly" in lowered
    assert "samesite=lax" in lowered
    assert "path=/" in lowered


def test_bearer_token_authenticates_and_cookie_wins_when_both_present(client) -> None:
    register(client, email="precedence@example.com")
    real = client.cookies.get(SESSION_COOKIE)
    other = TestClient(client.app)
    register(other, email="precedence-two@example.com")
    other_token = other.cookies.get(SESSION_COOKIE)

    # Cookie first in the client jar; Bearer from another account: the cookie (this client's
    # own session) decides, so a stray header cannot switch the resolved identity.
    client.cookies.set(SESSION_COOKIE, real)
    response = client.get("/api/auth/me", headers={"Authorization": f"Bearer {other_token}"})
    assert response.status_code == 200
    assert response.json()["user"]["email"] == "precedence@example.com"
