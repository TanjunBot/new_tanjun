from unittest.mock import AsyncMock, MagicMock, patch

import discord
import pytest

from commands.admin.lock import lock_channel
from commands.admin.nickname import change_nickname
from commands.admin.nuke import nuke_channel
from commands.admin.purge import purge
from commands.admin.removerole import removerole
from commands.admin.removetimeout import remove_timeout
from commands.admin.slowmode import set_slowmode
from commands.admin.unlock import unlock_channel
from localizer import tanjunLocalizer
from tests.helpers.db import AsyncIter
from tests.helpers.discord import (
    make_permissions,
    make_role,
    make_target_member,
    make_text_channel,
)
from tests.integration.commands.admin.conftest import make_view_interaction

pytestmark = pytest.mark.asyncio


def _role_overwrite():
    ow = MagicMock()
    ow._values = {"send_messages": True, "read_messages": True}
    ow.send_messages = True
    return ow


@patch("commands.admin.lock.save_channel_overwrites", new_callable=AsyncMock)
@patch("commands.admin.lock.clear_channel_overwrites", new_callable=AsyncMock)
async def test_lock_channel_success_with_overwrites(mock_clear, mock_save, admin_command_info):
    channel = make_text_channel(guild=admin_command_info.guild)
    role = make_role(position=1)
    channel.overwrites = {role: _role_overwrite()}
    channel.overwrites_for = MagicMock(return_value=_role_overwrite())
    await lock_channel(admin_command_info, channel=channel)
    mock_clear.assert_awaited_once()
    mock_save.assert_awaited()
    channel.set_permissions.assert_awaited()
    channel.send.assert_awaited_once()
    admin_command_info.reply.assert_awaited_once()


@patch("commands.admin.lock.clear_channel_overwrites", new_callable=AsyncMock)
async def test_lock_channel_default_channel(mock_clear, admin_command_info):
    admin_command_info.channel.overwrites = {}
    admin_command_info.channel.overwrites_for = MagicMock(return_value=_role_overwrite())
    await lock_channel(admin_command_info)
    mock_clear.assert_awaited_once()


async def test_lock_channel_missing_bot_permission(admin_command_info):
    channel = make_text_channel(guild=admin_command_info.guild)
    channel.permissions_for = MagicMock(return_value=make_permissions(manage_channels=False))
    await lock_channel(admin_command_info, channel=channel)
    admin_command_info.reply.assert_awaited_once()


@patch(
    "commands.admin.lock.clear_channel_overwrites", new_callable=AsyncMock, side_effect=discord.Forbidden(MagicMock(), "nope")
)
async def test_lock_channel_forbidden(mock_clear, admin_command_info):
    channel = make_text_channel(guild=admin_command_info.guild)
    channel.overwrites = {}
    channel.overwrites_for = MagicMock(return_value=_role_overwrite())
    await lock_channel(admin_command_info, channel=channel)
    admin_command_info.reply.assert_awaited_once()


@patch(
    "commands.admin.lock.clear_channel_overwrites",
    new_callable=AsyncMock,
    side_effect=discord.HTTPException(MagicMock(), "err"),
)
async def test_lock_channel_http_error(mock_clear, admin_command_info):
    channel = make_text_channel(guild=admin_command_info.guild)
    channel.overwrites = {}
    channel.overwrites_for = MagicMock(return_value=_role_overwrite())
    await lock_channel(admin_command_info, channel=channel)
    admin_command_info.reply.assert_awaited_once()


@patch("commands.admin.unlock.clear_channel_overwrites", new_callable=AsyncMock)
@patch("commands.admin.unlock.get_channel_overwrites")
async def test_unlock_channel_success(mock_get, mock_clear, admin_command_info):
    channel = make_text_channel(guild=admin_command_info.guild)
    role = make_role(role_id=777777777)
    channel.guild.get_role = MagicMock(return_value=role)
    overwrite = MagicMock()
    overwrite.role_id = "777777777"
    overwrite.overwrites = {"send_messages": True}
    mock_get.return_value = AsyncIter([overwrite])
    await unlock_channel(admin_command_info, channel=channel)
    channel.set_permissions.assert_awaited()
    channel.send.assert_awaited_once()
    admin_command_info.reply.assert_awaited_once()


