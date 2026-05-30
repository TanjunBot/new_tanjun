from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from commands.admin.trigger_messages.configure import configure_trigger_messages
from tests.integration.commands.admin.conftest import (
    make_trigger_channel,
    make_trigger_message,
    make_view_interaction,
)

pytestmark = pytest.mark.asyncio


async def test_configure_trigger_messages_missing_user_permission(restricted_command_info):
    await configure_trigger_messages(restricted_command_info)
    restricted_command_info.reply.assert_awaited_once()


@patch("commands.admin.trigger_messages.configure.trigger_message_service")
async def test_configure_trigger_messages_no_triggers(mock_service, admin_command_info):
    mock_service.get_all = AsyncMock(return_value=[])
    await configure_trigger_messages(admin_command_info)
    admin_command_info.reply.assert_awaited_once()


@patch("commands.admin.trigger_messages.configure.trigger_message_service")
async def test_configure_trigger_messages_with_triggers(mock_service, admin_command_info):
    trigger = make_trigger_message(case_sensitive=True)
    mock_service.get_all = AsyncMock(return_value=[trigger])
    mock_service.get_trigger_channels = AsyncMock(return_value=[make_trigger_channel()])
    await configure_trigger_messages(admin_command_info)
    admin_command_info.reply.assert_awaited_once()
    assert admin_command_info.reply.await_args.kwargs.get("view") is not None


@patch("commands.admin.trigger_messages.configure.trigger_message_service")
async def test_configure_trigger_messages_no_channels(mock_service, admin_command_info):
    trigger = make_trigger_message(case_sensitive=False)
    mock_service.get_all = AsyncMock(return_value=[trigger])
    mock_service.get_trigger_channels = AsyncMock(return_value=[])
    await configure_trigger_messages(admin_command_info)
    admin_command_info.reply.assert_awaited_once()


@patch("commands.admin.trigger_messages.configure.trigger_message_service")
async def test_configure_view_next_page(mock_service, admin_command_info):
    triggers = [make_trigger_message(trigger_id=1), make_trigger_message(trigger_id=2)]
    mock_service.get_all = AsyncMock(return_value=triggers)
    mock_service.get_trigger_channels = AsyncMock(return_value=[])
    await configure_trigger_messages(admin_command_info)
    view = admin_command_info.reply.await_args.kwargs["view"]
    interaction = make_view_interaction(user=admin_command_info.user)
    interaction.response.edit_message = AsyncMock()
    await view.next(interaction, MagicMock())
    interaction.response.edit_message.assert_awaited_once()


@patch("commands.admin.trigger_messages.configure.trigger_message_service")
async def test_configure_view_previous_page(mock_service, admin_command_info):
    triggers = [make_trigger_message(trigger_id=1), make_trigger_message(trigger_id=2)]
    mock_service.get_all = AsyncMock(return_value=triggers)
    mock_service.get_trigger_channels = AsyncMock(return_value=[])
    await configure_trigger_messages(admin_command_info)
    view = admin_command_info.reply.await_args.kwargs["view"]
    interaction = make_view_interaction(user=admin_command_info.user)
    interaction.response.edit_message = AsyncMock()
    await view.trigger(interaction, MagicMock())
    interaction.response.edit_message.assert_awaited_once()


@patch("commands.admin.trigger_messages.configure.trigger_message_service")
async def test_configure_view_remove_trigger(mock_service, admin_command_info):
    trigger = make_trigger_message()
    mock_service.get_all = AsyncMock(return_value=[trigger])
    mock_service.get_trigger_channels = AsyncMock(return_value=[])
    mock_service.delete = AsyncMock()
    await configure_trigger_messages(admin_command_info)
    view = admin_command_info.reply.await_args.kwargs["view"]
    interaction = make_view_interaction(user=admin_command_info.user)
    interaction.response.edit_message = AsyncMock()
    await view.remove(interaction, MagicMock())
    mock_service.delete.assert_awaited_once()


