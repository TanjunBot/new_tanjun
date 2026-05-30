from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from commands.logs.blacklist_channel.blacklist_remove_channel import blacklist_remove_channel
from commands.logs.blacklist_role.blacklist_remove_role import blacklist_remove_role
from commands.logs.blacklist_user.blacklist_remove_user import blacklist_remove_user
from commands.logs.configure_logs import configure_logs
from commands.logs.remove_log_channel import remove_log_channel
from commands.logs.set_log_channel import set_log_channel
from tests.helpers.discord import make_role, make_target_member, make_text_channel

pytestmark = pytest.mark.asyncio


@patch("commands.logs.set_log_channel.set_log_channel_api", new_callable=AsyncMock)
async def test_set_log_channel_success(mock_set, admin_command_info):
    channel = make_text_channel(guild=admin_command_info.guild)
    await set_log_channel(admin_command_info, channel)
    mock_set.assert_awaited_once()
    admin_command_info.reply.assert_awaited_once()


async def test_set_log_channel_missing_permission(restricted_command_info):
    channel = make_text_channel(guild=restricted_command_info.guild)
    await set_log_channel(restricted_command_info, channel)
    restricted_command_info.reply.assert_awaited_once()


@patch("commands.logs.remove_log_channel.get_log_channel_api", new_callable=AsyncMock, return_value=444444444)
@patch("commands.logs.remove_log_channel.remove_log_channel_api", new_callable=AsyncMock)
async def test_remove_log_channel_success(mock_remove, mock_get, admin_command_info):
    await remove_log_channel(admin_command_info)
    mock_remove.assert_awaited_once()
    admin_command_info.reply.assert_awaited_once()


async def test_remove_log_channel_missing_permission(restricted_command_info):
    await remove_log_channel(restricted_command_info)
    restricted_command_info.reply.assert_awaited_once()


@patch("commands.logs.configure_logs.get_log_enable_api", new_callable=AsyncMock)
async def test_configure_logs_success(mock_get, admin_command_info):
    log_enabled = MagicMock()
    log_enabled.get_option = MagicMock(return_value=False)
    log_enabled.set_option = MagicMock()
    mock_get.return_value = log_enabled
    await configure_logs(admin_command_info)
    admin_command_info.reply.assert_awaited_once()
    assert admin_command_info.reply.await_args.kwargs.get("view") is not None


async def test_configure_logs_missing_permission(restricted_command_info):
    await configure_logs(restricted_command_info)
    restricted_command_info.reply.assert_awaited_once()


@patch(
    "commands.logs.blacklist_user.blacklist_remove_user.is_log_entity_blacklisted", new_callable=AsyncMock, return_value=False
)
async def test_blacklist_remove_user_not_blacklisted(mock_check, admin_command_info):
    user = make_target_member()
    await blacklist_remove_user(admin_command_info, user)
    admin_command_info.reply.assert_awaited_once()


@patch("commands.logs.blacklist_user.blacklist_remove_user.remove_log_blacklist", new_callable=AsyncMock)
@patch(
    "commands.logs.blacklist_user.blacklist_remove_user.is_log_entity_blacklisted", new_callable=AsyncMock, return_value=True
)
async def test_blacklist_remove_user_success(mock_check, mock_remove, admin_command_info):
    user = make_target_member()
    await blacklist_remove_user(admin_command_info, user)
    mock_remove.assert_awaited_once()
    admin_command_info.reply.assert_awaited_once()


async def test_blacklist_remove_user_missing_permission(restricted_command_info):
    user = make_target_member()
    await blacklist_remove_user(restricted_command_info, user)
    restricted_command_info.reply.assert_awaited_once()


@patch(
    "commands.logs.blacklist_role.blacklist_remove_role.is_log_entity_blacklisted", new_callable=AsyncMock, return_value=True
)
@patch("commands.logs.blacklist_role.blacklist_remove_role.remove_log_blacklist", new_callable=AsyncMock)
async def test_blacklist_remove_role_success(mock_remove, mock_check, admin_command_info):
    role = make_role()
    await blacklist_remove_role(admin_command_info, role)
    mock_remove.assert_awaited_once()


@patch(
    "commands.logs.blacklist_channel.blacklist_remove_channel.is_log_entity_blacklisted",
    new_callable=AsyncMock,
    return_value=True,
)
@patch("commands.logs.blacklist_channel.blacklist_remove_channel.remove_log_blacklist", new_callable=AsyncMock)
async def test_blacklist_remove_channel_success(mock_remove, mock_check, admin_command_info):
    channel = make_text_channel(guild=admin_command_info.guild)
    await blacklist_remove_channel(admin_command_info, channel)
    mock_remove.assert_awaited_once()
