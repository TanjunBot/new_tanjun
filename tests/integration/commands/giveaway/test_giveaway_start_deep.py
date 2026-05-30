from __future__ import annotations

import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from commands.giveaway.start import (
    ChangeWinnersModal,
    CustomNameModal,
    DayRequirementModal,
    EndTimeModal,
    GiveawayBuilder,
    GiveawayBuilderButton,
    MessageRequirementModal,
    SponsorView,
    StartTimeModal,
    VoiceRequirementModal,
)
from tests.helpers.discord import make_text_channel
from tests.integration.commands.admin.conftest import make_view_interaction

pytestmark = pytest.mark.asyncio


def _builder(admin_command_info) -> GiveawayBuilder:
    channel = make_text_channel(guild=admin_command_info.guild)
    view = GiveawayBuilder(admin_command_info, "Prize", channel)
    view.generator_message = MagicMock()
    view.generator_message.edit = AsyncMock()
    return view


def _button(custom_id: str) -> MagicMock:
    return MagicMock(custom_id=custom_id)


async def _callback(view: GiveawayBuilder, custom_id: str, admin_command_info):
    interaction = make_view_interaction(user=admin_command_info.user)
    await view.button_callback(interaction, _button(custom_id))
    return interaction


@pytest.mark.parametrize(
    "custom_id",
    [
        "sponsor",
        "end_time",
        "start_time",
        "new_message_requirement",
        "day_requirement",
        "role_requirement",
        "voice_requirement",
        "add_channel_requirement",
    ],
)
async def test_builder_buttons_dispatch(custom_id, admin_command_info):
    view = _builder(admin_command_info)
    interaction = await _callback(view, custom_id, admin_command_info)
    assert interaction.response.send_modal.await_count + interaction.response.edit_message.await_count >= 1


async def test_builder_change_description_dispatch(admin_command_info):
    view = _builder(admin_command_info)
    interaction = make_view_interaction(user=admin_command_info.user)
    admin_command_info.client.wait_for = AsyncMock(side_effect=TimeoutError())
    await GiveawayBuilder.change_description(view, interaction, _button("change_description"))
    interaction.response.edit_message.assert_awaited_once()


async def test_builder_remove_channel_requirement_button(admin_command_info):
    view = _builder(admin_command_info)
    ch = make_text_channel(guild=admin_command_info.guild)
    admin_command_info.guild.get_channel = MagicMock(return_value=ch)
    view.giveaway_data["channel_requirements"] = {str(ch.id): 5}
    view.update_buttons()
    interaction = await _callback(view, "remove_channel_requirement", admin_command_info)
    interaction.response.edit_message.assert_awaited_once()


@patch("commands.giveaway.start.generateGiveawayEmbed", new_callable=AsyncMock, return_value=MagicMock())
async def test_builder_preview_button(mock_embed, admin_command_info):
    view = _builder(admin_command_info)
    interaction = await _callback(view, "preview", admin_command_info)
    interaction.response.send_message.assert_awaited_once()


async def test_change_description_timeout(admin_command_info):
    view = _builder(admin_command_info)
    interaction = make_view_interaction(user=admin_command_info.user)
    admin_command_info.client.wait_for = AsyncMock(side_effect=TimeoutError())
    await GiveawayBuilder.change_description(view, interaction, _button("change_description"))
    view.generator_message.edit.assert_awaited()


async def test_change_description_success(admin_command_info):
    view = _builder(admin_command_info)
    interaction = make_view_interaction(user=admin_command_info.user)
    msg = MagicMock()
    msg.content = "New description"
    msg.author = interaction.user
    msg.channel = interaction.channel
    msg.delete = AsyncMock()
    admin_command_info.client.wait_for = AsyncMock(return_value=msg)
    await GiveawayBuilder.change_description(view, interaction, _button("change_description"))
    assert view.giveaway_data["description"] == "New description"
    msg.delete.assert_awaited_once()


async def test_price_timeout(admin_command_info):
    view = _builder(admin_command_info)
    interaction = make_view_interaction(user=admin_command_info.user)
    admin_command_info.client.wait_for = AsyncMock(side_effect=TimeoutError())
    await GiveawayBuilder.price(view, interaction, _button("price"))
    view.generator_message.edit.assert_awaited()


async def test_message_too_long(admin_command_info):
    view = _builder(admin_command_info)
    interaction = make_view_interaction(user=admin_command_info.user)
    msg = MagicMock()
    msg.content = "x" * 200
    msg.author = interaction.user
    msg.channel = interaction.channel
    msg.delete = AsyncMock()
    admin_command_info.client.wait_for = AsyncMock(return_value=msg)
    await GiveawayBuilder.message(view, interaction, _button("message"))
    msg.delete.assert_awaited_once()


