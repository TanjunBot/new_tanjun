"""Integration tests for commands.utility.twitch.add_twitch_live_notification.addTwitchLiveNotification."""

from __future__ import annotations

from unittest.mock import AsyncMock
import pytest

from tests.helpers.assertions import assert_matrix_outcome
from tests.helpers.command_profiles import CommandProfile, profile_patches


pytestmark = [pytest.mark.asyncio, pytest.mark.integration]

PROFILE = CommandProfile.from_module('commands.utility.twitch.add_twitch_live_notification', 'addTwitchLiveNotification', 'info, twitch_name=None, channel=info.channel, notification_message=None')


async def test_addTwitchLiveNotification_restricted(restricted_command_info):
    info = restricted_command_info
    with profile_patches(PROFILE) as mocks:
        from commands.utility.twitch.add_twitch_live_notification import addTwitchLiveNotification as command_fn
        await command_fn(info, twitch_name=None, channel=info.channel, notification_message=None)
    assert_matrix_outcome(info, "restricted", PROFILE, mocks)


async def test_addTwitchLiveNotification_no_guild(no_guild_command_info):
    info = no_guild_command_info
    with profile_patches(PROFILE) as mocks:
        from commands.utility.twitch.add_twitch_live_notification import addTwitchLiveNotification as command_fn
        await command_fn(info, twitch_name=None, channel=info.channel, notification_message=None)
    assert_matrix_outcome(info, "no_guild", PROFILE, mocks)


async def test_addTwitchLiveNotification_admin(admin_command_info):
    info = admin_command_info
    with profile_patches(PROFILE) as mocks:
        from commands.utility.twitch.add_twitch_live_notification import addTwitchLiveNotification as command_fn
        await command_fn(info, twitch_name=None, channel=info.channel, notification_message=None)
    assert_matrix_outcome(info, "admin", PROFILE, mocks)
