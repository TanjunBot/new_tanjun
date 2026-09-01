"""Tests for loops/giveaway.py with time-based state transitions."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from freezegun import freeze_time

from loops import giveaway
from loops._voice_tracker import voice_user_manager

pytestmark = pytest.mark.asyncio

FROZEN_START = datetime(2025, 6, 15, 12, 0, 0, tzinfo=UTC)


class TestSendReadyGiveaways:
    @freeze_time(FROZEN_START)
    async def test_no_ready_giveaways_skips_send(self) -> None:
        client = MagicMock()
        with (
            patch("loops.giveaway.giveaway_service.get_send_ready", new_callable=AsyncMock, return_value=[]),
            patch("loops.giveaway.sendGiveaway", new_callable=AsyncMock) as mock_send,
        ):
            await giveaway.sendReadyGiveaways(client)
        mock_send.assert_not_awaited()

    @freeze_time(FROZEN_START)
    async def test_ready_giveaways_trigger_send(self) -> None:
        client = MagicMock()
        with (
            patch(
                "loops.giveaway.giveaway_service.get_send_ready",
                new_callable=AsyncMock,
                return_value=[10, 20],
            ),
            patch("loops.giveaway.sendGiveaway", new_callable=AsyncMock) as mock_send,
        ):
            await giveaway.sendReadyGiveaways(client)
        assert mock_send.await_count == 2
        mock_send.assert_any_await(giveawayid=10, client=client)
        mock_send.assert_any_await(giveawayid=20, client=client)

    async def test_state_transition_empty_to_ready_over_time(self) -> None:
        client = MagicMock()
        call_times: list[datetime] = []

        async def get_ready() -> list[int]:
            call_times.append(datetime.now(UTC))
            return [] if len(call_times) == 1 else [42]

        with freeze_time(FROZEN_START) as frozen:
            with (
                patch("loops.giveaway.giveaway_service.get_send_ready", side_effect=get_ready),
                patch("loops.giveaway.sendGiveaway", new_callable=AsyncMock) as mock_send,
            ):
                await giveaway.sendReadyGiveaways(client)
                frozen.tick(delta=timedelta(hours=1))
                await giveaway.sendReadyGiveaways(client)

        mock_send.assert_awaited_once_with(giveawayid=42, client=client)
        assert len(call_times) == 2
        assert call_times[1] - call_times[0] == timedelta(hours=1)


class TestCheckVoiceUsers:
    @freeze_time(FROZEN_START)
    async def test_no_active_users_skips_add_voice_minutes(self) -> None:
        voice_user_manager.clear()
        with patch("loops.giveaway.giveaway_service.add_voice_minutes", new_callable=AsyncMock) as mock_add:
            await giveaway.checkVoiceUsers(MagicMock())
        mock_add.assert_not_awaited()

    @freeze_time(FROZEN_START)
    async def test_active_users_receive_voice_minutes(self) -> None:
        voice_user_manager.clear()
        voice_user_manager.add(100, 200)
        voice_user_manager.add(101, 201)
        with patch("loops.giveaway.giveaway_service.add_voice_minutes", new_callable=AsyncMock) as mock_add:
            await giveaway.checkVoiceUsers(MagicMock())
        assert mock_add.await_count == 2
        mock_add.assert_any_await(100, 200)
        mock_add.assert_any_await(101, 201)
        voice_user_manager.clear()


class TestEndGiveaways:
    @freeze_time(FROZEN_START)
    async def test_no_ending_giveaways_skips_end(self) -> None:
        client = MagicMock()
        with (
            patch("loops.giveaway.giveaway_service.get_end_ready", new_callable=AsyncMock, return_value=[]),
            patch("loops.giveaway.endGiveaway", new_callable=AsyncMock) as mock_end,
        ):
            await giveaway.endGiveaways(client)
        mock_end.assert_not_awaited()

    @freeze_time(FROZEN_START)
    async def test_ending_giveaways_trigger_end(self) -> None:
        client = MagicMock()
        with (
            patch(
                "loops.giveaway.giveaway_service.get_end_ready",
                new_callable=AsyncMock,
                return_value=[5, 6, 7],
            ),
            patch("loops.giveaway.endGiveaway", new_callable=AsyncMock) as mock_end,
        ):
            await giveaway.endGiveaways(client)
        assert mock_end.await_count == 3

    async def test_end_transition_after_deadline_passes(self) -> None:
        client = MagicMock()
        phases: list[int] = []

        async def get_end_ready() -> list[int]:
            phases.append(len(phases))
            return [] if len(phases) == 1 else [99]

        with freeze_time(FROZEN_START) as frozen:
            with (
                patch("loops.giveaway.giveaway_service.get_end_ready", side_effect=get_end_ready),
                patch("loops.giveaway.endGiveaway", new_callable=AsyncMock) as mock_end,
            ):
                await giveaway.endGiveaways(client)
                frozen.tick(delta=timedelta(days=1))
                await giveaway.endGiveaways(client)

        mock_end.assert_awaited_once_with(giveaway_id=99, client=client)
