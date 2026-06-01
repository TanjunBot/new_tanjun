from __future__ import annotations


def load_all() -> None:
    from diagnostics.specs import (
        admin,
        ai,
        channel,
        fun,
        games,
        giveaway,
        image,
        level,
        logs,
        math,
        minigames,
        setup_wizards,
        utility,
    )

    for mod in (
        games,
        minigames,
        fun,
        math,
        image,
        admin,
        utility,
        channel,
        level,
        logs,
        giveaway,
        ai,
        setup_wizards,
    ):
        mod.register()
