from __future__ import annotations

from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from commands.giveaway import utility as gw_util
from models import GiveawayChannelRequirementModel


pytestmark = pytest.mark.asyncio


def _giveaway(**kwargs) -> MagicMock:
    gw = MagicMock()
    gw.title = "Prize"
    gw.description = kwargs.get("description", "Desc")
    gw.price = kwargs.get("price", None)
    gw.sponsor = kwargs.get("sponsor", None)
    gw.winners = 1
    gw.new_message_requirement = kwargs.get("new_message_requirement")
    gw.day_requirement = kwargs.get("day_requirement")
    gw.voice_requirement = kwargs.get("voice_requirement")
    gw.end_time = kwargs.get("end_time", datetime.now(timezone.utc))
    gw.guild_id = "123"
    gw.channel_id = "456"
    gw.message = "Giveaway!"
    gw.message_id = "789"
    return gw


async def test_generate_embed_minimal():
    embed = await gw_util.generateGiveawayEmbed(_giveaway(), "en_US", [], [])
    assert embed is not None


async def test_generate_embed_all_requirements():
    gw = _giveaway(
        description="D",
        price="5€",
        sponsor="111",
        new_message_requirement=10,
        day_requirement=7,
        voice_requirement=30,
        end_time="24h",
    )
    roles = ["999"]
    channels = [GiveawayChannelRequirementModel(channel_id="123456789012345678", amount=5)]
    embed = await gw_util.generateGiveawayEmbed(gw, "en_US", roles, channels)
    assert embed is not None


@patch("commands.giveaway.utility.giveaway_service.mark_sent", new_callable=AsyncMock)
@patch("commands.giveaway.utility.giveaway_service.get_participants", new_callable=AsyncMock, return_value=["1"])
@patch("commands.giveaway.utility.giveaway_service.get_channel_requirements", new_callable=AsyncMock, return_value=[])
@patch("commands.giveaway.utility.giveaway_service.get_role_requirements", new_callable=AsyncMock, return_value=[])
@patch("commands.giveaway.utility.giveaway_service.get", new_callable=AsyncMock)
async def test_send_giveaway(mock_get, mock_roles, mock_channels, mock_parts, mock_sent):
    gw = _giveaway()
    mock_get.return_value = gw
    guild = MagicMock(preferred_locale="en_US")
    channel = MagicMock()
    channel.send = AsyncMock(return_value=MagicMock(id=999))
    guild.get_channel = MagicMock(return_value=channel)
    client = MagicMock()
    client.get_guild = MagicMock(return_value=guild)
    await gw_util.sendGiveaway(1, client)
    channel.send.assert_awaited_once()
    mock_sent.assert_awaited_once()


@patch("commands.giveaway.utility.giveaway_service.get", new_callable=AsyncMock, return_value=None)
async def test_send_giveaway_missing(mock_get):
    await gw_util.sendGiveaway(1, MagicMock())


@patch("commands.giveaway.utility.giveaway_service.get", new_callable=AsyncMock)
async def test_send_giveaway_no_guild(mock_get):
    mock_get.return_value = _giveaway()
    client = MagicMock()
    client.get_guild = MagicMock(return_value=None)
    await gw_util.sendGiveaway(1, client)


@patch("commands.giveaway.utility.giveaway_service.get_channel_requirements", new_callable=AsyncMock, return_value=[])
@patch("commands.giveaway.utility.giveaway_service.get_role_requirements", new_callable=AsyncMock, return_value=[])
@patch("commands.giveaway.utility.giveaway_service.get", new_callable=AsyncMock)
async def test_update_embed(mock_get, mock_roles, mock_channels):
    gw = _giveaway()
    mock_get.return_value = gw
    guild = MagicMock(preferred_locale="en_US")
    channel = MagicMock()
    msg = MagicMock()
    msg.edit = AsyncMock()
    channel.fetch_message = AsyncMock(return_value=msg)
    guild.get_channel = MagicMock(return_value=channel)
    client = MagicMock()
    client.get_guild = MagicMock(return_value=guild)
    await gw_util.updateGiveawayEmbed(1, client)
    msg.edit.assert_awaited_once()


@patch("commands.giveaway.utility.giveaway_service.is_participant", new_callable=AsyncMock, return_value=True)
@patch("commands.giveaway.utility.giveaway_service.remove_participant", new_callable=AsyncMock)
@patch("commands.giveaway.utility.giveaway_service.get_participants", new_callable=AsyncMock, return_value=["1", "2"])
@patch("commands.giveaway.utility.giveaway_service.get", new_callable=AsyncMock)
async def test_add_participant_toggle_off(mock_get, mock_parts, mock_remove, mock_is):
    gw = _giveaway()
    mock_get.return_value = gw
    guild = MagicMock(preferred_locale="en_US")
    member = MagicMock()
    member.roles = []
    guild.get_member = MagicMock(return_value=member)
    channel = MagicMock()
    msg = MagicMock()
    msg.edit = AsyncMock()
    channel.fetch_message = AsyncMock(return_value=msg)
    guild.get_channel = MagicMock(return_value=channel)
    client = MagicMock()
    client.get_guild = MagicMock(return_value=guild)
    result = await gw_util.add_giveaway_participant(1, 1, client)
    assert result is not None
    mock_remove.assert_awaited_once()


@patch("commands.giveaway.utility.check_if_opted_out", new_callable=AsyncMock, return_value=True)
@patch("commands.giveaway.utility.giveaway_service.is_user_blacklisted", new_callable=AsyncMock, return_value=False)
@patch("commands.giveaway.utility.giveaway_service.is_participant", new_callable=AsyncMock, return_value=False)
@patch("commands.giveaway.utility.giveaway_service.get", new_callable=AsyncMock)
async def test_add_participant_opted_out(mock_get, mock_is, mock_bl, mock_opt):
    gw = _giveaway()
    mock_get.return_value = gw
    guild = MagicMock(preferred_locale="en_US")
    member = MagicMock()
    member.roles = []
    guild.get_member = MagicMock(return_value=member)
    client = MagicMock()
    client.get_guild = MagicMock(return_value=guild)
    result = await gw_util.add_giveaway_participant(1, 1, client)
    assert result is not None


@patch("commands.giveaway.utility.giveaway_service.is_participant", new_callable=AsyncMock, return_value=False)
@patch("commands.giveaway.utility.giveaway_service.is_user_blacklisted", new_callable=AsyncMock, return_value=True)
@patch("commands.giveaway.utility.giveaway_service.get", new_callable=AsyncMock)
async def test_add_participant_blacklisted(mock_get, mock_bl, mock_is):
    gw = _giveaway()
    mock_get.return_value = gw
    guild = MagicMock(preferred_locale="en_US")
    member = MagicMock()
    member.roles = []
    guild.get_member = MagicMock(return_value=member)
    client = MagicMock()
    client.get_guild = MagicMock(return_value=guild)
    result = await gw_util.add_giveaway_participant(1, 1, client)
    assert result is not None
