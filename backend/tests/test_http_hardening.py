"""Baseline HTTP hardening: the policy is asserted, not assumed.

This is a header/behaviour checklist — **not** a penetration test, and it does not claim one. It
exists so that the policy in ``app/http_hardening.py`` cannot silently disappear, and so the
development-only exception for the interactive docs stays deliberate.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.http_hardening import API_CSP, DOCS_CSP, PERMISSIONS_POLICY

HARDENED = {
    "x-content-type-options": "nosniff",
    "referrer-policy": "no-referrer",
    "x-frame-options": "DENY",
}


def _assert_baseline(response) -> None:
    for name, value in HARDENED.items():
        assert response.headers.get(name) == value, f"{name} missing from {response.url}"
    assert response.headers.get("permissions-policy") == PERMISSIONS_POLICY
    assert response.headers.get("content-security-policy") == API_CSP


def test_api_responses_carry_the_baseline_policy(client: TestClient) -> None:
    _assert_baseline(client.get("/api/health"))


def test_the_policy_applies_to_errors_and_preflights_too(client: TestClient) -> None:
    _assert_baseline(client.get("/api/plans/active"))  # 401
    _assert_baseline(client.get("/api/definitely-not-a-route"))  # 404
    _assert_baseline(
        client.options(
            "/api/health",
            headers={"Origin": "http://localhost:5173", "Access-Control-Request-Method": "GET"},
        )
    )


def test_frame_embedding_is_blocked_twice_over(client: TestClient) -> None:
    """X-Frame-Options for older browsers, frame-ancestors for modern ones."""
    response = client.get("/api/health")
    assert response.headers["x-frame-options"] == "DENY"
    assert "frame-ancestors 'none'" in response.headers["content-security-policy"]


def test_permissions_policy_switches_off_unused_features(client: TestClient) -> None:
    policy = client.get("/api/health").headers["permissions-policy"]
    for feature in ("camera", "microphone", "geolocation", "payment", "usb"):
        assert f"{feature}=()" in policy
    assert "microphone=*" not in policy and "camera=*" not in policy


def test_hsts_is_sent_only_on_requests_that_arrived_over_https(client: TestClient) -> None:
    plain = client.get("/api/health")
    assert "strict-transport-security" not in plain.headers, "HSTS over http would be ignored anyway"

    proxied = client.get("/api/health", headers={"X-Forwarded-Proto": "https"})
    assert proxied.headers["strict-transport-security"].startswith("max-age=")
    assert int(proxied.headers["strict-transport-security"].split("=")[1]) >= 31_536_000


def test_the_docs_ui_gets_a_policy_that_lets_it_load_and_nothing_more(client: TestClient) -> None:
    """Development keeps working: Swagger UI needs its own assets; the API stays locked down."""
    docs = client.get("/api/docs")
    assert docs.status_code == 200
    assert docs.headers["content-security-policy"] == DOCS_CSP
    assert "default-src 'none'" in DOCS_CSP
    assert "frame-ancestors 'none'" in DOCS_CSP
    assert docs.headers["content-security-policy"] != API_CSP

    api = client.get("/api/health")
    assert api.headers["content-security-policy"] == API_CSP


def test_the_strict_policy_has_no_exceptions_in_it() -> None:
    assert "unsafe-inline" not in API_CSP
    assert "unsafe-eval" not in API_CSP
    assert "*" not in API_CSP.replace("'none'", "")


def test_production_serves_no_interactive_docs_but_keeps_the_policy(client_factory) -> None:
    # A development instance first, so the schema exists: production refuses to create it implicitly.
    # Both clients share this test's database file.
    development = client_factory()
    assert development.get("/api/docs").status_code == 200

    production = client_factory(TALIMGO_ENV="production")
    assert production.get("/api/docs").status_code == 404
    assert production.get("/api/openapi.json").status_code == 404
    _assert_baseline(production.get("/api/health"))


@pytest.mark.parametrize("forwarded", ["https", "https, http", "HTTPS"])
def test_hsts_tolerates_the_shapes_a_proxy_actually_sends(client: TestClient, forwarded: str) -> None:
    response = client.get("/api/health", headers={"X-Forwarded-Proto": forwarded})
    assert "strict-transport-security" in response.headers


def test_a_forged_forwarded_proto_cannot_weaken_an_http_response(client: TestClient) -> None:
    """The header can only *add* HSTS; there is no code path where it removes a protection."""
    response = client.get("/api/health", headers={"X-Forwarded-Proto": "http"})
    assert "strict-transport-security" not in response.headers
    _assert_baseline(response)
