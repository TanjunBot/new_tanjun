from __future__ import annotations

import json
from unittest.mock import AsyncMock, MagicMock, patch

import aiohttp
import pytest

from services.brawlstars import BrawlStarsService


@pytest.fixture
def service() -> BrawlStarsService:
    return BrawlStarsService(token="test_token")


def _mock_response(status: int, json_data=None, headers=None):
    resp = AsyncMock()
    resp.status = status
    resp.headers = headers or {}
    resp.json = AsyncMock(return_value=json_data)
    resp.__aenter__ = AsyncMock(return_value=resp)
    resp.__aexit__ = AsyncMock(return_value=None)
    return resp


@pytest.mark.asyncio
async def test_get_retries_on_429(service: BrawlStarsService):
    session = AsyncMock()
    session.closed = False
    session.get = MagicMock(
        side_effect=[
            _mock_response(429, headers={"Retry-After": "0"}),
            _mock_response(200, {"tag": "#ABC", "name": "P", "trophies": 0}),
        ]
    )
    service._session = session
    service._owns_session = False
    with patch("asyncio.sleep", AsyncMock()):
        result = await service._get("/players/%23ABC")
    assert result is not None


@pytest.mark.asyncio
async def test_get_returns_none_on_error(service: BrawlStarsService):
    session = AsyncMock()
    session.closed = False
    session.get = MagicMock(side_effect=aiohttp.ClientError())
    service._session = session
    service._owns_session = False
    result = await service._get("/x")
    assert result is None


@pytest.mark.asyncio
async def test_get_battle_log(service: BrawlStarsService):
    items = [{"battleTime": "20240101T120000.000Z", "event": {"mode": "gemGrab", "map": "m"}, "battle": {"type": "ranked"}}]
    with patch.object(service, "_get", AsyncMock(return_value={"items": items})):
        battles = await service.get_battle_log("#TAG")
    assert len(battles) == 1


@pytest.mark.asyncio
async def test_get_events(service: BrawlStarsService):
    data = [
        {"startTime": "20240101T120000.000Z", "endTime": "20240101T130000.000Z", "event": {"id": 1, "mode": "m", "map": "map"}}
    ]
    with patch.object(service, "_get_list", AsyncMock(return_value=data)):
        events = await service.get_events()
    assert len(events) == 1


@pytest.mark.asyncio
async def test_get_club(service: BrawlStarsService):
    with patch.object(service, "_get", AsyncMock(return_value={"tag": "#C", "name": "Club", "requiredTrophies": 0})):
        club = await service.get_club("#C")
    assert club is not None
    assert club.name == "Club"


@pytest.mark.asyncio
async def test_context_manager(service: BrawlStarsService):
    with patch.object(service, "close", AsyncMock()) as close:
        async with service:
            pass
        close.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_list_non_200(service: BrawlStarsService):
    session = AsyncMock()
    session.closed = False
    session.get = MagicMock(return_value=_mock_response(500))
    service._session = session
    service._owns_session = False
    result = await service._get_list("/events/rotation")
    assert result == []


@pytest.mark.asyncio
async def test_get_json_decode_error(service: BrawlStarsService):
    session = AsyncMock()
    session.closed = False
    bad = _mock_response(200)
    bad.json = AsyncMock(side_effect=json.JSONDecodeError("x", "y", 0))
    session.get = MagicMock(return_value=bad)
    service._session = session
    service._owns_session = False
    result = await service._get("/x")
    assert result is None
