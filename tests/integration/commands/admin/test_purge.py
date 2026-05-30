import pytest
from unittest.mock import AsyncMock, MagicMock
import discord

from commands.admin.purge import purge
from tests.helpers.discord import make_permissions, make_text_channel


pytestmark = pytest.mark.asyncio


async def test_purge_missing_permission(restricted_command_info):
    await purge(restricted_command_info, 10)
    restricted_command_info.reply.assert_awaited_once()


async def test_purge_missing_bot_permission(admin_command_info):
    channel = make_text_channel(guild=admin_command_info.guild)
    bot_perms = make_permissions(manage_messages=False)
    channel.permissions_for = MagicMock(return_value=bot_perms)
    await purge(admin_command_info, 10, channel)
    admin_command_info.reply.assert_awaited_once()


async def test_purge_invalid_amount(admin_command_info):
    await purge(admin_command_info, 0)
    admin_command_info.reply.assert_awaited_once()


async def test_purge_negative_amount(admin_command_info):
    await purge(admin_command_info, -1)
    admin_command_info.reply.assert_awaited_once()


async def test_purge_success(admin_command_info):
    admin_command_info.channel.purge = AsyncMock(return_value=[MagicMock()] * 5)
    await purge(admin_command_info, 5)
    admin_command_info.reply.assert_awaited_once()


async def test_purge_forbidden(admin_command_info):
    import discord as discord_mod

    admin_command_info.channel.purge = AsyncMock(side_effect=discord_mod.Forbidden(MagicMock(), "nope"))
    await purge(admin_command_info, 5)
    admin_command_info.reply.assert_awaited_once()


async def test_purge_http_exception(admin_command_info):
    import discord as discord_mod

    admin_command_info.channel.purge = AsyncMock(side_effect=discord_mod.HTTPException(MagicMock(), "err"))
    await purge(admin_command_info, 5)
    admin_command_info.reply.assert_awaited_once()


async def test_purge_with_setting(admin_command_info):
    admin_command_info.channel.purge = AsyncMock(return_value=[])
    await purge(admin_command_info, 10, setting="bot")
    admin_command_info.reply.assert_awaited_once()
