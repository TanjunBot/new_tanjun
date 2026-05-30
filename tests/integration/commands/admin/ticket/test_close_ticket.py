from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from commands.admin.ticket.close_ticket import close_ticket, generate_summary_html
from tests.helpers.discord import make_interaction, make_member, make_text_channel

pytestmark = pytest.mark.asyncio


def _make_close_interaction():
    interaction = make_interaction()
    interaction.data = {"custom_id": "ticket_close;1;444444444"}
    interaction.response.defer = AsyncMock()
    interaction.followup.send = AsyncMock()
    interaction.channel = make_text_channel()
    interaction.channel.id = 444444444
    interaction.channel.name = "ticket-user"
    interaction.channel.send = AsyncMock()
    interaction.channel.edit = AsyncMock()
    return interaction


async def test_close_ticket_wrong_custom_id():
    interaction = make_interaction()
    interaction.data = {"custom_id": "other"}
    await close_ticket(interaction)
    interaction.response.defer.assert_not_called()


@patch("commands.admin.ticket.close_ticket.ticket_service")
async def test_close_ticket_config_not_found(mock_service):
    interaction = _make_close_interaction()
    mock_service.get_config = AsyncMock(return_value=None)
    await close_ticket(interaction)
    interaction.response.defer.assert_awaited_once()
    interaction.followup.send.assert_awaited_once()


@patch("commands.admin.ticket.close_ticket.ticket_service")
async def test_close_ticket_not_found(mock_service):
    interaction = _make_close_interaction()
    mock_service.get_config = AsyncMock(return_value=MagicMock())
    mock_service.get_by_config_and_channel = AsyncMock(return_value=None)
    await close_ticket(interaction)
    interaction.followup.send.assert_awaited_once()


@patch("commands.admin.ticket.close_ticket.ticket_service")
async def test_close_ticket_wrong_channel(mock_service):
    interaction = _make_close_interaction()
    mock_service.get_config = AsyncMock(return_value=MagicMock())
    ticket = MagicMock()
    ticket.channel_id = "999999999"
    mock_service.get_by_config_and_channel = AsyncMock(return_value=ticket)
    await close_ticket(interaction)
    interaction.followup.send.assert_awaited_once()


@patch("commands.admin.ticket.close_ticket.ticket_service")
async def test_close_ticket_no_summary_channel(mock_service):
    interaction = _make_close_interaction()
    mock_service.get_config = AsyncMock(return_value=MagicMock(summary_channel_id=None))
    ticket = MagicMock()
    ticket.channel_id = 444444444
    ticket.opener_id = 111111111
    ticket.opened_at = datetime.now(UTC)
    mock_service.get_by_config_and_channel = AsyncMock(return_value=ticket)
    interaction.guild.fetch_member = AsyncMock(return_value=make_member())
    await close_ticket(interaction)
    interaction.channel.send.assert_awaited_once()


@patch(
    "commands.admin.ticket.close_ticket.utility.upload_to_tanjun_logs",
    new_callable=AsyncMock,
    return_value="https://logs.example.com",
)
@patch("commands.admin.ticket.close_ticket.generate_summary_html", new_callable=AsyncMock, return_value="<html></html>")
@patch("commands.admin.ticket.close_ticket.ticket_service")
async def test_close_ticket_with_summary_channel(mock_service, mock_html, mock_upload):
    interaction = _make_close_interaction()
    mock_service.get_config = AsyncMock(return_value=MagicMock(summary_channel_id="555555555"))
    ticket = MagicMock()
    ticket.channel_id = 444444444
    ticket.opener_id = 111111111
    ticket.opened_at = datetime.now(UTC)
    mock_service.get_by_config_and_channel = AsyncMock(return_value=ticket)
    interaction.guild.fetch_member = AsyncMock(return_value=make_member())
    summary_channel = make_text_channel()
    summary_channel.send = AsyncMock()
    interaction.guild.get_channel = MagicMock(return_value=summary_channel)
    thread_channel = make_text_channel()
    thread_channel.id = 444444444
    thread_channel.name = "ticket-user"
    thread_channel.send = AsyncMock()
    thread_channel.edit = AsyncMock()
    interaction.channel = thread_channel
    await close_ticket(interaction)
    summary_channel.send.assert_awaited_once()
    interaction.channel.send.assert_awaited_once()


