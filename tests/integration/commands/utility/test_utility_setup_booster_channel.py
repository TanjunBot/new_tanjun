"""Integration tests for commands.utility.setup_booster_channel.setupBoosterChannel."""

from __future__ import annotations

from unittest.mock import AsyncMock
import pytest

from tests.helpers.assertions import assert_matrix_outcome
from tests.helpers.command_profiles import CommandProfile, profile_patches


pytestmark = [pytest.mark.asyncio, pytest.mark.integration]

PROFILE = CommandProfile.from_module('commands.utility.setup_booster_channel', 'setupBoosterChannel', 'info, category=info.channel')


async def test_setupBoosterChannel_restricted(restricted_command_info):
    info = restricted_command_info
    with profile_patches(PROFILE) as mocks:
        from commands.utility.setup_booster_channel import setupBoosterChannel as command_fn
        await command_fn(info, category=info.channel)
    assert_matrix_outcome(info, "restricted", PROFILE, mocks)


async def test_setupBoosterChannel_no_guild(no_guild_command_info):
    info = no_guild_command_info
    with profile_patches(PROFILE) as mocks:
        from commands.utility.setup_booster_channel import setupBoosterChannel as command_fn
        await command_fn(info, category=info.channel)
    assert_matrix_outcome(info, "no_guild", PROFILE, mocks)


async def test_setupBoosterChannel_admin(admin_command_info):
    info = admin_command_info
    with profile_patches(PROFILE) as mocks:
        from commands.utility.setup_booster_channel import setupBoosterChannel as command_fn
        await command_fn(info, category=info.channel)
    assert_matrix_outcome(info, "admin", PROFILE, mocks)
