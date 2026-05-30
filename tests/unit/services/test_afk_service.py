"""Tests for services/afk_service.py."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest

from services.afk_service import AfkMessage, AfkService


@pytest.fixture
def service() -> AfkService:
    return AfkService()


class TestAfkService:
    @pytest.mark.asyncio
    async def test_set_afk(self, service: AfkService):
        with patch("services.afk_service.execute_action", new_callable=AsyncMock) as mock_exec:
            await service.set_afk("111", "sleeping")
            mock_exec.assert_awaited_once()
            assert "afk_users" in mock_exec.await_args[0][0]

    @pytest.mark.asyncio
    async def test_remove_afk(self, service: AfkService):
        with patch("services.afk_service.execute_action", new_callable=AsyncMock) as mock_exec:
            await service.remove_afk("111")
            assert mock_exec.await_count == 2

    @pytest.mark.asyncio
    async def test_is_afk_true(self, service: AfkService):
        with patch("services.afk_service.safe_execute_query", new_callable=AsyncMock) as mock_q:
            mock_q.return_value = [(1,)]
            assert await service.is_afk("111") is True

    @pytest.mark.asyncio
    async def test_is_afk_false(self, service: AfkService):
        with patch("services.afk_service.safe_execute_query", new_callable=AsyncMock) as mock_q:
            mock_q.return_value = []
            assert await service.is_afk("111") is False

    @pytest.mark.asyncio
    async def test_get_reason(self, service: AfkService):
        with patch("services.afk_service.execute_query", new_callable=AsyncMock) as mock_q:
            mock_q.return_value = [("sleeping",)]
            assert await service.get_reason("111") == "sleeping"

    @pytest.mark.asyncio
    async def test_get_reason_none(self, service: AfkService):
        with patch("services.afk_service.execute_query", new_callable=AsyncMock) as mock_q:
            mock_q.return_value = []
            assert await service.get_reason("111") is None

    @pytest.mark.asyncio
    async def test_track_mention(self, service: AfkService):
        with patch("services.afk_service.execute_action", new_callable=AsyncMock) as mock_exec:
            await service.track_mention("111", "999", "444")
            assert "afkMessages" in mock_exec.await_args[0][0]

    @pytest.mark.asyncio
    async def test_get_mentions(self, service: AfkService):
        async def fake_iter(*args, **kwargs):
            yield ("999", "444")

        with patch("services.afk_service.execute_query_iter", side_effect=lambda q, p: fake_iter()):
            mentions = await service.get_mentions("111")
        assert mentions == [AfkMessage(message_id="999", channel_id="444")]

    @pytest.mark.asyncio
    async def test_clear_and_notify(self, service: AfkService):
        with patch.object(service, "get_mentions", new_callable=AsyncMock) as mock_get:
            with patch.object(service, "remove_afk", new_callable=AsyncMock) as mock_remove:
                mock_get.return_value = [AfkMessage("999", "444")]
                result = await service.clear_and_notify("111")
                mock_remove.assert_awaited_once()
                assert len(result) == 1
