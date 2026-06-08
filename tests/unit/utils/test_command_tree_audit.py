from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import tests.mock_config as mock_config

mock_config.patch_config_module()

from diagnostics.tree import collect_tree_paths
from tests.helpers.extension_loader import load_extension, make_bot_for_extensions
from utils.command_tree_audit import DISCORD_COMMAND_PAYLOAD_SAFE_LIMIT, CommandPayloadAudit

LEVEL_EXTENSION = "extensions.level"


@pytest.mark.asyncio
async def test_level_setbackground_registered_in_tree() -> None:
    bot = make_bot_for_extensions()
    await load_extension(bot, LEVEL_EXTENSION)
    level_cog = bot.cogs.get("levelCog")
    assert level_cog is not None
    await level_cog.on_ready()
    paths = collect_tree_paths(bot)
    assert "levelcommands_name level_setbackground_name" in paths


def test_command_payload_audit_dataclass_flags() -> None:
    entry = CommandPayloadAudit(
        command_name="levelcommands_name",
        payload_bytes=DISCORD_COMMAND_PAYLOAD_SAFE_LIMIT + 1,
        over_safe_limit=True,
        over_hard_limit=False,
    )
    assert entry.over_safe_limit
    assert not entry.over_hard_limit
