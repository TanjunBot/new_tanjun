from __future__ import annotations

from tests.helpers.live_e2e.cases._helpers import case

_GAMES = (
    "games_advanced_ttt_name",
    "games_akinator_name",
    "games_battleship_name",
    "games_connect4_name",
    "games_flagquiz_name",
    "games_hangman_name",
    "games_memory_name",
    "games_rps_name",
    "games_ttt_name",
    "games_wordle_name",
)

OVERRIDES = {
    f"games_name {name}": case(f"games_name {name}", assert_profile="games")
    for name in _GAMES
}
