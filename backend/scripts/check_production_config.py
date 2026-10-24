"""Preflight check for a production configuration, run before starting the API on a real host.

    python scripts/check_production_config.py

It reads the same settings the API reads (`app.config`) and applies the production requirements from
docs/DEPLOYMENT.md, including the one the application itself does not enforce: PostgreSQL instead of
SQLite. Nothing here prints a configuration *value*: results name the setting and the verdict only, so
the output is safe to paste into a ticket.

Exit code 0 means every check passed; 1 means at least one failed and the API must not be deployed.
"""

from __future__ import annotations

from sqlalchemy.engine import make_url

DEFAULT_SECRET_MARKERS = ("dev-only", "change-me", "changeme")


def _report(name: str, ok: bool, detail: str) -> bool:
    print(f"{'PASS' if ok else 'FAIL'}  {name} :: {detail}")
    return ok


def check_environment(env: str) -> bool:
    return _report(
        "TALIMGO_ENV",
        env == "production",
        "production" if env == "production" else f"{env!r} is not a production environment",
    )


def check_session_secret(secret: str) -> bool:
    """Mirrors the application's own production rule, without ever echoing the value."""
    weak_marker = next((marker for marker in DEFAULT_SECRET_MARKERS if marker in secret.lower()), "")
    ok = len(secret) >= 32 and not weak_marker
    detail = "32+ characters, no placeholder marker"
    if weak_marker:
        detail = f"contains the placeholder marker {weak_marker!r}"
    elif len(secret) < 32:
        detail = f"only {len(secret)} characters"
    return _report("TALIMGO_SESSION_SECRET", ok, detail)


def check_database(database_url: str) -> bool:
    """The application does not refuse SQLite in production; this check does, per docs/DEPLOYMENT.md."""
    try:
        url = make_url(database_url)
    except Exception:
        return _report("TALIMGO_DATABASE_URL", False, "not a parseable SQLAlchemy URL")
    dialect = url.get_backend_name()
    ok = dialect == "postgresql"
    detail = (
        f"driver {url.get_driver_name()} on {dialect}"
        if ok
        else f"{dialect!r} is a development convenience only; production requires PostgreSQL 14+"
    )
    return _report("TALIMGO_DATABASE_URL", ok, detail)


def check_origins(origins: list[str]) -> bool:
    ok = bool(origins) and all(origin.startswith(("http://", "https://")) for origin in origins)
    return _report(
        "TALIMGO_ALLOWED_ORIGINS",
        ok,
        f"{len(origins)} explicit origin(s)" if ok else "no usable origin listed",
    )


def check_local_ai(ai_enabled: bool, ai_model: str, ai_base_url: str) -> bool:
    """AI must stay off, or point at a local runtime with a named model."""
    if not ai_enabled:
        return _report("TALIMGO_AI_ENABLED", True, "tutoring disabled (no local runtime provisioned)")
    from app.ai.policy import is_local_host

    host = make_url(ai_base_url).host or ""
    ok = bool(ai_model.strip()) and is_local_host(host)
    detail = (
        f"model named, endpoint host is local ({'present' if host else 'missing'})"
        if ok
        else f"AI is enabled with model={'set' if ai_model.strip() else 'empty'} and a "
        f"{'local' if is_local_host(host) else 'non-local'} endpoint"
    )
    return _report("local-only AI", ok, detail)


def main() -> None:
    # The application's own validators run first: a weak secret, a wildcard origin or a non-local AI
    # endpoint raises here exactly as it would at startup, which is the most useful failure to see.
    from app.config import get_settings

    try:
        settings = get_settings()
    except Exception as exc:  # pydantic ValidationError, ValueError from the validators
        print(f"FAIL  startup configuration rejected :: {exc.__class__.__name__}")
        raise SystemExit(1) from exc

    checks = [
        check_environment(settings.env),
        check_session_secret(settings.session_secret),
        check_database(settings.database_url),
        check_origins(settings.origin_list),
        check_local_ai(settings.ai_enabled, settings.ai_model, settings.ai_base_url),
        _report(
            "interactive API docs",
            settings.env == "production",
            "served only outside production",
        ),
    ]

    if not all(checks):
        raise SystemExit("Production preflight FAILED: fix the checks above before deploying.")
    print("Production preflight passed. Start the API with the same environment.")


if __name__ == "__main__":
    main()
