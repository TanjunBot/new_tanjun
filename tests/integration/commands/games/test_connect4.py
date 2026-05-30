"""Integration tests for commands.games.connect4."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from tests.integration.commands.conftest import embed_from_reply, make_role, make_user
from tests.helpers.discord import make_command_info, make_guild, make_member, make_permissions, make_text_channel


from commands.games.connect4 import connect4 as command_fn


@pytest.mark.asyncio
async def test_connect4_invite():
    info = make_command_info()
    player = make_member()
    await command_fn(info, player, None)
    embed_from_reply(info.reply)
