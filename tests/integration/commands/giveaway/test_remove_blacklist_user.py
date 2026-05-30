"""Integration tests for commands.giveaway.remove_blacklist_user."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest

from commands.giveaway.remove_blacklist_user import remove_blacklist_user as command_fn
from tests.helpers.discord import make_command_info, make_permissions
from tests.integration.commands.conftest import embed_from_reply, make_user


@pytest.mark.asyncio
@patch("commands.giveaway.remove_blacklist_user.giveaway_service")
async def test_not_blacklisted(mock_svc):
    mock_svc.is_user_blacklisted = AsyncMock(return_value=False)
    info = make_command_info(permissions=make_permissions(administrator=True))
    await command_fn(info, make_user())
    embed_from_reply(info.reply)


@pytest.mark.asyncio
@patch("commands.giveaway.remove_blacklist_user.giveaway_service")
async def test_success(mock_svc):
    mock_svc.is_user_blacklisted = AsyncMock(return_value=True)
    mock_svc.remove_blacklisted_user = AsyncMock()
    info = make_command_info(permissions=make_permissions(administrator=True))
    await command_fn(info, make_user())
    embed_from_reply(info.reply)
    mock_svc.remove_blacklisted_user.assert_awaited_once()
