import pytest
from unittest.mock import AsyncMock, patch

from commands.level.enable_level_system import enable_level_system


pytestmark = pytest.mark.asyncio


async def test_enable_level_system_missing_permission(restricted_command_info):
    await enable_level_system(restricted_command_info)
    restricted_command_info.reply.assert_awaited_once()
    assert "embed" in restricted_command_info.reply.await_args.kwargs


@patch("commands.level.enable_level_system.get_level_system_status", new_callable=AsyncMock, return_value=True)
async def test_enable_level_system_already_set(mock_status, admin_command_info):
    await enable_level_system(admin_command_info)
    admin_command_info.reply.assert_awaited_once()
    assert "embed" in admin_command_info.reply.await_args.kwargs


@patch("commands.level.enable_level_system.get_level_system_status", new_callable=AsyncMock, return_value=False)
@patch("commands.level.enable_level_system.set_level_system_status", new_callable=AsyncMock)
async def test_enable_level_system_success(mock_set, mock_status, admin_command_info):
    await enable_level_system(admin_command_info)
    mock_set.assert_awaited_once()
    admin_command_info.reply.assert_awaited_once()
    assert "embed" in admin_command_info.reply.await_args.kwargs


@patch("commands.level.enable_level_system.get_level_system_status", new_callable=AsyncMock, return_value=False)
@patch("commands.level.enable_level_system.set_level_system_status", new_callable=AsyncMock)
async def test_enable_level_system_calls_api_with_guild_id(mock_set, mock_status, admin_command_info):
    await enable_level_system(admin_command_info)
    mock_set.assert_awaited_once_with(str(admin_command_info.guild.id), True)


async def test_enable_level_system_requires_guild(admin_command_info):
    admin_command_info.guild = None
    with pytest.raises((AssertionError, ValueError)):
        await enable_level_system(admin_command_info)


@patch("commands.level.enable_level_system.get_level_system_status", new_callable=AsyncMock, return_value=False)
@patch("commands.level.enable_level_system.set_level_system_status", new_callable=AsyncMock)
async def test_enable_level_system_reply_called_once(mock_set, mock_status, admin_command_info):
    await enable_level_system(admin_command_info)
    assert admin_command_info.reply.await_count == 1
