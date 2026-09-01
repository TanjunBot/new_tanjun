from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from commands.logs.blacklist_voice.blacklist_list_voice import blacklist_list_voice
from tests.helpers.assertions import assert_reply_embed

pytestmark = pytest.mark.asyncio


@patch("commands.logs.blacklist_voice.blacklist_list_voice.get_log_blacklist", new_callable=AsyncMock)
async def test_missing_permission(mock_get, restricted_command_info):
    await blacklist_list_voice(restricted_command_info)
    assert_reply_embed(restricted_command_info)
    mock_get.assert_not_called()


@patch("commands.logs.blacklist_voice.blacklist_list_voice.get_log_blacklist", new_callable=AsyncMock)
async def test_empty(mock_get, admin_command_info):
    mock_get.return_value = []
    await blacklist_list_voice(admin_command_info)
    assert_reply_embed(admin_command_info)
    assert admin_command_info.reply.await_args.kwargs.get("view") is not None


@patch("commands.logs.blacklist_voice.blacklist_list_voice.get_log_blacklist", new_callable=AsyncMock)
async def test_with_entries(mock_get, admin_command_info):
    mock_get.return_value = ["777777777", "888888888"]
    await blacklist_list_voice(admin_command_info)
    assert_reply_embed(admin_command_info)


@patch("commands.logs.blacklist_voice.blacklist_list_voice.remove_log_blacklist", new_callable=AsyncMock)
@patch("commands.logs.blacklist_voice.blacklist_list_voice.get_log_blacklist", new_callable=AsyncMock)
async def test_remove_button(mock_get, mock_remove, admin_command_info):
    mock_get.return_value = ["777777777"]
    await blacklist_list_voice(admin_command_info)
    view = admin_command_info.reply.await_args.kwargs["view"]
    interaction = MagicMock()
    interaction.response.edit_message = AsyncMock()
    await view.remove_channel(interaction, MagicMock())
    mock_remove.assert_awaited_once()


@patch("commands.logs.blacklist_voice.blacklist_list_voice.add_log_blacklist", new_callable=AsyncMock)
@patch("commands.logs.blacklist_voice.blacklist_list_voice.get_log_blacklist", new_callable=AsyncMock)
async def test_add_via_select(mock_get, mock_add, admin_command_info):
    mock_get.return_value = []
    await blacklist_list_voice(admin_command_info)
    view = admin_command_info.reply.await_args.kwargs["view"]
    interaction = MagicMock()
    interaction.data = {"component_type": 8, "values": ["999999999"]}
    interaction.response.edit_message = AsyncMock()
    await view.interaction_check(interaction)
    mock_add.assert_awaited_once()
