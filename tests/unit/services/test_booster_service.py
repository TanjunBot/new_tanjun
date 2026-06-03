"""Tests for services/booster_service.py."""

from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, patch

import pytest

from services.booster_service import (
    BoosterService,
    BoosterType,
    ClaimedBoosterType,
    _claimed_all_cache,
    clear_booster_read_cache,
)
from tests.helpers.concurrency import stress_concurrent
from tests.helpers.factories import CHANNEL_ID, GUILD_ID, ROLE_ID, USER_ID


@pytest.fixture
def service() -> BoosterService:
    return BoosterService()


@pytest.fixture(autouse=True)
def _reset_cache() -> None:
    clear_booster_read_cache()
    yield
    clear_booster_read_cache()


class TestBoosterService:
    @pytest.mark.asyncio
    async def test_add_channel(self, service: BoosterService):
        with patch("services.booster_service.execute_action", new_callable=AsyncMock) as mock_exec:
            await service.add(BoosterType.CHANNEL, "123", "444")
            assert "booster_channel" in mock_exec.await_args[0][0]

    @pytest.mark.asyncio
    async def test_add_role(self, service: BoosterService):
        with patch("services.booster_service.execute_action", new_callable=AsyncMock) as mock_exec:
            await service.add(BoosterType.ROLE, "123", "777")
            assert "boosterRole" in mock_exec.await_args[0][0]

    @pytest.mark.asyncio
    async def test_get_found(self, service: BoosterService):
        with patch("services.booster_service.execute_query", new_callable=AsyncMock) as mock_q:
            mock_q.return_value = [("444",)]
            result = await service.get(BoosterType.CHANNEL, "123")
            assert result == "444"

    @pytest.mark.asyncio
    async def test_get_none(self, service: BoosterService):
        with patch("services.booster_service.execute_query", new_callable=AsyncMock) as mock_q:
            mock_q.return_value = []
            result = await service.get(BoosterType.ROLE, "123")
            assert result is None

    @pytest.mark.asyncio
    async def test_delete_channel_requires_entity_id(self, service: BoosterService):
        with pytest.raises(ValueError, match="entity_id is required"):
            await service.delete(BoosterType.CHANNEL, "123")

    @pytest.mark.asyncio
    async def test_delete_channel(self, service: BoosterService):
        with patch("services.booster_service.execute_action", new_callable=AsyncMock) as mock_exec:
            await service.delete(BoosterType.CHANNEL, "123", "444")
            mock_exec.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_delete_role(self, service: BoosterService):
        with patch("services.booster_service.execute_action", new_callable=AsyncMock) as mock_exec:
            await service.delete(BoosterType.ROLE, "123")
            mock_exec.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_claim(self, service: BoosterService):
        with patch("services.booster_service.execute_action", new_callable=AsyncMock) as mock_exec:
            await service.claim(ClaimedBoosterType.CHANNEL, "111", "444", "123")
            assert "claimedBoosterChannel" in mock_exec.await_args[0][0]

    @pytest.mark.asyncio
    async def test_unclaim(self, service: BoosterService):
        with patch("services.booster_service.execute_action", new_callable=AsyncMock) as mock_exec:
            await service.unclaim(ClaimedBoosterType.ROLE, "111", "123")
            mock_exec.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_has_claim_true(self, service: BoosterService):
        with patch("services.booster_service.safe_execute_query", new_callable=AsyncMock) as mock_q:
            mock_q.return_value = [(1,)]
            assert await service.has_claim(ClaimedBoosterType.CHANNEL, "111") is True

    @pytest.mark.asyncio
    async def test_has_claim_false(self, service: BoosterService):
        with patch("services.booster_service.safe_execute_query", new_callable=AsyncMock) as mock_q:
            mock_q.return_value = []
            assert await service.has_claim(ClaimedBoosterType.CHANNEL, "111") is False

    @pytest.mark.asyncio
    async def test_get_claim_for_user_found(self, service: BoosterService):
        with patch("services.booster_service.safe_execute_query", new_callable=AsyncMock) as mock_q:
            mock_q.return_value = [(CHANNEL_ID,)]
            result = await service.get_claim_for_user(ClaimedBoosterType.CHANNEL, USER_ID, GUILD_ID)
            assert result == CHANNEL_ID

    @pytest.mark.asyncio
    async def test_get_claim_for_user_empty(self, service: BoosterService):
        with patch("services.booster_service.safe_execute_query", new_callable=AsyncMock) as mock_q:
            mock_q.return_value = []
            result = await service.get_claim_for_user(ClaimedBoosterType.ROLE, USER_ID, GUILD_ID)
            assert result is None

    @pytest.mark.asyncio
    async def test_get_user_claims_channel(self, service: BoosterService):
        with patch("services.booster_service.safe_execute_query", new_callable=AsyncMock) as mock_q:
            mock_q.return_value = [(USER_ID, CHANNEL_ID, GUILD_ID)]
            claims = await service.get_user_claims(ClaimedBoosterType.CHANNEL, USER_ID)
            assert len(claims) == 1
            assert str(claims[0].channel_id) == CHANNEL_ID

    @pytest.mark.asyncio
    async def test_get_user_claims_role_empty(self, service: BoosterService):
        with patch("services.booster_service.safe_execute_query", new_callable=AsyncMock) as mock_q:
            mock_q.return_value = []
            claims = await service.get_user_claims(ClaimedBoosterType.ROLE, USER_ID)
            assert claims == []

    @pytest.mark.asyncio
    async def test_get_all_claims_channel(self, service: BoosterService):
        with patch("services.booster_service.safe_execute_query", new_callable=AsyncMock) as mock_q:
            mock_q.return_value = [(USER_ID, CHANNEL_ID, GUILD_ID)]
            claims = await service.get_all_claims(ClaimedBoosterType.CHANNEL)
            assert len(claims) == 1

    @pytest.mark.asyncio
    async def test_get_all_claims_role_empty(self, service: BoosterService):
        with patch("services.booster_service.safe_execute_query", new_callable=AsyncMock) as mock_q:
            mock_q.return_value = []
            claims = await service.get_all_claims(ClaimedBoosterType.ROLE)
            assert claims == []

    @pytest.mark.asyncio
    async def test_get_all_claims_recovers_from_cached_none(self, service: BoosterService):
        with patch("services.booster_service.safe_execute_query", new_callable=AsyncMock) as mock_q:
            mock_q.return_value = [(USER_ID, CHANNEL_ID, GUILD_ID)]
            _claimed_all_cache.set(ClaimedBoosterType.CHANNEL.name, None)
            claims = await service.get_all_claims(ClaimedBoosterType.CHANNEL)
            assert len(claims) == 1
            mock_q.assert_awaited_once()


