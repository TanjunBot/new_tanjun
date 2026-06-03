from __future__ import annotations

import pytest

from commands.games.battleship import battleship
from commands.games.rps import rps
from commands.games.tic_tac_toe import tic_tac_toe
from tests.helpers.discord import make_member
from tests.helpers.view_state import embed_from_reply, view_from_reply
from tests.integration.commands.conftest import embed_from_reply as legacy_embed_from_reply

pytestmark = pytest.mark.asyncio


async def test_battleship_initial_view_and_embed(admin_command_info) -> None:
    player = make_member(user_id=admin_command_info.user.id, name="Player")
    await battleship(admin_command_info, player)
    embed_from_reply(admin_command_info)
    view_from_reply(admin_command_info)


async def test_rps_starts_with_reply(admin_command_info) -> None:
    opponent = make_member(user_id=222222222)
    await rps(admin_command_info, opponent)
    admin_command_info.reply.assert_awaited_once()


async def test_tic_tac_toe_initial_embed(admin_command_info) -> None:
    player = make_member()
    await tic_tac_toe(admin_command_info, player, None)
    legacy_embed_from_reply(admin_command_info.reply)
