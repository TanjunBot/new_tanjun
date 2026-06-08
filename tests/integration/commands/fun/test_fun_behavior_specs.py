from __future__ import annotations

import pytest

import diagnostics.registry as registry_mod
from diagnostics.registry import all_specs, run_spec
from tests.helpers.extension_loader import make_bot_for_extensions

pytestmark = [pytest.mark.integration, pytest.mark.asyncio]


def _can_discover_specs() -> bool:
    from discord import app_commands

    return isinstance(app_commands.Group, type)


def pytest_generate_tests(metafunc: pytest.Metafunc) -> None:
    if "spec" not in metafunc.fixturenames:
        return
    if not _can_discover_specs():
        return
    registry_mod.clear_spec_cache()
    try:
        from tests.helpers.fun_matrix import FUN_ACTIONS

        specs = [
            s
            for s in all_specs()
            if s.id.startswith("fun.FunCommands.")
            and s.method_name in FUN_ACTIONS
        ]
    except Exception:
        return
    metafunc.parametrize("spec", specs, ids=lambda item: item.id)


@pytest.fixture
def behavior_bot():
    return make_bot_for_extensions()


async def test_fun_behavior_spec(spec, behavior_bot) -> None:
    if not _can_discover_specs():
        pytest.skip("discord.app_commands.Group is not a real class in this test environment")
    outcome = await run_spec(spec, behavior_bot)
    assert outcome.passed, outcome.message
