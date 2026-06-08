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

    @pytest.mark.asyncio
    async def test_create_with_requirements(self):
        params = GiveawayCreateParams(
            guild_id=GUILD_ID,
            title="Req",
            description="Desc",
            winners=2,
            with_button=False,
            channel_id=CHANNEL_ID,
            end_time=datetime(2025, 12, 31, tzinfo=UTC),
            channel_requirements={CHANNEL_ID: 3},
            role_requirement=["role-1"],
        )
        with patch("services.giveaway_service.transaction", _fake_transaction):
            result = await GiveawayService.create(params)
        assert result == 1

    @pytest.mark.asyncio
    async def test_create_returns_none_on_error(self):
        params = GiveawayCreateParams(
            guild_id=GUILD_ID,
            title="Fail",
            description="Desc",
            winners=1,
            with_button=True,
            channel_id=CHANNEL_ID,
            end_time=datetime(2025, 12, 31, tzinfo=UTC),
        )

        @asynccontextmanager
        async def _boom():
            raise RuntimeError("db down")
            yield  # pragma: no cover

        with patch("services.giveaway_service.transaction", _boom):
            result = await GiveawayService.create(params)
        assert result is None

    @pytest.mark.asyncio
    async def test_update_with_requirements(self):
        params = GiveawayUpdateParams(
            guild_id=GUILD_ID,
            title="Updated",
            end_time=datetime(2025, 12, 31, tzinfo=UTC),
            channel_id=CHANNEL_ID,
            channel_requirements={CHANNEL_ID: 2},
            role_requirement=["role-2"],
        )
        with patch("services.giveaway_service.transaction", _fake_transaction):
            await GiveawayService.update(1, params)

    @pytest.mark.asyncio
    async def test_delete_old_with_ids(self):
        cursor = AsyncMock()
        cursor.execute = AsyncMock()
        cursor.fetchall = AsyncMock(return_value=[(1,), (2,)])
        conn = MagicMock()
        conn.cursor = MagicMock(return_value=AsyncMock())
        conn.cursor.return_value.__aenter__.return_value = cursor
        conn.__aenter__ = AsyncMock(return_value=conn)
        conn.__aexit__ = AsyncMock(return_value=None)

        @asynccontextmanager
        async def _tx():
            yield conn

        with patch("services.giveaway_service.transaction", _tx):
            await GiveawayService.delete_old()

    @pytest.mark.asyncio
    async def test_delete_old_no_ids(self):
        cursor = AsyncMock()
        cursor.execute = AsyncMock()
        cursor.fetchall = AsyncMock(return_value=[])
        conn = MagicMock()
        conn.cursor = MagicMock(return_value=AsyncMock())
        conn.cursor.return_value.__aenter__.return_value = cursor
        conn.__aenter__ = AsyncMock(return_value=conn)
        conn.__aexit__ = AsyncMock(return_value=None)

        @asynccontextmanager
        async def _tx():
            yield conn

        with patch("services.giveaway_service.transaction", _tx):
            await GiveawayService.delete_old()

    @pytest.mark.asyncio
    async def test_state_setters_and_getters(self):
        with patch("services.giveaway_service.execute_action", new_callable=AsyncMock) as action:
            await GiveawayService.set_message_id(1, 99)
            await GiveawayService.mark_sent(1, 100)
            await GiveawayService.set_ended(1)
            await GiveawayService.set_endtime(1, datetime(2025, 6, 1, tzinfo=UTC))
            assert action.await_count == 4

    @pytest.mark.asyncio
    async def test_get_send_and_end_ready(self):
        async def _iter(query: str):
            if "started = 0" in query:
                yield (10,)
            else:
                yield (20,)

        with patch("services.giveaway_service.execute_query_iter", side_effect=_iter):
            assert await GiveawayService.get_send_ready() == [10]
            assert await GiveawayService.get_end_ready() == [20]

    @pytest.mark.asyncio
    async def test_participant_tracking_and_blacklist(self):
        with (
            patch("services.giveaway_service.execute_action", new_callable=AsyncMock) as action,
            patch("services.giveaway_service.safe_execute_query", new_callable=AsyncMock) as safe_q,
            patch("services.giveaway_service.execute_query", new_callable=AsyncMock) as query,
        ):
            safe_q.return_value = [(4,)]
            query.return_value = [(7,)]
            await GiveawayService.remove_participant(1, USER_ID)
            await GiveawayService.add_voice_minutes(USER_ID, GUILD_ID)
            await GiveawayService.add_new_message(USER_ID, GUILD_ID)
            await GiveawayService.add_new_message_channel(USER_ID, GUILD_ID, CHANNEL_ID)
            await GiveawayService.add_blacklisted_user(GUILD_ID, USER_ID)
            await GiveawayService.add_blacklisted_role(GUILD_ID, "role-1")
            await GiveawayService.remove_blacklisted_user(GUILD_ID, USER_ID)
            await GiveawayService.remove_blacklisted_role(GUILD_ID, "role-1")
            assert await GiveawayService.get_new_messages(1, USER_ID) == 7
            assert await GiveawayService.get_new_messages_channel(1, CHANNEL_ID, USER_ID) == 4
            assert await GiveawayService.get_voice_time(1, USER_ID) == 4
            assert action.await_count == 8
