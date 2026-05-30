from __future__ import annotations

import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from commands.giveaway.edit_giveaway import GiveawayEditor, edit_giveaway
from tests.helpers.discord import make_permissions, make_text_channel
from tests.integration.commands.admin.conftest import make_view_interaction

pytestmark = pytest.mark.asyncio


def _giveaway_model(channel_id: str = "444444444"):
    g = MagicMock()
    g.title = "Prize"
    g.description = "Desc"
    g.winners = 2
    g.with_button = True
    g.custom_name = None
    g.sponsor = None
    g.price = "10"
    g.message = "Join!"
    g.end_time = datetime.datetime.now() + datetime.timedelta(days=1)
    g.start_time = datetime.datetime.now()
    g.new_message_requirement = 5
    g.day_requirement = 7
    g.voice_requirement = 30
    g.channel_id = channel_id
    return g


def _editor(admin_command_info, data: dict | None = None) -> GiveawayEditor:
    editor = GiveawayEditor(admin_command_info, 1)
    channel = make_text_channel(guild=admin_command_info.guild)
    editor.giveaway_data = data or {
        "title": "Prize",
        "description": "Desc",
        "winners": 2,
        "with_button": True,
        "custom_name": None,
        "sponsor": str(admin_command_info.user.id),
        "price": "10",
        "message": "Join",
        "end_time": "24h",
        "start_time": "0s",
        "new_message_requirement": 5,
        "day_requirement": 7,
        "role_requirement": [],
        "voice_requirement": 30,
        "channel_requirements": {},
        "target_channel": channel,
    }
    editor.generator_message = MagicMock()
    editor.generator_message.edit = AsyncMock()
    return editor


@patch("commands.giveaway.edit_giveaway.giveaway_service.get_channel_requirements", new_callable=AsyncMock, return_value={})
@patch("commands.giveaway.edit_giveaway.giveaway_service.get_role_requirements", new_callable=AsyncMock, return_value=[])
@patch("commands.giveaway.edit_giveaway.giveaway_service.get", new_callable=AsyncMock)
async def test_load_giveaway_data(mock_get, mock_roles, mock_channels, admin_command_info):
    ch = make_text_channel(guild=admin_command_info.guild)
    admin_command_info.guild.get_channel = MagicMock(return_value=ch)
    mock_get.return_value = _giveaway_model(str(ch.id))
    editor = GiveawayEditor(admin_command_info, 1)
    assert await editor.load_giveaway_data() is True
    assert editor.giveaway_data["title"] == "Prize"


@patch("commands.giveaway.edit_giveaway.giveaway_service.get", new_callable=AsyncMock, return_value=None)
async def test_load_giveaway_not_found(mock_get, admin_command_info):
    editor = GiveawayEditor(admin_command_info, 99)
    assert await editor.load_giveaway_data() is None


async def test_editor_update_embed(admin_command_info):
    editor = _editor(admin_command_info)
    editor.last_action = "updated"
    await editor.update_embed()
    editor.generator_message.edit.assert_awaited_once()


async def test_editor_interaction_check_denied(admin_command_info):
    editor = _editor(admin_command_info)
    interaction = make_view_interaction(user=MagicMock(id=999))
    assert await editor.interaction_check(interaction) is False


