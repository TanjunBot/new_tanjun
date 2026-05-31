"""Tests for hot-path DB read caches (log enable, blacklist, channel, booster claims)."""

from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

import tests.mock_config as mock_config

mock_config.patch_config_module()

from api import (  # noqa: E402
    _LOG_ENABLE_SELECT,
    _blacklist_cache,
    _guild_config_cache,
    _last_xp_gain_cache,
    clear_db_read_caches,
    get_counting_configs,
    get_log_blacklist,
    get_log_channel,
    get_log_enable,
    invalidate_counting_cache,
    set_log_enable,
    update_user_xp,
)
from repositories.log_blacklist_repository import LogBlacklistType  # noqa: E402
from services.booster_service import BoosterService, ClaimedBoosterType, clear_booster_read_cache  # noqa: E402
from tests.helpers.concurrency import stress_concurrent
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
    _blacklist_cache.clear()
    _guild_config_cache.clear()
    _last_xp_gain_cache.clear()
    yield
    clear_db_read_caches()
    clear_booster_read_cache()
    _blacklist_cache.clear()
    _guild_config_cache.clear()
    _last_xp_gain_cache.clear()


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


class TestLogEnableCacheErrors:
    async def test_fetch_error_not_cached(self) -> None:
        calls = 0

        async def flaky_query(query: str, params=None, bot=None):
            nonlocal calls
            calls += 1
            if calls == 1:
                raise RuntimeError("db down")
            return [_LOG_ENABLE_ROW]

        with patch("api.execute_query", side_effect=flaky_query):
            with pytest.raises(RuntimeError, match="db down"):
                await get_log_enable(GUILD_ID)
            result = await get_log_enable(GUILD_ID)
        assert result.guild_id == GUILD_ID
        assert calls == 2


class TestLogBlacklistCrossTypeIsolation:
    async def test_role_invalidation_does_not_flush_user_cache(self) -> None:
        from api import add_log_blacklist

        responses: dict[str, list[str]] = {
            "ROLE": ["role1", "role2"],
            "USER": ["user1"],
        }
        call_counts: dict[str, int] = {"ROLE": 0, "USER": 0}

        async def get_all(guild_id: str, blacklist_type: LogBlacklistType) -> list[str]:
            key = blacklist_type.name
            idx = call_counts[key]
            call_counts[key] += 1
            return [responses[key][min(idx, len(responses[key]) - 1)]]

        with (
            patch("api.log_blacklist_repo.add", new=AsyncMock()),
            patch("api.log_blacklist_repo.get_all", side_effect=get_all),
        ):
            await get_log_blacklist(GUILD_ID, LogBlacklistType.ROLE)
            await get_log_blacklist(GUILD_ID, LogBlacklistType.USER)
            await add_log_blacklist(GUILD_ID, "999", LogBlacklistType.ROLE)
            role_again = await get_log_blacklist(GUILD_ID, LogBlacklistType.ROLE)
            user_again = await get_log_blacklist(GUILD_ID, LogBlacklistType.USER)
        assert role_again == ["role2"]
        assert user_again == ["user1"]
        assert call_counts["ROLE"] == 2
        assert call_counts["USER"] == 1


class TestLogChannelNoneCaching:
    async def test_concurrent_none_miss_single_query(self) -> None:
        execute = AsyncMock(return_value=[])
        with patch("api.execute_query", new=execute):
            results = await stress_concurrent(lambda: get_log_channel(GUILD_ID), n=50)
        assert all(r is None for r in results)
        channel_queries = [c for c in execute.await_args_list if "log_channel" in c.args[0]]
        assert len(channel_queries) == 1

    async def test_none_result_cached_on_sequential_reads(self) -> None:
        execute = AsyncMock(return_value=[])
        with patch("api.execute_query", new=execute):
            assert await get_log_channel(GUILD_ID) is None
            assert await get_log_channel(GUILD_ID) is None
        channel_queries = [c for c in execute.await_args_list if "log_channel" in c.args[0]]
        assert len(channel_queries) == 1


class TestGuildConfigCache:
    async def test_cached_config_skips_db(self) -> None:
        _guild_config_cache.set(GUILD_ID, {"text_cooldown": 120, "voice_cooldown": 90})
        with patch("api.execute_query", new=AsyncMock()) as execute:
            from api import _get_cached_config

            text = await _get_cached_config(GUILD_ID, "text_cooldown", 60)
            voice = await _get_cached_config(GUILD_ID, "voice_cooldown", 60)
        assert text == 120
        assert voice == 90
        execute.assert_not_awaited()

    async def test_invalidate_guild_cache_on_level_status_change(self) -> None:
        _guild_config_cache.set(GUILD_ID, {"active": True})
        with patch("api.execute_action", new=AsyncMock()):
            await __import__("api").set_level_system_status(GUILD_ID, False)
        assert _guild_config_cache.get(GUILD_ID) is None


