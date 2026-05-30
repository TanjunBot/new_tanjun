"""Tests for repositories/trigger_message_repository.py."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest

from models import TriggerMessageChannelModel, TriggerMessageModel
from repositories.trigger_message_repository import TriggerMessageRepository
from tests.helpers.factories import CHANNEL_ID, GUILD_ID


@pytest.fixture
def repo() -> TriggerMessageRepository:
    return TriggerMessageRepository()


class TestTriggerMessageRepository:
    @pytest.mark.asyncio
    async def test_get_all(self, repo: TriggerMessageRepository):
        async def fake_iter(*args, **kwargs):
            yield TriggerMessageModel.from_row((1, GUILD_ID, "hello", "world", False))

        with patch.object(TriggerMessageModel, "iter_rows", side_effect=lambda q, p: fake_iter()):
            result = await repo.get_all(GUILD_ID)
        assert len(result) == 1

    @pytest.mark.asyncio
    async def test_add(self, repo: TriggerMessageRepository):
        with patch("api.execute_action", new_callable=AsyncMock) as mock_exec:
            await repo.add(GUILD_ID, "trigger", "response", True)
            mock_exec.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_remove(self, repo: TriggerMessageRepository):
        with patch("api.execute_action", new_callable=AsyncMock) as mock_exec:
            await repo.remove(GUILD_ID, "trigger")
            assert "DELETE FROM triggerMessages" in mock_exec.await_args[0][0]

    @pytest.mark.asyncio
    async def test_get_channels(self, repo: TriggerMessageRepository):
        async def fake_iter(*args, **kwargs):
            yield TriggerMessageChannelModel.from_row((GUILD_ID, CHANNEL_ID, 1))

        with patch.object(TriggerMessageChannelModel, "iter_rows", side_effect=lambda q, p: fake_iter()):
            result = await repo.get_channels(GUILD_ID, 1)
        assert len(result) == 1

    @pytest.mark.asyncio
    async def test_find_case_insensitive(self, repo: TriggerMessageRepository):
        row = (1, GUILD_ID, "Hello", "world", False)
        with patch("api.execute_query", new_callable=AsyncMock) as mock_q:
            mock_q.return_value = [row]
            result = await repo.find(GUILD_ID, "hello", CHANNEL_ID)
        assert result is not None
        assert result.trigger == "Hello"

    @pytest.mark.asyncio
    async def test_find_case_sensitive_mismatch(self, repo: TriggerMessageRepository):
        row = (1, GUILD_ID, "Hello", "world", True)
        with patch("api.execute_query", new_callable=AsyncMock) as mock_q:
            mock_q.return_value = [row]
            result = await repo.find(GUILD_ID, "hello", CHANNEL_ID)
        assert result is None

    @pytest.mark.asyncio
    async def test_find_not_found(self, repo: TriggerMessageRepository):
        with patch("api.execute_query", new_callable=AsyncMock) as mock_q:
            mock_q.return_value = []
            result = await repo.find(GUILD_ID, "missing", CHANNEL_ID)
        assert result is None
