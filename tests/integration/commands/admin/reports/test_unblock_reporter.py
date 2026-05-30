import pytest
from unittest.mock import AsyncMock, patch

from commands.admin.reports.unblock_reporter import unblock_reporter_cmd
from tests.helpers.discord import make_target_member


pytestmark = pytest.mark.asyncio


async def test_unblock_reporter_missing_user_permission(restricted_command_info):
    user = make_target_member()
    await unblock_reporter_cmd(restricted_command_info, user=user)
    restricted_command_info.reply.assert_awaited_once()


@patch("commands.admin.reports.unblock_reporter.check_if_reporter_is_blocked", new_callable=AsyncMock, return_value=False)
async def test_unblock_reporter_not_blocked(mock_check, admin_command_info):
    user = make_target_member()
    await unblock_reporter_cmd(admin_command_info, user=user)
    admin_command_info.reply.assert_awaited_once()


@patch("commands.admin.reports.unblock_reporter.unblock_reporter", new_callable=AsyncMock)
@patch("commands.admin.reports.unblock_reporter.check_if_reporter_is_blocked", new_callable=AsyncMock, return_value=True)
async def test_unblock_reporter_success(mock_check, mock_unblock, admin_command_info):
    user = make_target_member()
    await unblock_reporter_cmd(admin_command_info, user=user)
    mock_unblock.assert_awaited_once()
    admin_command_info.reply.assert_awaited_once()
