from __future__ import annotations

from tests.helpers.live_e2e.cases._helpers import case

_CHANNEL = {"channel": "__main__"}
_USER = {"user": "__owner__"}

OVERRIDES = {
    "level_config_name level_enable_name": case(
        "level_config_name level_enable_name",
        teardown="level.disable",
    ),
    "level_config_name level_disable_name": case(
        "level_config_name level_disable_name",
        setup="level.enable",
    ),
    "level_config_name level_givexp_name": case(
        "level_config_name level_givexp_name",
        option_overrides={**_USER, "amount": 10},
        setup="level.enable",
    ),
    "level_config_name level_takexp_name": case(
        "level_config_name level_takexp_name",
        option_overrides={**_USER, "amount": 5},
        setup="level.enable_with_xp",
    ),
    "level_config_name level_setlevelupchannel_name": case(
        "level_config_name level_setlevelupchannel_name",
        option_overrides=_CHANNEL,
        setup="level.enable",
        teardown="level.clear_levelup_channel",
    ),
    "level_config_name level_settextcooldown_name": case(
        "level_config_name level_settextcooldown_name",
        option_overrides={"cooldown": 30},
        setup="level.enable",
    ),
    "levelcommands_name level_rank_name": case(
        "levelcommands_name level_rank_name",
        option_overrides=_USER,
        setup="level.enable",
    ),
    "levelcommands_name level_leaderboard_name": case(
        "levelcommands_name level_leaderboard_name",
        setup="level.enable",
    ),
    "level_blacklist_name level_blacklist_addu_name": case(
        "level_blacklist_name level_blacklist_addu_name",
        option_overrides={"user": "__secondary__"},
        setup="level.enable",
        teardown="level.blacklist_remove_user",
    ),
    "level_blacklist_name level_blacklist_removeu_name": case(
        "level_blacklist_name level_blacklist_removeu_name",
        setup="level.blacklist_add_user",
    ),
    "level_boosts_name level_boosts_adduser_name": case(
        "level_boosts_name level_boosts_adduser_name",
        option_overrides={**_USER, "boost": 1.5},
        setup="level.enable",
        teardown="level.boost_remove_user",
    ),
}
