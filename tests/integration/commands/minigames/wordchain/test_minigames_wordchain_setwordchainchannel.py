"""Integration tests for commands.minigames.wordchain.setwordchainchannel.setwordchainchannel."""

from __future__ import annotations

from unittest.mock import AsyncMock
import pytest

from tests.helpers.assertions import assert_matrix_outcome
from tests.helpers.command_profiles import CommandProfile, profile_patches


pytestmark = [pytest.mark.asyncio, pytest.mark.integration]

PROFILE = CommandProfile.from_module('commands.minigames.wordchain.setwordchainchannel', 'setwordchainchannel', 'info, channel=info.channel')


async def test_setwordchainchannel_restricted(restricted_command_info):
    info = restricted_command_info
    with profile_patches(PROFILE) as mocks:
        from commands.minigames.wordchain.setwordchainchannel import setwordchainchannel as command_fn
        await command_fn(info, channel=info.channel)
    assert_matrix_outcome(info, "restricted", PROFILE, mocks)


async def test_setwordchainchannel_no_guild(no_guild_command_info):
    info = no_guild_command_info
    with profile_patches(PROFILE) as mocks:
        from commands.minigames.wordchain.setwordchainchannel import setwordchainchannel as command_fn
        await command_fn(info, channel=info.channel)
    assert_matrix_outcome(info, "no_guild", PROFILE, mocks)


async def test_setwordchainchannel_admin(admin_command_info):
    info = admin_command_info
    info.channel.send = AsyncMock()
    with profile_patches(PROFILE) as mocks:
        from commands.minigames.wordchain.setwordchainchannel import setwordchainchannel as command_fn
        await command_fn(info, channel=info.channel)
    assert_matrix_outcome(info, "admin", PROFILE, mocks)
