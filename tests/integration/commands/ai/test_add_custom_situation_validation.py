from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from commands.ai.add_custom_situation import add_custom_situation


pytestmark = pytest.mark.asyncio


@pytest.mark.parametrize(
    "name,situation,temp,top_p,freq,pres",
    [
        ("ab", "1234567890", 1, 1, 0, 0),
        ("valid", "short", 1, 1, 0, 0),
        ("valid", "x" * 4001, 1, 1, 0, 0),
        ("n" * 16, "1234567890", 1, 1, 0, 0),
        ("valid", "1234567890", 3, 1, 0, 0),
        ("valid", "1234567890", 1, 2, 0, 0),
        ("valid", "1234567890", 1, 1, 3, 0),
        ("valid", "1234567890", 1, 1, 0, 3),
    ],
)
async def test_add_custom_situation_validation_errors(admin_command_info, name, situation, temp, top_p, freq, pres):
    await add_custom_situation(admin_command_info, name, situation, temp, top_p, freq, pres)
    admin_command_info.reply.assert_awaited_once()


@patch("commands.ai.add_custom_situation.AiService.get_user_situation", new_callable=AsyncMock, return_value={"id": "1"})
@patch("commands.ai.add_custom_situation.AiService.get_situation", new_callable=AsyncMock, return_value=None)
async def test_add_custom_situation_already_has_user_situation(mock_get, mock_user, admin_command_info):
    with patch("commands.ai.add_custom_situation.config.adminIds", []):
        await add_custom_situation(admin_command_info, "personality", "1234567890")
    admin_command_info.reply.assert_awaited_once()


@patch("commands.ai.add_custom_situation.AiService.get_user_situation", new_callable=AsyncMock, return_value=None)
@patch("commands.ai.add_custom_situation.AiService.get_situation", new_callable=AsyncMock, return_value=MagicMock())
@patch("commands.ai.add_custom_situation.AiService.create_situation", new_callable=AsyncMock)
async def test_add_custom_situation_name_exists_non_admin(mock_create, mock_get, mock_user, admin_command_info):
    with patch("commands.ai.add_custom_situation.config.adminIds", []):
        await add_custom_situation(admin_command_info, "personality", "1234567890")
    admin_command_info.reply.assert_awaited_once()


@patch("commands.ai.add_custom_situation.AiService.get_user_situation", new_callable=AsyncMock, return_value=None)
@patch("commands.ai.add_custom_situation.AiService.get_situation", new_callable=AsyncMock, return_value=None)
@patch("commands.ai.add_custom_situation.AiService.create_situation", new_callable=AsyncMock)
async def test_add_custom_situation_success(mock_create, mock_get, mock_user, admin_command_info):
    ch = MagicMock()
    ch.send = AsyncMock()
    admin_command_info.client.fetch_channel = AsyncMock(return_value=ch)
    with patch("commands.ai.add_custom_situation.config.adminIds", [admin_command_info.user.id]):
        await add_custom_situation(admin_command_info, "personality", "1234567890")
    mock_create.assert_awaited_once()
    ch.send.assert_awaited_once()
