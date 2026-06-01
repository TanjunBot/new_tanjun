from __future__ import annotations

from diagnostics.specs._helpers import default_member_kwargs, register_kwargs, register_method_commands

_FUN_METHODS = (
    "hug",
    "kiss",
    "boop",
    "wave",
    "slap",
    "laugh",
    "tickle",
    "pat",
    "poke",
)


def register() -> None:
    for method in _FUN_METHODS:
        register_kwargs(f"fun.FunCommands.{method}", default_member_kwargs)
    register_method_commands(
        "fun",
        "FunCommands",
        {method: "fun_command" for method in _FUN_METHODS},
    )
