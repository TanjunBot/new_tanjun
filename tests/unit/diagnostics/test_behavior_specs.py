from __future__ import annotations

from unittest.mock import MagicMock

import pytest

import diagnostics.registry as registry_mod
from diagnostics.registry import all_specs, run_spec

pytestmark = pytest.mark.asyncio


def test_discovers_many_behavior_specs() -> None:
    registry_mod._specs_cache = None
    specs = all_specs()
    assert isinstance(specs, list)
    assert len(specs) > 50


async def test_run_spec_handles_unknown_spec() -> None:
    from diagnostics.models import CheckOutcome, CommandBehaviorSpec

    spec = CommandBehaviorSpec(
        id="test.UnknownGroup.unknown_method",
        extension="extensions.administration",
        group_cls=object,
        method_name="nope",
    )
    outcome = await run_spec(spec, MagicMock())
    assert isinstance(outcome, CheckOutcome)
    assert not outcome.passed
