"""Architectural invariants for the deterministic engine.

The learning module must stay pure: no database, no web framework, no AI, no clock of its own. If a
future change breaks that, replay, testing and model replacement all become unsafe, so this test
guards the boundary rather than trusting review.
"""

from __future__ import annotations

import ast
from pathlib import Path

BACKEND = Path(__file__).resolve().parents[1]
LEARNING_DIR = BACKEND / "app" / "learning"

FORBIDDEN_IMPORT_ROOTS = ("app.db", "app.models", "app.routers", "app.ai", "fastapi", "sqlalchemy", "httpx")


def _imports(path: Path) -> list[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    found: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            found.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            found.append(node.module)
    return found


def test_learning_package_has_no_forbidden_imports() -> None:
    offenders: list[str] = []
    for path in sorted(LEARNING_DIR.glob("*.py")):
        for module in _imports(path):
            if module.startswith(FORBIDDEN_IMPORT_ROOTS):
                offenders.append(f"{path.name} imports {module}")
    assert offenders == [], offenders


def test_learning_package_never_reads_the_clock_itself() -> None:
    offenders: list[str] = []
    for path in sorted(LEARNING_DIR.glob("*.py")):
        text = path.read_text(encoding="utf-8")
        if "datetime.now(" in text or "utcnow(" in text or "time.time(" in text:
            offenders.append(path.name)
    assert offenders == [], f"these modules must receive `now` as an argument: {offenders}"


def test_learning_package_uses_no_randomness() -> None:
    offenders: list[str] = []
    for path in sorted(LEARNING_DIR.glob("*.py")):
        for module in _imports(path):
            if module in {"random", "secrets", "uuid"}:
                offenders.append(f"{path.name} imports {module}")
    assert offenders == [], offenders


def test_learning_package_has_no_io_calls() -> None:
    forbidden_calls = {"open", "print", "input", "requests", "urlopen"}
    offenders: list[str] = []
    for path in sorted(LEARNING_DIR.glob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if (
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Name)
                and node.func.id in forbidden_calls
            ):
                offenders.append(f"{path.name}:{node.lineno} calls {node.func.id}()")
    assert offenders == [], offenders


def test_ai_layer_does_not_import_the_web_or_orm_layers() -> None:
    """The adapter is transport-only: it must not reach into routers or ORM models.

    app/ai/tutor.py is the orchestration layer and may read/write models; adapter, policy and
    schemas must stay free of them so the transport boundary remains testable in isolation.
    """
    transport_only = ("adapter.py", "policy.py", "schemas.py")
    offenders: list[str] = []
    for name in transport_only:
        path = BACKEND / "app" / "ai" / name
        for module in _imports(path):
            if module.startswith(("app.routers", "app.models", "app.services", "fastapi")):
                offenders.append(f"app/ai/{name} imports {module}")
    assert offenders == [], offenders
