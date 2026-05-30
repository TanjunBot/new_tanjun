import pytest

from commands.math.calc import calc

pytestmark = pytest.mark.asyncio


@pytest.mark.parametrize(
    "expression,has_error",
    [
        ("2+2", False),
        ("10/0", True),
        ("sqrt(16)", False),
        ("invalid!!!", True),
    ],
)
async def test_calc_expressions(admin_command_info, expression, has_error):
    await calc(admin_command_info, expression)
    admin_command_info.reply.assert_awaited_once()
    embed = admin_command_info.reply.await_args.kwargs["embed"]
    assert embed is not None
