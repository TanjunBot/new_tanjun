from __future__ import annotations

from tests.helpers.live_e2e.cases._helpers import case

_CHANNEL = {"channel": "__main__"}

OVERRIDES = {
    "logs_name logs_configure_name": case(
        "logs_name logs_configure_name",
        teardown="logs.remove",
    ),
    "logs_name logs_set_name": case(
        "logs_name logs_set_name",
        option_overrides=_CHANNEL,
        setup="logs.configure",
        teardown="logs.remove",
    ),
    "logs_name logs_remove_name": case(
        "logs_name logs_remove_name",
        setup="logs.configure",
    ),
    "logs_name logs_blacklist_name logs_blacklistc_add_name": case(
        "logs_name logs_blacklist_name logs_blacklistc_add_name",
        option_overrides=_CHANNEL,
        setup="logs.configure",
        teardown="logs.blacklistc_remove",
    ),
    "logs_name logs_blacklist_name logs_blacklistc_remove_name": case(
        "logs_name logs_blacklist_name logs_blacklistc_remove_name",
        setup="logs.blacklistc_add",
    ),
    "logs_name logs_blacklist_name logs_blacklistc_show_name": case(
        "logs_name logs_blacklist_name logs_blacklistc_show_name",
        setup="logs.configure",
    ),
}
