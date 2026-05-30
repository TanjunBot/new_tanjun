from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from commands.utility.claim_booster_channel import claimBoosterChannel
from commands.utility.claim_booster_role import claimBoosterRole, remove_claimed_booster_roles_that_are_expired
from commands.utility.delete_booster_channel import deleteBoosterChannel
from commands.utility.delete_booster_role import deleteBoosterRole
from commands.utility.setup_booster_channel import setupBoosterChannel
from commands.utility.setup_booster_role import setupBoosterRole
from services.booster_service import ClaimedBoosterType
from tests.helpers.discord import make_guild, make_member

pytestmark = pytest.mark.asyncio


@patch("commands.utility.claim_booster_role.booster_service.get", new_callable=AsyncMock, return_value=None)
async def test_claim_booster_role_no_setup(mock_get, admin_command_info):
    await claimBoosterRole(admin_command_info, "MyRole", "FF0000", None)
    admin_command_info.reply.assert_awaited_once()


@patch("commands.utility.claim_booster_role.booster_service.get", new_callable=AsyncMock, return_value="111")
async def test_claim_booster_role_not_booster(mock_get, admin_command_info):
    admin_command_info.user.premium_since = None
    await claimBoosterRole(admin_command_info, "MyRole", "FF0000", None)
    admin_command_info.reply.assert_awaited_once()


@patch("commands.utility.claim_booster_role.booster_service.get_claim_for_user", new_callable=AsyncMock, return_value=True)
@patch("commands.utility.claim_booster_role.booster_service.get", new_callable=AsyncMock, return_value="111")
async def test_claim_booster_role_already_claimed(mock_get, mock_claim, admin_command_info):
    admin_command_info.user.premium_since = MagicMock()
    await claimBoosterRole(admin_command_info, "MyRole", "FF0000", None)
    admin_command_info.reply.assert_awaited_once()


@patch("commands.utility.claim_booster_role.booster_service.get_claim_for_user", new_callable=AsyncMock, return_value=None)
@patch("commands.utility.claim_booster_role.booster_service.get", new_callable=AsyncMock, return_value="111")
async def test_claim_booster_role_invalid_color(mock_get, mock_claim, admin_command_info):
    admin_command_info.user.premium_since = MagicMock()
    await claimBoosterRole(admin_command_info, "MyRole", "nothex", None)
    admin_command_info.reply.assert_awaited_once()


@patch("commands.utility.claim_booster_role.booster_service.get_claim_for_user", new_callable=AsyncMock, return_value=None)
@patch("commands.utility.claim_booster_role.booster_service.get", new_callable=AsyncMock, return_value="999999999")
async def test_claim_booster_role_missing_template_role(mock_get, mock_claim, admin_command_info):
    admin_command_info.user.premium_since = MagicMock()
    admin_command_info.guild.get_role = MagicMock(return_value=None)
    await claimBoosterRole(admin_command_info, "MyRole", "FF0000", None)
    admin_command_info.reply.assert_awaited_once()


@patch("commands.utility.claim_booster_role.booster_service.claim", new_callable=AsyncMock)
@patch("commands.utility.claim_booster_role.booster_service.get_claim_for_user", new_callable=AsyncMock, return_value=None)
@patch("commands.utility.claim_booster_role.booster_service.get", new_callable=AsyncMock, return_value="111")
async def test_claim_booster_role_success(mock_get, mock_claim_user, mock_claim, admin_command_info):
    admin_command_info.user.premium_since = MagicMock()
    template = MagicMock()
    template.color = 0
    template.permissions = MagicMock()
    template.hoist = False
    template.mentionable = False
    template.position = 1
    admin_command_info.guild.get_role = MagicMock(return_value=template)
    new_role = MagicMock()
    new_role.edit = AsyncMock()
    admin_command_info.guild.create_role = AsyncMock(return_value=new_role)
    admin_command_info.user.add_roles = AsyncMock()
    await claimBoosterRole(admin_command_info, "MyRole", "#FF0000", None)
    mock_claim.assert_awaited_once()
    admin_command_info.reply.assert_awaited_once()


