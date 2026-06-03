from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from extensions.logs import LogsCommands
from models import LogEnableModel
from tests.helpers.discord import make_guild, make_member, make_permissions, make_text_channel
from tests.helpers.extensions import invoke_interaction_command
from tests.helpers.view_state import assert_selection_marker, count_selection_markers

pytestmark = pytest.mark.asyncio

GUILD_ID = "123456789012345678"


def _log_enable() -> LogEnableModel:
    return LogEnableModel(guild_id=GUILD_ID)


def _admin_user():
    user = make_member()
    user.guild_permissions = make_permissions(administrator=True)
    return user


@pytest.fixture
def logs_ui_api_mocks():
    with (
        patch("commands.logs.configure_logs.get_log_enable_api", new=AsyncMock(return_value=_log_enable())),
        patch("commands.logs.configure_logs.set_log_enable_api", new=AsyncMock()),
        patch("commands.logs.set_log_channel.set_log_channel_api", new=AsyncMock()) as set_ch,
        patch("commands.logs.set_log_channel.get_log_channel_api", new=AsyncMock(return_value=None)),
        patch("commands.logs.remove_log_channel.remove_log_channel_api", new=AsyncMock()) as remove_ch,
        patch("commands.logs.remove_log_channel.get_log_channel_api", new=AsyncMock(return_value="444444444")),
    ):
        yield {"set_ch": set_ch, "remove_ch": remove_ch}


async def test_configure_logs_cmd_initial_embed(logs_ui_api_mocks) -> None:
    group = LogsCommands(name="logs", description="logs")
    user = _admin_user()
    guild = make_guild()
    channel = make_text_channel(guild=guild)
    interaction = await invoke_interaction_command(
        group.configure_logs_cmd,
        user=user,
        guild=guild,
        channel=channel,
    )
    interaction.followup.send.assert_awaited()
    kwargs = interaction.followup.send.await_args.kwargs
    embed = kwargs.get("embed")
    assert embed is not None
    desc = embed.description or ""
    assert_selection_marker(desc)
    assert count_selection_markers(desc) == 1
    assert kwargs.get("view") is not None


async def test_set_log_channel_cmd_calls_api(logs_ui_api_mocks) -> None:
    group = LogsCommands(name="logs", description="logs")
    user = _admin_user()
    guild = make_guild()
    bot_member = make_member()
    guild.get_member = MagicMock(return_value=bot_member)
    ch = make_text_channel(guild=guild)
    ch.permissions_for = MagicMock(return_value=make_permissions(send_messages=True))
    ch.mention = "<#123>"
    user.guild_permissions = make_permissions(administrator=True)
    interaction = await invoke_interaction_command(
        group.set_log_channel_cmd,
        user=user,
        guild=guild,
        channel=ch,
        extra_kwargs={"channel": ch},
    )
    interaction.client.user = MagicMock(id=999999999)
    logs_ui_api_mocks["set_ch"].assert_awaited()


async def test_remove_log_channel_cmd_calls_api(logs_ui_api_mocks) -> None:
    group = LogsCommands(name="logs", description="logs")
    user = _admin_user()
    guild = make_guild()
    channel = make_text_channel(guild=guild)
    interaction = await invoke_interaction_command(
        group.remove_log_channel_cmd,
        user=user,
        guild=guild,
        channel=channel,
    )
    logs_ui_api_mocks["remove_ch"].assert_awaited()
    interaction.followup.send.assert_awaited()
