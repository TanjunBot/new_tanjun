from unittest.mock import AsyncMock, patch

import pytest

from services.brawlstars import (
    BrawlerInfo,
    BrawlStarPlayerBrawler,
    BrawlStarsBattle,
    BrawlStarsClub,
    BrawlStarsClubMember,
    BrawlStarsEvent,
    BrawlStarsEventDetail,
    BrawlStarsPlayer,
)
from tests.helpers.discord import make_command_info

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
        "brawlers": [
            BrawlerInfo(id=1, name="Shelly", power=11, rank=35, trophies=800, highest_trophies=900),
        ],
        "name_color": None,
    }
    defaults.update(kwargs)
    return BrawlStarsPlayer(**defaults)


def _battle():
    return BrawlStarsBattle.model_validate(
        {
            "battleTime": "20240101T120000.000Z",
            "event": {"id": 1, "mode": "gemGrab", "map": "Hard Rock Mine"},
            "battle": {
                "mode": "gemGrab",
                "type": "ranked",
                "result": "victory",
                "duration": 120,
                "trophyChange": 8,
            },
        }
    )


def _club():
    return BrawlStarsClub(
        tag="#CLUB1",
        name="TestClub",
        description="A club",
        required_trophies=1000,
        trophies=50000,
        members=[
            BrawlStarsClubMember(tag="#M1", name="Leader", role="president", trophies=10000),
            BrawlStarsClubMember(tag="#M2", name="Member", role="member", trophies=5000),
        ],
    )


def _event():
    return BrawlStarsEvent(
        start_time="2024-01-01T12:00:00.000Z",
        end_time="2024-01-01T18:00:00.000Z",
        event=BrawlStarsEventDetail(id=1, mode="gemGrab", map="Hard Rock Mine"),
    )


@pytest.mark.asyncio
@patch("commands.utility.brawlstars.link.get_brawlstars_linked_account", new_callable=AsyncMock)
@patch("commands.utility.brawlstars.link.add_brawlstars_linked_account", new_callable=AsyncMock)
@patch("commands.utility.brawlstars.link.get_brawlstars_service")
async def test_link_success(mock_service, mock_add, mock_linked):
    from commands.utility.brawlstars.link import link

    mock_linked.return_value = None
    mock_service.return_value.get_player = AsyncMock(return_value=_player())
    info = make_command_info()
    await link(info, "ABC123")
    info.reply.assert_awaited_once()
    mock_add.assert_awaited_once()


@pytest.mark.asyncio
@patch("commands.utility.brawlstars.link.get_brawlstars_service")
async def test_link_not_found(mock_service):
    from commands.utility.brawlstars.link import link

    mock_service.return_value.get_player = AsyncMock(return_value=None)
    info = make_command_info()
    await link(info, "INVALID")
    info.reply.assert_awaited_once()


@pytest.mark.asyncio
@patch("commands.utility.brawlstars.link.get_brawlstars_linked_account", new_callable=AsyncMock)
@patch("commands.utility.brawlstars.link.get_brawlstars_service")
async def test_link_already_linked(mock_service, mock_linked):
    from commands.utility.brawlstars.link import link

    mock_linked.return_value = "#EXISTING"
    mock_service.return_value.get_player = AsyncMock(return_value=_player())
    info = make_command_info()
    await link(info, "ABC123")
    info.reply.assert_awaited_once()


@pytest.mark.asyncio
@patch("commands.utility.brawlstars.link.get_brawlstars_service")
async def test_link_adds_hash_prefix(mock_service):
    from commands.utility.brawlstars.link import link

    mock_service.return_value.get_player = AsyncMock(return_value=_player())
    with patch("commands.utility.brawlstars.link.get_brawlstars_linked_account", new=AsyncMock(return_value=None)):
        with patch("commands.utility.brawlstars.link.add_brawlstars_linked_account", new=AsyncMock()) as mock_add:
            info = make_command_info()
            await link(info, "ABC123")
            mock_add.assert_awaited_once()
            assert mock_add.await_args.args[1] == "#ABC123"


