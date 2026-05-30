from __future__ import annotations

from collections.abc import Iterator
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

import tests.mock_config as mock_config

mock_config.patch_config_module()

from api import execute_action, execute_query, safe_execute_query, set_bot
from services.booster_service import (
    BoosterService,
    BoosterType,
    ClaimedBoosterType,
    booster_service,
)
from tests.helpers.db import make_bot, make_mock_pool
from tests.helpers.factories import CHANNEL_ID, GUILD_ID, ROLE_ID, USER_ID

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


class TestBoosterTypeEnum:
    def test_channel_table_name(self):
        assert BoosterType.CHANNEL.value == "booster_channel"

    def test_role_table_name(self):
        assert BoosterType.ROLE.value == "boosterRole"

    def test_claimed_channel_table(self):
        assert ClaimedBoosterType.CHANNEL.value == "claimedBoosterChannel"

    def test_claimed_role_table(self):
        assert ClaimedBoosterType.ROLE.value == "claimedBoosterRole"

    def test_singleton_instance(self):
        assert isinstance(booster_service, BoosterService)


class TestBoosterServicePrimary:
    async def test_add_channel(self, bot_with_pool):
        _, cursor = bot_with_pool
        cursor.rowcount = 1
        service = BoosterService()
        await service.add(BoosterType.CHANNEL, GUILD_ID, CHANNEL_ID)
        cursor.execute.assert_awaited()
        sql = cursor.execute.await_args[0][0]
        assert "booster_channel" in sql
        assert "channel_id" in sql

    async def test_add_role(self, bot_with_pool):
        _, cursor = bot_with_pool
        cursor.rowcount = 1
        service = BoosterService()
        await service.add(BoosterType.ROLE, GUILD_ID, ROLE_ID)
        sql = cursor.execute.await_args[0][0]
        assert "boosterRole" in sql
        assert "role_id" in sql

    async def test_get_channel_returns_id(self, bot_with_pool):
        _, cursor = bot_with_pool
        cursor.fetchall.return_value = [(CHANNEL_ID,)]
        service = BoosterService()
        result = await service.get(BoosterType.CHANNEL, GUILD_ID)
        assert result == CHANNEL_ID

    async def test_get_role_returns_none_when_missing(self, bot_with_pool):
        _, cursor = bot_with_pool
        cursor.fetchall.return_value = []
        service = BoosterService()
        result = await service.get(BoosterType.ROLE, GUILD_ID)
        assert result is None

    async def test_delete_channel_requires_entity_id(self):
        service = BoosterService()
        with pytest.raises(ValueError, match="entity_id is required"):
            await service.delete(BoosterType.CHANNEL, GUILD_ID)

    async def test_delete_channel_with_entity_id(self, bot_with_pool):
        _, cursor = bot_with_pool
        cursor.rowcount = 1
        service = BoosterService()
        await service.delete(BoosterType.CHANNEL, GUILD_ID, CHANNEL_ID)
        sql = cursor.execute.await_args[0][0]
        assert "channel_id" in sql

    async def test_delete_role_by_guild_only(self, bot_with_pool):
        _, cursor = bot_with_pool
        cursor.rowcount = 1
        service = BoosterService()
        await service.delete(BoosterType.ROLE, GUILD_ID)
        params = cursor.execute.await_args[0][1]
        assert params == (GUILD_ID,)


class TestBoosterServiceClaims:
    async def test_claim_channel(self, bot_with_pool):
        _, cursor = bot_with_pool
        cursor.rowcount = 1
        service = BoosterService()
        await service.claim(ClaimedBoosterType.CHANNEL, USER_ID, CHANNEL_ID, GUILD_ID)
        sql = cursor.execute.await_args[0][0]
        assert "claimedBoosterChannel" in sql

    async def test_claim_role(self, bot_with_pool):
        _, cursor = bot_with_pool
        cursor.rowcount = 1
        service = BoosterService()
        await service.claim(ClaimedBoosterType.ROLE, USER_ID, ROLE_ID, GUILD_ID)
        sql = cursor.execute.await_args[0][0]
        assert "claimedBoosterRole" in sql

    async def test_unclaim(self, bot_with_pool):
        _, cursor = bot_with_pool
        cursor.rowcount = 1
        service = BoosterService()
        await service.unclaim(ClaimedBoosterType.CHANNEL, USER_ID, GUILD_ID)
        params = cursor.execute.await_args[0][1]
        assert params == (USER_ID, GUILD_ID)

    async def test_get_claim_for_user_found(self, bot_with_pool):
        _, cursor = bot_with_pool
        cursor.fetchall.return_value = [(CHANNEL_ID,)]
        service = BoosterService()
        result = await service.get_claim_for_user(ClaimedBoosterType.CHANNEL, USER_ID, GUILD_ID)
        assert result == CHANNEL_ID

    async def test_get_claim_for_user_missing(self, bot_with_pool):
        _, cursor = bot_with_pool
        cursor.fetchall.return_value = []
        service = BoosterService()
        result = await service.get_claim_for_user(ClaimedBoosterType.ROLE, USER_ID, GUILD_ID)
        assert result is None

    async def test_has_claim_true(self, bot_with_pool):
        _, cursor = bot_with_pool
        cursor.fetchall.return_value = [(1,)]
        service = BoosterService()
        assert await service.has_claim(ClaimedBoosterType.CHANNEL, USER_ID) is True

    async def test_has_claim_false(self, bot_with_pool):
        _, cursor = bot_with_pool
        cursor.fetchall.return_value = []
        service = BoosterService()
        assert await service.has_claim(ClaimedBoosterType.ROLE, USER_ID) is False

    async def test_get_user_claims_channel(self, bot_with_pool):
        _, cursor = bot_with_pool
        cursor.fetchall.return_value = [(USER_ID, CHANNEL_ID, GUILD_ID)]
        service = BoosterService()
        claims = await service.get_user_claims(ClaimedBoosterType.CHANNEL, USER_ID)
        assert len(claims) == 1
        assert str(claims[0].channel_id) == CHANNEL_ID

    async def test_get_user_claims_role(self, bot_with_pool):
        _, cursor = bot_with_pool
        cursor.fetchall.return_value = [(USER_ID, ROLE_ID, GUILD_ID)]
        service = BoosterService()
        claims = await service.get_user_claims(ClaimedBoosterType.ROLE, USER_ID)
        assert len(claims) == 1
        assert str(claims[0].role_id) == ROLE_ID

    async def test_get_all_claims_channel(self, bot_with_pool):
        _, cursor = bot_with_pool
        cursor.fetchall.return_value = [(USER_ID, CHANNEL_ID, GUILD_ID)]
        service = BoosterService()
        claims = await service.get_all_claims(ClaimedBoosterType.CHANNEL)
        assert len(claims) == 1

    async def test_get_all_claims_role(self, bot_with_pool):
        _, cursor = bot_with_pool
        cursor.fetchall.return_value = [(USER_ID, ROLE_ID, GUILD_ID)]
        service = BoosterService()
        claims = await service.get_all_claims(ClaimedBoosterType.ROLE)
        assert len(claims) == 1

    async def test_execute_action_without_pool_returns_none(self):
        result = await execute_action("DELETE FROM booster_channel WHERE guild_id = %s", (GUILD_ID,))
        assert result is None

    async def test_execute_query_without_pool_returns_none(self):
        result = await execute_query("SELECT channel_id FROM booster_channel")
        assert result is None

    async def test_safe_execute_query_without_pool_returns_empty(self):
        result = await safe_execute_query("SELECT 1 FROM claimedBoosterChannel")
        assert result == []
