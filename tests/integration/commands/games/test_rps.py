"""Integration tests for commands.games.rps."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from tests.integration.commands.conftest import embed_from_reply, make_role, make_user
from tests.helpers.discord import make_command_info, make_guild, make_member, make_permissions, make_text_channel


from commands.games.rps import rps as command_fn


@pytest.mark.asyncio
async def test_rps_vs_bot():
    info = make_command_info()
    await command_fn(info, None)
    embed_from_reply(info.reply)
    assert info.reply.await_args.kwargs.get("view") is not None


@pytest.mark.asyncio
async def test_rps_vs_member():
    info = make_command_info()
    opponent = make_member(user_id=222)
    opponent.bot = False
    await command_fn(info, opponent)
    embed_from_reply(info.reply)
