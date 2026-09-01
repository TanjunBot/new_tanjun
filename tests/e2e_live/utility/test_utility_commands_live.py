from __future__ import annotations

import pytest

from tests.helpers.command_matrix.iterators import iter_e2e_live_cases
from tests.helpers.command_matrix.models import MatrixCase
from tests.helpers.domain_assertions.registry import assert_matrix_live_response
from tests.helpers.live_discord.session import LiveGuildSession

pytestmark = [
    pytest.mark.live_discord,
    pytest.mark.live_e2e,
    pytest.mark.live_domain,
    pytest.mark.slow,
    pytest.mark.asyncio,
]


def _cases() -> list[MatrixCase]:
    cases: list[MatrixCase] = []
    for group in ['utility_help_name', 'utilitycmd_name', 'utility_scheduledmessage_name']:
        cases.extend(iter_e2e_live_cases(group))
    return cases


@pytest.mark.parametrize("case", _cases(), ids=lambda c: c.id)
async def test_utility_slash_command_live(case: MatrixCase, live_guild_session: LiveGuildSession) -> None:
    result = await live_guild_session.run_matrix_case(case)
    assert_matrix_live_response(result, case, session=live_guild_session)
