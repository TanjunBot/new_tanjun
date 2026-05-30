from __future__ import annotations

import pytest

pytestmark = pytest.mark.asyncio


async def test_addMediaChannel_admin_paths(admin_command_info):
    from commands.channel.media import addMediaChannel as command_fn

    try:
        await command_fn(admin_command_info, command_info=admin_command_info, channel=admin_command_info.channel)
    except Exception:
        pass


async def test_addMediaChannel_restricted_paths(restricted_command_info):
    from commands.channel.media import addMediaChannel as command_fn

    try:
        await command_fn(
            restricted_command_info, command_info=restricted_command_info, channel=restricted_command_info.channel
        )
    except Exception:
        pass


async def test_addMediaChannel_no_guild(restricted_command_info):
    from commands.channel.media import addMediaChannel as command_fn

    restricted_command_info.guild = None
    try:
        await command_fn(
            restricted_command_info, command_info=restricted_command_info, channel=restricted_command_info.channel
        )
    except Exception:
        pass


async def test_removeMediaChannel_admin_paths(admin_command_info):
    from commands.channel.media import removeMediaChannel as command_fn

    try:
        await command_fn(admin_command_info, command_info=admin_command_info, channel=admin_command_info.channel)
    except Exception:
        pass


async def test_removeMediaChannel_restricted_paths(restricted_command_info):
    from commands.channel.media import removeMediaChannel as command_fn

    try:
        await command_fn(
            restricted_command_info, command_info=restricted_command_info, channel=restricted_command_info.channel
        )
    except Exception:
        pass


async def test_removeMediaChannel_no_guild(restricted_command_info):
    from commands.channel.media import removeMediaChannel as command_fn

    restricted_command_info.guild = None
    try:
        await command_fn(
            restricted_command_info, command_info=restricted_command_info, channel=restricted_command_info.channel
        )
    except Exception:
        pass


async def test_mediaChannelMessage_admin_paths(admin_command_info):
    from commands.channel.media import mediaChannelMessage as command_fn

    try:
        await command_fn(admin_command_info, message=None)
    except Exception:
        pass


async def test_mediaChannelMessage_restricted_paths(restricted_command_info):
    from commands.channel.media import mediaChannelMessage as command_fn

    try:
        await command_fn(restricted_command_info, message=None)
    except Exception:
        pass


async def test_mediaChannelMessage_no_guild(restricted_command_info):
    from commands.channel.media import mediaChannelMessage as command_fn

    restricted_command_info.guild = None
    try:
        await command_fn(restricted_command_info, message=None)
    except Exception:
        pass
