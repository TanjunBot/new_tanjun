from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from tests.helpers.view_state import embed_from_reply

pytestmark = pytest.mark.asyncio


@patch("commands.ai.ask_gpt.AiService.get_available_tokens", new_callable=AsyncMock, return_value=0)
@patch("commands.ai.ask_gpt.AiService.initialize_user", new_callable=AsyncMock)
async def test_ask_gpt_no_tokens_embed(mock_init, mock_tokens, admin_command_info) -> None:
    from commands.ai.ask_gpt import ask_gpt

    await ask_gpt(admin_command_info, "bot", "sit", "prompt")
    embed_from_reply(admin_command_info)


@patch("commands.ai.ask_gpt.AiService.get_available_tokens", new_callable=AsyncMock, return_value=100)
async def test_ask_gpt_no_api_embed(mock_tokens, admin_command_info) -> None:
    import commands.ai.ask_gpt as ask_mod
    from commands.ai.ask_gpt import ask_gpt

    ask_mod.client = None
    await ask_gpt(admin_command_info, "bot", "sit", "prompt")
    embed_from_reply(admin_command_info)


@patch("commands.ai.show_tokens.AiService.get_token_overview", new_callable=AsyncMock)
async def test_show_tokens_embed(mock_overview, admin_command_info) -> None:
    from commands.ai.show_tokens import show_tokens

    overview = MagicMock()
    overview.free_token = 1
    overview.plus_token = 2
    overview.paid_token = 3
    mock_overview.return_value = overview
    await show_tokens(admin_command_info)
    embed_from_reply(admin_command_info)
