"""Integration tests for commands.games.connect4."""

from __future__ import annotations

import pytest

from commands.games.connect4 import connect4 as command_fn
from tests.helpers.discord import make_command_info, make_member
from tests.integration.commands.conftest import embed_from_reply


@pytest.mark.asyncio
async def test_connect4_invite():
    info = make_command_info()
    player = make_member()
    await command_fn(info, player, None)
    embed_from_reply(info.reply)
