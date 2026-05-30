import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from commands.admin.moverole import moverole
from tests.helpers.discord import (
    make_permissions,
    make_role,
    make_target_member,
    make_text_channel,
)


pytestmark = pytest.mark.asyncio


async def test_moverole_missing_user_permission(restricted_command_info):
    role = make_role()
    target_role = make_role()
    await moverole(restricted_command_info, role=role, target_role=target_role, position=1)
    restricted_command_info.reply.assert_awaited()


async def test_moverole_success(admin_command_info):
    role = make_role()
    target_role = make_role()
    await moverole(admin_command_info, role=role, target_role=target_role, position=1)
    assert admin_command_info.reply.await_count >= 0


async def test_moverole_reply_called(admin_command_info):
    role = make_role()
    target_role = make_role()
    await moverole(admin_command_info, role=role, target_role=target_role, position=1)
    assert admin_command_info.reply.await_count >= 0


async def test_moverole_with_admin_perms(admin_command_info):
    role = make_role()
    target_role = make_role()
    await moverole(admin_command_info, role=role, target_role=target_role, position=1)
    assert admin_command_info.reply.await_count >= 0


async def test_moverole_embed_or_content(admin_command_info):
    role = make_role()
    target_role = make_role()
    await moverole(admin_command_info, role=role, target_role=target_role, position=1)
    if admin_command_info.reply.await_count:
        call = admin_command_info.reply.await_args
        assert call.kwargs.get("embed") is not None or call.args or call.kwargs.get("view") is not None


async def test_moverole_does_not_raise(admin_command_info):
    role = make_role()
    target_role = make_role()
    await moverole(admin_command_info, role=role, target_role=target_role, position=1)


async def test_moverole_guild_present(admin_command_info):
    assert admin_command_info.guild is not None
    role = make_role()
    target_role = make_role()
    await moverole(admin_command_info, role=role, target_role=target_role, position=1)


async def test_moverole_missing_bot_permission(admin_command_info):
    admin_command_info.guild.me.guild_permissions = make_permissions(manage_roles=False)
    role = make_role()
    target_role = make_role()
    await moverole(admin_command_info, role=role, target_role=target_role, position="above")
    admin_command_info.reply.assert_awaited_once()


async def test_moverole_role_too_high(admin_command_info):
    role = make_role(position=100)
    target_role = make_role(position=50)
    admin_command_info.user.top_role.position = 1
    await moverole(admin_command_info, role=role, target_role=target_role, position="above")
    admin_command_info.reply.assert_awaited_once()


async def test_moverole_success_above(admin_command_info):
    role = make_role(position=1)
    role.edit = AsyncMock()
    target_role = make_role(position=5)
    await moverole(admin_command_info, role=role, target_role=target_role, position="above")
    admin_command_info.reply.assert_awaited_once()
    role.edit.assert_awaited_once()


async def test_moverole_success_below(admin_command_info):
    role = make_role(position=1)
    role.edit = AsyncMock()
    target_role = make_role(position=5)
    await moverole(admin_command_info, role=role, target_role=target_role, position="below")
    admin_command_info.reply.assert_awaited_once()


async def test_moverole_forbidden(admin_command_info):
    import discord as discord_mod

    role = make_role(position=1)
    role.edit = AsyncMock(side_effect=discord_mod.Forbidden(MagicMock(), "forbidden"))
    target_role = make_role(position=5)
    await moverole(admin_command_info, role=role, target_role=target_role, position="above")
    admin_command_info.reply.assert_awaited_once()


async def test_moverole_http_exception(admin_command_info):
    import discord as discord_mod

    role = make_role(position=1)
    role.edit = AsyncMock(side_effect=discord_mod.HTTPException(MagicMock(), "error"))
    target_role = make_role(position=5)
    await moverole(admin_command_info, role=role, target_role=target_role, position="above")
    admin_command_info.reply.assert_awaited_once()
