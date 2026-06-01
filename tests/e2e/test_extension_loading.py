from __future__ import annotations

import importlib

import pytest

from tests.e2e.conftest import load_extension_bot
from tests.helpers.extension_loader import (
    EXTENSION_NAMES,
    fire_cog_on_ready,
    get_tree_command_names,
    get_tree_commands,
    load_all_extensions,
    load_extension,
)

pytestmark = [pytest.mark.asyncio, pytest.mark.e2e]

EXTENSION_COGS = {
    "extensions.admin": "AdminCog",
    "extensions.administration": "AdministrationCog",
    "extensions.ai": "AiCog",
    "extensions.channel": "ChannelCog",
    "extensions.error_handler": "ErrorHandlerCog",
    "extensions.fun": "FunCog",
    "extensions.games": "GameCog",
    "extensions.giveaway": "GiveawayCog",
    "extensions.image": "ImageCog",
    "extensions.level": "levelCog",
    "extensions.listeners": "ListenerCog",
    "extensions.loops": "LoopCog",
    "extensions.logs": "LogsCog",
    "extensions.math": "MathCog",
    "extensions.minigames": "MinigameCog",
    "extensions.setup_wizards": "SetupWizardsCog",
    "extensions.utility": "UtilityCog",
}

TREE_ROOT_AFTER_READY = {
    "extensions.ai": "ai_name",
    "extensions.channel": "channel_name",
    "extensions.fun": "funcmd_name",
    "extensions.games": "games_name",
    "extensions.giveaway": "giveaway_name",
    "extensions.image": "image_name",
    "extensions.level": "levelcommands_name",
    "extensions.logs": "logs_name",
    "extensions.math": "math_name",
    "extensions.minigames": "minigame_name",
}

ADMIN_TREE_ROOTS = (
    "admin_warn_name",
    "admin_role_name",
    "admin_rolemanage_name",
    "admin_report_name",
    "admin_triggermessages_name",
    "admin_jointocreate_name",
    "admin_moderation_name",
    "admin_purgegroup_name",
    "admin_channels_name",
    "admin_messaging_name",
    "admin_emoji_name",
    "admin_setup_name",
    "admin_localegroup_name",
)

UTILITY_TREE_ROOTS = ("utilitycmd_name", "utility_scheduledmessage_name")

NO_COG_EXTENSIONS = {"extensions.health_check"}


@pytest.mark.parametrize("extension", EXTENSION_NAMES)
async def test_extension_module_has_setup(extension: str):
    module = importlib.import_module(extension)
    assert hasattr(module, "setup")
    assert callable(module.setup)


@pytest.mark.parametrize("extension", EXTENSION_NAMES)
async def test_extension_setup_completes(extension_bot, extension: str):
    await load_extension(extension_bot, extension)
    assert extension in importlib.sys.modules


@pytest.mark.parametrize("extension", [e for e in EXTENSION_NAMES if e not in NO_COG_EXTENSIONS])
async def test_extension_registers_cog(extension: str):
    bot = await load_extension_bot(extension, fire_ready=False)
    cog_name = EXTENSION_COGS[extension]
    assert cog_name in bot.cogs


async def test_health_check_setup_without_cog(extension_bot):
    await load_extension(extension_bot, "extensions.health_check")
    assert extension_bot.cogs == {}


@pytest.mark.parametrize("extension", [e for e in EXTENSION_NAMES if e not in NO_COG_EXTENSIONS])
async def test_extension_add_cog_awaited(extension: str):
    bot = await load_extension_bot(extension, fire_ready=False)
    bot.add_cog.assert_awaited()


async def test_load_all_extensions_loads_every_module(extension_bot):
    loaded = await load_all_extensions(extension_bot)
    assert len(loaded) == len(EXTENSION_NAMES)
    assert set(loaded) == set(EXTENSION_NAMES)


async def test_all_extensions_register_expected_cogs(extension_bot):
    await load_all_extensions(extension_bot)
    for ext, cog_name in EXTENSION_COGS.items():
        assert cog_name in extension_bot.cogs


@pytest.mark.parametrize("extension,root_name", list(TREE_ROOT_AFTER_READY.items()))
async def test_on_ready_registers_tree_root(extension: str, root_name: str):
    bot = await load_extension_bot(extension)
    assert root_name in get_tree_command_names(bot)


@pytest.mark.parametrize("root_name", ADMIN_TREE_ROOTS)
async def test_admin_on_ready_registers_tree_roots(root_name: str):
    bot = await load_extension_bot("extensions.admin")
    assert root_name in get_tree_command_names(bot)


async def test_utility_on_ready_registers_tree_roots():
    bot = await load_extension_bot("extensions.utility")
    names = get_tree_command_names(bot)
    for root_name in UTILITY_TREE_ROOTS:
        assert root_name in names


async def test_setup_wizards_registers_tree_at_load(extension_bot):
    await load_extension(extension_bot, "extensions.setup_wizards")
    assert len(get_tree_commands(extension_bot)) == 1


async def test_error_handler_registers_no_tree_commands(extension_bot):
    await load_extension(extension_bot, "extensions.error_handler")
    await fire_cog_on_ready(extension_bot)
    assert get_tree_commands(extension_bot) == []


async def test_listeners_registers_no_tree_commands(extension_bot):
    await load_extension(extension_bot, "extensions.listeners")
    await fire_cog_on_ready(extension_bot)
    assert get_tree_commands(extension_bot) == []


async def test_loops_registers_no_tree_commands(extension_bot):
    await load_extension(extension_bot, "extensions.loops")
    await fire_cog_on_ready(extension_bot)
    assert get_tree_commands(extension_bot) == []


async def test_administration_registers_no_tree_commands(extension_bot):
    await load_extension(extension_bot, "extensions.administration")
    await fire_cog_on_ready(extension_bot)
    assert get_tree_commands(extension_bot) == []


async def test_error_handler_sets_tree_on_error(extension_bot):
    await load_extension(extension_bot, "extensions.error_handler")
    await fire_cog_on_ready(extension_bot)
    assert extension_bot.tree.on_error is not None


async def test_extension_count_is_eighteen():
    assert len(EXTENSION_NAMES) == 18
