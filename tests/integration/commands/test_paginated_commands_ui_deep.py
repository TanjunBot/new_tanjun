from __future__ import annotations

from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from commands.math.calculator import CalculatorView
from commands.utility.listscheduled import list_scheduled_messages
from models import ScheduledMessageModel
from services.brawlstars import BattleBrawler, BattlePlayer, BrawlStarsBattle
from tests.helpers.discord import make_target_member
from tests.helpers.factories import CHANNEL_ID, GUILD_ID, USER_ID
from tests.helpers.view_state import embed_from_reply, reply_description, view_from_reply
from tests.integration.commands.admin.conftest import make_view_interaction

pytestmark = pytest.mark.asyncio


def _scheduled_msg(msg_id: int = 1, content: str = "hello") -> ScheduledMessageModel:
    dt = datetime.now(UTC) + timedelta(hours=1)
    return ScheduledMessageModel.from_row(
        (msg_id, GUILD_ID, CHANNEL_ID, USER_ID, content, dt, None, None, None, None, dt)
    )


async def test_calculator_page_zero_has_number_buttons(admin_command_info) -> None:
    view = CalculatorView(admin_command_info)
    assert view.current_page == 0
    custom_ids = [getattr(c, "custom_id", None) for c in view.children]
    assert "7" in custom_ids
    assert "add" in custom_ids or "+" in str(custom_ids)


async def test_calculator_wrong_user_rejected(admin_command_info) -> None:
    view = CalculatorView(admin_command_info)
    wrong = make_view_interaction(make_target_member(user_id=99999))
    result = await view.interaction_check(wrong)
    assert result is False
    wrong.response.send_message.assert_awaited_once()


@patch("commands.utility.listscheduled.ScheduledMessageService.get_user_messages", new_callable=AsyncMock)
async def test_listscheduled_first_page_shows_first_message(mock_get, admin_command_info) -> None:
    mock_get.return_value = [_scheduled_msg(1, "first-msg"), _scheduled_msg(2, "second-msg")]
    admin_command_info.reply = AsyncMock(return_value=MagicMock(edit=AsyncMock()))
    await list_scheduled_messages(admin_command_info)
    embed = embed_from_reply(admin_command_info)
    field_text = " ".join(
        (getattr(f, "value", "") or "") + (getattr(f, "name", "") or "") for f in getattr(embed, "fields", [])
    )
    assert "first-msg" in field_text or "1" in field_text
    view = view_from_reply(admin_command_info)
    assert view.page == 0


@patch("commands.level.leaderboard.get_level_leaderboard_count", new_callable=AsyncMock, return_value=1)
@patch("commands.level.leaderboard.get_xp_scaling", new_callable=AsyncMock, return_value="medium")
@patch("commands.level.leaderboard.get_custom_formula", new_callable=AsyncMock, return_value=None)
@patch("commands.level.leaderboard.get_level_leaderboard_paginated", new_callable=AsyncMock)
@patch("commands.level.leaderboard.get_level_for_xp_async", new_callable=AsyncMock, return_value=1)
@patch("commands.level.leaderboard.get_xp_for_level_async", new_callable=AsyncMock, return_value=100)
async def test_leaderboard_initial_reply_has_embed(
    mock_xp_level,
    mock_level,
    mock_page,
    mock_formula,
    mock_scaling,
    mock_count,
    admin_command_info,
) -> None:
    from commands.level.leaderboard import leaderboard

    entry = MagicMock()
    entry.user_id = "111111111"
    entry.xp = 500
    mock_page.return_value = [entry]
    await leaderboard(admin_command_info)
    embed = embed_from_reply(admin_command_info)
    assert embed.title is not None
    view_from_reply(admin_command_info)


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


@patch("commands.utility.brawlstars.battlelog.get_brawlstars_service")
async def test_battlelog_first_page_before_next(mock_get_service, admin_command_info) -> None:
    from commands.utility.brawlstars.battlelog import battlelog

    team1 = [_player("#TAG", "Me"), _player("#ALLY", "Ally")]
    team2 = [_player("#E1", "E1"), _player("#E2", "E2")]
    battles = [_battle(teams=[team1, team2]), _battle(teams=[team1, team2])]
    service = MagicMock()
    service.get_battle_log = AsyncMock(return_value=battles)
    mock_get_service.return_value = service
    await battlelog(admin_command_info, "#TAG")
    desc = reply_description(admin_command_info)
    assert desc
    view = view_from_reply(admin_command_info)
    assert view.current_page == 0
