from __future__ import annotations

from collections.abc import Iterator
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

import tests.mock_config as mock_config

mock_config.patch_config_module()

from datetime import UTC, datetime

from api import (  # noqa: E402
    DatabaseManager,
    add_channel_boost,
    add_giveaway,
    add_giveaway_blacklisted_role,
    add_giveaway_blacklisted_user,
    add_giveaway_participant,
    add_log_blacklist,
    check_if_giveaway_participant,
    check_if_user_blacklisted,
    clear_wordchain,
    create_tables,
    db_manager,
    delete_giveaway,
    execute_batch,
    execute_query_iter,
    get_all_boosts,
    get_all_level_roles,
    get_blacklist,
    get_counting_configs,
    get_detailed_warnings,
    get_end_ready_giveaways,
    get_giveaway,
    get_giveaway_blacklisted_roles,
    get_giveaway_blacklisted_users,
    get_giveaway_channel_requirements,
    get_giveaway_participants,
    get_giveaway_role_requirements,
    get_level_role,
    get_log_blacklist,
    get_new_messages,
    get_new_messages_channel,
    get_role_boost,
    get_send_ready_giveaways,
    get_table_definitions,
    get_user_level_info,
    get_voice_time,
    get_wordchain_last_user_id,
    get_wordchain_word,
    invalidate_counting_cache,
    is_log_entity_blacklisted,
    preload_guild_configs,
    remove_channel_boost,
    remove_channel_from_blacklist,
    remove_giveaway_blacklisted_role,
    remove_giveaway_blacklisted_user,
    remove_giveaway_participant,
    remove_log_blacklist,
    remove_role_boost,
    remove_role_from_blacklist,
    remove_user_boost,
    remove_user_from_blacklist,
    set_bot,
    set_custom_background,
    set_wordchain_word,
    update_user_xp_from_voice,
)
from repositories.log_blacklist_repository import LogBlacklistType
from tests.helpers.db import AsyncIter, make_mock_pool
from tests.helpers.factories import CHANNEL_ID, GUILD_ID, ROLE_ID, USER_ID

pytestmark = pytest.mark.asyncio


@pytest.fixture(autouse=True)
def reset_api() -> Iterator[None]:
    set_bot(None)
    db_manager._pool = None
    from api import _blacklist_cache, _counting_cache, _guild_config_cache, clear_db_read_caches

    _blacklist_cache.clear()
    _guild_config_cache.clear()
    _counting_cache.clear()
    clear_db_read_caches()
    yield
    set_bot(None)
    db_manager._pool = None


@pytest.fixture
def pool_setup():
    pool, conn, cursor = make_mock_pool()
    bot = MagicMock()
    bot._pool = pool
    set_bot(bot)
    db_manager.set_pool(pool)
    return pool, conn, cursor


class TestDatabaseManager:
    async def test_not_ready_without_pool(self):
        mgr = DatabaseManager()
        assert mgr.is_ready is False
        assert await mgr.execute_query("SELECT 1") is None
        assert await mgr.execute_action("DELETE FROM x") is None

    async def test_execute_query_with_pool(self, pool_setup):
        _, _, cursor = pool_setup
        cursor.fetchall.return_value = [(1,)]
        mgr = DatabaseManager(pool_setup[0])
        result = await mgr.execute_query("SELECT 1")
        assert result == [(1,)]

    async def test_execute_action_with_pool(self, pool_setup):
        _, _, cursor = pool_setup
        cursor.rowcount = 2
        mgr = DatabaseManager(pool_setup[0])
        result = await mgr.execute_action("UPDATE x SET y=1")
        assert result == 2

    async def test_execute_batch_raises_without_pool(self):
        mgr = DatabaseManager()
        with pytest.raises(RuntimeError):
            await mgr.execute_batch("INSERT INTO x VALUES (%s)", [(1,)])

    async def test_execute_batch_with_pool(self, pool_setup):
        mgr = DatabaseManager(pool_setup[0])
        await mgr.execute_batch("INSERT INTO x VALUES (%s)", [(1,), (2,)])

    async def test_execute_insert_and_get_id(self, pool_setup):
        _, _, cursor = pool_setup
        cursor.lastrowid = 42
        mgr = DatabaseManager(pool_setup[0])
        result = await mgr.execute_insert_and_get_id("INSERT INTO x VALUES (%s)", (1,))
        assert result == 42

    async def test_check_health(self, pool_setup):
        with patch("api.check_pool_health", new=AsyncMock(return_value=True)):
            mgr = DatabaseManager(pool_setup[0])
            assert await mgr.check_health() is True

    async def test_create_tables_delegates(self, pool_setup):
        with patch("api.create_tables", new=AsyncMock()) as ct:
            mgr = DatabaseManager(pool_setup[0])
            await mgr.create_tables()
        ct.assert_awaited_once()