async def test_end_time_modal_submit(admin_command_info):
    view = _builder(admin_command_info)
    modal = EndTimeModal(view, admin_command_info, "t", "d")
    modal.children = [MagicMock(value="48h")]
    interaction = make_view_interaction(user=admin_command_info.user)
    interaction.response.edit_message = AsyncMock()
    await modal.on_submit(interaction)
    assert view.giveaway_data["end_time"] == "48h"


async def test_change_winners_modal_submit(admin_command_info):
    view = _builder(admin_command_info)
    modal = ChangeWinnersModal(view, admin_command_info, "t", "d")
    modal.children = [MagicMock(value="3")]
    interaction = make_view_interaction(user=admin_command_info.user)
    interaction.response.edit_message = AsyncMock()
    await modal.on_submit(interaction)
    assert view.giveaway_data["winners"] == 3


async def test_message_requirement_modal_submit(admin_command_info):
    view = _builder(admin_command_info)
    modal = MessageRequirementModal(view, admin_command_info, "t", "d")
    modal.children = [MagicMock(value="10")]
    interaction = make_view_interaction(user=admin_command_info.user)
    interaction.response.edit_message = AsyncMock()
    await modal.on_submit(interaction)
    assert view.giveaway_data["new_message_requirement"] == 10


async def test_custom_name_modal_unauthorized(admin_command_info):
    view = _builder(admin_command_info)
    modal = CustomNameModal(view, admin_command_info, "t", "d")
    interaction = make_view_interaction(user=MagicMock(id=999))
    ok = await modal.interaction_check(interaction)
    assert ok is False


async def test_sponsor_view_confirm(admin_command_info):
    view = _builder(admin_command_info)
    sponsor_view = SponsorView(admin_command_info, view)
    sponsor_view.selected_user = "111"
    interaction = make_view_interaction(user=admin_command_info.user)
    interaction.data = {"custom_id": "confirm"}
    interaction.response.edit_message = AsyncMock()
    await sponsor_view.on_button_press(interaction)
    assert view.giveaway_data["sponsor"] == "111"


async def test_sponsor_view_cancel(admin_command_info):
    view = _builder(admin_command_info)
    sponsor_view = SponsorView(admin_command_info, view)
    interaction = make_view_interaction(user=admin_command_info.user)
    interaction.data = {"custom_id": "cancel"}
    interaction.response.edit_message = AsyncMock()
    await sponsor_view.on_button_press(interaction)


async def test_sponsor_view_user_select(admin_command_info):
    view = _builder(admin_command_info)
    sponsor_view = SponsorView(admin_command_info, view)
    interaction = make_view_interaction(user=admin_command_info.user)
    interaction.data = {"values": ["222"]}
    interaction.response.edit_message = AsyncMock()
    await sponsor_view.on_user_select(interaction)
    assert sponsor_view.selected_user == "222"


async def test_builder_update_embed_with_data(admin_command_info):
    view = _builder(admin_command_info)
    view.last_action = "done"
    view.giveaway_data["sponsor"] = str(admin_command_info.user.id)
    view.giveaway_data["price"] = "5€"
    view.giveaway_data["message"] = "hi"
    view.giveaway_data["new_message_requirement"] = 1
    view.giveaway_data["day_requirement"] = 2
    view.giveaway_data["role_requirement"] = [str(admin_command_info.guild.id)]
    view.giveaway_data["voice_requirement"] = 10
    ch = make_text_channel(guild=admin_command_info.guild)
    admin_command_info.guild.get_channel = MagicMock(return_value=ch)
    view.giveaway_data["channel_requirements"] = {str(ch.id): 3}
    await view.update_embed()
    view.generator_message.edit.assert_awaited_once()


@patch("commands.giveaway.start.sendGiveaway", new_callable=AsyncMock)
@patch("commands.giveaway.start.giveaway_service")
async def test_builder_confirm_creates_giveaway(mock_service, mock_send, admin_command_info):
    mock_service.create = AsyncMock(return_value="gw-1")
    view = _builder(admin_command_info)
    view.giveaway_data["description"] = "desc"
    interaction = make_view_interaction(user=admin_command_info.user)
    interaction.response.edit_message = AsyncMock()
    with patch("commands.giveaway.start.utility.relativeTimeStrToDate") as rel:
        rel.return_value = datetime.datetime.now() - datetime.timedelta(hours=1)
        await view.confirm(interaction, _button("confirm"))
    mock_service.create.assert_awaited_once()
    mock_send.assert_awaited_once()