class TestBoosterServiceDbErrors:
    @pytest.mark.asyncio
    async def test_add_propagates_db_error(self, service: BoosterService):
        with patch(
            "services.booster_service.execute_action",
            new_callable=AsyncMock,
            side_effect=RuntimeError("db down"),
        ):
            with pytest.raises(RuntimeError, match="db down"):
                await service.add(BoosterType.CHANNEL, GUILD_ID, CHANNEL_ID)

    @pytest.mark.asyncio
    async def test_get_propagates_db_error(self, service: BoosterService):
        with patch(
            "services.booster_service.execute_query",
            new_callable=AsyncMock,
            side_effect=RuntimeError("query failed"),
        ):
            with pytest.raises(RuntimeError, match="query failed"):
                await service.get(BoosterType.ROLE, GUILD_ID)

    @pytest.mark.asyncio
    async def test_delete_channel_propagates_db_error(self, service: BoosterService):
        with patch(
            "services.booster_service.execute_action",
            new_callable=AsyncMock,
            side_effect=RuntimeError("delete failed"),
        ):
            with pytest.raises(RuntimeError, match="delete failed"):
                await service.delete(BoosterType.CHANNEL, GUILD_ID, CHANNEL_ID)

    @pytest.mark.asyncio
    async def test_claim_propagates_db_error(self, service: BoosterService):
        with patch(
            "services.booster_service.execute_action",
            new_callable=AsyncMock,
            side_effect=RuntimeError("claim failed"),
        ):
            with pytest.raises(RuntimeError, match="claim failed"):
                await service.claim(ClaimedBoosterType.CHANNEL, USER_ID, CHANNEL_ID, GUILD_ID)

    @pytest.mark.asyncio
    async def test_unclaim_propagates_db_error(self, service: BoosterService):
        with patch(
            "services.booster_service.execute_action",
            new_callable=AsyncMock,
            side_effect=RuntimeError("unclaim failed"),
        ):
            with pytest.raises(RuntimeError, match="unclaim failed"):
                await service.unclaim(ClaimedBoosterType.ROLE, USER_ID, GUILD_ID)

    @pytest.mark.asyncio
    async def test_get_claim_for_user_propagates_db_error(self, service: BoosterService):
        with patch(
            "services.booster_service.safe_execute_query",
            new_callable=AsyncMock,
            side_effect=RuntimeError("safe query failed"),
        ):
            with pytest.raises(RuntimeError, match="safe query failed"):
                await service.get_claim_for_user(ClaimedBoosterType.CHANNEL, USER_ID, GUILD_ID)

    @pytest.mark.asyncio
    async def test_has_claim_propagates_db_error(self, service: BoosterService):
        with patch(
            "services.booster_service.safe_execute_query",
            new_callable=AsyncMock,
            side_effect=RuntimeError("has claim failed"),
        ):
            with pytest.raises(RuntimeError, match="has claim failed"):
                await service.has_claim(ClaimedBoosterType.ROLE, USER_ID)

    @pytest.mark.asyncio
    async def test_get_user_claims_propagates_db_error(self, service: BoosterService):
        with patch(
            "services.booster_service.safe_execute_query",
            new_callable=AsyncMock,
            side_effect=RuntimeError("user claims failed"),
        ):
            with pytest.raises(RuntimeError, match="user claims failed"):
                await service.get_user_claims(ClaimedBoosterType.CHANNEL, USER_ID)

    @pytest.mark.asyncio
    async def test_get_all_claims_propagates_db_error(self, service: BoosterService):
        with patch(
            "services.booster_service.safe_execute_query",
            new_callable=AsyncMock,
            side_effect=RuntimeError("all claims failed"),
        ):
            with pytest.raises(RuntimeError, match="all claims failed"):
                await service.get_all_claims(ClaimedBoosterType.ROLE)


