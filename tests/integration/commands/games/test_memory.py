from __future__ import annotations

import pytest

from commands.games.memory import memory
from tests.helpers.assertions import assert_reply_embed
from tests.helpers.discord import make_member

pytestmark = pytest.mark.asyncio


async def test_memory_starts_game(admin_command_info):
    player = make_member(user_id=admin_command_info.user.id, name="Player")
    await memory(admin_command_info, player)
    admin_command_info.reply.assert_awaited_once()
    assert admin_command_info.reply.await_args.kwargs.get("embed") is not None
    assert admin_command_info.reply.await_args.kwargs.get("view") is not None


async def test_memory_embed_content(admin_command_info):
    player = make_member(user_id=admin_command_info.user.id, name="Player")
    await memory(admin_command_info, player)
    assert_reply_embed(admin_command_info)
