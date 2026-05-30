from unittest.mock import AsyncMock, MagicMock

import pytest

from commands.admin.embedcreator import create_embed
from tests.helpers.discord import make_text_channel
from tests.integration.commands.admin.conftest import make_view_interaction

pytestmark = pytest.mark.asyncio


async def _make_view(admin_command_info):
    channel = make_text_channel(guild=admin_command_info.guild)
    admin_command_info.reply = AsyncMock(return_value=MagicMock())
    await create_embed(admin_command_info, channel=channel, title="Test")
    return admin_command_info.reply.await_args.kwargs["view"], channel


async def test_create_embed_missing_user_permission(restricted_command_info):
    channel = make_text_channel(guild=restricted_command_info.guild)
    await create_embed(restricted_command_info, channel=channel, title="test")
    restricted_command_info.reply.assert_awaited_once()


async def test_create_embed_success(admin_command_info):
    view, channel = await _make_view(admin_command_info)
    assert view is not None
    assert view.target_channel == channel


async def test_create_embed_view_unauthorized_user(admin_command_info):
    view, _ = await _make_view(admin_command_info)
    other_user = MagicMock()
    other_user.id = 999999999
    interaction = make_view_interaction(user=other_user)
    result = await view.interaction_check(interaction)
    assert result is False


async def test_create_embed_add_field_max_reached(admin_command_info):
    view, _ = await _make_view(admin_command_info)
    view.field_count = 25
    interaction = make_view_interaction(user=admin_command_info.user)
    await view.add_field(interaction, MagicMock())
    interaction.response.send_message.assert_awaited_once()


async def test_create_embed_add_field_modal(admin_command_info):
    view, _ = await _make_view(admin_command_info)
    interaction = make_view_interaction(user=admin_command_info.user)
    await view.add_field(interaction, MagicMock())
    interaction.response.send_modal.assert_awaited_once()


async def test_create_embed_no_fields_to_edit(admin_command_info):
    view, _ = await _make_view(admin_command_info)
    interaction = make_view_interaction(user=admin_command_info.user)
    await view.edit_field(interaction, MagicMock())
    interaction.response.send_message.assert_awaited_once()


async def test_create_embed_no_fields_to_remove(admin_command_info):
    view, _ = await _make_view(admin_command_info)
    interaction = make_view_interaction(user=admin_command_info.user)
    await view.remove_field(interaction, MagicMock())
    interaction.response.send_message.assert_awaited_once()


async def test_create_embed_preview(admin_command_info):
    view, _ = await _make_view(admin_command_info)
    interaction = make_view_interaction(user=admin_command_info.user)
    interaction.channel = admin_command_info.channel
    interaction.channel.send = AsyncMock(return_value=MagicMock())
    await view.preview(interaction, MagicMock())
    interaction.response.send_message.assert_awaited_once()


async def test_create_embed_preview_deletes_existing(admin_command_info):
    view, _ = await _make_view(admin_command_info)
    old_preview = MagicMock()
    old_preview.delete = AsyncMock()
    view.preview_message = old_preview
    interaction = make_view_interaction(user=admin_command_info.user)
    interaction.channel = admin_command_info.channel
    interaction.channel.send = AsyncMock(return_value=MagicMock())
    await view.preview(interaction, MagicMock())
    old_preview.delete.assert_awaited_once()


async def test_create_embed_send(admin_command_info):
    view, channel = await _make_view(admin_command_info)
    interaction = make_view_interaction(user=admin_command_info.user)
    await view.send(interaction, MagicMock())
    channel.send.assert_awaited_once()


async def test_create_embed_field_modal_submit(admin_command_info):
    view, _ = await _make_view(admin_command_info)
    interaction = make_view_interaction(user=admin_command_info.user)
    await view.add_field(interaction, MagicMock())
    modal = interaction.response.send_modal.await_args.args[0]
    modal.name.value = "Field"
    modal.value.value = "Value"
    modal.inline.value = "y"
    await modal.on_submit(interaction)
    assert view.field_count == 1


async def test_create_embed_field_modal_inline_true(admin_command_info):
    view, _ = await _make_view(admin_command_info)
    interaction = make_view_interaction(user=admin_command_info.user)
    await view.add_field(interaction, MagicMock())
    modal = interaction.response.send_modal.await_args.args[0]
    modal.name.value = "F"
    modal.value.value = "V"
    modal.inline.value = "true"
    await modal.on_submit(interaction)
    assert view.field_count == 1


