"""Tests for repositories/twitch_repository.py."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest

from models import TwitchOnlineNotificationModel
from repositories.twitch_repository import TwitchRepository
from tests.helpers.factories import CHANNEL_ID, GUILD_ID


@pytest.fixture
def repo() -> TwitchRepository:
    return TwitchRepository()


class TestTwitchRepository:
    @pytest.mark.asyncio
    async def test_get_by_channel(self, repo: TwitchRepository):
        async def fake_iter(*args, **kwargs):
            yield TwitchOnlineNotificationModel.from_row((1, CHANNEL_ID, GUILD_ID, "uuid123456789012345", "streamer", "msg"))

        with patch.object(TwitchOnlineNotificationModel, "iter_rows", side_effect=fake_iter):
            result = await repo.get_by_channel(CHANNEL_ID)
        assert len(result) == 1
        assert result[0].twitch_name == "streamer"

    @pytest.mark.asyncio
    async def test_set(self, repo: TwitchRepository):
        with patch("api.execute_action", new_callable=AsyncMock) as mock_exec:
            await repo.set(GUILD_ID, CHANNEL_ID, "uuid-123456789012345", "streamer", "Live!")
            mock_exec.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_remove(self, repo: TwitchRepository):
        with patch("api.execute_action", new_callable=AsyncMock) as mock_exec:
            await repo.remove("1")
            assert "DELETE FROM twitchOnlineNotification" in mock_exec.await_args[0][0]

    @pytest.mark.asyncio
    async def test_get_by_twitch_uuid(self, repo: TwitchRepository):
        row = (1, CHANNEL_ID, GUILD_ID, "uuid-123456789012345", "streamer", None)
        with patch("api.safe_execute_query", new_callable=AsyncMock) as mock_q:
            mock_q.return_value = [row]
            result = await repo.get_by_twitch_uuid("uuid-123456789012345")
        assert result.twitch_uuid == "uuid-123456789012345"

    @pytest.mark.asyncio
    async def test_get_by_twitch_uuid_none(self, repo: TwitchRepository):
        with patch("api.safe_execute_query", new_callable=AsyncMock) as mock_q:
            mock_q.return_value = []
            result = await repo.get_by_twitch_uuid("missing")
        assert result is None

    @pytest.mark.asyncio
    async def test_get_all_uuids(self, repo: TwitchRepository):
        async def fake_iter(*args, **kwargs):
            yield ("uuid-1",)
            yield ("uuid-2",)

        with patch("api.execute_query_iter", side_effect=fake_iter):
            result = await repo.get_all_uuids()
        assert result == ["uuid-1", "uuid-2"]

    @pytest.mark.asyncio
    async def test_get_by_guild(self, repo: TwitchRepository):
        async def fake_iter(*args, **kwargs):
            yield (1, CHANNEL_ID, GUILD_ID, "uuid-123456789012345", "streamer", None)

        with patch.object(TwitchOnlineNotificationModel, "iter_rows", side_effect=lambda q, p: fake_iter()):
            result = await repo.get_by_guild(GUILD_ID)
        assert len(result) == 1
