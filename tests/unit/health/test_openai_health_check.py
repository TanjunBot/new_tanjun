from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from health.checks.openrouter import OpenRouterHealthCheck

from health.checks import HealthStatus


def _mock_response(status: int):
    resp = AsyncMock()
    resp.status = status
    resp.__aenter__ = AsyncMock(return_value=resp)
    resp.__aexit__ = AsyncMock(return_value=None)
    return resp


class TestOpenRouterHealthCheck:
    @pytest.fixture
    def check(self) -> OpenRouterHealthCheck:
        return OpenRouterHealthCheck()

    def test_name_and_critical(self, check: OpenRouterHealthCheck):
        assert check.name == "OpenRouter API"
        assert check.critical is True

    @pytest.mark.asyncio
    async def test_missing_key_critical(self, check: OpenRouterHealthCheck):
        with patch("services.openrouter_client.get_openrouter_api_key", return_value=""):
            result = await check.run()
        assert result.status == HealthStatus.CRITICAL
        assert "not configured" in result.message.lower()

    @pytest.mark.asyncio
    async def test_healthy_on_200(self, check: OpenRouterHealthCheck):
        mock_resp = _mock_response(200)
        mock_session = AsyncMock()
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=None)
        mock_session.get = MagicMock(return_value=mock_resp)

        with patch("health.checks.openrouter.ClientSession", return_value=mock_session):
            result = await check.run()
        assert result.status == HealthStatus.HEALTHY

    @pytest.mark.asyncio
    async def test_401_degraded(self, check: OpenRouterHealthCheck):
        mock_resp = _mock_response(401)
        mock_session = AsyncMock()
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=None)
        mock_session.get = MagicMock(return_value=mock_resp)

        with patch("health.checks.openrouter.ClientSession", return_value=mock_session):
            result = await check.run()
        assert result.status == HealthStatus.DEGRADED
        assert "401" in result.message

    @pytest.mark.asyncio
    async def test_429_degraded(self, check: OpenRouterHealthCheck):
        mock_resp = _mock_response(429)
        mock_session = AsyncMock()
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=None)
        mock_session.get = MagicMock(return_value=mock_resp)

        with patch("health.checks.openrouter.ClientSession", return_value=mock_session):
            result = await check.run()
        assert result.status == HealthStatus.DEGRADED

    @pytest.mark.asyncio
    async def test_other_status_degraded(self, check: OpenRouterHealthCheck):
        mock_resp = _mock_response(503)
        mock_session = AsyncMock()
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=None)
        mock_session.get = MagicMock(return_value=mock_resp)

        with patch("health.checks.openrouter.ClientSession", return_value=mock_session):
            result = await check.run()
        assert result.status == HealthStatus.DEGRADED

    @pytest.mark.asyncio
    async def test_timeout_degraded(self, check: OpenRouterHealthCheck):
        mock_session = AsyncMock()
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=None)
        mock_session.get = MagicMock(side_effect=TimeoutError)

        with patch("health.checks.openrouter.ClientSession", return_value=mock_session):
            result = await check.run()
        assert result.status == HealthStatus.DEGRADED
        assert "timed out" in result.message.lower()
