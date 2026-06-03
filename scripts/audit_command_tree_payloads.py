#!/usr/bin/env python3
"""Fail if any root slash command group exceeds Discord's safe payload size."""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import tests.mock_config as mock_config

mock_config.patch_config_module()

from tests.helpers.extension_loader import fire_cog_on_ready, load_all_extensions, make_bot_with_real_tree
from utils.command_tree_audit import find_oversized_root_commands


def _patch_logs_cog_on_ready_for_audit() -> None:
    from extensions.logs import LogsCog, LogsCommands
    from locale_keys import locale as l10n
    from extensions.logs import (
        CategoryBlacklistCommands,
        ChannelBlacklistCommands,
        RoleBlacklistCommands,
        UserBlacklistCommands,
        VoiceBlacklistCommands,
    )

    async def on_ready_register_only(self) -> None:
        logcmds = LogsCommands(name=l10n.logs.name.discord_key, description=l10n.logs.description.discord_key)
        channel_blacklist = ChannelBlacklistCommands(
            name=l10n.logs.blacklist.name.discord_key, description=l10n.logs.blacklist.description.discord_key
        )
        user_blacklist = UserBlacklistCommands(
            name=l10n.logs.blacklistu.name.discord_key, description=l10n.logs.blacklistu.description.discord_key
        )
        role_blacklist = RoleBlacklistCommands(
            name=l10n.logs.blacklistr.name.discord_key, description=l10n.logs.blacklistr.description.discord_key
        )
        voice_blacklist = VoiceBlacklistCommands(
            name=l10n.logs.blacklistv.name.discord_key, description=l10n.logs.blacklistv.description.discord_key
        )
        category_blacklist = CategoryBlacklistCommands(
            name=l10n.logs.blacklistcat.name.discord_key, description=l10n.logs.blacklistcat.description.discord_key
        )
        logcmds.add_command(channel_blacklist)
        logcmds.add_command(user_blacklist)
        logcmds.add_command(role_blacklist)
        logcmds.add_command(voice_blacklist)
        logcmds.add_command(category_blacklist)
        self.bot.tree.add_command(logcmds)

    LogsCog.on_ready = on_ready_register_only


async def _audit() -> int:
    _patch_logs_cog_on_ready_for_audit()
    bot = make_bot_with_real_tree()
    await load_all_extensions(bot)
    await fire_cog_on_ready(bot)
    oversized = find_oversized_root_commands(bot)
    if oversized:
        for entry in oversized:
            print(f"FAIL {entry.command_name}: {entry.payload_bytes} bytes")
        return 1
    print(f"OK: {len(bot.tree.get_commands())} root command groups within safe payload size")
    return 0


def main() -> int:
    return asyncio.run(_audit())


if __name__ == "__main__":
    raise SystemExit(main())
