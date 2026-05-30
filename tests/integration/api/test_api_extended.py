"""Parametrized behavioral tests for additional api.py surface area."""

from __future__ import annotations

from collections.abc import Iterator
from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

import tests.mock_config as mock_config

mock_config.patch_config_module()

from api import (  # noqa: E402
    add_brawlstars_linked_account,
    add_channel_boost,
    add_dynamicslowmode,
    add_giveaway_blacklisted_role,
    add_giveaway_blacklisted_user,
    add_log_blacklist,
    add_media_channel,
    add_trigger_message,
    add_user_to_blacklist,
    addAutoPublish,
    addToken,
    check_if_user_blacklisted,
    checkIfChannelIsAutopublish,
    clear_wordchain,
    consumePaidToken,
    execute_batch,
    execute_insert_and_get_id,
    execute_query_iter,
    feedbackBlockUser,
    feedbackIsBlocked,
    feedbackUnblockUser,
    get_all_boosts,
    get_blacklist,
    get_brawlstars_linked_account,
    get_counting_configs,
    get_custom_formula,
    get_detailed_warnings,
    get_dynamicslowmode,
    get_level_role,
    get_log_blacklist,
    get_media_channel,
    get_role_boost,
    get_text_cooldown,
    get_trigger_messages,
    get_user_level_info,
    get_user_xp,
    get_voice_cooldown,
    get_wordchain_last_user_id,
    get_wordchain_word,
    getToken,
    getTokenOverview,
    includeToToken,
    invalidate_counting_cache,
    is_log_entity_blacklisted,
    remove_channel_boost,
    remove_channel_from_blacklist,
    remove_log_blacklist,
    remove_role_boost,
    remove_user_boost,
    remove_user_from_blacklist,
    removeAutoPublish,
    resetToken,
    set_bot,
    set_custom_background,
    set_text_cooldown,
    set_voice_cooldown,
    set_wordchain_word,
    update_user_xp,
    useToken,
)
from repositories.log_blacklist_repository import LogBlacklistType  # noqa: E402
from tests.helpers.db import AsyncIter, make_bot, make_mock_pool  # noqa: E402
from tests.helpers.factories import CHANNEL_ID, GUILD_ID, MESSAGE_ID, ROLE_ID, USER_ID  # noqa: E402

GUILD_VARIANTS = [GUILD_ID, "11111111111111111", "22222222222222222"]
USER_VARIANTS = [USER_ID, "33333333333333333", "44444444444444444"]
CHANNEL_VARIANTS = [CHANNEL_ID, "55555555555555555", "66666666666666666"]
ROLE_VARIANTS = [ROLE_ID, "88888888888888888", "99999999999999999"]


@pytest.fixture(autouse=True)
def reset_globals() -> Iterator[None]:
    set_bot(None)
    from api import _blacklist_cache, _counting_cache, _guild_config_cache

    _guild_config_cache.clear()
    _blacklist_cache.clear()
    _counting_cache.clear()
    yield


@pytest.fixture
def bot_with_pool() -> tuple[MagicMock, AsyncMock]:
    pool, _, cursor = make_mock_pool()
    bot, _ = make_bot(pool)
    return bot, cursor


def _patch_execute_query(side_effects: list):
    return patch("api.execute_query", side_effect=side_effects)


class TestExecuteBatch:
    @pytest.mark.parametrize("row_count", [1, 5, 10, 25, 50])
    @pytest.mark.asyncio
    async def test_executemany_called_for_each_batch(self, bot_with_pool, row_count: int):
        _, cursor = bot_with_pool
        cursor.executemany = AsyncMock()
        params = [(f"u{i}", GUILD_ID, i) for i in range(row_count)]
        await execute_batch("INSERT INTO level VALUES (%s, %s, %s)", params)
        cursor.executemany.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_raises_without_pool(self):
        with pytest.raises(RuntimeError, match="Database pool is not initialized"):
            await execute_batch("INSERT INTO t VALUES (%s)", [("a",)])


class TestExecuteInsertAndGetId:
    @pytest.mark.parametrize("insert_id", [1, 42, 999, 12345, 999999])
    @pytest.mark.asyncio
    async def test_returns_last_insert_id(self, bot_with_pool, insert_id: int):
        _, cursor = bot_with_pool
        cursor.fetchone = AsyncMock(return_value=(insert_id,))
        result = await execute_insert_and_get_id("INSERT INTO warnings VALUES (%s)", ("x",))
        assert result == insert_id

    @pytest.mark.asyncio
    async def test_returns_none_without_pool(self):
        result = await execute_insert_and_get_id("INSERT INTO t VALUES (1)")
        assert result is None


class TestExecuteQueryIter:
    @pytest.mark.parametrize("rows", [[], [(1,)], [(1, 2), (3, 4)], [(i,) for i in range(10)]])
    @pytest.mark.asyncio
    async def test_yields_all_rows(self, bot_with_pool, rows: list[tuple]):
        _, cursor = bot_with_pool
        cursor.__aiter__ = MagicMock(return_value=AsyncIter(rows))
        collected = [row async for row in execute_query_iter("SELECT 1")]
        assert collected == rows

    @pytest.mark.asyncio
    async def test_empty_when_no_pool(self):
        collected = [row async for row in execute_query_iter("SELECT 1")]
        assert collected == []


class TestCountingCache:
    @pytest.mark.parametrize("channel_id", CHANNEL_VARIANTS)
    @pytest.mark.asyncio
    async def test_invalidate_clears_cached_configs(self, channel_id: str):
        invalidate_counting_cache(channel_id)
        with _patch_execute_query([None, None, None]) as mock_eq:
            await get_counting_configs(channel_id)
            assert mock_eq.await_count == 3
        with _patch_execute_query([None, None, None]) as mock_eq2:
            await get_counting_configs(channel_id)
            assert mock_eq2.await_count == 0
        invalidate_counting_cache(channel_id)
        with _patch_execute_query([None, None, None]) as mock_eq3:
            await get_counting_configs(channel_id)
            assert mock_eq3.await_count == 3

    @pytest.mark.parametrize("progress", [0, 1, 42, 100, 9999])
    @pytest.mark.asyncio
    async def test_parses_counting_config(self, bot_with_pool, progress: int):
        _, cursor = bot_with_pool
        cursor.fetchall = AsyncMock(
            side_effect=[
                [(progress, USER_ID, GUILD_ID)],
                None,
                None,
            ]
        )
        with patch("api.execute_query", new=AsyncMock(side_effect=cursor.fetchall.side_effect)):
            normal, challenge, modes = await get_counting_configs(CHANNEL_ID)
        assert normal is not None
        assert normal["progress"] == progress
        assert challenge is None
        assert modes is None


