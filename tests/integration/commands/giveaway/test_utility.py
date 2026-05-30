from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from commands.giveaway.utility import (
    addMessageToGiveaway,
    add_giveaway_participant,
    endGiveaway,
    generateGiveawayEmbed,
    sendGiveaway,
    updateGiveawayEmbed,
    updateGiveawayMessage,
)
from models import GiveawayChannelRequirementModel, GiveawayModel
from tests.helpers.discord import make_guild, make_member, make_message, make_text_channel

pytestmark = pytest.mark.asyncio


GUILD_ID = "123456789012345678"
CHANNEL_ID = "444444444444444444"
USER_ID = "111111111111111111"
MESSAGE_ID = "888888888888888888"


def _make_giveaway(**overrides):
    defaults = {
        "giveaway_id": 1,
        "guild_id": GUILD_ID,
        "title": "Test Giveaway",
        "description": "A test",
        "winners": 1,
        "with_button": True,
        "price": "100 coins",
        "sponsor": USER_ID,
        "message": "Enter now!",
        "end_time": datetime.now() + timedelta(hours=1),
        "start_time": datetime.now() - timedelta(days=1),
        "started": True,
        "ended": False,
        "send_failed": False,
        "channel_id": CHANNEL_ID,
        "message_id": MESSAGE_ID,
        "created_at": datetime.now(),
        "new_message_requirement": 5,
        "day_requirement": 7,
        "voice_requirement": 30,
    }
    defaults.update(overrides)
    return GiveawayModel(**defaults)


async def test_generate_giveaway_embed_full():
    giveaway = _make_giveaway()
    role_reqs = ["555555555"]
    channel_reqs = [GiveawayChannelRequirementModel(channel_id=CHANNEL_ID, amount=3)]
    embed = await generateGiveawayEmbed(giveaway, "en-US", role_reqs, channel_reqs)
    assert embed is not None
    assert embed.title is not None


async def test_generate_giveaway_embed_no_requirements():
    giveaway = _make_giveaway(
        new_message_requirement=None,
        day_requirement=None,
        voice_requirement=None,
        price=None,
        sponsor=None,
        description=None,
        end_time=None,
    )
    embed = await generateGiveawayEmbed(giveaway, "en-US", [], [])
    assert embed is not None


@patch("commands.giveaway.utility.giveaway_service")
async def test_send_giveaway_no_giveaway(mock_svc):
    mock_svc.get = AsyncMock(return_value=None)
    client = MagicMock()
    await sendGiveaway(1, client)
    client.get_guild.assert_not_called()


@patch("commands.giveaway.utility.giveaway_service")
async def test_send_giveaway_no_guild(mock_svc):
    mock_svc.get = AsyncMock(return_value=_make_giveaway())
    client = MagicMock()
    client.get_guild = MagicMock(return_value=None)
    await sendGiveaway(1, client)
    client.get_guild.assert_called_once()


@patch("commands.giveaway.utility.giveaway_service")
async def test_send_giveaway_success(mock_svc):
    giveaway = _make_giveaway()
    mock_svc.get = AsyncMock(return_value=giveaway)
    mock_svc.get_role_requirements = AsyncMock(return_value=[])
    mock_svc.get_channel_requirements = AsyncMock(return_value=[])
    mock_svc.get_participants = AsyncMock(return_value=[])
    mock_svc.mark_sent = AsyncMock()
    guild = make_guild()
    channel = make_text_channel(guild=guild)
    guild.get_channel = MagicMock(return_value=channel)
    client = MagicMock()
    client.get_guild = MagicMock(return_value=guild)
    await sendGiveaway(1, client)
    channel.send.assert_awaited_once()
    mock_svc.mark_sent.assert_awaited_once()


@patch("commands.giveaway.utility.giveaway_service")
async def test_update_giveaway_embed_no_giveaway(mock_svc):
    mock_svc.get = AsyncMock(return_value=None)
    await updateGiveawayEmbed(1, MagicMock())


