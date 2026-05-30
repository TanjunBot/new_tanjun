from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import discord
import pytest

from commands.utility.twitch.see_twitch_live_notifications import seeTwitchLiveNotifications
from tests.helpers.discord import make_permissions, make_target_member
from tests.integration.commands.admin.conftest import make_view_interaction


pytestmark = pytest.mark.asyncio


def _notification(nid: str = "111", twitch_name: str = "streamer") -> MagicMock:
    n = MagicMock()
    n.id = nid
    n.twitch_name = twitch_name
    n.notification_message = "Live now!"
    return n


def _view_from_reply(info):
    _, kwargs = info.reply.await_args
    return kwargs.get("view")


@patch("commands.utility.twitch.see_twitch_live_notifications.isinstance")
async def test_see_twitch_no_admin(mock_isinstance, admin_command_info):
    mock_isinstance.side_effect = lambda obj, cls: cls is discord.Member or cls is discord.abc.GuildChannel
    perms = make_permissions(administrator=False)
    admin_command_info.channel.permissions_for = MagicMock(return_value=perms)
    await seeTwitchLiveNotifications(admin_command_info)
    admin_command_info.reply.assert_awaited_once()


@patch("commands.utility.twitch.see_twitch_live_notifications.get_twitch_service", return_value=None)
async def test_see_twitch_service_unavailable(mock_svc, admin_command_info):
    await seeTwitchLiveNotifications(admin_command_info)
    admin_command_info.reply.assert_awaited_once()


@patch("commands.utility.twitch.see_twitch_live_notifications.get_twitch_service")
async def test_see_twitch_no_notifications(mock_get, admin_command_info):
    svc = MagicMock()
    svc.get_notifications_by_guild = AsyncMock(return_value=[])
    mock_get.return_value = svc
    await seeTwitchLiveNotifications(admin_command_info)
    admin_command_info.reply.assert_awaited_once()


@patch("commands.utility.twitch.see_twitch_live_notifications.parse_twitch_notification_message", return_value="parsed")
@patch("commands.utility.twitch.see_twitch_live_notifications.get_twitch_service")
async def test_see_twitch_single_notification(mock_get, mock_parse, admin_command_info):
    svc = MagicMock()
    svc.get_notifications_by_guild = AsyncMock(return_value=[_notification()])
    mock_get.return_value = svc
    await seeTwitchLiveNotifications(admin_command_info)
    admin_command_info.reply.assert_awaited_once()
    assert _view_from_reply(admin_command_info) is not None


@patch("commands.utility.twitch.see_twitch_live_notifications.parse_twitch_notification_message", return_value="parsed")
@patch("commands.utility.twitch.see_twitch_live_notifications.get_twitch_service")
async def test_see_twitch_pagination_and_delete(mock_get, mock_parse, admin_command_info):
    svc = MagicMock()
    notes = [_notification("111"), _notification("222")]
    svc.get_notifications_by_guild = AsyncMock(return_value=notes)
    svc.remove_notification = AsyncMock()
    mock_get.return_value = svc

    await seeTwitchLiveNotifications(admin_command_info)
    view = _view_from_reply(admin_command_info)

    next_interaction = make_view_interaction(admin_command_info.user)
    next_interaction.response.edit_message = AsyncMock()
    await view.next_page(next_interaction, MagicMock())
    next_interaction.response.edit_message.assert_awaited_once()

    prev_interaction = make_view_interaction(admin_command_info.user)
    prev_interaction.response.edit_message = AsyncMock()
    await view.previous_page(prev_interaction, MagicMock())
    prev_interaction.response.edit_message.assert_awaited_once()

    wrong = make_view_interaction(make_target_member(user_id=99999))
    await view.next_page(wrong, MagicMock())
    wrong.response.send_message.assert_awaited_once()

    wrong_del = make_view_interaction(make_target_member(user_id=99999))
    await view.delete_notification(wrong_del, MagicMock())
    wrong_del.response.send_message.assert_awaited_once()

    svc.get_notifications_by_guild = AsyncMock(return_value=[])
    del_interaction = make_view_interaction(admin_command_info.user)
    del_interaction.response.edit_message = AsyncMock()
    await view.delete_notification(del_interaction, MagicMock())
    svc.remove_notification.assert_awaited_once()
    del_interaction.response.edit_message.assert_awaited_once()

    with patch("commands.utility.twitch.see_twitch_live_notifications.get_twitch_service", return_value=None):
        none_interaction = make_view_interaction(admin_command_info.user)
        await view.delete_notification(none_interaction, MagicMock())
        none_interaction.response.send_message.assert_awaited_once()
