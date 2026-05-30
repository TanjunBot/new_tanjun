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

EXTENSION = "extensions.games"
COG_NAME = "GameCog"


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


async def test_root_command_name_is_games_name():
    bot = await load_extension_bot(EXTENSION)
    assert get_tree_command_names(bot) == ["games_name"]


async def test_root_group_has_7_entries():
    bot = await load_extension_bot(EXTENSION)
    root = find_tree_group(bot, "games_name")
    assert root is not None
    assert len(get_subcommand_names(root)) == 7


async def test_subcommand_games_ttt_name_registered():
    bot = await load_extension_bot(EXTENSION)
    root = find_tree_group(bot, "games_name")
    assert root is not None
    assert "games_ttt_name" in get_subcommand_names(root)


async def test_subcommand_games_connect4_name_registered():
    bot = await load_extension_bot(EXTENSION)
    root = find_tree_group(bot, "games_name")
    assert root is not None
    assert "games_connect4_name" in get_subcommand_names(root)


async def test_subcommand_games_akinator_name_registered():
    bot = await load_extension_bot(EXTENSION)
    root = find_tree_group(bot, "games_name")
    assert root is not None
    assert "games_akinator_name" in get_subcommand_names(root)


async def test_subcommand_games_wordle_name_registered():
    bot = await load_extension_bot(EXTENSION)
    root = find_tree_group(bot, "games_name")
    assert root is not None
    assert "games_wordle_name" in get_subcommand_names(root)


async def test_subcommand_hangman_name_registered():
    bot = await load_extension_bot(EXTENSION)
    root = find_tree_group(bot, "games_name")
    assert root is not None
    assert "hangman_name" in get_subcommand_names(root)


async def test_subcommand_games_flagquiz_name_registered():
    bot = await load_extension_bot(EXTENSION)
    root = find_tree_group(bot, "games_name")
    assert root is not None
    assert "games_flagquiz_name" in get_subcommand_names(root)


async def test_subcommand_games_rps_name_registered():
    bot = await load_extension_bot(EXTENSION)
    root = find_tree_group(bot, "games_name")
    assert root is not None
    assert "games_rps_name" in get_subcommand_names(root)
