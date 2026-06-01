from __future__ import annotations

import asyncio
import time
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from diagnostics.patches import extension_patches
from diagnostics.prefix_checks import _invoke_prefix_command


@pytest.mark.asyncio
async def test_sync_prefix_invoke_finishes_quickly() -> None:
    from extensions.administration import AdministrationCog

    bot = MagicMock()
    bot.tree = MagicMock()
    bot.tree.walk_commands = MagicMock(return_value=[MagicMock(), MagicMock()])
    bot.tree.sync = AsyncMock(return_value=[])

    cog = AdministrationCog(bot)
    sync = next((c for c in cog.get_commands() if c.name == "sync"), None)
    assert sync is not None

    with patch("config.adminIds", [1001]), extension_patches("extensions.administration"):
        started = time.monotonic()
        await asyncio.wait_for(_invoke_prefix_command(cog, sync, bot), timeout=2.0)

    assert time.monotonic() - started < 1.0