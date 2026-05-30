"""Integration tests for commands.ai.add_custom_situation."""

from __future__ import annotations

import pytest

from commands.ai.add_custom_situation import add_custom_situation as command_fn
from tests.helpers.discord import make_command_info
from tests.integration.commands.conftest import embed_from_reply


@pytest.mark.asyncio
async def test_short_situation():
    info = make_command_info()
    await command_fn(info, "ab", "short", 1.0, 1.0, 0.0, 0.0)
    embed_from_reply(info.reply)


@pytest.mark.asyncio
async def test_short_name():
    info = make_command_info()
    await command_fn(info, "ab", "long enough situation text", 1.0, 1.0, 0.0, 0.0)
    embed_from_reply(info.reply)
