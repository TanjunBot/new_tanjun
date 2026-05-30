"""Integration tests for commands.ai.ask_gpt."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from tests.integration.commands.conftest import embed_from_reply, make_role, make_user
from tests.helpers.discord import make_command_info, make_guild, make_member, make_permissions, make_text_channel


from commands.ai.ask_gpt import ask_gpt as command_fn


@pytest.mark.asyncio
@patch("commands.ai.ask_gpt.AiService")
async def test_no_tokens(mock_ai):
    mock_ai.get_available_tokens = AsyncMock(return_value=0)
    mock_ai.initialize_user = AsyncMock()
    mock_ai.get_available_tokens.side_effect = [0, 0]
    info = make_command_info()
    await command_fn(info, "bot", "situation", "prompt")
    embed_from_reply(info.reply)
