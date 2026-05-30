"""Tests for services/booster_service.py."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest

from services.booster_service import BoosterService, BoosterType, ClaimedBoosterType


@pytest.fixture
def service() -> BoosterService:
    return BoosterService()


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
