"""Integration tests for commands.games.tic_tac_toe."""

from __future__ import annotations

import pytest

from commands.games.tic_tac_toe import tic_tac_toe as command_fn
from tests.helpers.discord import make_command_info, make_member
from tests.integration.commands.conftest import embed_from_reply


@pytest.mark.asyncio
async def test_ttt_start():
    info = make_command_info()
    player = make_member()
    await command_fn(info, player, None)
    embed_from_reply(info.reply)