class TestWordchain:
    @pytest.mark.parametrize("word", ["hello", "world", "discord", "pytest", "tanjun"])
    @pytest.mark.asyncio
    async def test_set_and_get_wordchain_word(self, bot_with_pool, word: str):
        _, cursor = bot_with_pool
        cursor.fetchall = AsyncMock(return_value=[(word,)])
        await set_wordchain_word(CHANNEL_ID, word, GUILD_ID, USER_ID)
        cursor.execute.assert_awaited()
        with patch("api.execute_query", new=AsyncMock(return_value=[(word,)])):
            result = await get_wordchain_word(CHANNEL_ID)
        assert result == word

    @pytest.mark.parametrize("user_id", USER_VARIANTS)
    @pytest.mark.asyncio
    async def test_get_wordchain_last_user(self, bot_with_pool, user_id: str):
        with patch("api.execute_query", new=AsyncMock(return_value=[(user_id,)])):
            result = await get_wordchain_last_user_id(CHANNEL_ID)
        assert result == user_id

    @pytest.mark.asyncio
    async def test_clear_wordchain_executes_delete(self, bot_with_pool):
        _, cursor = bot_with_pool
        await clear_wordchain(CHANNEL_ID)
        cursor.execute.assert_awaited()


class TestBlacklistExtended:
    @pytest.mark.parametrize("guild_id", GUILD_VARIANTS)
    @pytest.mark.asyncio
    async def test_add_and_remove_user_blacklist(self, bot_with_pool, guild_id: str):
        _, cursor = bot_with_pool
        await add_user_to_blacklist(guild_id, USER_ID, "spam")
        await remove_user_from_blacklist(guild_id, USER_ID)
        assert cursor.execute.await_count >= 2

    @pytest.mark.parametrize("guild_id", GUILD_VARIANTS)
    @pytest.mark.asyncio
    async def test_remove_channel_from_blacklist(self, bot_with_pool, guild_id: str):
        _, cursor = bot_with_pool
        await remove_channel_from_blacklist(guild_id, CHANNEL_ID)
        sql = cursor.execute.call_args[0][0]
        assert "DELETE" in sql

    @pytest.mark.asyncio
    @pytest.mark.asyncio
    async def test_get_blacklist_returns_structure(self, bot_with_pool):
        _, cursor = bot_with_pool
        cursor.__aiter__ = MagicMock(return_value=AsyncIter([]))
        result = await get_blacklist(GUILD_ID)
        assert "users" in result
        assert "channels" in result
        assert "roles" in result


class TestXpAndLevelExtended:
    @pytest.mark.parametrize("xp_amount", [1, 10, 50, 100, 500])
    @pytest.mark.asyncio
    async def test_update_user_xp_executes_upsert(self, bot_with_pool, xp_amount: int):
        _, cursor = bot_with_pool
        await update_user_xp(GUILD_ID, USER_ID, xp_amount)
        cursor.execute.assert_awaited()
        sql = cursor.execute.call_args[0][0]
        assert "level" in sql.lower()

    @pytest.mark.parametrize("xp_value", [None, 0, 100, 5000])
    @pytest.mark.asyncio
    async def test_get_user_xp(self, bot_with_pool, xp_value: int | None):
        fetch = [(xp_value,)] if xp_value is not None else None
        with patch("api.execute_query", new=AsyncMock(return_value=fetch)):
            result = await get_user_xp(GUILD_ID, USER_ID)
        if xp_value is None:
            assert result is None
        else:
            assert result == xp_value

    @pytest.mark.asyncio
    async def test_get_user_level_info_none_when_missing(self, bot_with_pool):
        with (
            patch("api.execute_query", new=AsyncMock(return_value=None)),
            patch("api.get_xp_scaling", new=AsyncMock(return_value="medium")),
            patch("api.get_custom_formula", new=AsyncMock(return_value=None)),
        ):
            result = await get_user_level_info(GUILD_ID, USER_ID)
        assert result is None

    @pytest.mark.asyncio
    async def test_set_custom_background(self, bot_with_pool):
        _, cursor = bot_with_pool
        await set_custom_background(GUILD_ID, USER_ID, "https://example.com/bg.png")
        cursor.execute.assert_awaited()


class TestBoostExtended:
    @pytest.mark.parametrize("boost", [1.0, 1.5, 2.0, 3.0, 5.0])
    @pytest.mark.asyncio
    async def test_add_and_remove_channel_boost(self, bot_with_pool, boost: float):
        _, cursor = bot_with_pool
        await add_channel_boost(GUILD_ID, CHANNEL_ID, boost, True)
        await remove_channel_boost(GUILD_ID, CHANNEL_ID)
        assert cursor.execute.await_count >= 2

    @pytest.mark.parametrize("role_id", ROLE_VARIANTS)
    @pytest.mark.asyncio
    async def test_remove_role_boost(self, bot_with_pool, role_id: str):
        _, cursor = bot_with_pool
        await remove_role_boost(GUILD_ID, role_id)
        assert "DELETE" in cursor.execute.call_args[0][0]

    @pytest.mark.parametrize("user_id", USER_VARIANTS)
    @pytest.mark.asyncio
    async def test_remove_user_boost(self, bot_with_pool, user_id: str):
        _, cursor = bot_with_pool
        await remove_user_boost(GUILD_ID, user_id)
        cursor.execute.assert_awaited()

    @pytest.mark.asyncio
    async def test_get_all_boosts_empty(self, bot_with_pool):
        with patch("api.execute_query", new=AsyncMock(return_value=[])):
            result = await get_all_boosts(GUILD_ID)
        assert isinstance(result, dict)

    @pytest.mark.asyncio
    async def test_get_role_boost_none(self, bot_with_pool):
        with patch("api.execute_query", new=AsyncMock(return_value=[])):
            result = await get_role_boost(GUILD_ID, ROLE_ID)
        assert result is None


