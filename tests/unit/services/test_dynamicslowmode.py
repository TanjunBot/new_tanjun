"""Tests for services/dynamicslowmode.py."""

from __future__ import annotations

from datetime import datetime, timezone
from unittest.mock import AsyncMock, patch

import pytest

from models import DynamicSlowmodeModel
from services.dynamicslowmode import DynamicSlowmodeConfig, DynamicSlowmodeService
from tests.helpers.factories import CHANNEL_ID, GUILD_ID


@pytest.fixture
def service() -> DynamicSlowmodeService:
    return DynamicSlowmodeService()


class TestDynamicSlowmodeConfig:
    def test_from_db_model(self):
        db_model = DynamicSlowmodeModel.from_row((GUILD_ID, CHANNEL_ID, 5, 10, 60, 30))
        config = DynamicSlowmodeConfig.from_db_model(db_model)
        assert config.messages == 5
        assert config.per == 10


class TestDynamicSlowmodeService:
    @pytest.mark.asyncio
    async def test_configure(self, service: DynamicSlowmodeService):
        with patch("api.add_dynamicslowmode", new_callable=AsyncMock) as mock_add:
            await service.configure(GUILD_ID, CHANNEL_ID, 5, 10, 60)
            mock_add.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_configure_invalid_raises(self, service: DynamicSlowmodeService):
        with pytest.raises(ValueError):
            await service.configure(GUILD_ID, CHANNEL_ID, 0, 10, 60)
        with pytest.raises(ValueError):
            await service.configure(GUILD_ID, CHANNEL_ID, 5, 0, 60)
        with pytest.raises(ValueError):
            await service.configure(GUILD_ID, CHANNEL_ID, 5, 10, 0)

    @pytest.mark.asyncio
    async def test_get_all_configs(self, service: DynamicSlowmodeService):
        db_model = DynamicSlowmodeModel.from_row((GUILD_ID, CHANNEL_ID, 5, 10, 60, None))
        with patch("api.get_dynamicslowmode_channels", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = [db_model]
            configs = await service.get_all_configs(GUILD_ID)
        assert len(configs) == 1
        assert configs[0].messages == 5

    @pytest.mark.asyncio
    async def test_get_config_none(self, service: DynamicSlowmodeService):
        with patch("api.get_dynamicslowmode", new_callable=AsyncMock, return_value=None):
            assert await service.get_config(CHANNEL_ID) is None

    @pytest.mark.asyncio
    async def test_get_recent_messages(self, service: DynamicSlowmodeService):
        with patch("api.get_dynamicslowmode_messages", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = []
            result = await service.get_recent_messages(CHANNEL_ID)
        assert result == []

    @pytest.mark.asyncio
    async def test_clean_old(self, service: DynamicSlowmodeService):
        dt = datetime.now(timezone.utc)
        with patch("api.clear_old_dynamicslowmode_messages", new_callable=AsyncMock) as mock_clear:
            await service.clean_old(CHANNEL_ID, dt)
            mock_clear.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_should_throttle_over_limit(self, service: DynamicSlowmodeService):
        config = DynamicSlowmodeConfig(
            guild_id=GUILD_ID,
            channel_id=CHANNEL_ID,
            messages=1,
            per=10,
            reset_after=60,
        )
        channel_id = int(CHANNEL_ID)
        await service.should_throttle(channel_id, config)
        result = await service.should_throttle(channel_id, config)
        assert result is True

    @pytest.mark.asyncio
    async def test_remove(self, service: DynamicSlowmodeService):
        with patch("api.remove_dynamicslowmode", new_callable=AsyncMock) as mock_remove:
            await service.remove(GUILD_ID, CHANNEL_ID)
            mock_remove.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_get_config(self, service: DynamicSlowmodeService):
        db_model = DynamicSlowmodeModel.from_row((GUILD_ID, CHANNEL_ID, 5, 10, 60, None))
        with patch("api.get_dynamicslowmode", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = db_model
            config = await service.get_config(CHANNEL_ID)
        assert config is not None
        assert config.messages == 5

    @pytest.mark.asyncio
    async def test_should_throttle_under_limit(self, service: DynamicSlowmodeService):
        config = DynamicSlowmodeConfig(
            guild_id=GUILD_ID,
            channel_id=CHANNEL_ID,
            messages=5,
            per=10,
            reset_after=60,
        )
        result = await service.should_throttle(int(CHANNEL_ID), config)
        assert result is False

    @pytest.mark.asyncio
    async def test_track_message(self, service: DynamicSlowmodeService):
        dt = datetime.now(timezone.utc)
        with patch("api.add_dynamicslowmode_message", new_callable=AsyncMock) as mock_add:
            await service.track_message(CHANNEL_ID, "99999999999999999", dt)
            mock_add.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_cache_current_slowmode(self, service: DynamicSlowmodeService):
        with patch("api.cash_slowmode_delay", new_callable=AsyncMock) as mock_cache:
            await service.cache_current_slowmode(CHANNEL_ID, 30)
            mock_cache.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_restore_slowmode(self, service: DynamicSlowmodeService):
        with patch("api.remove_cashed_slowmode_delay", new_callable=AsyncMock) as mock_restore:
            await service.restore_slowmode(CHANNEL_ID)
            mock_restore.assert_awaited_once()
