import pytest
from unittest.mock import AsyncMock, MagicMock
import discord

from commands.admin.say import say
from tests.helpers.discord import make_permissions, make_text_channel


pytestmark = pytest.mark.asyncio


async def test_say_missing_permission(restricted_command_info):
    channel = make_text_channel(guild=restricted_command_info.guild)
    await say(restricted_command_info, channel, message="hello")
    restricted_command_info.reply.assert_awaited_once()


async def test_say_missing_bot_permission(admin_command_info):
    channel = make_text_channel(guild=admin_command_info.guild)
    channel.permissions_for = MagicMock(return_value=make_permissions(send_messages=False))
    await say(admin_command_info, channel, message="hello")
    admin_command_info.reply.assert_awaited_once()


async def test_say_success(admin_command_info):
    channel = make_text_channel(guild=admin_command_info.guild)
    channel.permissions_for = MagicMock(return_value=make_permissions(send_messages=True))
    await say(admin_command_info, channel, message="hello world")
    channel.send.assert_awaited_once_with("hello world")
    admin_command_info.reply.assert_awaited_once()


async def test_say_http_exception(admin_command_info):
    import discord as discord_mod

    channel = make_text_channel(guild=admin_command_info.guild)
    channel.permissions_for = MagicMock(return_value=make_permissions(send_messages=True))
    channel.send = AsyncMock(side_effect=discord_mod.HTTPException(MagicMock(), "fail"))
    await say(admin_command_info, channel, message="hello")
    admin_command_info.reply.assert_awaited_once()


async def test_say_sends_to_target_channel(admin_command_info):
    channel = make_text_channel(guild=admin_command_info.guild, channel_id=999)
    channel.permissions_for = MagicMock(return_value=make_permissions(send_messages=True))
    await say(admin_command_info, channel, message="test")
    channel.send.assert_awaited_once()


async def test_say_reply_has_embed(admin_command_info):
    channel = make_text_channel(guild=admin_command_info.guild)
    channel.permissions_for = MagicMock(return_value=make_permissions(send_messages=True))
    await say(admin_command_info, channel, message="hi")
    assert "embed" in admin_command_info.reply.await_args.kwargs