async def test_generate_summary_html_empty_history():
    channel = make_text_channel()
    channel.guild.preferred_locale = "en-US"

    async def empty_history(*args, **kwargs):
        if False:
            yield

    channel.history = empty_history
    member = make_member()
    result = await generate_summary_html(channel, member, datetime.now(UTC))
    assert "<html" in result.lower()


async def test_generate_summary_html_with_message():
    channel = make_text_channel()
    channel.guild.preferred_locale = "en-US"
    msg = MagicMock()
    msg.content = "Hello world"
    msg.embeds = []
    msg.role_mentions = []
    msg.mentions = []
    msg.channel_mentions = []
    msg.author = make_member()
    msg.author.display_avatar = MagicMock(url="https://example.com/avatar.png")

    async def one_message(*args, **kwargs):
        yield msg

    channel.history = one_message
    member = make_member()
    result = await generate_summary_html(channel, member, datetime.now(UTC))
    assert "Hello world" in result


async def test_generate_summary_html_with_embed_message():
    channel = make_text_channel()
    channel.guild.preferred_locale = "en-US"
    embed = MagicMock()
    embed.color = "#ff0000"
    embed.thumbnail = MagicMock(url="https://example.com/thumb.png")
    embed.title = "Title"
    embed.description = "Desc"
    embed.fields = [MagicMock(name="F", value="V")]
    embed.image = MagicMock(url="https://example.com/img.png")
    embed.footer = MagicMock(text="Footer", icon_url="https://example.com/icon.png")
    msg = MagicMock()
    msg.content = "Hello"
    msg.embeds = [embed]
    msg.role_mentions = []
    msg.mentions = []
    msg.channel_mentions = []
    msg.author = make_member()
    msg.author.display_avatar = MagicMock(url="https://example.com/avatar.png")

    async def one_message(*args, **kwargs):
        yield msg

    channel.history = one_message
    member = make_member()
    result = await generate_summary_html(channel, member, datetime.now(UTC))
    assert "Title" in result
    assert "Footer" in result


async def test_generate_summary_html_with_role_mentions():
    channel = make_text_channel()
    channel.guild.preferred_locale = "en-US"
    role = MagicMock()
    role.id = 555
    role.name = "Mod"
    role.color = "#ff0000"
    role.members = [make_member()]
    role.permissions = MagicMock()
    role.permissions.__iter__ = MagicMock(return_value=iter([("manage_messages", True)]))
    msg = MagicMock()
    msg.content = "Hello @role"
    msg.embeds = []
    msg.role_mentions = [role]
    msg.mentions = []
    msg.channel_mentions = []
    msg.author = make_member()
    msg.author.display_avatar = MagicMock(url="https://example.com/avatar.png")

    async def one_message(*args, **kwargs):
        yield msg

    channel.history = one_message
    result = await generate_summary_html(channel, make_member(), datetime.now(UTC))
    assert "Mod" in result


async def test_generate_summary_html_skips_empty_message():
    channel = make_text_channel()
    channel.guild.preferred_locale = None
    msg = MagicMock()
    msg.content = ""
    msg.embeds = []

    async def one_message(*args, **kwargs):
        yield msg

    channel.history = one_message
    result = await generate_summary_html(channel, make_member(), datetime.now(UTC))
    assert "<html" in result.lower()


@patch("commands.admin.ticket.close_ticket.ticket_service")
async def test_close_ticket_archive_text_channel(mock_service):
    interaction = _make_close_interaction()
    mock_service.get_config = AsyncMock(return_value=MagicMock(summary_channel_id=None))
    ticket = MagicMock()
    ticket.channel_id = 444444444
    ticket.opener_id = 111111111
    ticket.opened_at = datetime.now(UTC)
    mock_service.get_by_config_and_channel = AsyncMock(return_value=ticket)
    interaction.guild.fetch_member = AsyncMock(return_value=make_member())
    interaction.channel.edit = AsyncMock()
    await close_ticket(interaction)
    interaction.channel.edit.assert_awaited_once()
