from __future__ import annotations

from collections.abc import Iterator
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest
from pydantic import ValidationError

import tests.mock_config as mock_config

mock_config.patch_config_module()

from api import set_bot
from services.giveaway_service import (
    GiveawayCreateParams,
    GiveawayService,
    GiveawayUpdateParams,
    giveaway_service,
)
from tests.helpers.db import AsyncIter, make_bot, make_mock_pool
from tests.helpers.factories import CHANNEL_ID, GUILD_ID, ROLE_ID, USER_ID, _dt, giveaway_row

pytestmark = pytest.mark.asyncio


@pytest.fixture(autouse=True)
def reset_bot() -> Iterator[None]:
    set_bot(None)
    yield
    set_bot(None)


@pytest.fixture
def bot_with_pool():
    pool, _, cursor = make_mock_pool()
    bot, _ = make_bot(pool)
    return bot, cursor


def _create_params(**overrides):
    base = dict(
        guild_id=GUILD_ID,
        title="Prize Draw",
        channel_id=CHANNEL_ID,
        end_time=_dt(),
        start_time=_dt(),
    )
    base.update(overrides)
    return GiveawayCreateParams(**base)


def _update_params(**overrides):
    base = dict(
        guild_id=GUILD_ID,
        title="Updated",
        channel_id=CHANNEL_ID,
        end_time=_dt(),
    )
    base.update(overrides)
    return GiveawayUpdateParams(**base)


class TestGiveawayParams:
    def test_create_params_defaults(self):
        params = _create_params()
        assert params.winners == 1
        assert params.with_button is True

    def test_create_params_rejects_empty_title(self):
        with pytest.raises(ValidationError):
            _create_params(title="")

    def test_update_params_channel_requirements(self):
        params = _update_params(channel_requirements={"111": 5})
        assert params.channel_requirements["111"] == 5

    def test_singleton_instance(self):
        assert isinstance(giveaway_service, GiveawayService)


class TestGiveawayCrud:
    async def test_create_success(self, bot_with_pool):
        _, cursor = bot_with_pool
        cursor.fetchone = AsyncMock(return_value=(99,))
        cursor.executemany = AsyncMock()
        params = _create_params(
            channel_requirements={CHANNEL_ID: 3},
            role_requirement=[ROLE_ID],
        )
        result = await GiveawayService.create(params)
        assert result == 99
        assert cursor.executemany.await_count == 2

    async def test_create_returns_none_on_exception(self, bot_with_pool):
        _, cursor = bot_with_pool
        cursor.execute = AsyncMock(side_effect=RuntimeError("db fail"))
        result = await GiveawayService.create(_create_params())
        assert result is None

    async def test_create_returns_none_when_no_insert_id(self, bot_with_pool):
        _, cursor = bot_with_pool
        cursor.fetchone = AsyncMock(return_value=None)
        result = await GiveawayService.create(_create_params())
        assert result is None

    async def test_get_found(self, bot_with_pool):
        _, cursor = bot_with_pool
        cursor.fetchall.return_value = [giveaway_row()]
        model = await GiveawayService.get(1)
        assert model is not None
        assert model.giveaway_id == 1

    async def test_get_missing(self, bot_with_pool):
        _, cursor = bot_with_pool
        cursor.fetchall.return_value = []
        assert await GiveawayService.get(999) is None

    async def test_update_success(self, bot_with_pool):
        _, cursor = bot_with_pool
        params = _update_params(channel_requirements={CHANNEL_ID: 2}, role_requirement=[ROLE_ID])
        await GiveawayService.update(1, params)
        assert cursor.execute.await_count >= 4

    async def test_update_raises_on_error(self, bot_with_pool):
        _, cursor = bot_with_pool
        cursor.execute = AsyncMock(side_effect=RuntimeError("update fail"))
        with pytest.raises(RuntimeError):
            await GiveawayService.update(1, _update_params())

    async def test_delete_success(self, bot_with_pool):
        _, cursor = bot_with_pool
        await GiveawayService.delete(1)
        assert cursor.execute.await_count >= 7

    async def test_delete_raises_on_error(self, bot_with_pool):
        _, cursor = bot_with_pool
        cursor.execute = AsyncMock(side_effect=RuntimeError("delete fail"))
        with pytest.raises(RuntimeError):
            await GiveawayService.delete(1)

    async def test_delete_old_no_rows(self, bot_with_pool):
        _, cursor = bot_with_pool
        cursor.fetchall = AsyncMock(return_value=[])
        await GiveawayService.delete_old()
        assert cursor.execute.await_count == 1

    async def test_delete_old_with_rows(self, bot_with_pool):
        _, cursor = bot_with_pool
        cursor.fetchall = AsyncMock(return_value=[(1,), (2,)])
        await GiveawayService.delete_old()
        assert cursor.execute.await_count > 3

    async def test_delete_old_raises_on_error(self, bot_with_pool):
        _, cursor = bot_with_pool
        cursor.fetchall = AsyncMock(side_effect=RuntimeError("old fail"))
        with pytest.raises(RuntimeError):
            await GiveawayService.delete_old()


