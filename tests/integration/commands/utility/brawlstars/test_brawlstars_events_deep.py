from __future__ import annotations

from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from commands.utility.brawlstars.events import events
from tests.helpers.discord import make_target_member
from tests.integration.commands.admin.conftest import make_view_interaction


pytestmark = pytest.mark.asyncio


def _event(map_name="Gem_Grab", mode="gemGrab"):
    ev = MagicMock()
    ev.start_time = datetime.now(timezone.utc).isoformat()
    ev.end_time = datetime.now(timezone.utc).isoformat()
    ev.event = MagicMock()
    ev.event.map = map_name
    ev.event.mode = mode
    return ev


@patch("commands.utility.brawlstars.events.get_brawlstars_service")
async def test_events_not_found(mock_get_service, admin_command_info):
    service = MagicMock()
    service.get_events = AsyncMock(return_value=None)
    mock_get_service.return_value = service
    await events(admin_command_info)
    admin_command_info.reply.assert_awaited_once()


@patch("commands.utility.brawlstars.events.get_brawlstars_service")
async def test_events_pagination(mock_get_service, admin_command_info):
    service = MagicMock()
    service.get_events = AsyncMock(return_value=[_event(), _event("Brawl_Ball", "brawlBall")])
    mock_get_service.return_value = service
    await events(admin_command_info)
    admin_command_info.reply.assert_awaited_once()
    view = admin_command_info.reply.await_args.kwargs["view"]
    next_i = make_view_interaction(admin_command_info.user)
    next_i.response.edit_message = AsyncMock()
    await view.next(next_i, MagicMock())
    next_i.response.edit_message.assert_awaited_once()

    prev_i = make_view_interaction(admin_command_info.user)
    prev_i.response.edit_message = AsyncMock()
    await view.previous(prev_i, MagicMock())
    prev_i.response.edit_message.assert_awaited_once()

    wrong = make_view_interaction(make_target_member(user_id=99999))
    wrong.response.send_message = AsyncMock()
    await view.next(wrong, MagicMock())
    wrong.response.send_message.assert_awaited_once()