@pytest.mark.asyncio
@patch("commands.utility.brawlstars.unlink.get_brawlstars_linked_account", new_callable=AsyncMock)
async def test_unlink_not_linked(mock_linked):
    from commands.utility.brawlstars.unlink import unlink

    mock_linked.return_value = None
    info = make_command_info()
    await unlink(info)
    info.reply.assert_awaited_once()


@pytest.mark.asyncio
@patch("commands.utility.brawlstars.unlink.remove_brawlstars_linked_account", new_callable=AsyncMock)
@patch("commands.utility.brawlstars.unlink.get_brawlstars_linked_account", new_callable=AsyncMock)
async def test_unlink_success(mock_linked, mock_remove):
    from commands.utility.brawlstars.unlink import unlink

    mock_linked.return_value = "#ABC123"
    info = make_command_info()
    await unlink(info)
    info.reply.assert_awaited_once()
    mock_remove.assert_awaited_once()


@pytest.mark.asyncio
@patch("commands.utility.brawlstars.playerinfo.get_brawlstars_linked_account", new_callable=AsyncMock)
async def test_playerinfo_not_linked(mock_linked):
    from commands.utility.brawlstars.playerinfo import player_info

    mock_linked.return_value = None
    info = make_command_info()
    await player_info(info)
    info.reply.assert_awaited_once()


@pytest.mark.asyncio
@patch("commands.utility.brawlstars.playerinfo.get_brawlstars_service")
async def test_playerinfo_not_found(mock_service):
    from commands.utility.brawlstars.playerinfo import player_info

    mock_service.return_value.get_player = AsyncMock(return_value=None)
    info = make_command_info()
    await player_info(info, "#INVALID")
    info.reply.assert_awaited_once()


@pytest.mark.asyncio
@patch("commands.utility.brawlstars.playerinfo.get_brawlstars_service")
async def test_playerinfo_success(mock_service):
    from commands.utility.brawlstars.playerinfo import player_info

    mock_service.return_value.get_player = AsyncMock(return_value=_player())
    mock_service.return_value.get_brawler_list = AsyncMock(return_value=[BrawlStarPlayerBrawler(id=1, name="Shelly")])
    info = make_command_info()
    await player_info(info, "#ABC123")
    info.reply.assert_awaited_once()
    assert info.reply.await_args.kwargs.get("embed") is not None


@pytest.mark.asyncio
@patch("commands.utility.brawlstars.playerinfo.get_brawlstars_linked_account", new_callable=AsyncMock)
async def test_playerinfo_mention_not_linked(mock_linked):
    from commands.utility.brawlstars.playerinfo import player_info

    mock_linked.return_value = None
    info = make_command_info()
    await player_info(info, "<@222222222>")
    info.reply.assert_awaited_once()


@pytest.mark.asyncio
@patch("commands.utility.brawlstars.playerinfo.get_brawlstars_service")
async def test_playerinfo_adds_hash_prefix(mock_service):
    from commands.utility.brawlstars.playerinfo import player_info

    mock_service.return_value.get_player = AsyncMock(return_value=_player())
    mock_service.return_value.get_brawler_list = AsyncMock(return_value=[])
    info = make_command_info()
    await player_info(info, "ABC123")
    mock_service.return_value.get_player.assert_awaited_once_with("#ABC123")


@pytest.mark.asyncio
@patch("commands.utility.brawlstars.battlelog.get_brawlstars_linked_account", new_callable=AsyncMock)
async def test_battlelog_not_linked(mock_linked):
    from commands.utility.brawlstars.battlelog import battlelog

    mock_linked.return_value = None
    info = make_command_info()
    await battlelog(info)
    info.reply.assert_awaited_once()


@pytest.mark.asyncio
@patch("commands.utility.brawlstars.battlelog.get_brawlstars_service")
async def test_battlelog_not_found(mock_service):
    from commands.utility.brawlstars.battlelog import battlelog

    mock_service.return_value.get_battle_log = AsyncMock(return_value=[])
    info = make_command_info()
    await battlelog(info, "#ABC123")
    info.reply.assert_awaited_once()


