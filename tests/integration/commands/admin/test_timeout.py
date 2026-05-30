import pytest
from unittest.mock import AsyncMock, MagicMock

from commands.admin.timeout import timeout
from tests.helpers.discord import (
    make_permissions,
    make_role,
    make_target_member,
)


pytestmark = pytest.mark.asyncio


async def test_timeout_missing_user_permission(restricted_command_info):
    target = make_target_member(top_role_position=1)
    await timeout(restricted_command_info, target, duration=10)
    restricted_command_info.reply.assert_awaited_once()
    assert "embed" in restricted_command_info.reply.await_args.kwargs


async def test_timeout_missing_bot_permission(admin_command_info):
    guild = admin_command_info.guild
    guild.me.guild_permissions = make_permissions(moderate_members=True)
    setattr(guild.me.guild_permissions, "moderate_members", False)
    target = make_target_member(top_role_position=1)

    await timeout(admin_command_info, target, duration=10)
    admin_command_info.reply.assert_awaited_once()


async def test_timeout_target_too_high(admin_command_info):
    target = make_target_member(top_role_position=100)
    admin_command_info.user.top_role = make_role(position=1)
    await timeout(admin_command_info, target, duration=10)
    admin_command_info.reply.assert_awaited_once()
    call_kwargs = admin_command_info.reply.await_args.kwargs
    assert "embed" in call_kwargs


async def test_timeout_success(admin_command_info):
    target = make_target_member(top_role_position=1)
    await timeout(admin_command_info, target, duration=10)
    admin_command_info.reply.assert_awaited_once()
    call_kwargs = admin_command_info.reply.await_args.kwargs
    assert "embed" in call_kwargs


async def test_timeout_success_with_reason(admin_command_info):
    target = make_target_member(top_role_position=1)
    await timeout(admin_command_info, target, duration=10, reason="test reason")
    admin_command_info.reply.assert_awaited_once()


async def test_timeout_forbidden(admin_command_info):
    import discord as discord_mod

    target = make_target_member(top_role_position=1)
    target.ban = AsyncMock(side_effect=discord_mod.Forbidden(MagicMock(), "forbidden"))
    target.kick = AsyncMock(side_effect=discord_mod.Forbidden(MagicMock(), "forbidden"))
    target.timeout = AsyncMock(side_effect=discord_mod.Forbidden(MagicMock(), "forbidden"))
    await timeout(admin_command_info, target, duration=10)
    admin_command_info.reply.assert_awaited_once()
    call_kwargs = admin_command_info.reply.await_args.kwargs
    assert "embed" in call_kwargs


async def test_timeout_http_exception(admin_command_info):
    import discord as discord_mod

    target = make_target_member(top_role_position=1)
    target.ban = AsyncMock(side_effect=discord_mod.HTTPException(MagicMock(), "error"))
    target.kick = AsyncMock(side_effect=discord_mod.HTTPException(MagicMock(), "error"))
    target.timeout = AsyncMock(side_effect=discord_mod.HTTPException(MagicMock(), "error"))
    await timeout(admin_command_info, target, duration=10)
    admin_command_info.reply.assert_awaited_once()


async def test_timeout_already_timed_out(admin_command_info):
    from datetime import timedelta

    target = make_target_member(top_role_position=1)
    target.is_timed_out = MagicMock(return_value=True)
    await timeout(admin_command_info, target, duration=timedelta(minutes=5))
    admin_command_info.reply.assert_awaited_once()


async def test_timeout_invalid_duration_type_error(admin_command_info):
    target = make_target_member(top_role_position=1)
    target.is_timed_out = MagicMock(return_value=False)
    target.timeout = AsyncMock()
    await timeout(admin_command_info, target, duration="not-a-duration")
    admin_command_info.reply.assert_awaited_once()


async def test_timeout_missing_guild_raises(admin_command_info):
    admin_command_info.guild = None
    target = make_target_member(top_role_position=1)
    with pytest.raises(ValueError):
        await timeout(admin_command_info, target, duration=10)
