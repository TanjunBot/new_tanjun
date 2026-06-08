from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import tests.mock_config as mock_config

mock_config.patch_config_module()

from locale_keys import locale
from utils.command_tree_audit import DISCORD_COMMAND_PAYLOAD_SAFE_LIMIT, CommandPayloadAudit

pytestmark = pytest.mark.asyncio


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