@pytest.mark.parametrize(
    "custom_id",
    [
        "change_winners",
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
async def test_editor_button_callbacks(custom_id, admin_command_info):
    editor = _editor(admin_command_info)
    interaction = make_view_interaction(user=admin_command_info.user)
    await editor.button_callback(interaction, MagicMock(custom_id=custom_id))
    assert (
        interaction.response.send_modal.await_count
        + interaction.response.edit_message.await_count
        + interaction.response.send_message.await_count
        >= 1
    )


@patch("commands.giveaway.edit_giveaway.generateGiveawayEmbed", new_callable=AsyncMock, return_value=MagicMock())
@patch("models.GiveawayModel")
async def test_editor_preview(mock_model, mock_embed, admin_command_info):
    mock_model.return_value = MagicMock()
    editor = _editor(admin_command_info)
    interaction = make_view_interaction(user=admin_command_info.user)
    await editor.preview(interaction, MagicMock())
    interaction.response.send_message.assert_awaited_once()


@patch("commands.giveaway.edit_giveaway.updateGiveawayMessage", new_callable=AsyncMock)
@patch("commands.giveaway.edit_giveaway.giveaway_service.update", new_callable=AsyncMock)
async def test_editor_confirm(mock_update, mock_msg, admin_command_info):
    editor = _editor(admin_command_info)
    interaction = make_view_interaction(user=admin_command_info.user)
    interaction.response.edit_message = AsyncMock()
    await editor.confirm(interaction, MagicMock())
    mock_update.assert_awaited_once()
    mock_msg.assert_awaited_once()


async def test_editor_toggle_button(admin_command_info):
    editor = _editor(admin_command_info)
    interaction = make_view_interaction(user=admin_command_info.user)
    interaction.response.edit_message = AsyncMock()
    await editor.toggle_button(interaction, MagicMock())
    assert editor.giveaway_data["with_button"] is False


async def test_editor_change_description_timeout(admin_command_info):
    editor = _editor(admin_command_info)
    interaction = make_view_interaction(user=admin_command_info.user)
    admin_command_info.client.wait_for = AsyncMock(side_effect=TimeoutError())
    await GiveawayEditor.change_description(editor, interaction, MagicMock())
    editor.generator_message.edit.assert_awaited()


async def test_editor_message_too_long(admin_command_info):
    editor = _editor(admin_command_info)
    interaction = make_view_interaction(user=admin_command_info.user)
    msg = MagicMock()
    msg.content = "x" * 200
    msg.author = interaction.user
    msg.channel = interaction.channel
    msg.delete = AsyncMock()
    admin_command_info.client.wait_for = AsyncMock(return_value=msg)
    await GiveawayEditor.message(editor, interaction, MagicMock())
    msg.delete.assert_awaited_once()


async def test_editor_remove_channel_requirement(admin_command_info):
    editor = _editor(admin_command_info)
    ch = make_text_channel(guild=admin_command_info.guild)
    admin_command_info.guild.get_channel = MagicMock(return_value=ch)
    editor.giveaway_data["channel_requirements"] = {str(ch.id): 2}
    editor.update_buttons()
    interaction = make_view_interaction(user=admin_command_info.user)
    await editor.remove_channel_requirement(interaction, MagicMock())
    interaction.response.edit_message.assert_awaited_once()


@patch("commands.giveaway.edit_giveaway.GiveawayEditor")
async def test_edit_giveaway_entry(mock_cls, admin_command_info):
    editor = MagicMock()
    editor.load_giveaway_data = AsyncMock(return_value=True)
    editor.update_embed = AsyncMock()
    mock_cls.return_value = editor
    admin_command_info.reply = AsyncMock(return_value=MagicMock())
    admin_command_info.permissions = make_permissions(manage_guild=True)
    await edit_giveaway(admin_command_info, 1)
    editor.update_embed.assert_awaited_once()


async def test_editor_interaction_check_unauthorized(admin_command_info):
    editor = _editor(admin_command_info)
    interaction = make_view_interaction(user=MagicMock(id=999))
    ok = await editor.interaction_check(interaction)
    assert ok is False
    interaction.response.send_message.assert_awaited_once()


async def test_editor_start_time_button(admin_command_info):
    editor = _editor(admin_command_info)
    interaction = make_view_interaction(user=admin_command_info.user)
    await editor.start_time(interaction, MagicMock())
    interaction.response.send_modal.assert_awaited_once()


async def test_editor_change_description_success(admin_command_info):
    editor = _editor(admin_command_info)
    interaction = make_view_interaction(user=admin_command_info.user)
    interaction.response.edit_message = AsyncMock()
    msg = MagicMock()
    msg.content = "New desc"
    msg.author = interaction.user
    msg.channel = interaction.channel
    msg.delete = AsyncMock()
    admin_command_info.client.wait_for = AsyncMock(return_value=msg)
    await GiveawayEditor.change_description(editor, interaction, MagicMock())
    assert editor.giveaway_data["description"] == "New desc"


async def test_editor_price_success(admin_command_info):
    editor = _editor(admin_command_info)
    interaction = make_view_interaction(user=admin_command_info.user)
    interaction.response.edit_message = AsyncMock()
    msg = MagicMock()
    msg.content = "99€"
    msg.author = interaction.user
    msg.channel = interaction.channel
    msg.delete = AsyncMock()
    admin_command_info.client.wait_for = AsyncMock(return_value=msg)
    await GiveawayEditor.price(editor, interaction, MagicMock())
    assert editor.giveaway_data["price"] == "99€"


async def test_editor_message_success(admin_command_info):
    editor = _editor(admin_command_info)
    interaction = make_view_interaction(user=admin_command_info.user)
    interaction.response.edit_message = AsyncMock()
    msg = MagicMock()
    msg.content = "Join now"
    msg.author = interaction.user
    msg.channel = interaction.channel
    msg.delete = AsyncMock()
    admin_command_info.client.wait_for = AsyncMock(return_value=msg)
    await GiveawayEditor.message(editor, interaction, MagicMock())
    assert editor.giveaway_data["message"] == "Join now"
