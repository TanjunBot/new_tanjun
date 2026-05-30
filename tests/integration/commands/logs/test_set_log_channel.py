"""Integration tests for commands.logs.set_log_channel."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from commands.logs.set_log_channel import set_log_channel as command_fn
from tests.helpers.discord import make_command_info, make_guild, make_permissions, make_text_channel
from tests.integration.commands.conftest import embed_from_reply


def _info(admin: bool):
    guild = make_guild()
    channel = make_text_channel(guild=guild)
    channel.permissions_for = MagicMock(return_value=make_permissions(administrator=admin))
    client = MagicMock()
    client.user = MagicMock(id=guild.me.id)
    guild.get_member = MagicMock(side_effect=lambda uid: guild.me if uid == guild.me.id else None)
    return make_command_info(guild=guild, channel=channel, client=client)


@pytest.mark.asyncio
async def test_missing_permission():
    info = _info(False)
    await command_fn(info, make_text_channel())
    embed_from_reply(info.reply)


@pytest.mark.asyncio
@patch("commands.logs.set_log_channel.get_log_channel_api", new_callable=AsyncMock)
async def test_already_set(mock_get):
    mock_get.return_value = 1
    info = _info(True)
    ch = make_text_channel(guild=info.guild)
    ch.permissions_for = MagicMock(return_value=make_permissions(send_messages=True))
    await command_fn(info, ch)
    embed_from_reply(info.reply)


@pytest.mark.asyncio
@patch("commands.logs.set_log_channel.set_log_channel_api", new_callable=AsyncMock)
@patch("commands.logs.set_log_channel.get_log_channel_api", new_callable=AsyncMock)
async def test_success(mock_get, mock_set):
    mock_get.return_value = None
    info = _info(True)
    ch = make_text_channel(guild=info.guild)
    ch.permissions_for = MagicMock(return_value=make_permissions(send_messages=True))
    await command_fn(info, ch)
    embed_from_reply(info.reply)
    mock_set.assert_awaited_once()
