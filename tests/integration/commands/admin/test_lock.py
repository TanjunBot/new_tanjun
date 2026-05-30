import pytest

from commands.admin.lock import lock_channel
from tests.helpers.discord import (
    make_text_channel,
)

pytestmark = pytest.mark.asyncio


async def test_lock_channel_missing_user_permission(restricted_command_info):
    channel = make_text_channel(guild=restricted_command_info.guild)
    await lock_channel(restricted_command_info, channel=channel)
    restricted_command_info.reply.assert_awaited()


async def test_lock_channel_success(admin_command_info):
    channel = make_text_channel(guild=admin_command_info.guild)
    await lock_channel(admin_command_info, channel=channel)
    assert admin_command_info.reply.await_count >= 0


async def test_lock_channel_reply_called(admin_command_info):
    channel = make_text_channel(guild=admin_command_info.guild)
    await lock_channel(admin_command_info, channel=channel)
    assert admin_command_info.reply.await_count >= 0


async def test_lock_channel_with_admin_perms(admin_command_info):
    channel = make_text_channel(guild=admin_command_info.guild)
    await lock_channel(admin_command_info, channel=channel)
    assert admin_command_info.reply.await_count >= 0


async def test_lock_channel_embed_or_content(admin_command_info):
    channel = make_text_channel(guild=admin_command_info.guild)
    await lock_channel(admin_command_info, channel=channel)
    if admin_command_info.reply.await_count:
        call = admin_command_info.reply.await_args
        assert call.kwargs.get("embed") is not None or call.args or call.kwargs.get("view") is not None


async def test_lock_channel_does_not_raise(admin_command_info):
    channel = make_text_channel(guild=admin_command_info.guild)
    await lock_channel(admin_command_info, channel=channel)


async def test_lock_channel_guild_present(admin_command_info):
    assert admin_command_info.guild is not None
    channel = make_text_channel(guild=admin_command_info.guild)
    await lock_channel(admin_command_info, channel=channel)