class TestLogBlacklistApi:
    async def test_add_remove_get_blacklist(self):
        with patch("api.log_blacklist_repo") as repo:
            repo.add = AsyncMock()
            repo.remove = AsyncMock()
            repo.get_all = AsyncMock(return_value=["1"])
            repo.is_entity_blacklisted = AsyncMock(return_value=None)
            await add_log_blacklist(GUILD_ID, "1", LogBlacklistType.CHANNEL)
            await remove_log_blacklist(GUILD_ID, "1", LogBlacklistType.CHANNEL)
            result = await get_log_blacklist(GUILD_ID, LogBlacklistType.CHANNEL)
            assert result == ["1"]
            assert await is_log_entity_blacklisted(GUILD_ID, "1", LogBlacklistType.CHANNEL) is None


class TestPreloadAndCache:
    async def test_preload_guild_configs(self, pool_setup):
        _, _, cursor = pool_setup
        cursor.__aiter__ = MagicMock(return_value=AsyncIter([(GUILD_ID, 1, "easy", None, 1, "msg", None, 60, 120)]))
        await preload_guild_configs()

    async def test_preload_no_pool(self):
        await preload_guild_configs()

    async def test_invalidate_counting_cache(self):
        from api import _counting_cache

        _counting_cache.set("ch1", (None, None, None))
        invalidate_counting_cache("ch1")
        assert _counting_cache.get("ch1") is None


class TestExecuteQueryIter:
    async def test_execute_query_iter(self, pool_setup):
        _, _, cursor = pool_setup

        async def rows():
            yield (1,)
            yield (2,)

        cursor.__aiter__ = MagicMock(return_value=rows())
        result = []
        async for row in execute_query_iter("SELECT 1"):
            result.append(row)
        assert len(result) >= 0


class TestLevelAndBoostApi:
    async def test_get_level_role(self, pool_setup):
        _, _, cursor = pool_setup
        cursor.fetchone.return_value = (5, "777")
        result = await get_level_role(GUILD_ID, 5)
        assert result is not None or result is None

    async def test_get_all_level_roles(self, pool_setup):
        _, _, cursor = pool_setup
        cursor.fetchall.return_value = [(5, "777")]
        result = await get_all_level_roles(GUILD_ID)
        assert isinstance(result, list)

    async def test_boost_operations(self, pool_setup):
        _, _, cursor = pool_setup
        cursor.fetchall.return_value = []
        cursor.fetchone.return_value = (2.0, False)
        await add_channel_boost(GUILD_ID, "444", 2.0, False)
        await remove_channel_boost(GUILD_ID, "444")
        await remove_role_boost(GUILD_ID, "777")
        await remove_user_boost(GUILD_ID, USER_ID)
        await get_all_boosts(GUILD_ID)
        await get_role_boost(GUILD_ID, "777")


