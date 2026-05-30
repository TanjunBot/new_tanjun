from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest

import extensions.channel as channel_ext
from extensions.channel import DynamicslowmodeCommands, FarewellCommands, MediaCommands, WelcomeCommands
from tests.helpers.discord import make_text_channel
from tests.helpers.extensions import invoke_interaction_command
from tests.integration.extensions.conftest import load_extension_bot

pytestmark = pytest.mark.asyncio

EXTENSION = "extensions.channel"

PATCH_NAMES = [
    "setWelcomeChannelCommand",
    "removeWelcomeChannelCommand",
    "setFarewellChannelCommand",
    "removeFarewellChannelCommand",
    "addMediaChannelCommand",
    "removeMediaChannelCommand",
    "addDynamicslowmodeCommand",
    "removeDynamicslowmodeCommand",
    "getDynamicslowmodeChannelsCommand",
]


@pytest.fixture
def mock_cmds():
    patches = [patch.object(channel_ext, name, new=AsyncMock()) for name in PATCH_NAMES]
    for p in patches:
        p.start()
    yield
    for p in patches:
        p.stop()


@pytest.mark.parametrize(
    "group_cls,method,extra",
    [
        (WelcomeCommands, "welcome", {"channel": make_text_channel(), "message": "hi", "background": None}),
        (WelcomeCommands, "remove_welcome", {}),
        (FarewellCommands, "set_farewell_channel", {"channel": make_text_channel(), "message": "bye", "background": None}),
        (FarewellCommands, "remove_farewell_channel", {}),
        (MediaCommands, "media_add_cmd", {"channel": make_text_channel()}),
        (MediaCommands, "media_remove_cmd", {"channel": make_text_channel()}),
        (
            DynamicslowmodeCommands,
            "add_dynamicslowmode",
            {"channel": make_text_channel(), "messages": 5, "per": 60, "resetafter": 30},
        ),
        (DynamicslowmodeCommands, "remove_dynamicslowmode", {"channel": make_text_channel()}),
        (DynamicslowmodeCommands, "get_dynamicslowmode_channels", {}),
    ],
    ids=[f"ch{i}" for i in range(9)],
)
async def test_channel_commands(group_cls, method, extra, mock_cmds) -> None:
    group = group_cls(name="test", description="test")
    await invoke_interaction_command(getattr(group, method), extra_kwargs=extra)


async def test_channel_cog_on_ready(mock_cmds) -> None:
    bot = await load_extension_bot(EXTENSION, fire_ready=True)
    assert bot.tree.add_command.called
