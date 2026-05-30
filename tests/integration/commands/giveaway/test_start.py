"""Integration tests for commands.giveaway.start."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from commands.giveaway.start import start_giveaway as command_fn
from tests.helpers.discord import make_command_info, make_member, make_permissions, make_text_channel


@pytest.mark.asyncio
async def test_missing_permission():
    user = make_member()
    user.guild_permissions = make_permissions(manage_guild=False)
    info = make_command_info(user=user)
    await command_fn(info, "Prize", make_text_channel())
    info.reply.assert_awaited()


@pytest.mark.asyncio
@patch("commands.giveaway.start.GiveawayBuilder")
async def test_starts_builder(mock_builder_cls):
    user = make_member()
    user.guild_permissions = make_permissions(manage_guild=True)
    info = make_command_info(user=user)
    view = MagicMock()
    view.update_embed = AsyncMock()
    mock_builder_cls.return_value = view
    info.reply = AsyncMock(return_value=MagicMock())
    await command_fn(info, "Prize", make_text_channel())
    info.reply.assert_awaited()
    mock_builder_cls.assert_called_once()