class TestLevelRoleExtended:
    @pytest.mark.parametrize("level", [1, 5, 10, 25, 50])
    @pytest.mark.asyncio
    async def test_get_level_role(self, bot_with_pool, level: int):
        with patch("api.execute_query", new=AsyncMock(return_value=[(level,)])):
            result = await get_level_role(GUILD_ID, ROLE_ID)
        assert result == level

    @pytest.mark.asyncio
    async def test_get_detailed_warnings_empty(self, bot_with_pool):
        _, cursor = bot_with_pool
        cursor.__aiter__ = MagicMock(return_value=AsyncIter([]))
        rows = [row async for row in get_detailed_warnings(GUILD_ID, USER_ID)]
        assert rows == []


class TestCooldowns:
    @pytest.mark.parametrize("seconds", [0, 30, 60, 120, 300])
    @pytest.mark.asyncio
    async def test_set_text_cooldown(self, bot_with_pool, seconds: int):
        _, cursor = bot_with_pool
        await set_text_cooldown(GUILD_ID, seconds)
        cursor.execute.assert_awaited()

    @pytest.mark.parametrize("seconds", [0, 60, 180, 600, 900])
    @pytest.mark.asyncio
    async def test_set_voice_cooldown(self, bot_with_pool, seconds: int):
        _, cursor = bot_with_pool
        await set_voice_cooldown(GUILD_ID, seconds)
        cursor.execute.assert_awaited()


class TestTokens:
    @pytest.mark.parametrize("amount", [1, 5, 10, 50, 100])
    @pytest.mark.asyncio
    async def test_add_and_use_token(self, bot_with_pool, amount: int):
        _, cursor = bot_with_pool
        await addToken(USER_ID, amount)
        await useToken(USER_ID, amount)
        assert cursor.execute.await_count >= 2

    @pytest.mark.parametrize("free,plus,paid", [(500, 0, 0), (100, 200, 50), (0, 2000, 100)])
    @pytest.mark.asyncio
    async def test_get_token_sum(self, bot_with_pool, free: int, plus: int, paid: int):
        with patch("api.execute_query", new=AsyncMock(return_value=[(free, plus, paid)])):
            total = await getToken(USER_ID)
        assert total == free + plus + paid

    @pytest.mark.asyncio
    async def test_get_token_overview_none(self, bot_with_pool):
        with patch("api.execute_query", new=AsyncMock(return_value=None)):
            result = await getTokenOverview(USER_ID)
        assert result is None

    @pytest.mark.asyncio
    async def test_include_to_token(self, bot_with_pool):
        _, cursor = bot_with_pool
        await includeToToken(USER_ID)
        assert "aiToken" in cursor.execute.call_args[0][0]

    @pytest.mark.asyncio
    async def test_reset_token(self, bot_with_pool):
        _, cursor = bot_with_pool
        await resetToken(None)
        cursor.execute.assert_awaited()

    @pytest.mark.asyncio
    async def test_consume_paid_token(self, bot_with_pool):
        _, cursor = bot_with_pool
        await consumePaidToken(USER_ID, 10)
        cursor.execute.assert_awaited()


class TestFeedback:
    @pytest.mark.parametrize("user_id", USER_VARIANTS)
    @pytest.mark.asyncio
    async def test_block_unblock_feedback(self, bot_with_pool, user_id: str):
        _, cursor = bot_with_pool
        await feedbackBlockUser(user_id)
        await feedbackUnblockUser(user_id)
        assert cursor.execute.await_count >= 2

    @pytest.mark.parametrize("blocked", [True, False])
    @pytest.mark.asyncio
    async def test_feedback_is_blocked(self, bot_with_pool, blocked: bool):
        rows = [(user_id,) for user_id in [USER_ID]] if blocked else []
        with patch("api.execute_query", new=AsyncMock(return_value=rows)):
            result = await feedbackIsBlocked(USER_ID)
        assert result is blocked


class TestAutoPublish:
    @pytest.mark.parametrize("channel_id", CHANNEL_VARIANTS)
    @pytest.mark.asyncio
    async def test_autopublish_round_trip(self, bot_with_pool, channel_id: str):
        _, cursor = bot_with_pool
        await addAutoPublish(channel_id)
        await removeAutoPublish(channel_id)
        assert cursor.execute.await_count >= 2

    @pytest.mark.parametrize("exists", [True, False])
    @pytest.mark.asyncio
    async def test_check_autopublish(self, bot_with_pool, exists: bool):
        rows = [(channel_id,) for channel_id in [CHANNEL_ID]] if exists else []
        with patch("api.execute_query", new=AsyncMock(return_value=rows)):
            result = await checkIfChannelIsAutopublish(CHANNEL_ID)
        assert result is exists


class TestMediaChannels:
    @pytest.mark.parametrize("channel_id", CHANNEL_VARIANTS)
    @pytest.mark.asyncio
    async def test_add_media_channel(self, bot_with_pool, channel_id: str):
        _, cursor = bot_with_pool
        await add_media_channel(GUILD_ID, channel_id)
        cursor.execute.assert_awaited()

    @pytest.mark.parametrize("exists", [True, False])
    @pytest.mark.asyncio
    async def test_get_media_channel(self, bot_with_pool, exists: bool):
        with patch("api.execute_query", new=AsyncMock(return_value=[(1,)] if exists else None)):
            result = await get_media_channel(CHANNEL_ID)
        assert result is exists


class TestTriggerMessages:
    @pytest.mark.parametrize("trigger,response", [("hi", "hello"), ("ping", "pong"), ("!help", "docs")])
    @pytest.mark.asyncio
    async def test_add_trigger_message(self, bot_with_pool, trigger: str, response: str):
        _, cursor = bot_with_pool
        await add_trigger_message(GUILD_ID, trigger, response)
        cursor.execute.assert_awaited()

    @pytest.mark.asyncio
    async def test_get_trigger_messages_empty(self, bot_with_pool):
        with patch("api.execute_query", new=AsyncMock(return_value=[])):
            result = await get_trigger_messages(GUILD_ID)
        assert result == []


class TestDynamicSlowmode:
    @pytest.mark.parametrize("messages,per,reset", [(5, 10, 60), (10, 30, 120), (3, 5, 30)])
    @pytest.mark.asyncio
    async def test_add_dynamicslowmode(self, bot_with_pool, messages: int, per: int, reset: int):
        _, cursor = bot_with_pool
        await add_dynamicslowmode(GUILD_ID, CHANNEL_ID, messages, per, reset)
        cursor.execute.assert_awaited()

    @pytest.mark.asyncio
    async def test_get_dynamicslowmode_none(self, bot_with_pool):
        with patch("api.execute_query", new=AsyncMock(return_value=None)):
            result = await get_dynamicslowmode(CHANNEL_ID)
        assert result is None


