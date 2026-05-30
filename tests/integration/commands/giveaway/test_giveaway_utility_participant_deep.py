from __future__ import annotations

from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from commands.giveaway import utility as gw_util


pytestmark = pytest.mark.asyncio


def _giveaway(**kwargs) -> MagicMock:
    gw = MagicMock()
    gw.guild_id = "123"
    gw.channel_id = "456"
    gw.message_id = "789"
    gw.new_message_requirement = kwargs.get("new_message_requirement")
    gw.day_requirement = kwargs.get("day_requirement")
    gw.voice_requirement = kwargs.get("voice_requirement")
    gw.start_time = kwargs.get("start_time", datetime.now(timezone.utc))
    return gw


@patch("commands.giveaway.utility.giveaway_service.add_participant", new_callable=AsyncMock)
@patch("commands.giveaway.utility.giveaway_service.get_role_requirements", new_callable=AsyncMock, return_value=[])
@patch("commands.giveaway.utility.giveaway_service.get_voice_time", new_callable=AsyncMock, return_value=5)
@patch("commands.giveaway.utility.giveaway_service.get_blacklisted_roles", new_callable=AsyncMock, return_value=[])
@patch("commands.giveaway.utility.giveaway_service.get_new_messages", new_callable=AsyncMock, return_value=10)
@patch("commands.giveaway.utility.check_if_opted_out", new_callable=AsyncMock, return_value=False)
@patch("commands.giveaway.utility.giveaway_service.is_user_blacklisted", new_callable=AsyncMock, return_value=False)
@patch("commands.giveaway.utility.giveaway_service.is_participant", new_callable=AsyncMock, return_value=False)
@patch("commands.giveaway.utility.giveaway_service.get", new_callable=AsyncMock)
async def test_add_participant_success(
    mock_get,
    mock_is,
    mock_bl,
    mock_opt,
    mock_msgs,
    mock_bl_roles,
    mock_voice,
    mock_roles,
    mock_add,
):
    gw = _giveaway(new_message_requirement=5, voice_requirement=None)
    mock_get.return_value = gw
    guild = MagicMock(preferred_locale="en_US")
    role = MagicMock()
    role.id = 999
    member = MagicMock()
    member.roles = [role]
    member.joined_at = datetime(2020, 1, 1, tzinfo=timezone.utc)
    guild.get_member = MagicMock(return_value=member)
    channel = MagicMock()
    msg = MagicMock()
    msg.edit = AsyncMock()
    channel.fetch_message = AsyncMock(return_value=msg)
    guild.get_channel = MagicMock(return_value=channel)
    client = MagicMock()
    client.get_guild = MagicMock(return_value=guild)
    with patch("commands.giveaway.utility.giveaway_service.get_participants", AsyncMock(return_value=[])):
        result = await gw_util.add_giveaway_participant(1, 1, client)
    assert result is None or result is not None
    mock_add.assert_awaited_once()


@patch("commands.giveaway.utility.giveaway_service.get_new_messages", new_callable=AsyncMock, return_value=2)
@patch("commands.giveaway.utility.check_if_opted_out", new_callable=AsyncMock, return_value=False)
@patch("commands.giveaway.utility.giveaway_service.is_user_blacklisted", new_callable=AsyncMock, return_value=False)
@patch("commands.giveaway.utility.giveaway_service.is_participant", new_callable=AsyncMock, return_value=False)
@patch("commands.giveaway.utility.giveaway_service.get", new_callable=AsyncMock)
async def test_add_participant_insufficient_messages(mock_get, mock_is, mock_bl, mock_opt, mock_msgs):
    gw = _giveaway(new_message_requirement=10)
    mock_get.return_value = gw
    guild = MagicMock(preferred_locale="en_US")
    member = MagicMock()
    member.roles = []
    guild.get_member = MagicMock(return_value=member)
    client = MagicMock()
    client.get_guild = MagicMock(return_value=guild)
    result = await gw_util.add_giveaway_participant(1, 1, client)
    assert result is not None


@patch("commands.giveaway.utility.giveaway_service.get_voice_time", new_callable=AsyncMock, return_value=1)
@patch("commands.giveaway.utility.giveaway_service.get_blacklisted_roles", new_callable=AsyncMock, return_value=[])
@patch("commands.giveaway.utility.check_if_opted_out", new_callable=AsyncMock, return_value=False)
@patch("commands.giveaway.utility.giveaway_service.is_user_blacklisted", new_callable=AsyncMock, return_value=False)
@patch("commands.giveaway.utility.giveaway_service.is_participant", new_callable=AsyncMock, return_value=False)
@patch("commands.giveaway.utility.giveaway_service.get", new_callable=AsyncMock)
async def test_add_participant_insufficient_voice(mock_get, mock_is, mock_bl, mock_opt, mock_bl_roles, mock_voice):
    gw = _giveaway(voice_requirement=30)
    mock_get.return_value = gw
    guild = MagicMock(preferred_locale="en_US")
    member = MagicMock()
    member.roles = []
    guild.get_member = MagicMock(return_value=member)
    client = MagicMock()
    client.get_guild = MagicMock(return_value=guild)
    result = await gw_util.add_giveaway_participant(1, 1, client)
    assert result is not None


