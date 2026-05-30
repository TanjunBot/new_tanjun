from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from commands.channel.dynamicslowmode import (
    addDynamicslowmode,
    getDynamicslowmode_channels,
    removeDynamicslowmode,
)
from commands.channel.farewell import removeFarewellChannel, setFarewellChannel
from commands.channel.media import addMediaChannel, removeMediaChannel
from commands.channel.welcome import removeWelcomeChannel, setWelcomeChannel


pytestmark = pytest.mark.asyncio


async def test_welcome_no_permission(restricted_command_info):
    await setWelcomeChannel(restricted_command_info, restricted_command_info.channel)
    restricted_command_info.reply.assert_awaited_once()


async def test_welcome_bot_missing_perms(admin_command_info):
    perms = MagicMock(send_messages=False, embed_links=True, attach_files=True)
    admin_command_info.channel.permissions_for = MagicMock(return_value=perms)
    await setWelcomeChannel(admin_command_info, admin_command_info.channel)
    admin_command_info.reply.assert_awaited_once()


@patch("commands.channel.welcome.get_welcome_channel", new_callable=AsyncMock, return_value=True)
async def test_welcome_already_set(mock_get, admin_command_info):
    perms = MagicMock(send_messages=True, embed_links=True, attach_files=True)
    admin_command_info.channel.permissions_for = MagicMock(return_value=perms)
    await setWelcomeChannel(admin_command_info, admin_command_info.channel)
    admin_command_info.reply.assert_awaited_once()


@patch("commands.channel.welcome.set_welcome_channel", new_callable=AsyncMock)
@patch("commands.channel.welcome.get_welcome_channel", new_callable=AsyncMock, return_value=False)
async def test_welcome_success(mock_get, mock_set, admin_command_info):
    perms = MagicMock(send_messages=True, embed_links=True, attach_files=True)
    admin_command_info.channel.permissions_for = MagicMock(return_value=perms)
    await setWelcomeChannel(admin_command_info, admin_command_info.channel, message="hi")
    mock_set.assert_awaited_once()
    admin_command_info.reply.assert_awaited_once()


@patch("commands.channel.welcome.remove_welcome_channel", new_callable=AsyncMock, return_value=True)
async def test_remove_welcome_success(mock_remove, admin_command_info):
    await removeWelcomeChannel(admin_command_info)
    admin_command_info.reply.assert_awaited_once()


async def test_farewell_no_permission(restricted_command_info):
    await setFarewellChannel(restricted_command_info, restricted_command_info.channel)
    restricted_command_info.reply.assert_awaited_once()


@patch("commands.channel.farewell.set_leave_channel", new_callable=AsyncMock)
@patch("commands.channel.farewell.get_leave_channel", new_callable=AsyncMock, return_value=False)
async def test_farewell_success(mock_get, mock_set, admin_command_info):
    perms = MagicMock(send_messages=True, embed_links=True, attach_files=True)
    admin_command_info.channel.permissions_for = MagicMock(return_value=perms)
    await setFarewellChannel(admin_command_info, admin_command_info.channel)
    mock_set.assert_awaited_once()


@patch("commands.channel.farewell.remove_leave_channel", new_callable=AsyncMock, return_value=True)
async def test_remove_farewell(mock_remove, admin_command_info):
    await removeFarewellChannel(admin_command_info)
    admin_command_info.reply.assert_awaited_once()


async def test_media_add_no_permission(restricted_command_info):
    await addMediaChannel(restricted_command_info, restricted_command_info.channel)
    restricted_command_info.reply.assert_awaited_once()


@patch("commands.channel.media.add_media_channel", new_callable=AsyncMock)
@patch("commands.channel.media.get_media_channel", new_callable=AsyncMock, return_value=None)
async def test_media_add_success(mock_get, mock_add, admin_command_info):
    await addMediaChannel(admin_command_info, admin_command_info.channel)
    mock_add.assert_awaited_once()


@patch("commands.channel.media.remove_media_channel", new_callable=AsyncMock, return_value=True)
async def test_media_remove_success(mock_remove, admin_command_info):
    await removeMediaChannel(admin_command_info, admin_command_info.channel)
    admin_command_info.reply.assert_awaited_once()


async def test_dynamicslowmode_no_permission(restricted_command_info):
    await addDynamicslowmode(restricted_command_info, restricted_command_info.channel, 5, 60, 30)
    restricted_command_info.reply.assert_awaited_once()


@patch("commands.channel.dynamicslowmode._ds_service.configure", new_callable=AsyncMock)
@patch("commands.channel.dynamicslowmode._ds_service.get_config", new_callable=AsyncMock, return_value=None)
async def test_dynamicslowmode_add_success(mock_get, mock_configure, admin_command_info):
    perms = MagicMock(manage_messages=True, read_message_history=True, manage_channels=True)
    admin_command_info.channel.permissions_for = MagicMock(return_value=perms)
    await addDynamicslowmode(admin_command_info, admin_command_info.channel, 5, 60, 30)
    mock_configure.assert_awaited_once()


@patch("commands.channel.dynamicslowmode._ds_service.remove", new_callable=AsyncMock)
@patch("commands.channel.dynamicslowmode._ds_service.get_config", new_callable=AsyncMock, return_value=MagicMock())
async def test_dynamicslowmode_remove_success(mock_get, mock_remove, admin_command_info):
    await removeDynamicslowmode(admin_command_info, admin_command_info.channel)
    mock_remove.assert_awaited_once()


@patch("commands.channel.dynamicslowmode._ds_service.get_all_configs", new_callable=AsyncMock, return_value=[])
async def test_dynamicslowmode_list_empty(mock_get, admin_command_info):
    await getDynamicslowmode_channels(admin_command_info)
    admin_command_info.reply.assert_awaited_once()
