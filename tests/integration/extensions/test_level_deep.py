from __future__ import annotations

import inspect
from unittest.mock import AsyncMock, patch

import pytest

import extensions.level as level_ext
from extensions.level import (
    BlacklistCommands,
    LevelBoostCommands,
    LevelConfigCommands,
    levelCommands,
)
from tests.helpers.discord import make_member, make_role, make_text_channel
from tests.helpers.extensions import invoke_interaction_command
from tests.integration.extensions.conftest import load_extension_bot

pytestmark = pytest.mark.asyncio

EXTENSION = "extensions.level"


@pytest.fixture
def mock_level_commands():
    patches = []
    for name in dir(level_ext):
        if name.endswith("Command") or name.endswith("_command"):
            patches.append(patch.object(level_ext, name, AsyncMock()))
    for name in (
        "add_level_role_command",
        "remove_level_role_command",
        "show_level_roles_command",
        "give_xp_command",
        "take_xp_command",
        "leaderboard",
        "add_channel_to_blacklist_command",
        "add_role_to_blacklist_command",
        "add_user_to_blacklist_command",
        "remove_channel_from_blacklist_command",
        "remove_role_from_blacklist_command",
        "remove_user_from_blacklist_command",
        "show_blacklist_command",
        "add_channel_boost_command",
        "add_role_boost_command",
        "add_user_boost_command",
        "remove_channel_boost_command",
        "remove_role_boost_command",
        "remove_user_boost_command",
        "show_boosts_command",
        "calculate_user_channel_boost_command",
        "set_background_command",
        "show_rankcard_command",
        "set_text_cooldown_command",
        "set_voice_cooldown_command",
        "change_xp_scaling_command",
        "show_xp_scalings",
    ):
        if hasattr(level_ext, name):
            patches.append(patch.object(level_ext, name, AsyncMock()))
    for p in patches:
        p.start()
    yield
    for p in patches:
        p.stop()


@pytest.mark.parametrize(
    "group_cls",
    [BlacklistCommands, LevelBoostCommands, LevelConfigCommands, levelCommands],
    ids=["blacklist", "boost", "config", "commands"],
)
async def test_invoke_level_groups(group_cls, mock_level_commands):
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
                if "Member" in ann:
                    extra[pname] = make_member()
                elif "Role" in ann:
                    extra[pname] = make_role()
                elif "TextChannel" in ann:
                    extra[pname] = make_text_channel()
            await invoke_interaction_command(bound, extra_kwargs=extra)


async def test_level_cog_on_ready():
    bot = await load_extension_bot(EXTENSION, fire_ready=True)
    assert bot.tree.add_command.called
