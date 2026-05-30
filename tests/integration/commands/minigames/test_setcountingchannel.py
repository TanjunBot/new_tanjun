"""Integration tests for commands.minigames.counting.setcountingchannel."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest

from commands.minigames.counting.setcountingchannel import setCountingChannel as command_fn
from tests.helpers.discord import make_command_info, make_guild, make_text_channel
from tests.integration.commands.conftest import embed_from_reply


@pytest.mark.asyncio
@patch("commands.minigames.counting.setcountingchannel._repo")
@patch("commands.minigames.counting.setcountingchannel.require_bot_permissions", new_callable=AsyncMock)
@patch("commands.minigames.counting.setcountingchannel.require_moderate_members", new_callable=AsyncMock)
async def test_success(mock_mod, mock_bot, mock_repo):
    mock_mod.return_value = False
    mock_bot.return_value = False
    mock_repo.set_progress = AsyncMock()
    guild = make_guild()
    channel = make_text_channel(guild=guild)
    channel.send = AsyncMock()
    info = make_command_info(guild=guild, channel=channel)
    await command_fn(info, channel)
    embed_from_reply(info.reply)
    channel.send.assert_awaited()
