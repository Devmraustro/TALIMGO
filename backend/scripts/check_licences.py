#!/usr/bin/env python
"""Fail the build if an installed dependency carries an unacceptable licence.

TALIMGO distributes a hosted service; AGPL, SSPL and Commons-Clause terms are incompatible with that
plan, and a GPL dependency would make the whole distributed work copyleft. GPL is reported as a
warning because it is occasionally acceptable for a build-only tool, but it must be a deliberate
decision recorded in docs/OPEN_SOURCE_REUSE_AUDIT.md, never an accident.

Usage: python scripts/check_licences.py [--allow-gpl-build-tools]
"""

from __future__ import annotations

import argparse
import re
import sys
from importlib.metadata import distributions

BLOCK = {
    "AGPL": "GNU Affero General Public License",
    "SSPL": "Server Side Public License",
    "COMMONS CLAUSE": "Commons Clause",
    "BUSL": "Business Source License",
    "EUPL": "European Union Public Licence",
}
WARN = {"GPL": "GNU General Public License"}


def licence_text(distribution) -> str:
    metadata = distribution.metadata
    parts = [
        metadata.get("License-Expression", "") or "",
        metadata.get("License", "") or "",
        " ".join(metadata.get_all("Classifier", []) or []),
    ]
    return " ".join(parts).upper()


def _has_policy_token(text: str, token: str) -> bool:
    """Match GPL as a licence identifier without treating LGPL or AGPL as GPL."""
    if token == "GPL":
        return re.search(r"(?<![A-Z])GPL", text) is not None
    return token in text


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--allow-gpl-build-tools",
        action="store_true",
        help="treat GPL as a warning instead of a failure (default: fail)",
    )
    arguments = parser.parse_args()

    failures: list[str] = []
    warnings: list[str] = []
    for distribution in distributions():
        name = distribution.metadata.get("Name") or "unknown"
        text = licence_text(distribution)
        for token, description in BLOCK.items():
            if _has_policy_token(text, token):
                failures.append(f"{name}: {description} ({token}) is not allowed")
                break
        else:
            for token, description in WARN.items():
                if token in text:
                    message = f"{name}: {description} ({token})"
                    (warnings if arguments.allow_gpl_build_tools else failures).append(message)
                    break

    for warning in warnings:
        print(f"warning: {warning}")
    for failure in failures:
        print(f"error: {failure}", file=sys.stderr)
    if failures:
        return 1
    print(f"licence check passed ({len(list(distributions()))} distributions inspected)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