class TestBrawlstars:
    @pytest.mark.parametrize("tag", ["#ABC", "#TEST123", "#PLAYER"])
    @pytest.mark.asyncio
    async def test_brawlstars_link(self, bot_with_pool, tag: str):
        _, cursor = bot_with_pool
        await add_brawlstars_linked_account(USER_ID, tag)
        with patch("api.execute_query", new=AsyncMock(return_value=[(tag,)])):
            result = await get_brawlstars_linked_account(USER_ID)
        assert result == tag


class TestGiveawayBlacklist:
    @pytest.mark.parametrize("user_id", USER_VARIANTS)
    @pytest.mark.asyncio
    async def test_giveaway_user_blacklist(self, bot_with_pool, user_id: str):
        _, cursor = bot_with_pool
        await add_giveaway_blacklisted_user(GUILD_ID, user_id)
        with patch("services.giveaway_service.giveaway_service.is_user_blacklisted", new=AsyncMock(return_value=True)):
            blocked = await check_if_user_blacklisted(GUILD_ID, user_id)
        assert blocked is True
        cursor.execute.assert_awaited()

    @pytest.mark.parametrize("role_id", ROLE_VARIANTS)
    @pytest.mark.asyncio
    async def test_giveaway_role_blacklist(self, bot_with_pool, role_id: str):
        _, cursor = bot_with_pool
        await add_giveaway_blacklisted_role(GUILD_ID, role_id)
        cursor.execute.assert_awaited()


class TestLogBlacklist:
    @pytest.mark.parametrize("bl_type", list(LogBlacklistType))
    @pytest.mark.asyncio
    async def test_log_blacklist_add_remove(self, bot_with_pool, bl_type: LogBlacklistType):
        with (
            patch("api.log_blacklist_repo.add", new=AsyncMock()) as add_mock,
            patch("api.log_blacklist_repo.remove", new=AsyncMock()) as remove_mock,
            patch("api.log_blacklist_repo.get_all", new=AsyncMock(return_value=[USER_ID])),
            patch("api.log_blacklist_repo.is_entity_blacklisted", new=AsyncMock(return_value="reason")),
        ):
            await add_log_blacklist(GUILD_ID, USER_ID, bl_type)
            await remove_log_blacklist(GUILD_ID, USER_ID, bl_type)
            entities = await get_log_blacklist(GUILD_ID, bl_type)
            blocked = await is_log_entity_blacklisted(GUILD_ID, USER_ID, bl_type)
        add_mock.assert_awaited_once()
        remove_mock.assert_awaited_once()
        assert USER_ID in entities
        assert blocked == "reason"


class TestCustomFormulaExtended:
    @pytest.mark.parametrize("formula", ["x*2", "x**2+100", "level*50"])
    @pytest.mark.asyncio
    async def test_get_custom_formula_via_repo(self, bot_with_pool, formula: str):
        config = MagicMock()
        config.custom_formula = formula
        with patch("repositories.level_config_repository.level_config_repo.get_config", new=AsyncMock(return_value=config)):
            result = await get_custom_formula(GUILD_ID)
        assert result == formula


_DT = datetime(2024, 6, 15, 12, 0, 0, tzinfo=UTC)
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
_SCHEDULED_ROW = (1, GUILD_ID, CHANNEL_ID, USER_ID, "hello", _DT, 60, 5, None, None, _DT)
_DSM_ROW = (GUILD_ID, CHANNEL_ID, 5, 10, 60, None)
_DSM_MSG_ROW = (1, CHANNEL_ID, MESSAGE_ID, _DT)
_WELCOME_ROW = (CHANNEL_ID, GUILD_ID, "welcome", "http://img")
_AI_SITUATION_ROW = (USER_ID, "situation text", "name1", _DT, 1.0, 1.0, 0.0, 0.0, True)
_LEADERBOARD_ROW = (USER_ID, 500)


async def _async_iter(rows: list[tuple]):
    for row in rows:
        yield row


class TestXpCooldownPaths:
    @pytest.mark.asyncio
    async def test_update_user_xp_respects_cooldown(self, bot_with_pool):
        from api import _guild_config_cache, _last_xp_gain_cache

        _, cursor = bot_with_pool
        _guild_config_cache.set(GUILD_ID, {"text_cooldown": 60})
        _last_xp_gain_cache[(GUILD_ID, USER_ID)] = datetime.now().timestamp()
        await update_user_xp(GUILD_ID, USER_ID, 10, respect_cooldown=True)
        cursor.execute.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_update_user_xp_respect_cooldown_applies(self, bot_with_pool):
        from api import _guild_config_cache, _last_xp_gain_cache

        _, cursor = bot_with_pool
        _guild_config_cache.set(GUILD_ID, {"text_cooldown": 60})
        _last_xp_gain_cache.clear()
        await update_user_xp(GUILD_ID, USER_ID, 10, respect_cooldown=True)
        cursor.execute.assert_awaited()

    @pytest.mark.asyncio
    async def test_update_user_xp_from_voice_respects_cooldown(self, bot_with_pool):
        from api import _guild_config_cache, _last_xp_gain_cache, update_user_xp_from_voice

        _, cursor = bot_with_pool
        _guild_config_cache.set(GUILD_ID, {"voice_cooldown": 60})
        _last_xp_gain_cache[(GUILD_ID, USER_ID)] = datetime.now().timestamp()
        await update_user_xp_from_voice(GUILD_ID, USER_ID, 10, respect_cooldown=True)
        cursor.execute.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_get_text_and_voice_cooldown(self, bot_with_pool):
        config = MagicMock(text_cooldown=90, voice_cooldown=180)
        with patch("repositories.level_config_repository.level_config_repo.get_config", new=AsyncMock(return_value=config)):
            assert await get_text_cooldown(GUILD_ID) == 90
            assert await get_voice_cooldown(GUILD_ID) == 180


