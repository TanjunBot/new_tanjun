from __future__ import annotations

from tests.helpers.live_e2e.cases._helpers import case

OVERRIDES = {
    "utility_help_name": case("utility_help_name"),
    "utilitycmd_name utility_avatar_name": case(
        "utilitycmd_name utility_avatar_name",
        option_overrides={"user": "__owner__"},
    ),
    "utilitycmd_name utility_banner_name": case(
        "utilitycmd_name utility_banner_name",
        option_overrides={"user": "__owner__"},
    ),
    "utilitycmd_name utility_afk_name": case(
        "utilitycmd_name utility_afk_name",
        option_overrides={"reason": "e2e"},
        teardown="utility.clear_afk",
    ),
    "utilitycmd_name utility_feedback_name": case(
        "utilitycmd_name utility_feedback_name",
        option_overrides={"content": "e2e feedback"},
    ),
    "utilitycmd_name utility_report_name": case(
        "utilitycmd_name utility_report_name",
        option_overrides={"content": "e2e report"},
    ),
    "utilitycmd_name utility_twitch_name utility_twitch_add_name": case(
        "utilitycmd_name utility_twitch_name utility_twitch_add_name",
        option_overrides={"twitchname": "shroud", "notificationmessage": "live"},
        teardown="utility.twitch_remove",
    ),
    "utilitycmd_name utility_twitch_name utility_twitch_see_name": case(
        "utilitycmd_name utility_twitch_name utility_twitch_see_name",
        setup="utility.twitch_add",
    ),
    "utilitycmd_name utility_bs_name utility_bs_playerinfo_name": case(
        "utilitycmd_name utility_bs_name utility_bs_playerinfo_name",
        option_overrides={"tag": "#ABC123"},
    ),
    "utility_scheduledmessage_name utility_schedulemessage_name": case(
        "utility_scheduledmessage_name utility_schedulemessage_name",
        option_overrides={"content": "e2e scheduled", "sendin": "1h"},
        teardown="utility.remove_scheduled",
    ),
    "utility_scheduledmessage_name utility_listscheduled_name": case(
        "utility_scheduledmessage_name utility_listscheduled_name",
    ),
    "utility_scheduledmessage_name utility_removescheduled_name": case(
        "utility_scheduledmessage_name utility_removescheduled_name",
        setup="utility.schedule_message",
    ),
}
