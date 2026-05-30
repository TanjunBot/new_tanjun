"""Tests for OpenAIHealthCheck."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from OpenAIHealthCheck import OpenAIHealthCheck

from health.checks import HealthStatus


def _mock_response(status: int):
    resp = AsyncMock()
    resp.status = status
    resp.__aenter__ = AsyncMock(return_value=resp)
    resp.__aexit__ = AsyncMock(return_value=None)
    return resp


class TestOpenAIHealthCheck:
    @pytest.fixture
    def check(self) -> OpenAIHealthCheck:
        return OpenAIHealthCheck()

    def test_name_and_critical(self, check: OpenAIHealthCheck):
        assert check.name == "OpenAI API"
        assert check.critical is True

    @pytest.mark.asyncio
    async def test_missing_key_critical(self, check: OpenAIHealthCheck):
        with patch("OpenAIHealthCheck.openAiKey", "", create=True), patch("config.openAiKey", ""):
            result = await check.run()
        assert result.status == HealthStatus.CRITICAL
        assert "not configured" in result.message.lower()

    @pytest.mark.asyncio
    async def test_healthy_on_200(self, check: OpenAIHealthCheck):
        mock_resp = _mock_response(200)
        mock_session = AsyncMock()
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=None)
        mock_session.get = MagicMock(return_value=mock_resp)

        with patch("OpenAIHealthCheck.ClientSession", return_value=mock_session):
            result = await check.run()
        assert result.status == HealthStatus.HEALTHY

    @pytest.mark.asyncio
    async def test_401_critical(self, check: OpenAIHealthCheck):
        mock_resp = _mock_response(401)
        mock_session = AsyncMock()
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=None)
        mock_session.get = MagicMock(return_value=mock_resp)

        with patch("OpenAIHealthCheck.ClientSession", return_value=mock_session):
            result = await check.run()
        assert result.status == HealthStatus.CRITICAL
        assert "401" in result.message

    @pytest.mark.asyncio
    async def test_429_degraded(self, check: OpenAIHealthCheck):
        mock_resp = _mock_response(429)
        mock_session = AsyncMock()
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=None)
        mock_session.get = MagicMock(return_value=mock_resp)

        with patch("OpenAIHealthCheck.ClientSession", return_value=mock_session):
            result = await check.run()
        assert result.status == HealthStatus.DEGRADED

    @pytest.mark.asyncio
    async def test_other_status_degraded(self, check: OpenAIHealthCheck):
        mock_resp = _mock_response(503)
        mock_session = AsyncMock()
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=None)
        mock_session.get = MagicMock(return_value=mock_resp)

        with patch("OpenAIHealthCheck.ClientSession", return_value=mock_session):
            result = await check.run()
        assert result.status == HealthStatus.DEGRADED

    @pytest.mark.asyncio
    async def test_timeout_degraded(self, check: OpenAIHealthCheck):
        mock_session = AsyncMock()
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=None)
        mock_session.get = MagicMock(side_effect=TimeoutError)

        with patch("OpenAIHealthCheck.ClientSession", return_value=mock_session):
            result = await check.run()
        assert result.status == HealthStatus.DEGRADED
        assert "timed out" in result.message.lower()
