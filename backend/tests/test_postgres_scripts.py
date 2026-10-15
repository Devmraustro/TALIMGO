"""Regression tests for the PostgreSQL rehearsal scripts.

These run without a PostgreSQL server: they cover the refusals that decide whether a script is
allowed to touch a database at all, and the cleanup/reporting behaviour that decides what an operator
sees when a rehearsal fails. The rehearsal itself is exercised for real in the CI
``postgres-integration`` job.
"""

from __future__ import annotations

import importlib.util
import subprocess
import sys
import types
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"

VALID_URL = "postgresql+psycopg://postgres:postgres@127.0.0.1:5432/talimgo"


def load_script(name: str) -> types.ModuleType:
    """Import a scripts/*.py file by path (scripts/ is not an importable package)."""
    path = SCRIPTS / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def backup_restore() -> types.ModuleType:
    return load_script("postgres_backup_restore")


@pytest.mark.parametrize(
    ("url", "expected"),
    [
        # A rehearsal must never be pointed at another host, another database or another driver.
        ("sqlite:///./app.db", "must use postgresql+psycopg"),
        ("postgresql+psycopg://postgres:postgres@db.example.com:5432/talimgo", "loopback"),
        ("postgresql+psycopg://postgres:postgres@10.0.0.5:5432/talimgo", "loopback"),
        # 127.0.0.2 is loopback at the OS level but is not accepted: only the two documented names are.
        ("postgresql+psycopg://postgres:postgres@127.0.0.2:5432/talimgo", "loopback"),
        ("postgresql+psycopg://postgres:postgres@127.0.0.1:5432/zaroprod", "loopback"),
        ("postgresql+psycopg://postgres:postgres@127.0.0.1:5432/postgres", "loopback"),
        # No password means PGPASSWORD would be empty; refuse rather than guess a credential.
        ("postgresql+psycopg://postgres@127.0.0.1:5432/talimgo", "username and password"),
        ("", "must use postgresql+psycopg"),
    ],
)
def test_backup_restore_refuses_unapproved_targets(
    backup_restore: types.ModuleType,
    monkeypatch: pytest.MonkeyPatch,
    url: str,
    expected: str,
) -> None:
    monkeypatch.setenv("TALIMGO_DATABASE_URL", url)
    with pytest.raises(SystemExit) as refused:
        backup_restore.main()
    assert expected in str(refused.value)


@pytest.mark.parametrize(
    "module_name", ["postgres_smoke", "postgres_legacy_migration", "postgres_backup_restore"]
)
def test_scripts_refuse_a_non_psycopg_url(module_name: str, monkeypatch: pytest.MonkeyPatch) -> None:
    module = load_script(module_name)
    monkeypatch.setenv("TALIMGO_DATABASE_URL", "sqlite:///./ci-test.db")
    with pytest.raises(SystemExit) as refused:
        module.main()
    assert "SystemExit" not in str(refused.value)


def test_cleanup_failure_is_reported_not_raised(
    backup_restore: types.ModuleType, monkeypatch: pytest.MonkeyPatch
) -> None:
    def failing_run(args: list[str], env: dict[str, str]) -> None:
        raise subprocess.CalledProcessError(1, args)

    monkeypatch.setattr(backup_restore, "run", failing_run)
    error = backup_restore.run_cleanup(["dropdb", "--if-exists", "talimgo_restore"], {})
    assert isinstance(error, subprocess.CalledProcessError)


def _fake_run_factory(
    calls: list[list[str]], *, fail_dropdb_calls: set[int] = frozenset(), fail_restore: bool = False
):
    counter = {"dropdb": 0}

    def fake_run(args: list[str], env: dict[str, str]) -> None:
        calls.append(list(args))
        if args[0] == "pg_dump":
            Path(args[args.index("--file") + 1]).write_bytes(b"dump")
            return
        if args[0] == "dropdb":
            counter["dropdb"] += 1
            if counter["dropdb"] in fail_dropdb_calls:
                raise subprocess.CalledProcessError(1, args)
            return
        if args[0] == "pg_restore" and fail_restore:
            raise subprocess.CalledProcessError(1, args)

    return fake_run