class TestBoosterServiceCache:
    @pytest.mark.asyncio
    async def test_get_all_claims_concurrent_single_query(self, service: BoosterService):
        safe = AsyncMock(return_value=[(USER_ID, ROLE_ID, GUILD_ID)])
        with patch("services.booster_service.safe_execute_query", new=safe):
            results = await asyncio.gather(
                *[service.get_all_claims(ClaimedBoosterType.ROLE) for _ in range(30)]
            )
        assert len(results) == 30
        assert safe.await_count == 1

    @pytest.mark.asyncio
    async def test_claim_invalidates_get_all_claims_cache(self, service: BoosterService):
        with (
            patch("services.booster_service.execute_action", new_callable=AsyncMock),
            patch(
                "services.booster_service.safe_execute_query",
                new_callable=AsyncMock,
                return_value=[],
            ) as safe,
        ):
            await service.get_all_claims(ClaimedBoosterType.CHANNEL)
            await service.claim(ClaimedBoosterType.CHANNEL, USER_ID, CHANNEL_ID, GUILD_ID)
            await service.get_all_claims(ClaimedBoosterType.CHANNEL)
        assert safe.await_count == 2

    @pytest.mark.asyncio
    async def test_unclaim_invalidates_get_all_claims_cache(self, service: BoosterService):
        with (
            patch("services.booster_service.execute_action", new_callable=AsyncMock),
            patch(
                "services.booster_service.safe_execute_query",
                new_callable=AsyncMock,
                return_value=[],
            ) as safe,
        ):
            await service.get_all_claims(ClaimedBoosterType.ROLE)
            await service.unclaim(ClaimedBoosterType.ROLE, USER_ID, GUILD_ID)
            await service.get_all_claims(ClaimedBoosterType.ROLE)
        assert safe.await_count == 2

    @pytest.mark.asyncio
    async def test_concurrent_claims_all_execute(self, service: BoosterService):
        action = AsyncMock()
        with patch("services.booster_service.execute_action", new=action):
            await stress_concurrent(
                lambda: service.claim(ClaimedBoosterType.CHANNEL, USER_ID, CHANNEL_ID, GUILD_ID),
                n=20,
            )
        assert action.await_count == 20
