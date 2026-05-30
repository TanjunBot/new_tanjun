"""Integration tests for commands.ai.delete_custom_situation."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from tests.integration.commands.conftest import embed_from_reply, make_role, make_user
from tests.helpers.discord import make_command_info, make_guild, make_member, make_permissions, make_text_channel


from commands.ai.delete_custom_situation import delete_custom_situation as command_fn


@pytest.mark.asyncio
@patch("commands.ai.delete_custom_situation.AiService")
async def test_delete_not_found(mock_ai):
    mock_ai.get_user_situation = AsyncMock(return_value=None)
    info = make_command_info()
    await command_fn(info)
    embed_from_reply(info.reply)


@pytest.mark.asyncio
@patch("commands.ai.delete_custom_situation.AiService")
async def test_delete_success(mock_ai):
    situation = MagicMock()
    situation.user_id = 111
    situation.name = "Test"
    mock_ai.get_user_situation = AsyncMock(return_value=situation)
    mock_ai.delete_situation = AsyncMock()
    info = make_command_info()
    await command_fn(info)
    embed_from_reply(info.reply)
    mock_ai.delete_situation.assert_awaited_once()
