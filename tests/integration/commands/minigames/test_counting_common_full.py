from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from commands.minigames import _counting_common as common
from tests.helpers.discord import make_command_info, make_guild, make_member, make_permissions, make_text_channel

pytestmark = pytest.mark.asyncio


def _bot_member(info, **perm_flags):
    info.client.user = MagicMock(id=999)
    me = info.guild.me
    for key, val in perm_flags.items():
        setattr(me.guild_permissions, key, val)
    info.guild.get_member = MagicMock(return_value=me)
    return me


async def test_require_moderate_members_no_guild():
    from utility import CommandInfo

    info = CommandInfo(
        user=make_member(),
        guild=None,
        channel=make_text_channel(),
        locale="en-US",
        client=MagicMock(),
        command=MagicMock(),
        message=None,
        permissions=MagicMock(),
        reply=AsyncMock(),
    )
    assert await common.require_moderate_members(info, "pfx") is True


async def test_require_moderate_members_denied():
    perms = make_permissions(moderate_members=False)
    guild = make_guild()
    channel = make_text_channel(guild=guild)
    channel.permissions_for = MagicMock(return_value=perms)
    user = make_member()
    user.guild_permissions = perms
    info = make_command_info(user=user, guild=guild, channel=channel, reply=AsyncMock())
    assert await common.require_moderate_members(info, "pfx") is True
    info.reply.assert_awaited_once()


async def test_require_moderate_members_ok(admin_command_info):
    assert await common.require_moderate_members(admin_command_info, "pfx") is False


async def test_require_bot_permissions_no_client_user(admin_command_info):
    admin_command_info.client.user = None
    channel = make_text_channel(guild=admin_command_info.guild)
    assert await common.require_bot_permissions(admin_command_info, channel) is True


async def test_require_bot_permissions_no_self_member(admin_command_info):
    admin_command_info.client.user = MagicMock(id=999)
    admin_command_info.guild.get_member = MagicMock(return_value=None)
    channel = make_text_channel(guild=admin_command_info.guild)
    assert await common.require_bot_permissions(admin_command_info, channel) is True


@pytest.mark.parametrize(
    "flags",
    [
        {"send_messages": False},
        {"manage_messages": False},
        {"read_messages": False},
        {"view_channel": False},
    ],
)
async def test_require_bot_permissions_each_failure(admin_command_info, flags):
    _bot_member(admin_command_info, send_messages=True, manage_messages=True, read_messages=True, view_channel=True)
    channel = make_text_channel(guild=admin_command_info.guild)
    base = make_permissions(send_messages=True, manage_messages=True, read_messages=True, view_channel=True)
    for key, val in flags.items():
        setattr(base, key, val)
    channel.permissions_for = MagicMock(return_value=base)
    assert await common.require_bot_permissions(admin_command_info, channel) is True
    admin_command_info.reply.assert_awaited_once()


async def test_require_bot_permissions_ok(admin_command_info):
    _bot_member(admin_command_info)
    channel = make_text_channel(guild=admin_command_info.guild)
    channel.permissions_for = MagicMock(
        return_value=make_permissions(send_messages=True, manage_messages=True, read_messages=True, view_channel=True)
    )
    assert await common.require_bot_permissions(admin_command_info, channel) is False


async def test_require_counting_channel_missing(admin_command_info):
    with patch("commands.minigames._counting_common.tanjunEmbed", return_value=MagicMock()):
        result = await common.require_counting_channel(admin_command_info, 1, AsyncMock(return_value=None), "pfx")
    assert result is None
    admin_command_info.reply.assert_awaited_once()


async def test_require_counting_channel_found(admin_command_info):
    result = await common.require_counting_channel(admin_command_info, 1, AsyncMock(return_value=7), "pfx")
    assert result == 7


@pytest.mark.parametrize("progress", [-1, 2_000_000_000])
async def test_require_valid_progress_invalid(admin_command_info, progress):
    assert await common.require_valid_progress(admin_command_info, progress, "pfx") is True
    admin_command_info.reply.assert_awaited_once()


async def test_require_valid_progress_ok(admin_command_info):
    assert await common.require_valid_progress(admin_command_info, 10, "pfx") is False
