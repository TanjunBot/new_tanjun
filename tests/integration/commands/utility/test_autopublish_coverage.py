from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from commands.utility.autopublish import autopublish, autopublish_remove, publish_message
from tests.helpers.discord import make_message, make_text_channel

pytestmark = pytest.mark.asyncio


async def test_autopublish_no_guild(restricted_command_info):
    restricted_command_info.guild = None
    await autopublish(restricted_command_info, make_text_channel())
    restricted_command_info.reply.assert_awaited_once()


async def test_autopublish_no_channel(admin_command_info):
    admin_command_info.channel = None
    await autopublish(admin_command_info, make_text_channel())
    admin_command_info.reply.assert_awaited_once()


async def test_autopublish_no_permission(restricted_command_info):
    await autopublish(restricted_command_info, restricted_command_info.channel)
    restricted_command_info.reply.assert_awaited_once()


@patch("commands.utility.autopublish.checkIfChannelIsAutopublish", new_callable=AsyncMock, return_value=True)
@patch("commands.utility.autopublish.removeAutoPublish", new_callable=AsyncMock)
async def test_autopublish_already_enabled(mock_remove, mock_check, admin_command_info):
    await autopublish(admin_command_info, admin_command_info.channel)
    mock_remove.assert_awaited_once()
    admin_command_info.reply.assert_awaited_once()


@patch("commands.utility.autopublish.checkIfChannelIsAutopublish", new_callable=AsyncMock, return_value=False)
async def test_autopublish_not_news(mock_check, admin_command_info):
    admin_command_info.channel.is_news = MagicMock(return_value=False)
    await autopublish(admin_command_info, admin_command_info.channel)
    admin_command_info.reply.assert_awaited_once()


@patch("commands.utility.autopublish.checkIfChannelIsAutopublish", new_callable=AsyncMock, return_value=False)
@patch("commands.utility.autopublish.addAutoPublish", new_callable=AsyncMock)
async def test_autopublish_success(mock_add, mock_check, admin_command_info):
    admin_command_info.channel.is_news = MagicMock(return_value=True)
    await autopublish(admin_command_info, admin_command_info.channel)
    mock_add.assert_awaited_once()
    admin_command_info.reply.assert_awaited_once()


async def test_autopublish_remove_no_guild(restricted_command_info):
    restricted_command_info.guild = None
    await autopublish_remove(restricted_command_info, make_text_channel())
    restricted_command_info.reply.assert_awaited_once()


async def test_autopublish_remove_no_channel(admin_command_info):
    admin_command_info.channel = None
    await autopublish_remove(admin_command_info, make_text_channel())
    admin_command_info.reply.assert_awaited_once()


async def test_autopublish_remove_no_permission(restricted_command_info):
    await autopublish_remove(restricted_command_info, restricted_command_info.channel)
    restricted_command_info.reply.assert_awaited_once()


@patch("commands.utility.autopublish.checkIfChannelIsAutopublish", new_callable=AsyncMock, return_value=False)
async def test_autopublish_remove_not_enabled(mock_check, admin_command_info):
    await autopublish_remove(admin_command_info, admin_command_info.channel)
    admin_command_info.reply.assert_awaited_once()


@patch("commands.utility.autopublish.checkIfChannelIsAutopublish", new_callable=AsyncMock, return_value=True)
@patch("commands.utility.autopublish.removeAutoPublish", new_callable=AsyncMock)
async def test_autopublish_remove_success(mock_remove, mock_check, admin_command_info):
    await autopublish_remove(admin_command_info, admin_command_info.channel)
    mock_remove.assert_awaited_once()
    admin_command_info.reply.assert_awaited_once()


@patch("commands.utility.autopublish.checkIfChannelIsAutopublish", new_callable=AsyncMock, return_value=True)
async def test_publish_message_news_channel(mock_check):
    message = make_message()
    message.channel.is_news = MagicMock(return_value=True)
    message.publish = AsyncMock()
    await publish_message(message)
    message.publish.assert_awaited_once()


async def test_publish_message_non_news():
    message = make_message()
    message.channel.is_news = MagicMock(return_value=False)
    await publish_message(message)