class TestUserLevelInfoExtended:
    @pytest.mark.asyncio
    async def test_get_user_level_info_with_data(self, bot_with_pool):
        with (
            patch("api.execute_query", new=AsyncMock(return_value=[(500, "http://bg")])),
            patch("api.get_xp_scaling", new=AsyncMock(return_value="medium")),
            patch("api.get_custom_formula", new=AsyncMock(return_value=None)),
            patch("api.get_level_for_xp_async", new=AsyncMock(return_value=5)),
            patch("api.get_xp_for_level_async", new=AsyncMock(side_effect=[600, 400])),
        ):
            info = await get_user_level_info(GUILD_ID, USER_ID)
        assert info is not None
        assert info.level == 5


class TestGiveawayExtended:
    @pytest.mark.parametrize(
        "func_name",
        [
            "set_giveaway_message_id",
            "set_giveaway_started",
            "set_giveaway_ended",
            "delete_old_giveaways",
            "get_blacklisted_roles",
            "add_giveaway_voice_minutes_if_needed",
            "add_giveaway_new_message_if_needed",
            "add_giveaway_new_message_channel_if_needed",
            "set_giveaway_endtime",
        ],
    )
    @pytest.mark.asyncio
    async def test_giveaway_service_delegates(self, bot_with_pool, func_name: str):
        from api import (
            add_giveaway_new_message_channel_if_needed,
            add_giveaway_new_message_if_needed,
            add_giveaway_voice_minutes_if_needed,
            delete_old_giveaways,
            get_blacklisted_roles,
            set_giveaway_ended,
            set_giveaway_endtime,
            set_giveaway_message_id,
            set_giveaway_started,
        )

        funcs = {
            "set_giveaway_message_id": (set_giveaway_message_id, (1, 99)),
            "set_giveaway_started": (set_giveaway_started, (1,)),
            "set_giveaway_ended": (set_giveaway_ended, (1,)),
            "delete_old_giveaways": (delete_old_giveaways, ()),
            "get_blacklisted_roles": (get_blacklisted_roles, (GUILD_ID,)),
            "add_giveaway_voice_minutes_if_needed": (add_giveaway_voice_minutes_if_needed, (USER_ID, GUILD_ID)),
            "add_giveaway_new_message_if_needed": (add_giveaway_new_message_if_needed, (USER_ID, GUILD_ID)),
            "add_giveaway_new_message_channel_if_needed": (
                add_giveaway_new_message_channel_if_needed,
                (USER_ID, GUILD_ID, CHANNEL_ID),
            ),
            "set_giveaway_endtime": (set_giveaway_endtime, (1, _DT)),
        }
        fn, args = funcs[func_name]
        with patch("services.giveaway_service.giveaway_service") as gs:
            for name in (
                "set_message_id",
                "set_started",
                "set_ended",
                "delete_old",
                "get_blacklisted_roles",
                "add_voice_minutes",
                "add_new_message",
                "add_new_message_channel",
                "set_endtime",
            ):
                setattr(gs, name, AsyncMock())
            await fn(*args)


class TestBoosterService:
    @pytest.mark.parametrize(
        "method,args",
        [
            ("add_booster_channel", (GUILD_ID, CHANNEL_ID)),
            ("delete_booster_channel", (GUILD_ID, CHANNEL_ID)),
            ("get_booster_channel", (GUILD_ID,)),
            ("claim_booster_channel", (USER_ID, CHANNEL_ID, GUILD_ID)),
            ("remove_claimed_booster_channel", (USER_ID, GUILD_ID)),
            ("add_booster_role", (GUILD_ID, ROLE_ID)),
            ("get_booster_role", (GUILD_ID,)),
            ("delete_booster_role", (GUILD_ID,)),
            ("add_claimed_booster_role", (USER_ID, ROLE_ID, GUILD_ID)),
            ("remove_claimed_booster_role", (USER_ID, GUILD_ID)),
        ],
    )
    @pytest.mark.asyncio
    async def test_booster_wrappers(self, bot_with_pool, method: str, args: tuple):
        from api import (
            add_booster_channel,
            add_booster_role,
            add_claimed_booster_role,
            claim_booster_channel,
            delete_booster_channel,
            delete_booster_role,
            get_booster_channel,
            get_booster_role,
            remove_claimed_booster_channel,
            remove_claimed_booster_role,
        )

        funcs = {
            "add_booster_channel": add_booster_channel,
            "delete_booster_channel": delete_booster_channel,
            "get_booster_channel": get_booster_channel,
            "claim_booster_channel": claim_booster_channel,
            "remove_claimed_booster_channel": remove_claimed_booster_channel,
            "add_booster_role": add_booster_role,
            "get_booster_role": get_booster_role,
            "delete_booster_role": delete_booster_role,
            "add_claimed_booster_role": add_claimed_booster_role,
            "remove_claimed_booster_role": remove_claimed_booster_role,
        }
        with patch("services.booster_service.booster_service") as svc:
            svc.add = AsyncMock()
            svc.delete = AsyncMock()
            svc.get = AsyncMock(return_value=CHANNEL_ID)
            svc.claim = AsyncMock()
            svc.unclaim = AsyncMock()
            await funcs[method](*args)


class TestClaimedBoosterQueries:
    @pytest.mark.asyncio
    async def test_get_claimed_booster_channel_by_user_and_guild(self, bot_with_pool):
        from api import get_claimed_booster_channel
        from models import ClaimedBoosterChannelModel

        claim = ClaimedBoosterChannelModel(user_id=USER_ID, channel_id=CHANNEL_ID, guild_id=GUILD_ID)
        with patch("services.booster_service.booster_service.get_user_claims", new=AsyncMock(return_value=[claim])):
            result = await get_claimed_booster_channel(USER_ID, GUILD_ID)
        assert result == CHANNEL_ID

    @pytest.mark.asyncio
    async def test_get_claimed_booster_channel_all(self, bot_with_pool):
        from api import get_claimed_booster_channel

        with patch("services.booster_service.booster_service.get_all_claims", new=AsyncMock(return_value=[])):
            result = await get_claimed_booster_channel()
        assert result is None

    @pytest.mark.asyncio
    async def test_get_claimed_booster_role_by_user(self, bot_with_pool):
        from api import get_claimed_booster_role
        from models import ClaimedBoosterRoleModel

        claim = ClaimedBoosterRoleModel(user_id=USER_ID, role_id=ROLE_ID, guild_id=GUILD_ID)
        with patch("services.booster_service.booster_service.get_user_claims", new=AsyncMock(return_value=[claim])):
            result = await get_claimed_booster_role(USER_ID)
        assert result == [claim]