class TestGiveawayState:
    async def test_set_message_id(self, bot_with_pool):
        _, cursor = bot_with_pool
        cursor.rowcount = 1
        await GiveawayService.set_message_id(1, "555")
        assert "messageId" in cursor.execute.await_args[0][0]

    async def test_set_started(self, bot_with_pool):
        _, cursor = bot_with_pool
        cursor.rowcount = 1
        await GiveawayService.set_started(1)
        assert "started = 1" in cursor.execute.await_args[0][0]

    async def test_mark_sent(self, bot_with_pool):
        _, cursor = bot_with_pool
        cursor.rowcount = 1
        await GiveawayService.mark_sent(1, 555)
        sql = cursor.execute.await_args[0][0]
        assert "messageId" in sql and "started = 1" in sql

    async def test_set_ended(self, bot_with_pool):
        _, cursor = bot_with_pool
        cursor.rowcount = 1
        await GiveawayService.set_ended(1)
        assert "ended = 1" in cursor.execute.await_args[0][0]

    async def test_set_endtime(self, bot_with_pool):
        _, cursor = bot_with_pool
        cursor.rowcount = 1
        end = datetime(2025, 1, 1, tzinfo=timezone.utc)
        await GiveawayService.set_endtime(1, end)
        assert cursor.execute.await_args[0][1][0] == end

    async def test_get_send_ready(self, bot_with_pool):
        _, cursor = bot_with_pool
        cursor.__aiter__ = MagicMock(return_value=AsyncIter([(1,), (2,)]))
        ids = await GiveawayService.get_send_ready()
        assert ids == [1, 2]

    async def test_get_end_ready(self, bot_with_pool):
        _, cursor = bot_with_pool
        cursor.__aiter__ = MagicMock(return_value=AsyncIter([(3,)]))
        ids = await GiveawayService.get_end_ready()
        assert ids == [3]


class TestGiveawayRequirements:
    async def test_get_channel_requirements(self, bot_with_pool):
        _, cursor = bot_with_pool
        cursor.__aiter__ = MagicMock(return_value=AsyncIter([(CHANNEL_ID, 5)]))
        rows = await GiveawayService.get_channel_requirements(1)
        assert len(rows) == 1
        assert rows[0].amount == 5

    async def test_get_role_requirements(self, bot_with_pool):
        _, cursor = bot_with_pool
        cursor.__aiter__ = MagicMock(return_value=AsyncIter([(ROLE_ID,)]))
        roles = await GiveawayService.get_role_requirements(1)
        assert roles == [ROLE_ID]


class TestGiveawayParticipants:
    async def test_get_participants(self, bot_with_pool):
        _, cursor = bot_with_pool
        cursor.__aiter__ = MagicMock(return_value=AsyncIter([(USER_ID,)]))
        assert await GiveawayService.get_participants(1) == [USER_ID]

    async def test_add_participant(self, bot_with_pool):
        _, cursor = bot_with_pool
        cursor.rowcount = 1
        await GiveawayService.add_participant(1, USER_ID)
        params = cursor.execute.await_args[0][1]
        assert params == (USER_ID, 1)

    async def test_remove_participant(self, bot_with_pool):
        _, cursor = bot_with_pool
        cursor.rowcount = 1
        await GiveawayService.remove_participant(1, USER_ID)
        params = cursor.execute.await_args[0][1]
        assert params == (1, USER_ID)

    async def test_is_participant_true(self, bot_with_pool):
        _, cursor = bot_with_pool
        cursor.fetchall.return_value = [(USER_ID, 1)]
        assert await GiveawayService.is_participant(1, USER_ID) is True

    async def test_is_participant_false(self, bot_with_pool):
        _, cursor = bot_with_pool
        cursor.fetchall.return_value = []
        assert await GiveawayService.is_participant(1, USER_ID) is False


