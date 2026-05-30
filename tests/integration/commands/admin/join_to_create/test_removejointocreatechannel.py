from unittest.mock import AsyncMock, patch

import pytest

from commands.admin.join_to_create.removejointocreatechannel import removejointocreatechannel
from tests.helpers.discord import make_text_channel

pytestmark = pytest.mark.asyncio


async def test_removejointocreatechannel_missing_user_permission(restricted_command_info):
    channel = make_text_channel(guild=restricted_command_info.guild)
    await removejointocreatechannel(restricted_command_info, channel=channel)
    restricted_command_info.reply.assert_awaited_once()


@patch("commands.admin.join_to_create.removejointocreatechannel.get_join_to_create_channel", new_callable=AsyncMock)
async def test_removejointocreatechannel_not_set(mock_get, admin_command_info):
    mock_get.return_value = None
    channel = make_text_channel(guild=admin_command_info.guild)
    await removejointocreatechannel(admin_command_info, channel=channel)
    admin_command_info.reply.assert_awaited_once()


@patch("commands.admin.join_to_create.removejointocreatechannel.remove_join_to_create_channel", new_callable=AsyncMock)
@patch("commands.admin.join_to_create.removejointocreatechannel.get_join_to_create_channel", new_callable=AsyncMock)
async def test_removejointocreatechannel_success(mock_get, mock_remove, admin_command_info):
    mock_get.return_value = True
    channel = make_text_channel(guild=admin_command_info.guild)
    await removejointocreatechannel(admin_command_info, channel=channel)
    mock_remove.assert_awaited_once()
    admin_command_info.reply.assert_awaited_once()
