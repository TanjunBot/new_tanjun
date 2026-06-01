from __future__ import annotations

from diagnostics.specs._helpers import (
    default_member_kwargs,
    default_role_kwargs,
    register_kwargs,
    register_method_commands,
    register_skip,
)


def register() -> None:
    register_skip("giveaway.GiveawayCommands.start", "Launches live giveaway records and messages")

    register_method_commands(
        "giveaway",
        "BlacklistCommands",
        {
            "add_role": "add_blacklist_role",
            "remove_role": "remove_blacklist_role",
            "add_user": "add_blacklist_user",
            "remove_user": "remove_blacklist_user",
            "list": "list_blacklist",
        },
    )
    register_method_commands(
        "giveaway",
        "GiveawayCommands",
        {
            "end": "end_giveaway",
            "reroll": "reroll_giveaway",
            "edit": "edit_giveaway",
        },
    )
    register_kwargs("giveaway.BlacklistCommands.add_role", default_role_kwargs)
    register_kwargs("giveaway.BlacklistCommands.remove_role", default_role_kwargs)
    register_kwargs("giveaway.BlacklistCommands.add_user", default_member_kwargs)
    register_kwargs("giveaway.BlacklistCommands.remove_user", default_member_kwargs)
    register_kwargs("giveaway.GiveawayCommands.end", lambda: {"giveawayid": 1})
    register_kwargs("giveaway.GiveawayCommands.reroll", lambda: {"giveawayid": 1})
    register_kwargs("giveaway.GiveawayCommands.edit", lambda: {"giveawayid": 1, "title": "Prize"})
