"""Integration tests for commands.ai.add_custom_situation."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from tests.integration.commands.conftest import embed_from_reply, make_role, make_user
from tests.helpers.discord import make_command_info, make_guild, make_member, make_permissions, make_text_channel


from commands.ai.add_custom_situation import add_custom_situation as command_fn


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
