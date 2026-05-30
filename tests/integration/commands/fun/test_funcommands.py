"""Integration tests for commands.fun.funcommands."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from tests.integration.commands.conftest import embed_from_reply, make_role, make_user
from tests.helpers.discord import make_command_info, make_guild, make_member, make_permissions, make_text_channel


from commands.fun.funcommands import fun_command as command_fn


@pytest.mark.asyncio
@patch("commands.fun.funcommands.utility.getGif", new_callable=AsyncMock)
async def test_fun_poke(mock_gif):
    mock_gif.return_value = ["https://example.com/gif.gif"]
    info = make_command_info()
    target = make_member(user_id=222, name="Target")
    await command_fn(info, "poke", target, None)
    embed_from_reply(info.reply)


@pytest.mark.asyncio
@patch("commands.fun.funcommands.utility.getGif", new_callable=AsyncMock)
async def test_fun_wave_no_gif(mock_gif):
    mock_gif.return_value = []
    info = make_command_info()
    target = make_member(user_id=222, name="Target")
    await command_fn(info, "wave", target, "hello")
    embed_from_reply(info.reply)


@pytest.mark.asyncio
@patch("commands.fun.funcommands.utility.getGif", new_callable=AsyncMock)
async def test_fun_with_message(mock_gif):
    mock_gif.return_value = ["https://example.com/g.gif"]
    info = make_command_info()
    target = make_member()
    await command_fn(info, "hug", target, "thanks")
    embed_from_reply(info.reply)
