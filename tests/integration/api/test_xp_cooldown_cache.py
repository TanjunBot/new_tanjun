"""Integration tests for XP cooldown cache in update_user_xp."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest

import tests.mock_config as mock_config

mock_config.patch_config_module()

from api import (  # noqa: E402
    _guild_config_cache,
    _last_xp_gain_cache,
    clear_db_read_caches,
    update_user_xp,
)
from tests.helpers.factories import GUILD_ID, USER_ID  # noqa: E402

pytestmark = pytest.mark.asyncio


@pytest.fixture(autouse=True)
def _reset_caches() -> None:
    clear_db_read_caches()
    _guild_config_cache.clear()
    _last_xp_gain_cache.clear()
    yield
    clear_db_read_caches()
    _guild_config_cache.clear()
    _last_xp_gain_cache.clear()


class TestXpCooldownCache:
    async def test_two_grants_within_cooldown_single_db_write(self) -> None:
        _guild_config_cache.set(GUILD_ID, {"text_cooldown": 60})
        with patch("api.execute_action", new_callable=AsyncMock) as action:
            await update_user_xp(GUILD_ID, USER_ID, 5, respect_cooldown=True)
            await update_user_xp(GUILD_ID, USER_ID, 5, respect_cooldown=True)
        assert action.await_count == 1

    async def test_second_grant_allowed_after_cooldown_expires(self) -> None:
        _guild_config_cache.set(GUILD_ID, {"text_cooldown": 60})
        base_time = 1_000_000.0
        with (
            patch("api.time.time", side_effect=[base_time, base_time + 30, base_time + 61]),
            patch("api.execute_action", new_callable=AsyncMock) as action,
        ):
            await update_user_xp(GUILD_ID, USER_ID, 5, respect_cooldown=True)
            await update_user_xp(GUILD_ID, USER_ID, 5, respect_cooldown=True)
            await update_user_xp(GUILD_ID, USER_ID, 5, respect_cooldown=True)
        assert action.await_count == 2

    async def test_first_grant_updates_last_xp_gain_cache(self) -> None:
        _guild_config_cache.set(GUILD_ID, {"text_cooldown": 60})
        base_time = 2_000_000.0
        with (
            patch("api.time.time", return_value=base_time),
            patch("api.execute_action", new_callable=AsyncMock),
        ):
            await update_user_xp(GUILD_ID, USER_ID, 5, respect_cooldown=True)
        assert _last_xp_gain_cache[(GUILD_ID, USER_ID)] == base_time

    async def test_respect_cooldown_false_always_writes(self) -> None:
        _guild_config_cache.set(GUILD_ID, {"text_cooldown": 60})
        _last_xp_gain_cache[(GUILD_ID, USER_ID)] = 1_000_000.0
        with patch("api.execute_action", new_callable=AsyncMock) as action:
            await update_user_xp(GUILD_ID, USER_ID, 5, respect_cooldown=False)
            await update_user_xp(GUILD_ID, USER_ID, 5, respect_cooldown=False)
        assert action.await_count == 2
