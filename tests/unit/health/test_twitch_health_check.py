"""Tests for TwitchAPIHealthCheck."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from TwitchAPIHealthCheck import TwitchAPIHealthCheck
from health.checks import HealthStatus


def _mock_resp(status: int, json_data: dict | None = None):
    resp = AsyncMock()
    resp.status = status
    resp.json = AsyncMock(return_value=json_data or {})
    resp.__aenter__ = AsyncMock(return_value=resp)
    resp.__aexit__ = AsyncMock(return_value=None)
    return resp


class TestTwitchAPIHealthCheck:
    @pytest.fixture
    def check(self) -> TwitchAPIHealthCheck:
        return TwitchAPIHealthCheck()

    def test_name_and_critical(self, check: TwitchAPIHealthCheck):
        assert check.name == "Twitch API"
        assert check.critical is True

    @pytest.mark.asyncio
    async def test_missing_credentials(self, check: TwitchAPIHealthCheck):
        with patch("config.twitchId", ""):
            with patch("config.twitchSecret", ""):
                result = await check.run()
        assert result.status == HealthStatus.CRITICAL

    @pytest.mark.asyncio
    async def test_healthy(self, check: TwitchAPIHealthCheck):
        token_resp = _mock_resp(200, {"access_token": "token"})
        api_resp = _mock_resp(200)
        mock_session = AsyncMock()
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=None)
        mock_session.post = MagicMock(return_value=token_resp)
        mock_session.get = MagicMock(return_value=api_resp)

        with patch("TwitchAPIHealthCheck.ClientSession", return_value=mock_session):
            result = await check.run()
        assert result.status == HealthStatus.HEALTHY

    @pytest.mark.asyncio
    async def test_auth_failure(self, check: TwitchAPIHealthCheck):
        token_resp = _mock_resp(401, {"message": "Invalid client"})
        mock_session = AsyncMock()
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=None)
        mock_session.post = MagicMock(return_value=token_resp)

        with patch("TwitchAPIHealthCheck.ClientSession", return_value=mock_session):
            result = await check.run()
        assert result.status == HealthStatus.CRITICAL

    @pytest.mark.asyncio
    async def test_api_degraded(self, check: TwitchAPIHealthCheck):
        token_resp = _mock_resp(200, {"access_token": "token"})
        api_resp = _mock_resp(503)
        mock_session = AsyncMock()
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=None)
        mock_session.post = MagicMock(return_value=token_resp)
        mock_session.get = MagicMock(return_value=api_resp)

        with patch("TwitchAPIHealthCheck.ClientSession", return_value=mock_session):
            result = await check.run()
        assert result.status == HealthStatus.DEGRADED
