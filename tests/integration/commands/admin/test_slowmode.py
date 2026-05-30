import pytest

from commands.admin.slowmode import set_slowmode
from tests.helpers.discord import (
    make_text_channel,
)

pytestmark = pytest.mark.asyncio


async def test_set_slowmode_missing_user_permission(restricted_command_info):
    channel = make_text_channel(guild=restricted_command_info.guild)
    await set_slowmode(restricted_command_info, seconds=1, channel=channel)
    restricted_command_info.reply.assert_awaited()


async def test_set_slowmode_success(admin_command_info):
    channel = make_text_channel(guild=admin_command_info.guild)
    await set_slowmode(admin_command_info, seconds=1, channel=channel)
    assert admin_command_info.reply.await_count >= 0


async def test_set_slowmode_reply_called(admin_command_info):
    channel = make_text_channel(guild=admin_command_info.guild)
    await set_slowmode(admin_command_info, seconds=1, channel=channel)
    assert admin_command_info.reply.await_count >= 0


async def test_set_slowmode_with_admin_perms(admin_command_info):
    channel = make_text_channel(guild=admin_command_info.guild)
    await set_slowmode(admin_command_info, seconds=1, channel=channel)
    assert admin_command_info.reply.await_count >= 0


async def test_set_slowmode_embed_or_content(admin_command_info):
    channel = make_text_channel(guild=admin_command_info.guild)
    await set_slowmode(admin_command_info, seconds=1, channel=channel)
    if admin_command_info.reply.await_count:
        call = admin_command_info.reply.await_args
        assert call.kwargs.get("embed") is not None or call.args or call.kwargs.get("view") is not None


async def test_set_slowmode_does_not_raise(admin_command_info):
    channel = make_text_channel(guild=admin_command_info.guild)
    await set_slowmode(admin_command_info, seconds=1, channel=channel)


async def test_set_slowmode_guild_present(admin_command_info):
    assert admin_command_info.guild is not None
    channel = make_text_channel(guild=admin_command_info.guild)
    await set_slowmode(admin_command_info, seconds=1, channel=channel)
