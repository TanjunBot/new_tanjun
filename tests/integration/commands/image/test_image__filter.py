"""Integration tests for commands.image._filter.apply_filter."""

from __future__ import annotations

from unittest.mock import AsyncMock
import pytest

from tests.helpers.assertions import assert_matrix_outcome
from tests.helpers.command_profiles import CommandProfile, profile_patches


pytestmark = [pytest.mark.asyncio, pytest.mark.integration]

PROFILE = CommandProfile.from_module('commands.image._filter', 'apply_filter', 'info, image=None, filter_name=None')


async def test_apply_filter_restricted(restricted_command_info):
    info = restricted_command_info
    with profile_patches(PROFILE) as mocks:
        from commands.image._filter import apply_filter as command_fn
        await command_fn(info, image=None, filter_name=None)
    assert_matrix_outcome(info, "restricted", PROFILE, mocks)


async def test_apply_filter_no_guild(no_guild_command_info):
    info = no_guild_command_info
    with profile_patches(PROFILE) as mocks:
        from commands.image._filter import apply_filter as command_fn
        await command_fn(info, image=None, filter_name=None)
    assert_matrix_outcome(info, "no_guild", PROFILE, mocks)


async def test_apply_filter_admin(admin_command_info):
    info = admin_command_info
    with profile_patches(PROFILE) as mocks:
        from commands.image._filter import apply_filter as command_fn
        await command_fn(info, image=None, filter_name=None)
    assert_matrix_outcome(info, "admin", PROFILE, mocks)
