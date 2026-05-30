import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from commands.admin.ticket.open_ticket import openTicket, open_ticket_2
from tests.helpers.discord import make_interaction, make_permissions, make_text_channel


pytestmark = pytest.mark.asyncio


def _make_open_interaction():
    interaction = make_interaction()
    interaction.data = {"custom_id": "ticket_create;1"}
    interaction.response.defer = AsyncMock()
    interaction.followup.send = AsyncMock()
    return interaction


async def test_open_ticket_wrong_custom_id():
    interaction = make_interaction()
    interaction.data = {"custom_id": "other"}
    await openTicket(interaction)
    interaction.response.defer.assert_not_called()


async def test_open_ticket_opted_out_confirm_returns():
    interaction = make_interaction()
    interaction.data = {"custom_id": "ticket_create;1;optedOutConfirm"}
    await openTicket(interaction)
    interaction.response.defer.assert_not_called()


@patch("commands.admin.ticket.open_ticket.check_if_opted_out", new_callable=AsyncMock, return_value=True)
async def test_open_ticket_opted_out(mock_optout):
    interaction = _make_open_interaction()
    await openTicket(interaction)
    interaction.response.defer.assert_awaited_once()
    interaction.followup.send.assert_awaited_once()


@patch("commands.admin.ticket.open_ticket.check_if_opted_out", new_callable=AsyncMock, return_value=False)
@patch("commands.admin.ticket.open_ticket.open_ticket_2", new_callable=AsyncMock)
async def test_open_ticket_calls_open_ticket_2(mock_open, mock_optout):
    interaction = _make_open_interaction()
    await openTicket(interaction)
    mock_open.assert_awaited_once()


@patch("commands.admin.ticket.open_ticket.ticket_service")
async def test_open_ticket_2_not_found(mock_service):
    interaction = _make_open_interaction()
    mock_service.get_config = AsyncMock(return_value=None)
    interaction.response.send_message = AsyncMock()
    await open_ticket_2(interaction)
    interaction.response.send_message.assert_awaited_once()


@patch("commands.admin.ticket.open_ticket.ticket_service")
async def test_open_ticket_2_missing_thread_permission(mock_service):
    interaction = _make_open_interaction()
    ticket = MagicMock()
    ticket.introduction = None
    ticket.ping_role = None
    mock_service.get_config = AsyncMock(return_value=ticket)
    interaction.channel = MagicMock()
    interaction.channel.permissions_for = MagicMock(return_value=make_permissions(create_private_threads=False))
    interaction.response.send_message = AsyncMock()
    await open_ticket_2(interaction)
    interaction.response.send_message.assert_awaited_once()


@patch("commands.admin.ticket.open_ticket.ticket_service")
async def test_open_ticket_2_success(mock_service):
    interaction = _make_open_interaction()
    ticket = MagicMock()
    ticket.introduction = "Welcome to support"
    ticket.ping_role = "555555555"
    mock_service.get_config = AsyncMock(return_value=ticket)
    mock_service.open = AsyncMock()
    channel = make_text_channel()
    channel.create_thread = AsyncMock(return_value=MagicMock(
        id=777777777,
        send=AsyncMock(),
        add_user=AsyncMock(),
    ))
    channel.permissions_for = MagicMock(return_value=make_permissions(create_private_threads=True))
    interaction.channel = channel
    interaction.guild.preferred_locale = MagicMock(value="en-US")
    interaction.response.send_message = AsyncMock()
    await open_ticket_2(interaction)
    channel.create_thread.assert_awaited_once()
    interaction.followup.send.assert_awaited_once()


@patch("commands.admin.ticket.open_ticket.ticket_service")
async def test_open_ticket_2_service_failure_rollback(mock_service):
    interaction = _make_open_interaction()
    ticket = MagicMock()
    ticket.introduction = None
    ticket.ping_role = None
    mock_service.get_config = AsyncMock(return_value=ticket)
    mock_service.open = AsyncMock(side_effect=RuntimeError("db fail"))
    thread = MagicMock()
    thread.id = 777777777
    thread.send = AsyncMock()
    thread.add_user = AsyncMock()
    thread.delete = AsyncMock()
    channel = make_text_channel()
    channel.create_thread = AsyncMock(return_value=thread)
    channel.permissions_for = MagicMock(return_value=make_permissions(create_private_threads=True))
    interaction.channel = channel
    interaction.guild.preferred_locale = MagicMock(value="en-US")
    interaction.response.send_message = AsyncMock()
    with pytest.raises(RuntimeError):
        await open_ticket_2(interaction)
    thread.delete.assert_awaited_once()
    interaction.followup.send.assert_awaited_once()
