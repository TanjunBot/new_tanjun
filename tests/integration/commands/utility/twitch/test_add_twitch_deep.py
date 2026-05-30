from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import discord
import pytest

from commands.utility.twitch.add_twitch_live_notification import addTwitchLiveNotification
from tests.helpers.discord import make_permissions, make_text_channel


pytestmark = pytest.mark.asyncio


@patch("commands.utility.twitch.add_twitch_live_notification.isinstance")
async def test_add_twitch_no_admin(mock_isinstance, admin_command_info):
    mock_isinstance.side_effect = lambda obj, cls: cls is discord.Member or cls is discord.abc.GuildChannel
    perms = make_permissions(administrator=False)
    admin_command_info.channel.permissions_for = MagicMock(return_value=perms)
    ch = make_text_channel(guild=admin_command_info.guild)
    await addTwitchLiveNotification(admin_command_info, "streamer", ch)
    admin_command_info.reply.assert_awaited_once()


@patch("commands.utility.twitch.add_twitch_live_notification.isinstance")
async def test_add_twitch_bot_perms_fail(mock_isinstance, admin_command_info):
    mock_isinstance.side_effect = lambda obj, cls: cls is discord.Member or cls is discord.abc.GuildChannel
    ch = make_text_channel(guild=admin_command_info.guild)
    bot_perms = make_permissions(send_messages=False, embed_links=False)
    ch.permissions_for = MagicMock(return_value=bot_perms)
    await addTwitchLiveNotification(admin_command_info, "streamer", ch)
    admin_command_info.reply.assert_awaited_once()


@patch("commands.utility.twitch.add_twitch_live_notification.get_uuid_by_twitch_name", new_callable=AsyncMock, return_value=None)
@patch("commands.utility.twitch.add_twitch_live_notification.isinstance")
async def test_add_twitch_name_not_found(mock_isinstance, mock_uuid, admin_command_info):
    mock_isinstance.side_effect = lambda obj, cls: cls is discord.Member or cls is discord.abc.GuildChannel
    ch = make_text_channel(guild=admin_command_info.guild)
    bot_perms = make_permissions(send_messages=True, embed_links=True)
    ch.permissions_for = MagicMock(return_value=bot_perms)
    await addTwitchLiveNotification(admin_command_info, "missing", ch)
    admin_command_info.reply.assert_awaited_once()


@patch("commands.utility.twitch.add_twitch_live_notification.get_twitch_service", return_value=None)
@patch("commands.utility.twitch.add_twitch_live_notification.get_uuid_by_twitch_name", new_callable=AsyncMock, return_value="uuid-1")
@patch("commands.utility.twitch.add_twitch_live_notification.isinstance")
async def test_add_twitch_service_unavailable(mock_isinstance, mock_uuid, mock_svc, admin_command_info):
    mock_isinstance.side_effect = lambda obj, cls: cls is discord.Member or cls is discord.abc.GuildChannel
    ch = make_text_channel(guild=admin_command_info.guild)
    bot_perms = make_permissions(send_messages=True, embed_links=True)
    ch.permissions_for = MagicMock(return_value=bot_perms)
    await addTwitchLiveNotification(admin_command_info, "streamer", ch)
    admin_command_info.reply.assert_awaited_once()


@patch("commands.utility.twitch.add_twitch_live_notification.subscribe_to_twitch_online_notification", new_callable=AsyncMock)
@patch("commands.utility.twitch.add_twitch_live_notification.get_twitch_service")
@patch("commands.utility.twitch.add_twitch_live_notification.get_uuid_by_twitch_name", new_callable=AsyncMock, return_value="uuid-1")
@patch("commands.utility.twitch.add_twitch_live_notification.isinstance")
async def test_add_twitch_success(mock_isinstance, mock_uuid, mock_get_svc, mock_sub, admin_command_info):
    mock_isinstance.side_effect = lambda obj, cls: cls is discord.Member or cls is discord.abc.GuildChannel
    ch = make_text_channel(guild=admin_command_info.guild)
    bot_perms = make_permissions(send_messages=True, embed_links=True)
    ch.permissions_for = MagicMock(return_value=bot_perms)
    svc = MagicMock()
    svc.add_notification = AsyncMock()
    mock_get_svc.return_value = svc
    await addTwitchLiveNotification(admin_command_info, "streamer", ch, "Live!")
    svc.add_notification.assert_awaited_once()
    mock_sub.assert_awaited_once()
    admin_command_info.reply.assert_awaited_once()
