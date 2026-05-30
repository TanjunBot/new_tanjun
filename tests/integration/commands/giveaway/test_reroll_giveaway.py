"""Integration tests for commands.giveaway.reroll_giveaway."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest

from commands.giveaway.reroll_giveaway import reroll_giveaway as command_fn
from tests.helpers.discord import make_command_info, make_permissions
from tests.integration.commands.conftest import embed_from_reply


@pytest.mark.asyncio
async def test_missing_permission():
    info = make_command_info(permissions=make_permissions(manage_guild=False))
    await command_fn(info, 1)
    embed_from_reply(info.reply)


@pytest.mark.asyncio
@patch("commands.giveaway.reroll_giveaway.giveaway_service")
async def test_not_found(mock_svc):
    mock_svc.get = AsyncMock(return_value=None)
    info = make_command_info(permissions=make_permissions(manage_guild=True))
    await command_fn(info, 1)
    embed_from_reply(info.reply)
