from __future__ import annotations

from datetime import UTC, datetime
from unittest.mock import AsyncMock, patch

import pytest

from models import ScheduledMessageModel
from services.scheduled_message_service import ScheduledMessageService
from tests.helpers.factories import CHANNEL_ID, GUILD_ID, USER_ID, _dt


@pytest.mark.asyncio
async def test_get_due_messages():
    dt = _dt()

    async def fake_iter(*args, **kwargs):
        yield ScheduledMessageModel.from_row((1, GUILD_ID, CHANNEL_ID, USER_ID, "hi", dt, None, None, None, None, dt))

    with patch.object(ScheduledMessageModel, "iter_rows", side_effect=fake_iter):
        result = await ScheduledMessageService.get_due_messages()
    assert len(result) == 1


@pytest.mark.asyncio
async def test_get_upcoming_with_guild():
    dt = datetime(2025, 1, 1, tzinfo=UTC)
    end = datetime(2025, 12, 31, tzinfo=UTC)

    async def fake_iter(*args, **kwargs):
        yield ScheduledMessageModel.from_row((1, GUILD_ID, CHANNEL_ID, USER_ID, "hi", dt, None, None, None, None, dt))

    with patch.object(ScheduledMessageModel, "iter_rows", side_effect=fake_iter):
        result = await ScheduledMessageService.get_upcoming(USER_ID, dt, end, guild_id=GUILD_ID)
    assert len(result) == 1


@pytest.mark.asyncio
async def test_update_repeat():
    with patch("api.execute_action", new_callable=AsyncMock) as mock_exec:
        await ScheduledMessageService.update_repeat(1, 3)
    mock_exec.assert_awaited_once()


@pytest.mark.asyncio
async def test_update_discord_message_id():
    with patch("api.execute_action", new_callable=AsyncMock) as mock_exec:
        await ScheduledMessageService.update_discord_message_id(1, "999")
    mock_exec.assert_awaited_once()


@pytest.mark.asyncio
async def test_cancel_message():
    with patch("api.execute_action", new_callable=AsyncMock) as mock_exec:
        await ScheduledMessageService.cancel(1)
    mock_exec.assert_awaited_once()
