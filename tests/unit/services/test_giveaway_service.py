"""Tests for services/giveaway_service.py."""

from __future__ import annotations

from contextlib import asynccontextmanager
from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from models import GiveawayModel
from services.giveaway_service import GiveawayCreateParams, GiveawayService, GiveawayUpdateParams
from tests.helpers.factories import CHANNEL_ID, GUILD_ID, USER_ID, giveaway_row


@asynccontextmanager
async def _fake_transaction():
    cursor = AsyncMock()
    cursor.execute = AsyncMock()
    cursor.fetchone = AsyncMock(return_value=(1,))
    conn = MagicMock()
    conn.cursor = MagicMock(return_value=AsyncMock())
    conn.cursor.return_value.__aenter__.return_value = cursor
    conn.__aenter__ = AsyncMock(return_value=conn)
    conn.__aexit__ = AsyncMock(return_value=None)
    yield conn


class TestGiveawayService:
    @pytest.mark.asyncio
    async def test_create(self):
        params = GiveawayCreateParams(
            guild_id=GUILD_ID,
            title="Test",
            description="Desc",
            winners=1,
            with_button=True,
            channel_id=CHANNEL_ID,
            end_time=datetime(2025, 12, 31, tzinfo=UTC),
        )
        with patch("services.giveaway_service.transaction", _fake_transaction):
            result = await GiveawayService.create(params)
        assert result == 1

    @pytest.mark.asyncio
    async def test_get_found(self):
        with patch("services.giveaway_service.safe_execute_query", new_callable=AsyncMock) as mock_q:
            mock_q.return_value = [giveaway_row()]
            result = await GiveawayService.get(1)
        assert isinstance(result, GiveawayModel)

    @pytest.mark.asyncio
    async def test_get_none(self):
        with patch("services.giveaway_service.safe_execute_query", new_callable=AsyncMock) as mock_q:
            mock_q.return_value = []
            result = await GiveawayService.get(999)
        assert result is None

    @pytest.mark.asyncio
    async def test_update(self):
        params = GiveawayUpdateParams(
            guild_id=GUILD_ID,
            title="Updated",
            end_time=datetime(2025, 12, 31, tzinfo=UTC),
            channel_id=CHANNEL_ID,
        )
        with patch("services.giveaway_service.transaction", _fake_transaction):
            await GiveawayService.update(1, params)

    @pytest.mark.asyncio
    async def test_delete(self):
        with patch("services.giveaway_service.transaction", _fake_transaction):
            await GiveawayService.delete(1)

    @pytest.mark.asyncio
    async def test_add_participant(self):
        with patch("services.giveaway_service.execute_action", new_callable=AsyncMock) as mock_exec:
            await GiveawayService.add_participant(1, USER_ID)
            mock_exec.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_is_participant_true(self):
        with patch("services.giveaway_service.safe_execute_query", new_callable=AsyncMock) as mock_q:
            mock_q.return_value = [(1,)]
            assert await GiveawayService.is_participant(1, USER_ID) is True

    @pytest.mark.asyncio
    async def test_is_user_blacklisted(self):
        with patch("services.giveaway_service.execute_query", new_callable=AsyncMock) as mock_q:
            mock_q.return_value = [(USER_ID, "spam")]
            assert await GiveawayService.is_user_blacklisted(GUILD_ID, USER_ID) is True

    @pytest.mark.asyncio
    async def test_set_started(self):
        with patch("services.giveaway_service.execute_action", new_callable=AsyncMock) as mock_exec:
            await GiveawayService.set_started(1)
            mock_exec.assert_awaited_once()
