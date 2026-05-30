from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from commands.level.disable_level_system import disable_level_system
from tests.integration.commands.admin.conftest import make_view_interaction


pytestmark = pytest.mark.asyncio


async def _reply_with_auto_wait(admin_command_info, confirm: bool | None):
    msg = MagicMock()
    msg.edit = AsyncMock()
    msg.delete = AsyncMock()

    async def reply(**kwargs):
        view = kwargs.get("view")
        if view is not None:

            async def fast_wait():
                view.value = confirm

            view.wait = fast_wait
        return msg

    admin_command_info.reply = AsyncMock(side_effect=reply)
    return msg


async def test_disable_level_system_no_permission(restricted_command_info):
    await disable_level_system(restricted_command_info)
    restricted_command_info.reply.assert_awaited_once()


@patch("commands.level.disable_level_system.get_level_system_status", new_callable=AsyncMock, return_value=False)
async def test_disable_level_system_already_disabled(mock_status, admin_command_info):
    await disable_level_system(admin_command_info)
    admin_command_info.reply.assert_awaited_once()


@patch("commands.level.disable_level_system.set_level_system_status", new_callable=AsyncMock)
@patch("commands.level.disable_level_system.delete_level_system_data", new_callable=AsyncMock)
@patch("commands.level.disable_level_system.get_level_system_status", new_callable=AsyncMock, return_value=True)
async def test_disable_level_system_confirm(mock_status, mock_delete, mock_set, admin_command_info):
    msg = await _reply_with_auto_wait(admin_command_info, True)
    await disable_level_system(admin_command_info)
    mock_delete.assert_awaited_once()
    mock_set.assert_awaited_once()
    msg.edit.assert_awaited_once()


@patch("commands.level.disable_level_system.get_level_system_status", new_callable=AsyncMock, return_value=True)
async def test_disable_level_system_cancel(mock_status, admin_command_info):
    msg = await _reply_with_auto_wait(admin_command_info, False)
    await disable_level_system(admin_command_info)
    msg.edit.assert_awaited_once()


@patch("commands.level.disable_level_system.get_level_system_status", new_callable=AsyncMock, return_value=True)
async def test_disable_level_system_timeout(mock_status, admin_command_info):
    msg = await _reply_with_auto_wait(admin_command_info, None)
    await disable_level_system(admin_command_info)
    msg.delete.assert_awaited_once()


@patch("commands.level.disable_level_system.get_level_system_status", new_callable=AsyncMock, return_value=True)
async def test_disable_level_system_confirm_and_cancel_buttons(mock_status, admin_command_info):
    msg = MagicMock()
    msg.edit = AsyncMock()
    msg.delete = AsyncMock()

    async def reply(**kwargs):
        view = kwargs.get("view")
        if view is not None:
            interaction = make_view_interaction(admin_command_info.user)
            await view.confirm(interaction, MagicMock())
        return msg

    admin_command_info.reply = AsyncMock(side_effect=reply)

    async def fast_wait(self):
        pass

    with patch("commands.level.disable_level_system.delete_level_system_data", AsyncMock()):
        with patch("commands.level.disable_level_system.set_level_system_status", AsyncMock()):
            with patch("discord.ui.View.wait", fast_wait):
                await disable_level_system(admin_command_info)
    msg.edit.assert_awaited()
