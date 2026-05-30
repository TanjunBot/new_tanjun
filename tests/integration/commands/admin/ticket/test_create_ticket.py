from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from commands.admin.ticket.create_ticket import create_ticket
from tests.helpers.discord import make_permissions, make_role, make_text_channel

pytestmark = pytest.mark.asyncio


async def test_create_ticket_missing_user_permission(restricted_command_info):
    channel = make_text_channel(guild=restricted_command_info.guild)
    await create_ticket(restricted_command_info, channel=channel, name="Support", description="Get help")
    restricted_command_info.reply.assert_awaited_once()


async def test_create_ticket_missing_bot_permission(admin_command_info):
    channel = make_text_channel(guild=admin_command_info.guild)
    channel.permissions_for = MagicMock(return_value=make_permissions(send_messages=False))
    await create_ticket(admin_command_info, channel=channel, name="Support", description="Get help")
    admin_command_info.reply.assert_awaited_once()


@patch("commands.admin.ticket.create_ticket.ticket_service")
async def test_create_ticket_service_error(mock_service, admin_command_info):
    channel = make_text_channel(guild=admin_command_info.guild)
    channel.permissions_for = MagicMock(return_value=make_permissions(send_messages=True))
    mock_service.create_config = AsyncMock(return_value=None)
    await create_ticket(admin_command_info, channel=channel, name="Support", description="Get help")
    admin_command_info.reply.assert_awaited_once()


@patch("commands.admin.ticket.create_ticket.ticket_service")
async def test_create_ticket_success(mock_service, admin_command_info):
    channel = make_text_channel(guild=admin_command_info.guild)
    channel.permissions_for = MagicMock(return_value=make_permissions(send_messages=True))
    mock_service.create_config = AsyncMock(return_value=42)
    await create_ticket(
        admin_command_info,
        channel=channel,
        name="Support",
        description="Get help",
        ping_role=make_role(),
        summary_channel=make_text_channel(guild=admin_command_info.guild),
        introduction="Welcome",
    )
    channel.send.assert_awaited_once()
    admin_command_info.reply.assert_awaited_once()
