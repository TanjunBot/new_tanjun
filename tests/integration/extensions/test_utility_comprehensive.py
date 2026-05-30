from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

import extensions.utility as utility_ext
from extensions.utility import (
    AutoPublishCommands,
    BoosterChannelCommands,
    BoosterRoleCommands,
    BrawlStarsCommands,
    MessageTrackingCommands,
    ScheduledMessageCommands,
    TwitchCommands,
    UtilityCommands,
)
from tests.helpers.discord import make_interaction, make_member, make_role, make_text_channel
from tests.helpers.extensions import invoke_interaction_command
from tests.integration.extensions.conftest import load_extension_bot

pytestmark = pytest.mark.asyncio

EXTENSION = "extensions.utility"


def make_attachment() -> MagicMock:
    att = MagicMock()
    att.url = "https://example.com/a.png"
    att.filename = "a.png"
    return att


@pytest.fixture
def mock_cmds():
    patches = []
    for name in dir(utility_ext):
        if name.endswith("Command"):
            patches.append(patch.object(utility_ext, name, new=AsyncMock()))
    for p in patches:
        p.start()
    yield
    for p in patches:
        p.stop()


@pytest.mark.parametrize(
    "group_cls,method,extra",
    [
        (MessageTrackingCommands, "messagetrackingoptout", {}),
        (MessageTrackingCommands, "messagetrackingoptin", {}),
        (BoosterRoleCommands, "claimboosterrole", {"name": "role", "color": "#FF0000", "icon": None}),
        (BoosterRoleCommands, "deleteboosterrole", {}),
        (BoosterRoleCommands, "setupboosterrole", {"role": make_role()}),
        (BoosterChannelCommands, "claimboosterchannel", {"name": "vc"}),
        (BoosterChannelCommands, "deleteboosterchannel", {}),
        (BoosterChannelCommands, "setupboosterchannel", {"category": make_text_channel()}),
        (AutoPublishCommands, "autopublish", {"channel": make_text_channel()}),
        (AutoPublishCommands, "autopublish_remove", {"channel": make_text_channel()}),
        (BrawlStarsCommands, "battlelog", {"tag": "ABC"}),
        (BrawlStarsCommands, "playerinfo", {"tag": "ABC"}),
        (BrawlStarsCommands, "brawlers", {"tag": "ABC"}),
        (BrawlStarsCommands, "club", {"tag": "ABC"}),
        (BrawlStarsCommands, "events", {}),
        (BrawlStarsCommands, "link", {"tag": "ABC"}),
        (BrawlStarsCommands, "unlink", {}),
        (TwitchCommands, "add", {"twitchname": "ninja", "channel": make_text_channel(), "notificationmessage": "live"}),
        (TwitchCommands, "see", {}),
        (UtilityCommands, "avatar", {"user": make_member()}),
        (UtilityCommands, "banner", {"user": make_member()}),
        (UtilityCommands, "avatardecoration", {"user": make_member()}),
        (UtilityCommands, "feedback", {}),
        (UtilityCommands, "afk", {"reason": "brb"}),
        (UtilityCommands, "report", {"user": make_member(), "reason": "a" * 12}),
        (
            ScheduledMessageCommands,
            "schedulemessage",
            {
                "content": "hi",
                "sendin": "1h",
                "channel": make_text_channel(),
                "repeatinterval": None,
                "repeatamount": None,
                "attachment1": make_attachment(),
                "attachment2": None,
                "attachment3": None,
                "attachment4": None,
                "attachment5": None,
                "attachment6": None,
                "attachment7": None,
                "attachment8": None,
                "attachment9": None,
                "attachment10": None,
            },
        ),
        (ScheduledMessageCommands, "listscheduled", {}),
        (ScheduledMessageCommands, "removescheduled", {"messageid": 12345}),
    ],
    ids=[f"util{i}" for i in range(28)],
)
async def test_utility_commands(group_cls, method, extra, mock_cmds) -> None:
    group = group_cls(name="test", description="test")
    handler = getattr(group, method)
    if method == "feedback":
        interaction = make_interaction()
        interaction.response.send_message = AsyncMock()
        await handler(interaction)
    elif method == "removescheduled":
        await invoke_interaction_command(handler, extra_kwargs=extra)
    else:
        await invoke_interaction_command(handler, extra_kwargs=extra)


async def test_booster_info_commands(mock_cmds) -> None:
    role_group = BoosterRoleCommands(name="br", description="br")
    chan_group = BoosterChannelCommands(name="bc", description="bc")

    def _command_info(**kwargs):
        obj = MagicMock()
        for key, value in kwargs.items():
            setattr(obj, key, value)
        obj.reply = kwargs.get("reply", AsyncMock())
        return obj

    for group in (role_group, chan_group):
        interaction = make_interaction()
        interaction.response.defer = AsyncMock()
        interaction.followup.send = AsyncMock()
        with patch("utility.CommandInfo", side_effect=_command_info):
            await group.info(interaction)
        interaction.followup.send.assert_awaited_once()


async def test_autopublish_default_channel(mock_cmds) -> None:
    group = AutoPublishCommands(name="ap", description="ap")
    await invoke_interaction_command(group.autopublish, extra_kwargs={"channel": None})
    await invoke_interaction_command(group.autopublish_remove, extra_kwargs={"channel": None})


async def test_utility_default_user_args(mock_cmds) -> None:
    group = UtilityCommands(name="u", description="u")
    for cmd in (group.avatar, group.banner, group.avatardecoration):
        await invoke_interaction_command(cmd, extra_kwargs={"user": None})


async def test_utility_cog_help_and_on_ready(mock_cmds) -> None:
    bot = await load_extension_bot(EXTENSION, fire_ready=True)
    cog = bot.cogs["UtilityCog"]
    await invoke_interaction_command(cog.help_slash)
    assert bot.tree.add_command.called
