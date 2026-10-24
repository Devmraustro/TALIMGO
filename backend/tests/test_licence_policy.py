"""Regression tests for open-source licence policy matching."""

from scripts.check_licences import _has_policy_token


def test_lgpl_is_not_mistaken_for_gpl() -> None:
    assert not _has_policy_token("LGPL-3.0-ONLY", "GPL")
    assert not _has_policy_token("GNU LESSER GENERAL PUBLIC LICENSE (LGPLV3)", "GPL")


def test_standalone_gpl_identifiers_are_detected() -> None:
    assert _has_policy_token("GPL-3.0-ONLY", "GPL")
    assert _has_policy_token("GNU GENERAL PUBLIC LICENSE (GPLV3)", "GPL")


def test_blocked_agpl_still_matches() -> None:
    assert _has_policy_token("AGPL-3.0-ONLY", "AGPL")
