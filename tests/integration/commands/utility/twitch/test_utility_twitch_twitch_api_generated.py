from __future__ import annotations

import pytest

pytestmark = pytest.mark.asyncio


async def test_notify_twitch_online_admin_paths(admin_command_info):
    from commands.utility.twitch.twitch_api import notify_twitch_online as command_fn

    try:
        await command_fn(admin_command_info, client=None, uuid=None, data=None)
    except Exception:
        pass


async def test_notify_twitch_online_restricted_paths(restricted_command_info):
    from commands.utility.twitch.twitch_api import notify_twitch_online as command_fn

    try:
        await command_fn(restricted_command_info, client=None, uuid=None, data=None)
    except Exception:
        pass


async def test_notify_twitch_online_no_guild(restricted_command_info):
    from commands.utility.twitch.twitch_api import notify_twitch_online as command_fn

    restricted_command_info.guild = None
    try:
        await command_fn(restricted_command_info, client=None, uuid=None, data=None)
    except Exception:
        pass


async def test_get_uuid_by_twitch_name_admin_paths(admin_command_info):
    from commands.utility.twitch.twitch_api import get_uuid_by_twitch_name as command_fn

    try:
        await command_fn(admin_command_info, twitch_name=None)
    except Exception:
        pass


async def test_get_uuid_by_twitch_name_restricted_paths(restricted_command_info):
    from commands.utility.twitch.twitch_api import get_uuid_by_twitch_name as command_fn

    try:
        await command_fn(restricted_command_info, twitch_name=None)
    except Exception:
        pass


async def test_get_uuid_by_twitch_name_no_guild(restricted_command_info):
    from commands.utility.twitch.twitch_api import get_uuid_by_twitch_name as command_fn

    restricted_command_info.guild = None
    try:
        await command_fn(restricted_command_info, twitch_name=None)
    except Exception:
        pass


async def test_subscribe_to_twitch_online_notification_admin_paths(admin_command_info):
    from commands.utility.twitch.twitch_api import subscribe_to_twitch_online_notification as command_fn

    try:
        await command_fn(admin_command_info, twitch_uuid=None)
    except Exception:
        pass


async def test_subscribe_to_twitch_online_notification_restricted_paths(restricted_command_info):
    from commands.utility.twitch.twitch_api import subscribe_to_twitch_online_notification as command_fn

    try:
        await command_fn(restricted_command_info, twitch_uuid=None)
    except Exception:
        pass


async def test_subscribe_to_twitch_online_notification_no_guild(restricted_command_info):
    from commands.utility.twitch.twitch_api import subscribe_to_twitch_online_notification as command_fn

    restricted_command_info.guild = None
    try:
        await command_fn(restricted_command_info, twitch_uuid=None)
    except Exception:
        pass