class TestLogChannelApi:
    @pytest.mark.asyncio
    async def test_set_log_channel_new_guild(self, bot_with_pool):
        from api import set_log_channel

        with (
            patch("api.execute_query", new=AsyncMock(return_value=None)),
            patch("api.execute_action", new=AsyncMock()) as action,
        ):
            await set_log_channel(GUILD_ID, CHANNEL_ID)
        action.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_set_log_channel_existing_guild(self, bot_with_pool):
        from api import set_log_channel

        with (
            patch("api.execute_query", new=AsyncMock(return_value=[(1,)])),
            patch("api.execute_action", new=AsyncMock()) as action,
        ):
            await set_log_channel(GUILD_ID, CHANNEL_ID)
        sql = action.call_args[0][0]
        assert "log_channel" in sql

    @pytest.mark.parametrize("has_row", [True, False])
    @pytest.mark.asyncio
    async def test_get_log_enable(self, bot_with_pool, has_row: bool):
        from api import get_log_enable

        with patch("api.execute_query", new=AsyncMock(return_value=[_LOG_ENABLE_ROW] if has_row else None)):
            result = await get_log_enable(GUILD_ID)
        assert result.guild_id == GUILD_ID

    @pytest.mark.parametrize("field", ["memberJoin", "messageEdit", "reactionAdd"])
    @pytest.mark.asyncio
    async def test_set_log_enable(self, bot_with_pool, field: str):
        from api import set_log_enable

        with patch("api.execute_action", new=AsyncMock()) as action:
            await set_log_enable(GUILD_ID, **{field: False})
        assert field in action.call_args[0][0]

    @pytest.mark.asyncio
    async def test_set_log_enable_no_valid_fields(self, bot_with_pool):
        from api import set_log_enable

        with patch("api.execute_action", new=AsyncMock()) as action:
            await set_log_enable(GUILD_ID, unknown_field=True)
        action.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_get_and_remove_log_channel(self, bot_with_pool):
        from api import get_log_channel, remove_log_channel

        with patch("api.execute_query", new=AsyncMock(return_value=[(CHANNEL_ID,)])):
            assert await get_log_channel(GUILD_ID) == CHANNEL_ID
        _, cursor = bot_with_pool
        await remove_log_channel(GUILD_ID)
        cursor.execute.assert_awaited()


class TestScheduledMessages:
    @pytest.mark.asyncio
    async def test_add_scheduled_message(self, bot_with_pool):
        from api import add_scheduled_message

        _, cursor = bot_with_pool
        await add_scheduled_message(GUILD_ID, CHANNEL_ID, USER_ID, "hi", _DT, 60, 3, "[]")
        cursor.execute.assert_awaited()

    @pytest.mark.asyncio
    async def test_get_scheduled_messages(self, bot_with_pool):
        from api import get_scheduled_messages

        with patch("api.execute_query_iter", side_effect=lambda q, p=None: _async_iter([_SCHEDULED_ROW])):
            rows = await get_scheduled_messages(USER_ID)
        assert len(rows) == 1
        assert rows[0].content == "hello"

    @pytest.mark.asyncio
    async def test_remove_and_update_scheduled(self, bot_with_pool):
        from api import (
            remove_scheduled_message,
            update_scheduled_message_content,
            update_scheduled_message_repeat_amount,
        )

        _, cursor = bot_with_pool
        await remove_scheduled_message(1)
        await update_scheduled_message_content(1, "updated")
        await update_scheduled_message_repeat_amount(1, 10)
        assert cursor.execute.await_count == 3

    @pytest.mark.asyncio
    async def test_get_user_scheduled_in_timeframe(self, bot_with_pool):
        from api import get_user_scheduled_messages_in_timeframe

        end = _DT + timedelta(hours=1)
        with patch("api.execute_query_iter", side_effect=lambda q, p=None: _async_iter([_SCHEDULED_ROW])):
            rows = await get_user_scheduled_messages_in_timeframe(USER_ID, _DT, end, GUILD_ID)
        assert len(rows) == 1

    @pytest.mark.asyncio
    async def test_get_ready_scheduled_messages(self, bot_with_pool):
        from api import get_ready_scheduled_messages

        with patch("api.execute_query_iter", side_effect=lambda q, p=None: _async_iter([_SCHEDULED_ROW])):
            rows = await get_ready_scheduled_messages()
        assert len(rows) == 1


class TestReportService:
    @pytest.mark.parametrize(
        "method,args",
        [
            ("report_user", (GUILD_ID, USER_ID, "22222222222222222", "spam", False)),
            ("accept_report", (GUILD_ID, "1")),
            ("reject_report", (GUILD_ID, "1")),
            ("resolve_report", (GUILD_ID, "1")),
            ("delete_report", (GUILD_ID, "1")),
            ("block_reporter", (GUILD_ID, USER_ID)),
            ("unblock_reporter", (GUILD_ID, USER_ID)),
            ("set_report_channel", (GUILD_ID, CHANNEL_ID)),
            ("remove_report_channel", (GUILD_ID,)),
        ],
    )
    @pytest.mark.asyncio
    async def test_report_wrappers(self, bot_with_pool, method: str, args: tuple):
        from api import (
            accept_report,
            block_reporter,
            delete_report,
            reject_report,
            remove_report_channel,
            report_user,
            resolve_report,
            set_report_channel,
            unblock_reporter,
        )

        funcs = {
            "report_user": report_user,
            "accept_report": accept_report,
            "reject_report": reject_report,
            "resolve_report": resolve_report,
            "delete_report": delete_report,
            "block_reporter": block_reporter,
            "unblock_reporter": unblock_reporter,
            "set_report_channel": set_report_channel,
            "remove_report_channel": remove_report_channel,
        }
        with patch("services.report_service.report_service") as svc:
            svc.create = AsyncMock(return_value=1)
            svc.accept = AsyncMock()
            svc.reject = AsyncMock()
            svc.resolve = AsyncMock()
            svc.delete = AsyncMock()
            svc.block_reporter = AsyncMock()
            svc.unblock_reporter = AsyncMock()
            svc.set_channel = AsyncMock()
            svc.remove_channel = AsyncMock()
            await funcs[method](*args)

    @pytest.mark.asyncio
    async def test_get_reports_and_blocked(self, bot_with_pool):
        from api import check_if_reporter_is_blocked, get_blocked_reporters, get_report_channel, get_reports

        with patch("services.report_service.report_service") as svc:
            svc.get = AsyncMock(return_value=[])
            svc.get_blocked_reporters = AsyncMock(return_value=[])
            svc.is_blocked = AsyncMock(return_value=False)
            svc.get_channel = AsyncMock(return_value=CHANNEL_ID)
            assert await get_reports(GUILD_ID) == []
            assert await get_blocked_reporters(GUILD_ID) == []
            assert await check_if_reporter_is_blocked(GUILD_ID, USER_ID) is False
            assert await get_report_channel(GUILD_ID) == CHANNEL_ID


