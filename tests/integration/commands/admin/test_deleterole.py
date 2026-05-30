import pytest
from unittest.mock import AsyncMock, MagicMock

import discord as discord_mod

from commands.admin.deleterole import deleterole
from tests.helpers.discord import make_permissions, make_role


pytestmark = pytest.mark.asyncio


def _setup_deleterole(admin_command_info):
    admin_command_info.client.user = MagicMock(id=admin_command_info.guild.me.id)
    admin_command_info.guild.get_member = MagicMock(return_value=admin_command_info.guild.me)


async def test_deleterole_missing_user_permission(restricted_command_info):
    role = make_role()
    await deleterole(restricted_command_info, role=role, reason="test")
    restricted_command_info.reply.assert_awaited_once()


async def test_deleterole_missing_bot_permission(admin_command_info):
    guild = admin_command_info.guild
    guild.me.guild_permissions = make_permissions(manage_roles=False)
    guild.get_member = MagicMock(return_value=guild.me)
    admin_command_info.client.user = MagicMock(id=guild.me.id)
    role = make_role()
    await deleterole(admin_command_info, role=role, reason="test")
    admin_command_info.reply.assert_awaited_once()


async def test_deleterole_missing_bot_member(admin_command_info):
    admin_command_info.client.user = MagicMock(id=999)
    admin_command_info.guild.get_member = MagicMock(return_value=None)
    role = make_role(position=1)
    await deleterole(admin_command_info, role=role)
    admin_command_info.reply.assert_awaited_once()


async def test_deleterole_role_too_high(admin_command_info):
    _setup_deleterole(admin_command_info)
    role = make_role(position=100)
    admin_command_info.user.top_role.position = 1
    await deleterole(admin_command_info, role=role, reason="test")
    admin_command_info.reply.assert_awaited_once()


async def test_deleterole_bot_role_too_high(admin_command_info):
    _setup_deleterole(admin_command_info)
    role = make_role(position=100)
    admin_command_info.guild.me.top_role.position = 1
    await deleterole(admin_command_info, role=role, reason="test")
    admin_command_info.reply.assert_awaited_once()


async def test_deleterole_success_with_reason(admin_command_info):
    _setup_deleterole(admin_command_info)
    role = make_role(position=1)
    role.delete = AsyncMock()
    await deleterole(admin_command_info, role=role, reason="test reason")
    role.delete.assert_awaited_once_with(reason="test reason")
    admin_command_info.reply.assert_awaited_once()


async def test_deleterole_success_without_reason(admin_command_info):
    _setup_deleterole(admin_command_info)
    role = make_role(position=1)
    role.delete = AsyncMock()
    await deleterole(admin_command_info, role=role)
    role.delete.assert_awaited_once_with(reason=None)
    admin_command_info.reply.assert_awaited_once()


async def test_deleterole_forbidden(admin_command_info):
    _setup_deleterole(admin_command_info)
    role = make_role(position=1)
    role.delete = AsyncMock(side_effect=discord_mod.Forbidden(MagicMock(), "forbidden"))
    await deleterole(admin_command_info, role=role, reason="test")
    admin_command_info.reply.assert_awaited_once()


async def test_deleterole_http_exception(admin_command_info):
    _setup_deleterole(admin_command_info)
    role = make_role(position=1)
    exc = discord_mod.HTTPException(MagicMock(), "error")
    exc.status = 500
    role.delete = AsyncMock(side_effect=exc)
    await deleterole(admin_command_info, role=role, reason="test")
    admin_command_info.reply.assert_awaited_once()


async def test_deleterole_not_found(admin_command_info):
    _setup_deleterole(admin_command_info)
    role = make_role(position=1)
    role.delete = AsyncMock(side_effect=discord_mod.NotFound(MagicMock(), "not found"))
    await deleterole(admin_command_info, role=role, reason="test")
    admin_command_info.reply.assert_awaited_once()


async def test_deleterole_bot_role_equal_position(admin_command_info):
    _setup_deleterole(admin_command_info)
    role = make_role(position=50)
    admin_command_info.guild.me.top_role.position = 50
    await deleterole(admin_command_info, role=role)
    admin_command_info.reply.assert_awaited_once()


async def test_deleterole_user_role_equal_position(admin_command_info):
    _setup_deleterole(admin_command_info)
    role = make_role(position=50)
    admin_command_info.user.top_role.position = 50
    await deleterole(admin_command_info, role=role)
    admin_command_info.reply.assert_awaited_once()
