from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from external_api_health_checks import GIPHYHealthCheck

from health.checks import HealthStatus

pytestmark = pytest.mark.asyncio


async def test_giphy_no_api_key():
    with patch("config.giphyAPIKey", ""):
        result = await GIPHYHealthCheck().run()
    assert result.status == HealthStatus.DEGRADED


async def test_giphy_healthy():
    response = MagicMock(status=200)
    cm = MagicMock(__aenter__=AsyncMock(return_value=response), __aexit__=AsyncMock(return_value=False))
    session = MagicMock()
    session.get = MagicMock(return_value=cm)
    session.__aenter__ = AsyncMock(return_value=session)
    session.__aexit__ = AsyncMock(return_value=False)
    with (
        patch("config.giphyAPIKey", "key"),
        patch("external_api_health_checks.ClientSession", return_value=session),
    ):
        result = await GIPHYHealthCheck().run()
    assert result.status == HealthStatus.HEALTHY