@patch("commands.admin.unlock.get_channel_overwrites")
async def test_unlock_channel_not_locked(mock_get, admin_command_info):
    channel = make_text_channel(guild=admin_command_info.guild)
    mock_get.return_value = AsyncIter([])
    await unlock_channel(admin_command_info, channel=channel)
    admin_command_info.reply.assert_awaited_once()


async def test_unlock_channel_missing_bot_permission(admin_command_info):
    channel = make_text_channel(guild=admin_command_info.guild)
    channel.permissions_for = MagicMock(return_value=make_permissions(manage_channels=False))
    await unlock_channel(admin_command_info, channel=channel)
    admin_command_info.reply.assert_awaited_once()


@patch("commands.admin.unlock.get_channel_overwrites")
async def test_unlock_channel_forbidden(mock_get, admin_command_info):
    channel = make_text_channel(guild=admin_command_info.guild)
    role = make_role(role_id=777777777)
    channel.guild.get_role = MagicMock(return_value=role)
    overwrite = MagicMock()
    overwrite.role_id = "777777777"
    overwrite.overwrites = {"send_messages": True}
    mock_get.return_value = AsyncIter([overwrite])
    channel.set_permissions = AsyncMock(side_effect=discord.Forbidden(MagicMock(), "nope"))
    await unlock_channel(admin_command_info, channel=channel)
    admin_command_info.reply.assert_awaited_once()


@patch("commands.admin.unlock.get_channel_overwrites")
async def test_unlock_channel_http_error(mock_get, admin_command_info):
    channel = make_text_channel(guild=admin_command_info.guild)
    role = make_role(role_id=777777777)
    channel.guild.get_role = MagicMock(return_value=role)
    overwrite = MagicMock()
    overwrite.role_id = "777777777"
    overwrite.overwrites = {"send_messages": True}
    mock_get.return_value = AsyncIter([overwrite])
    channel.set_permissions = AsyncMock(side_effect=discord.HTTPException(MagicMock(), "err"))
    await unlock_channel(admin_command_info, channel=channel)
    admin_command_info.reply.assert_awaited_once()


async def test_unlock_channel_default_channel(admin_command_info):
    with patch("commands.admin.unlock.get_channel_overwrites", return_value=AsyncIter([])):
        await unlock_channel(admin_command_info)
    admin_command_info.reply.assert_awaited_once()


async def test_nickname_missing_bot_permission(admin_command_info):
    admin_command_info.guild.me.guild_permissions = make_permissions(manage_nicknames=False)
    member = make_target_member(top_role_position=1)
    await change_nickname(admin_command_info, member=member, nickname="new")
    admin_command_info.reply.assert_awaited_once()


async def test_nickname_target_too_high(admin_command_info):
    member = make_target_member(top_role_position=200)
    admin_command_info.user.top_role.position = 1
    await change_nickname(admin_command_info, member=member, nickname="new")
    admin_command_info.reply.assert_awaited_once()


async def test_nickname_success(admin_command_info):
    member = make_target_member(top_role_position=1)
    member.nick = "old"
    await change_nickname(admin_command_info, member=member, nickname="newnick")
    member.edit.assert_awaited_once_with(nick="newnick")
    admin_command_info.reply.assert_awaited_once()


async def test_nickname_remove(admin_command_info):
    member = make_target_member(top_role_position=1)
    member.nick = "oldnick"
    await change_nickname(admin_command_info, member=member, nickname=None)
    member.edit.assert_awaited_once_with(nick=None)
    admin_command_info.reply.assert_awaited_once()


async def test_nickname_forbidden(admin_command_info):
    member = make_target_member(top_role_position=1)
    member.edit = AsyncMock(side_effect=discord.Forbidden(MagicMock(), "nope"))
    await change_nickname(admin_command_info, member=member, nickname="x")
    admin_command_info.reply.assert_awaited_once()


async def test_nickname_http_error(admin_command_info):
    member = make_target_member(top_role_position=1)
    member.edit = AsyncMock(side_effect=discord.HTTPException(MagicMock(), "err"))
    await change_nickname(admin_command_info, member=member, nickname="x")
    admin_command_info.reply.assert_awaited_once()


async def test_nuke_missing_bot_permission(admin_command_info):
    admin_command_info.guild.me.guild_permissions = make_permissions(manage_channels=False)
    channel = make_text_channel(guild=admin_command_info.guild)
    await nuke_channel(admin_command_info, channel=channel)
    admin_command_info.reply.assert_awaited_once()


