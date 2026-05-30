from __future__ import annotations

import inspect
from unittest.mock import AsyncMock, patch

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
from tests.helpers.discord import make_member, make_text_channel
from tests.helpers.extensions import invoke_interaction_command
from tests.integration.extensions.conftest import load_extension_bot

pytestmark = pytest.mark.asyncio

EXTENSION = "extensions.utility"


@pytest.fixture
def mock_utility_commands():
    patches = []
    for name in dir(utility_ext):
        if name.endswith("Command") or name.endswith("Cmd"):
            patches.append(patch.object(utility_ext, name, AsyncMock()))
    for p in patches:
        p.start()
    yield
    for p in patches:
        p.stop()


@pytest.mark.parametrize(
    "group_cls",
    [
        MessageTrackingCommands,
        BoosterRoleCommands,
        BoosterChannelCommands,
        AutoPublishCommands,
        BrawlStarsCommands,
        TwitchCommands,
        UtilityCommands,
        ScheduledMessageCommands,
    ],
    ids=["tracking", "broles", "bochan", "autopub", "brawl", "twitch", "util", "sched"],
)
async def test_invoke_utility_groups(group_cls, mock_utility_commands):
    group = group_cls(name="test", description="test")
    for name, method in inspect.getmembers(group, predicate=inspect.isfunction):
        if inspect.iscoroutinefunction(method) and not name.startswith("_"):
            bound = getattr(group, name)
            extra = {}
            sig = inspect.signature(bound)
            for pname, param in sig.parameters.items():
                if pname in ("self", "interaction"):
                    continue
                ann = str(param.annotation)
                if "Member" in ann or "User" in ann:
                    extra[pname] = make_member()
                elif "TextChannel" in ann:
                    extra[pname] = make_text_channel()
            try:
                await invoke_interaction_command(bound, extra_kwargs=extra)
            except TypeError:
                await invoke_interaction_command(bound)


async def test_utility_cog_on_ready():
    bot = await load_extension_bot(EXTENSION, fire_ready=True)
    assert len(bot._tree_commands) >= 1
