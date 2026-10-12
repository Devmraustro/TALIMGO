"""Consistency checks for the checked-in deployment artifacts.

The unit files and shell helpers under `deploy/` are what an operator actually installs, so they are
tested for the properties that matter even though this environment cannot start systemd: the start
order the deployment guide promises, the hardening directives, and the refusal paths of the scripts.
The behaviours that need a real host (installing units, serving through Nginx, a real certificate) are
listed as untested in docs/DEPLOYMENT.md.
"""

from __future__ import annotations

import http.server
import os
import socket
import subprocess
import sys
import threading
from pathlib import Path

import pytest

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
BACKEND = REPOSITORY_ROOT / "backend"
DEPLOY = REPOSITORY_ROOT / "deploy"
API_UNIT = DEPLOY / "systemd" / "talimgo-api.service.example"
MAINTENANCE_UNIT = DEPLOY / "systemd" / "talimgo-maintenance.service.example"
MAINTENANCE_TIMER = DEPLOY / "systemd" / "talimgo-maintenance.timer.example"


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


def bash(script: Path, *arguments: str, timeout: float = 30) -> subprocess.CompletedProcess:
    return subprocess.run(["bash", str(script), *arguments], capture_output=True, text=True, timeout=timeout)


@pytest.mark.parametrize("script", ["stage-frontend.sh", "health-check.sh"])
def test_shell_helpers_parse(script: str) -> None:
    syntax = subprocess.run(["bash", "-n", str(DEPLOY / script)], capture_output=True, text=True, timeout=30)
    assert syntax.returncode == 0, syntax.stderr
    assert (DEPLOY / script).stat().st_mode & 0o111, f"{script} must be executable"


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
    """
    database = tmp_path / "maintenance.db"
    environment = {
        "PATH": os.environ.get("PATH", ""),
        "HOME": str(tmp_path),
        "TALIMGO_ENV": "test",
        "TALIMGO_DATABASE_URL": f"sqlite+pysqlite:///{database}",
        "TALIMGO_SESSION_SECRET": "deploy-artifact-test-session-secret-0001",
        "TALIMGO_AI_ENABLED": "false",
    }
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
        result = subprocess.run(
            ["bash", str(DEPLOY / "stage-frontend.sh"), *arguments],
            capture_output=True,
            text=True,
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

    if subprocess.run(["bash", "-c", "command -v node"], capture_output=True).returncode != 0:
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
