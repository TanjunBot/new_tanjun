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

EXTENSION = "extensions.health_check"

async def test_module_exposes_setup():
    module = importlib.import_module(EXTENSION)
    assert hasattr(module, "setup")
    assert callable(module.setup)

async def test_setup_completes_without_cog():
    bot = make_bot_for_extensions()
    await load_extension(bot, EXTENSION)
    bot.add_cog.assert_not_awaited()
    assert bot.cogs == {}

async def test_module_exposes_BackgroundLoopHealthCheck():
    module = importlib.import_module(EXTENSION)
    assert hasattr(module, "BackgroundLoopHealthCheck")

async def test_BackgroundLoopHealthCheck_has_run_method():
    module = importlib.import_module(EXTENSION)
    check = module.BackgroundLoopHealthCheck(make_bot_for_extensions())
    assert hasattr(check, "run")
    assert check.name == "Background Loops"
    assert check.critical is True
