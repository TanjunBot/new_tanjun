from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from commands.utility.brawlstars.battlelog import battlelog
from services.brawlstars import BattleBrawler, BattlePlayer, BrawlStarsBattle
from tests.helpers.discord import make_target_member
from tests.integration.commands.admin.conftest import make_view_interaction

pytestmark = pytest.mark.asyncio


def _brawler():
    return BattleBrawler(id=1, name="Shelly", power=11, trophies=500)


def _player(tag="#ABC", name="Player"):
    return BattlePlayer(tag=tag, name=name, brawler=_brawler())


def _battle(**kwargs) -> BrawlStarsBattle:
    data = {
        "battleTime": "20240101T120000.000Z",
        "event": {"mode": "gemGrab", "map": "HardRockMine"},
        "battle": {
            "type": "ranked",
            "result": kwargs.get("result", "victory"),
            "duration": kwargs.get("duration", 90),
            "trophyChange": kwargs.get("trophy_change", 5),
            "starPlayer": kwargs.get("star_player"),
            "players": kwargs.get("players"),
            "teams": kwargs.get("teams"),
        },
    }
    return BrawlStarsBattle.model_validate(data)


@patch("commands.utility.brawlstars.battlelog.get_brawlstars_linked_account", new_callable=AsyncMock, return_value=None)
async def test_battlelog_not_linked(mock_link, admin_command_info):
    await battlelog(admin_command_info)
    admin_command_info.reply.assert_awaited_once()


@patch("commands.utility.brawlstars.battlelog.get_brawlstars_service")
async def test_battlelog_empty_log(mock_get_service, admin_command_info):
    service = MagicMock()
    service.get_battle_log = AsyncMock(return_value=[])
    mock_get_service.return_value = service
    await battlelog(admin_command_info, "#TAG")
    admin_command_info.reply.assert_awaited_once()


@patch("commands.utility.brawlstars.battlelog.get_brawlstars_linked_account", new_callable=AsyncMock, return_value=None)
@patch("commands.utility.brawlstars.battlelog.get_brawlstars_service")
async def test_battlelog_mention_not_linked(mock_svc, mock_link, admin_command_info):
    await battlelog(admin_command_info, "<@123456789>")
    admin_command_info.reply.assert_awaited_once()


@patch("commands.utility.brawlstars.battlelog.get_brawlstars_service")
async def test_battlelog_single_battle_players(mock_get_service, admin_command_info):
    battles = [
        _battle(
            players=[_player("#TAG", "Me"), _player("#ENEMY", "Enemy")],
            star_player=_player("#SP", "Star"),
        )
    ]
    service = MagicMock()
    service.get_battle_log = AsyncMock(return_value=battles)
    mock_get_service.return_value = service
    await battlelog(admin_command_info, "#TAG")
    admin_command_info.reply.assert_awaited_once()


@patch("commands.utility.brawlstars.battlelog.get_brawlstars_service")
async def test_battlelog_teams_and_pagination(mock_get_service, admin_command_info):
    team1 = [_player("#TAG", "Me"), _player("#ALLY", "Ally")]
    team2 = [_player("#E1", "E1"), _player("#E2", "E2")]
    battles = [
        _battle(teams=[team1, team2]),
        _battle(teams=[team1, team2], result="defeat"),
    ]
    service = MagicMock()
    service.get_battle_log = AsyncMock(return_value=battles)
    mock_get_service.return_value = service
    await battlelog(admin_command_info, "#TAG")
    view = admin_command_info.reply.await_args.kwargs["view"]
    interaction = make_view_interaction(admin_command_info.user)
    interaction.response.edit_message = AsyncMock()
    await view.next(interaction, MagicMock())
    interaction.response.edit_message.assert_awaited_once()

    wrong = make_view_interaction(make_target_member(user_id=99999))
    await view.previous(wrong, MagicMock())
    wrong.response.send_message.assert_awaited_once()


@patch("commands.utility.brawlstars.battlelog.get_brawlstars_linked_account", new_callable=AsyncMock, return_value="TAG")
@patch("commands.utility.brawlstars.battlelog.get_brawlstars_service")
async def test_battlelog_linked_account_adds_hash(mock_svc, mock_link, admin_command_info):
    service = MagicMock()
    service.get_battle_log = AsyncMock(return_value=[_battle(players=[_player()])])
    mock_svc.return_value = service
    await battlelog(admin_command_info)
    service.get_battle_log.assert_awaited_once_with("#TAG")