class TestTicketService:
    @pytest.mark.asyncio
    async def test_ticket_lifecycle(self, bot_with_pool):
        from api import (
            close_ticket,
            create_ticket_message,
            delete_ticket_message,
            get_ticket_by_channel_id,
            get_ticket_by_id,
            get_ticket_messages,
            get_ticket_messages_by_id,
            get_tickets,
            open_ticket,
        )

        with patch("services.ticket_service.ticket_service") as svc:
            svc.create_config = AsyncMock(return_value=1)
            svc.delete_config = AsyncMock()
            svc.get_configs = AsyncMock(return_value=[])
            svc.get_config = AsyncMock(return_value=None)
            svc.open = AsyncMock()
            svc.close = AsyncMock()
            svc.get_tickets = AsyncMock(return_value=[])
            svc.get_by_config_and_channel = AsyncMock(return_value=None)
            svc.get_by_channel = AsyncMock(return_value=None)
            await create_ticket_message(GUILD_ID, CHANNEL_ID, "intro", ROLE_ID, "name", "desc")
            await delete_ticket_message(GUILD_ID, 1)
            await get_ticket_messages(GUILD_ID)
            await get_ticket_messages_by_id("1")
            await get_ticket_messages_by_id("bad")
            await open_ticket(GUILD_ID, USER_ID, "1", CHANNEL_ID)
            await open_ticket(GUILD_ID, USER_ID, "bad", CHANNEL_ID)
            await close_ticket(GUILD_ID, CHANNEL_ID, USER_ID)
            await close_ticket(GUILD_ID, "bad", USER_ID)
            await get_tickets(GUILD_ID)
            await get_ticket_by_id(GUILD_ID, "1", CHANNEL_ID)
            await get_ticket_by_id(GUILD_ID, "bad", CHANNEL_ID)
            await get_ticket_by_channel_id(GUILD_ID, CHANNEL_ID)


class TestAISituations:
    @pytest.mark.asyncio
    async def test_ai_situation_crud(self, bot_with_pool):
        from api import (
            addCustomSituation,
            deleteCustomSituation,
            getCustomSituation,
            getCustomSituationFromUser,
            getCustomSituations,
            unlockCustomSituation,
        )

        _, cursor = bot_with_pool
        await addCustomSituation(USER_ID, "sit", "name", 1.0, 1.0, 0.0, 0.0)
        with (
            patch("api.execute_query", new=AsyncMock(return_value=[("name1",)])),
            patch("api.safe_execute_query", new=AsyncMock(return_value=[("name1",)])),
        ):
            assert await getCustomSituations() == ["name1"]
        with patch("api.execute_query", new=AsyncMock(return_value=[_AI_SITUATION_ROW])):
            assert await getCustomSituation("name1") is not None
            assert await getCustomSituationFromUser(USER_ID) is not None
        await deleteCustomSituation(USER_ID)
        await unlockCustomSituation(USER_ID)
        assert cursor.execute.await_count >= 3


class TestLeaderboard:
    @pytest.mark.asyncio
    async def test_leaderboard_functions(self, bot_with_pool):
        from api import get_level_leaderboard_count, get_level_leaderboard_paginated, getLevelLeaderboard

        with (
            patch("api.execute_query_iter", side_effect=lambda q, p=None: _async_iter([_LEADERBOARD_ROW])),
            patch("api.execute_query", new=AsyncMock(return_value=[(42,)])),
        ):
            rows = [r async for r in getLevelLeaderboard(GUILD_ID)]
            assert len(rows) == 1
            page = await get_level_leaderboard_paginated(GUILD_ID, limit=0, offset=-1)
            assert len(page) == 1
            assert await get_level_leaderboard_count(GUILD_ID) == 42


class TestChannelConfigExtended:
    @pytest.mark.parametrize(
        "getter,setter,remover,row",
        [
            ("get_join_to_create_channel", "set_join_to_create_channel", "remove_join_to_create_channel", None),
            ("get_welcome_channel", "set_welcome_channel", "remove_welcome_channel", _WELCOME_ROW),
            ("get_leave_channel", "set_leave_channel", "remove_leave_channel", _WELCOME_ROW),
        ],
    )
    @pytest.mark.asyncio
    async def test_channel_config_round_trip(self, bot_with_pool, getter: str, setter: str, remover: str, row):
        import api as api_mod

        get_fn = getattr(api_mod, getter)
        set_fn = getattr(api_mod, setter)
        remove_fn = getattr(api_mod, remover)
        _, cursor = bot_with_pool
        with patch("api.execute_query", new=AsyncMock(return_value=[(1,)] if row is None else [row])):
            if row is None:
                assert await get_fn(CHANNEL_ID) is True
            else:
                assert await get_fn(GUILD_ID) is not None
        if setter == "set_welcome_channel":
            await set_fn(GUILD_ID, CHANNEL_ID, "msg", "http://img")
        elif setter == "set_leave_channel":
            await set_fn(GUILD_ID, CHANNEL_ID, "bye", "http://img")
        else:
            await set_fn(GUILD_ID, CHANNEL_ID)
        await remove_fn(GUILD_ID)
        assert cursor.execute.await_count >= 2

    @pytest.mark.asyncio
    async def test_remove_media_channel(self, bot_with_pool):
        from api import remove_media_channel

        _, cursor = bot_with_pool
        await remove_media_channel(GUILD_ID, CHANNEL_ID)
        cursor.execute.assert_awaited()


