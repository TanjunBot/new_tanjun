from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

import extensions.games as games_ext
from extensions.games import GameCommands
from tests.helpers.discord import make_interaction, make_member
from tests.helpers.extensions import invoke_interaction_command
from tests.integration.extensions.conftest import load_extension_bot

pytestmark = pytest.mark.asyncio

EXTENSION = "extensions.games"


@pytest.fixture
def mock_cmds():
    patches = []
    for name in dir(games_ext):
        if name in ("tic_tac_toe", "connect4", "akinator", "wordle", "hangman", "flag_quiz", "rps"):
            patches.append(patch.object(games_ext, name, new=AsyncMock()))
    for p in patches:
        p.start()
    yield
    for p in patches:
        p.stop()


def _choice(value: str) -> MagicMock:
    c = MagicMock()
    c.value = value
    return c


@pytest.mark.parametrize(
    "method,extra",
    [
        ("tic_tac_toe_cmd", {"user": make_member()}),
        ("connect4_cmd", {"user": make_member(), "size": _choice("7,6")}),
        ("connect4_cmd", {"user": make_member(), "size": _choice("8,7")}),
        ("akinator_cmd", {"theme": _choice("characters")}),
        ("wordle_cmd", {"language": _choice("en")}),
        ("hangman_cmd", {"language": _choice("en")}),
        ("flag_quiz_cmd", {}),
        ("rps_cmd", {"user": make_member()}),
    ],
    ids=["ttt", "c4default", "c4size", "aki", "wordle", "hangman", "flag", "rps"],
)
async def test_games_commands(method, extra, mock_cmds) -> None:
    group = GameCommands(name="games", description="games")
    handler = getattr(group, method)
    await invoke_interaction_command(handler, extra_kwargs=extra)


async def test_games_cog_on_ready(mock_cmds) -> None:
    bot = await load_extension_bot(EXTENSION, fire_ready=True)
    assert bot.tree.add_command.called
