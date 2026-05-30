from __future__ import annotations

from collections.abc import Iterator
from unittest.mock import MagicMock, patch

import pytest
from pydantic import ValidationError

import tests.mock_config as mock_config

mock_config.patch_config_module()

from api import set_bot
from services.ai_service import (
    AiService,
    AiSituation,
    AiTokenUsage,
    CreateSituationParams,
    TokenOverview,
)
from tests.helpers.db import AsyncIter, make_bot, make_mock_pool
from tests.helpers.factories import USER_ID

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


class TestAiModels:
    def test_token_usage_total_available(self):
        usage = AiTokenUsage(user_id=USER_ID, free_token=100, plus_token=50, paid_token=25)
        assert usage.total_available == 175

    def test_create_situation_params_valid(self):
        params = CreateSituationParams(
            user_id=USER_ID,
            situation="You are a helpful assistant for testing purposes.",
            name="testbot",
        )
        assert params.temperature == 1.0

    def test_create_situation_params_rejects_short_name(self):
        with pytest.raises(ValidationError):
            CreateSituationParams(
                user_id=USER_ID,
                situation="You are a helpful assistant for testing purposes.",
                name="ab",
            )

    def test_create_situation_params_rejects_short_situation(self):
        with pytest.raises(ValidationError):
            CreateSituationParams(user_id=USER_ID, situation="too short", name="validname")


class TestAiServiceInit:
    def test_reads_openai_key_from_config(self):
        with patch("services.ai_service.openAiKey", "test-key"):
            service = AiService()
            assert service._openai_key == "test-key"

    def test_falls_back_to_env(self, monkeypatch):
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)
        with patch("services.ai_service.openAiKey", None):
            monkeypatch.setenv("OPENAI_API_KEY", "env-key")
            service = AiService()
            assert service._openai_key == "env-key"


class TestAiTokenManagement:
    async def test_get_usage_found(self, bot_with_pool):
        _, cursor = bot_with_pool
        cursor.fetchall.return_value = [(USER_ID, 500, 100, 50, 10)]
        usage = await AiService.get_usage(USER_ID)
        assert usage is not None
        assert usage.free_token == 500
        assert usage.used_token == 10

    async def test_get_usage_missing(self, bot_with_pool):
        _, cursor = bot_with_pool
        cursor.fetchall.return_value = []
        assert await AiService.get_usage(USER_ID) is None

    async def test_consume_from_free_only(self, bot_with_pool):
        _, cursor = bot_with_pool
        cursor.fetchall.return_value = [(100, 0, 0)]
        cursor.rowcount = 1
        assert await AiService.consume(USER_ID, 30) is True
        params = cursor.execute.await_args_list[-1][0][1]
        assert params[0] == 70

    async def test_consume_drains_all_pools(self, bot_with_pool):
        _, cursor = bot_with_pool
        cursor.fetchall.return_value = [(10, 20, 30)]
        cursor.rowcount = 1
        assert await AiService.consume(USER_ID, 50) is True
        params = cursor.execute.await_args_list[-1][0][1]
        assert params[:3] == (0, 0, 10)

    async def test_consume_insufficient_tokens(self, bot_with_pool):
        _, cursor = bot_with_pool
        cursor.fetchall.return_value = [(5, 0, 0)]
        assert await AiService.consume(USER_ID, 100) is False

    async def test_consume_no_user_record(self, bot_with_pool):
        _, cursor = bot_with_pool
        cursor.fetchall.return_value = []
        assert await AiService.consume(USER_ID, 1) is False

    async def test_get_available_tokens_with_user(self, bot_with_pool):
        _, cursor = bot_with_pool
        cursor.fetchall.return_value = [(USER_ID, 100, 50, 25, 0)]
        assert await AiService.get_available_tokens(USER_ID) == 175

    async def test_get_available_tokens_without_user(self, bot_with_pool):
        _, cursor = bot_with_pool
        cursor.fetchall.return_value = []
        assert await AiService.get_available_tokens(USER_ID) == 0

    async def test_initialize_user(self, bot_with_pool):
        _, cursor = bot_with_pool
        cursor.rowcount = 1
        await AiService.initialize_user(USER_ID)
        assert "INSERT IGNORE" in cursor.execute.await_args[0][0]

    async def test_add_paid_tokens(self, bot_with_pool):
        _, cursor = bot_with_pool
        cursor.rowcount = 1
        await AiService.add_paid_tokens(USER_ID, 500)
        assert "paidToken" in cursor.execute.await_args[0][0]

    async def test_refill_without_entitlements(self, bot_with_pool):
        _, cursor = bot_with_pool
        cursor.rowcount = 1
        await AiService.refill()
        assert cursor.execute.await_count == 1

    async def test_refill_with_entitlements(self, bot_with_pool):
        _, cursor = bot_with_pool
        cursor.rowcount = 1
        entitlement = MagicMock(user_id=USER_ID)
        await AiService.refill([entitlement])
        assert cursor.execute.await_count == 2

    async def test_get_token_overview(self, bot_with_pool):
        _, cursor = bot_with_pool
        cursor.fetchall.return_value = [(500, 2000, 100, 50)]
        overview = await AiService.get_token_overview(USER_ID)
        assert isinstance(overview, TokenOverview)
        assert overview.plus_token == 2000

    async def test_get_token_overview_missing(self, bot_with_pool):
        _, cursor = bot_with_pool
        cursor.fetchall.return_value = []
        assert await AiService.get_token_overview(USER_ID) is None


