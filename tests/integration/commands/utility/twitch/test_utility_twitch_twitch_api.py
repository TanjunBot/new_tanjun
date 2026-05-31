"""Integration tests for commands.utility.twitch.twitch_api.notify_twitch_online."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest


pytestmark = [pytest.mark.asyncio, pytest.mark.integration]


async def test_notify_twitch_online_without_service():
    with patch("commands.utility.twitch.twitch_api.get_twitch_service", return_value=None):
        from commands.utility.twitch.twitch_api import notify_twitch_online

        await notify_twitch_online(client=MagicMock(), uuid="uuid", data={})


async def test_notify_twitch_online_delegates_to_service():
    service = MagicMock()
    service.send_live_notification = AsyncMock()
    client = MagicMock()
    payload = {"stream": "live"}

    with patch("commands.utility.twitch.twitch_api.get_twitch_service", return_value=service):
        from commands.utility.twitch.twitch_api import notify_twitch_online

        await notify_twitch_online(client=client, uuid="uuid-1", data=payload)

    service.send_live_notification.assert_awaited_once_with(client, "uuid-1", payload)
