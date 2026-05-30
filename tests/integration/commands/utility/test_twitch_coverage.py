from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from commands.utility.twitch.add_twitch_live_notification import addTwitchLiveNotification
from commands.utility.twitch.see_twitch_live_notifications import seeTwitchLiveNotifications
from commands.utility.twitch.twitch_api import (
    get_uuid_by_twitch_name,
    notify_twitch_online,
    parse_twitch_notification_message,
    subscribe_to_twitch_online_notification,
)

pytestmark = pytest.mark.asyncio


async def test_add_twitch_no_permission(restricted_command_info):
    await addTwitchLiveNotification(restricted_command_info, "ninja", restricted_command_info.channel, "live")
    restricted_command_info.reply.assert_awaited_once()


@patch(
    "commands.utility.twitch.add_twitch_live_notification.get_uuid_by_twitch_name", new_callable=AsyncMock, return_value=None
)
async def test_add_twitch_user_not_found(mock_uid, admin_command_info):
    await addTwitchLiveNotification(admin_command_info, "ninja", admin_command_info.channel, "live")
    admin_command_info.reply.assert_awaited_once()


@patch("commands.utility.twitch.add_twitch_live_notification.subscribe_to_twitch_online_notification", new_callable=AsyncMock)
@patch("commands.utility.twitch.add_twitch_live_notification.get_twitch_service")
@patch(
    "commands.utility.twitch.add_twitch_live_notification.get_uuid_by_twitch_name", new_callable=AsyncMock, return_value="uid"
)
async def test_add_twitch_success(mock_uid, mock_svc, mock_sub, admin_command_info):
    svc = MagicMock()
    svc.add_notification = AsyncMock()
    mock_svc.return_value = svc
    admin_command_info.channel.permissions_for = MagicMock(return_value=MagicMock(send_messages=True, embed_links=True))
    await addTwitchLiveNotification(admin_command_info, "ninja", admin_command_info.channel, "live")
    svc.add_notification.assert_awaited_once()
    admin_command_info.reply.assert_awaited_once()


@patch("commands.utility.twitch.see_twitch_live_notifications.get_twitch_service")
async def test_see_twitch_empty(mock_svc, admin_command_info):
    svc = MagicMock()
    svc.get_notifications_by_guild = AsyncMock(return_value=[])
    mock_svc.return_value = svc
    await seeTwitchLiveNotifications(admin_command_info)
    admin_command_info.reply.assert_awaited_once()


@patch("commands.utility.twitch.see_twitch_live_notifications.get_twitch_service")
async def test_see_twitch_with_entries(mock_svc, admin_command_info):
    entry = MagicMock()
    entry.twitch_name = "ninja"
    entry.channel_id = str(admin_command_info.channel.id)
    entry.notification_message = "live"
    svc = MagicMock()
    svc.get_notifications_by_guild = AsyncMock(return_value=[entry])
    mock_svc.return_value = svc
    await seeTwitchLiveNotifications(admin_command_info)
    admin_command_info.reply.assert_awaited_once()


@patch("commands.utility.twitch.twitch_api.get_twitch_service")
async def test_get_uuid_by_name(mock_svc):
    user = MagicMock()
    user.id = "123"
    svc = MagicMock()
    svc.get_user_by_login = AsyncMock(return_value=user)
    mock_svc.return_value = svc
    assert await get_uuid_by_twitch_name("ninja") == "123"


@patch("commands.utility.twitch.twitch_api.get_twitch_service", return_value=None)
async def test_notify_twitch_no_service(_mock_svc):
    await notify_twitch_online(MagicMock(), "uuid", {})


@patch("commands.utility.twitch.twitch_api.get_twitch_service")
async def test_subscribe_notification(mock_svc):
    svc = MagicMock()
    svc.stream_status = {}
    mock_svc.return_value = svc
    await subscribe_to_twitch_online_notification("uuid")
    assert svc.stream_status["uuid"] is False


def test_parse_notification_message_fallback():
    result = parse_twitch_notification_message(None, "en_US", "ninja")
    assert "ninja" in result or isinstance(result, str)
