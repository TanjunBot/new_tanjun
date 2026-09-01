from __future__ import annotations

import importlib

import pytest

from tests.helpers.extension_loader import (
    find_tree_group,
    fire_cog_on_ready,
    get_subcommand_names,
    get_tree_command_names,
    get_tree_commands,
    load_extension,
    make_bot_for_extensions,
)
from tests.integration.extensions.conftest import load_extension_bot

pytestmark = pytest.mark.asyncio

EXTENSION = "extensions.fun"
COG_NAME = "FunCog"

# The fun extension registers 9 subcommands under funcmd_name
FUN_SUBCOMMANDS = [
    "fun_hug_name",
    "fun_kiss_name",
    "fun_boop_name",
    "fun_wave_name",
    "fun_slap_name",
    "fun_laugh_name",
    "fun_tickle_name",
    "fun_pat_name",
    "fun_poke_name",
]


async def test_module_exposes_setup():
    module = importlib.import_module(EXTENSION)
    assert hasattr(module, "setup")
    assert callable(module.setup)


async def test_setup_registers_cog():
    bot = await load_extension_bot(EXTENSION, fire_ready=False)
    assert COG_NAME in bot.cogs


async def test_setup_calls_add_cog_once():
    bot = await load_extension_bot(EXTENSION, fire_ready=False)
    bot.add_cog.assert_awaited_once()


async def test_get_cog_returns_registered_instance():
    bot = await load_extension_bot(EXTENSION, fire_ready=False)
    assert bot.get_cog(COG_NAME) is bot.cogs[COG_NAME]


async def test_cog_stores_bot_reference():
    bot = await load_extension_bot(EXTENSION, fire_ready=False)
    assert bot.cogs[COG_NAME].bot is bot


async def test_on_ready_adds_command_to_tree():
    bot = make_bot_for_extensions()
    await load_extension(bot, EXTENSION)
    assert get_tree_commands(bot) == []
    await fire_cog_on_ready(bot)
    assert len(get_tree_commands(bot)) == 1


async def test_root_command_name_is_funcmd_name():
    bot = await load_extension_bot(EXTENSION)
    assert get_tree_command_names(bot) == ["funcmd_name"]


async def test_root_group_has_all_action_subcommands():
    bot = await load_extension_bot(EXTENSION)
    root = find_tree_group(bot, "funcmd_name")
    assert root is not None
    assert len(get_subcommand_names(root)) == len(FUN_SUBCOMMANDS)


async def test_all_fun_subcommands_registered():
    bot = await load_extension_bot(EXTENSION)
    root = find_tree_group(bot, "funcmd_name")
    assert root is not None
    names = get_subcommand_names(root)
    for expected in FUN_SUBCOMMANDS:
        assert expected in names, f"Missing fun subcommand: {expected}"
