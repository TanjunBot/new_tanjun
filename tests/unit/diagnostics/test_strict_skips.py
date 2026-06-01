from __future__ import annotations

from diagnostics.strict_skips import (
    PREFIX_COMMANDS_EXCLUDED_SET,
    PREFIX_SKIP_ALLOWLIST,
    is_allowed_prefix_skip,
    is_allowed_slash_skip,
)


def test_is_allowed_slash_skip_false_by_default() -> None:
    assert not is_allowed_slash_skip("utility.foo.bar")


def test_is_allowed_prefix_skip_excluded_set() -> None:
    assert is_allowed_prefix_skip("test_bot")
    assert is_allowed_prefix_skip("benchmark_bot")


def test_is_allowed_prefix_skip_allowlist() -> None:
    name = next(iter(PREFIX_SKIP_ALLOWLIST))
    assert is_allowed_prefix_skip(name)


def test_excluded_set_contains_mass_dm_commands() -> None:
    assert "database_sync" in PREFIX_COMMANDS_EXCLUDED_SET
