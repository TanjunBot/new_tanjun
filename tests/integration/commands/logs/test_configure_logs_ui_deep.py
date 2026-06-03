from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from commands.logs.configure_logs import LOG_OPTIONS, configure_logs
from tests.helpers.view_state import (
    assert_selection_marker,
    count_selection_markers,
    embed_from_reply,
    reply_description,
    view_from_reply,
)
from tests.integration.commands.admin.conftest import make_view_interaction

pytestmark = pytest.mark.asyncio


def _log_enabled(enabled: bool = False):
    le = MagicMock()
    le.get_option = MagicMock(return_value=enabled)
    le.set_option = MagicMock()
    return le


@patch("commands.logs.configure_logs.set_log_enable_api", new_callable=AsyncMock)
@patch("commands.logs.configure_logs.get_log_enable_api", new_callable=AsyncMock)
async def test_configure_logs_initial_embed_first_option_selected(mock_get, mock_set, admin_command_info):
    mock_get.return_value = _log_enabled(False)
    await configure_logs(admin_command_info)
    desc = reply_description(admin_command_info)
    assert_selection_marker(desc)
    assert count_selection_markers(desc) == 1
    view = view_from_reply(admin_command_info)
    assert view.selected_index == 0


@patch("commands.logs.configure_logs.set_log_enable_api", new_callable=AsyncMock)
@patch("commands.logs.configure_logs.get_log_enable_api", new_callable=AsyncMock)
async def test_configure_logs_up_wraps_to_last(mock_get, mock_set, admin_command_info):
    mock_get.return_value = _log_enabled(False)
    await configure_logs(admin_command_info)
    view = view_from_reply(admin_command_info)
    view.children = [MagicMock(disabled=False), MagicMock(), MagicMock(), MagicMock(disabled=False)]
    interaction = make_view_interaction(admin_command_info.user)
    interaction.response.edit_message = AsyncMock()
    await view.up(interaction, MagicMock())
    assert view.selected_index == len(LOG_OPTIONS) - 1
    interaction.response.edit_message.assert_awaited_once()


@patch("commands.logs.configure_logs.set_log_enable_api", new_callable=AsyncMock)
@patch("commands.logs.configure_logs.get_log_enable_api", new_callable=AsyncMock)
async def test_configure_logs_down_wraps_to_first(mock_get, mock_set, admin_command_info):
    mock_get.return_value = _log_enabled(False)
    await configure_logs(admin_command_info)
    view = view_from_reply(admin_command_info)
    view.selected_index = len(LOG_OPTIONS) - 1
    view.children = [MagicMock(disabled=False), MagicMock(), MagicMock(), MagicMock(disabled=False)]
    interaction = make_view_interaction(admin_command_info.user)
    interaction.response.edit_message = AsyncMock()
    await view.down(interaction, MagicMock())
    assert view.selected_index == 0


@patch("commands.logs.configure_logs.set_log_enable_api", new_callable=AsyncMock)
@patch("commands.logs.configure_logs.get_log_enable_api", new_callable=AsyncMock)
async def test_configure_logs_activate_calls_api_for_selected_index(mock_get, mock_set, admin_command_info):
    mock_get.return_value = _log_enabled(False)
    await configure_logs(admin_command_info)
    view = view_from_reply(admin_command_info)
    view.message = MagicMock(edit=AsyncMock())
    view.children = [MagicMock(disabled=False), MagicMock(), MagicMock(), MagicMock(disabled=False)]
    interaction = make_view_interaction(admin_command_info.user)
    interaction.response.edit_message = AsyncMock()
    await view.activate(interaction, MagicMock())
    mock_set.assert_awaited_with(admin_command_info.guild.id, **{LOG_OPTIONS[0]: True})


@patch("commands.logs.configure_logs.set_log_enable_api", new_callable=AsyncMock)
@patch("commands.logs.configure_logs.get_log_enable_api", new_callable=AsyncMock)
async def test_configure_logs_deactivate_calls_api(mock_get, mock_set, admin_command_info):
    mock_get.return_value = _log_enabled(True)
    await configure_logs(admin_command_info)
    view = view_from_reply(admin_command_info)
    view.message = MagicMock(edit=AsyncMock())
    view.children = [MagicMock(disabled=True), MagicMock(), MagicMock(), MagicMock(disabled=False)]
    interaction = make_view_interaction(admin_command_info.user)
    interaction.response.edit_message = AsyncMock()
    await view.deactivate(interaction, MagicMock())
    mock_set.assert_awaited_with(admin_command_info.guild.id, **{LOG_OPTIONS[0]: False})


@patch("commands.logs.configure_logs.set_log_enable_api", new_callable=AsyncMock)
@patch("commands.logs.configure_logs.get_log_enable_api", new_callable=AsyncMock)
async def test_configure_logs_reply_has_view_and_embed(mock_get, mock_set, admin_command_info):
    mock_get.return_value = _log_enabled(False)
    await configure_logs(admin_command_info)
    embed = embed_from_reply(admin_command_info)
    assert embed.title is not None
    view = view_from_reply(admin_command_info)
    assert view is not None