class TestAiSituations:
    async def test_get_situation(self, bot_with_pool):
        _, cursor = bot_with_pool
        cursor.fetchall.return_value = [
            (USER_ID, "prompt", "name1", None, 1.0, 1.0, 0.0, 0.0, False),
        ]
        situation = await AiService.get_situation("name1")
        assert isinstance(situation, AiSituation)
        assert situation.name == "name1"

    async def test_get_situation_unlocked_only(self, bot_with_pool):
        _, cursor = bot_with_pool
        cursor.fetchall.return_value = []
        assert await AiService.get_situation("locked", require_unlocked=True) is None
        sql = cursor.execute.await_args[0][0]
        assert "unlocked = 1" in sql

    async def test_get_user_situation(self, bot_with_pool):
        _, cursor = bot_with_pool
        cursor.fetchall.return_value = [
            (USER_ID, "prompt", "mine", None, 0.8, 0.9, 0.1, 0.2, True),
        ]
        situation = await AiService.get_user_situation(USER_ID)
        assert situation is not None
        assert situation.unlocked is True

    async def test_get_user_situation_missing(self, bot_with_pool):
        _, cursor = bot_with_pool
        cursor.fetchall.return_value = []
        assert await AiService.get_user_situation(USER_ID) is None

    async def test_create_situation(self, bot_with_pool):
        _, cursor = bot_with_pool
        cursor.rowcount = 1
        params = CreateSituationParams(
            user_id=USER_ID,
            situation="You are a pirate speaking only in nautical terms for fun.",
            name="pirategpt",
        )
        await AiService.create_situation(params)
        assert "aiSituations" in cursor.execute.await_args[0][0]

    async def test_delete_situation(self, bot_with_pool):
        _, cursor = bot_with_pool
        cursor.rowcount = 1
        await AiService.delete_situation(USER_ID)
        assert "DELETE FROM aiSituations" in cursor.execute.await_args[0][0]

    async def test_unlock_situation(self, bot_with_pool):
        _, cursor = bot_with_pool
        cursor.rowcount = 1
        await AiService.unlock_situation(USER_ID)
        assert "unlocked = 1" in cursor.execute.await_args[0][0]

    async def test_get_public_situations(self, bot_with_pool):
        _, cursor = bot_with_pool
        cursor.fetchall.return_value = [("sit_a",), ("sit_b",)]
        names = await AiService.get_public_situations()
        assert names == ["sit_a", "sit_b"]

    async def test_get_public_situations_iterator(self, bot_with_pool):
        _, cursor = bot_with_pool
        cursor.__aiter__ = MagicMock(return_value=AsyncIter([("iter_a",), ("iter_b",)]))
        collected = []
        async for name in AiService.get_public_situations_iterator():
            collected.append(name)
        assert collected == ["iter_a", "iter_b"]
