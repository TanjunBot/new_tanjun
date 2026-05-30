"""Integration tests for commands.giveaway.end_giveaway."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from tests.integration.commands.conftest import embed_from_reply, make_role, make_user
from tests.helpers.discord import make_command_info, make_guild, make_member, make_permissions, make_text_channel


from commands.giveaway.end_giveaway import end_giveaway as command_fn


def _giveaway(**kw):
    g = MagicMock()
    g.guild_id = kw.get("guild_id", "123456789")
    g.ended = kw.get("ended", False)
    return g


@pytest.mark.asyncio
async def test_missing_permission():
    info = make_command_info(permissions=make_permissions(manage_guild=False))
    await command_fn(info, 1)
    embed_from_reply(info.reply)


@pytest.mark.asyncio
@patch("commands.giveaway.end_giveaway.giveaway_service")
async def test_not_found(mock_svc):
    mock_svc.get = AsyncMock(return_value=None)
    info = make_command_info(permissions=make_permissions(manage_guild=True))
    await command_fn(info, 99)
    embed_from_reply(info.reply)


@pytest.mark.asyncio
@patch("commands.giveaway.end_giveaway.endGiveaway", new_callable=AsyncMock)
@patch("commands.giveaway.end_giveaway.giveaway_service")
async def test_success(mock_svc, mock_end):
    mock_svc.get = AsyncMock(return_value=_giveaway())
    info = make_command_info(permissions=make_permissions(manage_guild=True))
    await command_fn(info, 1)
    embed_from_reply(info.reply)
    mock_end.assert_awaited_once()
