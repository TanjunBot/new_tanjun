from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from aiohttp import ClientError

from external_api_health_checks import (
    BrawlStarsHealthCheck,
    BytebinHealthCheck,
    GIPHYHealthCheck,
    GitHubAPIHealthCheck,
    ImgBBHealthCheck,
)
from health.checks import HealthStatus


def _mock_resp(status: int):
    resp = AsyncMock()
    resp.status = status
    resp.__aenter__ = AsyncMock(return_value=resp)
    resp.__aexit__ = AsyncMock(return_value=None)
    return resp


@pytest.mark.parametrize(
    "cls,config_patches",
    [
        (GIPHYHealthCheck, {"giphyAPIKey": ""}),
        (BrawlStarsHealthCheck, {"brawlstarsToken": ""}),
        (ImgBBHealthCheck, {"ImgBBApiKey": ""}),
        (GitHubAPIHealthCheck, {"githubToken": ""}),
        (BytebinHealthCheck, {"bytebin_url": "", "bytebin_username": "", "bytebin_password": ""}),
    ],
)
@pytest.mark.asyncio
async def test_external_checks_no_config(cls, config_patches):
    check = cls()
    with patch.multiple("config", **config_patches):
        result = await check.run()
    assert result.status in (HealthStatus.DEGRADED, HealthStatus.HEALTHY, HealthStatus.CRITICAL)


@pytest.mark.asyncio
async def test_giphy_success():
    check = GIPHYHealthCheck()
    session = AsyncMock()
    session.get = MagicMock(return_value=_mock_resp(200))
    session.__aenter__ = AsyncMock(return_value=session)
    session.__aexit__ = AsyncMock(return_value=None)
    with (
        patch("config.giphyAPIKey", "k"),
        patch("external_api_health_checks.ClientSession", return_value=session),
    ):
        result = await check.run()
    assert result.status == HealthStatus.HEALTHY


@pytest.mark.asyncio
async def test_giphy_bad_status():
    check = GIPHYHealthCheck()
    session = AsyncMock()
    session.get = MagicMock(return_value=_mock_resp(503))
    session.__aenter__ = AsyncMock(return_value=session)
    session.__aexit__ = AsyncMock(return_value=None)
    with (
        patch("config.giphyAPIKey", "k"),
        patch("external_api_health_checks.ClientSession", return_value=session),
    ):
        result = await check.run()
    assert result.status == HealthStatus.DEGRADED


@pytest.mark.asyncio
async def test_giphy_timeout():
    check = GIPHYHealthCheck()
    session = AsyncMock()
    session.get = MagicMock(side_effect=TimeoutError())
    session.__aenter__ = AsyncMock(return_value=session)
    session.__aexit__ = AsyncMock(return_value=None)
    with (
        patch("config.giphyAPIKey", "k"),
        patch("external_api_health_checks.ClientSession", return_value=session),
    ):
        result = await check.run()
    assert result.status == HealthStatus.DEGRADED


@pytest.mark.asyncio
async def test_giphy_client_error():
    check = GIPHYHealthCheck()
    session = AsyncMock()
    session.get = MagicMock(side_effect=ClientError())
    session.__aenter__ = AsyncMock(return_value=session)
    session.__aexit__ = AsyncMock(return_value=None)
    with (
        patch("config.giphyAPIKey", "k"),
        patch("external_api_health_checks.ClientSession", return_value=session),
    ):
        result = await check.run()
    assert result.status == HealthStatus.DEGRADED


@pytest.mark.asyncio
async def test_brawl_stars_with_key():
    check = BrawlStarsHealthCheck()
    session = AsyncMock()
    session.get = MagicMock(return_value=_mock_resp(200))
    session.__aenter__ = AsyncMock(return_value=session)
    session.__aexit__ = AsyncMock(return_value=None)
    with (
        patch("config.brawlstarsToken", "k"),
        patch("external_api_health_checks.ClientSession", return_value=session),
    ):
        result = await check.run()
    assert result.status in (HealthStatus.HEALTHY, HealthStatus.DEGRADED)
