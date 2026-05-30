from __future__ import annotations

from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from commands.giveaway import utility as gw_util
from commands.giveaway.edit_giveaway import GiveawayEditor
from commands.giveaway.start import (
    AddChannelRequirementView,
    ChangeWinnersModal,
    DayRequirementModal,
    EndTimeModal,
    MessageRequirementModal,
    RoleRequirementView,
    StartTimeModal,
    VoiceRequirementModal,
)
from tests.helpers.discord import make_text_channel
from tests.integration.commands.admin.conftest import make_view_interaction
from tests.integration.commands.giveaway.test_giveaway_edit_deep import _editor
from tests.integration.commands.giveaway.test_giveaway_start_deep import _builder


pytestmark = pytest.mark.asyncio


def _giveaway(**kwargs) -> MagicMock:
    gw = MagicMock()
    gw.guild_id = "123"
    gw.channel_id = "456"
    gw.message_id = "789"
    gw.message = "Giveaway!"
    gw.title = "Prize"
    gw.description = "Desc"
    gw.ended = kwargs.get("ended", False)
    gw.winners = kwargs.get("winners", 1)
    gw.new_message_requirement = kwargs.get("new_message_requirement")
    gw.day_requirement = kwargs.get("day_requirement")
    gw.voice_requirement = kwargs.get("voice_requirement")
    gw.start_time = kwargs.get("start_time", datetime.now())
    return gw


@patch("commands.giveaway.utility.giveaway_service.mark_sent", new_callable=AsyncMock)
@patch("commands.giveaway.utility.giveaway_service.get_participants", new_callable=AsyncMock, return_value=[])
@patch("commands.giveaway.utility.giveaway_service.get_channel_requirements", new_callable=AsyncMock, return_value=[])
@patch("commands.giveaway.utility.giveaway_service.get_role_requirements", new_callable=AsyncMock, return_value=[])
@patch("commands.giveaway.utility.giveaway_service.get", new_callable=AsyncMock)
async def test_send_giveaway_no_channel(mock_get, mock_roles, mock_channels, mock_parts, mock_sent):
    gw = _giveaway()
    mock_get.return_value = gw
    guild = MagicMock(preferred_locale="en_US")
    guild.get_channel = MagicMock(return_value=None)
    client = MagicMock()
    client.get_guild = MagicMock(return_value=guild)
    await gw_util.sendGiveaway(1, client)
    mock_sent.assert_not_awaited()


@patch("commands.giveaway.utility.giveaway_service.get_channel_requirements", new_callable=AsyncMock, return_value=[])
@patch("commands.giveaway.utility.giveaway_service.get_role_requirements", new_callable=AsyncMock, return_value=[])
@patch("commands.giveaway.utility.giveaway_service.get", new_callable=AsyncMock)
async def test_update_embed_no_guild(mock_get, mock_roles, mock_channels):
    mock_get.return_value = _giveaway()
    client = MagicMock()
    client.get_guild = MagicMock(return_value=None)
    await gw_util.updateGiveawayEmbed(1, client)


@patch("commands.giveaway.utility.giveaway_service.get_channel_requirements", new_callable=AsyncMock, return_value=[])
@patch("commands.giveaway.utility.giveaway_service.get_role_requirements", new_callable=AsyncMock, return_value=[])
@patch("commands.giveaway.utility.giveaway_service.get", new_callable=AsyncMock)
async def test_update_embed_no_channel(mock_get, mock_roles, mock_channels):
    mock_get.return_value = _giveaway()
    guild = MagicMock(preferred_locale="en_US")
    guild.get_channel = MagicMock(return_value=None)
    client = MagicMock()
    client.get_guild = MagicMock(return_value=guild)
    await gw_util.updateGiveawayEmbed(1, client)


@patch("commands.giveaway.utility.giveaway_service.get", new_callable=AsyncMock)
async def test_add_participant_no_guild(mock_get):
    mock_get.return_value = _giveaway()
    client = MagicMock()
    client.get_guild = MagicMock(return_value=None)
    assert await gw_util.add_giveaway_participant(1, 1, client) is None


