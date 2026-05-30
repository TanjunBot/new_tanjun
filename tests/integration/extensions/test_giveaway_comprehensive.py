from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest

import extensions.giveaway as giveaway_ext
from extensions.giveaway import BlacklistCommands, GiveawayCommands
from tests.helpers.discord import make_member, make_role, make_text_channel
from tests.helpers.extensions import invoke_interaction_command
from tests.integration.extensions.conftest import load_extension_bot

pytestmark = pytest.mark.asyncio

EXTENSION = "extensions.giveaway"

PATCH_NAMES = [
    "add_blacklist_role",
    "remove_blacklist_role",
    "add_blacklist_user",
    "remove_blacklist_user",
    "list_blacklist",
    "start_giveaway",
    "end_giveaway",
    "edit_giveaway",
    "reroll_giveaway",
]


@pytest.fixture
def mock_cmds():
    patches = [patch.object(giveaway_ext, name, new=AsyncMock()) for name in PATCH_NAMES]
    for p in patches:
        p.start()
    yield
    for p in patches:
        p.stop()


@pytest.mark.parametrize(
    "group_cls,method,extra",
    [
        (BlacklistCommands, "add_role", {"role": make_role()}),
        (BlacklistCommands, "remove_role", {"role": make_role()}),
        (BlacklistCommands, "add_user", {"user": make_member()}),
        (BlacklistCommands, "remove_user", {"user": make_member()}),
        (BlacklistCommands, "list", {}),
        (GiveawayCommands, "start", {"title": "Prize", "channel": make_text_channel()}),
        (GiveawayCommands, "end", {"giveawayid": 1}),
        (GiveawayCommands, "edit", {"giveawayid": 1}),
        (GiveawayCommands, "reroll", {"giveawayid": 1}),
    ],
    ids=[f"gw{i}" for i in range(9)],
)
async def test_giveaway_commands(group_cls, method, extra, mock_cmds) -> None:
    group = group_cls(name="test", description="test")
    await invoke_interaction_command(getattr(group, method), extra_kwargs=extra)


async def test_giveaway_cog_on_ready(mock_cmds) -> None:
    bot = await load_extension_bot(EXTENSION, fire_ready=True)
    assert bot.tree.add_command.called
