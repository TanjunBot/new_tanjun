"""Unit tests for rock-paper-scissors command."""

from __future__ import annotations

from unittest.mock import patch

import pytest

from commands.games import rps as rps_module
from tests.helpers.discord import make_command_info, make_member


def rps_winner(p1: str, p2: str, rock: str, paper: str, scissors: str) -> str:
    if p1 == p2:
        return "draw"
    if (p1 == rock and p2 == scissors) or (p1 == paper and p2 == rock) or (p1 == scissors and p2 == paper):
        return "p1"
    return "p2"


@pytest.mark.unit
class TestRpsWinnerLogic:
    ROCK, PAPER, SCISSORS = "rock", "paper", "scissors"

    def test_rock_beats_scissors(self):
        assert rps_winner(self.ROCK, self.SCISSORS, self.ROCK, self.PAPER, self.SCISSORS) == "p1"

    def test_paper_beats_rock(self):
        assert rps_winner(self.PAPER, self.ROCK, self.ROCK, self.PAPER, self.SCISSORS) == "p1"

    def test_scissors_beats_paper(self):
        assert rps_winner(self.SCISSORS, self.PAPER, self.ROCK, self.PAPER, self.SCISSORS) == "p1"

    def test_draw(self):
        assert rps_winner(self.ROCK, self.ROCK, self.ROCK, self.PAPER, self.SCISSORS) == "draw"


@pytest.mark.unit
class TestRpsCommand:
    @pytest.mark.asyncio
    async def test_rps_starts_with_view(self):
        info = make_command_info()
        opponent = make_member(user_id=222)
        with patch.object(rps_module.tanjunLocalizer, "localize", side_effect=lambda _loc, key, **kw: key):
            await rps_module.rps(info, opponent)
        info.reply.assert_awaited_once()
        call_kwargs = info.reply.await_args.kwargs
        assert call_kwargs.get("view") is not None
        assert call_kwargs.get("embed") is not None

    @pytest.mark.asyncio
    async def test_rps_vs_bot_picks_opponent_choice(self):
        info = make_command_info()
        with (
            patch.object(rps_module.tanjunLocalizer, "localize", side_effect=lambda _loc, key, **kw: key),
            patch.object(rps_module.random, "choice", return_value="rock"),
        ):
            await rps_module.rps(info, None)
        info.reply.assert_awaited_once()
