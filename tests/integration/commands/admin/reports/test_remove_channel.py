from unittest.mock import AsyncMock, patch

import pytest

from commands.admin.reports.remove_channel import remove_channel

pytestmark = pytest.mark.asyncio


async def test_remove_channel_missing_user_permission(restricted_command_info):
    await remove_channel(restricted_command_info)
    restricted_command_info.reply.assert_awaited_once()


@patch("commands.admin.reports.remove_channel.get_report_channel", new_callable=AsyncMock, return_value=None)
async def test_remove_channel_no_channel(mock_get, admin_command_info):
    await remove_channel(admin_command_info)
    admin_command_info.reply.assert_awaited_once()


@patch("commands.admin.reports.remove_channel.remove_report_channel", new_callable=AsyncMock)
@patch("commands.admin.reports.remove_channel.get_report_channel", new_callable=AsyncMock, return_value=True)
async def test_remove_channel_success(mock_get, mock_remove, admin_command_info):
    await remove_channel(admin_command_info)
    mock_remove.assert_awaited_once()
    admin_command_info.reply.assert_awaited_once()
