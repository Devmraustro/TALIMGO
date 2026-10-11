"""Post-deployment verification against a real, authorised TALIMGO target.

Run this after a deployment, against the public HTTPS hostname, with the owner's approval: it creates
one disposable account, exercises the session and goal paths through the real edge, checks the
response-header policy, and then deletes the account it created.

    python scripts/verify_deployment.py --base-url https://talimgo.example --host talimgo.example

It refuses a plain-HTTP target and refuses a `--host` that does not match the URL, so a typo cannot
send a run of account-creating requests to the wrong service. Certificate verification is on unless
`--insecure-tls` is passed, which is for a rehearsal host whose certificate is not yet trusted — never
for a real deployment.

Nothing here is a penetration test or a load test, and a pass says nothing about the local model
runtime (see /api/health/ai and docs/LOCAL_AI_ARCHITECTURE.md) or about browser behaviour.
"""

from __future__ import annotations

import argparse
import sys
import urllib.parse
from uuid import uuid4

import httpx

# Deliberately disclosed and single-use: the account it belongs to is deleted by this run.
DISPOSABLE_PASSWORD = "deploy-verification-password-1"
REQUIRED_DOCUMENT_HEADERS = (
    "x-content-type-options",
    "referrer-policy",
)
REQUIRED_HTTPS_HEADERS = ("strict-transport-security",)
# Either header is acceptable to refuse framing: the API sets both, an edge may set one.
FRAMING_HEADERS = ("x-frame-options", "content-security-policy")


class Results:
    """Collects check outcomes and decides the process exit code."""

    def __init__(self) -> None:
        self.failures = 0

    def record(self, name: str, ok: bool, detail: str = "") -> bool:
        suffix = f" :: {detail}" if detail else ""
        print(f"{'PASS' if ok else 'FAIL'}  {name}{suffix}")
        if not ok:
            self.failures += 1
        return ok


def check_header_policy(results: Results, headers: httpx.Headers) -> None:
    """The header contract a deployed edge+API must satisfy for browsers."""
    for name in REQUIRED_HTTPS_HEADERS:
        results.record(f"{name} present", name in headers, headers.get(name, "missing"))
    for name in REQUIRED_DOCUMENT_HEADERS:
        results.record(f"{name} present", name in headers, headers.get(name, "missing"))
    results.record(
        "framing refused",
        any(name in headers for name in FRAMING_HEADERS),
        " / ".join(f"{n}={headers.get(n)}" for n in FRAMING_HEADERS),
    )


def check_redirect(
    results: Results, client: httpx.Client, https_url: str, http_port: int | None = None
) -> None:
    """The plain-HTTP entry point must send the browser to HTTPS, keeping path and query.

    ``http_port`` exists only for a rehearsal on a non-privileged port; on a real deployment the
    default standard port is correct.
    """
    parsed = urllib.parse.urlsplit(https_url)
    http_netloc = parsed.hostname if http_port is None else f"{parsed.hostname}:{http_port}"
    http_url = urllib.parse.urlunsplit(("http", http_netloc, "/api/health", "from=verify", ""))
    try:
        response = client.get(http_url, follow_redirects=False)
    except httpx.HTTPError as exc:
        results.record("HTTP redirects to HTTPS", False, exc.__class__.__name__)
        return
    location = response.headers.get("location", "")
    expected = f"https://{parsed.netloc}/api/health?from=verify"
    results.record(
        "HTTP redirects to HTTPS",
        response.status_code in {301, 302, 307, 308} and location == expected,
        f"{response.status_code} -> {location or 'no Location header'}",
    )


