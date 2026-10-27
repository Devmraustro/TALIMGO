"""Consistency checks for the checked-in deployment artifacts.

The unit files and shell helpers under `deploy/` are what an operator actually installs, so they are
tested for the properties that matter even though this environment cannot start systemd: the start
order the deployment guide promises, the hardening directives, and the refusal paths of the scripts.
The behaviours that need a real host (installing units, serving through Nginx, a real certificate) are
listed as untested in docs/DEPLOYMENT.md.

The shell helpers are real programs, so they are really executed: CI runs this suite on Ubuntu,
where `bash` is on `PATH`; a Windows developer runs them with Git for Windows' Bash, which
`tests.deploy_shell` locates and adapts (paths, interpreter). Nothing here is skipped for lack of a
shell — a missing shell is reported as a failure with the reason.
"""

from __future__ import annotations

import http.client
import http.server
import importlib.util
import json
import os
import re
import socket
import subprocess
import sys
import threading
from pathlib import Path

import pytest

from tests.deploy_shell import ShellUnavailable, run_bash, run_script

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
BACKEND = REPOSITORY_ROOT / "backend"
DEPLOY = REPOSITORY_ROOT / "deploy"
API_UNIT = DEPLOY / "systemd" / "talimgo-api.service.example"
MAINTENANCE_UNIT = DEPLOY / "systemd" / "talimgo-maintenance.service.example"
MAINTENANCE_TIMER = DEPLOY / "systemd" / "talimgo-maintenance.timer.example"
CI_WORKFLOW = REPOSITORY_ROOT / ".github" / "workflows" / "ci.yml"
CI_UPSTREAM = DEPLOY / "nginx" / "ci_upstream.py"


def unit_directives(path: Path) -> dict[str, list[str]]:
    """Parse an INI-style unit file into {key: [values]} (systemd allows repeated keys)."""
    directives: dict[str, list[str]] = {}
    for raw in path.read_text().splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or line.startswith("[") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        directives.setdefault(key.strip(), []).append(value.strip())
    return directives


def shell(*arguments: str, timeout: float = 30) -> subprocess.CompletedProcess:
    """Run the shell itself (a syntax check, a `command -v` probe)."""
    try:
        return run_bash(arguments, timeout=timeout)
    except ShellUnavailable as error:
        pytest.fail(str(error))


def bash(
    script: Path,
    *arguments: str,
    timeout: float = 30,
    cwd: Path | None = None,
) -> subprocess.CompletedProcess:
    """Run one of the checked-in deployment scripts."""
    try:
        return run_script(script, *arguments, timeout=timeout, cwd=cwd)
    except ShellUnavailable as error:
        pytest.fail(str(error))


def is_executable_in_the_repository(path: Path) -> bool:
    """Whether the repository ships this script as executable.

    On POSIX the working tree's mode is the answer, and it is what a clone of the repository
    produces. Windows has no executable bit, so the recorded git mode is: `git ls-files --stage`
    reports the mode a fresh clone would create (100755 for these scripts).
    """
    if os.name != "nt":
        return bool(path.stat().st_mode & 0o111)
    try:
        recorded = subprocess.run(
            ["git", "ls-files", "--stage", "--", path.relative_to(REPOSITORY_ROOT).as_posix()],
            capture_output=True,
            text=True,
            timeout=30,
            cwd=REPOSITORY_ROOT,
        )
    except FileNotFoundError:  # pragma: no cover - a Windows machine without git
        pytest.fail("git is required to read the recorded file mode")
    assert recorded.returncode == 0, recorded.stderr
    return recorded.stdout.split(" ", 1)[0] == "100755"


@pytest.mark.parametrize("script", ["stage-frontend.sh", "health-check.sh"])
def test_shell_helpers_parse(script: str) -> None:
    path = DEPLOY / script
    syntax = shell("-n", str(path))
    assert syntax.returncode == 0, syntax.stderr
    assert is_executable_in_the_repository(path), f"{script} must be executable"


def test_backend_vercel_config_never_runs_the_frontend_build() -> None:
    # The talimgo-api Vercel project uses backend/ as its root directory. Without its own
    # vercel.json it inherited the repository-root frontend commands and every production
    # deployment died running `npm ci --prefix frontend` where no frontend lockfile exists
    # (dpl_3TCjz4g1JGrVxAEfqDa421zHFbWz). The backend config must stay Python-only.
    config = json.loads((BACKEND / "vercel.json").read_text(encoding="utf-8"))
    assert config.get("framework") == "fastapi"
    for key in ("installCommand", "buildCommand", "outputDirectory"):
        value = config.get(key)
        assert value is None or "npm" not in str(value), f"backend vercel.json must not run npm ({key})"


