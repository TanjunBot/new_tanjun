"""Integration tests for commands.giveaway.edit_giveaway."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from commands.giveaway.edit_giveaway import edit_giveaway as command_fn
from tests.helpers.discord import make_command_info, make_guild, make_permissions, make_text_channel


@pytest.mark.asyncio
async def test_missing_permission():
    guild = make_guild()
    channel = make_text_channel(guild=guild)
    channel.permissions_for = MagicMock(return_value=make_permissions(manage_guild=False))
    info = make_command_info(guild=guild, channel=channel)
    await command_fn(info, 1)
    info.reply.assert_awaited()


@pytest.mark.asyncio
@patch("commands.giveaway.edit_giveaway.GiveawayEditor")
async def test_not_found(mock_editor_cls):
    editor = MagicMock()
    editor.load_giveaway_data = AsyncMock(return_value=False)
    mock_editor_cls.return_value = editor
    guild = make_guild()
    channel = make_text_channel(guild=guild)
    channel.permissions_for = MagicMock(return_value=make_permissions(manage_guild=True))
    info = make_command_info(guild=guild, channel=channel)
    await command_fn(info, 1)
    info.reply.assert_awaited()
