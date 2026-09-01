from __future__ import annotations

import pytest

from commands.games.battleship import battleship
from tests.helpers.assertions import assert_reply_embed
from tests.helpers.discord import make_member

pytestmark = pytest.mark.asyncio


async def test_battleship_vs_bot(admin_command_info):
    player = make_member(user_id=admin_command_info.user.id, name="Player")
    await battleship(admin_command_info, player)
    admin_command_info.reply.assert_awaited_once()
    assert admin_command_info.reply.await_args.kwargs.get("embed") is not None
    assert admin_command_info.reply.await_args.kwargs.get("view") is not None


async def test_battleship_two_players(admin_command_info):
    player1 = make_member(user_id=admin_command_info.user.id, name="Player1")
    player2 = make_member(user_id=222222222, name="Player2")
    await battleship(admin_command_info, player1, player2)
    assert_reply_embed(admin_command_info)
    assert admin_command_info.reply.await_args.kwargs.get("view") is not None