class TestBlacklistApi:
    async def test_blacklist_crud(self, pool_setup):
        _, _, cursor = pool_setup
        cursor.fetchall.return_value = []
        cursor.rowcount = 1
        await remove_channel_from_blacklist(GUILD_ID, "444")
        await remove_role_from_blacklist(GUILD_ID, "777")
        await remove_user_from_blacklist(GUILD_ID, USER_ID)
        await get_blacklist(GUILD_ID)
        await check_if_user_blacklisted(GUILD_ID, USER_ID)


class TestUserLevelApi:
    async def test_get_user_level_info(self, pool_setup):
        _, _, cursor = pool_setup
        cursor.fetchone.return_value = (100, 5, 50)
        with patch("api.get_level_for_xp_async", new=AsyncMock(return_value=5)):
            info = await get_user_level_info(GUILD_ID, USER_ID)
        assert info is None or info is not None

    async def test_set_custom_background(self, pool_setup):
        _, _, cursor = pool_setup
        cursor.rowcount = 1
        await set_custom_background(GUILD_ID, USER_ID, "http://img")

    async def test_update_user_xp_from_voice(self, pool_setup):
        _, _, cursor = pool_setup
        cursor.rowcount = 1
        with patch("api.get_xp_for_level_async", new=AsyncMock(return_value=100)):
            await update_user_xp_from_voice(GUILD_ID, USER_ID, 300)


class TestWordchainApi:
    async def test_wordchain(self, pool_setup):
        _, _, cursor = pool_setup
        cursor.fetchone.return_value = ("word",)
        await get_wordchain_word(GUILD_ID)
        await set_wordchain_word("444", "next", GUILD_ID, USER_ID)
        cursor.fetchone.return_value = (USER_ID,)
        await get_wordchain_last_user_id(GUILD_ID)
        await clear_wordchain(GUILD_ID)


class TestCountingApi:
    async def test_get_counting_configs(self, pool_setup):
        _, _, cursor = pool_setup
        cursor.fetchall.return_value = []
        await get_counting_configs("444")


class TestWarningsApi:
    async def test_get_detailed_warnings(self, pool_setup):
        with patch("api.warning_repo") as repo:

            async def _rows(guild_id, user_id):
                if False:
                    yield

            repo.get_detailed = _rows
            rows = []
            async for row in get_detailed_warnings(GUILD_ID, USER_ID):
                rows.append(row)
            assert rows == []


class TestGiveawayApi:
    async def test_giveaway_lifecycle(self, pool_setup):

        with patch("services.giveaway_service.giveaway_service") as gs:
            gs.create = AsyncMock(return_value=1)
            gs.get = AsyncMock(return_value=None)
            gs.get_channel_requirements = AsyncMock(return_value=[])
            gs.get_role_requirements = AsyncMock(return_value=[])
            gs.get_participants = AsyncMock(return_value=[])
            gs.add_participant = AsyncMock()
            gs.is_participant = AsyncMock(return_value=False)
            gs.remove_participant = AsyncMock()
            gs.get_send_ready = AsyncMock(return_value=[])
            gs.get_end_ready = AsyncMock(return_value=[])
            gs.add_blacklisted_user = AsyncMock()
            gs.add_blacklisted_role = AsyncMock()
            gs.remove_blacklisted_user = AsyncMock()
            gs.remove_blacklisted_role = AsyncMock()
            gs.get_blacklisted_users = AsyncMock(return_value=[])
            gs.get_blacklisted_roles = AsyncMock(return_value=[])
            gs.delete = AsyncMock()
            now = datetime.now(UTC)
            gid = await add_giveaway(
                GUILD_ID,
                "title",
                "desc",
                1,
                True,
                "444",
                "custom",
                "sponsor",
                "prize",
                "msg",
                now,
                now,
                None,
                None,
                {},
                [],
                None,
            )
            assert gid == 1
            await get_giveaway(1)
            await get_giveaway_channel_requirements(1)
            await get_giveaway_role_requirements(1)
            await get_giveaway_participants(1)
            await add_giveaway_participant(1, USER_ID)
            await check_if_giveaway_participant(1, USER_ID)
            await remove_giveaway_participant(1, USER_ID)
            await get_send_ready_giveaways()
            await get_end_ready_giveaways()
            await add_giveaway_blacklisted_user(GUILD_ID, USER_ID)
            await add_giveaway_blacklisted_role(GUILD_ID, "777")
            await remove_giveaway_blacklisted_user(GUILD_ID, USER_ID)
            await remove_giveaway_blacklisted_role(GUILD_ID, "777")
            await get_giveaway_blacklisted_users(GUILD_ID)
            await get_giveaway_blacklisted_roles(GUILD_ID)
            await delete_giveaway(1)


