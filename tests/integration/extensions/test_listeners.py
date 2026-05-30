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

EXTENSION = "extensions.listeners"
COG_NAME = "ListenerCog"

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

async def test_cog_has_listener_on_message():
    bot = await load_extension_bot(EXTENSION, fire_ready=False)
    assert hasattr(bot.cogs[COG_NAME], "on_message")

async def test_cog_has_listener_on_interaction():
    bot = await load_extension_bot(EXTENSION, fire_ready=False)
    assert hasattr(bot.cogs[COG_NAME], "on_interaction")

async def test_cog_has_listener_on_voice_state_update():
    bot = await load_extension_bot(EXTENSION, fire_ready=False)
    assert hasattr(bot.cogs[COG_NAME], "on_voice_state_update")

async def test_cog_has_listener_on_message_edit():
    bot = await load_extension_bot(EXTENSION, fire_ready=False)
    assert hasattr(bot.cogs[COG_NAME], "on_message_edit")

async def test_cog_has_listener_on_message_delete():
    bot = await load_extension_bot(EXTENSION, fire_ready=False)
    assert hasattr(bot.cogs[COG_NAME], "on_message_delete")

async def test_cog_has_listener_on_member_join():
    bot = await load_extension_bot(EXTENSION, fire_ready=False)
    assert hasattr(bot.cogs[COG_NAME], "on_member_join")

async def test_cog_has_listener_on_member_remove():
    bot = await load_extension_bot(EXTENSION, fire_ready=False)
    assert hasattr(bot.cogs[COG_NAME], "on_member_remove")
