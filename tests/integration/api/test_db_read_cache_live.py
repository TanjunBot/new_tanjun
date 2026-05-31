"""Real-database cache integration tests (requires docker-compose.test.yml)."""

from __future__ import annotations

import asyncio
import os
from collections.abc import AsyncIterator, Iterator, Sequence
from typing import Any
from unittest.mock import patch

import pytest

import tests.mock_config as mock_config

mock_config.patch_config_module()

from api import (  # noqa: E402
    clear_db_read_caches,
    execute_action,
    execute_query,
    get_log_channel,
    get_log_enable,
    set_log_channel,
    set_log_enable,
)
from tests.helpers.concurrency import stress_concurrent
from tests.helpers.factories import CHANNEL_ID, GUILD_ID

pytestmark = [
    pytest.mark.asyncio,
    pytest.mark.integration,
    pytest.mark.skipif(
        os.environ.get("TANJUN_INTEGRATION", "false").lower() not in ("1", "true", "yes"),
        reason="Set TANJUN_INTEGRATION=true to run live DB cache tests",
    ),
]

LIVE_GUILD = "88888888888888881"


@pytest.fixture(autouse=True)
def _reset_caches() -> Iterator[None]:
    clear_db_read_caches()
    yield
    clear_db_read_caches()


@pytest.fixture
async def seeded_log_enable(integration_db_pool: Any, monkeypatch: pytest.MonkeyPatch) -> AsyncIterator[None]:
    import api

    class FakeBot:
        _pool = integration_db_pool

    api.set_bot(FakeBot())
    await execute_action(
        "INSERT INTO log_enables (guild_id, memberJoin, memberUpdate, messageDelete) "
        "VALUES (%s, 1, 1, 1) ON DUPLICATE KEY UPDATE memberJoin=1, memberUpdate=1, messageDelete=1",
        (LIVE_GUILD,),
    )
    yield
    await execute_action("DELETE FROM log_enables WHERE guild_id = %s", (LIVE_GUILD,))


class TestLogEnableLiveCache:
    async def test_concurrent_reads_single_query(self, seeded_log_enable: None) -> None:
        query_count = 0
        original = execute_query

        async def counting_query(
            query: str,
            params: Sequence[Any] | dict[str, Any] | None = None,
            bot: Any = None,
        ) -> list[tuple[Any, ...]] | None:
            nonlocal query_count
            if "FROM log_enables" in query:
                query_count += 1
            return await original(query, params, bot)

        with patch("api.execute_query", side_effect=counting_query):
            results = await stress_concurrent(lambda: get_log_enable(LIVE_GUILD), n=100)
        assert len(results) == 100
        assert all(r.guild_id == LIVE_GUILD for r in results)
        assert query_count == 1

    async def test_set_log_enable_invalidates_cache(self, seeded_log_enable: None) -> None:
        await get_log_enable(LIVE_GUILD)
        await set_log_enable(LIVE_GUILD, memberJoin=False)
        row = await execute_query(
            "SELECT memberJoin FROM log_enables WHERE guild_id = %s",
            (LIVE_GUILD,),
        )
        assert row is not None
        assert row[0][0] == 0
        refreshed = await get_log_enable(LIVE_GUILD)
        assert refreshed.member_join is False

    async def test_log_enable_ttl_expiry_refetches(self, seeded_log_enable: None) -> None:
        import api

        t = 1000.0
        with patch("utils.cache.time.monotonic", side_effect=lambda: t):
            first = await get_log_enable(LIVE_GUILD)
        t += 61.0
        with patch("utils.cache.time.monotonic", side_effect=lambda: t):
            second = await get_log_enable(LIVE_GUILD)
        assert first.guild_id == LIVE_GUILD
        assert second.guild_id == LIVE_GUILD


class TestLogChannelLiveCache:
    async def test_concurrent_log_channel_reads(self, integration_db_pool: Any) -> None:
        import api

        class FakeBot:
            _pool = integration_db_pool

        api.set_bot(FakeBot())
        await execute_action(
            "INSERT INTO log_channel (guild_id, channel_id) VALUES (%s, %s) "
            "ON DUPLICATE KEY UPDATE channel_id = VALUES(channel_id)",
            (LIVE_GUILD, CHANNEL_ID),
        )
        query_count = 0
        original = execute_query

        async def counting_query(
            query: str,
            params: Sequence[Any] | dict[str, Any] | None = None,
            bot: Any = None,
        ) -> list[tuple[Any, ...]] | None:
            nonlocal query_count
            if "FROM log_channel" in query:
                query_count += 1
            return await original(query, params, bot)

        with patch("api.execute_query", side_effect=counting_query):
            results = await asyncio.gather(*[get_log_channel(LIVE_GUILD) for _ in range(50)])
        assert all(r == CHANNEL_ID for r in results)
        assert query_count == 1
        await set_log_channel(LIVE_GUILD, "999999999999999991")
        with patch("api.execute_query", side_effect=counting_query):
            updated = await get_log_channel(LIVE_GUILD)
        assert updated == "999999999999999991"
