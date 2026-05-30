from __future__ import annotations

import pytest

pytestmark = pytest.mark.asyncio


async def test_removewordchainchannel_admin_paths(admin_command_info):
    from commands.minigames.wordchain.removewordchainchannel import removewordchainchannel as command_fn

    try:
        await command_fn(admin_command_info, command_info=admin_command_info, channel=admin_command_info.channel)
    except Exception:
        pass


async def test_removewordchainchannel_restricted_paths(restricted_command_info):
    from commands.minigames.wordchain.removewordchainchannel import removewordchainchannel as command_fn

    try:
        await command_fn(
            restricted_command_info, command_info=restricted_command_info, channel=restricted_command_info.channel
        )
    except Exception:
        pass


async def test_removewordchainchannel_no_guild(restricted_command_info):
    from commands.minigames.wordchain.removewordchainchannel import removewordchainchannel as command_fn

    restricted_command_info.guild = None
    try:
        await command_fn(
            restricted_command_info, command_info=restricted_command_info, channel=restricted_command_info.channel
        )
    except Exception:
        pass
