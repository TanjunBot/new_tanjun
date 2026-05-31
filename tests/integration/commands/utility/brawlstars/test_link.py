from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest

from services.brawlstars import BrawlStarsClub, BrawlStarsPlayer
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


@patch("commands.utility.brawlstars.link.get_brawlstars_linked_account", new_callable=AsyncMock)
@patch("commands.utility.brawlstars.link.add_brawlstars_linked_account", new_callable=AsyncMock)
@patch("commands.utility.brawlstars.link.get_brawlstars_service")
async def test_link_success(mock_service, mock_add, mock_linked, admin_command_info):
    from commands.utility.brawlstars.link import link

    mock_linked.return_value = None
    mock_service.return_value.get_player = AsyncMock(return_value=_player())
    await link(admin_command_info, "ABC123")
    assert_reply_embed(admin_command_info)
    mock_add.assert_awaited_once()


@patch("commands.utility.brawlstars.link.get_brawlstars_service")
async def test_link_not_found(mock_service, admin_command_info):
    from commands.utility.brawlstars.link import link

    mock_service.return_value.get_player = AsyncMock(return_value=None)
    await link(admin_command_info, "INVALID")
    assert_reply_embed(admin_command_info)


@patch("commands.utility.brawlstars.link.get_brawlstars_linked_account", new_callable=AsyncMock)
@patch("commands.utility.brawlstars.link.get_brawlstars_service")
async def test_link_already_linked(mock_service, mock_linked, admin_command_info):
    from commands.utility.brawlstars.link import link

    mock_linked.return_value = "#EXISTING"
    mock_service.return_value.get_player = AsyncMock(return_value=_player())
    await link(admin_command_info, "ABC123")
    assert_reply_embed(admin_command_info)


@patch("commands.utility.brawlstars.link.get_brawlstars_service")
async def test_link_adds_hash_prefix(mock_service, admin_command_info):
    from commands.utility.brawlstars.link import link

    mock_service.return_value.get_player = AsyncMock(return_value=_player())
    with patch("commands.utility.brawlstars.link.get_brawlstars_linked_account", new=AsyncMock(return_value=None)):
        with patch("commands.utility.brawlstars.link.add_brawlstars_linked_account", new=AsyncMock()) as mock_add:
            await link(admin_command_info, "ABC123")
            mock_add.assert_awaited_once()
            assert mock_add.await_args.args[1] == "#ABC123"
