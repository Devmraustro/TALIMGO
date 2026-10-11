"""Tests for the post-deployment verification script.

The API-flow and header checks run in-process against the real application (via the same
``httpx``-based test client the rest of the suite uses). The plain-HTTP redirect check needs a real
edge and is asserted in CI's ``proxy-tls-smoke`` job and documented in docs/DEPLOYMENT.md.
"""

from __future__ import annotations

from pathlib import Path

import httpx
import pytest
from starlette.testclient import TestClient

from tests.test_postgres_scripts import load_script

verify_deployment = load_script("verify_deployment")
SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"


@pytest.fixture
def results() -> object:
    return verify_deployment.Results()


def test_refuses_a_plain_http_target() -> None:
    with pytest.raises(SystemExit) as refused:
        verify_deployment.main(["--base-url", "http://talimgo.example", "--host", "talimgo.example"])
    assert "must use https" in str(refused.value)


def test_refuses_a_host_that_does_not_match_the_url() -> None:
    with pytest.raises(SystemExit) as refused:
        verify_deployment.main(["--base-url", "https://talimgo.example", "--host", "talimg0.example"])
    assert "does not match" in str(refused.value)


def test_missing_argument_is_an_error() -> None:
    with pytest.raises(SystemExit):
        verify_deployment.main(["--base-url", "https://talimgo.example"])


def test_header_policy_reports_each_missing_header(results) -> None:
    headers = httpx.Headers({"Strict-Transport-Security": "max-age=31536000"})
    verify_deployment.check_header_policy(results, headers)
    # Only HSTS is present in this response: the two header checks and the framing check fail.
    assert results.failures == 3


def test_header_policy_accepts_the_application_policy(results) -> None:
    """The policy the verification script requires is exactly what the application produces."""
    from starlette.requests import Request

    from app.http_hardening import hardening_headers

    request = Request(
        {
            "type": "http",
            "method": "GET",
            "path": "/api/health",
            "headers": [(b"x-forwarded-proto", b"https")],
            "scheme": "http",
            "server": ("talimgo.example", 443),
            "query_string": b"",
        }
    )
    verify_deployment.check_header_policy(results, httpx.Headers(hardening_headers(request)))
    assert results.failures == 0


def test_api_flow_passes_against_the_real_application(monkeypatch, tmp_path) -> None:
    """Register, session read-back, goal persistence and self-deletion, in-process.

    Runs the application in `production` mode (the mode this script exists to verify): the docs UI
    must be absent, so the schema is created first, exactly as `alembic upgrade head` would.
    """
    monkeypatch.setenv("TALIMGO_ENV", "production")
    monkeypatch.setenv("TALIMGO_DATABASE_URL", f"sqlite:///{tmp_path / 'verify-deployment.db'}")
    monkeypatch.setenv("TALIMGO_SESSION_SECRET", "verify-deployment-test-session-secret-value")
    monkeypatch.setenv("TALIMGO_AI_ENABLED", "false")
    from app.config import reset_settings_cache
    from app.db import get_engine, reset_engine
    from app.main import create_app
    from app.models import Base

    reset_settings_cache()
    reset_engine()
    Base.metadata.create_all(get_engine())
    results = verify_deployment.Results()
    with TestClient(create_app(), base_url="https://talimgo.example") as client:
        email = verify_deployment.run_api_checks(results, client)
    assert results.failures == 0, "verification checks failed"
    assert email is not None and email.startswith("deploy-verification-")


def test_redirect_check_honours_a_rehearsal_http_port(results) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.port == 8080, request.url
        return httpx.Response(
            301, headers={"location": "https://talimgo.example:8443/api/health?from=verify"}
        )

    with httpx.Client(transport=httpx.MockTransport(handler)) as client:
        verify_deployment.check_redirect(results, client, "https://talimgo.example:8443", http_port=8080)
    assert results.failures == 0


def test_redirect_check_reports_a_wrong_location(results) -> None:
    transport = httpx.MockTransport(lambda request: httpx.Response(200, request=request))
    with httpx.Client(transport=transport) as client:
        verify_deployment.check_redirect(results, client, "https://talimgo.example")
    assert results.failures == 1


def test_redirect_check_accepts_a_301_that_keeps_path_and_query(results) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.scheme == "http"
        assert request.url.path == "/api/health"
        assert request.url.query == b"from=verify"
        return httpx.Response(301, headers={"location": "https://talimgo.example/api/health?from=verify"})

    with httpx.Client(transport=httpx.MockTransport(handler)) as client:
        verify_deployment.check_redirect(results, client, "https://talimgo.example")
    assert results.failures == 0