@patch("commands.giveaway.utility.giveaway_service.get", new_callable=AsyncMock)
async def test_add_participant_no_member(mock_get):
    mock_get.return_value = _giveaway()
    guild = MagicMock(preferred_locale="en_US")
    guild.get_member = MagicMock(return_value=None)
    client = MagicMock()
    client.get_guild = MagicMock(return_value=guild)
    assert await gw_util.add_giveaway_participant(1, 1, client) is None


@patch("commands.giveaway.utility.check_if_opted_out", new_callable=AsyncMock, return_value=False)
@patch("commands.giveaway.utility.giveaway_service.is_user_blacklisted", new_callable=AsyncMock, return_value=False)
@patch("commands.giveaway.utility.giveaway_service.is_participant", new_callable=AsyncMock, return_value=False)
@patch("commands.giveaway.utility.giveaway_service.get", new_callable=AsyncMock)
async def test_add_participant_day_member_missing(mock_get, mock_is, mock_bl, mock_opt):
    gw = _giveaway(day_requirement=30)
    mock_get.return_value = gw
    guild = MagicMock(preferred_locale="en_US")
    guild.get_member = MagicMock(return_value=None)
    client = MagicMock()
    client.get_guild = MagicMock(return_value=guild)
    assert await gw_util.add_giveaway_participant(1, 1, client) is None


@patch("commands.giveaway.utility.check_if_opted_out", new_callable=AsyncMock, return_value=False)
@patch("commands.giveaway.utility.giveaway_service.is_user_blacklisted", new_callable=AsyncMock, return_value=False)
@patch("commands.giveaway.utility.giveaway_service.is_participant", new_callable=AsyncMock, return_value=False)
@patch("commands.giveaway.utility.giveaway_service.get_voice_time", new_callable=AsyncMock, return_value=0)
@patch("commands.giveaway.utility.giveaway_service.get", new_callable=AsyncMock)
async def test_add_participant_voice_member_missing(mock_get, mock_is, mock_bl, mock_voice, mock_opt):
    gw = _giveaway(voice_requirement=30)
    mock_get.return_value = gw
    guild = MagicMock(preferred_locale="en_US")
    guild.get_member = MagicMock(return_value=None)
    client = MagicMock()
    client.get_guild = MagicMock(return_value=guild)
    assert await gw_util.add_giveaway_participant(1, 1, client) is None


@patch("commands.giveaway.utility.check_if_opted_out", new_callable=AsyncMock, return_value=False)
@patch("commands.giveaway.utility.giveaway_service.is_user_blacklisted", new_callable=AsyncMock, return_value=False)
@patch("commands.giveaway.utility.giveaway_service.is_participant", new_callable=AsyncMock, return_value=False)
@patch("commands.giveaway.utility.giveaway_service.get", new_callable=AsyncMock)
async def test_add_participant_day_no_start_time(mock_get, mock_is, mock_bl, mock_opt):
    gw = _giveaway(day_requirement=30, start_time=None)
    mock_get.return_value = gw
    guild = MagicMock(preferred_locale="en_US")
    member = MagicMock()
    member.joined_at = datetime(2020, 1, 1, tzinfo=timezone.utc)
    member.roles = []
    guild.get_member = MagicMock(return_value=member)
    client = MagicMock()
    client.get_guild = MagicMock(return_value=guild)
    assert await gw_util.add_giveaway_participant(1, 1, client) is None


@patch("commands.giveaway.utility.giveaway_service.set_ended", new_callable=AsyncMock)
@patch("commands.giveaway.utility.giveaway_service.get_participants", new_callable=AsyncMock, return_value=[])
@patch("commands.giveaway.utility.giveaway_service.get", new_callable=AsyncMock)
async def test_end_giveaway_no_guild(mock_get, mock_parts, mock_ended):
    mock_get.return_value = _giveaway()
    client = MagicMock()
    client.get_guild = MagicMock(return_value=None)
    await gw_util.endGiveaway(1, client)
    mock_ended.assert_not_awaited()


