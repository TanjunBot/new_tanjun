"""Integration tests for commands.minigames.wordchain.setwordchainchannel."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from commands.minigames.wordchain.setwordchainchannel import setwordchainchannel as command_fn
from tests.helpers.discord import make_command_info, make_guild, make_permissions, make_text_channel
from tests.integration.commands.conftest import embed_from_reply


@pytest.mark.asyncio
async def test_missing_permission():
    guild = make_guild()
    channel = make_text_channel(guild=guild)
    channel.permissions_for = MagicMock(return_value=make_permissions(moderate_members=False))
    info = make_command_info(guild=guild, channel=channel)
    await command_fn(info, make_text_channel(guild=guild))
    embed_from_reply(info.reply)
