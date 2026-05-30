from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from commands.channel.dynamicslowmode import addDynamicslowmode, removeDynamicslowmode
from commands.channel.farewell import removeFarewellChannel, setFarewellChannel
from commands.channel.media import addMediaChannel, removeMediaChannel
from commands.channel.welcome import removeWelcomeChannel, setWelcomeChannel
from tests.helpers.discord import make_permissions, make_text_channel

pytestmark = pytest.mark.asyncio


async def test_set_welcome_missing_permission(restricted_command_info):
    channel = make_text_channel(guild=restricted_command_info.guild)
    await setWelcomeChannel(restricted_command_info, channel)
    restricted_command_info.reply.assert_awaited_once()


async def test_set_welcome_missing_bot_permission(admin_command_info):
    channel = make_text_channel(guild=admin_command_info.guild)
    channel.permissions_for = MagicMock(return_value=make_permissions(send_messages=False))
    await setWelcomeChannel(admin_command_info, channel)
    admin_command_info.reply.assert_awaited_once()


@patch("commands.channel.welcome.get_welcome_channel", new_callable=AsyncMock, return_value=True)
async def test_set_welcome_already_set(mock_get, admin_command_info):
    channel = make_text_channel(guild=admin_command_info.guild)
    await setWelcomeChannel(admin_command_info, channel)
    admin_command_info.reply.assert_awaited_once()


@patch("commands.channel.welcome.set_welcome_channel", new_callable=AsyncMock)
@patch("commands.channel.welcome.get_welcome_channel", new_callable=AsyncMock, return_value=None)
async def test_set_welcome_success(mock_get, mock_set, admin_command_info):
    channel = make_text_channel(guild=admin_command_info.guild)
    await setWelcomeChannel(admin_command_info, channel, message="hello")
    mock_set.assert_awaited_once()
    admin_command_info.reply.assert_awaited_once()


@patch("commands.channel.welcome.remove_welcome_channel", new_callable=AsyncMock)
@patch("commands.channel.welcome.get_welcome_channel", new_callable=AsyncMock, return_value=True)
async def test_remove_welcome_success(mock_get, mock_remove, admin_command_info):
    await removeWelcomeChannel(admin_command_info)
    mock_remove.assert_awaited_once()
    admin_command_info.reply.assert_awaited_once()


@patch("commands.channel.welcome.get_welcome_channel", new_callable=AsyncMock, return_value=None)
async def test_remove_welcome_not_set(mock_get, admin_command_info):
    await removeWelcomeChannel(admin_command_info)
    admin_command_info.reply.assert_awaited_once()


async def test_set_farewell_missing_permission(restricted_command_info):
    channel = make_text_channel(guild=restricted_command_info.guild)
    await setFarewellChannel(restricted_command_info, channel)
    restricted_command_info.reply.assert_awaited_once()


@patch("commands.channel.farewell.set_leave_channel", new_callable=AsyncMock)
@patch("commands.channel.farewell.get_leave_channel", new_callable=AsyncMock, return_value=None)
async def test_set_farewell_success(mock_get, mock_set, admin_command_info):
    channel = make_text_channel(guild=admin_command_info.guild)
    await setFarewellChannel(admin_command_info, channel, message="bye")
    mock_set.assert_awaited_once()


@patch("commands.channel.farewell.remove_leave_channel", new_callable=AsyncMock)
@patch("commands.channel.farewell.get_leave_channel", new_callable=AsyncMock, return_value=True)
async def test_remove_farewell_success(mock_get, mock_remove, admin_command_info):
    await removeFarewellChannel(admin_command_info)
    mock_remove.assert_awaited_once()


async def test_set_media_missing_permission(restricted_command_info):
    channel = make_text_channel(guild=restricted_command_info.guild)
    await addMediaChannel(restricted_command_info, channel)
    restricted_command_info.reply.assert_awaited_once()


@patch("commands.channel.media.add_media_channel", new_callable=AsyncMock)
@patch("commands.channel.media.get_media_channel", new_callable=AsyncMock, return_value=None)
async def test_set_media_success(mock_get, mock_set, admin_command_info):
    channel = make_text_channel(guild=admin_command_info.guild)
    await addMediaChannel(admin_command_info, channel)
    mock_set.assert_awaited_once()


@patch("commands.channel.media.remove_media_channel", new_callable=AsyncMock)
@patch("commands.channel.media.get_media_channel", new_callable=AsyncMock, return_value=True)
async def test_remove_media_success(mock_get, mock_remove, admin_command_info):
    channel = make_text_channel(guild=admin_command_info.guild)
    await removeMediaChannel(admin_command_info, channel)
    mock_remove.assert_awaited_once()


async def test_set_dynamic_slowmode_missing_permission(restricted_command_info):
    channel = make_text_channel(guild=restricted_command_info.guild)
    await addDynamicslowmode(restricted_command_info, channel, 10, 5)
    restricted_command_info.reply.assert_awaited_once()


@patch("commands.channel.dynamicslowmode._ds_service")
async def test_set_dynamic_slowmode_success(mock_service, admin_command_info):
    mock_service.get_config = AsyncMock(return_value=None)
    mock_service.configure = AsyncMock()
    channel = make_text_channel(guild=admin_command_info.guild)
    await addDynamicslowmode(admin_command_info, channel, 10, 5)
    mock_service.configure.assert_awaited_once()


@patch("commands.channel.dynamicslowmode._ds_service")
async def test_remove_dynamic_slowmode_success(mock_service, admin_command_info):
    mock_service.get_config = AsyncMock(return_value={"messages": 10})
    mock_service.remove = AsyncMock()
    channel = make_text_channel(guild=admin_command_info.guild)
    await removeDynamicslowmode(admin_command_info, channel)
    mock_service.remove.assert_awaited_once()