@patch("commands.giveaway.utility.giveaway_service.set_ended", new_callable=AsyncMock)
@patch("commands.giveaway.utility.giveaway_service.get_participants", new_callable=AsyncMock, return_value=[])
@patch("commands.giveaway.utility.giveaway_service.get", new_callable=AsyncMock)
async def test_end_giveaway_no_channel(mock_get, mock_parts, mock_ended):
    mock_get.return_value = _giveaway()
    guild = MagicMock(preferred_locale="en_US")
    guild.get_channel = MagicMock(return_value=None)
    client = MagicMock()
    client.get_guild = MagicMock(return_value=guild)
    await gw_util.endGiveaway(1, client)
    mock_ended.assert_not_awaited()


@patch("commands.giveaway.utility.giveaway_service.get_channel_requirements", new_callable=AsyncMock, return_value=[])
@patch("commands.giveaway.utility.giveaway_service.get_role_requirements", new_callable=AsyncMock, return_value=[])
@patch("commands.giveaway.utility.giveaway_service.get", new_callable=AsyncMock)
async def test_update_message_no_guild(mock_get, mock_roles, mock_channels):
    mock_get.return_value = _giveaway()
    client = MagicMock()
    client.get_guild = MagicMock(return_value=None)
    await gw_util.updateGiveawayMessage(1, client)


@patch("commands.giveaway.utility.giveaway_service.get_channel_requirements", new_callable=AsyncMock, return_value=[])
@patch("commands.giveaway.utility.giveaway_service.get_role_requirements", new_callable=AsyncMock, return_value=[])
@patch("commands.giveaway.utility.giveaway_service.get", new_callable=AsyncMock)
async def test_update_message_no_channel(mock_get, mock_roles, mock_channels):
    mock_get.return_value = _giveaway()
    guild = MagicMock(preferred_locale="en_US")
    guild.get_channel = MagicMock(return_value=None)
    client = MagicMock()
    client.get_guild = MagicMock(return_value=guild)
    await gw_util.updateGiveawayMessage(1, client)


async def test_editor_interaction_check_ok(admin_command_info):
    editor = _editor(admin_command_info)
    interaction = make_view_interaction(user=admin_command_info.user)
    assert await editor.interaction_check(interaction) is True


@pytest.mark.parametrize(
    "custom_id",
    [
        "change_description",
        "custom_name",
        "preview",
        "confirm",
    ],
)
async def test_editor_button_callback_routes(custom_id, admin_command_info):
    editor = _editor(admin_command_info)
    interaction = make_view_interaction(user=admin_command_info.user)
    interaction.response.edit_message = AsyncMock()
    interaction.response.send_modal = AsyncMock()
    with (
        patch.object(GiveawayEditor, "change_description", AsyncMock()) as desc,
        patch.object(GiveawayEditor, "confirm", AsyncMock()) as confirm,
        patch.object(GiveawayEditor, "preview", AsyncMock()) as preview,
    ):
        await editor.button_callback(interaction, MagicMock(custom_id=custom_id))
    if custom_id == "change_description":
        desc.assert_awaited_once()
    elif custom_id == "confirm":
        confirm.assert_awaited_once()
    elif custom_id == "preview":
        preview.assert_awaited_once()
    else:
        interaction.response.send_modal.assert_awaited_once()


async def test_editor_toggle_via_callback(admin_command_info):
    editor = _editor(admin_command_info)
    ch = make_text_channel(guild=admin_command_info.guild)
    admin_command_info.guild.get_channel = MagicMock(return_value=ch)
    interaction = make_view_interaction(user=admin_command_info.user)
    interaction.response.edit_message = AsyncMock()
    await editor.button_callback(interaction, MagicMock(custom_id="toggle_button"))
    assert editor.giveaway_data["with_button"] is False


