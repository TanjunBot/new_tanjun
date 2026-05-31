from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from commands.logs.blacklist_category.blacklist_category import blacklist_category as command_fn
from tests.helpers.assertions import assert_reply_embed

pytestmark = pytest.mark.asyncio


def _make_category(channel_id: int = 555555555) -> MagicMock:
    channel = MagicMock()
    channel.id = channel_id
    return channel


async def test_missing_permission(restricted_command_info):
    await command_fn(restricted_command_info, _make_category())
    assert_reply_embed(restricted_command_info)


@patch("commands.logs.blacklist_category.blacklist_category.is_log_entity_blacklisted", new_callable=AsyncMock)
@patch("commands.logs.blacklist_category.blacklist_category.add_log_blacklist", new_callable=AsyncMock)
async def test_success(mock_add, mock_is, admin_command_info):
    mock_is.return_value = False
    await command_fn(admin_command_info, _make_category())
    assert_reply_embed(admin_command_info)
    mock_add.assert_awaited_once()


@patch("commands.logs.blacklist_category.blacklist_category.is_log_entity_blacklisted", new_callable=AsyncMock)
async def test_already_blacklisted(mock_is, admin_command_info):
    mock_is.return_value = True
    await command_fn(admin_command_info, _make_category())
    assert_reply_embed(admin_command_info)
