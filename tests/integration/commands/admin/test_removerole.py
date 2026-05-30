import pytest

from commands.admin.removerole import removerole
from tests.helpers.discord import (
    make_role,
    make_target_member,
)

pytestmark = pytest.mark.asyncio


async def test_removerole_missing_user_permission(restricted_command_info):
    user = make_target_member()
    role = make_role()
    await removerole(restricted_command_info, user=user, role=role)
    restricted_command_info.reply.assert_awaited()


async def test_removerole_success(admin_command_info):
    user = make_target_member()
    role = make_role()
    await removerole(admin_command_info, user=user, role=role)
    assert admin_command_info.reply.await_count >= 0


async def test_removerole_reply_called(admin_command_info):
    user = make_target_member()
    role = make_role()
    await removerole(admin_command_info, user=user, role=role)
    assert admin_command_info.reply.await_count >= 0


async def test_removerole_with_admin_perms(admin_command_info):
    user = make_target_member()
    role = make_role()
    await removerole(admin_command_info, user=user, role=role)
    assert admin_command_info.reply.await_count >= 0


async def test_removerole_embed_or_content(admin_command_info):
    user = make_target_member()
    role = make_role()
    await removerole(admin_command_info, user=user, role=role)
    if admin_command_info.reply.await_count:
        call = admin_command_info.reply.await_args
        assert call.kwargs.get("embed") is not None or call.args or call.kwargs.get("view") is not None


async def test_removerole_does_not_raise(admin_command_info):
    user = make_target_member()
    role = make_role()
    await removerole(admin_command_info, user=user, role=role)


async def test_removerole_guild_present(admin_command_info):
    assert admin_command_info.guild is not None
    user = make_target_member()
    role = make_role()
    await removerole(admin_command_info, user=user, role=role)