@pytest.mark.asyncio
@patch("commands.utility.brawlstars.battlelog.get_brawlstars_service")
async def test_battlelog_success(mock_service):
    from commands.utility.brawlstars.battlelog import battlelog

    mock_service.return_value.get_battle_log = AsyncMock(return_value=[_battle()])
    info = make_command_info()
    await battlelog(info, "#ABC123")
    info.reply.assert_awaited_once()


@pytest.mark.asyncio
@patch("commands.utility.brawlstars.battlelog.get_brawlstars_linked_account", new_callable=AsyncMock)
async def test_battlelog_mention_not_linked(mock_linked):
    from commands.utility.brawlstars.battlelog import battlelog

    mock_linked.return_value = None
    info = make_command_info()
    await battlelog(info, "<@222222222>")
    info.reply.assert_awaited_once()


@pytest.mark.asyncio
@patch("commands.utility.brawlstars.club.get_brawlstars_service")
async def test_club_not_found(mock_service):
    from commands.utility.brawlstars.club import club

    mock_service.return_value.get_club = AsyncMock(return_value=None)
    info = make_command_info()
    await club(info, "INVALID")
    info.reply.assert_awaited_once()


@pytest.mark.asyncio
@patch("commands.utility.brawlstars.club.get_brawlstars_service")
async def test_club_success(mock_service):
    from commands.utility.brawlstars.club import club

    mock_service.return_value.get_club = AsyncMock(return_value=_club())
    info = make_command_info()
    await club(info, "CLUB1")
    info.reply.assert_awaited_once()
    assert info.reply.await_args.kwargs.get("view") is not None


@pytest.mark.asyncio
@patch("commands.utility.brawlstars.brawlers.get_brawlstars_linked_account", new_callable=AsyncMock)
async def test_brawlers_not_linked(mock_linked):
    from commands.utility.brawlstars.brawlers import brawlers

    mock_linked.return_value = None
    info = make_command_info()
    await brawlers(info)
    info.reply.assert_awaited_once()


@pytest.mark.asyncio
@patch("commands.utility.brawlstars.brawlers.get_brawlstars_service")
async def test_brawlers_not_found(mock_service):
    from commands.utility.brawlstars.brawlers import brawlers

    mock_service.return_value.get_player = AsyncMock(return_value=None)
    info = make_command_info()
    await brawlers(info, "#ABC123")
    info.reply.assert_awaited_once()


@pytest.mark.asyncio
@patch("commands.utility.brawlstars.brawlers.get_brawlstars_service")
async def test_brawlers_success(mock_service):
    from commands.utility.brawlstars.brawlers import brawlers

    mock_service.return_value.get_player = AsyncMock(return_value=_player())
    info = make_command_info()
    await brawlers(info, "#ABC123")
    info.reply.assert_awaited_once()
    assert info.reply.await_args.kwargs.get("embed") is not None


@pytest.mark.asyncio
@patch("commands.utility.brawlstars.events.get_brawlstars_service")
async def test_events_not_found(mock_service):
    from commands.utility.brawlstars.events import events

    mock_service.return_value.get_events = AsyncMock(return_value=[])
    info = make_command_info()
    await events(info)
    info.reply.assert_awaited_once()


@pytest.mark.asyncio
@patch("commands.utility.brawlstars.events.get_brawlstars_service")
async def test_events_single(mock_service):
    from commands.utility.brawlstars.events import events

    mock_service.return_value.get_events = AsyncMock(return_value=[_event()])
    info = make_command_info()
    await events(info)
    info.reply.assert_awaited_once()
    assert info.reply.await_args.kwargs.get("embed") is not None


@pytest.mark.asyncio
@patch("commands.utility.brawlstars.events.get_brawlstars_service")
async def test_events_multiple(mock_service):
    from commands.utility.brawlstars.events import events

    mock_service.return_value.get_events = AsyncMock(return_value=[_event(), _event()])
    info = make_command_info()
    await events(info)
    info.reply.assert_awaited_once()
    assert info.reply.await_args.kwargs.get("view") is not None
