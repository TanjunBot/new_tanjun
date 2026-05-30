from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest

import extensions.minigames as minigames_ext
from extensions.minigames import (
    CountingChallengeCommands,
    CountingCommands,
    CountingModesCommands,
    WordChainCommands,
)
from tests.helpers.discord import make_text_channel
from tests.helpers.extensions import invoke_interaction_command
from tests.integration.extensions.conftest import load_extension_bot

pytestmark = pytest.mark.asyncio

EXTENSION = "extensions.minigames"

COMMAND_PATCHES = [
    "setCountingChannelCommand",
    "removeCountingChannelCommand",
    "setCountingProgressCommand",
    "setCountingChallengeChannelCommand",
    "removeCountingChallengeChannelCommand",
    "setCountingChallengeProgressCommand",
    "setCountingModesChannelCommand",
    "removeCountingModesChannelCommand",
    "setCountingModesProgressCommand",
    "setWordChainChannelCommand",
    "removeWordChainChannelCommand",
]


@pytest.fixture
def mock_cmds():
    patches = [patch.object(minigames_ext, name, new=AsyncMock()) for name in COMMAND_PATCHES]
    for p in patches:
        p.start()
    yield
    for p in patches:
        p.stop()


@pytest.mark.parametrize(
    "group_cls,method,extra",
    [
        (CountingCommands, "setcountingchannel", {"channel": None}),
        (CountingCommands, "setcountingchannel", {"channel": make_text_channel()}),
        (CountingCommands, "removecountingchannel", {"channel": None}),
        (CountingCommands, "setcountingprogress", {"channel": make_text_channel(), "progress": 5}),
        (CountingChallengeCommands, "setcountingchallengechannel", {"channel": make_text_channel()}),
        (CountingChallengeCommands, "removecountingchallengechannel", {"channel": make_text_channel()}),
        (CountingChallengeCommands, "setcountingchallengeprogress", {"channel": make_text_channel(), "progress": 3}),
        (CountingModesCommands, "setcountingmodeschannel", {"channel": make_text_channel()}),
        (CountingModesCommands, "removecountingmodeschannel", {"channel": make_text_channel()}),
        (CountingModesCommands, "setcountingmodesprogress", {"channel": make_text_channel(), "progress": 2}),
        (WordChainCommands, "setwordchainchannel", {"channel": make_text_channel()}),
        (WordChainCommands, "removewordchainchannel", {"channel": make_text_channel()}),
    ],
    ids=[f"mini{i}" for i in range(12)],
)
async def test_minigames_commands(group_cls, method, extra, mock_cmds) -> None:
    group = group_cls(name="test", description="test")
    await invoke_interaction_command(getattr(group, method), extra_kwargs=extra)


async def test_minigames_cog_on_ready(mock_cmds) -> None:
    bot = await load_extension_bot(EXTENSION, fire_ready=True)
    assert bot.tree.add_command.called
