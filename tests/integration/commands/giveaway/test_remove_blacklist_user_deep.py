from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest

from commands.giveaway.remove_blacklist_user import remove_blacklist_user
from tests.helpers.discord import make_target_member

pytestmark = pytest.mark.asyncio


async def test_remove_blacklist_user_no_permission(admin_command_info):
    admin_command_info.permissions.administrator = False
    user = make_target_member(user_id=555555555)
    await remove_blacklist_user(admin_command_info, user)
    admin_command_info.reply.assert_awaited_once()


@patch(
    "commands.giveaway.remove_blacklist_user.giveaway_service.is_user_blacklisted", new_callable=AsyncMock, return_value=False
)
async def test_remove_blacklist_user_not_blacklisted(mock_is, admin_command_info):
    user = make_target_member(user_id=555555555)
    await remove_blacklist_user(admin_command_info, user)
    admin_command_info.reply.assert_awaited_once()


@patch("commands.giveaway.remove_blacklist_user.giveaway_service.remove_blacklisted_user", new_callable=AsyncMock)
@patch(
    "commands.giveaway.remove_blacklist_user.giveaway_service.is_user_blacklisted", new_callable=AsyncMock, return_value=True
)
async def test_remove_blacklist_user_success(mock_is, mock_remove, admin_command_info):
    user = make_target_member(user_id=555555555)
    await remove_blacklist_user(admin_command_info, user)
    mock_remove.assert_awaited_once()
    admin_command_info.reply.assert_awaited_once()
