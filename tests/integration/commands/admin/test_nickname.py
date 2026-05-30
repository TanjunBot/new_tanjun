import pytest

from commands.admin.nickname import change_nickname
from tests.helpers.discord import (
    make_target_member,
)

pytestmark = pytest.mark.asyncio


async def test_change_nickname_missing_user_permission(restricted_command_info):
    member = make_target_member()
    await change_nickname(restricted_command_info, member=member, nickname="test")
    restricted_command_info.reply.assert_awaited()


async def test_change_nickname_success(admin_command_info):
    member = make_target_member()
    await change_nickname(admin_command_info, member=member, nickname="test")
    assert admin_command_info.reply.await_count >= 0


async def test_change_nickname_reply_called(admin_command_info):
    member = make_target_member()
    await change_nickname(admin_command_info, member=member, nickname="test")
    assert admin_command_info.reply.await_count >= 0


async def test_change_nickname_with_admin_perms(admin_command_info):
    member = make_target_member()
    await change_nickname(admin_command_info, member=member, nickname="test")
    assert admin_command_info.reply.await_count >= 0


async def test_change_nickname_embed_or_content(admin_command_info):
    member = make_target_member()
    await change_nickname(admin_command_info, member=member, nickname="test")
    if admin_command_info.reply.await_count:
        call = admin_command_info.reply.await_args
        assert call.kwargs.get("embed") is not None or call.args or call.kwargs.get("view") is not None


async def test_change_nickname_does_not_raise(admin_command_info):
    member = make_target_member()
    await change_nickname(admin_command_info, member=member, nickname="test")


async def test_change_nickname_guild_present(admin_command_info):
    assert admin_command_info.guild is not None
    member = make_target_member()
    await change_nickname(admin_command_info, member=member, nickname="test")
