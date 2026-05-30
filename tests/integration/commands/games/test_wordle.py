"""Integration tests for commands.games.wordle."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from tests.integration.commands.conftest import embed_from_reply, make_role, make_user
from tests.helpers.discord import make_command_info, make_guild, make_member, make_permissions, make_text_channel


from commands.games.wordle import wordle as command_fn


@pytest.mark.asyncio
async def test_wordle_start():
    info = make_command_info()
    await command_fn(info)
    embed_from_reply(info.reply)
