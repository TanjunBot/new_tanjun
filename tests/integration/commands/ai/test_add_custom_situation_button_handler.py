from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from commands.ai.add_custom_situation_button_handler import approve_custom_situation, deny_custom_situation

pytestmark = pytest.mark.asyncio


def _interaction(custom_id: str, *, use_client: bool = True) -> MagicMock:
    interaction = MagicMock()
    interaction.data = {"custom_id": custom_id}
    interaction.response.send_message = AsyncMock()
    interaction.channel.send = AsyncMock()
    user = MagicMock()
    user.send = AsyncMock()
    if use_client:
        interaction.client.get_user = MagicMock(return_value=user)
    else:
        interaction.bot.get_user = MagicMock(return_value=user)
    return interaction


@pytest.mark.parametrize(
    "handler,custom_id",
    [
        (approve_custom_situation, "approve;123;en-US"),
        (deny_custom_situation, "deny;456;en-US"),
    ],
)
async def test_situation_not_found(handler, custom_id: str) -> None:
    interaction = _interaction(custom_id)
    with patch("commands.ai.add_custom_situation_button_handler.AiService.get_user_situation", new=AsyncMock(return_value=None)):
        await handler(interaction)
    interaction.response.send_message.assert_awaited_once()


@pytest.mark.parametrize(
    "handler,custom_id,use_client",
    [
        (approve_custom_situation, "approve;123;en-US", True),
        (deny_custom_situation, "deny;456;en-US", False),
    ],
)
async def test_creator_gone(handler, custom_id: str, use_client: bool) -> None:
    interaction = _interaction(custom_id, use_client=use_client)
    if use_client:
        interaction.client.get_user = MagicMock(return_value=None)
    else:
        interaction.bot.get_user = MagicMock(return_value=None)
    with patch("commands.ai.add_custom_situation_button_handler.AiService.get_user_situation", new=AsyncMock(return_value={"id": "1"})):
        await handler(interaction)
    interaction.channel.send.assert_awaited_once()


async def test_approve_success() -> None:
    interaction = _interaction("approve;123;en-US")
    with (
        patch("commands.ai.add_custom_situation_button_handler.AiService.get_user_situation", new=AsyncMock(return_value={"id": "1"})),
        patch("commands.ai.add_custom_situation_button_handler.AiService.unlock_situation", new=AsyncMock()),
    ):
        await approve_custom_situation(interaction)
    interaction.channel.send.assert_awaited_once()


async def test_deny_success() -> None:
    interaction = _interaction("deny;456;en-US", use_client=False)
    with (
        patch("commands.ai.add_custom_situation_button_handler.AiService.get_user_situation", new=AsyncMock(return_value={"id": "1"})),
        patch("commands.ai.add_custom_situation_button_handler.AiService.delete_situation", new=AsyncMock()),
    ):
        await deny_custom_situation(interaction)
    interaction.channel.send.assert_awaited_once()


async def test_approve_dm_forbidden() -> None:
    import discord as discord_mod

    interaction = _interaction("approve;123;en-US")
    interaction.client.get_user.return_value.send = AsyncMock(side_effect=discord_mod.Forbidden(MagicMock(), "forbidden"))
    with (
        patch("commands.ai.add_custom_situation_button_handler.AiService.get_user_situation", new=AsyncMock(return_value={"id": "1"})),
        patch("commands.ai.add_custom_situation_button_handler.AiService.unlock_situation", new=AsyncMock()),
    ):
        await approve_custom_situation(interaction)
    interaction.channel.send.assert_awaited_once()
