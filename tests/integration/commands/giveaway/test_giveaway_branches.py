from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from commands.giveaway.edit_giveaway import edit_giveaway
from commands.giveaway.end_giveaway import end_giveaway
from commands.giveaway.reroll_giveaway import reroll_giveaway
from commands.giveaway.start import GiveawayBuilder, start_giveaway
from commands.giveaway.utility import sendGiveaway
from tests.helpers.discord import make_guild, make_permissions, make_text_channel
from tests.integration.commands.admin.conftest import make_view_interaction

pytestmark = pytest.mark.asyncio

_DEFAULT_GUILD_ID = str(make_guild().id)


def _giveaway(**kwargs):
    g = MagicMock()
    g.guild_id = kwargs.get("guild_id", _DEFAULT_GUILD_ID)
    g.ended = kwargs.get("ended", False)
    g.started = kwargs.get("started", True)
    g.channel_id = kwargs.get("channel_id", "444444444")
    g.message_id = kwargs.get("message_id", "555555555")
    return g


async def test_start_giveaway_no_permission(restricted_command_info):
    await start_giveaway(restricted_command_info, "Prize", make_text_channel())
    restricted_command_info.reply.assert_awaited_once()


@patch("commands.giveaway.start.GiveawayBuilder")
async def test_start_giveaway_launches_builder(mock_cls, admin_command_info):
    view = MagicMock()
    view.update_embed = AsyncMock()
    mock_cls.return_value = view
    msg = MagicMock()
    admin_command_info.reply = AsyncMock(return_value=msg)
    channel = make_text_channel(guild=admin_command_info.guild)
    await start_giveaway(admin_command_info, "Prize", channel)
    mock_cls.assert_called_once()
    view.update_embed.assert_awaited()


@patch("commands.giveaway.end_giveaway.endGiveaway", new_callable=AsyncMock)
@patch("commands.giveaway.end_giveaway.giveaway_service")
async def test_end_giveaway_success(mock_service, mock_end, admin_command_info):
    admin_command_info.permissions = make_permissions(manage_guild=True)
    mock_service.get = AsyncMock(return_value=_giveaway())
    await end_giveaway(admin_command_info, 1)
    mock_end.assert_awaited_once()
    admin_command_info.reply.assert_awaited_once()


async def test_end_giveaway_missing_permission(restricted_command_info):
    restricted_command_info.permissions = make_permissions(manage_guild=False)
    await end_giveaway(restricted_command_info, 1)
    restricted_command_info.reply.assert_awaited_once()


@patch("commands.giveaway.end_giveaway.giveaway_service")
async def test_end_giveaway_not_found(mock_service, admin_command_info):
    admin_command_info.permissions = make_permissions(manage_guild=True)
    mock_service.get = AsyncMock(return_value=None)
    await end_giveaway(admin_command_info, 1)
    admin_command_info.reply.assert_awaited_once()


@patch("commands.giveaway.end_giveaway.giveaway_service")
async def test_end_giveaway_wrong_guild(mock_service, admin_command_info):
    admin_command_info.permissions = make_permissions(manage_guild=True)
    mock_service.get = AsyncMock(return_value=_giveaway(guild_id="999999999"))
    await end_giveaway(admin_command_info, 1)
    admin_command_info.reply.assert_awaited_once()


@patch("commands.giveaway.end_giveaway.giveaway_service")
async def test_end_giveaway_already_ended(mock_service, admin_command_info):
    admin_command_info.permissions = make_permissions(manage_guild=True)
    mock_service.get = AsyncMock(return_value=_giveaway(ended=True))
    await end_giveaway(admin_command_info, 1)
    admin_command_info.reply.assert_awaited_once()


@patch("commands.giveaway.end_giveaway.giveaway_service")
async def test_end_giveaway_not_started(mock_service, admin_command_info):
    admin_command_info.permissions = make_permissions(manage_guild=True)
    mock_service.get = AsyncMock(return_value=_giveaway(started=False))
    mock_service.delete = AsyncMock()
    await end_giveaway(admin_command_info, 1)
    mock_service.delete.assert_awaited_once()
    admin_command_info.reply.assert_awaited_once()


@patch("commands.giveaway.reroll_giveaway.perform_reroll", new_callable=AsyncMock)
@patch("commands.giveaway.reroll_giveaway.giveaway_service")
async def test_reroll_giveaway_single_winner(mock_service, mock_reroll, admin_command_info):
    admin_command_info.permissions = make_permissions(manage_guild=True)
    g = _giveaway(ended=True)
    g.winners = 1
    mock_service.get = AsyncMock(return_value=g)
    await reroll_giveaway(admin_command_info, 1)
    mock_reroll.assert_awaited_once()


async def test_reroll_giveaway_missing_permission(restricted_command_info):
    restricted_command_info.permissions = make_permissions(manage_guild=False)
    await reroll_giveaway(restricted_command_info, 1)
    restricted_command_info.reply.assert_awaited_once()


