from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

import extensions.admin as admin_ext
from extensions.admin import (
    AdminChannelCommands,
    AdminEmojiCommands,
    AdminLocaleCommands,
    AdminMessagingCommands,
    AdminModerationCommands,
    AdminPurgeCommands,
    AdminSetupCommands,
    JoinToCreateCommands,
    ReportCommands,
    RoleCommands,
    RoleManageCommands,
    TriggerMessagesCommands,
    WarnCommands,
)
from tests.helpers.discord import make_guild, make_member, make_role, make_text_channel
from tests.helpers.extensions import invoke_interaction_command
from tests.integration.extensions.conftest import load_extension_bot

pytestmark = pytest.mark.asyncio

EXTENSION = "extensions.admin"


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


def make_voice_channel():
    from tests.helpers.discord import MockVoiceChannel

    ch = MockVoiceChannel()
    ch.id = 777777777
    ch.guild = make_guild()
    return ch


def _choice(value: str) -> MagicMock:
    choice = MagicMock()
    choice.value = value
    return choice


@pytest.mark.parametrize(
    "group_cls,method,extra",
    [
        (WarnCommands, "add", {"user": make_member(), "reason": "warn"}),
        (WarnCommands, "view", {"user": make_member()}),
        (WarnCommands, "config", {}),
        (RoleCommands, "addrole", {"user": make_member(), "role": make_role()}),
        (RoleCommands, "removerole", {"user": make_member(), "role": make_role()}),
        (RoleManageCommands, "createrole", {"name": "NewRole"}),
        (RoleManageCommands, "deleterole", {"role": make_role(), "reason": "cleanup"}),
        (
            RoleManageCommands,
            "moverole",
            {
                "role": make_role(),
                "target_role": make_role(role_id=666),
                "position": _choice("above"),
            },
        ),
        (
            RoleManageCommands,
            "copyrole",
            {"role": make_role(), "copymembers": _choice("false")},
        ),
        (TriggerMessagesCommands, "configure", {}),
        (
            TriggerMessagesCommands,
            "add",
            {
                "trigger": "hello",
                "response": "world",
                "casesensitive": _choice("f"),
            },
        ),
        (JoinToCreateCommands, "set_channel", {"channel": make_voice_channel()}),
        (JoinToCreateCommands, "remove_channel", {"channel": make_voice_channel()}),
    ],
    ids=[f"grp{i}" for i in range(13)],
)
async def test_group_commands(group_cls, method, extra, mock_cmds) -> None:
    group = group_cls(name="test", description="test")
    await invoke_interaction_command(getattr(group, method), extra_kwargs=extra)


async def test_report_commands(mock_cmds) -> None:
    group = ReportCommands(name="r", description="r")
    await invoke_interaction_command(group.remove_channel)
    await invoke_interaction_command(group.show_reports, extra_kwargs={"user": make_member()})
    await invoke_interaction_command(group.unblock_reporter, extra_kwargs={"user": make_member()})


async def test_administration_moderation(mock_cmds) -> None:
    group = AdminModerationCommands(name="a", description="a")
    member = make_member()
    await invoke_interaction_command(group.kick, extra_kwargs={"user": member, "reason": "kick"})
    await invoke_interaction_command(
        group.ban,
        extra_kwargs={"user": member, "reason": "ban", "delete_message_days": 1},
    )
    await invoke_interaction_command(group.unban, extra_kwargs={"username": "user#1", "reason": "unban"})
    await invoke_interaction_command(
        group.timeout,
        extra_kwargs={"user": member, "duration": 60, "reason": "timeout"},
    )
    await invoke_interaction_command(group.removetimeout, extra_kwargs={"user": member, "reason": "ok"})
    await invoke_interaction_command(group.nickname, extra_kwargs={"user": member, "nickname": "nick"})
    channel_group = AdminChannelCommands(name="a", description="a")
    await invoke_interaction_command(channel_group.lock, extra_kwargs={"channel": make_text_channel()})
    await invoke_interaction_command(channel_group.unlock, extra_kwargs={"channel": make_text_channel()})


async def test_administration_channel_ops(mock_cmds) -> None:
    group = AdminChannelCommands(name="a", description="a")
    channel = make_text_channel()
    await invoke_interaction_command(group.lock, extra_kwargs={"channel": channel})
    await invoke_interaction_command(group.unlock, extra_kwargs={"channel": channel})
    await invoke_interaction_command(group.nuke, extra_kwargs={"channel": channel})


async def test_administration_roles_and_misc(mock_cmds) -> None:
    emoji_group = AdminEmojiCommands(name="a", description="a")
    await invoke_interaction_command(emoji_group.claimboosterrole, extra_kwargs={"role": make_role()})
    await invoke_interaction_command(emoji_group.copy_emoji, extra_kwargs={"emoji": ":e:"})
    setup_group = AdminSetupCommands(name="a", description="a")
    await invoke_interaction_command(
        setup_group.create_ticket,
        extra_kwargs={
            "name": "ticket",
            "description": "desc",
            "channel": make_text_channel(),
            "pingrole": make_role(),
            "summarychannel": make_text_channel(),
            "introduction": "hi",
        },
    )
    locale_group = AdminLocaleCommands(name="a", description="a")
    await invoke_interaction_command(locale_group.set_locale, extra_kwargs={"locale": "en"})


async def test_admin_cog_on_ready(mock_cmds) -> None:
    bot = await load_extension_bot(EXTENSION, fire_ready=True)
    assert bot.tree.add_command.called
