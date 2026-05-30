"""Tests for services/scheduled_message_service.py."""

from __future__ import annotations

from datetime import UTC, datetime
from unittest.mock import AsyncMock, patch

import pytest

from models import ScheduledMessageModel
from services.scheduled_message_service import ScheduledMessageService, ScheduleMessageParams
from tests.helpers.factories import CHANNEL_ID, GUILD_ID, MESSAGE_ID, USER_ID, _dt


class TestScheduledMessageService:
    @pytest.mark.asyncio
    async def test_schedule(self):
        params = ScheduleMessageParams.model_construct(
            guild_id=GUILD_ID,
            channel_id=CHANNEL_ID,
            user_id=USER_ID,
            content="Hello",
            send_time=datetime(2025, 1, 1, tzinfo=UTC),
            repeat_interval=None,
            repeat_amount=None,
            attachments=None,
        )
        with patch("api.execute_action", new_callable=AsyncMock) as mock_exec:
            await ScheduledMessageService.schedule(params)
            mock_exec.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_cancel(self):
        with patch("api.execute_action", new_callable=AsyncMock) as mock_exec:
            await ScheduledMessageService.cancel(1)
            mock_exec.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_update_content(self):
        with patch("api.execute_action", new_callable=AsyncMock) as mock_exec:
            await ScheduledMessageService.update_content(1, "new content")
            mock_exec.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_get_user_messages(self):
        dt = _dt()

        async def fake_iter(*args, **kwargs):
            yield ScheduledMessageModel.from_row((1, GUILD_ID, CHANNEL_ID, USER_ID, "hi", dt, None, None, None, None, dt))

        with patch.object(ScheduledMessageModel, "iter_rows", side_effect=lambda q, p: fake_iter()):
            result = await ScheduledMessageService.get_user_messages(USER_ID)
        assert len(result) == 1

    @pytest.mark.asyncio
    async def test_find_by_discord_message_id(self):
        dt = _dt()

        async def fake_iter(*args, **kwargs):
            yield ScheduledMessageModel.from_row(
                (1, GUILD_ID, CHANNEL_ID, USER_ID, "hi", dt, None, None, None, MESSAGE_ID, dt)
            )

        with patch.object(ScheduledMessageModel, "iter_rows", side_effect=fake_iter):
            result = await ScheduledMessageService.find_by_discord_message_id(MESSAGE_ID)
        assert result is not None

    @pytest.mark.asyncio
    async def test_update_send_time(self):
        dt = datetime(2025, 6, 1, tzinfo=UTC)
        with patch("api.execute_action", new_callable=AsyncMock) as mock_exec:
            await ScheduledMessageService.update_send_time(1, dt)
            mock_exec.assert_awaited_once()
