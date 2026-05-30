from unittest.mock import AsyncMock, MagicMock

import discord as discord_mod
import pytest

from commands.admin.createrole import createrole
from tests.helpers.discord import make_permissions, make_role

pytestmark = pytest.mark.asyncio


async def test_createrole_missing_user_permission(restricted_command_info):
    await createrole(restricted_command_info, name="test")
    restricted_command_info.reply.assert_awaited_once()


async def test_createrole_missing_bot_permission(admin_command_info):
    guild = admin_command_info.guild
    guild.me.guild_permissions = make_permissions(manage_roles=False)
    guild.get_member = MagicMock(return_value=guild.me)
    admin_command_info.client.user = MagicMock(id=guild.me.id)
    await createrole(admin_command_info, name="test")
    admin_command_info.reply.assert_awaited_once()


async def test_createrole_missing_name(admin_command_info):
    admin_command_info.client.user = MagicMock(id=admin_command_info.guild.me.id)
    admin_command_info.guild.get_member = MagicMock(return_value=admin_command_info.guild.me)
    await createrole(admin_command_info, name="")
    admin_command_info.reply.assert_awaited_once()


async def test_createrole_name_too_long(admin_command_info):
    admin_command_info.client.user = MagicMock(id=admin_command_info.guild.me.id)
    admin_command_info.guild.get_member = MagicMock(return_value=admin_command_info.guild.me)
    await createrole(admin_command_info, name="x" * 101)
    admin_command_info.reply.assert_awaited_once()


async def test_createrole_invalid_color(admin_command_info):
    admin_command_info.client.user = MagicMock(id=admin_command_info.guild.me.id)
    admin_command_info.guild.get_member = MagicMock(return_value=admin_command_info.guild.me)
    await createrole(admin_command_info, name="test", color="notacolor")
    admin_command_info.reply.assert_awaited_once()


async def test_createrole_color_without_hash(admin_command_info):
    admin_command_info.client.user = MagicMock(id=admin_command_info.guild.me.id)
    admin_command_info.guild.get_member = MagicMock(return_value=admin_command_info.guild.me)
    new_role = make_role(name="test")
    admin_command_info.guild.create_role = AsyncMock(return_value=new_role)
    await createrole(admin_command_info, name="test", color="FF0000")
    admin_command_info.reply.assert_awaited_once()


async def test_createrole_reason_too_long(admin_command_info):
    admin_command_info.client.user = MagicMock(id=admin_command_info.guild.me.id)
    admin_command_info.guild.get_member = MagicMock(return_value=admin_command_info.guild.me)
    await createrole(admin_command_info, name="test", reason="x" * 513)
    admin_command_info.reply.assert_awaited_once()


async def test_createrole_role_icons_not_enabled(admin_command_info):
    admin_command_info.client.user = MagicMock(id=admin_command_info.guild.me.id)
    admin_command_info.guild.get_member = MagicMock(return_value=admin_command_info.guild.me)
    admin_command_info.guild.features = []
    attachment = MagicMock()
    attachment.filename = "icon.webp"
    attachment.size = 100
    await createrole(admin_command_info, name="test", display_icon=attachment)
    admin_command_info.reply.assert_awaited_once()


async def test_createrole_invalid_icon_extension(admin_command_info):
    import discord

    admin_command_info.client.user = MagicMock(id=admin_command_info.guild.me.id)
    admin_command_info.guild.get_member = MagicMock(return_value=admin_command_info.guild.me)
    admin_command_info.guild.features = ["ROLE_ICONS"]
    attachment = discord.Attachment()
    attachment.filename = "icon.png"
    attachment.size = 100
    await createrole(admin_command_info, name="test", display_icon=attachment)
    admin_command_info.reply.assert_awaited_once()


async def test_createrole_icon_too_large(admin_command_info):
    import discord

    admin_command_info.client.user = MagicMock(id=admin_command_info.guild.me.id)
    admin_command_info.guild.get_member = MagicMock(return_value=admin_command_info.guild.me)
    admin_command_info.guild.features = ["ROLE_ICONS"]
    attachment = discord.Attachment()
    attachment.filename = "icon.webp"
    attachment.size = 300000
    await createrole(admin_command_info, name="test", display_icon=attachment)
    admin_command_info.reply.assert_awaited_once()


async def test_createrole_success(admin_command_info):
    admin_command_info.client.user = MagicMock(id=admin_command_info.guild.me.id)
    admin_command_info.guild.get_member = MagicMock(return_value=admin_command_info.guild.me)
    new_role = make_role(name="NewRole")
    admin_command_info.guild.create_role = AsyncMock(return_value=new_role)
    await createrole(admin_command_info, name="NewRole", color="#FF0000", reason="test", hoist=True, mentionable=True)
    admin_command_info.reply.assert_awaited_once()
    admin_command_info.guild.create_role.assert_awaited_once()


async def test_createrole_success_with_attachment(admin_command_info):
    import discord

    admin_command_info.client.user = MagicMock(id=admin_command_info.guild.me.id)
    admin_command_info.guild.get_member = MagicMock(return_value=admin_command_info.guild.me)
    admin_command_info.guild.features = ["ROLE_ICONS"]
    attachment = discord.Attachment()
    attachment.filename = "icon.webp"
    attachment.size = 100
    attachment.read = AsyncMock(return_value=b"bytes")
    new_role = make_role(name="IconRole")
    admin_command_info.guild.create_role = AsyncMock(return_value=new_role)
    await createrole(admin_command_info, name="IconRole", display_icon=attachment)
    admin_command_info.reply.assert_awaited_once()


async def test_createrole_success_with_unicode_icon(admin_command_info):
    admin_command_info.client.user = MagicMock(id=admin_command_info.guild.me.id)
    admin_command_info.guild.get_member = MagicMock(return_value=admin_command_info.guild.me)
    admin_command_info.guild.features = ["ROLE_ICONS"]
    new_role = make_role(name="EmojiRole")
    admin_command_info.guild.create_role = AsyncMock(return_value=new_role)
    await createrole(admin_command_info, name="EmojiRole", display_icon="🎭")
    admin_command_info.reply.assert_awaited_once()


async def test_createrole_forbidden(admin_command_info):
    admin_command_info.client.user = MagicMock(id=admin_command_info.guild.me.id)
    admin_command_info.guild.get_member = MagicMock(return_value=admin_command_info.guild.me)
    admin_command_info.guild.create_role = AsyncMock(side_effect=discord_mod.Forbidden(MagicMock(), "forbidden"))
    await createrole(admin_command_info, name="test")
    admin_command_info.reply.assert_awaited_once()


async def test_createrole_http_exception(admin_command_info):
    admin_command_info.client.user = MagicMock(id=admin_command_info.guild.me.id)
    admin_command_info.guild.get_member = MagicMock(return_value=admin_command_info.guild.me)
    exc = discord_mod.HTTPException(MagicMock(), "error")
    exc.status = 500
    admin_command_info.guild.create_role = AsyncMock(side_effect=exc)
    await createrole(admin_command_info, name="test")
    admin_command_info.reply.assert_awaited_once()


async def test_createrole_not_found(admin_command_info):
    admin_command_info.client.user = MagicMock(id=admin_command_info.guild.me.id)
    admin_command_info.guild.get_member = MagicMock(return_value=admin_command_info.guild.me)
    admin_command_info.guild.create_role = AsyncMock(side_effect=discord_mod.NotFound(MagicMock(), "not found"))
    await createrole(admin_command_info, name="test")
    admin_command_info.reply.assert_awaited_once()
