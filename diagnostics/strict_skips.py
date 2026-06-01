from __future__ import annotations

from diagnostics.prefix_skips import PREFIX_COMMANDS_EXCLUDED, PREFIX_SKIP_REASONS

PREFIX_SKIP_ALLOWLIST: dict[str, str] = dict(PREFIX_SKIP_REASONS)

PREFIX_COMMANDS_EXCLUDED_SET = frozenset(PREFIX_COMMANDS_EXCLUDED) | frozenset(
    {
        "test_bot",
        "benchmark_bot",
    }
)

SLASH_SKIP_ALLOWLIST: dict[str, str] = {}


def is_allowed_slash_skip(spec_id: str) -> bool:
    return spec_id in SLASH_SKIP_ALLOWLIST


def is_allowed_prefix_skip(command_name: str) -> bool:
    return command_name in PREFIX_SKIP_ALLOWLIST or command_name in PREFIX_COMMANDS_EXCLUDED_SET
