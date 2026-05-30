import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from commands.utility.afk import afk, checkIfAfkHasToBeRemoved, checkIfMentionsAreAfk
from commands.utility.feedback import feedback
from commands.utility.help import help
from commands.utility.removescheduled import remove_scheduled_message
from tests.helpers.discord import make_interaction, make_message, make_target_member


pytestmark = pytest.mark.asyncio


class _StubView:
    def __init__(self, *args, **kwargs) -> None:
        pass

    def add_item(self, item) -> None:
        pass


class _StubSelect(_StubView):
    @classmethod
    def generate_options(cls, client):
        return []


@pytest.fixture(autouse=True)
def stub_help_discord_ui():
    import discord

    old_view, old_select = discord.ui.View, discord.ui.Select
    discord.ui.View = _StubView
    discord.ui.Select = _StubSelect
    yield
    discord.ui.View = old_view
    discord.ui.Select = old_select


@patch("commands.utility.afk.check_if_opted_out", new_callable=AsyncMock, return_value=True)
async def test_afk_opted_out(mock_opt, admin_command_info):
    await afk(admin_command_info, "brb")
    admin_command_info.reply.assert_awaited_once()


@patch("commands.utility.afk.check_if_opted_out", new_callable=AsyncMock, return_value=False)
@patch("commands.utility.afk.afk_service")
async def test_afk_already_afk(mock_service, mock_opt, admin_command_info):
    mock_service.is_afk = AsyncMock(return_value=True)
    await afk(admin_command_info, "brb")
    admin_command_info.reply.assert_awaited_once()


@patch("commands.utility.afk.check_if_opted_out", new_callable=AsyncMock, return_value=False)
@patch("commands.utility.afk.afk_service")
async def test_afk_success(mock_service, mock_opt, admin_command_info):
    mock_service.is_afk = AsyncMock(return_value=False)
    mock_service.set_afk = AsyncMock()
    await afk(admin_command_info, "brb")
    mock_service.set_afk.assert_awaited_once()
    admin_command_info.reply.assert_awaited_once()


@patch("commands.utility.afk.check_if_opted_out", new_callable=AsyncMock, return_value=False)
@patch("commands.utility.afk.afk_service")
async def test_afk_removed_no_mentions(mock_service, mock_opt, admin_command_info):
    mock_service.is_afk = AsyncMock(return_value=True)
    mock_service.clear_and_notify = AsyncMock(return_value=[])
    message = make_message(author=admin_command_info.user, guild=admin_command_info.guild)
    message.channel.send = AsyncMock()
    await checkIfAfkHasToBeRemoved(message)
    message.channel.send.assert_awaited_once()


@patch("commands.utility.afk.check_if_opted_out", new_callable=AsyncMock, return_value=False)
@patch("commands.utility.afk.afk_service")
async def test_afk_removed_with_mentions(mock_service, mock_opt, admin_command_info):
    mock_service.is_afk = AsyncMock(return_value=True)
    mention = MagicMock(channel_id=1, message_id=2)
    mock_service.clear_and_notify = AsyncMock(return_value=[mention])
    message = make_message(author=admin_command_info.user, guild=admin_command_info.guild)
    message.channel.send = AsyncMock()
    await checkIfAfkHasToBeRemoved(message)
    message.channel.send.assert_awaited_once()


@patch("commands.utility.afk.afk_service")
async def test_mentions_are_afk(mock_service, admin_command_info):
    target = make_target_member()
    mock_service.is_afk = AsyncMock(return_value=True)
    mock_service.get_reason = AsyncMock(return_value="sleeping")
    mock_service.track_mention = AsyncMock()
    message = make_message(guild=admin_command_info.guild)
    message.mentions = [target]
    message.channel.send = AsyncMock()
    with patch("commands.utility.afk.check_if_opted_out", new_callable=AsyncMock, return_value=False):
        await checkIfMentionsAreAfk(message)
    message.channel.send.assert_awaited_once()


async def test_help_command(admin_command_info):
    ctx = make_interaction(user=admin_command_info.user)
    admin_command_info.client.tree = MagicMock()
    admin_command_info.client.tree.walk_commands = MagicMock(return_value=[])
    await help(admin_command_info, ctx)
    admin_command_info.reply.assert_awaited_once()


@patch("commands.utility.feedback.feedbackIsBlocked", new_callable=AsyncMock, return_value=False)
async def test_feedback_success(mock_blocked, admin_command_info):
    ctx = make_interaction(user=admin_command_info.user)
    ctx.response.send_modal = AsyncMock()
    await feedback(admin_command_info, ctx)
    ctx.response.send_modal.assert_awaited_once()


@patch("commands.utility.feedback.feedbackIsBlocked", new_callable=AsyncMock, return_value=True)
async def test_feedback_blocked(mock_blocked, admin_command_info):
    await feedback(admin_command_info, make_interaction(user=admin_command_info.user))
    admin_command_info.reply.assert_awaited_once()


@patch("commands.utility.removescheduled.ScheduledMessageService")
async def test_remove_scheduled_no_messages(mock_service, admin_command_info):
    mock_service.get_user_messages = AsyncMock(return_value=[])
    await remove_scheduled_message(admin_command_info)
    admin_command_info.reply.assert_awaited_once()


@patch("commands.utility.removescheduled.ScheduledMessageService")
async def test_remove_scheduled_not_found(mock_service, admin_command_info):
    msg = MagicMock(message_id=1)
    mock_service.get_user_messages = AsyncMock(return_value=[msg])
    mock_service.remove = AsyncMock(return_value=False)
    await remove_scheduled_message(admin_command_info, message_id=999)
    admin_command_info.reply.assert_awaited_once()
