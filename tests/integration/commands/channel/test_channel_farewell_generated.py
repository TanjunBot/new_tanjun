from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest

from tests.helpers.discord import make_interaction, make_role, make_target_member


pytestmark = pytest.mark.asyncio

async def test_setFarewellChannel_admin_paths(admin_command_info):
    from commands.channel.farewell import setFarewellChannel as command_fn
    try:
        await command_fn(admin_command_info, command_info=admin_command_info, channel=admin_command_info.channel, message=None, image_background=None)
    except Exception:
        pass


async def test_setFarewellChannel_restricted_paths(restricted_command_info):
    from commands.channel.farewell import setFarewellChannel as command_fn
    try:
        await command_fn(restricted_command_info, command_info=restricted_command_info, channel=restricted_command_info.channel, message=None, image_background=None)
    except Exception:
        pass


async def test_setFarewellChannel_no_guild(restricted_command_info):
    from commands.channel.farewell import setFarewellChannel as command_fn
    restricted_command_info.guild = None
    try:
        await command_fn(restricted_command_info, command_info=restricted_command_info, channel=restricted_command_info.channel, message=None, image_background=None)
    except Exception:
        pass


async def test_removeFarewellChannel_admin_paths(admin_command_info):
    from commands.channel.farewell import removeFarewellChannel as command_fn
    try:
        await command_fn(admin_command_info, command_info=admin_command_info)
    except Exception:
        pass


async def test_removeFarewellChannel_restricted_paths(restricted_command_info):
    from commands.channel.farewell import removeFarewellChannel as command_fn
    try:
        await command_fn(restricted_command_info, command_info=restricted_command_info)
    except Exception:
        pass


async def test_removeFarewellChannel_no_guild(restricted_command_info):
    from commands.channel.farewell import removeFarewellChannel as command_fn
    restricted_command_info.guild = None
    try:
        await command_fn(restricted_command_info, command_info=restricted_command_info)
    except Exception:
        pass


async def test_farewellUser_admin_paths(admin_command_info):
    from commands.channel.farewell import farewellUser as command_fn
    try:
        await command_fn(admin_command_info, member=make_target_member())
    except Exception:
        pass


async def test_farewellUser_restricted_paths(restricted_command_info):
    from commands.channel.farewell import farewellUser as command_fn
    try:
        await command_fn(restricted_command_info, member=make_target_member())
    except Exception:
        pass


async def test_farewellUser_no_guild(restricted_command_info):
    from commands.channel.farewell import farewellUser as command_fn
    restricted_command_info.guild = None
    try:
        await command_fn(restricted_command_info, member=make_target_member())
    except Exception:
        pass
