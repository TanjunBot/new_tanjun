import pytest
from unittest.mock import AsyncMock, MagicMock
import discord

from commands.admin.unban import unban
from tests.helpers.db import AsyncIter
from tests.helpers.discord import make_permissions


pytestmark = pytest.mark.asyncio


async def test_unban_missing_permission(restricted_command_info):
    await unban(restricted_command_info, "user")
    restricted_command_info.reply.assert_awaited_once()


async def test_unban_missing_bot_permission(admin_command_info):
    admin_command_info.guild.me.guild_permissions = make_permissions(ban_members=False)
    await unban(admin_command_info, "user")
    admin_command_info.reply.assert_awaited_once()


async def test_unban_user_not_found(admin_command_info):
    admin_command_info.guild.bans = MagicMock(return_value=AsyncIter([]))
    admin_command_info.guild.unban = AsyncMock()
    await unban(admin_command_info, "missing")
    admin_command_info.reply.assert_awaited_once()


async def test_unban_success(admin_command_info):
    ban_entry = MagicMock()
    ban_entry.user = MagicMock()
    ban_entry.user.name = "banneduser"
    admin_command_info.guild.bans = MagicMock(return_value=AsyncIter([ban_entry]))
    admin_command_info.guild.unban = AsyncMock()
    await unban(admin_command_info, "banneduser", reason="appeal")
    admin_command_info.guild.unban.assert_awaited_once()
    admin_command_info.reply.assert_awaited_once()


async def test_unban_forbidden(admin_command_info):
    ban_entry = MagicMock()
    ban_entry.user = MagicMock()
    ban_entry.user.name = "user"
    admin_command_info.guild.bans = MagicMock(return_value=AsyncIter([ban_entry]))
    admin_command_info.guild.unban = AsyncMock(side_effect=discord.Forbidden(MagicMock(), "no"))
    await unban(admin_command_info, "user")
    admin_command_info.reply.assert_awaited_once()


async def test_unban_http_exception(admin_command_info):
    async def failing_bans():
        raise discord.HTTPException(MagicMock(), "err")
        yield

    admin_command_info.guild.bans = failing_bans
    await unban(admin_command_info, "user")
    admin_command_info.reply.assert_awaited_once()
