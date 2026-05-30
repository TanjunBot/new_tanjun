"""Tests for repositories/log_blacklist_repository.py."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest

from repositories.log_blacklist_repository import LogBlacklistRepository, LogBlacklistType


@pytest.fixture
def repo() -> LogBlacklistRepository:
    return LogBlacklistRepository()


class TestLogBlacklistType:
    def test_channel(self):
        assert LogBlacklistType.CHANNEL.table == "logBlacklistChannel"
        assert LogBlacklistType.CHANNEL.column == "channel_id"

    def test_role(self):
        assert LogBlacklistType.ROLE.table == "logRoleBlacklist"

    def test_user(self):
        assert LogBlacklistType.USER.table == "logUserBlacklist"


class TestLogBlacklistRepository:
    @pytest.mark.asyncio
    async def test_add(self, repo: LogBlacklistRepository):
        with patch("api.execute_action", new_callable=AsyncMock) as mock_exec:
            await repo.add("123", "444", LogBlacklistType.CHANNEL)
            mock_exec.assert_awaited_once()
            assert "logBlacklistChannel" in mock_exec.await_args[0][0]

    @pytest.mark.asyncio
    async def test_remove(self, repo: LogBlacklistRepository):
        with patch("api.execute_action", new_callable=AsyncMock) as mock_exec:
            await repo.remove("123", "777", LogBlacklistType.ROLE)
            assert "DELETE FROM logRoleBlacklist" in mock_exec.await_args[0][0]

    @pytest.mark.asyncio
    async def test_get_all(self, repo: LogBlacklistRepository):
        async def fake_iter(*args, **kwargs):
            yield ("444444444",)
            yield ("555555555",)

        with patch("api.execute_query_iter", side_effect=lambda q, p: fake_iter()):
            result = await repo.get_all("123", LogBlacklistType.CHANNEL)
        assert result == ["444444444", "555555555"]

    @pytest.mark.asyncio
    async def test_is_entity_blacklisted_true(self, repo: LogBlacklistRepository):
        with patch("api.execute_query", new_callable=AsyncMock) as mock_q:
            mock_q.return_value = [("111111111",)]
            result = await repo.is_entity_blacklisted("123", "111", LogBlacklistType.USER)
            assert result == "111111111"

    @pytest.mark.asyncio
    async def test_is_entity_blacklisted_false(self, repo: LogBlacklistRepository):
        with patch("api.execute_query", new_callable=AsyncMock) as mock_q:
            mock_q.return_value = []
            result = await repo.is_entity_blacklisted("123", "111", LogBlacklistType.USER)
            assert result is None
