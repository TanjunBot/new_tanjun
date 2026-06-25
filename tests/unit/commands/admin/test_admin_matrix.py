from __future__ import annotations

import pytest

from tests.helpers.command_matrix.iterators import iter_unit_cases
from tests.helpers.command_matrix.models import MatrixCase
from tests.helpers.command_matrix.test_runners import run_unit_matrix_case

pytestmark = pytest.mark.asyncio


def _cases() -> list[MatrixCase]:
    cases: list[MatrixCase] = []
    for group in ['admin_channels_name', 'admin_emoji_name', 'admin_jointocreate_name', 'admin_localegroup_name', 'admin_messaging_name', 'admin_moderation_name', 'admin_purgegroup_name', 'admin_report_name', 'admin_role_name', 'admin_rolemanage_name', 'admin_setup_name', 'admin_triggermessages_name', 'admin_warn_name']:
        cases.extend(iter_unit_cases(group))
    return cases


@pytest.mark.parametrize("case", _cases(), ids=lambda c: c.id)
async def test_admin_unit_matrix(case: MatrixCase) -> None:
    await run_unit_matrix_case(case)