async def test_editor_price_via_callback(admin_command_info):
    editor = _editor(admin_command_info)
    interaction = make_view_interaction(user=admin_command_info.user)
    interaction.response.edit_message = AsyncMock()
    admin_command_info.client.wait_for = AsyncMock(side_effect=TimeoutError())
    await editor.button_callback(interaction, MagicMock(custom_id="price"))
    editor.generator_message.edit.assert_awaited()

    view = _builder(admin_command_info)
    modal = ChangeWinnersModal(view, admin_command_info, "t", "d")
    interaction = make_view_interaction(user=admin_command_info.user)
    assert await modal.interaction_check(interaction) is True


async def test_change_winners_modal_timeout(admin_command_info):
    view = _builder(admin_command_info)
    modal = ChangeWinnersModal(view, admin_command_info, "t", "d")
    await modal.on_timeout()
    view.generator_message.edit.assert_awaited()


async def test_end_time_modal_check_ok(admin_command_info):
    view = _builder(admin_command_info)
    modal = EndTimeModal(view, admin_command_info, "t", "d")
    interaction = make_view_interaction(user=admin_command_info.user)
    assert await modal.interaction_check(interaction) is True


async def test_end_time_modal_timeout(admin_command_info):
    view = _builder(admin_command_info)
    modal = EndTimeModal(view, admin_command_info, "t", "d")
    await modal.on_timeout()
    view.generator_message.edit.assert_awaited()


async def test_start_time_modal_check_ok(admin_command_info):
    view = _builder(admin_command_info)
    modal = StartTimeModal(view, admin_command_info, "t", "d")
    interaction = make_view_interaction(user=admin_command_info.user)
    assert await modal.interaction_check(interaction) is True


async def test_message_requirement_modal_timeout(admin_command_info):
    view = _builder(admin_command_info)
    modal = MessageRequirementModal(view, admin_command_info, "t", "d")
    await modal.on_timeout()
    view.generator_message.edit.assert_awaited()


async def test_day_requirement_modal_check_ok(admin_command_info):
    view = _builder(admin_command_info)
    modal = DayRequirementModal(view, admin_command_info, "t", "d")
    interaction = make_view_interaction(user=admin_command_info.user)
    assert await modal.interaction_check(interaction) is True


async def test_voice_requirement_modal_timeout(admin_command_info):
    view = _builder(admin_command_info)
    modal = VoiceRequirementModal(view, admin_command_info, "t", "d")
    await modal.on_timeout()
    view.generator_message.edit.assert_awaited()


async def test_role_requirement_view_cancel(admin_command_info):
    view = _builder(admin_command_info)
    role_view = RoleRequirementView(view, admin_command_info, "t", "d")
    interaction = make_view_interaction(user=admin_command_info.user)
    interaction.response.edit_message = AsyncMock()
    await role_view.cancel(interaction)
    interaction.response.edit_message.assert_awaited_once()


async def test_role_requirement_view_timeout(admin_command_info):
    view = _builder(admin_command_info)
    role_view = RoleRequirementView(view, admin_command_info, "t", "d")
    await role_view.on_timeout()
    view.generator_message.edit.assert_awaited()


async def test_add_channel_view_select_and_confirm(admin_command_info):
    view = _builder(admin_command_info)
    ch_view = AddChannelRequirementView(admin_command_info, view)
    interaction = make_view_interaction(user=admin_command_info.user)
    interaction.data = {"values": ["123456789012345678"]}
    interaction.response.edit_message = AsyncMock()
    await ch_view.on_channel_select(interaction)
    interaction.response.edit_message.assert_awaited_once()
    confirm = make_view_interaction(user=admin_command_info.user)
    confirm.data = {"custom_id": "confirm"}
    confirm.response.send_modal = AsyncMock()
    await ch_view.on_button_press(confirm)
    confirm.response.send_modal.assert_awaited_once()


async def test_add_channel_view_cancel(admin_command_info):
    view = _builder(admin_command_info)
    ch_view = AddChannelRequirementView(admin_command_info, view)
    interaction = make_view_interaction(user=admin_command_info.user)
    interaction.data = {"custom_id": "cancel"}
    interaction.response.edit_message = AsyncMock()
    await ch_view.on_button_press(interaction)
    interaction.response.edit_message.assert_awaited_once()
