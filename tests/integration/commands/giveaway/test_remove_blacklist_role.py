"""Integration tests for commands.giveaway.remove_blacklist_role."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from tests.integration.commands.conftest import embed_from_reply, make_role, make_user
from tests.helpers.discord import make_command_info, make_guild, make_member, make_permissions, make_text_channel


from commands.giveaway.remove_blacklist_role import remove_blacklist_role as command_fn


@pytest.mark.asyncio
async def test_missing_permission():
    info = make_command_info(permissions=make_permissions(administrator=False))
    await command_fn(info, make_role())
    embed_from_reply(info.reply)


@pytest.mark.asyncio
@patch("commands.giveaway.remove_blacklist_role.giveaway_service")
async def test_not_blacklisted(mock_svc):
    mock_svc.get_blacklisted_roles = AsyncMock(return_value=[])
    info = make_command_info(permissions=make_permissions(administrator=True))
    await command_fn(info, make_role())
    embed_from_reply(info.reply)


@pytest.mark.asyncio
@patch("commands.giveaway.remove_blacklist_role.giveaway_service")
async def test_success(mock_svc):
    mock_svc.get_blacklisted_roles = AsyncMock(return_value=[MagicMock(entity_id="222222222")])
    mock_svc.remove_blacklisted_role = AsyncMock()
    info = make_command_info(permissions=make_permissions(administrator=True))
    role = make_role()
    await command_fn(info, role)
    embed_from_reply(info.reply)
    mock_svc.remove_blacklisted_role.assert_awaited_once()
