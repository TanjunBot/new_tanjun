"""Tests for repositories/warning_repository.py."""

from __future__ import annotations

from datetime import datetime, timezone
from unittest.mock import AsyncMock, patch

import pytest

from models import DetailedWarningModel, WarnConfigModel, WarningModel
from repositories.warning_repository import WarningRepository
from tests.helpers.factories import GUILD_ID, USER_ID, warning_row


@pytest.fixture
def repo() -> WarningRepository:
    return WarningRepository()


class TestWarningRepository:
    @pytest.mark.asyncio
    async def test_add(self, repo: WarningRepository):
        with patch("api.execute_insert_and_get_id", new_callable=AsyncMock) as mock_insert:
            mock_insert.return_value = 42
            result = await repo.add("123", "111", "reason", "222")
            assert result == 42
            mock_insert.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_get_all_for_user(self, repo: WarningRepository):
        async def fake_iter(*args, **kwargs):
            yield WarningModel.from_row(warning_row())

        with patch.object(WarningModel, "iter_rows", side_effect=lambda q, p: fake_iter()):
            rows = [w async for w in repo.get_all(GUILD_ID, USER_ID)]
        assert len(rows) == 1

    @pytest.mark.asyncio
    async def test_get_all_for_guild(self, repo: WarningRepository):
        async def fake_iter(*args, **kwargs):
            yield WarningModel.from_row(warning_row())

        with patch.object(WarningModel, "iter_rows", side_effect=lambda q, p: fake_iter()):
            rows = [w async for w in repo.get_all(GUILD_ID)]
        assert len(rows) == 1

    @pytest.mark.asyncio
    async def test_get_detailed(self, repo: WarningRepository):
        dt = datetime(2024, 6, 15, tzinfo=timezone.utc)

        async def fake_iter(*args, **kwargs):
            yield DetailedWarningModel.from_row((1, "reason", dt, None, USER_ID))

        with patch.object(DetailedWarningModel, "iter_rows", side_effect=lambda q, p: fake_iter()):
            rows = [w async for w in repo.get_detailed(GUILD_ID, USER_ID)]
        assert rows[0].reason == "reason"

    @pytest.mark.asyncio
    async def test_remove(self, repo: WarningRepository):
        with patch("api.execute_action", new_callable=AsyncMock) as mock_exec:
            await repo.remove(5)
            mock_exec.assert_awaited_once()
            assert "DELETE FROM warnings" in mock_exec.await_args[0][0]

    @pytest.mark.asyncio
    async def test_set_config(self, repo: WarningRepository):
        with patch("api.execute_action", new_callable=AsyncMock) as mock_exec:
            await repo.set_config("123", 30, 3, 600, 5, 10)
            mock_exec.assert_awaited_once()
            assert "warn_config" in mock_exec.await_args[0][0]

    @pytest.mark.asyncio
    async def test_get_config_found(self, repo: WarningRepository):
        with patch("api.execute_query", new_callable=AsyncMock) as mock_q:
            mock_q.return_value = [("123456789", 30, 3, 600, 5, 10)]
            result = await repo.get_config("123456789")
            assert result.expiration_days == 30

    @pytest.mark.asyncio
    async def test_get_config_none(self, repo: WarningRepository):
        with patch("api.execute_query", new_callable=AsyncMock) as mock_q:
            mock_q.return_value = []
            result = await repo.get_config("999")
            assert result is None