@patch("commands.utility.claim_booster_channel.booster_service.get", new_callable=AsyncMock, return_value=None)
async def test_claim_booster_channel_no_setup(mock_get, admin_command_info):
    await claimBoosterChannel(admin_command_info, "vc")
    admin_command_info.reply.assert_awaited_once()


@patch("commands.utility.setup_booster_role.booster_service.get", new_callable=AsyncMock, return_value=None)
@patch("commands.utility.setup_booster_role.booster_service.add", new_callable=AsyncMock)
async def test_setup_booster_role_success(mock_add, mock_get, admin_command_info):
    role = MagicMock()
    role.id = 111
    await setupBoosterRole(admin_command_info, role)
    mock_add.assert_awaited_once()
    admin_command_info.reply.assert_awaited_once()


@patch("commands.utility.setup_booster_channel.booster_service.get", new_callable=AsyncMock, return_value=None)
@patch("commands.utility.setup_booster_channel.booster_service.add", new_callable=AsyncMock)
async def test_setup_booster_channel_success(mock_add, mock_get, admin_command_info):
    category = MagicMock()
    category.id = 999
    await setupBoosterChannel(admin_command_info, category)
    mock_add.assert_awaited_once()
    admin_command_info.reply.assert_awaited_once()


@patch("commands.utility.delete_booster_role.booster_service.get", new_callable=AsyncMock, return_value=None)
async def test_delete_booster_role_not_setup(mock_get, admin_command_info):
    await deleteBoosterRole(admin_command_info)
    admin_command_info.reply.assert_awaited_once()


@patch("commands.utility.delete_booster_channel.booster_service.get", new_callable=AsyncMock, return_value=None)
async def test_delete_booster_channel_not_setup(mock_get, admin_command_info):
    await deleteBoosterChannel(admin_command_info)
    admin_command_info.reply.assert_awaited_once()


@patch("commands.utility.claim_booster_role.booster_service.unclaim", new_callable=AsyncMock)
@patch("commands.utility.claim_booster_role.booster_service.get_all_claims", new_callable=AsyncMock)
async def test_remove_expired_booster_roles_cleanup(mock_claims, mock_unclaim):
    entry = MagicMock()
    entry.guild_id = "1"
    entry.user_id = "2"
    entry.role_id = "3"
    mock_claims.return_value = [entry]
    client = MagicMock()
    client.get_guild = MagicMock(return_value=None)
    await remove_claimed_booster_roles_that_are_expired(client)
    mock_unclaim.assert_awaited_once_with(ClaimedBoosterType.ROLE, "2", "1")


@patch("commands.utility.claim_booster_role.booster_service.unclaim", new_callable=AsyncMock)
@patch("commands.utility.claim_booster_role.booster_service.get_all_claims", new_callable=AsyncMock)
async def test_remove_expired_booster_roles_premium_lapsed(mock_claims, mock_unclaim):
    entry = MagicMock()
    entry.guild_id = "123456789012345678"
    entry.user_id = "111111111111111111"
    entry.role_id = "222222222222222222"
    mock_claims.return_value = [entry]
    guild = make_guild(guild_id=int(entry.guild_id))
    user = make_member(user_id=int(entry.user_id))
    user.premium_since = None
    role = MagicMock()
    role.delete = AsyncMock()
    user.remove_roles = AsyncMock()
    guild.get_member = MagicMock(return_value=user)
    guild.get_role = MagicMock(return_value=role)
    guild.preferred_locale = "en_US"
    client = MagicMock()
    client.get_guild = MagicMock(return_value=guild)
    await remove_claimed_booster_roles_that_are_expired(client)
    mock_unclaim.assert_awaited()