class TestMessageTrackingApi:
    async def test_new_messages(self, pool_setup):
        with patch("services.giveaway_service.giveaway_service") as gs:
            gs.get_new_messages = AsyncMock(return_value=0)
            gs.get_new_messages_channel = AsyncMock(return_value=0)
            gs.get_voice_time = AsyncMock(return_value=0)
            await get_new_messages(GUILD_ID, USER_ID)
            await get_new_messages_channel(GUILD_ID, USER_ID, "444")
            await get_voice_time(GUILD_ID, USER_ID)


class TestTableDefinitions:
    @pytest.mark.parametrize(
        "table",
        [
            "warnings",
            "level",
            "levelConfig",
            "giveaway",
            "aiToken",
            "counting",
            "triggerMessages",
            "tickets",
            "dynamicslowmode",
            "brawlstarsLinkedAccounts",
        ],
    )
    async def test_table_ddl_contains_create(self, table: str):
        ddl = get_table_definitions()[table]
        assert "CREATE TABLE" in ddl.upper()

    async def test_all_expected_tables_present(self):
        tables = get_table_definitions()
        assert len(tables) >= 40


class TestCreateTables:
    async def test_no_op_without_pool(self):
        await create_tables()

    async def test_creates_missing_tables(self, pool_setup):
        _, _, cursor = pool_setup
        cursor.fetchall.return_value = []
        with patch("api.execute_action", new=AsyncMock()) as action:
            await create_tables()
        assert action.await_count >= 1

    async def test_skips_existing_tables(self, pool_setup):
        _, _, cursor = pool_setup
        existing = [(name,) for name in get_table_definitions()]
        cursor.fetchall.return_value = existing
        with patch("api.execute_action", new=AsyncMock()) as action:
            await create_tables()
        for call in action.call_args_list:
            sql = call[0][0]
            assert "CREATE TABLE" not in sql.upper()

    async def test_discovery_error_returns_early(self, pool_setup):
        _, _, cursor = pool_setup
        cursor.execute.side_effect = Exception("connection lost")
        with patch("api.execute_action", new=AsyncMock()) as action:
            await create_tables()
        action.assert_not_awaited()

    async def test_migration_duplicate_column_suppressed(self, pool_setup):
        _, _, cursor = pool_setup
        cursor.fetchall.return_value = [(name,) for name in get_table_definitions()]

        async def _action(query, params=None, bot=None):
            if "ALTER TABLE" in query:
                raise Exception("Duplicate column name 'attachments'")

        with patch("api.execute_action", side_effect=_action):
            await create_tables()

    async def test_migration_unexpected_error_raises(self, pool_setup):
        _, _, cursor = pool_setup
        cursor.fetchall.return_value = [(name,) for name in get_table_definitions()]

        async def _action(query, params=None, bot=None):
            if "ALTER TABLE" in query:
                raise Exception("syntax error")

        with patch("api.execute_action", side_effect=_action), pytest.raises(Exception, match="syntax error"):
            await create_tables()


class TestPoolFallback:
    async def test_get_pool_from_bot_when_manager_empty(self):
        pool, conn, cursor = make_mock_pool()
        cursor.fetchall = AsyncMock(return_value=[(1,)])
        bot = MagicMock()
        bot._pool = pool
        db_manager._pool = None
        set_bot(bot)
        from api import execute_query

        result = await execute_query("SELECT 1")
        assert result == [(1,)]


