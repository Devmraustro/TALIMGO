"""Settings-file resolution: deterministic, independent of the working directory, and documented.

The bug this locks out: ``env_file=".env"`` was resolved against the *process* working directory, so
the README's instruction (``cp ../.env.example ../.env``) produced a file the app never read when it
was started from ``backend/``.
"""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from app.config import Settings, get_settings, reset_settings_cache

BACKEND_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = BACKEND_ROOT.parent


@pytest.fixture()
def _clean_env(monkeypatch):
    for key in [key for key in os.environ if key.startswith("TALIMGO_")]:
        monkeypatch.delenv(key, raising=False)
    reset_settings_cache()
    yield
    reset_settings_cache()


def test_env_file_next_to_the_package_is_read_regardless_of_cwd(tmp_path, monkeypatch, _clean_env):
    env_file = BACKEND_ROOT / ".env"
    existed = env_file.exists()
    backup = env_file.read_text(encoding="utf-8") if existed else None
    try:
        env_file.write_text("TALIMGO_ALLOWED_ORIGINS=http://from-backend-env\n", encoding="utf-8")
        for cwd in (tmp_path, BACKEND_ROOT, REPO_ROOT):
            monkeypatch.chdir(cwd)
            reset_settings_cache()
            assert get_settings().allowed_origins == "http://from-backend-env", f"cwd={cwd}"
    finally:
        if backup is None:
            env_file.unlink(missing_ok=True)
        else:
            env_file.write_text(backup, encoding="utf-8")


def test_the_backend_file_wins_over_a_repository_root_file(tmp_path, monkeypatch, _clean_env):
    backend_env = BACKEND_ROOT / ".env"
    root_env = REPO_ROOT / ".env"
    backups = {
        path: (path.exists(), path.read_text() if path.exists() else None) for path in (backend_env, root_env)
    }
    try:
        root_env.write_text("TALIMGO_ALLOWED_ORIGINS=http://from-root\n", encoding="utf-8")
        backend_env.write_text("TALIMGO_ALLOWED_ORIGINS=http://from-backend\n", encoding="utf-8")
        reset_settings_cache()
        assert get_settings().allowed_origins == "http://from-backend"
    finally:
        for path, (existed, content) in backups.items():
            if existed and content is not None:
                path.write_text(content, encoding="utf-8")
            else:
                path.unlink(missing_ok=True)


def test_the_environment_variable_file_override_is_honoured(tmp_path, monkeypatch, _clean_env):
    custom = tmp_path / "custom.env"
    custom.write_text("TALIMGO_ALLOWED_ORIGINS=http://from-override\n", encoding="utf-8")
    monkeypatch.setenv("TALIMGO_ENV_FILE", str(custom))
    reset_settings_cache()
    assert get_settings().allowed_origins == "http://from-override"


def test_the_example_file_documents_every_setting() -> None:
    """A configuration file that drifts from the code is worse than none."""
    example = (BACKEND_ROOT / ".env.example").read_text(encoding="utf-8")
    missing = [
        f"TALIMGO_{name.upper()}"
        for name in Settings.model_fields
        if name not in {"env_file"} and f"TALIMGO_{name.upper()}" not in example
    ]
    assert missing == [], f"settings missing from backend/.env.example: {missing}"


def test_the_example_file_contains_no_real_secret() -> None:
    example = (BACKEND_ROOT / ".env.example").read_text(encoding="utf-8")
    assert "change-me" in example, "the example must show an obvious placeholder, not a usable secret"
    for line in example.splitlines():
        if line.startswith("TALIMGO_SESSION_SECRET="):
            assert line.split("=", 1)[1].strip() in {"change-me-in-production-use-32-bytes-of-random"}
