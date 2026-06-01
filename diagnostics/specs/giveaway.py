from __future__ import annotations

from diagnostics.specs._helpers import register_skip


def register() -> None:
    register_skip("giveaway.GiveawayCommands.create", "Creates live giveaway records and messages")