async def test_nuke_view_timeout(admin_command_info):
    channel = make_text_channel(guild=admin_command_info.guild)
    admin_command_info.channel.send = AsyncMock()
    await nuke_channel(admin_command_info, channel=channel)
    admin_command_info.channel.send.assert_awaited()


async def test_nuke_cancelled(admin_command_info):
    channel = make_text_channel(guild=admin_command_info.guild)
    call = admin_command_info.reply
    captured_view = {}

    async def capture(*args, **kwargs):
        view = kwargs.get("view")
        if view:
            captured_view["view"] = view
            view.value = False
            view.wait = AsyncMock()
        return MagicMock()

    admin_command_info.reply = AsyncMock(side_effect=capture)
    await nuke_channel(admin_command_info, channel=channel)
    assert "view" in captured_view


async def test_nuke_wrong_confirmation(admin_command_info):
    channel = make_text_channel(guild=admin_command_info.guild)
    admin_command_info.channel.send = AsyncMock()

    async def capture(*args, **kwargs):
        view = kwargs.get("view")
        if view:
            view.value = True
            view.wait = AsyncMock()
        return MagicMock()

    admin_command_info.reply = AsyncMock(side_effect=capture)
    admin_command_info.client.wait_for = AsyncMock(
        return_value=MagicMock(content="wrongword", author=admin_command_info.user, channel=admin_command_info.channel)
    )
    await nuke_channel(admin_command_info, channel=channel)
    admin_command_info.channel.send.assert_awaited()


async def test_nuke_wait_for_timeout(admin_command_info):
    channel = make_text_channel(guild=admin_command_info.guild)
    admin_command_info.channel.send = AsyncMock()

    async def capture(*args, **kwargs):
        view = kwargs.get("view")
        if view:
            view.value = True
            view.wait = AsyncMock()
        return MagicMock()

    admin_command_info.reply = AsyncMock(side_effect=capture)
    admin_command_info.client.wait_for = AsyncMock(side_effect=TimeoutError())
    await nuke_channel(admin_command_info, channel=channel)
    admin_command_info.channel.send.assert_awaited()


async def test_nuke_clone_forbidden(admin_command_info):
    channel = make_text_channel(guild=admin_command_info.guild)
    admin_command_info.channel.send = AsyncMock()
    channel.clone = AsyncMock(side_effect=discord.Forbidden(MagicMock(), "nope"))

    async def capture(*args, **kwargs):
        view = kwargs.get("view")
        if view:
            view.value = True
            view.wait = AsyncMock()
        return MagicMock()

    admin_command_info.reply = AsyncMock(side_effect=capture)
    word = tanjunLocalizer.localize(str(admin_command_info.locale), "commands.admin.nuke.confirmationWord")
    admin_command_info.client.wait_for = AsyncMock(
        return_value=MagicMock(content=word, author=admin_command_info.user, channel=admin_command_info.channel)
    )
    await nuke_channel(admin_command_info, channel=channel)
    admin_command_info.channel.send.assert_awaited()


async def test_nuke_clone_http_error(admin_command_info):
    channel = make_text_channel(guild=admin_command_info.guild)
    admin_command_info.channel.send = AsyncMock()
    channel.clone = AsyncMock(side_effect=discord.HTTPException(MagicMock(), "err"))

    async def capture(*args, **kwargs):
        view = kwargs.get("view")
        if view:
            view.value = True
            view.wait = AsyncMock()
        return MagicMock()

    admin_command_info.reply = AsyncMock(side_effect=capture)
    word = tanjunLocalizer.localize(str(admin_command_info.locale), "commands.admin.nuke.confirmationWord")
    admin_command_info.client.wait_for = AsyncMock(
        return_value=MagicMock(content=word, author=admin_command_info.user, channel=admin_command_info.channel)
    )
    await nuke_channel(admin_command_info, channel=channel)
    admin_command_info.channel.send.assert_awaited()


