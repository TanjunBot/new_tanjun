"""Tests for services/brawlstars.py."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from services.brawlstars import BrawlStarsPlayer, BrawlStarsService


@pytest.fixture
def service() -> BrawlStarsService:
    return BrawlStarsService(token="test_token")


def _player_data() -> dict:
    return {
        "tag": "#ABC123",
        "name": "Player",
        "trophies": 1000,
        "highestTrophies": 1500,
        "expLevel": 50,
        "expPoints": 100,
        "isQualifiedFromChampionshipChallenge": False,
        "3vs3Victories": 100,
        "soloVictories": 50,
        "duoVictories": 30,
        "bestRoboRumbleTime": 0,
        "bestTimeAsBigBrawler": 0,
        "club": {"tag": "#CLUB", "name": "Club"},
    }


class TestBrawlStarsService:
    @pytest.mark.asyncio
    async def test_get_player_success(self, service: BrawlStarsService):
        with patch.object(service, "_get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = _player_data()
            result = await service.get_player("#ABC123")
        assert isinstance(result, BrawlStarsPlayer)
        assert result.name == "Player"

    @pytest.mark.asyncio
    async def test_get_player_not_found(self, service: BrawlStarsService):
        with patch.object(service, "_get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = None
            result = await service.get_player("#MISSING")
        assert result is None

    @pytest.mark.asyncio
    async def test_link_account(self, service: BrawlStarsService):
        with patch("api.add_brawlstars_linked_account", new_callable=AsyncMock) as mock_add:
            await service.link_account("11111111111111111", "#ABC")
            mock_add.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_unlink_account(self, service: BrawlStarsService):
        with patch("api.remove_brawlstars_linked_account", new_callable=AsyncMock) as mock_remove:
            await service.unlink_account("11111111111111111")
            mock_remove.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_get_linked_account(self, service: BrawlStarsService):
        with patch("api.get_brawlstars_linked_account", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = "#ABC"
            result = await service.get_linked_account("11111111111111111")
        assert result == "#ABC"

    @pytest.mark.asyncio
    async def test_close_owned_session(self, service: BrawlStarsService):
        mock_session = AsyncMock()
        mock_session.closed = False
        service._session = mock_session
        service._owns_session = True
        await service.close()
        mock_session.close.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_get_brawler_list(self, service: BrawlStarsService):
        with patch.object(service, "_get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = {"items": []}
            result = await service.get_brawler_list()
        assert result == []