def test_a_failed_restore_is_not_masked_by_a_failed_cleanup(
    backup_restore: types.ModuleType, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The error an operator sees must be the restore failure, not the cleanup that followed it."""
    monkeypatch.setenv("TALIMGO_DATABASE_URL", VALID_URL)
    calls: list[list[str]] = []
    # second dropdb call is the cleanup one (the first is the pre-restore drop of the scratch DB)
    monkeypatch.setattr(
        backup_restore,
        "run",
        _fake_run_factory(calls, fail_dropdb_calls={2}, fail_restore=True),
    )
    with pytest.raises(subprocess.CalledProcessError) as failure:
        backup_restore.main()
    assert failure.value.cmd[0] == "pg_restore"
    assert [call[0] for call in calls] == ["pg_dump", "dropdb", "createdb", "pg_restore", "dropdb"]


def test_a_leftover_scratch_database_fails_the_run(
    backup_restore: types.ModuleType, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Cleanup failure on an otherwise successful rehearsal is a failure: state was left behind."""
    monkeypatch.setenv("TALIMGO_DATABASE_URL", VALID_URL)
    calls: list[list[str]] = []
    monkeypatch.setattr(
        backup_restore, "run", _fake_run_factory(calls, fail_dropdb_calls={2}, fail_restore=False)
    )
    monkeypatch.setattr(backup_restore, "table_counts", lambda url: {"users": 1, "goals": 1})
    monkeypatch.setattr(backup_restore, "alembic_revision", lambda url: "c4a7d9e12f60")
    monkeypatch.setattr(
        backup_restore.subprocess,
        "run",
        lambda *a, **k: subprocess.CompletedProcess(a[0] if a else [], 0),
    )
    with pytest.raises(SystemExit) as refused:
        backup_restore.main()
    assert "still on the server" in str(refused.value)
    assert [call[0] for call in calls].count("dropdb") == 2


@pytest.mark.parametrize(
    "url",
    [
        VALID_URL,
        # "localhost" is the second documented loopback name and must be accepted.
        "postgresql+psycopg://postgres:postgres@localhost:5432/talimgo",
    ],
)
def test_a_successful_rehearsal_drops_the_scratch_database(
    backup_restore: types.ModuleType,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture,
    url: str,
) -> None:
    monkeypatch.setenv("TALIMGO_DATABASE_URL", url)
    calls: list[list[str]] = []
    monkeypatch.setattr(backup_restore, "run", _fake_run_factory(calls))
    monkeypatch.setattr(backup_restore, "table_counts", lambda url: {"users": 1, "goals": 1})
    monkeypatch.setattr(backup_restore, "alembic_revision", lambda url: "c4a7d9e12f60")
    monkeypatch.setattr(
        backup_restore.subprocess,
        "run",
        lambda *a, **k: subprocess.CompletedProcess(a[0] if a else [], 0),
    )
    backup_restore.main()
    assert [call[0] for call in calls] == ["pg_dump", "dropdb", "createdb", "pg_restore", "dropdb"]
    assert "backup/restore passed" in capsys.readouterr().out


class _FakeResult:
    def __init__(self, count: int) -> None:
        self._count = count

    def scalar_one(self) -> int:
        return self._count


class _FakeConnection:
    def __init__(self, count: int) -> None:
        self._count = count

    def execute(self, *_args: object, **_kwargs: object) -> _FakeResult:
        return _FakeResult(self._count)

    def __enter__(self) -> _FakeConnection:
        return self

    def __exit__(self, *_exc: object) -> None:
        return None


class _FakeEngine:
    def __init__(self, count: int) -> None:
        self._count = count

    def connect(self) -> _FakeConnection:
        return _FakeConnection(self._count)

    def dispose(self) -> None:
        return None


@pytest.fixture
def legacy_migration() -> types.ModuleType:
    return load_script("postgres_legacy_migration")


def test_legacy_migration_refuses_a_database_that_is_not_empty(
    legacy_migration: types.ModuleType, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The target must be empty: `upgrade <previous revision>` would *downgrade* a populated database.

    Without this guard the rehearsal silently rewrites a database that already has a schema (and then
    fails on the legacy insert with a NotNullViolation that looks like a migration defect). Alembic must
    never be reached in that case.
    """
    monkeypatch.setenv("TALIMGO_DATABASE_URL", VALID_URL)
    monkeypatch.setattr(legacy_migration, "create_engine", lambda *_a, **_k: _FakeEngine(23))

    def should_not_run(*_args: object, **_kwargs: object) -> None:
        raise AssertionError("Alembic must not be invoked on a database that is not empty")

    monkeypatch.setattr(legacy_migration, "run_alembic", should_not_run)

    with pytest.raises(SystemExit) as refused:
        legacy_migration.main()
    assert "needs an empty database" in str(refused.value)


def test_legacy_migration_proceeds_on_an_empty_database(
    legacy_migration: types.ModuleType, monkeypatch: pytest.MonkeyPatch
) -> None:
    """An empty database passes the guard and reaches the rehearsal (which is then stubbed out)."""
    monkeypatch.setenv("TALIMGO_DATABASE_URL", VALID_URL)
    monkeypatch.setattr(legacy_migration, "create_engine", lambda *_a, **_k: _FakeEngine(0))
    calls: list[tuple[str, ...]] = []

    def stop_after_alembic(env: dict, *arguments: str) -> None:
        calls.append(arguments)
        raise SystemExit("stub reached Alembic")

    monkeypatch.setattr(legacy_migration, "run_alembic", stop_after_alembic)

    with pytest.raises(SystemExit) as stopped:
        legacy_migration.main()
    assert "stub reached Alembic" in str(stopped.value)
    assert calls and calls[0] == ("upgrade", legacy_migration.LEGACY_REVISION)