async def test_nuke_clone_not_found(admin_command_info):
    channel = make_text_channel(guild=admin_command_info.guild)
    admin_command_info.channel.send = AsyncMock()
    channel.clone = AsyncMock(side_effect=discord.NotFound(MagicMock(), "missing"))

    async def capture(*args, **kwargs):
        view = kwargs.get("view")
        if view:
            view.value = True
            view.wait = AsyncMock()
        return MagicMock()

    admin_command_info.reply = AsyncMock(side_effect=capture)
    word = tanjunLocalizer.localize(str(admin_command_info.locale), "commands.admin.nuke.confirmationWord")
    admin_command_info.client.wait_for = AsyncMock(
        return_value=MagicMock(content=word, author=admin_command_info.user, channel=admin_command_info.channel)
    )
    await nuke_channel(admin_command_info, channel=channel)
    admin_command_info.channel.send.assert_awaited()


async def test_nuke_success_clone(admin_command_info):
    channel = make_text_channel(guild=admin_command_info.guild)
    new_channel = make_text_channel(guild=admin_command_info.guild)
    channel.clone = AsyncMock(return_value=new_channel)
    channel.delete = AsyncMock()
    new_channel.send = AsyncMock()

    async def capture(*args, **kwargs):
        view = kwargs.get("view")
        if view:
            view.value = True
            view.wait = AsyncMock()
        return MagicMock()

    admin_command_info.reply = AsyncMock(side_effect=capture)
    word = tanjunLocalizer.localize(str(admin_command_info.locale), "commands.admin.nuke.confirmationWord")
    admin_command_info.client.wait_for = AsyncMock(
        return_value=MagicMock(content=word, author=admin_command_info.user, channel=admin_command_info.channel)
    )
    await nuke_channel(admin_command_info, channel=channel)
    channel.delete.assert_awaited_once()
    new_channel.send.assert_awaited_once()


async def test_nuke_unauthorized_interaction(admin_command_info):
    channel = make_text_channel(guild=admin_command_info.guild)
    captured = {}

    async def capture(*args, **kwargs):
        view = kwargs.get("view")
        if view:
            captured["view"] = view
        return MagicMock()

    admin_command_info.reply = AsyncMock(side_effect=capture)
    await nuke_channel(admin_command_info, channel=channel)
    view = captured["view"]
    interaction = make_view_interaction(user=make_target_member(user_id=999999999))
    result = await view.interaction_check(interaction)
    assert result is False


async def test_nuke_confirm_button(admin_command_info):
    channel = make_text_channel(guild=admin_command_info.guild)
    captured = {}

    async def capture(*args, **kwargs):
        view = kwargs.get("view")
        if view:
            captured["view"] = view
            view.wait = AsyncMock()
            view.value = False
        return MagicMock()

    admin_command_info.reply = AsyncMock(side_effect=capture)
    await nuke_channel(admin_command_info, channel=channel)
    view = captured["view"]
    view.command_info = admin_command_info
    interaction = make_view_interaction(user=admin_command_info.user)
    button = MagicMock()
    await view.confirm(interaction, button)
    assert view.value is True
    interaction.response.send_message.assert_awaited_once()


async def test_nuke_cancel_button(admin_command_info):
    channel = make_text_channel(guild=admin_command_info.guild)
    captured = {}

    async def capture(*args, **kwargs):
        view = kwargs.get("view")
        if view:
            captured["view"] = view
            view.wait = AsyncMock()
        return MagicMock()

    admin_command_info.reply = AsyncMock(side_effect=capture)
    await nuke_channel(admin_command_info, channel=channel)
    view = captured["view"]
    interaction = make_view_interaction(user=admin_command_info.user)
    await view.cancel(interaction, MagicMock())
    assert view.value is False


async def test_nuke_view_on_timeout(admin_command_info):
    channel = make_text_channel(guild=admin_command_info.guild)
    captured = {}

    async def capture(*args, **kwargs):
        view = kwargs.get("view")
        if view:
            captured["view"] = view
            view.wait = AsyncMock()
        msg = MagicMock()
        msg.edit = AsyncMock()
        view.message = msg
        return msg

    admin_command_info.reply = AsyncMock(side_effect=capture)
    await nuke_channel(admin_command_info, channel=channel)
    view = captured["view"]
    await view.on_timeout()
    view.message.edit.assert_awaited_once()


