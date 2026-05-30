from unittest.mock import AsyncMock, patch

import pytest

from commands.level.set_levelup_channel import set_levelup_channel_command
from tests.helpers.discord import make_text_channel

pytestmark = pytest.mark.asyncio


async def test_set_levelup_channel_missing_permission(restricted_command_info):
    channel = make_text_channel(guild=restricted_command_info.guild)
    await set_levelup_channel_command(restricted_command_info, channel)
    restricted_command_info.reply.assert_awaited_once()


@patch("commands.level.set_levelup_channel.set_levelup_channel", new_callable=AsyncMock)
async def test_set_levelup_channel_success(mock_set, admin_command_info):
    channel = make_text_channel(guild=admin_command_info.guild)
    await set_levelup_channel_command(admin_command_info, channel)
    mock_set.assert_awaited_once_with(str(admin_command_info.guild.id), str(channel.id))
    admin_command_info.reply.assert_awaited_once()


@patch("commands.level.set_levelup_channel.set_levelup_channel", new_callable=AsyncMock)
async def test_set_levelup_channel_reset(mock_set, admin_command_info):
    await set_levelup_channel_command(admin_command_info, None)
    mock_set.assert_awaited_once_with(str(admin_command_info.guild.id), None)
    admin_command_info.reply.assert_awaited_once()
