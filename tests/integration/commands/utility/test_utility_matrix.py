from __future__ import annotations

import pytest

from tests.helpers.command_matrix.iterators import iter_integration_cases
from tests.helpers.command_matrix.models import MatrixCase
from tests.helpers.command_matrix.test_runners import run_integration_matrix_case

pytestmark = [pytest.mark.integration, pytest.mark.asyncio]


def _cases() -> list[MatrixCase]:
    cases: list[MatrixCase] = []
    for group in ['utility_help_name', 'utilitycmd_name', 'utility_scheduledmessage_name']:
        cases.extend(iter_integration_cases(group))
    return cases


@pytest.mark.parametrize("case", _cases(), ids=lambda c: c.id)
async def test_utility_integration_matrix(case: MatrixCase) -> None:
    await run_integration_matrix_case(case)