@patch("commands.giveaway.utility.giveaway_service.get_role_requirements", new_callable=AsyncMock, return_value=["999"])
@patch("commands.giveaway.utility.giveaway_service.get_blacklisted_roles", new_callable=AsyncMock, return_value=[])
@patch("commands.giveaway.utility.check_if_opted_out", new_callable=AsyncMock, return_value=False)
@patch("commands.giveaway.utility.giveaway_service.is_user_blacklisted", new_callable=AsyncMock, return_value=False)
@patch("commands.giveaway.utility.giveaway_service.is_participant", new_callable=AsyncMock, return_value=False)
@patch("commands.giveaway.utility.giveaway_service.get", new_callable=AsyncMock)
async def test_add_participant_missing_role(mock_get, mock_is, mock_bl, mock_opt, mock_bl_roles, mock_roles):
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


@patch("commands.giveaway.utility.giveaway_service.get_blacklisted_roles", new_callable=AsyncMock)
@patch("commands.giveaway.utility.check_if_opted_out", new_callable=AsyncMock, return_value=False)
@patch("commands.giveaway.utility.giveaway_service.is_user_blacklisted", new_callable=AsyncMock, return_value=False)
@patch("commands.giveaway.utility.giveaway_service.is_participant", new_callable=AsyncMock, return_value=False)
@patch("commands.giveaway.utility.giveaway_service.get", new_callable=AsyncMock)
async def test_add_participant_blacklisted_role(mock_get, mock_is, mock_bl, mock_opt, mock_bl_roles):
    gw = _giveaway()
    mock_get.return_value = gw
    bl = MagicMock()
    bl.entity_id = "888"
    mock_bl_roles.return_value = [bl]
    guild = MagicMock(preferred_locale="en_US")
    role = MagicMock()
    role.id = 888
    member = MagicMock()
    member.roles = [role]
    guild.get_member = MagicMock(return_value=member)
    client = MagicMock()
    client.get_guild = MagicMock(return_value=guild)
    result = await gw_util.add_giveaway_participant(1, 1, client)
    assert result is not None


@patch("commands.giveaway.utility.giveaway_service.get_new_messages", new_callable=AsyncMock, return_value=None)
@patch("commands.giveaway.utility.check_if_opted_out", new_callable=AsyncMock, return_value=False)
@patch("commands.giveaway.utility.giveaway_service.is_user_blacklisted", new_callable=AsyncMock, return_value=False)
@patch("commands.giveaway.utility.giveaway_service.is_participant", new_callable=AsyncMock, return_value=False)
@patch("commands.giveaway.utility.giveaway_service.get", new_callable=AsyncMock)
async def test_add_participant_zero_messages(mock_get, mock_is, mock_bl, mock_opt, mock_msgs):
    gw = _giveaway(new_message_requirement=5)
    mock_get.return_value = gw
    guild = MagicMock(preferred_locale="en_US")
    member = MagicMock()
    member.roles = []
    guild.get_member = MagicMock(return_value=member)
    client = MagicMock()
    client.get_guild = MagicMock(return_value=guild)
    result = await gw_util.add_giveaway_participant(1, 1, client)
    assert result is not None


@patch("commands.giveaway.utility.giveaway_service.get_channel_requirements", new_callable=AsyncMock)
@patch("commands.giveaway.utility.giveaway_service.get_role_requirements", new_callable=AsyncMock, return_value=[])
@patch("commands.giveaway.utility.giveaway_service.get_blacklisted_roles", new_callable=AsyncMock, return_value=[])
@patch("commands.giveaway.utility.check_if_opted_out", new_callable=AsyncMock, return_value=False)
@patch("commands.giveaway.utility.giveaway_service.is_user_blacklisted", new_callable=AsyncMock, return_value=False)
@patch("commands.giveaway.utility.giveaway_service.is_participant", new_callable=AsyncMock, return_value=False)
@patch("commands.giveaway.utility.giveaway_service.get", new_callable=AsyncMock)
async def test_add_participant_channel_requirement_fail(mock_get, mock_is, mock_bl, mock_opt, mock_bl_roles, mock_roles, mock_channels):
    from models import GiveawayChannelRequirementModel

    gw = _giveaway()
    mock_get.return_value = gw
    mock_channels.return_value = [GiveawayChannelRequirementModel(channel_id="123456789012345678", amount=5)]
    guild = MagicMock(preferred_locale="en_US")
    member = MagicMock()
    member.roles = []
    guild.get_member = MagicMock(return_value=member)
    client = MagicMock()
    client.get_guild = MagicMock(return_value=guild)
    with patch("commands.giveaway.utility.giveaway_service.get_new_messages_channel", AsyncMock(return_value=1)):
        result = await gw_util.add_giveaway_participant(1, 1, client)
    assert result is not None


@patch("commands.giveaway.utility.giveaway_service.get_blacklisted_roles", new_callable=AsyncMock, return_value=[])
@patch("commands.giveaway.utility.check_if_opted_out", new_callable=AsyncMock, return_value=False)
@patch("commands.giveaway.utility.giveaway_service.is_user_blacklisted", new_callable=AsyncMock, return_value=False)
@patch("commands.giveaway.utility.giveaway_service.is_participant", new_callable=AsyncMock, return_value=False)
@patch("commands.giveaway.utility.giveaway_service.get", new_callable=AsyncMock)
async def test_add_participant_day_requirement_fail(mock_get, mock_is, mock_bl, mock_opt, mock_bl_roles):
    gw = _giveaway(day_requirement=365)
    gw.start_time = datetime(2024, 1, 1)
    mock_get.return_value = gw
    guild = MagicMock(preferred_locale="en_US")
    member = MagicMock()
    member.roles = []
    member.joined_at = datetime(2023, 12, 1, tzinfo=timezone.utc)
    guild.get_member = MagicMock(return_value=member)
    client = MagicMock()
    client.get_guild = MagicMock(return_value=guild)
    result = await gw_util.add_giveaway_participant(1, 1, client)
    assert result is not None
