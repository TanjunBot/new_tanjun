from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import discord
import pytest

from commands.level.level_blacklist import (
    add_role_to_blacklist_command,
    add_user_to_blacklist_command,
    remove_role_from_blacklist_command,
    remove_user_from_blacklist_command,
    show_blacklist_command,
)
from tests.helpers.discord import make_permissions, make_role, make_target_member

pytestmark = pytest.mark.asyncio


def _deny_admin(info):
    perms = make_permissions(administrator=False)
    info.channel.permissions_for = MagicMock(return_value=perms)


@patch("commands.level.level_blacklist.isinstance")
async def test_add_role_no_permission(mock_isinstance, admin_command_info):
    mock_isinstance.side_effect = lambda obj, cls: cls is discord.Member or cls is discord.abc.GuildChannel
    _deny_admin(admin_command_info)
    await add_role_to_blacklist_command(admin_command_info, make_role())
    admin_command_info.reply.assert_awaited_once()


@patch("commands.level.level_blacklist.isinstance")
async def test_remove_role_no_permission(mock_isinstance, admin_command_info):
    mock_isinstance.side_effect = lambda obj, cls: cls is discord.Member or cls is discord.abc.GuildChannel
    _deny_admin(admin_command_info)
    await remove_role_from_blacklist_command(admin_command_info, make_role())
    admin_command_info.reply.assert_awaited_once()


@patch("commands.level.level_blacklist.isinstance")
async def test_add_user_no_permission(mock_isinstance, admin_command_info):
    mock_isinstance.side_effect = lambda obj, cls: cls is discord.Member or cls is discord.abc.GuildChannel
    _deny_admin(admin_command_info)
    await add_user_to_blacklist_command(admin_command_info, make_target_member())
    admin_command_info.reply.assert_awaited_once()


@patch("commands.level.level_blacklist.isinstance")
async def test_remove_user_no_permission(mock_isinstance, admin_command_info):
    mock_isinstance.side_effect = lambda obj, cls: cls is discord.Member or cls is discord.abc.GuildChannel
    _deny_admin(admin_command_info)
    await remove_user_from_blacklist_command(admin_command_info, make_target_member())
    admin_command_info.reply.assert_awaited_once()


@patch("commands.level.level_blacklist.isinstance")
async def test_show_blacklist_no_permission(mock_isinstance, admin_command_info):
    mock_isinstance.side_effect = lambda obj, cls: cls is discord.Member or cls is discord.abc.GuildChannel
    _deny_admin(admin_command_info)
    await show_blacklist_command(admin_command_info)
    admin_command_info.reply.assert_awaited_once()


@patch("commands.level.level_blacklist.remove_role_from_blacklist", new_callable=AsyncMock)
async def test_remove_role_success(mock_remove, admin_command_info):
    await remove_role_from_blacklist_command(admin_command_info, make_role())
    mock_remove.assert_awaited_once()


@patch("commands.level.level_blacklist.remove_user_from_blacklist", new_callable=AsyncMock)
async def test_remove_user_success(mock_remove, admin_command_info):
    await remove_user_from_blacklist_command(admin_command_info, make_target_member())
    mock_remove.assert_awaited_once()


@patch("commands.level.level_blacklist.get_blacklist", new_callable=AsyncMock)
async def test_show_blacklist_with_entries(mock_get, admin_command_info):
    mock_get.return_value = {
        "channels": [("111", "spam")],
        "roles": [("222", None)],
        "users": [("333", "abuse")],
    }
    await show_blacklist_command(admin_command_info)
    admin_command_info.reply.assert_awaited_once()
