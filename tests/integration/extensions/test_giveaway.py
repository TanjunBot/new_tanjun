from __future__ import annotations

import importlib

import pytest

from tests.helpers.extension_loader import (
    find_nested_group,
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

EXTENSION = "extensions.giveaway"
COG_NAME = "GiveawayCog"

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

async def test_root_command_name_is_giveaway_name():
    bot = await load_extension_bot(EXTENSION)
    assert get_tree_command_names(bot) == ["giveaway_name"]

async def test_root_group_has_5_entries():
    bot = await load_extension_bot(EXTENSION)
    root = find_tree_group(bot, "giveaway_name")
    assert root is not None
    assert len(get_subcommand_names(root)) == 5

async def test_subcommand_giveaway_start_name_registered():
    bot = await load_extension_bot(EXTENSION)
    root = find_tree_group(bot, "giveaway_name")
    assert root is not None
    assert "giveaway_start_name" in get_subcommand_names(root)

async def test_subcommand_giveaway_end_name_registered():
    bot = await load_extension_bot(EXTENSION)
    root = find_tree_group(bot, "giveaway_name")
    assert root is not None
    assert "giveaway_end_name" in get_subcommand_names(root)

async def test_subcommand_giveaway_reroll_name_registered():
    bot = await load_extension_bot(EXTENSION)
    root = find_tree_group(bot, "giveaway_name")
    assert root is not None
    assert "giveaway_reroll_name" in get_subcommand_names(root)

async def test_subcommand_giveaway_edit_name_registered():
    bot = await load_extension_bot(EXTENSION)
    root = find_tree_group(bot, "giveaway_name")
    assert root is not None
    assert "giveaway_edit_name" in get_subcommand_names(root)

async def test_subcommand_giveaway_blacklist_name_registered():
    bot = await load_extension_bot(EXTENSION)
    root = find_tree_group(bot, "giveaway_name")
    assert root is not None
    assert "giveaway_blacklist_name" in get_subcommand_names(root)

async def test_nested_group_giveaway_blacklist_name_has_5_commands():
    bot = await load_extension_bot(EXTENSION)
    root = find_tree_group(bot, "giveaway_name")
    nested = find_nested_group(root, "giveaway_blacklist_name")
    assert nested is not None
    assert len(get_subcommand_names(nested)) == 5

async def test_nested_giveaway_blacklist_name_giveaway_bl_add_role_name_registered():
    bot = await load_extension_bot(EXTENSION)
    root = find_tree_group(bot, "giveaway_name")
    nested = find_nested_group(root, "giveaway_blacklist_name")
    assert nested is not None
    assert "giveaway_bl_add_role_name" in get_subcommand_names(nested)

async def test_nested_giveaway_blacklist_name_giveaway_bl_remove_role_name_registered():
    bot = await load_extension_bot(EXTENSION)
    root = find_tree_group(bot, "giveaway_name")
    nested = find_nested_group(root, "giveaway_blacklist_name")
    assert nested is not None
    assert "giveaway_bl_remove_role_name" in get_subcommand_names(nested)

async def test_nested_giveaway_blacklist_name_giveaway_bl_add_user_name_registered():
    bot = await load_extension_bot(EXTENSION)
    root = find_tree_group(bot, "giveaway_name")
    nested = find_nested_group(root, "giveaway_blacklist_name")
    assert nested is not None
    assert "giveaway_bl_add_user_name" in get_subcommand_names(nested)

async def test_nested_giveaway_blacklist_name_giveaway_bl_remove_user_name_registered():
    bot = await load_extension_bot(EXTENSION)
    root = find_tree_group(bot, "giveaway_name")
    nested = find_nested_group(root, "giveaway_blacklist_name")
    assert nested is not None
    assert "giveaway_bl_remove_user_name" in get_subcommand_names(nested)

async def test_nested_giveaway_blacklist_name_giveaway_bl_list_name_registered():
    bot = await load_extension_bot(EXTENSION)
    root = find_tree_group(bot, "giveaway_name")
    nested = find_nested_group(root, "giveaway_blacklist_name")
    assert nested is not None
    assert "giveaway_bl_list_name" in get_subcommand_names(nested)
