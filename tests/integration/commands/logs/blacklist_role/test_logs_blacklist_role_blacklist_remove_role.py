"""Integration tests for commands.logs.blacklist_role.blacklist_remove_role.blacklist_remove_role."""

from __future__ import annotations

from unittest.mock import AsyncMock
from tests.helpers.discord import make_role
import pytest

from tests.helpers.assertions import assert_matrix_outcome
from tests.helpers.command_profiles import CommandProfile, profile_patches


pytestmark = [pytest.mark.asyncio, pytest.mark.integration]

PROFILE = CommandProfile.from_module('commands.logs.blacklist_role.blacklist_remove_role', 'blacklist_remove_role', 'info, role=make_role()')


async def test_blacklist_remove_role_restricted(restricted_command_info):
    info = restricted_command_info
    with profile_patches(PROFILE) as mocks:
        from commands.logs.blacklist_role.blacklist_remove_role import blacklist_remove_role as command_fn
        await command_fn(info, role=make_role())
    assert_matrix_outcome(info, "restricted", PROFILE, mocks)


async def test_blacklist_remove_role_no_guild(no_guild_command_info):
    info = no_guild_command_info
    with profile_patches(PROFILE) as mocks:
        from commands.logs.blacklist_role.blacklist_remove_role import blacklist_remove_role as command_fn
        await command_fn(info, role=make_role())
    assert_matrix_outcome(info, "no_guild", PROFILE, mocks)


async def test_blacklist_remove_role_admin(admin_command_info):
    info = admin_command_info
    with profile_patches(PROFILE) as mocks:
        from commands.logs.blacklist_role.blacklist_remove_role import blacklist_remove_role as command_fn
        await command_fn(info, role=make_role())
    assert_matrix_outcome(info, "admin", PROFILE, mocks)
