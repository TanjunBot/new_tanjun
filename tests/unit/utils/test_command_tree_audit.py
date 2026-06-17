from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import tests.mock_config as mock_config

mock_config.patch_config_module()

from locale_keys import locale
from utils.command_tree_audit import (
    DISCORD_COMMAND_PAYLOAD_LIMIT,
    DISCORD_COMMAND_PAYLOAD_SAFE_LIMIT,
    CommandPayloadAudit,
    audit_root_command_payloads,
    find_oversized_root_commands,
)


@pytest.mark.asyncio
async def test_level_setbackground_registered_in_tree() -> None:
    import importlib

    import extensions.level as level_mod

    importlib.reload(level_mod)
    level_cmds = level_mod.levelCommands(
        name=locale.levelcommands.name.discord_key,
        description=locale.levelcommands.description.discord_key,
    )
    names = {getattr(cmd, "name", "") for cmd in level_cmds.commands}
    assert "level_setbackground_name" in names


def test_command_payload_audit_dataclass_flags() -> None:
    entry = CommandPayloadAudit(
        command_name="levelcommands_name",
        payload_bytes=DISCORD_COMMAND_PAYLOAD_SAFE_LIMIT + 1,
        over_safe_limit=True,
        over_hard_limit=False,
    )
    assert entry.over_safe_limit
    assert not entry.over_hard_limit


def _make_bot_with_tree():
    bot = MagicMock()
    tree = MagicMock()
    bot.tree = tree
    return bot, tree


def test_audit_root_command_payloads_empty_tree() -> None:
    bot, tree = _make_bot_with_tree()
    tree.get_commands.return_value = []
    assert audit_root_command_payloads(bot) == []


def test_audit_root_command_payloads_with_commands() -> None:
    bot, tree = _make_bot_with_tree()
    cmd = MagicMock()
    cmd.name = "test"
    cmd.to_dict.return_value = {"name": "test", "description": "A test command"}
    tree.get_commands.return_value = [cmd]

    results = audit_root_command_payloads(bot)
    assert len(results) == 1
    assert isinstance(results[0], CommandPayloadAudit)
    assert results[0].command_name == "test"
    assert results[0].payload_bytes > 0
    assert not results[0].over_safe_limit
    assert not results[0].over_hard_limit


def test_audit_root_command_payloads_tree_is_none() -> None:
    bot, _ = _make_bot_with_tree()
    bot.tree = None
    assert audit_root_command_payloads(bot) == []


def test_find_oversized_root_commands() -> None:
    bot, tree = _make_bot_with_tree()
    small_cmd = MagicMock()
    small_cmd.name = "small"
    small_cmd.to_dict.return_value = {"name": "small"}
    large_cmd = MagicMock()
    large_cmd.name = "large"
    # Create a payload large enough to exceed the safe/hard limits.
    large_cmd.to_dict.return_value = {"name": "large", "x": "x" * DISCORD_COMMAND_PAYLOAD_LIMIT}
    tree.get_commands.return_value = [small_cmd, large_cmd]

    oversized = find_oversized_root_commands(bot)
    assert len(oversized) == 1
    assert oversized[0].command_name == "large"
    assert oversized[0].over_safe_limit
    assert oversized[0].over_hard_limit


def test_find_oversized_root_commands_no_tree() -> None:
    bot, _ = _make_bot_with_tree()
    bot.tree = None
    assert find_oversized_root_commands(bot) == []