@patch("commands.admin.trigger_messages.configure.trigger_message_service")
async def test_configure_view_new_modal(mock_service, admin_command_info):
    trigger = make_trigger_message()
    mock_service.get_all = AsyncMock(return_value=[trigger])
    mock_service.get_trigger_channels = AsyncMock(return_value=[])
    await configure_trigger_messages(admin_command_info)
    view = admin_command_info.reply.await_args.kwargs["view"]
    interaction = make_view_interaction(user=admin_command_info.user)
    await view.new(interaction, MagicMock())
    interaction.response.send_modal.assert_awaited_once()


@patch("commands.admin.trigger_messages.configure.trigger_message_service")
async def test_configure_modal_submit(mock_service, admin_command_info):
    trigger = make_trigger_message()
    mock_service.get_all = AsyncMock(return_value=[trigger])
    mock_service.get_trigger_channels = AsyncMock(return_value=[])
    mock_service.create = AsyncMock()
    await configure_trigger_messages(admin_command_info)
    view = admin_command_info.reply.await_args.kwargs["view"]
    interaction = make_view_interaction(user=admin_command_info.user)
    await view.new(interaction, MagicMock())
    modal = interaction.response.send_modal.await_args.args[0]
    modal.children[0].value = "trigger"
    modal.children[1].value = "response"
    modal.children[2].value = "y"
    interaction.response.edit_message = AsyncMock()
    await modal.on_submit(interaction)
    mock_service.create.assert_awaited_once()


@patch("commands.admin.trigger_messages.configure.trigger_message_service")
async def test_configure_view_up_down(mock_service, admin_command_info):
    trigger = make_trigger_message()
    channels = [make_trigger_channel(111), make_trigger_channel(222)]
    mock_service.get_all = AsyncMock(return_value=[trigger])
    mock_service.get_trigger_channels = AsyncMock(return_value=channels)
    await configure_trigger_messages(admin_command_info)
    view = admin_command_info.reply.await_args.kwargs["view"]
    interaction = make_view_interaction(user=admin_command_info.user)
    interaction.response.edit_message = AsyncMock()
    await view.down(interaction, MagicMock())
    await view.up(interaction, MagicMock())
    assert interaction.response.edit_message.await_count >= 2


@patch("commands.admin.trigger_messages.configure.trigger_message_service")
async def test_configure_view_remove_channel(mock_service, admin_command_info):
    trigger = make_trigger_message()
    channels = [make_trigger_channel(111), make_trigger_channel(222)]
    mock_service.get_all = AsyncMock(return_value=[trigger])
    mock_service.get_trigger_channels = AsyncMock(return_value=channels)
    mock_service.remove_channel = AsyncMock()
    await configure_trigger_messages(admin_command_info)
    view = admin_command_info.reply.await_args.kwargs["view"]
    interaction = make_view_interaction(user=admin_command_info.user)
    interaction.response.edit_message = AsyncMock()
    await view.remove_channel(interaction, MagicMock())
    mock_service.remove_channel.assert_awaited_once()


@patch("commands.admin.trigger_messages.configure.trigger_message_service")
async def test_configure_channel_select(mock_service, admin_command_info):
    trigger = make_trigger_message()
    mock_service.get_all = AsyncMock(return_value=[trigger])
    mock_service.get_trigger_channels = AsyncMock(return_value=[])
    mock_service.add_channel = AsyncMock()
    await configure_trigger_messages(admin_command_info)
    view = admin_command_info.reply.await_args.kwargs["view"]
    interaction = make_view_interaction(user=admin_command_info.user)
    await view.add_channel(interaction, MagicMock())
    channel_view = interaction.response.edit_message.await_args.kwargs["view"]
    interaction.response.edit_message = AsyncMock()
    interaction.data = {"values": ["555555555"]}
    await channel_view.on_channel_select(interaction)
    mock_service.add_channel.assert_awaited_once()
