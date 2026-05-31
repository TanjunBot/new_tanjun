from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import discord
import pytest

from commands.logs.blacklist_user.blacklist_remove_user import blacklist_remove_user
from tests.helpers.assertions import assert_reply_embed
from tests.helpers.discord import make_permissions
from tests.integration.commands.conftest import make_user

pytestmark = pytest.mark.asyncio


@patch("commands.logs.blacklist_user.blacklist_remove_user.isinstance")
async def test_missing_permission(mock_isinstance, admin_command_info):
    mock_isinstance.side_effect = lambda obj, cls: cls is discord.Member or cls is discord.abc.GuildChannel
    admin_command_info.channel.permissions_for = MagicMock(return_value=make_permissions(administrator=False))
    await blacklist_remove_user(admin_command_info, make_user())
    assert_reply_embed(admin_command_info)


@patch(
    "commands.logs.blacklist_user.blacklist_remove_user.is_log_entity_blacklisted",
    new_callable=AsyncMock,
    return_value=False,
)
async def test_not_blacklisted(mock_is, admin_command_info):
    await blacklist_remove_user(admin_command_info, make_user())
    assert_reply_embed(admin_command_info)


@patch("commands.logs.blacklist_user.blacklist_remove_user.remove_log_blacklist", new_callable=AsyncMock)
@patch(
    "commands.logs.blacklist_user.blacklist_remove_user.is_log_entity_blacklisted",
    new_callable=AsyncMock,
    return_value=True,
)
async def test_success(mock_is, mock_remove, admin_command_info):
    await blacklist_remove_user(admin_command_info, make_user())
    assert_reply_embed(admin_command_info)
    mock_remove.assert_awaited_once()
