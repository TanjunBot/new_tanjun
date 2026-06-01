from __future__ import annotations

from diagnostics.mocks import make_choice, make_member
from diagnostics.specs._helpers import register_kwargs, register_method_commands


def register() -> None:
    def _member():
        return make_member()

    register_kwargs("games.GameCommands.tic_tac_toe_cmd", lambda: {"user": _member()})
    register_kwargs("games.GameCommands.connect4_cmd", lambda: {"user": _member(), "size": make_choice("7,6")})
    register_kwargs("games.GameCommands.akinator_cmd", lambda: {"theme": make_choice("characters")})
    register_kwargs("games.GameCommands.wordle_cmd", lambda: {"language": make_choice("own")})
    register_kwargs("games.GameCommands.hangman_cmd", lambda: {"language": make_choice("own")})
    register_kwargs("games.GameCommands.rps_cmd", lambda: {"user": _member()})
    register_kwargs("games.GameCommands.battleship_cmd", lambda: {"user": _member()})
    register_kwargs("games.GameCommands.advanced_ttt_cmd", lambda: {"user": _member()})
    register_kwargs("games.GameCommands.flag_quiz_cmd", {})
    register_kwargs("games.GameCommands.memory_cmd", {})

    register_method_commands(
        "games",
        "GameCommands",
        {
            "tic_tac_toe_cmd": "tic_tac_toe",
            "connect4_cmd": "connect4",
            "akinator_cmd": "akinator",
            "wordle_cmd": "wordle",
            "hangman_cmd": "hangman",
            "flag_quiz_cmd": "flag_quiz",
            "rps_cmd": "rps",
            "battleship_cmd": "battleship",
            "memory_cmd": "memory",
            "advanced_ttt_cmd": "advanced_tic_tac_toe",
        },
    )
