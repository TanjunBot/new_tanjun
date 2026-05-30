from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

import extensions.level as level_ext
from extensions.level import BlacklistCommands, LevelBoostCommands, LevelConfigCommands, levelCommands
from tests.helpers.discord import make_member, make_role, make_text_channel
from tests.helpers.extensions import invoke_interaction_command
from tests.integration.extensions.conftest import load_extension_bot

pytestmark = pytest.mark.asyncio

EXTENSION = "extensions.level"

COMMAND_PATCHES = (
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
    "disableLevelSystemCommand",
    "enableLevelSystemCommand",
    "changeLevelupMessageCommand",
    "disableLevelupMessageCommand",
    "enableLevelupMessageCommand",
    "setLevelupChannelCommand",
)


@pytest.fixture
def mock_cmds():
    patches = []
    for name in COMMAND_PATCHES:
        if hasattr(level_ext, name):
            patches.append(patch.object(level_ext, name, new=AsyncMock()))
    for p in patches:
        p.start()
    yield
    for p in patches:
        p.stop()


def make_attachment() -> MagicMock:
    att = MagicMock()
    att.url = "https://example.com/bg.png"
    return att


@pytest.mark.parametrize(
    "group_cls,method,extra",
    [
        (BlacklistCommands, "add_channel", {"channel": make_text_channel(), "reason": "spam"}),
        (BlacklistCommands, "remove_channel", {"channel": make_text_channel()}),
        (BlacklistCommands, "add_role", {"role": make_role(), "reason": "bots"}),
        (BlacklistCommands, "remove_role", {"role": make_role()}),
        (BlacklistCommands, "add_user", {"user": make_member(), "reason": "abuse"}),
        (BlacklistCommands, "remove_user", {"user": make_member()}),
        (BlacklistCommands, "show", {}),
        (
            LevelBoostCommands,
            "add_role_boost",
            {"role": make_role(), "boost": 1.5, "additive": True},
        ),
        (
            LevelBoostCommands,
            "add_channel_boost",
            {"channel": make_text_channel(), "boost": 2.0, "additive": False},
        ),
        (
            LevelBoostCommands,
            "add_user_boost",
            {"user": make_member(), "boost": 1.2, "additive": True},
        ),
        (LevelBoostCommands, "remove_role_boost", {"role": make_role()}),
        (LevelBoostCommands, "remove_channel_boost", {"channel": make_text_channel()}),
        (LevelBoostCommands, "remove_user_boost", {"user": make_member()}),
        (LevelBoostCommands, "show_boosts", {}),
        (
            LevelBoostCommands,
            "calculate_user_channel_boost",
            {"user": make_member(), "channel": make_text_channel()},
        ),
        (LevelConfigCommands, "disablelevelsystem", {}),
        (LevelConfigCommands, "enablelevelsystem", {}),
        (LevelConfigCommands, "changelevelupmessage", {"newmessage": "gg {user}"}),
        (LevelConfigCommands, "disablelevelupmessage", {}),
        (LevelConfigCommands, "enablelevelupmessage", {}),
        (LevelConfigCommands, "setlevelupchannel", {"channel": make_text_channel()}),
        (LevelConfigCommands, "changexpscaling", {"scaling": "easy", "customformula": None}),
        (LevelConfigCommands, "showxpscalings", {"startlevel": 1, "endlevel": 3}),
        (LevelConfigCommands, "addlevelrole", {"role": make_role(), "level": 5}),
        (LevelConfigCommands, "removelevelrole", {"role": make_role()}),
        (LevelConfigCommands, "showlevelroles", {}),
        (LevelConfigCommands, "give_xp", {"user": make_member(), "amount": 100}),
        (LevelConfigCommands, "take_xp", {"user": make_member(), "amount": 50}),
        (LevelConfigCommands, "settextcooldown", {"cooldown": 30}),
        (LevelConfigCommands, "setvoicecooldown", {"cooldown": 60}),
        (levelCommands, "rankcard", {"user": make_member()}),
        (levelCommands, "set_background", {"image": make_attachment()}),
        (levelCommands, "leaderboard", {"page": 2}),
    ],
    ids=[f"lvl{i}" for i in range(33)],
)
async def test_level_commands(group_cls, method, extra, mock_cmds) -> None:
    group = group_cls(name="test", description="test")
    handler = getattr(group, method)
    if method in ("showxpscalings", "leaderboard"):
        from tests.helpers.discord import make_guild, make_interaction, make_member, make_text_channel

        guild = make_guild()
        interaction = make_interaction(guild=guild, channel=make_text_channel(guild=guild), user=make_member())
        interaction.original_response = AsyncMock(return_value=MagicMock())
        kwargs = {"interaction": interaction, **extra}
        await handler(**kwargs)
    else:
        await invoke_interaction_command(handler, extra_kwargs=extra)


async def test_level_cog_on_ready(mock_cmds) -> None:
    bot = await load_extension_bot(EXTENSION, fire_ready=True)
    assert bot.tree.add_command.called
