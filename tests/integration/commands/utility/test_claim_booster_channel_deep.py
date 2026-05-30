from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from commands.utility.claim_booster_channel import claimBoosterChannel, remove_claimed_booster_channels_that_are_expired
from services.booster_service import BoosterType, ClaimedBoosterType


pytestmark = pytest.mark.asyncio


def _entry(user_id=1, guild_id=123, channel_id=456) -> MagicMock:
    e = MagicMock()
    e.user_id = user_id
    e.guild_id = guild_id
    e.channel_id = channel_id
    return e


@patch("commands.utility.claim_booster_channel.booster_service.get", new_callable=AsyncMock, return_value=None)
async def test_claim_no_booster_configured(mock_get, admin_command_info):
    await claimBoosterChannel(admin_command_info, "My Channel")
    admin_command_info.reply.assert_awaited_once()


@patch("commands.utility.claim_booster_channel.booster_service.get", new_callable=AsyncMock, return_value="999")
async def test_claim_not_booster(mock_get, admin_command_info):
    admin_command_info.user.premium_since = None
    await claimBoosterChannel(admin_command_info, "My Channel")
    admin_command_info.reply.assert_awaited_once()


@patch("commands.utility.claim_booster_channel.booster_service.get_claim_for_user", new_callable=AsyncMock, return_value="existing")
@patch("commands.utility.claim_booster_channel.booster_service.get", new_callable=AsyncMock, return_value="999")
async def test_claim_already_claimed(mock_get, mock_claim, admin_command_info):
    admin_command_info.user.premium_since = MagicMock()
    await claimBoosterChannel(admin_command_info, "My Channel")
    admin_command_info.reply.assert_awaited_once()


@patch("commands.utility.claim_booster_channel.booster_service.get_claim_for_user", new_callable=AsyncMock, return_value=None)
@patch("commands.utility.claim_booster_channel.booster_service.get", new_callable=AsyncMock, return_value="999")
async def test_claim_category_not_found(mock_get, mock_claim, admin_command_info):
    admin_command_info.user.premium_since = MagicMock()
    admin_command_info.guild.get_channel = MagicMock(return_value=None)
    await claimBoosterChannel(admin_command_info, "My Channel")
    admin_command_info.reply.assert_awaited_once()


@patch("commands.utility.claim_booster_channel.booster_service.claim", new_callable=AsyncMock)
@patch("commands.utility.claim_booster_channel.booster_service.get_claim_for_user", new_callable=AsyncMock, return_value=None)
@patch("commands.utility.claim_booster_channel.booster_service.get", new_callable=AsyncMock, return_value="999")
async def test_claim_success(mock_get, mock_user_claim, mock_claim, admin_command_info):
    admin_command_info.user.premium_since = MagicMock()
    category = MagicMock()
    admin_command_info.guild.get_channel = MagicMock(return_value=category)
    new_channel = MagicMock(id=777)
    admin_command_info.guild.create_voice_channel = AsyncMock(return_value=new_channel)
    await claimBoosterChannel(admin_command_info, "Boost VC")
    mock_claim.assert_awaited_once()
    admin_command_info.reply.assert_awaited_once()


@patch("commands.utility.claim_booster_channel.booster_service.unclaim", new_callable=AsyncMock)
@patch("commands.utility.claim_booster_channel.booster_service.get_all_claims", new_callable=AsyncMock, return_value=[])
async def test_remove_expired_empty(mock_claims, mock_unclaim):
    client = MagicMock()
    await remove_claimed_booster_channels_that_are_expired(client)
    mock_unclaim.assert_not_awaited()


@patch("commands.utility.claim_booster_channel.booster_service.unclaim", new_callable=AsyncMock)
@patch("commands.utility.claim_booster_channel.booster_service.get_all_claims", new_callable=AsyncMock)
async def test_remove_expired_guild_gone(mock_claims, mock_unclaim):
    mock_claims.return_value = [_entry()]
    client = MagicMock()
    client.get_guild = MagicMock(return_value=None)
    await remove_claimed_booster_channels_that_are_expired(client)
    mock_unclaim.assert_awaited_once()


@patch("commands.utility.claim_booster_channel.booster_service.unclaim", new_callable=AsyncMock)
@patch("commands.utility.claim_booster_channel.booster_service.get_all_claims", new_callable=AsyncMock)
async def test_remove_expired_user_gone(mock_claims, mock_unclaim):
    guild = MagicMock()
    guild.get_member = MagicMock(return_value=None)
    mock_claims.return_value = [_entry()]
    client = MagicMock()
    client.get_guild = MagicMock(return_value=guild)
    await remove_claimed_booster_channels_that_are_expired(client)
    mock_unclaim.assert_awaited_once()


@patch("commands.utility.claim_booster_channel.booster_service.unclaim", new_callable=AsyncMock)
@patch("commands.utility.claim_booster_channel.booster_service.get_all_claims", new_callable=AsyncMock)
async def test_remove_expired_booster_lapsed(mock_claims, mock_unclaim):
    guild = MagicMock(preferred_locale="en_US")
    member = MagicMock(premium_since=None)
    channel = MagicMock()
    channel.delete = AsyncMock()
    guild.get_member = MagicMock(return_value=member)
    guild.get_channel = MagicMock(return_value=channel)
    mock_claims.return_value = [_entry()]
    client = MagicMock()
    client.get_guild = MagicMock(return_value=guild)
    await remove_claimed_booster_channels_that_are_expired(client)
    mock_unclaim.assert_awaited_once()
    channel.delete.assert_awaited_once()


@patch("commands.utility.claim_booster_channel.booster_service.unclaim", new_callable=AsyncMock)
@patch("commands.utility.claim_booster_channel.booster_service.get_all_claims", new_callable=AsyncMock)
async def test_remove_expired_channel_gone(mock_claims, mock_unclaim):
    guild = MagicMock(preferred_locale="en_US")
    member = MagicMock(premium_since=MagicMock())
    guild.get_member = MagicMock(return_value=member)
    guild.get_channel = MagicMock(return_value=None)
    mock_claims.return_value = [_entry()]
    client = MagicMock()
    client.get_guild = MagicMock(return_value=guild)
    await remove_claimed_booster_channels_that_are_expired(client)
    mock_unclaim.assert_awaited_once()
