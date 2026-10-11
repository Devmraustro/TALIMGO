#!/usr/bin/env python
"""Source-level gate for the local-only AI promise (AGENTS.md §2).

Runtime behaviour is covered by the test suite (tests/test_ai_local_only.py): the adapter validates
every endpoint and refuses anything that is not loopback/private. This script covers the *source
tree*, so a regression is caught in CI even if the offending path is never executed by a test:

1. Every absolute URL literal in application code must point at a local address — with exactly one
   exception, the deny list in app/ai/policy.py, which names hosted providers in order to refuse them.
2. No module may import a hosted generative-AI SDK (Python or JavaScript).
3. No dependency manifest may declare one.

Usage: python scripts/check_no_external_ai.py
"""

from __future__ import annotations

import json
import re
import sys
import tomllib
from ipaddress import ip_address
from pathlib import Path
from urllib.parse import urlparse

REPO = Path(__file__).resolve().parents[2]
BACKEND = REPO / "backend"
FRONTEND = REPO / "frontend"

URL_PATTERN = re.compile(r"https?://[^\s\"'`)\]}>,;]+")
PY_IMPORT_PATTERN = re.compile(
    r"^\s*(?:import|from)\s+(openai|anthropic|cohere|mistralai|groq|replicate|litellm|"
    r"google\.generativeai|google\.genai|bedrock_runtime|boto3)\b",
    re.MULTILINE,
)
TS_IMPORT_PATTERN = re.compile(
    r"""(?:from\s*|require\(\s*|import\(\s*)["'](openai|@anthropic-ai/sdk|@google/generative-ai|"""
    r"""cohere-ai|@mistralai/[^"']+|groq-sdk|replicate|litellm)["']"""
)
FORBIDDEN_PACKAGES = {
    "openai",
    "anthropic",
    "google-generativeai",
    "google-genai",
    "cohere",
    "mistralai",
    "groq",
    "replicate",
    "litellm",
    "boto3",
    "botocore",
}

# app/ai/policy.py exists to name these; nothing else may mention them in a URL literal.
PROVIDER_MENTION_ALLOWLIST = {BACKEND / "app" / "ai" / "policy.py"}

# Narrow, self-expiring exceptions for *browser* asset origins in a Content-Security-Policy string:
# they name hosts the learner's browser may fetch from when viewing the development-only interactive
# API docs. The application itself never requests them, they do not exist in production (the docs
# routes are disabled), and each entry is a (relative path, exact literal) pair. Entries that stop
# being used are reported as failures, so this cannot decay into a blanket file exemption.
CSP_LITERAL_EXCEPTIONS = {
    ("backend/app/http_hardening.py", "https://cdn.jsdelivr.net"),
    ("backend/app/http_hardening.py", "https://fastapi.tiangolo.com"),
}


def is_local_host(host: str) -> bool:
    if host in {"localhost", "127.0.0.1", "::1", "0.0.0.0", "host.docker.internal"}:
        return True
    if host.endswith(".localhost") or host.endswith(".local"):
        return True
    try:
        address = ip_address(host)
    except ValueError:
        return False
    return address.is_loopback or address.is_private or address.is_link_local


def source_files() -> list[Path]:
    files = [*BACKEND.glob("app/**/*.py"), *FRONTEND.glob("src/**/*.ts"), *FRONTEND.glob("src/**/*.tsx")]
    return sorted(files)


def check_urls(failures: list[str]) -> int:
    checked = 0
    used_exceptions: set[tuple[str, str]] = set()
    for path in source_files():
        text = path.read_text(encoding="utf-8")
        relative = str(path.relative_to(REPO))
        for match in URL_PATTERN.finditer(text):
            raw = match.group(0)
            host = urlparse(raw).hostname or ""
            checked += 1
            if is_local_host(host) or "%s" in raw or "{" in raw:
                continue
            if path in PROVIDER_MENTION_ALLOWLIST:
                continue
            if (relative, raw) in CSP_LITERAL_EXCEPTIONS:
                used_exceptions.add((relative, raw))
                continue
            failures.append(f"{relative}: non-local URL literal {raw!r}")
    for stale in sorted(CSP_LITERAL_EXCEPTIONS - used_exceptions):
        failures.append(
            f"{stale[0]}: stale CSP exception for {stale[1]!r} — remove it from "
            "CSP_LITERAL_EXCEPTIONS"
        )
    return checked


def check_imports(failures: list[str]) -> int:
    checked = 0
    for path in source_files():
        text = path.read_text(encoding="utf-8")
        pattern = PY_IMPORT_PATTERN if path.suffix == ".py" else TS_IMPORT_PATTERN
        for match in pattern.finditer(text):
            failures.append(f"{path.relative_to(REPO)}: imports hosted AI SDK {match.group(1)!r}")
        checked += 1
    return checked


def check_manifests(failures: list[str]) -> None:
    pyproject = tomllib.loads((BACKEND / "pyproject.toml").read_text(encoding="utf-8"))
    for requirement in pyproject["project"]["dependencies"]:
        name = re.split(r"[<>=!\[; ]", requirement.strip(), maxsplit=1)[0].lower()
        if name in FORBIDDEN_PACKAGES:
            failures.append(f"backend/pyproject.toml declares {name}")
    for group in pyproject.get("project", {}).get("optional-dependencies", {}).values():
        for requirement in group:
            name = re.split(r"[<>=!\[; ]", requirement.strip(), maxsplit=1)[0].lower()
            if name in FORBIDDEN_PACKAGES:
                failures.append(f"backend/pyproject.toml declares {name}")

    manifest = json.loads((FRONTEND / "package.json").read_text(encoding="utf-8"))
    for section in ("dependencies", "devDependencies", "peerDependencies"):
        for name in manifest.get(section, {}):
            if name.lower() in FORBIDDEN_PACKAGES:
                failures.append(f"frontend/package.json declares {name}")


def main() -> int:
    failures: list[str] = []
    urls = check_urls(failures)
    files = check_imports(failures)
    check_manifests(failures)

    for failure in failures:
        print(f"error: {failure}", file=sys.stderr)
    if failures:
        print(
            f"\n{len(failures)} violation(s) of the local-only AI rule. See AGENTS.md §2.",
            file=sys.stderr,
        )
        return 1
    print(
        f"local-only AI check passed ({files} source files, {urls} URL literals, "
        "no hosted providers imported or declared)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
