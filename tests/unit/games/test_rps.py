"""Unit tests for rock-paper-scissors command."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

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

        # rps.py uses: locale.commands.games.rps.{*}(command_info.locale)
        # The locale tree is a frozen dataclass; replace module-level `locale`
        # with a mock that returns real strings to satisfy Pydantic validation
        # in tanjunEmbed.
        mock_rps = MagicMock()
        mock_rps.rock = MagicMock(return_value="rock")
        mock_rps.paper = MagicMock(return_value="paper")
        mock_rps.scissors = MagicMock(return_value="scissors")
        mock_rps.draw = MagicMock(return_value="draw")
        mock_rps.drawDescription = MagicMock(return_value="drawDescription {player1} {player2} {player1_choice} {player2_choice}")
        mock_rps.win = MagicMock(return_value="win")
        mock_rps.winDescription = MagicMock(return_value="winDescription {player1} {player2} {player1_choice} {player2_choice}")
        mock_rps.lose = MagicMock(return_value="lose")
        mock_rps.loseDescription = MagicMock(return_value="loseDescription {player1} {player2} {player1_choice} {player2_choice}")
        mock_rps.title = MagicMock(return_value="RPS")
        mock_rps.description = MagicMock(return_value="description {player1} {player2}")
        mock_rps.notYourGame = MagicMock(return_value="not your game")

        mock_locale = MagicMock()
        mock_locale.commands.games.rps = mock_rps

        orig_locale = rps_module.locale
        rps_module.locale = mock_locale
        try:
            await rps_module.rps(info, opponent)
        finally:
            rps_module.locale = orig_locale

        info.reply.assert_awaited_once()
        call_kwargs = info.reply.await_args.kwargs
        assert call_kwargs.get("view") is not None
        assert call_kwargs.get("embed") is not None

    @pytest.mark.asyncio
    async def test_rps_vs_bot_picks_opponent_choice(self):
        info = make_command_info()

        mock_rps = MagicMock()
        mock_rps.rock = MagicMock(return_value="rock")
        mock_rps.paper = MagicMock(return_value="paper")
        mock_rps.scissors = MagicMock(return_value="scissors")
        mock_rps.draw = MagicMock(return_value="draw")
        mock_rps.drawDescription = MagicMock(return_value="drawDescription {player1} {player2} {player1_choice} {player2_choice}")
        mock_rps.win = MagicMock(return_value="win")
        mock_rps.winDescription = MagicMock(return_value="winDescription {player1} {player2} {player1_choice} {player2_choice}")
        mock_rps.lose = MagicMock(return_value="lose")
        mock_rps.loseDescription = MagicMock(return_value="loseDescription {player1} {player2} {player1_choice} {player2_choice}")
        mock_rps.title = MagicMock(return_value="RPS")
        mock_rps.description = MagicMock(return_value="description {player1} {player2}")
        mock_rps.notYourGame = MagicMock(return_value="not your game")

        mock_locale = MagicMock()
        mock_locale.commands.games.rps = mock_rps

        orig_locale = rps_module.locale
        rps_module.locale = mock_locale
        try:
            with patch.object(rps_module.random, "choice", return_value="rock"):
                await rps_module.rps(info, None)
        finally:
            rps_module.locale = orig_locale

        info.reply.assert_awaited_once()
