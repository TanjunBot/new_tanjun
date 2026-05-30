"""Integration tests for commands.utility.removescheduled.remove_scheduled_message."""

from __future__ import annotations

from unittest.mock import AsyncMock
import pytest

from tests.helpers.assertions import assert_matrix_outcome
from tests.helpers.command_profiles import CommandProfile, profile_patches


pytestmark = [pytest.mark.asyncio, pytest.mark.integration]

PROFILE = CommandProfile.from_module('commands.utility.removescheduled', 'remove_scheduled_message', 'info, message_id=1')


async def test_remove_scheduled_message_restricted(restricted_command_info):
    info = restricted_command_info
    with profile_patches(PROFILE) as mocks:
        from commands.utility.removescheduled import remove_scheduled_message as command_fn
        await command_fn(info, message_id=1)
    assert_matrix_outcome(info, "restricted", PROFILE, mocks)


async def test_remove_scheduled_message_no_guild(no_guild_command_info):
    info = no_guild_command_info
    with profile_patches(PROFILE) as mocks:
        from commands.utility.removescheduled import remove_scheduled_message as command_fn
        await command_fn(info, message_id=1)
    assert_matrix_outcome(info, "no_guild", PROFILE, mocks)


async def test_remove_scheduled_message_admin(admin_command_info):
    info = admin_command_info
    with profile_patches(PROFILE) as mocks:
        from commands.utility.removescheduled import remove_scheduled_message as command_fn
        await command_fn(info, message_id=1)
    assert_matrix_outcome(info, "admin", PROFILE, mocks)
