"""Authentication, session handling and account controls."""

from __future__ import annotations

from tests.conftest import register


def test_registration_creates_a_session_cookie_and_records_consents(client) -> None:
    body = register(client)
    assert client.cookies.get("talimgo_session"), "a session cookie must be issued"
    consents = {row["kind"]: row["granted"] for row in body["consents"]}
    assert consents["account"] is True
    assert consents["ai_processing"] is True
    assert "password" not in str(body).lower()


def test_registration_rejects_a_weak_password(client) -> None:
    response = client.post(
        "/api/auth/register",
        json={
            "email": "weak@example.com",
            "password": "short",
            "display_name": "Weak",
            "accept_terms": True,
        },
    )
    assert response.status_code == 422
    assert "problems" in response.json()["detail"]


def test_registration_requires_terms_acceptance(client) -> None:
    response = client.post(
        "/api/auth/register",
        json={
            "email": "noterms@example.com",
            "password": "a-long-enough-password",
            "display_name": "No Terms",
            "accept_terms": False,
        },
    )
    assert response.status_code == 400


def test_duplicate_email_is_rejected_without_creating_a_second_account(client) -> None:
    register(client, email="duplicate@example.com")
    client.post("/api/auth/logout")
    response = client.post(
        "/api/auth/register",
        json={
            "email": "duplicate@example.com",
            "password": "another-long-password",
            "display_name": "Second",
            "accept_terms": True,
        },
    )
    assert response.status_code == 409


def test_login_with_wrong_password_is_generic_401(client) -> None:
    register(client, email="login@example.com", password="first-password-here")
    client.post("/api/auth/logout")
    response = client.post(
        "/api/auth/login", json={"email": "login@example.com", "password": "definitely-wrong"}
    )
    assert response.status_code == 401
    assert "incorrect" in response.json()["detail"].lower()


def test_login_unknown_email_returns_the_same_message_as_wrong_password(client) -> None:
    register(client, email="known@example.com", password="first-password-here")
    client.post("/api/auth/logout")
    wrong_password = client.post(
        "/api/auth/login", json={"email": "known@example.com", "password": "nope-nope-nope"}
    )
    unknown_user = client.post(
        "/api/auth/login", json={"email": "nobody@example.com", "password": "nope-nope-nope"}
    )
    assert wrong_password.status_code == unknown_user.status_code == 401
    assert wrong_password.json()["detail"] == unknown_user.json()["detail"]


def test_repeated_failures_lock_the_account_temporarily(client) -> None:
    register(client, email="lockme@example.com", password="first-password-here")
    client.post("/api/auth/logout")
    statuses = [
        client.post("/api/auth/login", json={"email": "lockme@example.com", "password": "wrong"}).status_code
        for _ in range(10)
    ]
    assert 429 in statuses, "brute force must eventually be throttled"


def test_protected_routes_require_authentication(client) -> None:
    assert client.get("/api/auth/me").status_code == 401
    assert client.get("/api/dashboard").status_code == 401
    assert client.get("/api/plans/active").status_code == 401
    assert client.get("/api/practice/progress/mastery").status_code == 401


def test_logout_revokes_the_session_server_side(client) -> None:
    register(client)
    assert client.get("/api/auth/me").status_code == 200
    client.post("/api/auth/logout")
    assert client.get("/api/auth/me").status_code == 401


def test_session_token_is_stored_hashed(client) -> None:
    from app.db import session_scope
    from app.models import Session

    register(client)
    raw_token = client.cookies.get("talimgo_session")
    assert raw_token
    with session_scope() as db:
        rows = db.query(Session).all()
    assert len(rows) == 1
    assert rows[0].token_hash != raw_token, "the raw token must never be stored"
    assert len(rows[0].token_hash) == 64


def test_profile_can_be_updated_and_switches_locale(client) -> None:
    register(client)
    response = client.patch(
        "/api/me/profile",
        json={"locale": "ar", "weekly_minutes": 300, "availability_days": ["mon", "wed", "sat"]},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["locale"] == "ar"
    assert body["weekly_minutes"] == 300
    assert body["availability_days"] == ["mon", "wed", "sat"], "canonical weekday order"


def test_invalid_profile_values_are_rejected(client) -> None:
    register(client)
    assert client.patch("/api/me/profile", json={"locale": "fr"}).status_code == 422
    assert client.patch("/api/me/profile", json={"weekly_minutes": 5}).status_code == 422
    assert client.patch("/api/me/profile", json={"availability_days": ["funday"]}).status_code == 422


def test_consent_can_be_withdrawn_and_is_recorded(client) -> None:
    register(client)
    response = client.post("/api/me/consents", json={"kind": "ai_processing", "granted": False})
    assert response.status_code == 200
    assert response.json()["granted"] is False
    consents = {row["kind"]: row["granted"] for row in client.get("/api/me/consents").json()}
    assert consents["ai_processing"] is False


def test_export_contains_the_learners_own_data_only(client) -> None:
    from tests.conftest import create_goal

    first = register(client, email="exporter@example.com")
    create_goal(client)
    export = client.get("/api/me/export")
    assert export.status_code == 200
    payload = export.json()["account"]
    assert payload["account"]["email"] == "exporter@example.com"
    assert payload["goals"], "the learner's goal must be included"

    client.post("/api/auth/logout")
    register(client, email="other@example.com")
    second_export = client.get("/api/me/export").json()["account"]
    assert second_export["account"]["email"] == "other@example.com"
    assert "exporter@example.com" not in str(second_export)
    del first


def test_account_deletion_requires_the_password_and_then_removes_the_account(client) -> None:
    register(client, email="delete-me@example.com", password="delete-me-password")
    refused = client.post("/api/me/delete", json={"password": "wrong-password", "confirmation": "DELETE"})
    assert refused.status_code == 403

    accepted = client.post(
        "/api/me/delete", json={"password": "delete-me-password", "confirmation": "DELETE"}
    )
    assert accepted.status_code == 204
    assert client.get("/api/auth/me").status_code == 401

    relogin = client.post(
        "/api/auth/login", json={"email": "delete-me@example.com", "password": "delete-me-password"}
    )
    assert relogin.status_code == 401, "the account must no longer exist"


def test_deletion_requires_the_explicit_confirmation_word(client) -> None:
    register(client, password="confirmation-password")
    response = client.post(
        "/api/me/delete", json={"password": "confirmation-password", "confirmation": "delete"}
    )
    assert response.status_code == 422