@patch("commands.giveaway.utility.giveaway_service")
async def test_update_giveaway_embed_success(mock_svc):
    giveaway = _make_giveaway()
    mock_svc.get = AsyncMock(return_value=giveaway)
    mock_svc.get_role_requirements = AsyncMock(return_value=[])
    mock_svc.get_channel_requirements = AsyncMock(return_value=[])
    guild = make_guild()
    channel = make_text_channel(guild=guild)
    message = MagicMock()
    message.edit = AsyncMock()
    channel.fetch_message = AsyncMock(return_value=message)
    guild.get_channel = MagicMock(return_value=channel)
    client = MagicMock()
    client.get_guild = MagicMock(return_value=guild)
    await updateGiveawayEmbed(1, client)
    message.edit.assert_awaited_once()


@patch("commands.giveaway.utility.giveaway_service")
@patch("commands.giveaway.utility.check_if_opted_out", new_callable=AsyncMock)
async def test_add_giveaway_participant_blacklisted(mock_opt, mock_svc):
    mock_opt.return_value = False
    mock_svc.get = AsyncMock(return_value=_make_giveaway())
    mock_svc.is_participant = AsyncMock(return_value=False)
    mock_svc.is_user_blacklisted = AsyncMock(return_value=True)
    guild = make_guild()
    member = make_member()
    guild.get_member = MagicMock(return_value=member)
    client = MagicMock()
    client.get_guild = MagicMock(return_value=guild)
    result = await add_giveaway_participant(1, member.id, client)
    assert result is not None


@patch("commands.giveaway.utility.giveaway_service")
@patch("commands.giveaway.utility.check_if_opted_out", new_callable=AsyncMock)
async def test_add_giveaway_participant_opted_out(mock_opt, mock_svc):
    mock_opt.return_value = True
    mock_svc.get = AsyncMock(return_value=_make_giveaway())
    mock_svc.is_participant = AsyncMock(return_value=False)
    mock_svc.is_user_blacklisted = AsyncMock(return_value=False)
    mock_svc.is_participant = AsyncMock(return_value=False)
    guild = make_guild()
    member = make_member()
    guild.get_member = MagicMock(return_value=member)
    client = MagicMock()
    client.get_guild = MagicMock(return_value=guild)
    result = await add_giveaway_participant(1, member.id, client)
    assert result is not None


@patch("commands.giveaway.utility.giveaway_service")
async def test_add_giveaway_participant_remove_existing(mock_svc):
    giveaway = _make_giveaway(
        new_message_requirement=None,
        day_requirement=None,
        voice_requirement=None,
    )
    mock_svc.get = AsyncMock(return_value=giveaway)
    mock_svc.is_participant = AsyncMock(return_value=True)
    mock_svc.remove_participant = AsyncMock()
    mock_svc.get_participants = AsyncMock(return_value=[111111111])
    guild = make_guild()
    channel = make_text_channel(guild=guild)
    message = MagicMock()
    message.edit = AsyncMock()
    channel.fetch_message = AsyncMock(return_value=message)
    guild.get_channel = MagicMock(return_value=channel)
    guild.get_member = MagicMock(return_value=make_member())
    client = MagicMock()
    client.get_guild = MagicMock(return_value=guild)
    result = await add_giveaway_participant(1, 111111111, client)
    mock_svc.remove_participant.assert_awaited_once()
    assert result is not None


@patch("commands.giveaway.utility.giveaway_service")
@patch("commands.giveaway.utility.check_if_opted_out", new_callable=AsyncMock)
async def test_add_giveaway_participant_success(mock_opt, mock_svc):
    mock_opt.return_value = False
    giveaway = _make_giveaway(
        new_message_requirement=None,
        day_requirement=None,
        voice_requirement=None,
    )
    mock_svc.get = AsyncMock(return_value=giveaway)
    mock_svc.is_participant = AsyncMock(return_value=False)
    mock_svc.is_user_blacklisted = AsyncMock(return_value=False)
    mock_svc.get_blacklisted_roles = AsyncMock(return_value=[])
    mock_svc.get_role_requirements = AsyncMock(return_value=[])
    mock_svc.get_channel_requirements = AsyncMock(return_value=[])
    mock_svc.add_participant = AsyncMock()
    mock_svc.get_participants = AsyncMock(return_value=[111111111])
    guild = make_guild()
    channel = make_text_channel(guild=guild)
    message = MagicMock()
    message.edit = AsyncMock()
    channel.fetch_message = AsyncMock(return_value=message)
    guild.get_channel = MagicMock(return_value=channel)
    member = make_member()
    guild.get_member = MagicMock(return_value=member)
    client = MagicMock()
    client.get_guild = MagicMock(return_value=guild)
    result = await add_giveaway_participant(1, member.id, client)
    mock_svc.add_participant.assert_awaited_once()
    assert result is not None


