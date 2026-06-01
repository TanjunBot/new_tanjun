from __future__ import annotations

from diagnostics.specs._helpers import (
    default_channel_kwargs,
    default_member_kwargs,
    default_role_kwargs,
    register_kwargs,
    register_method_commands,
)


def register() -> None:
    register_method_commands(
        "logs",
        "ChannelBlacklistCommands",
        {
            "add_blacklist_channel_cmd": "blacklist_channel",
            "remove_blacklist_channel_cmd": "blacklist_remove_channel",
            "show_blacklist_channel_cmd": "blacklist_list_channel",
        },
    )
    register_method_commands(
        "logs",
        "UserBlacklistCommands",
        {
            "add_blacklist_user_cmd": "blacklist_user",
            "remove_blacklist_user_cmd": "blacklist_remove_user",
            "show_blacklist_user_cmd": "blacklist_list_user",
        },
    )
    register_method_commands(
        "logs",
        "RoleBlacklistCommands",
        {
            "add_blacklist_role_cmd": "blacklist_role",
            "remove_blacklist_role_cmd": "blacklist_remove_role",
            "show_blacklist_role_cmd": "blacklist_list_role",
        },
    )
    register_method_commands(
        "logs",
        "VoiceBlacklistCommands",
        {
            "add_blacklist_voice_cmd": "blacklist_voice",
            "remove_blacklist_voice_cmd": "blacklist_remove_voice",
            "show_blacklist_voice_cmd": "blacklist_list_voice",
        },
    )
    register_method_commands(
        "logs",
        "CategoryBlacklistCommands",
        {
            "add_blacklist_category_cmd": "blacklist_category",
            "remove_blacklist_category_cmd": "blacklist_remove_category",
            "show_blacklist_category_cmd": "blacklist_list_category",
        },
    )
    register_method_commands(
        "logs",
        "LogsCommands",
        {
            "set_log_channel_cmd": "set_log_channel",
            "remove_log_channel_cmd": "remove_log_channel",
            "configure_logs_cmd": "configure_logs",
        },
    )
    register_kwargs("logs.ChannelBlacklistCommands.add_blacklist_channel_cmd", default_channel_kwargs)
    register_kwargs("logs.ChannelBlacklistCommands.remove_blacklist_channel_cmd", default_channel_kwargs)
    register_kwargs("logs.UserBlacklistCommands.add_blacklist_user_cmd", default_member_kwargs)
    register_kwargs("logs.UserBlacklistCommands.remove_blacklist_user_cmd", default_member_kwargs)
    register_kwargs("logs.RoleBlacklistCommands.add_blacklist_role_cmd", default_role_kwargs)
    register_kwargs("logs.RoleBlacklistCommands.remove_blacklist_role_cmd", default_role_kwargs)
    register_kwargs("logs.VoiceBlacklistCommands.add_blacklist_voice_cmd", default_channel_kwargs)
    register_kwargs("logs.VoiceBlacklistCommands.remove_blacklist_voice_cmd", default_channel_kwargs)
    register_kwargs("logs.CategoryBlacklistCommands.add_blacklist_category_cmd", default_channel_kwargs)
    register_kwargs("logs.CategoryBlacklistCommands.remove_blacklist_category_cmd", default_channel_kwargs)
    register_kwargs("logs.LogsCommands.set_log_channel_cmd", default_channel_kwargs)
