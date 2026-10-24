"""Rehearse PostgreSQL backup and restore against a disposable local CI service.

This deliberately refuses arbitrary database targets: it only operates on the CI source database
named "talimgo" at loopback and a dedicated scratch database named "talimgo_restore".

The dump lives in a temporary directory and the scratch database is dropped on the way out whether
the rehearsal succeeded or failed. A failure to drop it is reported and makes the script fail without
replacing the error that caused the run to fail in the first place.
"""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.engine import make_url

SOURCE_DATABASE = "talimgo"
RESTORE_DATABASE = "talimgo_restore"
EXPECTED_HOSTS = {"127.0.0.1", "localhost"}


def run(args: list[str], env: dict[str, str]) -> None:
    subprocess.run(args, check=True, env=env)


def run_cleanup(args: list[str], env: dict[str, str]) -> subprocess.CalledProcessError | None:
    """Drop the scratch database, returning a failure instead of raising it.

    Cleanup runs in a ``finally`` block. Raising here would replace the error that actually made the
    rehearsal fail, sending whoever reads the output after the wrong problem, so the failure is
    returned for the caller to report. Leftover state is still never silent: the caller exits
    non-zero when the scratch database could not be removed.
    """
    try:
        run(args, env)
    except subprocess.CalledProcessError as exc:
        return exc
    return None


def connection_args(url, database: str | None = None) -> list[str]:
    args = [
        "--host",
        url.host or "127.0.0.1",
        "--port",
        str(url.port or 5432),
        "--username",
        url.username or "postgres",
    ]
    if database is not None:
        args.extend(["--dbname", database])
    return args


def table_counts(database_url: str) -> dict[str, int]:
    engine = create_engine(database_url, pool_pre_ping=True)
    try:
        with engine.connect() as connection:
            names = inspect(connection).get_table_names(schema="public")
            counts: dict[str, int] = {}
            for name in sorted(names):
                quoted = name.replace('"', '""')
                counts[name] = int(
                    connection.execute(text(f'SELECT COUNT(*) FROM public."{quoted}"')).scalar_one()
                )
            return counts
    finally:
        engine.dispose()


def alembic_revision(database_url: str) -> str:
    engine = create_engine(database_url, pool_pre_ping=True)
    try:
        with engine.connect() as connection:
            return str(connection.execute(text("SELECT version_num FROM alembic_version")).scalar_one())
    finally:
        engine.dispose()


def main() -> None:
    raw_url = os.environ.get("TALIMGO_DATABASE_URL", "")
    if not raw_url.startswith("postgresql+psycopg://"):
        raise SystemExit("Refusing to run: TALIMGO_DATABASE_URL must use postgresql+psycopg.")
    source_url = make_url(raw_url)
    if source_url.database != SOURCE_DATABASE or source_url.host not in EXPECTED_HOSTS:
        raise SystemExit("Refusing to run: source must be loopback PostgreSQL database 'talimgo'.")
    if not source_url.username or source_url.password is None:
        raise SystemExit("Refusing to run: PostgreSQL username and password are required.")

    env = os.environ.copy()
    env["PGPASSWORD"] = source_url.password
    env.setdefault("PGCONNECT_TIMEOUT", "5")
    source_args = connection_args(source_url)
    restore_url = source_url.set(database=RESTORE_DATABASE)
    restore_url_string = restore_url.render_as_string(hide_password=False)

    with tempfile.TemporaryDirectory(prefix="talimgo-pg-restore-") as temp_dir:
        dump_path = os.path.join(temp_dir, "talimgo.dump")
        cleanup_error: subprocess.CalledProcessError | None = None
        try:
            run(
                [
                    "pg_dump",
                    *source_args,
                    "--format=custom",
                    "--no-owner",
                    "--no-acl",
                    "--file",
                    dump_path,
                    SOURCE_DATABASE,
                ],
                env,
            )
            if not os.path.isfile(dump_path) or os.path.getsize(dump_path) == 0:
                raise AssertionError("pg_dump did not create a non-empty backup.")

            run(["dropdb", "--if-exists", *source_args, RESTORE_DATABASE], env)
            run(
                [
                    "createdb",
                    *source_args,
                    "--owner",
                    source_url.username,
                    RESTORE_DATABASE,
                ],
                env,
            )
            run(
                [
                    "pg_restore",
                    *source_args,
                    "--dbname",
                    RESTORE_DATABASE,
                    "--exit-on-error",
                    "--no-owner",
                    "--no-acl",
                    dump_path,
                ],
                env,
            )

            source_counts = table_counts(raw_url)
            restored_counts = table_counts(restore_url_string)
            if source_counts != restored_counts:
                raise AssertionError(
                    f"Backup/restore row counts differ. Source: {source_counts}; restored: {restored_counts}"
                )
            if source_counts.get("users", 0) < 1 or source_counts.get("goals", 0) < 1:
                raise AssertionError("Backup rehearsal must include a populated user and goal.")
            source_revision = alembic_revision(raw_url)
            restored_revision = alembic_revision(restore_url_string)
            if source_revision != restored_revision:
                raise AssertionError(
                    f"Alembic revision changed across restore: {source_revision} != {restored_revision}"
                )

            restored_env = env.copy()
            restored_env["TALIMGO_DATABASE_URL"] = restore_url_string
            subprocess.run(
                [sys.executable, "scripts/postgres_smoke.py"],
                check=True,
                env=restored_env,
            )
            print(
                "PostgreSQL backup/restore passed: custom dump restored, all public table row counts "
                "and Alembic revision match, and restored API health/account/session/goal smoke passed."
            )
        finally:
            cleanup_error = run_cleanup(["dropdb", "--if-exists", *source_args, RESTORE_DATABASE], env)
            if cleanup_error is not None:
                # Printed, not raised: if the rehearsal already failed, that error is the useful one.
                print(
                    f"warning: the scratch database {RESTORE_DATABASE} could not be dropped "
                    f"({cleanup_error.cmd[0]} exited {cleanup_error.returncode})",
                    file=sys.stderr,
                )

    if cleanup_error is not None:
        raise SystemExit(
            f"Backup rehearsal finished but the scratch database {RESTORE_DATABASE} is still on the "
            "server. Remove it before relying on the next run's results."
        )


if __name__ == "__main__":
    main()
