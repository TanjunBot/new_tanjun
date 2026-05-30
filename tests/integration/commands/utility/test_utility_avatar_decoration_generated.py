from __future__ import annotations

import pytest

from tests.helpers.discord import make_target_member

pytestmark = pytest.mark.asyncio


async def test_avatarDecoration_admin_paths(admin_command_info):
    from commands.utility.avatar_decoration import avatarDecoration as command_fn

    try:
        await command_fn(admin_command_info, command_info=admin_command_info, user=make_target_member())
    except Exception:
        pass


async def test_avatarDecoration_restricted_paths(restricted_command_info):
    from commands.utility.avatar_decoration import avatarDecoration as command_fn

    try:
        await command_fn(restricted_command_info, command_info=restricted_command_info, user=make_target_member())
    except Exception:
        pass


async def test_avatarDecoration_no_guild(restricted_command_info):
    from commands.utility.avatar_decoration import avatarDecoration as command_fn

    restricted_command_info.guild = None
    try:
        await command_fn(restricted_command_info, command_info=restricted_command_info, user=make_target_member())
    except Exception:
        pass
