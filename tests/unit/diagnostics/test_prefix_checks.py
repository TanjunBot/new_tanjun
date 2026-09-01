from __future__ import annotations

import asyncio
import sys
import time
import types
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from diagnostics.models import CheckOutcome
from diagnostics.patches import extension_patches
from diagnostics.prefix_checks import _invoke_prefix_command, run_prefix_command_checks
from diagnostics.strict_skips import PREFIX_COMMANDS_EXCLUDED_SET

pytestmark = pytest.mark.asyncio


def _admin_module(cog: MagicMock | None = None) -> types.ModuleType:
    mod = types.ModuleType("extensions.administration")
    mod.AdministrationCog = MagicMock(return_value=cog)
    return mod


async def test_sync_prefix_invoke_finishes_quickly() -> None:
    bot = MagicMock()
    cog = MagicMock()

    async def _sync(*_args: object, **_kwargs: object) -> None:
        return None

    sync = MagicMock()
    sync.name = "sync"
    sync.callback = _sync

    started = time.monotonic()
    await asyncio.wait_for(_invoke_prefix_command(cog, sync, bot), timeout=2.0)
    assert time.monotonic() - started < 1.0


async def test_run_prefix_skips_excluded_commands() -> None:
    bot = MagicMock()
    excluded_name = next(iter(PREFIX_COMMANDS_EXCLUDED_SET - {"test_bot", "benchmark_bot"}))
    cmd_excluded = MagicMock()
    cmd_excluded.name = excluded_name

    cog = MagicMock()
    cog.get_commands = MagicMock(return_value=[cmd_excluded])
    bot.cogs = {"AdministrationCog": cog}

    with patch.dict(sys.modules, {"extensions.administration": _admin_module(cog)}):
        outcomes = await run_prefix_command_checks(bot)
    skipped = [o for o in outcomes if o.skipped and o.skip_allowed]
    assert any(excluded_name in o.check_id for o in skipped)


async def test_run_prefix_no_cog_fails() -> None:
    bot = MagicMock()
    bot.cogs = {}
    mod = _admin_module()
    mod.AdministrationCog = MagicMock(side_effect=RuntimeError("cannot load"))
    with patch.dict(sys.modules, {"extensions.administration": mod}):
        outcomes = await run_prefix_command_checks(bot)
    assert len(outcomes) == 1
    assert not outcomes[0].passed


async def test_run_prefix_command_failure() -> None:
    bot = MagicMock()

    async def _bad(_ctx: object) -> None:
        raise RuntimeError("handler failed")

    cmd = MagicMock()
    cmd.name = "help"
    cmd.callback = _bad

    cog = MagicMock()
    cog.get_commands = MagicMock(return_value=[cmd])
    bot.cogs = {"AdministrationCog": cog}

    with (
        patch.dict(sys.modules, {"extensions.administration": _admin_module(cog)}),
        patch("diagnostics.prefix_checks.extension_patches", side_effect=extension_patches),
        patch("config.adminIds", [1001]),
    ):
        outcomes = await run_prefix_command_checks(bot)

    failed = [o for o in outcomes if not o.passed and not o.skipped]
    assert any("help" in o.check_id for o in failed)