@patch("commands.giveaway.reroll_giveaway.giveaway_service")
async def test_reroll_giveaway_not_found(mock_service, admin_command_info):
    admin_command_info.permissions = make_permissions(manage_guild=True)
    mock_service.get = AsyncMock(return_value=None)
    await reroll_giveaway(admin_command_info, 1)
    admin_command_info.reply.assert_awaited_once()


@patch("commands.giveaway.reroll_giveaway.giveaway_service")
async def test_reroll_giveaway_not_ended(mock_service, admin_command_info):
    admin_command_info.permissions = make_permissions(manage_guild=True)
    mock_service.get = AsyncMock(return_value=_giveaway(ended=False))
    await reroll_giveaway(admin_command_info, 1)
    admin_command_info.reply.assert_awaited_once()


@patch("commands.giveaway.edit_giveaway.GiveawayEditor")
async def test_edit_giveaway_success(mock_editor_cls, admin_command_info):
    editor = MagicMock()
    editor.load_giveaway_data = AsyncMock(return_value=True)
    editor.update_embed = AsyncMock()
    mock_editor_cls.return_value = editor
    admin_command_info.reply = AsyncMock(return_value=MagicMock())
    await edit_giveaway(admin_command_info, 1)
    admin_command_info.reply.assert_awaited_once()
    editor.update_embed.assert_awaited_once()


@patch("commands.giveaway.edit_giveaway.GiveawayEditor")
async def test_edit_giveaway_not_found(mock_editor_cls, admin_command_info):
    editor = MagicMock()
    editor.load_giveaway_data = AsyncMock(return_value=False)
    mock_editor_cls.return_value = editor
    await edit_giveaway(admin_command_info, 1)
    admin_command_info.reply.assert_awaited_once()


async def test_giveaway_builder_update_embed(admin_command_info):
    channel = make_text_channel(guild=admin_command_info.guild)
    view = GiveawayBuilder(admin_command_info, "Title", channel)
    view.generator_message = MagicMock()
    view.generator_message.edit = AsyncMock()
    await view.update_embed()
    view.generator_message.edit.assert_awaited_once()


async def test_giveaway_builder_unauthorized(admin_command_info):
    channel = make_text_channel(guild=admin_command_info.guild)
    view = GiveawayBuilder(admin_command_info, "Title", channel)
    interaction = make_view_interaction(user=MagicMock(id=999))
    result = await view.interaction_check(interaction)
    assert result is False


@patch("commands.giveaway.start.generateGiveawayEmbed", new_callable=AsyncMock)
async def test_giveaway_builder_preview(mock_embed, admin_command_info):
    channel = make_text_channel(guild=admin_command_info.guild)
    view = GiveawayBuilder(admin_command_info, "Title", channel)
    mock_embed.return_value = MagicMock()
    interaction = make_view_interaction(user=admin_command_info.user)
    button = MagicMock(custom_id="preview")
    await view.button_callback(interaction, button)
    interaction.response.send_message.assert_awaited_once()


@patch("commands.giveaway.start.ChangeWinnersModal")
async def test_giveaway_builder_change_winners(mock_modal, admin_command_info):
    channel = make_text_channel(guild=admin_command_info.guild)
    view = GiveawayBuilder(admin_command_info, "Title", channel)
    interaction = make_view_interaction(user=admin_command_info.user)
    button = MagicMock(custom_id="change_winners")
    await view.button_callback(interaction, button)
    interaction.response.send_modal.assert_awaited_once()


@patch("commands.giveaway.utility.giveaway_service")
async def test_send_giveaway(mock_service, admin_command_info):
    giveaway = MagicMock(
        guild_id=str(admin_command_info.guild.id),
        channel_id="444444444",
        message_id=None,
        message="Giveaway!",
    )
    mock_service.get = AsyncMock(return_value=giveaway)
    mock_service.get_role_requirements = AsyncMock(return_value=[])
    mock_service.get_channel_requirements = AsyncMock(return_value=[])
    mock_service.get_participants = AsyncMock(return_value=[])
    mock_service.mark_sent = AsyncMock()
    channel = make_text_channel(guild=admin_command_info.guild)
    admin_command_info.client.get_guild = MagicMock(return_value=admin_command_info.guild)
    admin_command_info.guild.get_channel = MagicMock(return_value=channel)
    channel.send = AsyncMock(return_value=MagicMock(id=123))
    with patch("commands.giveaway.utility.generateGiveawayEmbed", new_callable=AsyncMock, return_value=MagicMock()):
        await sendGiveaway(1, admin_command_info.client)
    mock_service.mark_sent.assert_awaited_once()


async def test_edit_giveaway_missing_permission(restricted_command_info):
    await edit_giveaway(restricted_command_info, 1)
    restricted_command_info.reply.assert_awaited_once()