@pytest.mark.parametrize(
    "setting",
    [
        "all",
        "bot",
        "user",
        "notPinned",
        "userNotPinned",
        "botNotPinned",
        "notAdmin",
        "userNotAdmin",
        "embeds",
        "files",
        "notAdminNotPinned",
    ],
)
async def test_purge_settings(admin_command_info, setting):
    admin_command_info.channel.purge = AsyncMock(return_value=[MagicMock()] * 3)
    await purge(admin_command_info, 5, setting=setting)
    admin_command_info.reply.assert_awaited_once()
    check_fn = admin_command_info.channel.purge.await_args.kwargs["check"]
    msg = MagicMock()
    msg.author.bot = False
    msg.pinned = False
    msg.embeds = [MagicMock()]
    msg.attachments = [MagicMock()]
    msg.author.guild_permissions = make_permissions(administrator=False)
    check_fn(msg)


async def test_purge_default_channel(admin_command_info):
    admin_command_info.channel.purge = AsyncMock(return_value=[])
    await purge(admin_command_info, 5)
    admin_command_info.reply.assert_awaited_once()


async def test_removerole_missing_bot_permission(admin_command_info):
    admin_command_info.guild.me.guild_permissions = make_permissions(manage_roles=False)
    user = make_target_member()
    role = make_role(position=1)
    await removerole(admin_command_info, user=user, role=role)
    admin_command_info.reply.assert_awaited_once()


async def test_removerole_user_lacks_role(admin_command_info):
    user = make_target_member()
    role = make_role(position=1)
    user.roles = []
    await removerole(admin_command_info, user=user, role=role)
    admin_command_info.reply.assert_awaited_once()


async def test_removerole_role_too_high_user(admin_command_info):
    user = make_target_member()
    role = make_role(position=50)
    user.roles = [role]
    admin_command_info.user.top_role.position = 10
    await removerole(admin_command_info, user=user, role=role)
    admin_command_info.reply.assert_awaited_once()


async def test_removerole_role_too_high_bot(admin_command_info):
    user = make_target_member()
    role = make_role(position=200)
    user.roles = [role]
    admin_command_info.guild.me.top_role.position = 50
    await removerole(admin_command_info, user=user, role=role)
    admin_command_info.reply.assert_awaited_once()


async def test_removerole_success(admin_command_info):
    user = make_target_member()
    role = make_role(position=1)
    user.roles = [role]
    await removerole(admin_command_info, user=user, role=role)
    user.remove_roles.assert_awaited_once_with(role)
    admin_command_info.reply.assert_awaited_once()


async def test_removerole_multiple_mode(admin_command_info):
    await removerole(admin_command_info)
    call = admin_command_info.reply.await_args
    assert call.kwargs.get("view") is not None


async def test_removerole_view_confirm_no_selection(admin_command_info):
    await removerole(admin_command_info)
    view = admin_command_info.reply.await_args.kwargs["view"]
    view.command_info = admin_command_info
    interaction = make_view_interaction(user=admin_command_info.user)
    await view.confirm(interaction, MagicMock())
    interaction.response.send_message.assert_awaited_once()


async def test_removerole_view_confirm_success(admin_command_info):
    await removerole(admin_command_info)
    view = admin_command_info.reply.await_args.kwargs["view"]
    view.command_info = admin_command_info
    user = make_target_member()
    role = make_role(position=1)
    user.roles = [role]
    view.selected_users = [user]
    view.selected_roles = [role]
    interaction = make_view_interaction(user=admin_command_info.user)
    await view.confirm(interaction, MagicMock())
    user.remove_roles.assert_awaited_once_with(role)


async def test_removerole_view_cancel(admin_command_info):
    await removerole(admin_command_info)
    view = admin_command_info.reply.await_args.kwargs["view"]
    view.command_info = admin_command_info
    interaction = make_view_interaction(user=admin_command_info.user)
    await view.cancel(interaction, MagicMock())
    interaction.response.edit_message.assert_awaited_once()


async def test_removerole_view_role_select_missing_guild(admin_command_info):
    await removerole(admin_command_info)
    view = admin_command_info.reply.await_args.kwargs["view"]
    view.command_info = admin_command_info
    interaction = make_view_interaction(user=admin_command_info.user)
    interaction.guild = None
    interaction.data = {"component_type": 6, "values": ["888888888"]}
    with pytest.raises(ValueError):
        await view.interaction_check(interaction)


