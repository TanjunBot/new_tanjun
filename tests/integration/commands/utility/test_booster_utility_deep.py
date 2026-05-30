from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from commands.utility.delete_booster_channel import deleteBoosterChannel
from commands.utility.delete_booster_role import deleteBoosterRole
from commands.utility.setup_booster_channel import setupBoosterChannel
from commands.utility.setup_booster_role import setupBoosterRole
from services.booster_service import BoosterType
from tests.helpers.discord import make_member, make_permissions

pytestmark = pytest.mark.asyncio


async def test_delete_booster_channel_no_guild(admin_command_info):
    admin_command_info.guild = None
    await deleteBoosterChannel(admin_command_info)
    admin_command_info.reply.assert_awaited_once()


async def test_delete_booster_channel_no_channel(admin_command_info):
    admin_command_info.channel = None
    await deleteBoosterChannel(admin_command_info)
    admin_command_info.reply.assert_awaited_once()


async def test_delete_booster_channel_no_permission(admin_command_info):
    member = make_member()
    member.guild_permissions = make_permissions(administrator=False)
    admin_command_info.user = member
    perms = make_permissions(administrator=False)
    admin_command_info.channel.permissions_for = MagicMock(return_value=perms)
    await deleteBoosterChannel(admin_command_info)
    admin_command_info.reply.assert_awaited_once()


@patch("commands.utility.delete_booster_channel.booster_service.get", new_callable=AsyncMock, return_value=None)
async def test_delete_booster_channel_not_configured(mock_get, admin_command_info):
    perms = make_permissions(administrator=True)
    admin_command_info.channel.permissions_for = MagicMock(return_value=perms)
    await deleteBoosterChannel(admin_command_info)
    admin_command_info.reply.assert_awaited_once()


@patch("commands.utility.delete_booster_channel.booster_service.delete", new_callable=AsyncMock)
@patch("commands.utility.delete_booster_channel.booster_service.get", new_callable=AsyncMock, return_value="123")
async def test_delete_booster_channel_success(mock_get, mock_delete, admin_command_info):
    perms = make_permissions(administrator=True)
    admin_command_info.channel.permissions_for = MagicMock(return_value=perms)
    await deleteBoosterChannel(admin_command_info)
    mock_delete.assert_awaited_once()
    admin_command_info.reply.assert_awaited_once()


async def test_delete_booster_role_no_guild(admin_command_info):
    admin_command_info.guild = None
    await deleteBoosterRole(admin_command_info)
    admin_command_info.reply.assert_awaited_once()


async def test_delete_booster_role_no_channel(admin_command_info):
    admin_command_info.channel = None
    await deleteBoosterRole(admin_command_info)
    admin_command_info.reply.assert_awaited_once()


async def test_delete_booster_role_no_permission(admin_command_info):
    member = make_member()
    admin_command_info.user = member
    perms = make_permissions(administrator=False)
    admin_command_info.channel.permissions_for = MagicMock(return_value=perms)
    await deleteBoosterRole(admin_command_info)
    admin_command_info.reply.assert_awaited_once()


@patch("commands.utility.delete_booster_role.booster_service.get", new_callable=AsyncMock, return_value=None)
async def test_delete_booster_role_not_configured(mock_get, admin_command_info):
    perms = make_permissions(administrator=True)
    admin_command_info.channel.permissions_for = MagicMock(return_value=perms)
    await deleteBoosterRole(admin_command_info)
    admin_command_info.reply.assert_awaited_once()


@patch("commands.utility.delete_booster_role.booster_service.delete", new_callable=AsyncMock)
@patch("commands.utility.delete_booster_role.booster_service.get", new_callable=AsyncMock, return_value="456")
async def test_delete_booster_role_success(mock_get, mock_delete, admin_command_info):
    perms = make_permissions(administrator=True)
    admin_command_info.channel.permissions_for = MagicMock(return_value=perms)
    await deleteBoosterRole(admin_command_info)
    mock_delete.assert_awaited_once()


async def test_setup_booster_channel_no_guild(admin_command_info):
    admin_command_info.guild = None
    await setupBoosterChannel(admin_command_info, MagicMock())
    admin_command_info.reply.assert_awaited_once()


async def test_setup_booster_channel_no_permission(admin_command_info):
    admin_command_info.user.guild_permissions = make_permissions(administrator=False)
    await setupBoosterChannel(admin_command_info, MagicMock())
    admin_command_info.reply.assert_awaited_once()


@patch("commands.utility.setup_booster_channel.booster_service.get", new_callable=AsyncMock, return_value="existing")
async def test_setup_booster_channel_already_set(mock_get, admin_command_info):
    admin_command_info.user.guild_permissions = make_permissions(administrator=True)
    await setupBoosterChannel(admin_command_info, MagicMock())
    admin_command_info.reply.assert_awaited_once()


@patch("commands.utility.setup_booster_channel.booster_service.add", new_callable=AsyncMock)
@patch("commands.utility.setup_booster_channel.booster_service.get", new_callable=AsyncMock, return_value=None)
async def test_setup_booster_channel_success(mock_get, mock_add, admin_command_info):
    admin_command_info.user.guild_permissions = make_permissions(administrator=True)
    category = MagicMock()
    category.id = 777
    await setupBoosterChannel(admin_command_info, category)
    mock_add.assert_awaited_once_with(BoosterType.CHANNEL, str(admin_command_info.guild.id), "777")


async def test_setup_booster_role_no_guild(admin_command_info):
    admin_command_info.guild = None
    await setupBoosterRole(admin_command_info, MagicMock())
    admin_command_info.reply.assert_awaited_once()


async def test_setup_booster_role_no_permission(admin_command_info):
    admin_command_info.user.guild_permissions = make_permissions(administrator=False)
    await setupBoosterRole(admin_command_info, MagicMock())
    admin_command_info.reply.assert_awaited_once()


@patch("commands.utility.setup_booster_role.booster_service.get", new_callable=AsyncMock, return_value="existing")
async def test_setup_booster_role_already_set(mock_get, admin_command_info):
    admin_command_info.user.guild_permissions = make_permissions(administrator=True)
    await setupBoosterRole(admin_command_info, MagicMock())
    admin_command_info.reply.assert_awaited_once()


@patch("commands.utility.setup_booster_role.booster_service.add", new_callable=AsyncMock)
@patch("commands.utility.setup_booster_role.booster_service.get", new_callable=AsyncMock, return_value=None)
async def test_setup_booster_role_success(mock_get, mock_add, admin_command_info):
    admin_command_info.user.guild_permissions = make_permissions(administrator=True)
    role = MagicMock()
    role.id = 888
    await setupBoosterRole(admin_command_info, role)
    mock_add.assert_awaited_once_with(BoosterType.ROLE, str(admin_command_info.guild.id), "888")
