from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from commands.giveaway.start import (
    AddChannelRequirementValueModal,
    AddChannelRequirementView,
    RemoveChannelRequirementView,
)
from tests.helpers.discord import make_text_channel
from tests.integration.commands.admin.conftest import make_view_interaction
from tests.integration.commands.giveaway.test_giveaway_start_deep import _builder

pytestmark = pytest.mark.asyncio


async def test_add_channel_requirement_view_select_and_confirm(admin_command_info):
    view = _builder(admin_command_info)
    ch = make_text_channel(guild=admin_command_info.guild)
    req_view = AddChannelRequirementView(admin_command_info, view)
    req_view.selected_channels = [str(ch.id)]
    interaction = make_view_interaction(user=admin_command_info.user)
    interaction.data = {"custom_id": "confirm"}
    await req_view.on_button_press(interaction)
    interaction.response.send_modal.assert_awaited_once()


async def test_add_channel_requirement_view_cancel(admin_command_info):
    view = _builder(admin_command_info)
    req_view = AddChannelRequirementView(admin_command_info, view)
    interaction = make_view_interaction(user=admin_command_info.user)
    interaction.data = {"custom_id": "cancel"}
    interaction.response.edit_message = AsyncMock()
    await req_view.on_button_press(interaction)
    interaction.response.edit_message.assert_awaited_once()


async def test_add_channel_requirement_view_channel_select(admin_command_info):
    view = _builder(admin_command_info)
    req_view = AddChannelRequirementView(admin_command_info, view)
    ch = make_text_channel(guild=admin_command_info.guild)
    interaction = make_view_interaction(user=admin_command_info.user)
    interaction.data = {"values": [str(ch.id)]}
    interaction.response.edit_message = AsyncMock()
    await req_view.on_channel_select(interaction)
    assert req_view.selected_channels == [str(ch.id)]


async def test_add_channel_requirement_view_unauthorized(admin_command_info):
    view = _builder(admin_command_info)
    req_view = AddChannelRequirementView(admin_command_info, view)
    interaction = make_view_interaction(user=MagicMock(id=999))
    ok = await req_view.interaction_check(interaction)
    assert ok is False


async def test_add_channel_requirement_view_timeout(admin_command_info):
    view = _builder(admin_command_info)
    req_view = AddChannelRequirementView(admin_command_info, view)
    await req_view.on_timeout()
    view.generator_message.edit.assert_awaited()


async def test_add_channel_requirement_value_modal_submit(admin_command_info):
    view = _builder(admin_command_info)
    ch = make_text_channel(guild=admin_command_info.guild)
    admin_command_info.guild.get_channel = MagicMock(return_value=ch)
    modal = AddChannelRequirementValueModal(view, admin_command_info, ch.id, "t", "d")
    modal.children = [MagicMock(value="5")]
    interaction = make_view_interaction(user=admin_command_info.user)
    interaction.response.edit_message = AsyncMock()
    await modal.on_submit(interaction)
    assert view.giveaway_data["channel_requirements"][str(ch.id)] == "5"


async def test_add_channel_requirement_value_modal_denied(admin_command_info):
    view = _builder(admin_command_info)
    ch = make_text_channel(guild=admin_command_info.guild)
    modal = AddChannelRequirementValueModal(view, admin_command_info, ch.id, "t", "d")
    interaction = make_view_interaction(user=MagicMock(id=999))
    ok = await modal.interaction_check(interaction)
    assert ok is False


async def test_remove_channel_requirement_view_confirm(admin_command_info):
    view = _builder(admin_command_info)
    ch = make_text_channel(guild=admin_command_info.guild, channel_id=555)
    admin_command_info.guild.get_channel = MagicMock(return_value=ch)
    view.giveaway_data["channel_requirements"] = {str(ch.id): 2}
    req_view = RemoveChannelRequirementView(admin_command_info, view)
    req_view.selected_channels = [str(ch.id)]
    interaction = make_view_interaction(user=admin_command_info.user)
    interaction.data = {"custom_id": "confirm"}
    interaction.response.edit_message = AsyncMock()
    await req_view.on_button_press(interaction)
    assert str(ch.id) not in view.giveaway_data["channel_requirements"]


async def test_remove_channel_requirement_view_cancel(admin_command_info):
    view = _builder(admin_command_info)
    ch = make_text_channel(guild=admin_command_info.guild)
    admin_command_info.guild.get_channel = MagicMock(return_value=ch)
    view.giveaway_data["channel_requirements"] = {str(ch.id): 2}
    req_view = RemoveChannelRequirementView(admin_command_info, view)
    interaction = make_view_interaction(user=admin_command_info.user)
    interaction.data = {"custom_id": "cancel"}
    await req_view.on_button_press(interaction)
    assert str(ch.id) in view.giveaway_data["channel_requirements"]


async def test_remove_channel_requirement_view_select(admin_command_info):
    view = _builder(admin_command_info)
    ch = make_text_channel(guild=admin_command_info.guild)
    admin_command_info.guild.get_channel = MagicMock(return_value=ch)
    view.giveaway_data["channel_requirements"] = {str(ch.id): 2}
    req_view = RemoveChannelRequirementView(admin_command_info, view)
    interaction = make_view_interaction(user=admin_command_info.user)
    interaction.data = {"values": [str(ch.id)]}
    interaction.response.edit_message = AsyncMock()
    await req_view.on_channel_select(interaction)
    assert req_view.selected_channels == [str(ch.id)]
