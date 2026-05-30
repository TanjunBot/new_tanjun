from unittest.mock import AsyncMock, patch

import pytest

from commands.level.disable_levelup_message import disable_levelup_message

pytestmark = pytest.mark.asyncio


async def test_disable_levelup_message_missing_permission(restricted_command_info):
    await disable_levelup_message(restricted_command_info)
    restricted_command_info.reply.assert_awaited_once()
    assert "embed" in restricted_command_info.reply.await_args.kwargs


@patch("commands.level.disable_levelup_message.get_levelup_message_status", new_callable=AsyncMock, return_value=False)
async def test_disable_levelup_message_already_set(mock_status, admin_command_info):
    await disable_levelup_message(admin_command_info)
    admin_command_info.reply.assert_awaited_once()
    assert "embed" in admin_command_info.reply.await_args.kwargs


@patch("commands.level.disable_levelup_message.get_levelup_message_status", new_callable=AsyncMock, return_value=True)
@patch("commands.level.disable_levelup_message.set_levelup_message_status", new_callable=AsyncMock)
async def test_disable_levelup_message_success(mock_set, mock_status, admin_command_info):
    await disable_levelup_message(admin_command_info)
    mock_set.assert_awaited_once()
    admin_command_info.reply.assert_awaited_once()
    assert "embed" in admin_command_info.reply.await_args.kwargs


@patch("commands.level.disable_levelup_message.get_levelup_message_status", new_callable=AsyncMock, return_value=True)
@patch("commands.level.disable_levelup_message.set_levelup_message_status", new_callable=AsyncMock)
async def test_disable_levelup_message_calls_api_with_guild_id(mock_set, mock_status, admin_command_info):
    await disable_levelup_message(admin_command_info)
    mock_set.assert_awaited_once_with(str(admin_command_info.guild.id), False)


async def test_disable_levelup_message_requires_guild(admin_command_info):
    admin_command_info.guild = None
    with pytest.raises((AssertionError, ValueError)):
        await disable_levelup_message(admin_command_info)


@patch("commands.level.disable_levelup_message.get_levelup_message_status", new_callable=AsyncMock, return_value=True)
@patch("commands.level.disable_levelup_message.set_levelup_message_status", new_callable=AsyncMock)
async def test_disable_levelup_message_reply_called_once(mock_set, mock_status, admin_command_info):
    await disable_levelup_message(admin_command_info)
    assert admin_command_info.reply.await_count == 1
