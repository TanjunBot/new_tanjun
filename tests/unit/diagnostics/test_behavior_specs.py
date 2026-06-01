from __future__ import annotations

import asyncio
from unittest.mock import MagicMock

import pytest

from diagnostics.registry import all_specs, run_spec

pytestmark = pytest.mark.asyncio


@pytest.fixture(scope="module")
def behavior_specs():
    return all_specs()


def test_discovers_many_behavior_specs(behavior_specs):
    assert len(behavior_specs) >= 150


@pytest.mark.parametrize("spec", all_specs(), ids=lambda s: s.id)
async def test_behavior_spec(spec):
    outcome = await run_spec(spec, MagicMock())
    if spec.skip_reason:
        assert outcome.skipped
        return
    assert outcome.passed, outcome.message
