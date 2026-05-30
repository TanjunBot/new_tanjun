from __future__ import annotations

from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from commands.giveaway import utility as gw_util

pytestmark = pytest.mark.asyncio


def _giveaway(**kwargs) -> MagicMock:
    gw = MagicMock()
    gw.guild_id = "123"
    gw.channel_id = "456"
    gw.message_id = "789"
    gw.message = "Giveaway!"
    gw.title = "Prize"
    gw.description = "Desc"
    gw.ended = kwargs.get("ended", False)
    gw.winners = kwargs.get("winners", 1)
    gw.start_time = datetime.now(UTC)
    return gw


def _client_with_guild(guild=None):
    if guild is None:
        guild = MagicMock(preferred_locale="en_US", name="Test Guild")
    client = MagicMock()
    client.get_guild = MagicMock(return_value=guild)
    return client, guild


@patch("commands.giveaway.utility.giveaway_service.set_ended", new_callable=AsyncMock)
@patch("commands.giveaway.utility.giveaway_service.get_participants", new_callable=AsyncMock, return_value=[])
@patch("commands.giveaway.utility.giveaway_service.get", new_callable=AsyncMock)
async def test_end_giveaway_no_participants(mock_get, mock_parts, mock_ended):
    gw = _giveaway()
    mock_get.return_value = gw
    client, guild = _client_with_guild()
    channel = MagicMock()
    msg = MagicMock()
    msg.edit = AsyncMock()
    msg.reply = AsyncMock()
    channel.fetch_message = AsyncMock(return_value=msg)
    guild.get_channel = MagicMock(return_value=channel)
    await gw_util.endGiveaway(1, client)
    mock_ended.assert_awaited_once()
    msg.reply.assert_awaited_once()


@patch("commands.giveaway.utility.giveaway_service.set_ended", new_callable=AsyncMock)
@patch("commands.giveaway.utility.giveaway_service.remove_participant", new_callable=AsyncMock)
@patch("commands.giveaway.utility.giveaway_service.get_participants", new_callable=AsyncMock, return_value=[111, 222])
@patch("commands.giveaway.utility.giveaway_service.get", new_callable=AsyncMock)
async def test_end_giveaway_with_winners(mock_get, mock_parts, mock_remove, mock_ended):
    gw = _giveaway(winners=1)
    mock_get.return_value = gw
    client, guild = _client_with_guild()
    winner = MagicMock()
    winner.send = AsyncMock()
    guild.get_member = MagicMock(return_value=winner)
    channel = MagicMock()
    msg = MagicMock()
    msg.edit = AsyncMock()
    msg.reply = AsyncMock()
    channel.fetch_message = AsyncMock(return_value=msg)
    guild.get_channel = MagicMock(return_value=channel)
    await gw_util.endGiveaway(1, client)
    mock_ended.assert_awaited_once()
    msg.reply.assert_awaited_once()


@patch("commands.giveaway.utility.giveaway_service.get", new_callable=AsyncMock, return_value=None)
async def test_end_giveaway_missing(mock_get):
    await gw_util.endGiveaway(1, MagicMock())


@patch("commands.giveaway.utility.giveaway_service.get", new_callable=AsyncMock)
async def test_end_giveaway_already_ended(mock_get):
    mock_get.return_value = _giveaway(ended=True)
    await gw_util.endGiveaway(1, MagicMock())


@patch("commands.giveaway.utility.check_if_opted_out", new_callable=AsyncMock, return_value=True)
async def test_add_message_opted_out(mock_opt):
    msg = MagicMock()
    msg.author.id = 1
    await gw_util.addMessageToGiveaway(msg)


@patch("commands.giveaway.utility.giveaway_service.add_new_message_channel", new_callable=AsyncMock)
@patch("commands.giveaway.utility.giveaway_service.add_new_message", new_callable=AsyncMock)
@patch("commands.giveaway.utility.check_if_opted_out", new_callable=AsyncMock, return_value=False)
async def test_add_message_success(mock_opt, mock_add, mock_add_ch):
    msg = MagicMock()
    msg.author.id = 1
    msg.guild.id = 123
    msg.channel.id = 456
    await gw_util.addMessageToGiveaway(msg)
    mock_add.assert_awaited_once()
    mock_add_ch.assert_awaited_once()


@patch("commands.giveaway.utility.giveaway_service.get_channel_requirements", new_callable=AsyncMock, return_value=[])
@patch("commands.giveaway.utility.giveaway_service.get_role_requirements", new_callable=AsyncMock, return_value=[])
@patch("commands.giveaway.utility.giveaway_service.get", new_callable=AsyncMock)
async def test_update_giveaway_message(mock_get, mock_roles, mock_channels):
    gw = _giveaway()
    mock_get.return_value = gw
    client, guild = _client_with_guild()
    channel = MagicMock()
    msg = MagicMock()
    msg.edit = AsyncMock()
    channel.fetch_message = AsyncMock(return_value=msg)
    guild.get_channel = MagicMock(return_value=channel)
    await gw_util.updateGiveawayMessage(1, client)
    msg.edit.assert_awaited_once()
