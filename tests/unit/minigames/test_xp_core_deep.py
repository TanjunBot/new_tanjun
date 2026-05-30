from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from minigames import _xp_core

pytestmark = pytest.mark.asyncio


@patch("minigames._xp_core.xp_calculator.calculate_xp", new_callable=AsyncMock, return_value=15)
async def test_calculate_xp_delegates(mock_calc):
    result = await _xp_core.calculate_xp("1", "2", "3", ["4"])
    assert result == 15
    mock_calc.assert_awaited_once_with("1", "2", ["4"], "3")


@patch("minigames._xp_core._get_cached_blacklist", new_callable=AsyncMock)
async def test_is_entity_blacklisted_user(mock_bl):
    user = MagicMock()
    user.entity_id = "99"
    mock_bl.return_value = {"channels": [], "users": [user], "roles": []}
    assert await _xp_core.is_entity_blacklisted("1", "99", "3", set()) is True


@patch("minigames._xp_core._get_cached_blacklist", new_callable=AsyncMock)
async def test_is_entity_blacklisted_channel(mock_bl):
    ch = MagicMock()
    ch.entity_id = "55"
    mock_bl.return_value = {"channels": [ch], "users": [], "roles": []}
    assert await _xp_core.is_entity_blacklisted("1", "2", "55", set()) is True


@patch("minigames._xp_core._get_cached_blacklist", new_callable=AsyncMock)
async def test_is_entity_blacklisted_role(mock_bl):
    role = MagicMock()
    role.entity_id = "77"
    mock_bl.return_value = {"channels": [], "users": [], "roles": [role]}
    assert await _xp_core.is_entity_blacklisted("1", "2", "3", {"77"}) is True
