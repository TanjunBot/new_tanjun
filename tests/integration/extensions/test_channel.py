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

EXTENSION = "extensions.channel"
COG_NAME = "ChannelCog"


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


async def test_root_command_name_is_channel_name():
    bot = await load_extension_bot(EXTENSION)
    assert get_tree_command_names(bot) == ["channel_name"]


async def test_root_group_has_4_entries():
    bot = await load_extension_bot(EXTENSION)
    root = find_tree_group(bot, "channel_name")
    assert root is not None
    assert len(get_subcommand_names(root)) == 4


async def test_subcommand_channel_welcome_name_registered():
    bot = await load_extension_bot(EXTENSION)
    root = find_tree_group(bot, "channel_name")
    assert root is not None
    assert "channel_welcome_name" in get_subcommand_names(root)


async def test_subcommand_channel_farewell_name_registered():
    bot = await load_extension_bot(EXTENSION)
    root = find_tree_group(bot, "channel_name")
    assert root is not None
    assert "channel_farewell_name" in get_subcommand_names(root)


async def test_subcommand_channel_media_name_registered():
    bot = await load_extension_bot(EXTENSION)
    root = find_tree_group(bot, "channel_name")
    assert root is not None
    assert "channel_media_name" in get_subcommand_names(root)


async def test_subcommand_channel_ds_name_registered():
    bot = await load_extension_bot(EXTENSION)
    root = find_tree_group(bot, "channel_name")
    assert root is not None
    assert "channel_ds_name" in get_subcommand_names(root)
