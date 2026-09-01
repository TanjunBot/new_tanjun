from __future__ import annotations

import pytest

from tests.e2e.conftest import load_extension_bot
from tests.helpers.extension_loader import (
    find_nested_group,
    find_tree_group,
    get_subcommand_names,
    get_tree_command_names,
    get_tree_commands,
)
from tests.integration.extensions.test_admin import ADMIN_TOP_LEVEL_GROUPS

pytestmark = [pytest.mark.asyncio, pytest.mark.e2e]

TREE_GROUPS = {
    "extensions.ai": ("ai_name", 4),
    "extensions.channel": ("channel_name", 4),
    "extensions.fun": ("funcmd_name", 1),
    "extensions.games": ("games_name", 7),
    "extensions.giveaway": ("giveaway_name", 5),
    "extensions.image": ("image_name", 13),
    "extensions.level": ("levelcommands_name", 3),
    "extensions.logs": ("logs_name", 6),
    "extensions.math": ("math_name", 6),
    "extensions.minigames": ("minigame_name", 4),
}


@pytest.mark.parametrize(
    "extension,root_name,min_subs",
    [(ext, root, subs) for ext, (root, subs) in TREE_GROUPS.items()],
)
async def test_tree_root_group_exists(extension: str, root_name: str, min_subs: int):
    bot = await load_extension_bot(extension)
    root = find_tree_group(bot, root_name)
    assert root is not None
    assert len(get_subcommand_names(root)) >= min_subs


@pytest.mark.parametrize("root_name", ADMIN_TOP_LEVEL_GROUPS)
async def test_admin_top_level_group_exists(root_name: str):
    bot = await load_extension_bot("extensions.admin")
    root = find_tree_group(bot, root_name)
    assert root is not None
    assert len(get_subcommand_names(root)) >= 1


async def test_admin_kick_subcommand_registered():
    bot = await load_extension_bot("extensions.admin")
    root = find_tree_group(bot, "admin_moderation_name")
    assert root is not None
    assert "admin_kick_name" in get_subcommand_names(root)


async def test_admin_ban_subcommand_registered():
    bot = await load_extension_bot("extensions.admin")
    root = find_tree_group(bot, "admin_moderation_name")
    assert root is not None
    assert "admin_ban_name" in get_subcommand_names(root)


async def test_giveaway_create_subcommand_registered():
    bot = await load_extension_bot("extensions.giveaway")
    root = find_tree_group(bot, "giveaway_name")
    assert root is not None
    names = get_subcommand_names(root)
    assert len(names) >= 1


async def test_level_config_nested_group():
    bot = await load_extension_bot("extensions.level")
    root = find_tree_group(bot, "levelcommands_name")
    assert root is not None
    nested = find_nested_group(root, "level_config_name")
    assert nested is not None or len(get_subcommand_names(root)) >= 1


async def test_minigames_counting_subcommand():
    bot = await load_extension_bot("extensions.minigames")
    root = find_tree_group(bot, "minigame_name")
    assert root is not None
    assert len(get_subcommand_names(root)) >= 4


async def test_setup_wizards_single_tree_command(extension_bot):
    from tests.helpers.extension_loader import load_extension

    await load_extension(extension_bot, "extensions.setup_wizards")
    names = get_tree_command_names(extension_bot)
    assert len(names) == 1


async def test_all_extensions_bot_has_multiple_tree_roots(all_extensions_bot):
    names = get_tree_command_names(all_extensions_bot)
    assert len(names) >= 10


async def test_tree_add_command_invoked_for_admin():
    bot = await load_extension_bot("extensions.admin")
    assert bot.tree.add_command.called


async def test_utility_tree_roots():
    bot = await load_extension_bot("extensions.utility")
    names = get_tree_command_names(bot)
    assert "utilitycmd_name" in names
    assert "utility_scheduledmessage_name" in names


async def test_math_tree_root_name():
    bot = await load_extension_bot("extensions.math")
    assert get_tree_command_names(bot) == ["math_name"]


async def test_logs_tree_root_name():
    bot = await load_extension_bot("extensions.logs")
    assert get_tree_command_names(bot) == ["logs_name"]


async def test_games_tree_root_name():
    bot = await load_extension_bot("extensions.games")
    assert get_tree_command_names(bot) == ["games_name"]


async def test_channel_tree_root_name():
    bot = await load_extension_bot("extensions.channel")
    assert get_tree_command_names(bot) == ["channel_name"]


async def test_ai_tree_root_name():
    bot = await load_extension_bot("extensions.ai")
    assert get_tree_command_names(bot) == ["ai_name"]


async def test_image_tree_root_name():
    bot = await load_extension_bot("extensions.image")
    assert get_tree_command_names(bot) == ["image_name"]


async def test_fun_tree_root_name():
    bot = await load_extension_bot("extensions.fun")
    assert get_tree_command_names(bot) == ["funcmd_name"]


async def test_error_handler_tree_empty_after_ready():
    bot = await load_extension_bot("extensions.error_handler")
    assert get_tree_commands(bot) == []


async def test_listeners_tree_empty_after_ready():
    bot = await load_extension_bot("extensions.listeners")
    assert get_tree_commands(bot) == []
