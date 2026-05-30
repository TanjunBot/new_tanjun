from __future__ import annotations

import importlib

import pytest

from tests.integration.extensions.conftest import load_extension_bot

pytestmark = pytest.mark.asyncio

EXTENSION = "extensions.administration"
COG_NAME = "AdministrationCog"


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


async def test_cog_has_prefix_command_sync():
    bot = await load_extension_bot(EXTENSION, fire_ready=False)
    assert hasattr(bot.cogs[COG_NAME], "sync")
