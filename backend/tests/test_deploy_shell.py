"""Tests for the helper that finds a POSIX shell and adapts the paths given to it.

`test_deploy_artifacts.py` exercises the deployment scripts through this helper. These tests
cover the helper itself, so a defect in the discovery or the path translation is reported as
what it is, instead of appearing as a mysterious failure inside a deployment script.

Everything here is platform-independent unless it says otherwise: the same file runs in CI on
Ubuntu and on a Windows developer machine.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

from tests.deploy_shell import (
    SHELL_VARIABLE,
    ShellUnavailable,
    run_bash,
    shell_environment,
    shell_executable,
    shell_path,
)


def test_a_posix_path_is_never_rewritten() -> None:
    """On Linux the scripts are handed paths the shell already understands."""
    assert shell_path("/srv/talimgo/frontend/dist") == "/srv/talimgo/frontend/dist"


def test_a_url_is_never_rewritten() -> None:
    """The health check is given a URL; it is not a filesystem path and must survive intact."""
    assert shell_path("http://127.0.0.1:8000") == "http://127.0.0.1:8000"
    assert shell_path("https://api.talimgo.test/api/health") == "https://api.talimgo.test/api/health"


def test_translating_a_path_twice_changes_nothing() -> None:
    """The translation is applied to the script and to its arguments; it must be idempotent."""
    original = str(Path("C:/Users/someone/dist")) if os.name == "nt" else "/srv/talimgo/dist"
    once = shell_path(original)
    assert shell_path(once) == once


@pytest.mark.skipif(os.name != "nt", reason="Windows path syntax")
def test_a_windows_path_becomes_the_form_git_bash_understands() -> None:
    assert shell_path(r"C:\Users\someone\dist") == "/c/Users/someone/dist"


def test_the_override_selects_the_shell(monkeypatch: pytest.MonkeyPatch) -> None:
    """`TALIMGO_TEST_BASH` is the documented way to choose the shell explicitly."""
    monkeypatch.setenv(SHELL_VARIABLE, sys.executable)
    assert shell_executable() == sys.executable


def test_the_override_is_honoured_even_after_the_shell_was_resolved(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path,
) -> None:
    """The automatic discovery is cached; the override is not, so it always wins.

    Without this, a shell resolved once would be used for the rest of the session: a stale shell
    would then run the deployment scripts even though another one was asked for.
    """
    chosen = tmp_path / "chosen-bash"
    chosen.write_text("", encoding="utf-8")
    shell_executable()
    monkeypatch.setenv(SHELL_VARIABLE, str(chosen))
    assert shell_executable() == str(chosen)


def test_an_override_that_is_not_a_file_is_reported(monkeypatch: pytest.MonkeyPatch, tmp_path) -> None:
    """A typo in the override must fail with the reason, not silently fall back to another shell."""
    monkeypatch.setenv(SHELL_VARIABLE, str(tmp_path / "no-such-bash"))
    with pytest.raises(ShellUnavailable) as failure:
        shell_executable()
    assert SHELL_VARIABLE in str(failure.value)
    assert "no-such-bash" in str(failure.value)


@pytest.mark.skipif(os.name != "nt", reason="SystemRoot is a Windows variable")
def test_the_shell_environment_keeps_the_platform_variables() -> None:
    """A child process needs the platform's own variables.

    The interpreter cannot initialise its socket layer without `SystemRoot`, so the environment
    the scripts run in is inherited rather than replaced.
    """
    environment = shell_environment()
    # Windows stores the variable under an upper-case name; the lookup is case-insensitive there.
    inherited = {key.upper(): value for key, value in environment.items()}
    assert inherited.get("SYSTEMROOT") == os.environ.get("SYSTEMROOT")
    assert environment.get("PATH"), "the shell still needs a search path"


@pytest.mark.skipif(os.name != "nt", reason="the shim is a Windows workaround")
def test_the_python3_shim_runs_the_interpreter_the_tests_use() -> None:
    """`health-check.sh` requires a `python3`; Windows only has the Microsoft Store alias.

    The shim must therefore resolve, and it must run the interpreter that is running the tests.
    """
    result = run_bash(["-c", "python3 -c 'import sys; print(sys.executable)'"])
    assert result.returncode == 0, result.stderr
    assert Path(result.stdout.strip()).name.lower() == Path(sys.executable).name.lower()
