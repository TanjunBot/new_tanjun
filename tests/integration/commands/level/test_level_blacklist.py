import pytest
from unittest.mock import AsyncMock, patch

from commands.level.level_blacklist import (
    add_channel_to_blacklist_command,
    add_role_to_blacklist_command,
    add_user_to_blacklist_command,
    remove_channel_from_blacklist_command,
    remove_role_from_blacklist_command,
    remove_user_from_blacklist_command,
    show_blacklist_command,
)
from tests.helpers.discord import make_role, make_target_member, make_text_channel


pytestmark = pytest.mark.asyncio


async def test_add_channel_missing_permission(restricted_command_info):
    channel = make_text_channel(guild=restricted_command_info.guild)
    await add_channel_to_blacklist_command(restricted_command_info, channel)
    restricted_command_info.reply.assert_awaited_once()


@patch("commands.level.level_blacklist.add_channel_to_blacklist", new_callable=AsyncMock)
async def test_add_channel_success(mock_add, admin_command_info):
    channel = make_text_channel(guild=admin_command_info.guild)
    await add_channel_to_blacklist_command(admin_command_info, channel, "spam")
    mock_add.assert_awaited_once()
    admin_command_info.reply.assert_awaited_once()


async def test_remove_channel_missing_permission(restricted_command_info):
    channel = make_text_channel(guild=restricted_command_info.guild)
    await remove_channel_from_blacklist_command(restricted_command_info, channel)
    restricted_command_info.reply.assert_awaited_once()


@patch("commands.level.level_blacklist.remove_channel_from_blacklist", new_callable=AsyncMock)
async def test_remove_channel_success(mock_remove, admin_command_info):
    channel = make_text_channel(guild=admin_command_info.guild)
    await remove_channel_from_blacklist_command(admin_command_info, channel)
    mock_remove.assert_awaited_once()


@patch("commands.level.level_blacklist.add_role_to_blacklist", new_callable=AsyncMock)
async def test_add_role_success(mock_add, admin_command_info):
    role = make_role()
    await add_role_to_blacklist_command(admin_command_info, role)
    mock_add.assert_awaited_once()


@patch("commands.level.level_blacklist.add_user_to_blacklist", new_callable=AsyncMock)
async def test_add_user_success(mock_add, admin_command_info):
    user = make_target_member()
    await add_user_to_blacklist_command(admin_command_info, user)
    mock_add.assert_awaited_once()


@patch("commands.level.level_blacklist.get_blacklist", new_callable=AsyncMock, return_value={"channels": [], "roles": [], "users": []})
async def test_show_blacklist(mock_get, admin_command_info):
    await show_blacklist_command(admin_command_info)
    admin_command_info.reply.assert_awaited_once()
