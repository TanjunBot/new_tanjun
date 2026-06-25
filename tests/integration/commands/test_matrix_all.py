from __future__ import annotations

import pytest

from diagnostics.registry import all_specs
from tests.helpers.command_matrix.test_runners import run_behavior_spec_test

pytestmark = [pytest.mark.integration, pytest.mark.asyncio]


def _all_specs():
    return [s for s in all_specs() if s.tree_path and not s.skip_reason]


@pytest.mark.parametrize("spec", _all_specs(), ids=lambda s: s.id)
async def test_all_commands_behavior_spec(spec) -> None:
    await run_behavior_spec_test(spec)
