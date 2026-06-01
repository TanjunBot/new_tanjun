from __future__ import annotations

from diagnostics.specs._helpers import default_channel_kwargs, register_kwargs, register_method_commands


def register() -> None:
    groups = (
        (
            "CountingCommands",
            {
                "setcountingchannel": "setCountingChannelCommand",
                "removecountingchannel": "removeCountingChannelCommand",
                "setcountingprogress": "setCountingProgressCommand",
            },
        ),
        (
            "CountingChallengeCommands",
            {
                "setcountingchallengechannel": "setCountingChallengeChannelCommand",
                "removecountingchallengechannel": "removeCountingChallengeChannelCommand",
                "setcountingchallengeprogress": "setCountingChallengeProgressCommand",
            },
        ),
        (
            "CountingModesCommands",
            {
                "setcountingmodeschannel": "setCountingModesChannelCommand",
                "removecountingmodeschannel": "removeCountingModesChannelCommand",
                "setcountingmodesprogress": "setCountingModesProgressCommand",
            },
        ),
        (
            "WordChainCommands",
            {
                "setwordchainchannel": "setWordChainChannelCommand",
                "removewordchainchannel": "removeWordChainChannelCommand",
            },
        ),
    )
    for cls, mapping in groups:
        for method in mapping:
            register_kwargs(f"minigames.{cls}.{method}", default_channel_kwargs)
        register_method_commands("minigames", cls, mapping)
