from __future__ import annotations

import pytest

from tests.helpers.command_matrix.iterators import iter_unit_cases
from tests.helpers.command_matrix.models import MatrixCase
from tests.helpers.command_matrix.test_runners import run_unit_matrix_case

pytestmark = pytest.mark.asyncio


def _cases() -> list[MatrixCase]:
    cases: list[MatrixCase] = []
    for group in ['logs_name']:
        cases.extend(iter_unit_cases(group))
    return cases


@pytest.mark.parametrize("case", _cases(), ids=lambda c: c.id)
async def test_logs_unit_matrix(case: MatrixCase) -> None:
    await run_unit_matrix_case(case)
