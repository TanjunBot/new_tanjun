import pytest
from unittest.mock import AsyncMock, patch

from commands.level.level_boosts import (
    add_channel_boost_command,
    add_role_boost_command,
    add_user_boost_command,
    remove_channel_boost_command,
    remove_role_boost_command,
    remove_user_boost_command,
    show_boosts_command,
)
from tests.helpers.discord import make_role, make_target_member, make_text_channel


pytestmark = pytest.mark.asyncio


async def test_add_role_boost_missing_permission(restricted_command_info):
    role = make_role()
    await add_role_boost_command(restricted_command_info, role, 2.0, False)
    restricted_command_info.reply.assert_awaited_once()


@patch("commands.level.level_boosts.add_role_boost", new_callable=AsyncMock)
async def test_add_role_boost_success(mock_add, admin_command_info):
    role = make_role()
    await add_role_boost_command(admin_command_info, role, 2.0, False)
    mock_add.assert_awaited_once()


@patch("commands.level.level_boosts.add_channel_boost", new_callable=AsyncMock)
async def test_add_channel_boost_success(mock_add, admin_command_info):
    channel = make_text_channel(guild=admin_command_info.guild)
    await add_channel_boost_command(admin_command_info, channel, 1.5, True)
    mock_add.assert_awaited_once()


@patch("commands.level.level_boosts.add_user_boost", new_callable=AsyncMock)
async def test_add_user_boost_success(mock_add, admin_command_info):
    user = make_target_member()
    await add_user_boost_command(admin_command_info, user, 2.0, False)
    mock_add.assert_awaited_once()


@patch("commands.level.level_boosts.remove_role_boost", new_callable=AsyncMock)
async def test_remove_role_boost_success(mock_remove, admin_command_info):
    role = make_role()
    await remove_role_boost_command(admin_command_info, role)
    mock_remove.assert_awaited_once()


@patch("commands.level.level_boosts.remove_channel_boost", new_callable=AsyncMock)
async def test_remove_channel_boost_success(mock_remove, admin_command_info):
    channel = make_text_channel(guild=admin_command_info.guild)
    await remove_channel_boost_command(admin_command_info, channel)
    mock_remove.assert_awaited_once()


@patch("commands.level.level_boosts.get_all_boosts", new_callable=AsyncMock, return_value={"roles": [], "channels": [], "users": []})
async def test_show_boosts(mock_get, admin_command_info):
    await show_boosts_command(admin_command_info)
    admin_command_info.reply.assert_awaited_once()
