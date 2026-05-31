from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest

from services.brawlstars import BrawlStarPlayerBrawler, BrawlStarsClub, BrawlStarsPlayer
from tests.helpers.assertions import assert_reply_embed

pytestmark = pytest.mark.asyncio


def _player(**kwargs):
    defaults = {
        "tag": "#ABC123",
        "name": "TestPlayer",
        "trophies": 5000,
        "highest_trophies": 6000,
        "exp_level": 50,
        "x3vs3_victories": 100,
        "solo_victories": 50,
        "duo_victories": 25,
        "club": BrawlStarsClub(tag="#CLUB1", name="TestClub"),
        "brawlers": [],
        "name_color": None,
    }
    defaults.update(kwargs)
    return BrawlStarsPlayer(**defaults)


@patch("commands.utility.brawlstars.playerinfo.get_brawlstars_linked_account", new_callable=AsyncMock)
async def test_playerinfo_not_linked(mock_linked, admin_command_info):
    from commands.utility.brawlstars.playerinfo import player_info

    mock_linked.return_value = None
    await player_info(admin_command_info)
    assert_reply_embed(admin_command_info)


@patch("commands.utility.brawlstars.playerinfo.get_brawlstars_service")
async def test_playerinfo_not_found(mock_service, admin_command_info):
    from commands.utility.brawlstars.playerinfo import player_info

    mock_service.return_value.get_player = AsyncMock(return_value=None)
    await player_info(admin_command_info, "#INVALID")
    admin_command_info.reply.assert_awaited_once()


@patch("commands.utility.brawlstars.playerinfo.get_brawlstars_service")
async def test_playerinfo_success(mock_service, admin_command_info):
    from commands.utility.brawlstars.playerinfo import player_info

    mock_service.return_value.get_player = AsyncMock(return_value=_player())
    mock_service.return_value.get_brawler_list = AsyncMock(return_value=[BrawlStarPlayerBrawler(id=1, name="Shelly")])
    await player_info(admin_command_info, "#ABC123")
    assert_reply_embed(admin_command_info)


@patch("commands.utility.brawlstars.playerinfo.get_brawlstars_linked_account", new_callable=AsyncMock)
async def test_playerinfo_mention_not_linked(mock_linked, admin_command_info):
    from commands.utility.brawlstars.playerinfo import player_info

    mock_linked.return_value = None
    await player_info(admin_command_info, "<@222222222>")
    assert_reply_embed(admin_command_info)


@patch("commands.utility.brawlstars.playerinfo.get_brawlstars_service")
async def test_playerinfo_adds_hash_prefix(mock_service, admin_command_info):
    from commands.utility.brawlstars.playerinfo import player_info

    mock_service.return_value.get_player = AsyncMock(return_value=_player())
    mock_service.return_value.get_brawler_list = AsyncMock(return_value=[])
    await player_info(admin_command_info, "ABC123")
    mock_service.return_value.get_player.assert_awaited_once_with("#ABC123")