async def test_start_time_modal_submit(admin_command_info):
    view = _builder(admin_command_info)
    modal = StartTimeModal(view, admin_command_info, "t", "d")
    modal.children = [MagicMock(value="1h")]
    interaction = make_view_interaction(user=admin_command_info.user)
    interaction.response.edit_message = AsyncMock()
    await modal.on_submit(interaction)
    assert view.giveaway_data["start_time"] == "1h"


async def test_day_requirement_modal_submit(admin_command_info):
    view = _builder(admin_command_info)
    modal = DayRequirementModal(view, admin_command_info, "t", "d")
    modal.children = [MagicMock(value="7")]
    interaction = make_view_interaction(user=admin_command_info.user)
    interaction.response.edit_message = AsyncMock()
    await modal.on_submit(interaction)
    assert view.giveaway_data["day_requirement"] == 7


async def test_voice_requirement_modal_submit(admin_command_info):
    view = _builder(admin_command_info)
    modal = VoiceRequirementModal(view, admin_command_info, "t", "d")
    modal.children = [MagicMock(value="30")]
    interaction = make_view_interaction(user=admin_command_info.user)
    interaction.response.edit_message = AsyncMock()
    await modal.on_submit(interaction)
    assert view.giveaway_data["voice_requirement"] == 30


async def test_modal_interaction_check_denied(admin_command_info):
    view = _builder(admin_command_info)
    modal = EndTimeModal(view, admin_command_info, "t", "d")
    interaction = make_view_interaction(user=MagicMock(id=999))
    ok = await modal.interaction_check(interaction)
    assert ok is False


async def test_modal_on_timeout(admin_command_info):
    view = _builder(admin_command_info)
    modal = ChangeWinnersModal(view, admin_command_info, "t", "d")
    await modal.on_timeout()
    view.generator_message.edit.assert_awaited()


async def test_giveaway_builder_button_callback(admin_command_info):
    view = _builder(admin_command_info)
    btn = GiveawayBuilderButton(label="x", custom_id="end_time", style=MagicMock())
    btn.view = view
    interaction = make_view_interaction(user=admin_command_info.user)
    with patch.object(view, "end_time", new_callable=AsyncMock) as mock_handler:
        await btn.callback(interaction)
        mock_handler.assert_awaited_once()


async def test_role_requirement_view_confirm(admin_command_info):
    view = _builder(admin_command_info)
    role_view = __import__("commands.giveaway.start", fromlist=["RoleRequirementView"]).RoleRequirementView(
        view, admin_command_info, "t", "d"
    )
    role_view.roles = ["123"]
    interaction = make_view_interaction(user=admin_command_info.user)
    interaction.response.edit_message = AsyncMock()
    await role_view.confirm(interaction)
    assert view.giveaway_data["role_requirement"] == ["123"]


async def test_role_requirement_view_submit(admin_command_info):
    view = _builder(admin_command_info)
    from commands.giveaway.start import RoleRequirementView

    role_view = RoleRequirementView(view, admin_command_info, "t", "d")
    interaction = make_view_interaction(user=admin_command_info.user)
    interaction.data = {"values": ["456"]}
    interaction.response.edit_message = AsyncMock()
    await role_view.submit(interaction)
    assert role_view.roles == ["456"]


async def test_custom_name_modal_submit(admin_command_info):
    view = _builder(admin_command_info)
    modal = CustomNameModal(view, admin_command_info, "t", "d")
    modal.children = [MagicMock(value="Winner")]
    interaction = make_view_interaction(user=admin_command_info.user)
    interaction.response.edit_message = AsyncMock()
    await modal.on_submit(interaction)
    assert view.giveaway_data["custom_name"] == "Winner"


async def test_toggle_button(admin_command_info):
    view = _builder(admin_command_info)
    interaction = make_view_interaction(user=admin_command_info.user)
    interaction.response.edit_message = AsyncMock()
    await view.toggle_button(interaction, _button("toggle_button"))
    assert view.giveaway_data["with_button"] is False


async def test_sponsor_view_interaction_check_ok(admin_command_info):
    view = _builder(admin_command_info)
    sponsor_view = SponsorView(admin_command_info, view)
    interaction = make_view_interaction(user=admin_command_info.user)
    assert await sponsor_view.interaction_check(interaction) is True


async def test_sponsor_view_on_timeout(admin_command_info):
    view = _builder(admin_command_info)
    sponsor_view = SponsorView(admin_command_info, view)
    await sponsor_view.on_timeout()
    view.generator_message.edit.assert_awaited()


async def test_custom_name_modal_interaction_check_ok(admin_command_info):
    view = _builder(admin_command_info)
    modal = CustomNameModal(view, admin_command_info, "t", "d")
    interaction = make_view_interaction(user=admin_command_info.user)
    assert await modal.interaction_check(interaction) is True