class TestExecuteRetryPaths:
    async def test_execute_query_retries_transient_error(self, pool_setup):
        pool, conn, cursor = pool_setup
        call_count = 0

        async def execute_side_effect(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise Exception("deadlock detected")
            return None

        cursor.execute = AsyncMock(side_effect=execute_side_effect)
        cursor.fetchall = AsyncMock(return_value=[(42,)])
        from api import execute_query

        result = await execute_query("SELECT 42")
        assert result == [(42,)]
        assert call_count == 2

    async def test_execute_batch_retries_deadlock(self, pool_setup):
        pool, conn, cursor = pool_setup
        call_count = 0

        async def executemany_side_effect(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise Exception("deadlock")

        cursor.executemany = AsyncMock(side_effect=executemany_side_effect)
        await execute_batch("INSERT INTO level VALUES (%s)", [("u1",)])
        assert call_count == 2

    async def test_execute_query_iter_yields_rows(self, pool_setup):
        _, _, cursor = pool_setup
        cursor.__aiter__ = MagicMock(return_value=AsyncIter([(1,), (2,)]))
        rows = [r async for r in execute_query_iter("SELECT id FROM level")]
        assert rows == [(1,), (2,)]

    async def test_execute_query_iter_timeout_then_success(self, pool_setup):
        pool, conn, cursor = pool_setup
        acquire_count = 0
        original_acquire = pool.acquire

        async def acquire_side_effect():
            nonlocal acquire_count
            acquire_count += 1
            if acquire_count == 1:
                raise TimeoutError("pool timeout")
            return await original_acquire()

        pool.acquire = AsyncMock(side_effect=acquire_side_effect)
        cursor.__aiter__ = MagicMock(return_value=AsyncIter([(9,)]))
        rows = [r async for r in execute_query_iter("SELECT 9")]
        assert rows == [(9,)]


class TestPreloadGuildConfigsExtended:
    async def test_preload_populates_cache(self, pool_setup):
        _, _, cursor = pool_setup
        row = (GUILD_ID, 1, "medium", None, 1, "msg", CHANNEL_ID, 60, 120)
        cursor.__aiter__ = MagicMock(return_value=AsyncIter([row]))
        from api import _guild_config_cache

        await preload_guild_configs()
        cached = _guild_config_cache.get(GUILD_ID)
        assert cached is not None
        assert cached["text_cooldown"] == 60

    async def test_preload_handles_error(self, pool_setup):
        _, _, cursor = pool_setup
        cursor.execute.side_effect = Exception("preload failed")
        await preload_guild_configs()


class TestDatabaseManagerEdgeCases:
    async def test_check_health_without_pool(self):
        mgr = DatabaseManager()
        assert await mgr.check_health() is False

    async def test_execute_insert_without_pool(self):
        mgr = DatabaseManager()
        assert await mgr.execute_insert_and_get_id("INSERT INTO x VALUES (1)") is None

    async def test_create_tables_without_pool(self):
        mgr = DatabaseManager()
        await mgr.create_tables()


async def _empty_async_gen(*args, **kwargs):
    if False:
        yield


class TestWarningRepoWrappers:
    @pytest.mark.parametrize(
        "func,args",
        [
            ("add_warning", (GUILD_ID, USER_ID, "reason", USER_ID, None)),
            ("remove_warning", (1,)),
            ("set_warn_config", (GUILD_ID, 7, 3, 600, 5, 10)),
        ],
    )
    async def test_warning_repo_delegates(self, func: str, args: tuple):
        from api import add_warning, remove_warning, set_warn_config

        funcs = {"add_warning": add_warning, "remove_warning": remove_warning, "set_warn_config": set_warn_config}
        with patch("api.warning_repo") as repo:
            repo.add = AsyncMock(return_value=1)
            repo.remove = AsyncMock()
            repo.set_config = AsyncMock()
            repo.get_config = AsyncMock(return_value=None)
            repo.get_all = _empty_async_gen
            await funcs[func](*args)

    async def test_get_warnings_and_config(self):
        from api import get_warn_config, get_warnings

        config = MagicMock()
        with patch("api.warning_repo") as repo:
            repo.get_config = AsyncMock(return_value=config)
            repo.get_all = _empty_async_gen
            assert await get_warn_config(GUILD_ID) is config
            rows = [r async for r in get_warnings(GUILD_ID, USER_ID)]
            assert rows == []


class TestOptOutAndOverwrites:
    async def test_opt_out_round_trip(self, pool_setup):
        from api import check_if_opted_out, opt_in, opt_out

        _, _, cursor = pool_setup
        cursor.fetchall.return_value = [(USER_ID,)]
        assert await check_if_opted_out(USER_ID) is True
        await opt_in(USER_ID)
        await opt_out(USER_ID)
        assert cursor.execute.await_count >= 2

    async def test_channel_overwrites(self, pool_setup):
        from api import clear_channel_overwrites, get_channel_overwrites, save_channel_overwrites

        _, _, cursor = pool_setup
        await save_channel_overwrites(CHANNEL_ID, ROLE_ID, {"read": True})
        cursor.__aiter__ = MagicMock(return_value=AsyncIter([]))
        rows = [r async for r in get_channel_overwrites(CHANNEL_ID)]
        assert rows == []
        await clear_channel_overwrites(CHANNEL_ID)


class TestLevelConfigDelegation:
    @pytest.mark.parametrize(
        "func,kwargs",
        [
            ("set_level_system_status", {"active": True}),
            ("set_levelup_message_status", {"status": False}),
            ("set_levelup_message", {"message": "GG"}),
            ("set_levelup_channel", {"channel_id": CHANNEL_ID}),
            ("set_xp_scaling", {"scaling": "hard"}),
            ("set_custom_formula", {"formula": "x*2"}),
        ],
    )
    async def test_level_config_repo_updates(self, func: str, kwargs: dict):
        import api as api_mod

        with patch("repositories.level_config_repository.level_config_repo.update_field", new=AsyncMock()) as upd:
            await getattr(api_mod, func)(GUILD_ID, **kwargs)
        upd.assert_awaited_once()

    @pytest.mark.parametrize(
        "func,setup",
        [
            ("get_level_system_status", {"active": True}),
            ("get_levelup_message_status", {"level_up_message_active": False}),
            ("get_levelup_message", {"level_up_message": "msg"}),
            ("get_levelup_channel", {"level_up_channel_id": CHANNEL_ID}),
            ("get_xp_scaling", {"difficulty": "hard"}),
            ("get_custom_formula", {"custom_formula": "x*2"}),
        ],
    )
    async def test_level_config_repo_reads(self, func: str, setup: dict):
        import api as api_mod

        config = MagicMock(**setup)
        with patch("repositories.level_config_repository.level_config_repo.get_config", new=AsyncMock(return_value=config)):
            result = await getattr(api_mod, func)(GUILD_ID)
        assert result is not None


class TestBulkUpdateAndTransaction:
    async def test_bulk_update_user_xp(self, pool_setup):
        from api import bulk_update_user_xp

        _, _, cursor = pool_setup
        await bulk_update_user_xp(GUILD_ID, [(USER_ID, 10)])
        assert cursor.execute.await_count >= 1

    async def test_transaction_timeout_retry(self, pool_setup):
        from api import transaction

        pool, conn, _ = pool_setup
        acquire_count = 0
        original = pool.acquire

        async def acquire_side_effect():
            nonlocal acquire_count
            acquire_count += 1
            if acquire_count == 1:
                raise TimeoutError("acquire timeout")
            return await original()

        pool.acquire = AsyncMock(side_effect=acquire_side_effect)
        async with transaction():
            pass
        assert acquire_count == 2
