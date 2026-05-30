"""Tests for services/ai_service.py."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest

from services.ai_service import AiService, AiTokenUsage, CreateSituationParams
from tests.helpers.factories import USER_ID


class TestAiTokenUsage:
    def test_total_available(self):
        usage = AiTokenUsage(user_id=USER_ID, free_token=10, plus_token=5, paid_token=3, used_token=2)
        assert usage.total_available == 18


class TestAiService:
    @pytest.fixture
    def service(self) -> AiService:
        return AiService()

    @pytest.mark.asyncio
    async def test_get_usage_found(self, service: AiService):
        with patch("api.execute_query", new_callable=AsyncMock) as mock_q:
            mock_q.return_value = [(USER_ID, 100, 50, 25, 10)]
            result = await AiService.get_usage(USER_ID)
        assert result is not None
        assert result.free_token == 100

    @pytest.mark.asyncio
    async def test_get_usage_none(self, service: AiService):
        with patch("api.execute_query", new_callable=AsyncMock) as mock_q:
            mock_q.return_value = []
            result = await AiService.get_usage(USER_ID)
        assert result is None

    @pytest.mark.asyncio
    async def test_get_available_tokens(self, service: AiService):
        with patch("api.execute_query", new_callable=AsyncMock) as mock_q:
            mock_q.return_value = [(USER_ID, 100, 50, 25, 10)]
            result = await AiService.get_available_tokens(USER_ID)
        assert result == 175

    @pytest.mark.asyncio
    async def test_consume_success(self, service: AiService):
        with patch("api.execute_action", new_callable=AsyncMock, return_value=1):
            with patch("api.execute_query", new_callable=AsyncMock) as mock_q:
                mock_q.return_value = [(100, 0, 0)]
                result = await AiService.consume(USER_ID, 5)
        assert result is True

    @pytest.mark.asyncio
    async def test_initialize_user(self, service: AiService):
        with patch("api.execute_action", new_callable=AsyncMock) as mock_exec:
            await AiService.initialize_user(USER_ID)
            mock_exec.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_create_situation(self, service: AiService):
        params = CreateSituationParams(
            user_id=USER_ID,
            situation="You are helpful",
            name="helper",
        )
        with patch("api.execute_action", new_callable=AsyncMock) as mock_exec:
            await AiService.create_situation(params)
            mock_exec.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_delete_situation(self, service: AiService):
        with patch("api.execute_action", new_callable=AsyncMock) as mock_exec:
            await AiService.delete_situation(USER_ID)
            mock_exec.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_get_public_situations(self, service: AiService):
        with patch("api.safe_execute_query", new_callable=AsyncMock) as mock_q:
            mock_q.return_value = [("situation1",), ("situation2",)]
            result = await AiService.get_public_situations()
        assert result == ["situation1", "situation2"]
