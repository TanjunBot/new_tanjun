from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from commands.channel.media import addMediaChannel, mediaChannelMessage, removeMediaChannel
from tests.helpers.discord import make_permissions, make_text_channel

pytestmark = pytest.mark.asyncio


def _target_channel(guild, bot_perms=None):
    ch = make_text_channel(guild=guild)
    ch.send = AsyncMock()
    if bot_perms is None:
        bot_perms = make_permissions(manage_messages=True, read_message_history=True)
    ch.permissions_for = MagicMock(return_value=bot_perms)
    return ch


async def test_add_media_channel_no_permission(admin_command_info):
    perms = make_permissions(manage_channels=False)
    admin_command_info.channel.permissions_for = MagicMock(return_value=perms)
    ch = _target_channel(admin_command_info.guild)
    await addMediaChannel(admin_command_info, ch)
    admin_command_info.reply.assert_awaited_once()


async def test_add_media_channel_bot_missing_perms(admin_command_info):
    perms = make_permissions(manage_channels=True)
    admin_command_info.channel.permissions_for = MagicMock(return_value=perms)
    ch = _target_channel(admin_command_info.guild, make_permissions(manage_messages=False))
    await addMediaChannel(admin_command_info, ch)
    admin_command_info.reply.assert_awaited_once()


@patch("commands.channel.media.get_media_channel", new_callable=AsyncMock, return_value=True)
async def test_add_media_channel_already_set(mock_get, admin_command_info):
    perms = make_permissions(manage_channels=True)
    admin_command_info.channel.permissions_for = MagicMock(return_value=perms)
    ch = _target_channel(admin_command_info.guild)
    await addMediaChannel(admin_command_info, ch)
    admin_command_info.reply.assert_awaited_once()


@patch("commands.channel.media.add_media_channel", new_callable=AsyncMock)
@patch("commands.channel.media.get_media_channel", new_callable=AsyncMock, return_value=None)
async def test_add_media_channel_success(mock_get, mock_add, admin_command_info):
    perms = make_permissions(manage_channels=True)
    admin_command_info.channel.permissions_for = MagicMock(return_value=perms)
    ch = _target_channel(admin_command_info.guild)
    await addMediaChannel(admin_command_info, ch)
    ch.send.assert_awaited_once()
    mock_add.assert_awaited_once()
    admin_command_info.reply.assert_awaited_once()


async def test_remove_media_channel_no_permission(admin_command_info):
    perms = make_permissions(manage_channels=False)
    admin_command_info.channel.permissions_for = MagicMock(return_value=perms)
    ch = _target_channel(admin_command_info.guild)
    await removeMediaChannel(admin_command_info, ch)
    admin_command_info.reply.assert_awaited_once()


@patch("commands.channel.media.get_media_channel", new_callable=AsyncMock, return_value=None)
async def test_remove_media_channel_not_set(mock_get, admin_command_info):
    perms = make_permissions(manage_channels=True)
    admin_command_info.channel.permissions_for = MagicMock(return_value=perms)
    ch = _target_channel(admin_command_info.guild)
    await removeMediaChannel(admin_command_info, ch)
    admin_command_info.reply.assert_awaited_once()


@patch("commands.channel.media.remove_media_channel", new_callable=AsyncMock)
@patch("commands.channel.media.get_media_channel", new_callable=AsyncMock, return_value=True)
async def test_remove_media_channel_success(mock_get, mock_remove, admin_command_info):
    perms = make_permissions(manage_channels=True)
    admin_command_info.channel.permissions_for = MagicMock(return_value=perms)
    ch = _target_channel(admin_command_info.guild)
    await removeMediaChannel(admin_command_info, ch)
    ch.send.assert_awaited_once()
    mock_remove.assert_awaited_once()


@patch("commands.channel.media.check_if_opted_out", new_callable=AsyncMock, return_value=False)
@patch("commands.channel.media.get_media_channel", new_callable=AsyncMock, return_value=True)
async def test_media_message_deletes_non_media(mock_get, mock_opt):
    msg = MagicMock()
    msg.channel = MagicMock(id=1)
    msg.author = MagicMock(id=2)
    msg.author.send = AsyncMock()
    msg.attachments = []
    msg.delete = AsyncMock()
    msg.guild = MagicMock(preferred_locale="en_US")
    await mediaChannelMessage(msg)
    msg.delete.assert_awaited_once()
    msg.author.send.assert_awaited_once()


@patch("commands.channel.media.check_if_opted_out", new_callable=AsyncMock, return_value=True)
@patch("commands.channel.media.get_media_channel", new_callable=AsyncMock, return_value=True)
async def test_media_message_opted_out(mock_get, mock_opt):
    msg = MagicMock()
    msg.channel = MagicMock(id=1)
    msg.author = MagicMock(id=2)
    msg.author.send = AsyncMock()
    msg.attachments = []
    msg.delete = AsyncMock()
    msg.guild = MagicMock(preferred_locale="en_US")
    await mediaChannelMessage(msg)
    msg.delete.assert_awaited_once()


@patch("commands.channel.media.get_media_channel", new_callable=AsyncMock, return_value=False)
async def test_media_message_not_media_channel(mock_get):
    msg = MagicMock()
    msg.channel = MagicMock(id=1)
    msg.delete = AsyncMock()
    await mediaChannelMessage(msg)
    msg.delete.assert_not_awaited()
