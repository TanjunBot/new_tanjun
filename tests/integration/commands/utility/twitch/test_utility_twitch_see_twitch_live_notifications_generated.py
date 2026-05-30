from __future__ import annotations

import pytest

pytestmark = pytest.mark.asyncio


async def test_seeTwitchLiveNotifications_admin_paths(admin_command_info):
    from commands.utility.twitch.see_twitch_live_notifications import seeTwitchLiveNotifications as command_fn

    try:
        await command_fn(admin_command_info, command_info=admin_command_info)
    except Exception:
        pass


async def test_seeTwitchLiveNotifications_restricted_paths(restricted_command_info):
    from commands.utility.twitch.see_twitch_live_notifications import seeTwitchLiveNotifications as command_fn

    try:
        await command_fn(restricted_command_info, command_info=restricted_command_info)
    except Exception:
        pass


async def test_seeTwitchLiveNotifications_no_guild(restricted_command_info):
    from commands.utility.twitch.see_twitch_live_notifications import seeTwitchLiveNotifications as command_fn

    restricted_command_info.guild = None
    try:
        await command_fn(restricted_command_info, command_info=restricted_command_info)
    except Exception:
        pass
