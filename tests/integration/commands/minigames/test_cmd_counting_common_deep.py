from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from commands.minigames import _counting_common as common
from tests.helpers.discord import make_command_info, make_member, make_permissions, make_text_channel


pytestmark = pytest.mark.asyncio


async def test_require_moderate_members_no_guild(admin_command_info):
    admin_command_info.guild = None
    admin_command_info.reply = AsyncMock()
    assert await common.require_moderate_members(admin_command_info, "prefix") is True
    admin_command_info.reply.assert_not_awaited()


async def test_require_bot_permissions_no_client_user():
    channel = make_text_channel()
    info = make_command_info(channel=channel, reply=AsyncMock())
    info.client.user = None
    assert await common.require_bot_permissions(info, channel) is True


async def test_require_bot_permissions_no_send():
    channel = make_text_channel()
    info = make_command_info(channel=channel, reply=AsyncMock())
    bot_member = make_member()
    perms = make_permissions(send_messages=False, manage_messages=True, read_messages=True, view_channel=True)
    channel.permissions_for = MagicMock(return_value=perms)
    info.guild.get_member = MagicMock(return_value=bot_member)
    assert await common.require_bot_permissions(info, channel) is True
    info.reply.assert_awaited_once()


async def test_require_bot_permissions_no_manage_messages():
    channel = make_text_channel()
    info = make_command_info(channel=channel, reply=AsyncMock())
    bot_member = make_member()
    perms = make_permissions(send_messages=True, manage_messages=False, read_messages=True, view_channel=True)
    channel.permissions_for = MagicMock(return_value=perms)
    info.guild.get_member = MagicMock(return_value=bot_member)
    assert await common.require_bot_permissions(info, channel) is True


async def test_require_bot_permissions_no_read():
    channel = make_text_channel()
    info = make_command_info(channel=channel, reply=AsyncMock())
    bot_member = make_member()
    perms = make_permissions(send_messages=True, manage_messages=True, read_messages=False, view_channel=True)
    channel.permissions_for = MagicMock(return_value=perms)
    info.guild.get_member = MagicMock(return_value=bot_member)
    assert await common.require_bot_permissions(info, channel) is True


async def test_require_bot_permissions_no_view():
    channel = make_text_channel()
    info = make_command_info(channel=channel, reply=AsyncMock())
    bot_member = make_member()
    perms = make_permissions(send_messages=True, manage_messages=True, read_messages=True, view_channel=False)
    channel.permissions_for = MagicMock(return_value=perms)
    info.guild.get_member = MagicMock(return_value=bot_member)
    assert await common.require_bot_permissions(info, channel) is True


async def test_require_counting_channel_missing():
    info = make_command_info(reply=AsyncMock())
    result = await common.require_counting_channel(info, 1, AsyncMock(return_value=None), "prefix")
    assert result is None
    info.reply.assert_awaited_once()


async def test_require_valid_progress_negative():
    info = make_command_info(reply=AsyncMock())
    assert await common.require_valid_progress(info, -1, "prefix") is True


async def test_require_valid_progress_too_high():
    info = make_command_info(reply=AsyncMock())
    assert await common.require_valid_progress(info, 2_000_000_000, "prefix") is True
