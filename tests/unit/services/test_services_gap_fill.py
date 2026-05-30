from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from services.dynamicslowmode import DynamicSlowmodeConfig, DynamicSlowmodeService


pytestmark = pytest.mark.asyncio


async def test_dynamicslowmode_configure_validation():
    svc = DynamicSlowmodeService()
    with pytest.raises(ValueError):
        await svc.configure("1", "2", 0, 5, 10)


@patch("api.add_dynamicslowmode", new_callable=AsyncMock)
async def test_dynamicslowmode_configure_success(mock_add):
    svc = DynamicSlowmodeService()
    await svc.configure("1", "2", 3, 5, 10)
    mock_add.assert_awaited_once()


@patch("api.remove_dynamicslowmode", new_callable=AsyncMock)
async def test_dynamicslowmode_remove_clears_memory(mock_remove):
    svc = DynamicSlowmodeService()
    svc._recent_messages[99] = __import__("collections").deque([1.0])
    await svc.remove("1", "99")
    assert 99 not in svc._recent_messages


@patch("api.get_dynamicslowmode", new_callable=AsyncMock, return_value=None)
async def test_dynamicslowmode_get_config_none(mock_get):
    svc = DynamicSlowmodeService()
    assert await svc.get_config("1") is None


def test_dynamic_slowmode_config_from_db():
    db = MagicMock(guild_id="1", channel_id="2", messages=5, per=10, reset_after=60, cached_slowmode=3)
    cfg = DynamicSlowmodeConfig.from_db_model(db)
    assert cfg.messages == 5