@patch("commands.giveaway.utility.giveaway_service")
@patch("commands.giveaway.utility.check_if_opted_out", new_callable=AsyncMock)
async def test_add_message_to_giveaway(mock_opt, mock_svc):
    mock_opt.return_value = False
    mock_svc.add_new_message = AsyncMock()
    mock_svc.add_new_message_channel = AsyncMock()
    message = make_message()
    await addMessageToGiveaway(message)
    mock_svc.add_new_message.assert_awaited_once()


@patch("commands.giveaway.utility.giveaway_service")
async def test_end_giveaway_no_participants(mock_svc):
    giveaway = _make_giveaway()
    mock_svc.get = AsyncMock(return_value=giveaway)
    mock_svc.get_participants = AsyncMock(return_value=[])
    mock_svc.set_ended = AsyncMock()
    guild = make_guild()
    channel = make_text_channel(guild=guild)
    message = MagicMock()
    message.edit = AsyncMock()
    message.reply = AsyncMock()
    channel.fetch_message = AsyncMock(return_value=message)
    guild.get_channel = MagicMock(return_value=channel)
    client = MagicMock()
    client.get_guild = MagicMock(return_value=guild)
    await endGiveaway(1, client)
    mock_svc.set_ended.assert_awaited_once()


@patch("commands.giveaway.utility.giveaway_service")
async def test_end_giveaway_with_winners(mock_svc):
    giveaway = _make_giveaway(winners=1)
    mock_svc.get = AsyncMock(return_value=giveaway)
    mock_svc.get_participants = AsyncMock(return_value=[111111111, 222222222])
    mock_svc.remove_participant = AsyncMock()
    mock_svc.set_ended = AsyncMock()
    guild = make_guild()
    channel = make_text_channel(guild=guild)
    message = MagicMock()
    message.edit = AsyncMock()
    message.reply = AsyncMock()
    channel.fetch_message = AsyncMock(return_value=message)
    guild.get_channel = MagicMock(return_value=channel)
    winner = make_member(user_id=111111111)
    guild.get_member = MagicMock(return_value=winner)
    client = MagicMock()
    client.get_guild = MagicMock(return_value=guild)
    await endGiveaway(1, client)
    mock_svc.set_ended.assert_awaited_once()


@patch("commands.giveaway.utility.giveaway_service")
async def test_end_giveaway_already_ended(mock_svc):
    mock_svc.get = AsyncMock(return_value=_make_giveaway(ended=True))
    client = MagicMock()
    await endGiveaway(1, client)
    client.get_guild.assert_not_called()


@patch("commands.giveaway.utility.giveaway_service")
async def test_update_giveaway_message_not_found(mock_svc):
    import discord

    giveaway = _make_giveaway()
    mock_svc.get = AsyncMock(return_value=giveaway)
    mock_svc.get_role_requirements = AsyncMock(return_value=[])
    mock_svc.get_channel_requirements = AsyncMock(return_value=[])
    guild = make_guild()
    channel = make_text_channel(guild=guild)
    channel.fetch_message = AsyncMock(side_effect=discord.errors.NotFound(MagicMock(), "not found"))
    guild.get_channel = MagicMock(return_value=channel)
    client = MagicMock()
    client.get_guild = MagicMock(return_value=guild)
    await updateGiveawayMessage(1, client)