async def test_create_embed_footer_modal(admin_command_info):
    view, _ = await _make_view(admin_command_info)
    interaction = make_view_interaction(user=admin_command_info.user)
    await view.set_footer(interaction, MagicMock())
    modal = interaction.response.send_modal.await_args.args[0]
    modal.text.value = "footer"
    modal.icon_url.value = "https://example.com/icon.png"
    await modal.on_submit(interaction)
    interaction.response.send_message.assert_awaited_once()


async def test_create_embed_footer_modal_no_icon(admin_command_info):
    view, _ = await _make_view(admin_command_info)
    interaction = make_view_interaction(user=admin_command_info.user)
    await view.set_footer(interaction, MagicMock())
    modal = interaction.response.send_modal.await_args.args[0]
    modal.text.value = "footer"
    modal.icon_url.value = ""
    await modal.on_submit(interaction)
    interaction.response.send_message.assert_awaited_once()


async def test_create_embed_color_modal_valid(admin_command_info):
    view, _ = await _make_view(admin_command_info)
    interaction = make_view_interaction(user=admin_command_info.user)
    await view.set_color(interaction, MagicMock())
    modal = interaction.response.send_modal.await_args.args[0]
    modal.color.value = "#FF0000"
    await modal.on_submit(interaction)
    interaction.response.send_message.assert_awaited_once()


async def test_create_embed_color_modal_invalid(admin_command_info):
    view, _ = await _make_view(admin_command_info)
    interaction = make_view_interaction(user=admin_command_info.user)
    await view.set_color(interaction, MagicMock())
    modal = interaction.response.send_modal.await_args.args[0]
    modal.color.value = "invalid"
    await modal.on_submit(interaction)
    interaction.response.send_message.assert_awaited_once()


async def test_create_embed_image_modal(admin_command_info):
    view, _ = await _make_view(admin_command_info)
    interaction = make_view_interaction(user=admin_command_info.user)
    await view.set_image(interaction, MagicMock())
    modal = interaction.response.send_modal.await_args.args[0]
    modal.image_url.value = "https://example.com/image.png"
    await modal.on_submit(interaction)
    interaction.response.send_message.assert_awaited_once()


async def test_create_embed_thumbnail_modal(admin_command_info):
    view, _ = await _make_view(admin_command_info)
    interaction = make_view_interaction(user=admin_command_info.user)
    await view.set_thumbnail(interaction, MagicMock())
    modal = interaction.response.send_modal.await_args.args[0]
    modal.thumbnail_url.value = "https://example.com/thumb.png"
    await modal.on_submit(interaction)
    interaction.response.send_message.assert_awaited_once()


async def test_create_embed_set_description_timeout(admin_command_info):
    view, _ = await _make_view(admin_command_info)
    admin_command_info.client.wait_for = AsyncMock(side_effect=TimeoutError())
    interaction = make_view_interaction(user=admin_command_info.user)
    interaction.channel = admin_command_info.channel
    await view.set_description(interaction, MagicMock())
    interaction.followup.send_message.assert_awaited_once()


async def test_create_embed_set_description_success(admin_command_info):
    view, _ = await _make_view(admin_command_info)
    msg = MagicMock()
    msg.content = "New description"
    msg.delete = AsyncMock()
    admin_command_info.client.wait_for = AsyncMock(return_value=msg)
    interaction = make_view_interaction(user=admin_command_info.user)
    interaction.channel = admin_command_info.channel
    interaction.user = admin_command_info.user
    await view.set_description(interaction, MagicMock())
    msg.delete.assert_awaited_once()


async def test_create_embed_edit_field_modal(admin_command_info):
    view, _ = await _make_view(admin_command_info)
    view.embed.add_field(name="Old", value="Val", inline=False)
    view.field_count = 1
    interaction = make_view_interaction(user=admin_command_info.user)
    await view.edit_field(interaction, MagicMock())
    modal = interaction.response.send_modal.await_args.args[0]
    modal.field_index.values = ["0"]
    modal.name.value = "New"
    modal.value.value = "Updated"
    modal.inline.value = "n"
    await modal.on_submit(interaction)
    interaction.response.send_message.assert_awaited_once()


async def test_create_embed_remove_field_modal(admin_command_info):
    view, _ = await _make_view(admin_command_info)
    view.embed.add_field(name="Old", value="Val", inline=False)
    view.field_count = 1
    interaction = make_view_interaction(user=admin_command_info.user)
    await view.remove_field(interaction, MagicMock())
    modal = interaction.response.send_modal.await_args.args[0]
    modal.field_index.values = ["0"]
    await modal.on_submit(interaction)
    assert view.field_count == 0


async def test_create_embed_on_timeout(admin_command_info):
    view, _ = await _make_view(admin_command_info)
    msg = MagicMock()
    msg.edit = AsyncMock()
    view.message = msg
    await view.on_timeout()
    msg.edit.assert_awaited_once()
