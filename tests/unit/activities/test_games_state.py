import asyncio

import pytest

from activities.base import Player
from activities.games.connect4 import Connect4Game
from activities.games.rps import RPSGame
from activities.games.tictactoe import TicTacToeGame


def players():
    return Player(user_id="host", username="host", display_name="Host", is_host=True), Player(
        user_id="guest", username="guest", display_name="Guest"
    )


@pytest.mark.asyncio
async def test_tictactoe_rejects_non_host_reset_and_malformed_config():
    host, guest = players()
    game = TicTacToeGame("s", host)
    game.add_player(guest)

    result = await game.handle_action("guest", "restart", {})
    assert result["error"].startswith("Only the host")

    result = await game.handle_action("host", "start", {"difficulty": "not-a-number"})
    assert result["error"] == "Invalid difficulty"


@pytest.mark.asyncio
async def test_connect4_rejects_malformed_configuration_without_mutating_board():
    host, guest = players()
    game = Connect4Game("s", host)
    game.add_player(guest)

    result = await game.handle_action("host", "start", {"rows": "invalid"})
    assert result["error"] == "Invalid game configuration"
    assert game.board == [""] * (6 * 7)


@pytest.mark.asyncio
async def test_rps_rejects_duplicate_pick_and_invalid_target():
    host, guest = players()
    game = RPSGame("s", host)
    game.add_player(guest)

    result = await game.handle_action("host", "start", {"target_wins": 0})
    assert result["error"] == "Target wins must be between 1 and 100"
    await game.handle_action("host", "start", {})

    assert (await game.handle_action("host", "pick", {"choice": "rock"}))["status"] == "picked"
    result = await game.handle_action("host", "pick", {"choice": "paper"})
    assert result["error"] == "You have already picked this round"


@pytest.mark.asyncio
async def test_concurrent_tictactoe_moves_are_serialized():
    host, guest = players()
    game = TicTacToeGame("s", host)
    game.add_player(guest)
    await game.handle_action("host", "start", {})

    first, second = await asyncio.gather(
        game.handle_action("host", "move", {"cell": 0}),
        game.handle_action("host", "move", {"cell": 1}),
    )
    assert sorted(result.get("status") for result in (first, second)) == ["error", "moved"]