def test_the_api_unit_enforces_the_documented_start_order() -> None:
    """Preflight, then migrations, then start, then a readiness probe — in that order."""
    unit = unit_directives(API_UNIT)
    preflight = unit["ExecStartPre"][0]
    migrations = unit["ExecStartPre"][1]
    assert "check_production_config.py" in preflight
    assert "alembic upgrade head" in migrations
    assert "app.main:app" in unit["ExecStart"][0]
    assert "--host 127.0.0.1" in unit["ExecStart"][0], "the API must not bind a public interface"
    assert "health-check.sh" in unit["ExecStartPost"][0]
    assert "--wait" in unit["ExecStartPost"][0], "a single immediate probe would race the process"
    # The probe must be allowed to finish before systemd declares the start failed.
    assert int(unit["TimeoutStartSec"][0]) >= 30


def test_the_api_unit_is_hardened_and_restarts_without_masking_failures() -> None:
    unit = unit_directives(API_UNIT)
    assert unit["EnvironmentFile"][0].startswith("/etc/talimgo/"), "secrets stay outside the repo"
    assert unit["Restart"][0] == "on-failure"
    for directive in (
        "NoNewPrivileges",
        "PrivateTmp",
        "ProtectSystem",
        "ProtectHome",
        "RestrictSUIDSGID",
        "MemoryDenyWriteExecute",
        "ReadWritePaths",
    ):
        assert directive in unit, f"{directive} is part of the documented hardening"
    assert unit["ProtectSystem"][0] == "strict"
    # The service must not be able to write its own code or configuration.
    assert "/srv/talimgo" not in unit["ReadWritePaths"][0]


def test_the_api_unit_runs_as_a_service_user_and_logs_to_the_journal() -> None:
    unit = unit_directives(API_UNIT)
    assert unit["User"][0] != "root"
    assert unit["StandardOutput"][0] == "journal"
    assert unit["SyslogIdentifier"][0] == "talimgo-api"


def maintenance_environment(tmp_path) -> dict[str, str]:
    """A throwaway, migrated database so the maintenance command can run for real.

    Housekeeping deletes rows, so this never touches a development or production database: the schema is
    built in `tmp_path` and the process is given only that URL.

    The environment is inherited rather than replaced. A child process needs the platform's own
    variables — on Windows the interpreter cannot even initialise its socket layer without
    `SystemRoot` — while every `TALIMGO_*` variable that could point the application at another
    database, secret or environment is dropped before the ones this test needs are set.
    """
    database = tmp_path / "maintenance.db"
    environment = {key: value for key, value in os.environ.items() if not key.startswith("TALIMGO_")}
    environment.update(
        {
            "HOME": str(tmp_path),
            "TALIMGO_ENV": "test",
            "TALIMGO_DATABASE_URL": f"sqlite+pysqlite:///{database}",
            "TALIMGO_SESSION_SECRET": "deploy-artifact-test-session-secret-0001",
            "TALIMGO_AI_ENABLED": "false",
        }
    )
    subprocess.run(
        [sys.executable, "-m", "alembic", "upgrade", "head"],
        capture_output=True,
        text=True,
        check=True,
        cwd=BACKEND,
        env=environment,
        timeout=180,
    )
    return environment


