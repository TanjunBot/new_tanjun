"""Integration tests for commands.logs.remove_log_channel."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from commands.logs.remove_log_channel import remove_log_channel as command_fn
from tests.helpers.discord import make_command_info, make_guild, make_permissions, make_text_channel
from tests.integration.commands.conftest import embed_from_reply


@pytest.mark.asyncio
@patch("commands.logs.remove_log_channel.get_log_channel_api", new_callable=AsyncMock)
async def test_not_set(mock_get):
    mock_get.return_value = None
    guild = make_guild()
    channel = make_text_channel(guild=guild)
    channel.permissions_for = MagicMock(return_value=make_permissions(administrator=True))
    info = make_command_info(guild=guild, channel=channel)
    await command_fn(info)
    embed_from_reply(info.reply)


@pytest.mark.asyncio
@patch("commands.logs.remove_log_channel.remove_log_channel_api", new_callable=AsyncMock)
@patch("commands.logs.remove_log_channel.get_log_channel_api", new_callable=AsyncMock)
async def test_success(mock_get, mock_remove):
    mock_get.return_value = 444
    guild = make_guild()
    channel = make_text_channel(guild=guild)
    channel.permissions_for = MagicMock(return_value=make_permissions(administrator=True))
    info = make_command_info(guild=guild, channel=channel)
    await command_fn(info)
    embed_from_reply(info.reply)
