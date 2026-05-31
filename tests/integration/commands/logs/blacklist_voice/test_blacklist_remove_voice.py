from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from commands.logs.blacklist_voice.blacklist_remove_voice import blacklist_remove_voice
from tests.helpers.assertions import assert_reply_embed

pytestmark = pytest.mark.asyncio


def _make_voice_channel() -> MagicMock:
    channel = MagicMock()
    channel.id = 666666666
    return channel


async def test_missing_permission(restricted_command_info):
    await blacklist_remove_voice(restricted_command_info, _make_voice_channel())
    assert_reply_embed(restricted_command_info)


@patch(
    "commands.logs.blacklist_voice.blacklist_remove_voice.is_log_entity_blacklisted",
    new_callable=AsyncMock,
    return_value=False,
)
async def test_not_blacklisted(mock_is, admin_command_info):
    await blacklist_remove_voice(admin_command_info, _make_voice_channel())
    assert_reply_embed(admin_command_info)


@patch("commands.logs.blacklist_voice.blacklist_remove_voice.remove_log_blacklist", new_callable=AsyncMock)
@patch(
    "commands.logs.blacklist_voice.blacklist_remove_voice.is_log_entity_blacklisted",
    new_callable=AsyncMock,
    return_value=True,
)
async def test_success(mock_is, mock_remove, admin_command_info):
    await blacklist_remove_voice(admin_command_info, _make_voice_channel())
    assert_reply_embed(admin_command_info)
    mock_remove.assert_awaited_once()
