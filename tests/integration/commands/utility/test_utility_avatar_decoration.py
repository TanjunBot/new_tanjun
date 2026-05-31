"""Integration tests for commands.utility.avatar_decoration.avatarDecoration."""

from __future__ import annotations

from unittest.mock import AsyncMock
from tests.helpers.discord import make_target_member
import pytest

from tests.helpers.assertions import assert_matrix_outcome
from tests.helpers.command_profiles import CommandProfile, profile_patches


pytestmark = [pytest.mark.asyncio, pytest.mark.integration]

PROFILE = CommandProfile.from_module('commands.utility.avatar_decoration', 'avatarDecoration', 'info, user=make_target_member()')


async def test_avatarDecoration_restricted(restricted_command_info):
    info = restricted_command_info
    with profile_patches(PROFILE) as mocks:
        from commands.utility.avatar_decoration import avatarDecoration as command_fn
        await command_fn(info, user=make_target_member())
    assert_matrix_outcome(info, "restricted", PROFILE, mocks)


async def test_avatarDecoration_no_guild(no_guild_command_info):
    info = no_guild_command_info
    with profile_patches(PROFILE) as mocks:
        from commands.utility.avatar_decoration import avatarDecoration as command_fn
        await command_fn(info, user=make_target_member())
    assert_matrix_outcome(info, "no_guild", PROFILE, mocks)


async def test_avatarDecoration_admin(admin_command_info):
    info = admin_command_info
    with profile_patches(PROFILE) as mocks:
        from commands.utility.avatar_decoration import avatarDecoration as command_fn
        await command_fn(info, user=make_target_member())
    assert_matrix_outcome(info, "admin", PROFILE, mocks)
