"""Integration tests for commands.utility.help."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from commands.utility.help import help as command_fn
from tests.helpers.discord import make_command_info
from tests.integration.commands.conftest import embed_from_reply


class _StubView:
    def __init__(self, *args, **kwargs) -> None:
        pass

    def add_item(self, item) -> None:
        pass


class _StubSelect(_StubView):
    pass


@pytest.fixture(autouse=True)
def stub_discord_ui():
    import discord

    old_view, old_select = discord.ui.View, discord.ui.Select
    discord.ui.View = _StubView
    discord.ui.Select = _StubSelect
    yield
    discord.ui.View = old_view
    discord.ui.Select = old_select


@pytest.mark.asyncio
async def test_help_default():
    info = make_command_info()
    info.client.tree = MagicMock()
    info.client.tree.walk_commands = MagicMock(return_value=[])
    ctx = MagicMock()
    await command_fn(info, ctx)
    embed_from_reply(info.reply)
    assert info.reply.await_args.kwargs.get("view") is not None


@pytest.mark.asyncio
async def test_help_with_tree():
    info = make_command_info()
    parent = MagicMock()
    parent.qualified_name = "games"
    parent.name = "games"
    parent.description = "games_desc"
    info.client.tree = MagicMock()
    info.client.tree.walk_commands = MagicMock(return_value=[MagicMock(parent=parent)])
    ctx = MagicMock()
    await command_fn(info, ctx)
    embed_from_reply(info.reply)
