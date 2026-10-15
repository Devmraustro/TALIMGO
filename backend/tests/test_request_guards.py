"""Request guards: JSON-only bodies, declared size, and no unbounded chunked reads.

These controls are defence in depth — a reverse proxy must still cap bodies and rate (see
docs/DEPLOYMENT.md) — but they are asserted here so they cannot be dropped silently.
"""

from __future__ import annotations

from fastapi.testclient import TestClient


def test_mutating_endpoints_require_json(client: TestClient) -> None:
    """A cross-site HTML form cannot send application/json, so the form POST path is closed."""
    form = client.post(
        "/api/auth/login",
        content="email=a@example.com&password=hunter2",
        headers={"content-type": "application/x-www-form-urlencoded"},
    )
    assert form.status_code == 415
    assert "application/json" in form.json()["detail"]

    text = client.post(
        "/api/auth/login", content="email=a@example.com", headers={"content-type": "text/plain"}
    )
    assert text.status_code == 415


def test_a_json_request_is_accepted(client: TestClient) -> None:
    response = client.post("/api/auth/login", json={"email": "nobody@example.com", "password": "x"})
    assert response.status_code in {401, 403, 422}, "the guard must not reject a well-formed JSON call"


def test_a_bodyless_request_is_still_allowed(client: TestClient) -> None:
    """Logout carries no body; requiring a content type there would break a real flow."""
    response = client.post("/api/auth/logout")
    assert response.status_code in {200, 204, 401}


def test_oversized_bodies_are_refused_before_parsing(client: TestClient) -> None:
    from app.config import get_settings

    limit = get_settings().max_request_bytes
    response = client.post(
        "/api/auth/login",
        content=b"x" * (limit + 1),
        headers={"content-type": "application/json"},
    )
    assert response.status_code == 413
    assert response.json()["limit_bytes"] == limit


def test_a_malformed_content_length_is_refused(client: TestClient) -> None:
    response = client.post(
        "/api/auth/login",
        content=b"{}",
        headers={"content-type": "application/json", "content-length": "not-a-number"},
    )
    assert response.status_code in {400, 411}, response.text


def test_chunked_bodies_on_mutating_methods_are_refused(client: TestClient) -> None:
    """No declared length means no bound; the request is refused rather than read."""

    def chunked():
        yield b'{"email": "a@example.com"'

    response = client.post("/api/auth/login", content=chunked(), headers={"content-type": "application/json"})
    assert response.status_code in {411, 415, 413}


def test_reads_are_not_affected_by_the_guard(client: TestClient) -> None:
    assert client.get("/api/health").status_code == 200
    assert client.get("/api/curriculum/paths").status_code == 200


def test_refusals_carry_the_hardening_headers(client: TestClient) -> None:
    response = client.post("/api/auth/login", content="x=1", headers={"content-type": "text/plain"})
    assert response.status_code == 415
    assert response.headers["x-content-type-options"] == "nosniff"