async def test_removerole_missing_guild_raises(admin_command_info):
    admin_command_info.guild = None
    with pytest.raises(ValueError):
        await removerole(admin_command_info, user=make_target_member(), role=make_role())


async def test_removerole_view_role_select(admin_command_info):
    await removerole(admin_command_info)
    view = admin_command_info.reply.await_args.kwargs["view"]
    role = make_role(role_id=888888888)
    interaction = make_view_interaction(user=admin_command_info.user, guild=admin_command_info.guild)
    interaction.data = {"component_type": 6, "values": ["888888888"]}
    interaction.guild.get_role = MagicMock(return_value=role)
    await view.interaction_check(interaction)
    assert view.selected_roles == [role]


async def test_removerole_view_user_select(admin_command_info):
    await removerole(admin_command_info)
    view = admin_command_info.reply.await_args.kwargs["view"]
    member = make_target_member(user_id=777777777)
    interaction = make_view_interaction(user=admin_command_info.user, guild=admin_command_info.guild)
    interaction.data = {"component_type": 5, "values": ["777777777"]}
    interaction.guild.fetch_member = AsyncMock(return_value=member)
    await view.interaction_check(interaction)
    assert view.selected_users == [member]


async def test_removerole_view_on_error(admin_command_info):
    await removerole(admin_command_info)
    view = admin_command_info.reply.await_args.kwargs["view"]
    view.command_info = admin_command_info
    interaction = make_view_interaction(user=admin_command_info.user)
    await view.on_error(interaction, RuntimeError("x"), MagicMock())
    interaction.response.send_message.assert_awaited_once()


async def test_remove_timeout_not_timed_out(admin_command_info):
    target = make_target_member(top_role_position=1)
    target.is_timed_out = MagicMock(return_value=False)
    await remove_timeout(admin_command_info, target)
    admin_command_info.reply.assert_awaited_once()


async def test_remove_timeout_success_no_reason(admin_command_info):
    target = make_target_member(top_role_position=1)
    target.is_timed_out = MagicMock(return_value=True)
    await remove_timeout(admin_command_info, target)
    target.timeout.assert_awaited_once_with(None, reason=None)
    admin_command_info.reply.assert_awaited_once()


async def test_slowmode_missing_bot_permission(admin_command_info):
    channel = make_text_channel(guild=admin_command_info.guild)
    channel.permissions_for = MagicMock(return_value=make_permissions(manage_channels=False))
    await set_slowmode(admin_command_info, seconds=10, channel=channel)
    admin_command_info.reply.assert_awaited_once()


@pytest.mark.parametrize("seconds", [-1, 30000])
async def test_slowmode_invalid_duration(admin_command_info, seconds):
    channel = make_text_channel(guild=admin_command_info.guild)
    await set_slowmode(admin_command_info, seconds=seconds, channel=channel)
    admin_command_info.reply.assert_awaited_once()


async def test_slowmode_disabled(admin_command_info):
    channel = make_text_channel(guild=admin_command_info.guild)
    await set_slowmode(admin_command_info, seconds=0, channel=channel)
    channel.edit.assert_awaited_once_with(slowmode_delay=0)
    admin_command_info.reply.assert_awaited_once()


async def test_slowmode_enabled(admin_command_info):
    channel = make_text_channel(guild=admin_command_info.guild)
    await set_slowmode(admin_command_info, seconds=30, channel=channel)
    channel.edit.assert_awaited_once_with(slowmode_delay=30)
    admin_command_info.reply.assert_awaited_once()


async def test_slowmode_default_channel(admin_command_info):
    await set_slowmode(admin_command_info, seconds=5)
    admin_command_info.channel.edit.assert_awaited_once_with(slowmode_delay=5)


async def test_slowmode_forbidden(admin_command_info):
    channel = make_text_channel(guild=admin_command_info.guild)
    channel.edit = AsyncMock(side_effect=discord.Forbidden(MagicMock(), "nope"))
    await set_slowmode(admin_command_info, seconds=5, channel=channel)
    admin_command_info.reply.assert_awaited_once()


async def test_slowmode_http_error(admin_command_info):
    channel = make_text_channel(guild=admin_command_info.guild)
    channel.edit = AsyncMock(side_effect=discord.HTTPException(MagicMock(), "err"))
    await set_slowmode(admin_command_info, seconds=5, channel=channel)
    admin_command_info.reply.assert_awaited_once()
