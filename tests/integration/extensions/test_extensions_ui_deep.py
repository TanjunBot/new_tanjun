from __future__ import annotations

import pytest

from tests.integration.extensions.conftest import load_extension_bot

pytestmark = pytest.mark.asyncio

EXTENSIONS_WITH_SETUP = [
    "extensions.setup_wizards",
    "extensions.logs",
]


@pytest.mark.parametrize("extension", EXTENSIONS_WITH_SETUP)
async def test_extension_loads_and_registers_commands(extension: str) -> None:
    bot = await load_extension_bot(extension, fire_ready=True)
    assert bot.cogs


async def test_setup_wizards_tree_has_logs_command() -> None:
    bot = await load_extension_bot("extensions.setup_wizards", fire_ready=True)
    cog = bot.cogs.get("SetupWizardsCog")
    assert cog is not None
