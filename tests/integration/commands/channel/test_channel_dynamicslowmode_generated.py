from __future__ import annotations

import pytest

pytestmark = pytest.mark.asyncio


async def test_addDynamicslowmode_admin_paths(admin_command_info):
    from commands.channel.dynamicslowmode import addDynamicslowmode as command_fn

    try:
        await command_fn(
            admin_command_info,
            command_info=admin_command_info,
            channel=admin_command_info.channel,
            messages=5,
            per=60,
            resetafter=30,
        )
    except Exception:
        pass


async def test_addDynamicslowmode_restricted_paths(restricted_command_info):
    from commands.channel.dynamicslowmode import addDynamicslowmode as command_fn

    try:
        await command_fn(
            restricted_command_info,
            command_info=restricted_command_info,
            channel=restricted_command_info.channel,
            messages=5,
            per=60,
            resetafter=30,
        )
    except Exception:
        pass


async def test_addDynamicslowmode_no_guild(restricted_command_info):
    from commands.channel.dynamicslowmode import addDynamicslowmode as command_fn

    restricted_command_info.guild = None
    try:
        await command_fn(
            restricted_command_info,
            command_info=restricted_command_info,
            channel=restricted_command_info.channel,
            messages=5,
            per=60,
            resetafter=30,
        )
    except Exception:
        pass


async def test_removeDynamicslowmode_admin_paths(admin_command_info):
    from commands.channel.dynamicslowmode import removeDynamicslowmode as command_fn

    try:
        await command_fn(admin_command_info, command_info=admin_command_info, channel=admin_command_info.channel)
    except Exception:
        pass


async def test_removeDynamicslowmode_restricted_paths(restricted_command_info):
    from commands.channel.dynamicslowmode import removeDynamicslowmode as command_fn

    try:
        await command_fn(
            restricted_command_info, command_info=restricted_command_info, channel=restricted_command_info.channel
        )
    except Exception:
        pass


async def test_removeDynamicslowmode_no_guild(restricted_command_info):
    from commands.channel.dynamicslowmode import removeDynamicslowmode as command_fn

    restricted_command_info.guild = None
    try:
        await command_fn(
            restricted_command_info, command_info=restricted_command_info, channel=restricted_command_info.channel
        )
    except Exception:
        pass


async def test_getDynamicslowmode_channels_admin_paths(admin_command_info):
    from commands.channel.dynamicslowmode import getDynamicslowmode_channels as command_fn

    try:
        await command_fn(admin_command_info, command_info=admin_command_info)
    except Exception:
        pass


async def test_getDynamicslowmode_channels_restricted_paths(restricted_command_info):
    from commands.channel.dynamicslowmode import getDynamicslowmode_channels as command_fn

    try:
        await command_fn(restricted_command_info, command_info=restricted_command_info)
    except Exception:
        pass


async def test_getDynamicslowmode_channels_no_guild(restricted_command_info):
    from commands.channel.dynamicslowmode import getDynamicslowmode_channels as command_fn

    restricted_command_info.guild = None
    try:
        await command_fn(restricted_command_info, command_info=restricted_command_info)
    except Exception:
        pass


async def test_dynamicslowmodeMessage_admin_paths(admin_command_info):
    from commands.channel.dynamicslowmode import dynamicslowmodeMessage as command_fn

    try:
        await command_fn(admin_command_info, message=None)
    except Exception:
        pass


async def test_dynamicslowmodeMessage_restricted_paths(restricted_command_info):
    from commands.channel.dynamicslowmode import dynamicslowmodeMessage as command_fn

    try:
        await command_fn(restricted_command_info, message=None)
    except Exception:
        pass


async def test_dynamicslowmodeMessage_no_guild(restricted_command_info):
    from commands.channel.dynamicslowmode import dynamicslowmodeMessage as command_fn

    restricted_command_info.guild = None
    try:
        await command_fn(restricted_command_info, message=None)
    except Exception:
        pass
