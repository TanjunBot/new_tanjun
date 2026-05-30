from unittest.mock import AsyncMock, patch

import pytest

from commands.level.change_levelup_message import change_levelup_message

pytestmark = pytest.mark.asyncio


async def test_change_levelup_message_missing_permission(restricted_command_info):
    await change_levelup_message(restricted_command_info, "hello")
    restricted_command_info.reply.assert_awaited_once()


async def test_change_levelup_message_too_long(admin_command_info):
    await change_levelup_message(admin_command_info, "x" * 256)
    admin_command_info.reply.assert_awaited_once()


@patch("commands.level.change_levelup_message.set_levelup_message", new_callable=AsyncMock)
async def test_change_levelup_message_success(mock_set, admin_command_info):
    await change_levelup_message(admin_command_info, "GG {user}!")
    mock_set.assert_awaited_once()
    admin_command_info.reply.assert_awaited_once()


@patch("commands.level.change_levelup_message.set_levelup_message", new_callable=AsyncMock)
async def test_change_levelup_message_guild_id(mock_set, admin_command_info):
    await change_levelup_message(admin_command_info, "level up")
    mock_set.assert_awaited_once_with(str(admin_command_info.guild.id), "level up")
