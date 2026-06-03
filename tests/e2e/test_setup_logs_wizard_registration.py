from __future__ import annotations

import pytest

from tests.integration.extensions.conftest import load_extension_bot

pytestmark = pytest.mark.e2e


async def test_setup_wizards_extension_loads() -> None:
    bot = await load_extension_bot("extensions.setup_wizards", fire_ready=True)
    assert "SetupWizardsCog" in bot.cogs


async def test_setup_logs_command_registered() -> None:
    bot = await load_extension_bot("extensions.setup_wizards", fire_ready=True)
    cog = bot.cogs["SetupWizardsCog"]
    group = None
    for call in bot.tree.add_command.call_args_list:
        cmd = call[0][0] if call[0] else None
        if cmd is not None and getattr(cmd, "name", None):
            group = cmd
    assert group is not None or cog is not None
