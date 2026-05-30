"""Integration tests for commands.games.flag_quiz."""

from __future__ import annotations

import pytest

from commands.games.flag_quiz import flag_quiz as command_fn
from tests.helpers.discord import make_command_info
from tests.integration.commands.conftest import embed_from_reply


@pytest.mark.asyncio
async def test_flag_quiz_start():
    info = make_command_info()
    await command_fn(info)
    embed_from_reply(info.reply)