def run_api_checks(results: Results, client: httpx.Client) -> str | None:
    """Drive the real API through the edge with one disposable account. Returns the email used."""
    health = client.get("/api/health")
    results.record(
        "health endpoint answers ok",
        health.status_code == 200 and health.json().get("status") == "ok",
        f"{health.status_code}",
    )

    check_header_policy(results, health.headers)

    docs = client.get("/api/docs")
    results.record(
        "interactive docs are not served",
        docs.status_code == 404,
        f"{docs.status_code} (production must set TALIMGO_ENV=production)",
    )

    email = f"deploy-verification-{uuid4().hex[:12]}@example.com"
    registered = client.post(
        "/api/auth/register",
        json={
            "email": email,
            "password": DISPOSABLE_PASSWORD,
            "display_name": "Deploy verification",
            "accept_terms": True,
            "accept_ai_processing": False,
        },
    )
    if not results.record(
        "disposable account created", registered.status_code == 201, f"{registered.status_code}"
    ):
        return None

    try:
        session = client.get("/api/auth/me")
        results.record(
            "session survives a new request",
            session.status_code == 200 and session.json().get("user", {}).get("email") == email,
            f"{session.status_code}",
        )

        paths = client.get("/api/curriculum/paths")
        path_id = "python-foundations"
        if paths.status_code == 200 and isinstance(paths.json(), list) and paths.json():
            path_id = paths.json()[0].get("id", path_id)
        goal = client.post(
            "/api/goals",
            json={
                "path_id": path_id,
                "statement": "Deployment verification goal",
                "weekly_minutes": 120,
            },
        )
        results.record("goal created", goal.status_code == 201, f"{goal.status_code}")
        listed = client.get("/api/goals")
        goal_id = goal.json().get("id") if goal.status_code == 201 else None
        results.record(
            "goal is readable back",
            listed.status_code == 200 and any(row.get("id") == goal_id for row in listed.json())
            if goal_id
            else False,
            f"{listed.status_code}",
        )
    except Exception as exc:
        # Verification must still attempt deletion if a request fails unexpectedly after registration.
        results.record("post-registration API checks completed", False, exc.__class__.__name__)
    finally:
        # Always attempt cleanup, including after network or response-decoding failures.
        try:
            removed = client.post(
                "/api/me/delete",
                json={"password": DISPOSABLE_PASSWORD, "confirmation": "DELETE"},
            )
            results.record("disposable account deleted", removed.status_code == 204, f"{removed.status_code}")
        except Exception as exc:
            results.record("disposable account deletion request completed", False, exc.__class__.__name__)

        try:
            after = client.get("/api/auth/me")
            results.record("deleted session is refused", after.status_code == 401, f"{after.status_code}")
        except Exception as exc:
            results.record("deleted session refusal check completed", False, exc.__class__.__name__)



def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Verify a deployed TALIMGO target.")
    parser.add_argument("--base-url", required=True, help="public HTTPS origin, e.g. https://talimgo.example")
    parser.add_argument(
        "--host",
        required=True,
        help="the hostname you mean to test; must match the base URL exactly (guards against typos)",
    )
    parser.add_argument("--timeout", type=float, default=10.0, help="per-request timeout in seconds")
    parser.add_argument(
        "--http-port",
        type=int,
        default=None,
        help="port the plain-HTTP entry point listens on; rehearsal hosts only (default: standard port)",
    )
    parser.add_argument(
        "--insecure-tls",
        action="store_true",
        help="skip certificate verification (rehearsal hosts only; never a real deployment)",
    )
    arguments = parser.parse_args(argv)

    parsed = urllib.parse.urlsplit(arguments.base_url)
    if parsed.scheme != "https":
        raise SystemExit("Refusing to run: --base-url must use https (this verifies a TLS deployment).")
    if parsed.hostname != arguments.host:
        raise SystemExit(
            f"Refusing to run: --host {arguments.host!r} does not match {parsed.hostname!r} in --base-url."
        )
    if arguments.insecure_tls:
        print("warning: TLS certificate verification is disabled for this run.", file=sys.stderr)

    results = Results()
    with httpx.Client(
        base_url=arguments.base_url,
        timeout=arguments.timeout,
        verify=not arguments.insecure_tls,
        follow_redirects=False,
    ) as client:
        check_redirect(results, client, arguments.base_url, arguments.http_port)
        email = run_api_checks(results, client)

    if results.failures:
        if email:
            print(
                f"leftover disposable account (delete it if the run failed early): {email}", file=sys.stderr
            )
        raise SystemExit(f"Deployment verification FAILED: {results.failures} check(s) did not pass.")
    print(
        "Deployment verification passed: TLS redirect, edge headers, session and goal persistence, "
        "and account deletion."
    )


if __name__ == "__main__":
    main()
