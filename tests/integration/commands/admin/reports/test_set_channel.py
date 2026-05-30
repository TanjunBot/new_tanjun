from unittest.mock import AsyncMock, patch

import pytest

from commands.admin.reports.set_channel import set_channel
from tests.helpers.discord import make_permissions, make_text_channel

pytestmark = pytest.mark.asyncio


async def test_set_channel_missing_user_permission(restricted_command_info):
    channel = make_text_channel(guild=restricted_command_info.guild)
    await set_channel(restricted_command_info, channel=channel)
    restricted_command_info.reply.assert_awaited_once()


async def test_set_channel_missing_bot_permission(admin_command_info):
    channel = make_text_channel(guild=admin_command_info.guild)
    channel.permissions_for = lambda m: make_permissions(send_messages=False)
    await set_channel(admin_command_info, channel=channel)
    admin_command_info.reply.assert_awaited_once()


@patch("commands.admin.reports.set_channel.get_report_channel", new_callable=AsyncMock, return_value=True)
async def test_set_channel_already_set(mock_get, admin_command_info):
    channel = make_text_channel(guild=admin_command_info.guild)
    channel.permissions_for = lambda m: make_permissions(send_messages=True)
    await set_channel(admin_command_info, channel=channel)
    admin_command_info.reply.assert_awaited_once()


@patch("commands.admin.reports.set_channel.set_report_channel", new_callable=AsyncMock)
@patch("commands.admin.reports.set_channel.get_report_channel", new_callable=AsyncMock, return_value=None)
async def test_set_channel_success(mock_get, mock_set, admin_command_info):
    channel = make_text_channel(guild=admin_command_info.guild)
    channel.permissions_for = lambda m: make_permissions(send_messages=True)
    await set_channel(admin_command_info, channel=channel)
    mock_set.assert_awaited_once()
    admin_command_info.reply.assert_awaited_once()
