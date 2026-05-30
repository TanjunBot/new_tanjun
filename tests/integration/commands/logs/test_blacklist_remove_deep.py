from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import discord
import pytest

from commands.logs.blacklist_channel.blacklist_remove_channel import blacklist_remove_channel
from commands.logs.blacklist_role.blacklist_remove_role import blacklist_remove_role
from tests.helpers.discord import make_permissions, make_text_channel


pytestmark = pytest.mark.asyncio


@patch("commands.logs.blacklist_channel.blacklist_remove_channel.isinstance")
async def test_blacklist_remove_channel_no_admin(mock_isinstance, admin_command_info):
    mock_isinstance.side_effect = lambda obj, cls: cls is discord.Member or cls is discord.abc.GuildChannel
    perms = make_permissions(administrator=False)
    admin_command_info.channel.permissions_for = MagicMock(return_value=perms)
    channel = make_text_channel(guild=admin_command_info.guild)
    await blacklist_remove_channel(admin_command_info, channel)
    admin_command_info.reply.assert_awaited_once()


@patch("commands.logs.blacklist_channel.blacklist_remove_channel.is_log_entity_blacklisted", new_callable=AsyncMock, return_value=False)
async def test_blacklist_remove_channel_not_blacklisted(mock_is, admin_command_info):
    channel = make_text_channel(guild=admin_command_info.guild)
    await blacklist_remove_channel(admin_command_info, channel)
    admin_command_info.reply.assert_awaited_once()


@patch("commands.logs.blacklist_channel.blacklist_remove_channel.remove_log_blacklist", new_callable=AsyncMock)
@patch("commands.logs.blacklist_channel.blacklist_remove_channel.is_log_entity_blacklisted", new_callable=AsyncMock, return_value=True)
async def test_blacklist_remove_channel_success(mock_is, mock_remove, admin_command_info):
    channel = make_text_channel(guild=admin_command_info.guild)
    await blacklist_remove_channel(admin_command_info, channel)
    mock_remove.assert_awaited_once()
    admin_command_info.reply.assert_awaited_once()


@patch("commands.logs.blacklist_role.blacklist_remove_role.isinstance")
async def test_blacklist_remove_role_no_admin(mock_isinstance, admin_command_info):
    mock_isinstance.side_effect = lambda obj, cls: cls is discord.Member or cls is discord.abc.GuildChannel
    perms = make_permissions(administrator=False)
    admin_command_info.channel.permissions_for = MagicMock(return_value=perms)
    role = MagicMock()
    await blacklist_remove_role(admin_command_info, role)
    admin_command_info.reply.assert_awaited_once()


@patch("commands.logs.blacklist_role.blacklist_remove_role.is_log_entity_blacklisted", new_callable=AsyncMock, return_value=False)
async def test_blacklist_remove_role_not_blacklisted(mock_is, admin_command_info):
    role = MagicMock()
    await blacklist_remove_role(admin_command_info, role)
    admin_command_info.reply.assert_awaited_once()


@patch("commands.logs.blacklist_role.blacklist_remove_role.remove_log_blacklist", new_callable=AsyncMock)
@patch("commands.logs.blacklist_role.blacklist_remove_role.is_log_entity_blacklisted", new_callable=AsyncMock, return_value=True)
async def test_blacklist_remove_role_success(mock_is, mock_remove, admin_command_info):
    role = MagicMock()
    await blacklist_remove_role(admin_command_info, role)
    mock_remove.assert_awaited_once()
    admin_command_info.reply.assert_awaited_once()
