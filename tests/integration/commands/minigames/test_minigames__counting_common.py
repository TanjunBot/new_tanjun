"""Integration tests for commands.minigames._counting_common.require_moderate_members."""

from __future__ import annotations

from unittest.mock import AsyncMock
import pytest

from tests.helpers.assertions import assert_matrix_outcome
from tests.helpers.command_profiles import CommandProfile, profile_patches


pytestmark = [pytest.mark.asyncio, pytest.mark.integration]

PROFILE = CommandProfile.from_module('commands.minigames._counting_common', 'require_moderate_members', 'info, locale_key_prefix="minigames.test"')


async def test_require_moderate_members_restricted(restricted_command_info):
    info = restricted_command_info
    with profile_patches(PROFILE) as mocks:
        from commands.minigames._counting_common import require_moderate_members as command_fn
        await command_fn(info, locale_key_prefix="minigames.test")
    assert_matrix_outcome(info, "restricted", PROFILE, mocks)


async def test_require_moderate_members_no_guild(no_guild_command_info):
    info = no_guild_command_info
    with profile_patches(PROFILE) as mocks:
        from commands.minigames._counting_common import require_moderate_members as command_fn
        await command_fn(info, locale_key_prefix="minigames.test")
    assert_matrix_outcome(info, "no_guild", PROFILE, mocks)


async def test_require_moderate_members_admin(admin_command_info):
    info = admin_command_info
    with profile_patches(PROFILE) as mocks:
        from commands.minigames._counting_common import require_moderate_members as command_fn
        await command_fn(info, locale_key_prefix="minigames.test")
    assert_matrix_outcome(info, "admin", PROFILE, mocks)
