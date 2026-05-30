"""Integration tests for commands.giveaway.add_blacklist_role."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from commands.giveaway.add_blacklist_role import add_blacklist_role as command_fn
from tests.helpers.discord import make_command_info, make_permissions
from tests.integration.commands.conftest import embed_from_reply, make_role


@pytest.mark.asyncio
async def test_missing_permission():
    info = make_command_info(permissions=make_permissions(administrator=False))
    await command_fn(info, make_role())
    embed_from_reply(info.reply)


@pytest.mark.asyncio
@patch("commands.giveaway.add_blacklist_role.giveaway_service")
async def test_success_add(mock_svc):
    mock_svc.get_blacklisted_roles = AsyncMock(return_value=[])
    mock_svc.add_blacklisted_role = AsyncMock()
    info = make_command_info(permissions=make_permissions(administrator=True))
    await command_fn(info, make_role())
    embed_from_reply(info.reply)
    mock_svc.add_blacklisted_role.assert_awaited_once()


@pytest.mark.asyncio
@patch("commands.giveaway.add_blacklist_role.giveaway_service")
async def test_already_exists(mock_svc):
    entity = MagicMock(entity_id="222222222")
    mock_svc.get_blacklisted_roles = AsyncMock(return_value=[entity])
    mock_svc.get_blacklisted_users = AsyncMock(return_value=[entity])
    mock_svc.is_user_blacklisted = AsyncMock(return_value=True)
    info = make_command_info(permissions=make_permissions(administrator=True))
    await command_fn(info, make_role())
    embed_from_reply(info.reply)


@pytest.mark.asyncio
@patch("commands.giveaway.add_blacklist_role.giveaway_service")
async def test_success(mock_svc):
    mock_svc.get_blacklisted_roles = AsyncMock(return_value=[])
    mock_svc.get_blacklisted_users = AsyncMock(return_value=[])
    mock_svc.is_user_blacklisted = AsyncMock(return_value=False)
    mock_svc.add_blacklisted_role = AsyncMock()
    mock_svc.add_blacklisted_user = AsyncMock()
    mock_svc.remove_blacklisted_role = AsyncMock()
    mock_svc.remove_blacklisted_user = AsyncMock()
    info = make_command_info(permissions=make_permissions(administrator=True))
    await command_fn(info, make_role())
    embed_from_reply(info.reply)