class TestGiveawayTracking:
    async def test_get_new_messages(self, bot_with_pool):
        _, cursor = bot_with_pool
        cursor.fetchall.return_value = [(12,)]
        assert await GiveawayService.get_new_messages(1, USER_ID) == 12

    async def test_get_new_messages_channel(self, bot_with_pool):
        _, cursor = bot_with_pool
        cursor.fetchall.return_value = [(7,)]
        assert await GiveawayService.get_new_messages_channel(1, CHANNEL_ID, USER_ID) == 7

    async def test_get_voice_time(self, bot_with_pool):
        _, cursor = bot_with_pool
        cursor.fetchall.return_value = [(30,)]
        assert await GiveawayService.get_voice_time(1, USER_ID) == 30

    async def test_add_voice_minutes(self, bot_with_pool):
        _, cursor = bot_with_pool
        cursor.rowcount = 1
        await GiveawayService.add_voice_minutes(USER_ID, GUILD_ID)
        assert "giveawayVoiceTime" in cursor.execute.await_args[0][0]

    async def test_add_new_message(self, bot_with_pool):
        _, cursor = bot_with_pool
        cursor.rowcount = 1
        await GiveawayService.add_new_message(USER_ID, GUILD_ID)
        assert "giveawayNewMessage" in cursor.execute.await_args[0][0]

    async def test_add_new_message_channel(self, bot_with_pool):
        _, cursor = bot_with_pool
        cursor.rowcount = 1
        await GiveawayService.add_new_message_channel(USER_ID, GUILD_ID, CHANNEL_ID)
        params = cursor.execute.await_args[0][1]
        assert params[0] == CHANNEL_ID


class TestGiveawayBlacklist:
    async def test_add_blacklisted_user(self, bot_with_pool):
        _, cursor = bot_with_pool
        cursor.rowcount = 1
        await GiveawayService.add_blacklisted_user(GUILD_ID, USER_ID)
        assert "giveawayBlacklistedUser" in cursor.execute.await_args[0][0]

    async def test_add_blacklisted_role(self, bot_with_pool):
        _, cursor = bot_with_pool
        cursor.rowcount = 1
        await GiveawayService.add_blacklisted_role(GUILD_ID, ROLE_ID)
        assert "giveawayBlacklistedRole" in cursor.execute.await_args[0][0]

    async def test_remove_blacklisted_user(self, bot_with_pool):
        _, cursor = bot_with_pool
        cursor.rowcount = 1
        await GiveawayService.remove_blacklisted_user(GUILD_ID, USER_ID)
        assert "DELETE" in cursor.execute.await_args[0][0]

    async def test_remove_blacklisted_role(self, bot_with_pool):
        _, cursor = bot_with_pool
        cursor.rowcount = 1
        await GiveawayService.remove_blacklisted_role(GUILD_ID, ROLE_ID)
        assert "DELETE" in cursor.execute.await_args[0][0]

    async def test_get_blacklisted_users(self, bot_with_pool):
        _, cursor = bot_with_pool
        cursor.__aiter__ = MagicMock(return_value=AsyncIter([(USER_ID, "spam")]))
        rows = await GiveawayService.get_blacklisted_users(GUILD_ID)
        assert len(rows) == 1

    async def test_get_blacklisted_roles(self, bot_with_pool):
        _, cursor = bot_with_pool
        cursor.__aiter__ = MagicMock(return_value=AsyncIter([(ROLE_ID, None)]))
        rows = await GiveawayService.get_blacklisted_roles(GUILD_ID)
        assert len(rows) == 1

    async def test_is_user_blacklisted_true(self, bot_with_pool):
        _, cursor = bot_with_pool
        cursor.fetchall.return_value = [(GUILD_ID, USER_ID)]
        assert await GiveawayService.is_user_blacklisted(GUILD_ID, USER_ID) is True

    async def test_is_user_blacklisted_false(self, bot_with_pool):
        _, cursor = bot_with_pool
        cursor.fetchall.return_value = []
        assert await GiveawayService.is_user_blacklisted(GUILD_ID, USER_ID) is False
