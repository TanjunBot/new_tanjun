from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from commands.utility.twitch import twitch_api


@pytest.mark.asyncio
async def test_notify_twitch_online_no_service():
    with patch("commands.utility.twitch.twitch_api.get_twitch_service", return_value=None):
        await twitch_api.notify_twitch_online(MagicMock(), "uuid", {})


@pytest.mark.asyncio
async def test_notify_twitch_online_success():
    svc = MagicMock()
    svc.send_live_notification = AsyncMock()
    with patch("commands.utility.twitch.twitch_api.get_twitch_service", return_value=svc):
        await twitch_api.notify_twitch_online(MagicMock(), "uuid", {"x": 1})
    svc.send_live_notification.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_uuid_no_service():
    with patch("commands.utility.twitch.twitch_api.get_twitch_service", return_value=None):
        assert await twitch_api.get_uuid_by_twitch_name("name") is None


@pytest.mark.asyncio
async def test_get_uuid_not_found():
    svc = MagicMock()
    svc.get_user_by_login = AsyncMock(return_value=None)
    with patch("commands.utility.twitch.twitch_api.get_twitch_service", return_value=svc):
        assert await twitch_api.get_uuid_by_twitch_name("name") is None


@pytest.mark.asyncio
async def test_get_uuid_found():
    user = MagicMock()
    user.id = "abc"
    svc = MagicMock()
    svc.get_user_by_login = AsyncMock(return_value=user)
    with patch("commands.utility.twitch.twitch_api.get_twitch_service", return_value=svc):
        assert await twitch_api.get_uuid_by_twitch_name("name") == "abc"


@pytest.mark.asyncio
async def test_subscribe_empty_uuid():
    svc = MagicMock()
    svc.stream_status = {}
    with patch("commands.utility.twitch.twitch_api.get_twitch_service", return_value=svc):
        await twitch_api.subscribe_to_twitch_online_notification("")
    assert svc.stream_status == {}


@pytest.mark.asyncio
async def test_subscribe_sets_status():
    svc = MagicMock()
    svc.stream_status = {}
    with patch("commands.utility.twitch.twitch_api.get_twitch_service", return_value=svc):
        await twitch_api.subscribe_to_twitch_online_notification("uuid-1")
    assert svc.stream_status["uuid-1"] is False


def test_parse_message_no_service_with_template():
    with patch("commands.utility.twitch.twitch_api.get_twitch_service", return_value=None):
        result = twitch_api.parse_twitch_notification_message("Hello {name}", "en", "streamer")
    assert "streamer" in result


def test_parse_message_no_service_default():
    with patch("commands.utility.twitch.twitch_api.get_twitch_service", return_value=None):
        result = twitch_api.parse_twitch_notification_message(None, "en", "streamer")
    assert isinstance(result, str)


def test_parse_message_with_service():
    svc = MagicMock()
    svc.parse_notification_message = MagicMock(return_value="parsed")
    with patch("commands.utility.twitch.twitch_api.get_twitch_service", return_value=svc):
        assert twitch_api.parse_twitch_notification_message("msg", "en", "n") == "parsed"
