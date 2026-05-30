import pytest
from unittest.mock import AsyncMock, MagicMock

from commands.admin.removetimeout import remove_timeout
from tests.helpers.discord import (
    make_permissions,
    make_target_member,
)


pytestmark = pytest.mark.asyncio


async def test_remove_timeout_missing_user_permission(restricted_command_info):
    target = make_target_member(top_role_position=1)
    await remove_timeout(restricted_command_info, target)
    restricted_command_info.reply.assert_awaited_once()
    assert "embed" in restricted_command_info.reply.await_args.kwargs


async def test_remove_timeout_missing_bot_permission(admin_command_info):
    guild = admin_command_info.guild
    guild.me.guild_permissions = make_permissions(moderate_members=True)
    setattr(guild.me.guild_permissions, "moderate_members", False)
    target = make_target_member(top_role_position=1)

    await remove_timeout(admin_command_info, target)
    admin_command_info.reply.assert_awaited_once()


async def test_remove_timeout_target_too_high(admin_command_info):
    target = make_target_member(top_role_position=100)
    admin_command_info.user.top_role.position = 1
    await remove_timeout(admin_command_info, target)
    admin_command_info.reply.assert_awaited_once()
    call_kwargs = admin_command_info.reply.await_args.kwargs
    assert "embed" in call_kwargs


async def test_remove_timeout_success(admin_command_info):
    target = make_target_member(top_role_position=1)
    await remove_timeout(admin_command_info, target)
    admin_command_info.reply.assert_awaited_once()
    call_kwargs = admin_command_info.reply.await_args.kwargs
    assert "embed" in call_kwargs


async def test_remove_timeout_success_with_reason(admin_command_info):
    target = make_target_member(top_role_position=1)
    await remove_timeout(admin_command_info, target, reason="test reason")
    admin_command_info.reply.assert_awaited_once()


async def test_remove_timeout_forbidden(admin_command_info):
    import discord as discord_mod

    target = make_target_member(top_role_position=1)
    target.ban = AsyncMock(side_effect=discord_mod.Forbidden(MagicMock(), "forbidden"))
    target.kick = AsyncMock(side_effect=discord_mod.Forbidden(MagicMock(), "forbidden"))
    target.timeout = AsyncMock(side_effect=discord_mod.Forbidden(MagicMock(), "forbidden"))
    await remove_timeout(admin_command_info, target)
    admin_command_info.reply.assert_awaited_once()
    call_kwargs = admin_command_info.reply.await_args.kwargs
    assert "embed" in call_kwargs


async def test_remove_timeout_http_exception(admin_command_info):
    import discord as discord_mod

    target = make_target_member(top_role_position=1)
    target.ban = AsyncMock(side_effect=discord_mod.HTTPException(MagicMock(), "error"))
    target.kick = AsyncMock(side_effect=discord_mod.HTTPException(MagicMock(), "error"))
    target.timeout = AsyncMock(side_effect=discord_mod.HTTPException(MagicMock(), "error"))
    await remove_timeout(admin_command_info, target)
    admin_command_info.reply.assert_awaited_once()
