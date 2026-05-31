"""Tests for hot-path DB read caches (log enable, blacklist, channel, booster claims)."""

from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

import tests.mock_config as mock_config

mock_config.patch_config_module()

from api import (  # noqa: E402
    _LOG_ENABLE_SELECT,
    clear_db_read_caches,
    get_log_blacklist,
    get_log_channel,
    get_log_enable,
    set_log_enable,
)
from repositories.log_blacklist_repository import LogBlacklistType  # noqa: E402
from services.booster_service import BoosterService, ClaimedBoosterType, clear_booster_read_cache  # noqa: E402
from tests.helpers.factories import CHANNEL_ID, GUILD_ID, ROLE_ID, USER_ID  # noqa: E402

pytestmark = pytest.mark.asyncio

_LOG_ENABLE_ROW = (
    GUILD_ID,
    1,
    1,
    1,
    0,
    1,
    1,
    1,
    1,
    1,
    0,
    1,
    1,
    1,
    1,
    1,
    1,
    1,
    1,
    1,
    0,
    0,
    1,
    1,
    1,
)


@pytest.fixture(autouse=True)
def _reset_caches() -> None:
    clear_db_read_caches()
    clear_booster_read_cache()
    yield
    clear_db_read_caches()
    clear_booster_read_cache()


def _log_enable_calls(execute: AsyncMock) -> int:
    return sum(
        1
        for call in execute.await_args_list
        if call.args and _LOG_ENABLE_SELECT in call.args[0]
    )


class TestLogEnableCacheContention:
    async def test_concurrent_get_log_enable_single_db_query(self) -> None:
        execute = AsyncMock(return_value=[_LOG_ENABLE_ROW])
        with patch("api.execute_query", new=execute):
            results = await asyncio.gather(*[get_log_enable(GUILD_ID) for _ in range(100)])
        assert len(results) == 100
        assert all(r.guild_id == GUILD_ID for r in results)
        assert _log_enable_calls(execute) == 1

    async def test_concurrent_get_log_enable_different_guilds(self) -> None:
        guilds = [str(900000000000000000 + i) for i in range(10)]
        execute = AsyncMock(
            side_effect=lambda q, p=None, bot=None: [
                (
                    p[0],
                    1,
                    1,
                    1,
                    0,
                    1,
                    1,
                    1,
                    1,
                    1,
                    0,
                    1,
                    1,
                    1,
                    1,
                    1,
                    1,
                    1,
                    1,
                    1,
                    0,
                    0,
                    1,
                    1,
                    1,
                )
            ]
        )
        with patch("api.execute_query", new=execute):
            await asyncio.gather(*[get_log_enable(g) for g in guilds])
        assert _log_enable_calls(execute) == len(guilds)


class TestLogBlacklistCache:
    async def test_get_log_blacklist_cached_per_type(self) -> None:
        with patch(
            "api.log_blacklist_repo.get_all",
            new=AsyncMock(return_value=["111"]),
        ) as get_all:
            first = await get_log_blacklist(GUILD_ID, LogBlacklistType.ROLE)
            second = await get_log_blacklist(GUILD_ID, LogBlacklistType.ROLE)
            other = await get_log_blacklist(GUILD_ID, LogBlacklistType.USER)
        assert first == ["111"]
        assert second == ["111"]
        assert get_all.await_count == 2

    async def test_add_log_blacklist_invalidates_cache(self) -> None:
        from api import add_log_blacklist

        with (
            patch("api.log_blacklist_repo.add", new=AsyncMock()),
            patch(
                "api.log_blacklist_repo.get_all",
                new=AsyncMock(return_value=[]),
            ) as get_all,
        ):
            await get_log_blacklist(GUILD_ID, LogBlacklistType.CHANNEL)
            await add_log_blacklist(GUILD_ID, "999", LogBlacklistType.CHANNEL)
            await get_log_blacklist(GUILD_ID, LogBlacklistType.CHANNEL)
        assert get_all.await_count == 2


class TestLogChannelCache:
    async def test_get_log_channel_concurrent_single_query(self) -> None:
        execute = AsyncMock(return_value=[(CHANNEL_ID,)])
        with patch("api.execute_query", new=execute):
            results = await asyncio.gather(*[get_log_channel(GUILD_ID) for _ in range(50)])
        assert all(r == CHANNEL_ID for r in results)
        channel_queries = [c for c in execute.await_args_list if "log_channel" in c.args[0]]
        assert len(channel_queries) == 1


class TestBoosterClaimsCache:
    async def test_get_all_claims_concurrent_single_query(self) -> None:
        service = BoosterService()
        row = (USER_ID, ROLE_ID, GUILD_ID)
        safe = AsyncMock(return_value=[row])
        with patch("services.booster_service.safe_execute_query", new=safe):
            results = await asyncio.gather(
                *[service.get_all_claims(ClaimedBoosterType.ROLE) for _ in range(40)]
            )
        assert len(results) == 40
        assert safe.await_count == 1

    async def test_claim_invalidates_get_all_claims_cache(self) -> None:
        service = BoosterService()
        with (
            patch("services.booster_service.execute_action", new=AsyncMock()),
            patch(
                "services.booster_service.safe_execute_query",
                new=AsyncMock(return_value=[]),
            ) as safe,
        ):
            await service.get_all_claims(ClaimedBoosterType.CHANNEL)
            await service.claim(ClaimedBoosterType.CHANNEL, "u", "c", GUILD_ID)
            await service.get_all_claims(ClaimedBoosterType.CHANNEL)
        assert safe.await_count == 2


class TestSetLogEnableInvalidatesCache:
    async def test_set_log_enable_refetches_after_update(self) -> None:
        execute = AsyncMock(return_value=[_LOG_ENABLE_ROW])
        with (
            patch("api.execute_query", new=execute),
            patch("api.execute_action", new=AsyncMock()),
        ):
            await get_log_enable(GUILD_ID)
            await set_log_enable(GUILD_ID, memberJoin=False)
            await get_log_enable(GUILD_ID)
        assert _log_enable_calls(execute) == 2
