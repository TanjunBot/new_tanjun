"""Tests for repositories/level_config_repository.py."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest

from models import LevelConfig
from repositories.level_config_repository import LevelConfigRepository
from tests.helpers.factories import GUILD_ID


@pytest.fixture
def repo() -> LevelConfigRepository:
    return LevelConfigRepository()


class TestLevelConfigRepository:
    @pytest.mark.asyncio
    async def test_save_config(self, repo: LevelConfigRepository):
        config = LevelConfig(guild_id=GUILD_ID, difficulty="easy")
        with patch("api.execute_action", new_callable=AsyncMock) as mock_exec:
            with patch("api._invalidate_guild_cache") as mock_inv:
                await repo.save_config(config)
                mock_exec.assert_awaited_once()
                mock_inv.assert_called_once_with(GUILD_ID)

    @pytest.mark.asyncio
    async def test_update_field(self, repo: LevelConfigRepository):
        with patch("api.execute_action", new_callable=AsyncMock) as mock_exec, patch("api._invalidate_guild_cache"):
            await repo.update_field(GUILD_ID, active=False)
            mock_exec.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_update_field_empty_kwargs_noop(self, repo: LevelConfigRepository):
        with patch("api.execute_action", new_callable=AsyncMock) as mock_exec:
            await repo.update_field(GUILD_ID)
            mock_exec.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_update_field_invalid_difficulty(self, repo: LevelConfigRepository):
        with pytest.raises(ValueError, match="Invalid difficulty"):
            await repo.update_field(GUILD_ID, difficulty="invalid")

    @pytest.mark.asyncio
    async def test_update_field_unknown_field(self, repo: LevelConfigRepository):
        with pytest.raises(ValueError, match="Unknown level config field"):
            await repo.update_field(GUILD_ID, unknown_field=True)

    @pytest.mark.asyncio
    async def test_delete_config(self, repo: LevelConfigRepository):
        with patch("api.execute_action", new_callable=AsyncMock) as mock_exec, patch("api._invalidate_guild_cache"):
            await repo.delete_config(GUILD_ID)
            assert "DELETE FROM levelConfig" in mock_exec.await_args[0][0]
