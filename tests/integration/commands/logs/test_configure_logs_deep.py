from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from commands.logs.configure_logs import configure_logs
from tests.integration.commands.admin.conftest import make_view_interaction

pytestmark = pytest.mark.asyncio


def _log_enabled(enabled=False):
    le = MagicMock()
    le.get_option = MagicMock(return_value=enabled)
    le.set_option = MagicMock()
    return le


async def test_configure_logs_no_permission(restricted_command_info):
    await configure_logs(restricted_command_info)
    restricted_command_info.reply.assert_awaited_once()


@patch("commands.logs.configure_logs.set_log_enable_api", new_callable=AsyncMock)
@patch("commands.logs.configure_logs.get_log_enable_api", new_callable=AsyncMock)
async def test_configure_logs_view_buttons(mock_get, mock_set, admin_command_info):
    mock_get.return_value = _log_enabled(False)
    await configure_logs(admin_command_info)
    view = admin_command_info.reply.await_args.kwargs["view"]
    view.message = MagicMock(edit=AsyncMock())
    view.children = [
        MagicMock(disabled=False),
        MagicMock(),
        MagicMock(),
        MagicMock(disabled=False),
    ]

    interaction = make_view_interaction(admin_command_info.user)
    interaction.response.edit_message = AsyncMock()
    await view.activate(interaction, MagicMock())
    mock_set.assert_awaited()

    interaction2 = make_view_interaction(admin_command_info.user)
    interaction2.response.edit_message = AsyncMock()
    await view.up(interaction2, MagicMock())
    interaction2.response.edit_message.assert_awaited_once()

    interaction3 = make_view_interaction(admin_command_info.user)
    interaction3.response.edit_message = AsyncMock()
    await view.down(interaction3, MagicMock())

    mock_get.return_value = _log_enabled(True)
    interaction4 = make_view_interaction(admin_command_info.user)
    interaction4.response.edit_message = AsyncMock()
    await view.deactivate(interaction4, MagicMock())

    await view.on_timeout()
    view.message.edit.assert_awaited_once()
