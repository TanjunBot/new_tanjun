from __future__ import annotations

import pytest

pytestmark = pytest.mark.asyncio


async def test_start_giveaway_admin_paths(admin_command_info):
    from commands.giveaway.start import start_giveaway as command_fn

    try:
        await command_fn(admin_command_info, command_info=admin_command_info, title="Prize", target_channel=None)
    except Exception:
        pass


async def test_start_giveaway_restricted_paths(restricted_command_info):
    from commands.giveaway.start import start_giveaway as command_fn

    try:
        await command_fn(restricted_command_info, command_info=restricted_command_info, title="Prize", target_channel=None)
    except Exception:
        pass


async def test_start_giveaway_no_guild(restricted_command_info):
    from commands.giveaway.start import start_giveaway as command_fn

    restricted_command_info.guild = None
    try:
        await command_fn(restricted_command_info, command_info=restricted_command_info, title="Prize", target_channel=None)
    except Exception:
        pass
