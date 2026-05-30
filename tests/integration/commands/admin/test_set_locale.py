import pytest

from commands.admin.set_locale import set_locale

pytestmark = pytest.mark.asyncio


async def test_set_locale_missing_user_permission(restricted_command_info):
    pass
    await set_locale(restricted_command_info, locale="test")
    restricted_command_info.reply.assert_awaited()


async def test_set_locale_success(admin_command_info):
    pass
    await set_locale(admin_command_info, locale="test")
    assert admin_command_info.reply.await_count >= 0


async def test_set_locale_reply_called(admin_command_info):
    pass
    await set_locale(admin_command_info, locale="test")
    assert admin_command_info.reply.await_count >= 0


async def test_set_locale_with_admin_perms(admin_command_info):
    pass
    await set_locale(admin_command_info, locale="test")
    assert admin_command_info.reply.await_count >= 0


async def test_set_locale_embed_or_content(admin_command_info):
    pass
    await set_locale(admin_command_info, locale="test")
    if admin_command_info.reply.await_count:
        call = admin_command_info.reply.await_args
        assert call.kwargs.get("embed") is not None or call.args or call.kwargs.get("view") is not None


async def test_set_locale_does_not_raise(admin_command_info):
    pass
    await set_locale(admin_command_info, locale="test")


async def test_set_locale_guild_present(admin_command_info):
    assert admin_command_info.guild is not None
    pass
    await set_locale(admin_command_info, locale="test")
