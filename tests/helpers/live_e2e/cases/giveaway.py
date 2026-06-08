from __future__ import annotations

from tests.helpers.live_e2e.cases._helpers import case

OVERRIDES = {
    "giveaway_name giveaway_start_name": case(
        "giveaway_name giveaway_start_name",
        option_overrides={
            "duration": 120,
            "winners": 1,
            "prize": "e2e prize",
            "channel": "__main__",
        },
        teardown="giveaway.end",
    ),
    "giveaway_name giveaway_end_name": case(
        "giveaway_name giveaway_end_name",
        setup="giveaway.start",
    ),
    "giveaway_name giveaway_edit_name": case(
        "giveaway_name giveaway_edit_name",
        setup="giveaway.start",
        option_overrides={"prize": "edited prize"},
        teardown="giveaway.end",
    ),
    "giveaway_name giveaway_reroll_name": case(
        "giveaway_name giveaway_reroll_name",
        setup="giveaway.ended",
    ),
    "giveaway_name giveaway_blacklist_name giveaway_bl_add_user_name": case(
        "giveaway_name giveaway_blacklist_name giveaway_bl_add_user_name",
        option_overrides={"user": "__secondary__"},
        teardown="giveaway.bl_remove_user",
    ),
    "giveaway_name giveaway_blacklist_name giveaway_bl_remove_user_name": case(
        "giveaway_name giveaway_blacklist_name giveaway_bl_remove_user_name",
        setup="giveaway.bl_add_user",
    ),
    "giveaway_name giveaway_blacklist_name giveaway_bl_list_name": case(
        "giveaway_name giveaway_blacklist_name giveaway_bl_list_name",
    ),
}
