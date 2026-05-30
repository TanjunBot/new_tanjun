"""Integration tests for commands.giveaway.list_blacklist."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from commands.giveaway.list_blacklist import list_blacklist as command_fn
from tests.helpers.discord import make_command_info, make_permissions
from tests.integration.commands.conftest import embed_from_reply


@pytest.mark.asyncio
async def test_missing_permission():
    info = make_command_info(permissions=make_permissions(administrator=False))
    await command_fn(info)
    embed_from_reply(info.reply)


@pytest.mark.asyncio
@patch("commands.giveaway.list_blacklist.giveaway_service")
async def test_empty(mock_svc):
    mock_svc.get_blacklisted_roles = AsyncMock(return_value=[])
    mock_svc.get_blacklisted_users = AsyncMock(return_value=[])
    info = make_command_info(permissions=make_permissions(administrator=True))
    await command_fn(info)
    embed_from_reply(info.reply)


@pytest.mark.asyncio
@patch("commands.giveaway.list_blacklist.giveaway_service")
async def test_with_entries(mock_svc):
    mock_svc.get_blacklisted_roles = AsyncMock(return_value=[MagicMock(entity_id="1")])
    mock_svc.get_blacklisted_users = AsyncMock(return_value=[MagicMock(entity_id="2")])
    info = make_command_info(permissions=make_permissions(administrator=True))
    await command_fn(info)
    embed_from_reply(info.reply)
