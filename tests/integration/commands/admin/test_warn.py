import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from commands.admin.warn import warn_user
from tests.helpers.discord import make_role, make_target_member, make_warn_config
from tests.integration.commands.admin.conftest import async_iter_from


pytestmark = pytest.mark.asyncio


async def test_warn_user_missing_permission(restricted_command_info):
    member = make_target_member()
    await warn_user(restricted_command_info, member)
    restricted_command_info.reply.assert_awaited_once()


async def test_warn_user_target_too_high(admin_command_info):
    member = make_target_member(top_role_position=100)
    admin_command_info.user.top_role = make_role(position=1)
    await warn_user(admin_command_info, member)
    admin_command_info.reply.assert_awaited_once()


@patch("commands.admin.warn.get_warnings")
@patch("commands.admin.warn.add_warning", new_callable=AsyncMock)
@patch("commands.admin.warn.get_warn_config", new_callable=AsyncMock)
async def test_warn_user_success(mock_config, mock_add, mock_warnings, admin_command_info):
    mock_config.return_value = make_warn_config()
    mock_warnings.return_value = async_iter_from([])
    member = make_target_member(top_role_position=1)
    await warn_user(admin_command_info, member, reason="spam")
    mock_add.assert_awaited_once()
    admin_command_info.reply.assert_awaited_once()
    member.send.assert_awaited_once()


@patch("commands.admin.warn.get_warnings")
@patch("commands.admin.warn.add_warning", new_callable=AsyncMock)
@patch("commands.admin.warn.get_warn_config", new_callable=AsyncMock)
async def test_warn_user_no_reason(mock_config, mock_add, mock_warnings, admin_command_info):
    mock_config.return_value = make_warn_config(expiration_days=7)
    mock_warnings.return_value = async_iter_from([MagicMock()])
    member = make_target_member(top_role_position=1)
    await warn_user(admin_command_info, member)
    mock_add.assert_awaited_once()


@patch("commands.admin.warn.get_warnings")
@patch("commands.admin.warn.add_warning", new_callable=AsyncMock)
@patch("commands.admin.warn.get_warn_config", new_callable=AsyncMock)
async def test_warn_user_ban_threshold(mock_config, mock_add, mock_warnings, admin_command_info):
    mock_config.return_value = make_warn_config(ban_threshold=1, kick_threshold=5, timeout_threshold=3)
    mock_warnings.return_value = async_iter_from([MagicMock()])
    member = make_target_member(top_role_position=1)
    await warn_user(admin_command_info, member, reason="bad")
    member.ban.assert_awaited_once()


@patch("commands.admin.warn.get_warnings")
@patch("commands.admin.warn.add_warning", new_callable=AsyncMock)
@patch("commands.admin.warn.get_warn_config", new_callable=AsyncMock)
async def test_warn_user_kick_threshold(mock_config, mock_add, mock_warnings, admin_command_info):
    mock_config.return_value = make_warn_config(ban_threshold=10, kick_threshold=1, timeout_threshold=3)
    mock_warnings.return_value = async_iter_from([MagicMock()])
    member = make_target_member(top_role_position=1)
    await warn_user(admin_command_info, member, reason="bad")
    member.kick.assert_awaited_once()


@patch("commands.admin.warn.get_warnings")
@patch("commands.admin.warn.add_warning", new_callable=AsyncMock)
@patch("commands.admin.warn.get_warn_config", new_callable=AsyncMock)
async def test_warn_user_timeout_threshold(mock_config, mock_add, mock_warnings, admin_command_info):
    mock_config.return_value = make_warn_config(ban_threshold=10, kick_threshold=5, timeout_threshold=1, timeout_duration=30)
    mock_warnings.return_value = async_iter_from([MagicMock()])
    member = make_target_member(top_role_position=1)
    await warn_user(admin_command_info, member, reason="bad")
    member.timeout.assert_awaited_once()


@patch("commands.admin.warn.get_warnings")
@patch("commands.admin.warn.add_warning", new_callable=AsyncMock)
@patch("commands.admin.warn.get_warn_config", new_callable=AsyncMock)
async def test_warn_user_dm_forbidden(mock_config, mock_add, mock_warnings, admin_command_info):
    import discord as discord_mod

    mock_config.return_value = make_warn_config()
    mock_warnings.return_value = async_iter_from([])
    member = make_target_member(top_role_position=1)
    member.send = AsyncMock(side_effect=discord_mod.Forbidden(MagicMock(), "forbidden"))
    await warn_user(admin_command_info, member, reason="spam")
    admin_command_info.reply.assert_awaited_once()
