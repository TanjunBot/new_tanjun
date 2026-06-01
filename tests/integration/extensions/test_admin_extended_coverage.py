from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

import extensions.admin as admin_ext
from extensions.admin import (
    AdminChannelCommands,
    AdminEmojiCommands,
    AdminMessagingCommands,
    AdminPurgeCommands,
    AdminSetupCommands,
    ReportCommands,
)
from tests.helpers.discord import make_interaction, make_member, make_role, make_text_channel
from tests.helpers.extensions import invoke_interaction_command

pytestmark = pytest.mark.asyncio


@pytest.fixture
def mock_cmds():
    patches = []
    for name in dir(admin_ext):
        if name.endswith("Command"):
            patches.append(patch.object(admin_ext, name, new=AsyncMock()))
    for p in patches:
        p.start()
    yield
    for p in patches:
        p.stop()


def _choice(value: str) -> MagicMock:
    choice = MagicMock()
    choice.value = value
    return choice


async def _invoke_group_command(group, method_name: str, **kwargs):
    handler = getattr(group, method_name)
    channel = kwargs.get("channel")
    await invoke_interaction_command(
        handler,
        channel=channel if channel is not None else make_text_channel(),
        extra_kwargs=kwargs,
    )


@pytest.mark.parametrize(
    "extra",
    [
        {"channel": make_text_channel()},
    ],
)
async def test_report_set_channel(extra, mock_cmds) -> None:
    group = ReportCommands(name="r", description="r")
    await invoke_interaction_command(group.set_channel, extra_kwargs=extra)


async def test_report_set_channel_default_channel(mock_cmds) -> None:
    group = ReportCommands(name="r", description="r")
    await invoke_interaction_command(group.set_channel, extra_kwargs={})


async def test_purge_all_setting(mock_cmds) -> None:
    group = AdminPurgeCommands(name="a", description="a")
    await _invoke_group_command(
        group,
        "purge",
        limit=25,
        channel=make_text_channel(),
        setting="all",
    )


async def test_purge_choice_setting(mock_cmds) -> None:
    group = AdminPurgeCommands(name="a", description="a")
    await _invoke_group_command(
        group,
        "purge",
        limit=10,
        channel=None,
        setting=_choice("bots"),
    )


async def test_slowmode(mock_cmds) -> None:
    group = AdminChannelCommands(name="a", description="a")
    await _invoke_group_command(group, "slowmode", seconds=30, channel=make_text_channel())


async def test_say_with_explicit_channel(mock_cmds) -> None:
    group = AdminMessagingCommands(name="a", description="a")
    await _invoke_group_command(
        group,
        "say",
        message="hello world",
        channel=make_text_channel(),
    )


async def test_say_defaults_channel(mock_cmds) -> None:
    group = AdminMessagingCommands(name="a", description="a")
    await _invoke_group_command(group, "say", message="default channel", channel=None)


async def test_embed_with_channel(mock_cmds) -> None:
    group = AdminMessagingCommands(name="a", description="a")
    await _invoke_group_command(group, "embed", title="Title", channel=make_text_channel())


async def test_embed_defaults_channel(mock_cmds) -> None:
    group = AdminMessagingCommands(name="a", description="a")
    await _invoke_group_command(group, "embed", title="Default", channel=None)


async def test_nuke_defaults_channel(mock_cmds) -> None:
    group = AdminChannelCommands(name="a", description="a")
    await _invoke_group_command(group, "nuke", channel=None)


async def test_create_ticket_defaults_channel(mock_cmds) -> None:
    group = AdminSetupCommands(name="a", description="a")
    await _invoke_group_command(
        group,
        "create_ticket",
        name="support",
        description="Need help",
        channel=None,
        pingrole=make_role(),
        summarychannel=make_text_channel(),
        introduction="Hi",
    )


async def test_createemoji_sends_role_select(mock_cmds) -> None:
    group = AdminEmojiCommands(name="a", description="a")
    guild = make_interaction().guild
    guild.default_role = make_role()
    interaction = await invoke_interaction_command(
        group.createemoji,
        guild=guild,
        extra_kwargs={"name": "emoji1", "imageurl": "https://example.com/e.png"},
    )
    interaction.followup.send.assert_awaited_once()


async def test_report_show_reports(mock_cmds) -> None:
    group = ReportCommands(name="r", description="r")
    await invoke_interaction_command(group.show_reports, extra_kwargs={"user": make_member()})


async def test_report_unblock_reporter(mock_cmds) -> None:
    group = ReportCommands(name="r", description="r")
    await invoke_interaction_command(group.unblock_reporter, extra_kwargs={"user": make_member()})
