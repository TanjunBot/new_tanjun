from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from commands.admin.boosterrole import create_booster_role
from tests.helpers.discord import make_permissions, make_role

pytestmark = pytest.mark.asyncio


async def test_create_booster_role_missing_user_permission(restricted_command_info):
    role = make_role()
    await create_booster_role(restricted_command_info, role=role)
    restricted_command_info.reply.assert_awaited_once()


async def test_create_booster_role_missing_bot_permission(admin_command_info):
    admin_command_info.guild.me.guild_permissions = make_permissions(manage_roles=False)
    role = make_role(position=5)
    await create_booster_role(admin_command_info, role=role)
    admin_command_info.reply.assert_awaited_once()


@patch("commands.admin.boosterrole.booster_service")
async def test_create_booster_role_remove(mock_service, admin_command_info):
    mock_service.delete = AsyncMock()
    await create_booster_role(admin_command_info, role=None)
    mock_service.delete.assert_awaited_once()
    admin_command_info.reply.assert_awaited_once()


async def test_create_booster_role_target_too_high(admin_command_info):
    role = make_role(position=100)
    admin_command_info.user.top_role = make_role(position=10)
    await create_booster_role(admin_command_info, role=role)
    admin_command_info.reply.assert_awaited_once()


async def test_create_booster_role_bot_role_too_high(admin_command_info):
    role = make_role(position=100)
    admin_command_info.guild.me.top_role = make_role(position=10)
    admin_command_info.client.user = MagicMock(id=111)
    await create_booster_role(admin_command_info, role=role)
    admin_command_info.reply.assert_awaited_once()


@patch("commands.admin.boosterrole.booster_service")
async def test_create_booster_role_success(mock_service, admin_command_info):
    mock_service.add = AsyncMock()
    role = make_role(position=5)
    role.permissions = MagicMock(administrator=False)
    admin_command_info.client.user = MagicMock(id=111)
    await create_booster_role(admin_command_info, role=role)
    mock_service.add.assert_awaited_once()
    admin_command_info.reply.assert_awaited_once()


@patch("commands.admin.boosterrole.booster_service")
async def test_create_booster_role_success_admin_warning(mock_service, admin_command_info):
    mock_service.add = AsyncMock()
    role = make_role(position=5)
    role.permissions = MagicMock(administrator=True)
    admin_command_info.client.user = MagicMock(id=111)
    await create_booster_role(admin_command_info, role=role)
    admin_command_info.reply.assert_awaited_once()


@patch("commands.admin.boosterrole.booster_service")
async def test_create_booster_role_forbidden(mock_service, admin_command_info):
    import discord as discord_mod

    mock_service.add = AsyncMock(side_effect=discord_mod.Forbidden(MagicMock(), "forbidden"))
    role = make_role(position=5)
    role.permissions = MagicMock(administrator=False)
    admin_command_info.client.user = MagicMock(id=111)
    await create_booster_role(admin_command_info, role=role)
    admin_command_info.reply.assert_awaited_once()


@patch("commands.admin.boosterrole.booster_service")
async def test_create_booster_role_http_exception(mock_service, admin_command_info):
    import discord as discord_mod

    mock_service.add = AsyncMock(side_effect=discord_mod.HTTPException(MagicMock(), "error"))
    role = make_role(position=5)
    role.permissions = MagicMock(administrator=False)
    admin_command_info.client.user = MagicMock(id=111)
    await create_booster_role(admin_command_info, role=role)
    admin_command_info.reply.assert_awaited_once()


async def test_create_booster_role_missing_guild_raises(admin_command_info):
    admin_command_info.guild = None
    with pytest.raises(ValueError):
        await create_booster_role(admin_command_info, role=make_role())


async def test_create_booster_role_missing_client_user_raises(admin_command_info):
    admin_command_info.client.user = None
    role = make_role(position=5)
    with pytest.raises(ValueError):
        await create_booster_role(admin_command_info, role=role)
