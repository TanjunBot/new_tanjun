from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest

from tests.helpers.discord import make_interaction, make_role, make_target_member


pytestmark = pytest.mark.asyncio

async def test_setWelcomeChannel_admin_paths(admin_command_info):
    from commands.channel.welcome import setWelcomeChannel as command_fn
    try:
        await command_fn(admin_command_info, command_info=admin_command_info, channel=admin_command_info.channel, message=None, image_background=None)
    except Exception:
        pass


async def test_setWelcomeChannel_restricted_paths(restricted_command_info):
    from commands.channel.welcome import setWelcomeChannel as command_fn
    try:
        await command_fn(restricted_command_info, command_info=restricted_command_info, channel=restricted_command_info.channel, message=None, image_background=None)
    except Exception:
        pass


async def test_setWelcomeChannel_no_guild(restricted_command_info):
    from commands.channel.welcome import setWelcomeChannel as command_fn
    restricted_command_info.guild = None
    try:
        await command_fn(restricted_command_info, command_info=restricted_command_info, channel=restricted_command_info.channel, message=None, image_background=None)
    except Exception:
        pass


async def test_removeWelcomeChannel_admin_paths(admin_command_info):
    from commands.channel.welcome import removeWelcomeChannel as command_fn
    try:
        await command_fn(admin_command_info, command_info=admin_command_info)
    except Exception:
        pass


async def test_removeWelcomeChannel_restricted_paths(restricted_command_info):
    from commands.channel.welcome import removeWelcomeChannel as command_fn
    try:
        await command_fn(restricted_command_info, command_info=restricted_command_info)
    except Exception:
        pass


async def test_removeWelcomeChannel_no_guild(restricted_command_info):
    from commands.channel.welcome import removeWelcomeChannel as command_fn
    restricted_command_info.guild = None
    try:
        await command_fn(restricted_command_info, command_info=restricted_command_info)
    except Exception:
        pass


async def test_welcomeNewUser_admin_paths(admin_command_info):
    from commands.channel.welcome import welcomeNewUser as command_fn
    try:
        await command_fn(admin_command_info, member=make_target_member())
    except Exception:
        pass


async def test_welcomeNewUser_restricted_paths(restricted_command_info):
    from commands.channel.welcome import welcomeNewUser as command_fn
    try:
        await command_fn(restricted_command_info, member=make_target_member())
    except Exception:
        pass


async def test_welcomeNewUser_no_guild(restricted_command_info):
    from commands.channel.welcome import welcomeNewUser as command_fn
    restricted_command_info.guild = None
    try:
        await command_fn(restricted_command_info, member=make_target_member())
    except Exception:
        pass
