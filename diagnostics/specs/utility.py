from __future__ import annotations

from diagnostics.assertions import expect_interaction_or_modal
from diagnostics.mocks import make_attachment, make_member, make_text_channel
from diagnostics.specs._helpers import (
    default_channel_kwargs,
    default_member_kwargs,
    default_role_kwargs,
    register_defer_and_mock,
    register_kwargs,
    register_method_commands,
)
from diagnostics.specs.overrides import SPEC_CUSTOM_ASSERTIONS, SPEC_PATCH_EXCLUDE


def register() -> None:
    register_kwargs("utility.UtilityCog.help_slash", lambda: {})
    register_defer_and_mock("utility.UtilityCog.help_slash", "helpCommand")

    register_kwargs("utility.MessageTrackingCommands.messagetrackingoptout", lambda: {})
    register_kwargs("utility.MessageTrackingCommands.messagetrackingoptin", lambda: {})
    register_method_commands(
        "utility",
        "MessageTrackingCommands",
        {"messagetrackingoptout": "optOutCommand", "messagetrackingoptin": "optInCommand"},
    )

    register_kwargs(
        "utility.BoosterRoleCommands.claimboosterrole",
        lambda: {"name": "role", "color": "#FF0000", "icon": None},
    )
    register_kwargs("utility.BoosterRoleCommands.setupboosterrole", default_role_kwargs)
    register_kwargs("utility.BoosterRoleCommands.deleteboosterrole", lambda: {})
    register_method_commands(
        "utility",
        "BoosterRoleCommands",
        {
            "claimboosterrole": "claimboosterroleCommand",
            "setupboosterrole": "setupboosterroleCommand",
            "deleteboosterrole": "deleteboosterroleCommand",
        },
    )

    register_kwargs("utility.BoosterChannelCommands.setupboosterchannel", default_channel_kwargs)
    register_kwargs("utility.BoosterChannelCommands.claimboosterchannel", lambda: {"name": "vc"})
    register_kwargs("utility.BoosterChannelCommands.deleteboosterchannel", lambda: {})
    register_method_commands(
        "utility",
        "BoosterChannelCommands",
        {
            "setupboosterchannel": "setupboosterchannelCommand",
            "claimboosterchannel": "claimboosterchannelCommand",
            "deleteboosterchannel": "deleteboosterchannelCommand",
        },
    )

    register_kwargs("utility.AutoPublishCommands.autopublish", default_channel_kwargs)
    register_kwargs("utility.AutoPublishCommands.autopublish_remove", default_channel_kwargs)
    register_method_commands(
        "utility",
        "AutoPublishCommands",
        {"autopublish": "autopublishCommand", "autopublish_remove": "autopublishRemoveCommand"},
    )

    brawl_methods = {
        "battlelog": "battlelogCommand",
        "playerinfo": "brawlstarsPlayerInfoCommand",
        "brawlers": "brawlstarsBrawlersCommand",
        "club": "brawlstarsClubCommand",
        "events": "brawlstarsEventsCommand",
        "link": "brawlstarsLinkCommand",
        "unlink": "brawlstarsUnlinkCommand",
    }
    register_method_commands("utility", "BrawlStarsCommands", brawl_methods)
    register_kwargs("utility.BrawlStarsCommands.battlelog", lambda: {"tag": "ABC"})
    register_kwargs("utility.BrawlStarsCommands.playerinfo", lambda: {"tag": "ABC"})
    register_kwargs("utility.BrawlStarsCommands.brawlers", lambda: {"tag": "ABC"})
    register_kwargs("utility.BrawlStarsCommands.club", lambda: {"tag": "ABC"})

    register_method_commands(
        "utility",
        "TwitchCommands",
        {"add": "addTwitchLiveNotificationCommand", "see": "seeTwitchLiveNotificationsCommand"},
    )
    register_kwargs(
        "utility.TwitchCommands.add",
        lambda: {
            "twitchname": "ninja",
            "channel": make_text_channel(),
            "notificationmessage": "live",
        },
    )
    register_kwargs("utility.TwitchCommands.see", lambda: {})

    register_kwargs("utility.UtilityCommands.avatar", default_member_kwargs)
    register_kwargs("utility.UtilityCommands.banner", default_member_kwargs)
    register_kwargs("utility.UtilityCommands.avatardecoration", default_member_kwargs)
    register_kwargs("utility.UtilityCommands.afk", lambda: {"reason": "brb"})
    register_kwargs(
        "utility.UtilityCommands.report",
        lambda: {"user": make_member(), "reason": "a" * 12},
    )
    register_method_commands(
        "utility",
        "UtilityCommands",
        {
            "avatar": "avatarCommand",
            "banner": "bannerCommand",
            "avatardecoration": "avatarDecorationCommand",
            "afk": "afkCommand",
            "report": "reportCommand",
        },
    )
    SPEC_PATCH_EXCLUDE["utility.UtilityCommands.feedback"] = ("feedbackCommand",)
    SPEC_CUSTOM_ASSERTIONS["utility.UtilityCommands.feedback"] = expect_interaction_or_modal

    register_method_commands(
        "utility",
        "ScheduledMessageCommands",
        {
            "schedulemessage": "scheduleMessageCommand",
            "listscheduled": "listScheduledCommand",
            "removescheduled": "removeScheduledCommand",
        },
    )
    register_kwargs(
        "utility.ScheduledMessageCommands.schedulemessage",
        lambda: {
            "content": "hi",
            "sendin": "1h",
            "channel": make_text_channel(),
            "repeatinterval": None,
            "repeatamount": None,
            "attachment1": make_attachment(),
            "attachment2": None,
            "attachment3": None,
            "attachment4": None,
            "attachment5": None,
            "attachment6": None,
            "attachment7": None,
            "attachment8": None,
            "attachment9": None,
            "attachment10": None,
        },
    )
    register_kwargs("utility.ScheduledMessageCommands.removescheduled", lambda: {"messageid": 12345})