class TestBlacklistCacheIsolation:
    async def test_blacklist_cached_per_guild(self) -> None:
        other_guild = "900000000000000001"
        with patch(
            "api.get_blacklist",
            new=AsyncMock(side_effect=[{"users": []}, {"users": ["x"]}]),
        ) as get_bl:
            from api import _get_cached_blacklist

            first = await _get_cached_blacklist(GUILD_ID)
            second = await _get_cached_blacklist(GUILD_ID)
            other = await _get_cached_blacklist(other_guild)
        assert first == {"users": []}
        assert second == {"users": []}
        assert other == {"users": ["x"]}
        assert get_bl.await_count == 2


class TestCountingCacheInvalidation:
    async def test_invalidate_counting_cache_refetches(self) -> None:
        invalidate_counting_cache(CHANNEL_ID)
        with patch("api.execute_query", new=AsyncMock(return_value=None)) as execute:
            await get_counting_configs(CHANNEL_ID)
            await get_counting_configs(CHANNEL_ID)
            assert execute.await_count == 3
        invalidate_counting_cache(CHANNEL_ID)
        with patch("api.execute_query", new=AsyncMock(return_value=None)) as execute2:
            await get_counting_configs(CHANNEL_ID)
            assert execute2.await_count == 3


class TestXpCooldownCache:
    async def test_cooldown_skips_db_write(self) -> None:
        import time

        _guild_config_cache.set(GUILD_ID, {"text_cooldown": 60})
        _last_xp_gain_cache[(GUILD_ID, USER_ID)] = time.time()
        with patch("api.execute_action", new=AsyncMock()) as action:
            await update_user_xp(GUILD_ID, USER_ID, 5, respect_cooldown=True)
        action.assert_not_awaited()

    async def test_different_users_independent_cooldowns(self) -> None:
        import time

        other_user = "900000000000000002"
        _guild_config_cache.set(GUILD_ID, {"text_cooldown": 60})
        _last_xp_gain_cache[(GUILD_ID, USER_ID)] = time.time()
        with patch("api.execute_action", new=AsyncMock()) as action:
            await update_user_xp(GUILD_ID, other_user, 5, respect_cooldown=True)
        action.assert_awaited_once()


class TestLogEnableTtlExpiry:
    async def test_log_enable_ttl_expiry_forces_refetch(self) -> None:
        execute = AsyncMock(return_value=[_LOG_ENABLE_ROW])
        t = 1000.0
        with patch("api.execute_query", new=execute), patch(
            "utils.cache.time.monotonic", side_effect=lambda: t
        ):
            await get_log_enable(GUILD_ID)
            assert _log_enable_calls(execute) == 1
        t += 61.0
        with patch("api.execute_query", new=execute), patch(
            "utils.cache.time.monotonic", side_effect=lambda: t
        ):
            await get_log_enable(GUILD_ID)
        assert _log_enable_calls(execute) == 2


class TestPreloadGuildConfigs:
    async def test_preload_guild_configs_single_query(self) -> None:
        from api import _guild_config_cache, preload_guild_configs, set_bot

        rows = [
            (GUILD_ID, 1, "medium", None, 1, "msg", CHANNEL_ID, 60, 60),
            ("900000000000000002", 0, "easy", None, 0, None, None, 30, 30),
        ]
        cursor = MagicMock()
        cursor.execute = AsyncMock()

        async def async_iter():
            for row in rows:
                yield row

        cursor.__aiter__ = lambda self: async_iter()
        cursor_cm = MagicMock()
        cursor_cm.__aenter__ = AsyncMock(return_value=cursor)
        cursor_cm.__aexit__ = AsyncMock(return_value=False)

        conn = MagicMock()
        conn.cursor.return_value = cursor_cm
        conn.__aenter__ = AsyncMock(return_value=conn)
        conn.__aexit__ = AsyncMock(return_value=False)

        pool = MagicMock()
        pool.acquire = AsyncMock(return_value=conn)

        bot = MagicMock()
        bot._pool = pool
        set_bot(bot)

        _guild_config_cache.set("stale_guild", {"active": False})
        await preload_guild_configs(bot)

        cursor.execute.assert_awaited_once()
        assert _guild_config_cache.get("stale_guild") is None
        assert _guild_config_cache.get(GUILD_ID) is not None
        assert _guild_config_cache.get("900000000000000002") is not None

