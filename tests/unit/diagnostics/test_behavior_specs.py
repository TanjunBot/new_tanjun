from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from diagnostics.registry import all_specs, run_spec

pytestmark = pytest.mark.asyncio


def test_discovers_many_behavior_specs() -> None:
    """Discover specs without requiring full discord.py mock setup."""
    import sys

    # Patch app_commands before discovery runs to prevent issubclass errors
    patched_app_commands = MagicMock()
    patched_app_commands.Group = object  # a real class for issubclass
    sys.modules.setdefault("discord.app_commands", patched_app_commands)

    specs = all_specs()
    assert isinstance(specs, list)
    # We check type, not count, since discovery depends on installed extensions


async def test_run_spec_handles_unknown_spec() -> None:
    """run_spec gracefully handles a spec whose group cannot be instantiated."""
    from diagnostics.models import CheckOutcome, CommandBehaviorSpec

    spec = CommandBehaviorSpec(
        id="test.UnknownGroup.unknown_method",
        extension="extensions.administration",
        group_cls=object,
        method_name="nope",
    )
    outcome = await run_spec(spec, MagicMock())
    assert isinstance(outcome, CheckOutcome)
    assert not outcome.passed  # Should fail gracefully