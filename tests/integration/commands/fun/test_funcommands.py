from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest

from commands.fun.funcommands import fun_command as command_fn
from tests.helpers.assertions import assert_reply_embed
from tests.helpers.discord import make_member

pytestmark = pytest.mark.asyncio

FUN_ACTIONS = ["hug", "kiss", "boop", "wave", "slap", "laugh", "tickle", "pat", "poke"]


@pytest.mark.parametrize("action", FUN_ACTIONS)
@patch("commands.fun.funcommands.utility.getGif", new_callable=AsyncMock)
async def test_fun_action_with_gif(mock_gif, action, admin_command_info):
    mock_gif.return_value = ["https://example.com/gif.gif"]
    target = make_member(user_id=222222222, name="Target")
    await command_fn(admin_command_info, action, target, None)
    assert_reply_embed(admin_command_info)


@pytest.mark.parametrize("action", FUN_ACTIONS)
@patch("commands.fun.funcommands.utility.getGif", new_callable=AsyncMock)
async def test_fun_action_no_gif(mock_gif, action, admin_command_info):
    mock_gif.return_value = []
    target = make_member(user_id=222222222, name="Target")
    await command_fn(admin_command_info, action, target, None)
    assert_reply_embed(admin_command_info)


@pytest.mark.parametrize("action", FUN_ACTIONS)
@patch("commands.fun.funcommands.utility.getGif", new_callable=AsyncMock)
async def test_fun_action_with_message(mock_gif, action, admin_command_info):
    mock_gif.return_value = ["https://example.com/g.gif"]
    target = make_member()
    await command_fn(admin_command_info, action, target, "hello")
    assert_reply_embed(admin_command_info)
