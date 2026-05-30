"""Unit tests for counting minigame entrypoint wrappers."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest

from minigames import counting as normal_counting
from minigames import counting_challenge as challenge_counting
from tests.helpers.discord import make_message


@pytest.mark.unit
class TestCountingHandlers:
    @pytest.mark.asyncio
    async def test_normal_counting_delegates_to_common(self):
        message = make_message(content="1")
        with patch("minigames._counting_common.counting", new_callable=AsyncMock) as base:
            await normal_counting.counting(message)
            base.assert_awaited_once()
            assert base.await_args.kwargs.get("config") is None

    @pytest.mark.asyncio
    async def test_challenge_counting_passes_failure_callbacks(self):
        message = make_message(content="1")
        with patch("minigames.counting_challenge._counting_base", new_callable=AsyncMock) as base:
            await challenge_counting.counting(message)
            base.assert_awaited_once()
            assert base.await_args.kwargs.get("on_failure") is not None
            assert base.await_args.kwargs.get("on_double_count") is not None