def test_maintenance_is_a_separate_oneshot_with_its_own_timer(tmp_path) -> None:
    unit = unit_directives(MAINTENANCE_UNIT)
    assert unit["Type"][0] == "oneshot"
    assert "app.maintenance" in unit["ExecStart"][0]
    assert "app.main:app" not in unit["ExecStart"][0], "housekeeping must not start the API"
    # The unit's command must be one the application really implements: run it for real. `--dry-run`
    # is the documented way to check housekeeping without deleting anything (see docs/DEPLOYMENT.md),
    # and it is what the unit's own comment points an administrator at.
    result = subprocess.run(
        [sys.executable, "-m", "app.maintenance", "--dry-run"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=BACKEND,
        env=maintenance_environment(tmp_path),
    )
    assert result.returncode == 0, result.stderr
    # The summary is written through the application's logger, which goes to stderr under systemd
    # (journald captures both streams); check both so this does not depend on the logging target.
    assert "dry_run" in result.stdout + result.stderr, "the module must report what a dry run would do"

    timer = unit_directives(MAINTENANCE_TIMER)
    assert timer["OnCalendar"][0].startswith("*-*-*")
    assert timer["Persistent"][0] == "true", "a missed run must not be skipped silently"


def test_the_documented_release_target_is_the_directory_the_proxy_serves() -> None:
    """The release procedure and the Nginx example must name the same directory.

    The staging script publishes the *contents* of frontend/dist, so a target one level above the
    proxy's `root` leaves the document outside the served path and every request fails. That is what the
    first draft of the guide did; this test keeps the two artifacts in agreement.

    The mismatch is also reproduced end to end against a real Nginx in this round's rehearsal: staging
    to the parent directory made the edge answer 500/404 while the file sat one level up.
    """
    nginx = (REPOSITORY_ROOT / "deploy" / "nginx" / "talimgo.conf.example").read_text()
    roots = re.findall(r"^\s*root\s+([^;]+);", nginx, flags=re.MULTILINE)
    served = [root.strip() for root in roots if "certbot" not in root]
    assert len(served) == 1, f"expected exactly one served root in the example, found {served}"

    guide = (REPOSITORY_ROOT / "docs" / "DEPLOYMENT.md").read_text()
    command = re.search(r"stage-frontend\.sh --target (\S+)", guide)
    assert command is not None, "the release procedure must show a staging command"
    assert command.group(1) == served[0], (
        f"the guide stages into {command.group(1)} but the proxy serves {served[0]}"
    )

    script = (DEPLOY / "stage-frontend.sh").read_text()
    assert served[0] in script, "the script's own usage text must name the served directory"


def test_the_maintenance_timer_is_named_after_its_unit() -> None:
    """systemd matches talimgo-maintenance.timer to talimgo-maintenance.service by name."""
    assert MAINTENANCE_TIMER.name.replace(".timer.example", "") == MAINTENANCE_UNIT.name.replace(
        ".service.example", ""
    )


def test_staging_refuses_unsafe_targets_and_never_writes_outside_them(tmp_path) -> None:
    """Every unsafe target is refused, and a refused run leaves no directory behind.

    `/` and `//` are in the list because stripping a trailing slash turns them into an empty string: the
    guard must reject the raw value before normalising it (found by this test).
    """
    working_directory = tmp_path / "cwd"
    working_directory.mkdir()
    for arguments in (
        (),
        ("--target", ""),
        ("--target", "relative/path"),
        ("--target", "/"),
        ("--target", "//"),
        ("--target", "/etc"),
        ("--target", "/etc/"),
        ("--target", "/srv"),
        ("--target", f"{tmp_path}/missing-parent/frontend"),
        ("--target", "/nope/../etc/talimgo"),
        ("--nope",),
    ):
        result = bash(
            DEPLOY / "stage-frontend.sh",
            *arguments,
            timeout=60,
            cwd=working_directory,
        )
        assert result.returncode != 0, f"{arguments} should have been refused"
        assert "refusing" in result.stderr or "unknown argument" in result.stderr

    assert list(working_directory.iterdir()) == [], "a refused run must not leave files behind"


def test_staging_reports_what_it_would_do_without_touching_anything(tmp_path) -> None:
    target = tmp_path / "frontend"
    result = bash(DEPLOY / "stage-frontend.sh", "--target", str(target), "--dry-run")
    assert result.returncode == 0, result.stderr
    assert "would" in result.stdout
    assert not target.exists(), "a dry run must not create the target"


def test_staging_refuses_a_build_that_fails_the_release_gate(tmp_path) -> None:
    """An insecure or local address in the artifact must stop the release, not just warn."""
    bad_dist = tmp_path / "bad"
    (bad_dist / "assets").mkdir(parents=True)
    (bad_dist / "index.html").write_text(
        '<!doctype html><script type="module" src="/assets/app.js"></script>'
    )
    (bad_dist / "assets" / "app.js").write_text('const api = "http://localhost:8000";')
    target = tmp_path / "frontend"

    if shell("-c", "command -v node").returncode != 0:
        pytest.skip("node is required to run the release gate")

    result = bash(
        DEPLOY / "stage-frontend.sh",
        "--target",
        str(target),
        "--dist",
        str(bad_dist),
        "--skip-build",
    )
    assert result.returncode == 1, result.stdout + result.stderr
    assert "local/private host" in result.stderr
    assert not target.exists(), "a refused release must not be published"


def test_staging_publishes_a_good_build_and_keeps_the_previous_release(tmp_path) -> None:
    dist = tmp_path / "dist"
    (dist / "assets").mkdir(parents=True)
    (dist / "index.html").write_text(
        '<!doctype html><link rel="stylesheet" href="/assets/index.css">'
        '<script type="module" src="/assets/index.js"></script>'
    )
    (dist / "assets" / "index.js").write_text('fetch("/api/health");')
    (dist / "assets" / "index.css").write_text("body{color:#111}")
    target = tmp_path / "frontend"

    first = bash(DEPLOY / "stage-frontend.sh", "--target", str(target), "--dist", str(dist), "--skip-build")
    assert first.returncode == 0, first.stderr
    assert (target / "index.html").is_file()

    (dist / "index.html").write_text(
        '<!doctype html><link rel="stylesheet" href="/assets/index.css">'
        '<script type="module" src="/assets/index.js"></script><p>second</p>'
    )
    second = bash(DEPLOY / "stage-frontend.sh", "--target", str(target), "--dist", str(dist), "--skip-build")
    assert second.returncode == 0, second.stderr
    assert (tmp_path / "frontend.previous" / "index.html").is_file(), "rollback copy missing"
    assert "second" in (target / "index.html").read_text()


class _HealthHandler(http.server.BaseHTTPRequestHandler):
    """Serves the API's recorded /api/health contract, or a configured failure."""

    payload = b'{"status": "ok", "version": "0.1.0"}'
    content_type = "application/json"
    status = 200

    def do_GET(self) -> None:
        body = self.payload
        self.send_response(self.status)
        self.send_header("Content-Type", self.content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format: str, *args: object) -> None:
        pass


def serve_once(handler: type[http.server.BaseHTTPRequestHandler]) -> tuple[str, threading.Thread]:
    server = http.server.HTTPServer(("127.0.0.1", 0), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return f"http://127.0.0.1:{server.server_port}", thread


def test_health_check_accepts_the_documented_contract() -> None:
    url, _ = serve_once(_HealthHandler)
    result = bash(DEPLOY / "health-check.sh", "--url", url, "--timeout", "5")
    assert result.returncode == 0, result.stderr
    assert "healthy" in result.stdout


def test_health_check_refuses_a_non_api_answer() -> None:
    """Exactly the deployed Vercel shell case: HTTP 200 but not TALIMGO's API answering."""

    class StaticHost(_HealthHandler):
        payload = b"<!doctype html><title>404: NOT_FOUND</title>"
        content_type = "text/html"

    url, _ = serve_once(StaticHost)
    result = bash(DEPLOY / "health-check.sh", "--url", url, "--timeout", "5")
    assert result.returncode == 1
    assert "did not answer with JSON" in result.stderr


def test_health_check_refuses_a_non_ok_status() -> None:
    class Degraded(_HealthHandler):
        payload = b'{"status": "degraded"}'

    url, _ = serve_once(Degraded)
    result = bash(DEPLOY / "health-check.sh", "--url", url, "--timeout", "5")
    assert result.returncode == 1
    assert "status=" in result.stderr


def test_health_check_usage_errors_are_distinct_from_unhealthy() -> None:
    """Exit code 2 means 'called wrongly'; 1 means 'the API is not healthy'. Supervisors depend on it."""
    for arguments in (("--url", "ftp://host"), ("--timeout", "abc"), ("--wait", "-1"), ("--nope",)):
        result = bash(DEPLOY / "health-check.sh", *arguments)
        assert result.returncode == 2, f"{arguments} -> {result.returncode}"


def test_health_check_fails_when_nothing_is_listening() -> None:
    with socket.socket() as probe:
        probe.bind(("127.0.0.1", 0))
        closed_port = probe.getsockname()[1]
    result = bash(DEPLOY / "health-check.sh", "--url", f"http://127.0.0.1:{closed_port}", "--timeout", "2")
    assert result.returncode == 1
    assert "unhealthy" in result.stderr


def proxy_smoke_step() -> str:
    """The CI edge-smoke job's text, from its job id to the next job."""
    workflow = CI_WORKFLOW.read_text()
    start = workflow.index("proxy-tls-smoke:")
    end = workflow.index("\n  local-only-ai:", start)
    return workflow[start:end]


def test_edge_smoke_waits_for_the_upstream_before_asserting_through_the_edge() -> None:
    """Regression for push run 39716615747 (the same SHA passed as PR run 39716622524).

    The step probed only the static document, which the edge serves from disk, then immediately
    asserted on the first proxied response. When the test upstream's interpreter took longer to
    start than the static checks took to run, that request read the edge's own 502 page and the
    JSON assertion failed on it. Waiting must stay in front of the first proxied request, both
    readiness waits must fail the step instead of falling through, and a failure must print the
    logs that say which response the edge returned.
    """
    step = proxy_smoke_step()
    upstream_wait = step.index("http://127.0.0.1:8000/api/health")
    first_proxied_request = step.index("ci-edge-passthrough")
    assert upstream_wait < first_proxied_request, "the upstream wait must precede the first proxied request"
    assert 'test "$upstream_ready" = "1"' in step, "an upstream that never starts must fail the step"
    assert 'test "$edge_ready" = "1"' in step, (
        "an edge that never serves must fail the step, not fall through"
    )
    assert "edge smoke diagnostics" in step, "a failure must print its evidence"
    assert "/var/log/nginx/talimgo-error.log" in step, "the edge log is part of that evidence"
    assert step.count("talimgo-upstream.log") >= 2, "the upstream log is written once and dumped on failure"


def test_edge_smoke_keeps_its_trust_boundary_assertions() -> None:
    """The readiness fix must not weaken what the job proves about the edge.

    These are the security properties of the shipped example: an API refusal passes through with its
    own body and Retry-After, client-supplied forwarding headers are replaced (never trusted), the
    plain-HTTP entry point redirects keeping path and query, and the auth location is rate limited.
    """
    step = proxy_smoke_step()
    for assertion in (
        "'301|https://talimgo.example/demo?from=http'",
        "max-age=31536000",
        'assert d["detail"] == "api-level limit reached"',
        "'^Retry-After: 7'",
        'h["X-Forwarded-Proto"] == "https"',
        'h["X-Forwarded-For"] == "127.0.0.1"',
        'h["Forwarded"] is None',
        "test \"$auth_status\" = '429'",
    ):
        assert assertion in step, f"missing edge assertion: {assertion}"


def test_ci_upstream_serves_the_contract_the_edge_smoke_asserts() -> None:
    """The fixture behind the edge: exercised directly, on an ephemeral loopback port.

    If this contract drifts, the CI job fails at the edge and reads like a proxy defect. Checking the
    fixture on its own keeps the two apart. Threading and the loopback bind are asserted on the
    source because they are properties of how the CI job runs it (127.0.0.1:8000), not of a handler
    bound to a test port.
    """
    spec = importlib.util.spec_from_file_location("talimgo_ci_upstream", CI_UPSTREAM)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), module.Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    port = server.server_address[1]
    try:
        refusal = http.client.HTTPConnection("127.0.0.1", port, timeout=5)
        refusal.request("GET", "/api/ci-edge-passthrough")
        refusal_response = refusal.getresponse()
        refusal_body = refusal_response.read()
        assert refusal_response.status == 429
        assert refusal_response.getheader("Retry-After") == "7"
        assert json.loads(refusal_body) == {"detail": "api-level limit reached"}
        refusal.close()

        echo = http.client.HTTPConnection("127.0.0.1", port, timeout=5)
        echo.request(
            "GET",
            "/api/health",
            headers={"X-Forwarded-Proto": "https", "X-Forwarded-For": "127.0.0.1"},
        )
        echo_response = echo.getresponse()
        echoed = json.loads(echo_response.read())
        assert echo_response.status == 200
        assert echoed["headers"]["X-Forwarded-Proto"] == "https"
        assert echoed["headers"]["X-Forwarded-For"] == "127.0.0.1"
        assert echoed["headers"]["Forwarded"] is None
        echo.close()

        outside = http.client.HTTPConnection("127.0.0.1", port, timeout=5)
        outside.request("GET", "/not-an-api-path")
        assert outside.getresponse().status == 404
        outside.close()
    finally:
        server.shutdown()
        server.server_close()

    source = CI_UPSTREAM.read_text()
    assert "ThreadingHTTPServer" in source
    assert '("127.0.0.1", 8000)' in source, "the fixture must stay on loopback, where the example points"
