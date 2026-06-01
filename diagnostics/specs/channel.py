from __future__ import annotations

from diagnostics.specs._helpers import default_channel_kwargs, register_kwargs, register_method_commands


def register() -> None:
    register_method_commands(
        "channel",
        "WelcomeCommands",
        {"welcome": "setWelcomeChannelCommand", "remove_welcome": "removeWelcomeChannelCommand"},
    )
    register_method_commands(
        "channel",
        "FarewellCommands",
        {
            "set_farewell_channel": "setFarewellChannelCommand",
            "remove_farewell_channel": "removeFarewellChannelCommand",
        },
    )
    register_method_commands(
        "channel",
        "MediaCommands",
        {"media_add_cmd": "addMediaChannelCommand", "media_remove_cmd": "removeMediaChannelCommand"},
    )
    register_method_commands(
        "channel",
        "DynamicslowmodeCommands",
        {
            "add_dynamicslowmode": "addDynamicslowmodeCommand",
            "remove_dynamicslowmode": "removeDynamicslowmodeCommand",
            "get_dynamicslowmode_channels": "getDynamicslowmodeChannelsCommand",
        },
    )
    for method in (
        "welcome",
        "set_farewell_channel",
        "media_add_cmd",
        "media_remove_cmd",
        "add_dynamicslowmode",
        "remove_dynamicslowmode",
    ):
        cls = {
            "welcome": "WelcomeCommands",
            "set_farewell_channel": "FarewellCommands",
            "media_add_cmd": "MediaCommands",
            "media_remove_cmd": "MediaCommands",
            "add_dynamicslowmode": "DynamicslowmodeCommands",
            "remove_dynamicslowmode": "DynamicslowmodeCommands",
        }[method]
        register_kwargs(f"channel.{cls}.{method}", default_channel_kwargs)
