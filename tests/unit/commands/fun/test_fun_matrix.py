from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest

from commands.fun.funcommands import fun_command
from tests.helpers.command_matrix.iterators import iter_unit_cases
from tests.helpers.command_matrix.models import MatrixCase
from tests.helpers.command_matrix.test_runners import run_unit_matrix_case
from tests.helpers.discord import make_member
from tests.helpers.fun_assertions import assert_invalid_fun_embed, embed_from_reply
from tests.helpers.fun_command_info import command_info_for_profile

pytestmark = pytest.mark.asyncio


def _cases() -> list[MatrixCase]:
    return list(iter_unit_cases("funcmd_name"))


@pytest.mark.parametrize("case", _cases(), ids=lambda c: c.id)
async def test_fun_unit_matrix(case: MatrixCase) -> None:
    await run_unit_matrix_case(case)


@patch("commands.fun.funcommands.utility.getGif", new_callable=AsyncMock)
async def test_fun_invalid_action(mock_gif: AsyncMock) -> None:
    mock_gif.return_value = []
    info = command_info_for_profile("admin")
    target = make_member(user_id=222222222222222222, name="TargetUser")
    await fun_command(info, "not_a_real_action", target, None)
    assert_invalid_fun_embed(embed_from_reply(info.reply))
    mock_gif.assert_not_awaited()
