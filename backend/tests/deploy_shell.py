"""Run the checked-in deployment scripts with a POSIX shell, whichever host the tests run on.

The files under `deploy/` are Linux deployment artifacts: systemd units, absolute POSIX paths, an
Nginx example. CI runs this suite on `ubuntu-latest`, where `bash` is already on `PATH` and every
path is already POSIX, so everything below is a pass-through on that platform.

A Windows developer normally has Git for Windows (MSYS2 Bash) rather than a Linux shell. That Bash
is not on `PATH` by default, it spells paths `/c/...` rather than `C:\\...`, and Windows has no
`python3` — only the Microsoft Store alias, which opens the Store instead of running Python. This
module resolves the shell once, translates the paths the scripts are handed, and provides the
interpreter the health check asks for, so the deployment tests keep their meaning on every platform
instead of being skipped.

`TALIMGO_TEST_BASH` selects the shell explicitly when the automatic resolution is not the one the
developer wants.
"""

from __future__ import annotations

import atexit
import functools
import os
import re
import shutil
import subprocess
import sys
import tempfile
from collections.abc import Sequence
from pathlib import Path

SHELL_VARIABLE = "TALIMGO_TEST_BASH"
WINDOWS_ABSOLUTE_PATH = re.compile(r"^[A-Za-z]:[\\/]")


class ShellUnavailable(RuntimeError):
    """No Bash executable could be found for the deployment scripts."""


def _git_for_windows_bash_candidates() -> list[Path]:
    """Where Git for Windows installs Bash, derived from the environment.

    Nothing here is one developer's personal path: the roots come from the system variables
    `ProgramFiles`, `ProgramFiles(x86)` and `LOCALAPPDATA`, so the same code finds the Bash of
    every Git for Windows installation on the machine.
    """
    candidates: list[Path] = []
    for variable in ("ProgramW6432", "ProgramFiles", "ProgramFiles(x86)", "LOCALAPPDATA"):
        root = os.environ.get(variable)
        if not root:
            continue
        candidates.append(Path(root) / "Git" / "bin" / "bash.exe")
        candidates.append(Path(root) / "Git" / "usr" / "bin" / "bash.exe")
    return candidates


def _is_wsl_launcher(path: str) -> bool:
    """Whether this is the `bash.exe` in System32, which is the WSL launcher and not a shell.

    The launcher needs a WSL distribution and speaks `/mnt/c/...` paths, not the `/c/...` form
    Git Bash uses, so the translation in `shell_path` would not apply to it.
    """
    system_root = os.environ.get("SYSTEMROOT", r"C:\Windows")
    launcher = Path(system_root) / "System32" / "bash.exe"
    try:
        return Path(path).resolve() == launcher.resolve()
    except OSError:  # pragma: no cover - a path that cannot be resolved is not the launcher
        return False


@functools.lru_cache(maxsize=1)
def _detect_shell() -> str:
    """The Bash this host provides, discovered once.

    Only the automatic discovery is cached: it touches the filesystem, and the answer cannot
    change while the tests run.
    """
    if os.name == "nt":
        # Git for Windows comes first: its Bash is the one whose path syntax the translation in
        # `shell_path` matches.
        for candidate in _git_for_windows_bash_candidates():
            if candidate.is_file():
                return str(candidate)

    on_path = shutil.which("bash")
    if on_path and not _is_wsl_launcher(on_path):
        return on_path

    raise ShellUnavailable(
        "no Bash executable was found for the deployment scripts. Install Git for Windows (its "
        "Bash lives in 'Program Files/Git/bin') or point "
        f"{SHELL_VARIABLE} at the Bash to use. The 'bash.exe' in System32 is the WSL launcher "
        "and is not used: it needs a distribution and a different path syntax."
    )


def _resolve_shell() -> str:
    """The Bash executable to use, or an explanation of why there is none.

    The override is read on every call, not cached with the discovery: a test or a developer
    pointing the suite at another shell must take effect immediately, whatever was resolved
    earlier in the same process.
    """
    override = os.environ.get(SHELL_VARIABLE)
    if override:
        if not Path(override).is_file():
            raise ShellUnavailable(f"{SHELL_VARIABLE}={override!r} is not a file")
        return override

    return _detect_shell()


def shell_executable() -> str:
    """The Bash that runs the deployment scripts."""
    return _resolve_shell()


def _windows_path_to_posix(text: str) -> str:
    """`C:\\Users\\me` -> `/c/Users/me`, the path syntax Git Bash understands."""
    drive, _, remainder = text.partition(":")
    return f"/{drive.lower()}{remainder.replace(chr(92), '/')}"  # chr(92) is a backslash


def shell_path(path: Path | str) -> str:
    """The path as the resolved shell spells it.

    A POSIX host already uses the shell's own syntax, so the path is returned unchanged. On
    Windows the deployment scripts are handed the MSYS2 form of the path, because they insist on
    absolute POSIX paths: the staged release lives at `/srv/talimgo/frontend/dist` and the script
    refuses any target that does not start with `/`.
    """
    text = str(path)
    if os.name != "nt" or not WINDOWS_ABSOLUTE_PATH.match(text):
        return text
    return _windows_path_to_posix(text)


@functools.lru_cache(maxsize=1)
def _python3_shim_directory() -> Path:
    """A directory holding a `python3` that runs the interpreter this test session uses.

    `deploy/health-check.sh` requires a `python3` on `PATH`. Windows has none: `python3` is the
    Microsoft Store alias, which opens the Store instead of running Python. The shim is created
    once per session and removed when the session ends.
    """
    if not sys.executable:
        raise ShellUnavailable("the interpreter running the tests has no executable path")
    directory = Path(tempfile.mkdtemp(prefix="talimgo-deploy-shell-"))
    shim = directory / "python3"
    shim.write_text(
        f'#!/usr/bin/env bash\nexec "{shell_path(sys.executable)}" "$@"\n',
        encoding="utf-8",
    )
    atexit.register(shutil.rmtree, directory, True)
    return directory


def shell_environment() -> dict[str, str]:
    """The environment a deployment script runs in.

    The inherited environment is kept: a child process needs the platform's own variables (on
    Windows the interpreter cannot initialise its socket layer without `SystemRoot`), and only the
    `python3` the health check asks for is put in front of `PATH`.
    """
    environment = dict(os.environ)
    if os.name == "nt":
        shim = _python3_shim_directory()
        environment["PATH"] = f"{shim}{os.pathsep}{environment.get('PATH', '')}"
    return environment


def run_bash(
    arguments: Sequence[str],
    *,
    timeout: float = 30,
    cwd: Path | None = None,
) -> subprocess.CompletedProcess:
    """Run the shell with the given arguments and capture what it printed."""
    command = [shell_executable(), *(shell_path(argument) for argument in arguments)]
    return subprocess.run(
        command,
        capture_output=True,
        text=True,
        timeout=timeout,
        cwd=cwd,
        env=shell_environment(),
    )


def run_script(
    script: Path,
    *arguments: str,
    timeout: float = 30,
    cwd: Path | None = None,
) -> subprocess.CompletedProcess:
    """Run one of the checked-in deployment scripts."""
    return run_bash([shell_path(script), *arguments], timeout=timeout, cwd=cwd)