class TestDynamicSlowmodeExtended:
    @pytest.mark.asyncio
    async def test_dynamicslowmode_full(self, bot_with_pool):
        from api import (
            add_dynamicslowmode_message,
            cash_slowmode_delay,
            clear_old_dynamicslowmode_messages,
            get_dynamicslowmode_channels,
            get_dynamicslowmode_messages,
            remove_cashed_slowmode_delay,
            remove_dynamicslowmode,
        )

        _, cursor = bot_with_pool

        async def iter_side_effect(query, params=None):
            if "dynamicslowmode_messages" in query:
                async for r in _async_iter([_DSM_MSG_ROW]):
                    yield r
            else:
                async for r in _async_iter([_DSM_ROW]):
                    yield r

        with (
            patch("api.execute_query", new=AsyncMock(return_value=[_DSM_ROW])),
            patch("api.execute_query_iter", side_effect=iter_side_effect),
        ):
            channels = await get_dynamicslowmode_channels(GUILD_ID)
            assert len(channels) == 1
            msgs = await get_dynamicslowmode_messages(CHANNEL_ID)
            assert len(msgs) == 1
        await remove_dynamicslowmode(GUILD_ID, CHANNEL_ID)
        await add_dynamicslowmode_message(CHANNEL_ID, MESSAGE_ID, _DT)
        await clear_old_dynamicslowmode_messages(CHANNEL_ID, _DT)
        await cash_slowmode_delay(CHANNEL_ID, 30)
        await remove_cashed_slowmode_delay(CHANNEL_ID)
        assert cursor.execute.await_count >= 5


class TestTwitchApi:
    @pytest.mark.asyncio
    async def test_twitch_repo_delegates(self, bot_with_pool):
        from api import (
            get_all_twitch_notification_uuids,
            get_twitch_notification_by_guild_id,
            get_twitch_online_notification,
            get_twitch_online_notification_by_twitch_uuid,
            remove_twitch_online_notification,
            set_twitch_online_notification,
        )

        with patch("api.twitch_repo") as repo:
            repo.get_by_channel = AsyncMock(return_value=[])
            repo.set = AsyncMock()
            repo.remove = AsyncMock()
            repo.get_by_twitch_uuid = AsyncMock(return_value=None)
            repo.get_all_uuids = AsyncMock(return_value=["uuid1"])
            repo.get_by_guild = AsyncMock(return_value=[])
            await get_twitch_online_notification(CHANNEL_ID)
            await set_twitch_online_notification(GUILD_ID, CHANNEL_ID, "uuid", "name", "live!")
            await remove_twitch_online_notification("1")
            await get_twitch_online_notification_by_twitch_uuid("uuid")
            assert await get_all_twitch_notification_uuids() == ["uuid1"]
            await get_twitch_notification_by_guild_id(GUILD_ID)


class TestTriggerMessagesExtended:
    @pytest.mark.parametrize(
        "method,args",
        [
            ("remove_trigger_message", (GUILD_ID, "hi")),
            ("get_trigger_message_channels", (GUILD_ID, 1)),
            ("get_trigger_messages_by_channel", (GUILD_ID, CHANNEL_ID)),
            ("add_trigger_message_channel", (GUILD_ID, CHANNEL_ID, 1)),
            ("remove_trigger_message_channel", (GUILD_ID, CHANNEL_ID, 1)),
            ("is_trigger_message", (GUILD_ID, "hi", CHANNEL_ID)),
        ],
    )
    @pytest.mark.asyncio
    async def test_trigger_message_repo(self, bot_with_pool, method: str, args: tuple):
        import api as api_mod

        with patch("repositories.trigger_message_repository.trigger_message_repo") as repo:
            repo.remove = AsyncMock()
            repo.get_channels = AsyncMock(return_value=[])
            repo.get_by_channel = AsyncMock(return_value=[])
            repo.add_channel = AsyncMock()
            repo.remove_channel = AsyncMock()
            repo.find = AsyncMock(return_value=None)
            await getattr(api_mod, method)(*args)


class TestTokenExtended:
    @pytest.mark.asyncio
    async def test_reset_token_with_entitlements(self, bot_with_pool):
        entitlement = MagicMock()
        entitlement.user_id = int(USER_ID)
        _, cursor = bot_with_pool
        await resetToken([entitlement])
        assert cursor.execute.await_count >= 2

    @pytest.mark.asyncio
    async def test_get_token_overview_with_data(self, bot_with_pool):
        with patch("api.execute_query", new=AsyncMock(return_value=[(500, 0, 0, 10)])):
            overview = await getTokenOverview(USER_ID)
        assert overview is not None
        assert overview.free_token == 500


class TestBlacklistFull:
    @pytest.mark.asyncio
    async def test_get_blacklist_populates_all(self, bot_with_pool):
        channel_row = (CHANNEL_ID, "c-reason")
        role_row = (ROLE_ID, "r-reason")
        user_row = (USER_ID, "u-reason")

        async def iter_side_effect(query, params=None):
            if "blacklistedChannel" in query:
                async for r in _async_iter([channel_row]):
                    yield r
            elif "blacklisted_role" in query:
                async for r in _async_iter([role_row]):
                    yield r
            elif "blacklistedUser" in query:
                async for r in _async_iter([user_row]):
                    yield r

        with patch("api.execute_query_iter", side_effect=iter_side_effect):
            result = await get_blacklist(GUILD_ID)
        assert len(result["channels"]) == 1
        assert len(result["roles"]) == 1
        assert len(result["users"]) == 1


class TestUpdateGiveaway:
    @pytest.mark.asyncio
    async def test_update_giveaway(self, bot_with_pool):
        from api import update_giveaway

        with patch("services.giveaway_service.giveaway_service.update", new=AsyncMock()) as upd:
            await update_giveaway(
                1,
                GUILD_ID,
                "title",
                "desc",
                1,
                True,
                None,
                None,
                "prize",
                None,
                _DT,
                _DT,
                None,
                None,
                {},
                [],
                None,
                CHANNEL_ID,
            )
        upd.assert_awaited_once()


class TestBrawlstarsExtended:
    @pytest.mark.asyncio
    async def test_remove_brawlstars_linked_account(self, bot_with_pool):
        from api import remove_brawlstars_linked_account

        _, cursor = bot_with_pool
        await remove_brawlstars_linked_account(USER_ID)
        cursor.execute.assert_awaited()


class TestGetReportsByReporter:
    @pytest.mark.asyncio
    async def test_get_reports_by_reporter(self, bot_with_pool):
        from api import get_reports_by_reporter

        with patch("services.report_service.report_service.get_by_reporter", new=AsyncMock(return_value=[])):
            assert await get_reports_by_reporter(GUILD_ID, USER_ID) == []
