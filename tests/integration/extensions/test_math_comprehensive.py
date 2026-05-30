from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

import extensions.math as math_ext
from extensions.math import MathCommands, num2wordLocaleAutocomplete
from tests.helpers.extensions import invoke_interaction_command
from tests.integration.extensions.conftest import load_extension_bot

pytestmark = pytest.mark.asyncio

EXTENSION = "extensions.math"

PATCH_NAMES = [
    "calcCommand",
    "calculator_command",
    "faculty_command",
    "num2word_command",
    "plot_function_command",
    "random_number_command",
]


@pytest.fixture
def mock_cmds():
    patches = [patch.object(math_ext, name, new=AsyncMock()) for name in PATCH_NAMES]
    for p in patches:
        p.start()
    yield
    for p in patches:
        p.stop()


@pytest.mark.parametrize(
    "method,extra",
    [
        ("calc", {"expression": "2+2"}),
        ("calculator", {"equation": "2+2"}),
        ("faculty", {"number": 5}),
        ("plot_function", {"func": "x**2"}),
        ("random_number", {"min": 1, "max": 10}),
    ],
    ids=["calc", "calculator", "faculty", "plot", "random"],
)
async def test_math_commands(method, extra, mock_cmds) -> None:
    group = MathCommands(name="math", description="math")
    await invoke_interaction_command(getattr(group, method), extra_kwargs=extra)


async def test_num2word_autocomplete(mock_cmds) -> None:
    choices = await num2wordLocaleAutocomplete(MagicMock(), "en")
    assert len(choices) >= 1


async def test_math_cog_on_ready(mock_cmds) -> None:
    bot = await load_extension_bot(EXTENSION, fire_ready=True)
    assert bot.tree.add_command.called
