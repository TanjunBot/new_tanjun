from __future__ import annotations

from diagnostics.specs._helpers import (
    default_channel_kwargs,
    default_image_kwargs,
    default_member_kwargs,
    default_role_kwargs,
    register_kwargs,
    register_method_commands,
)


def register() -> None:
    register_method_commands(
        "level",
        "BlacklistCommands",
        {
            "add_channel": "add_channel_to_blacklist_command",
            "remove_channel": "remove_channel_from_blacklist_command",
            "add_role": "add_role_to_blacklist_command",
            "remove_role": "remove_role_from_blacklist_command",
            "add_user": "add_user_to_blacklist_command",
            "remove_user": "remove_user_from_blacklist_command",
            "show": "show_blacklist_command",
        },
    )
    for method in (
        "add_channel",
        "remove_channel",
        "add_role",
        "remove_role",
        "add_user",
        "remove_user",
    ):
        spec = f"level.BlacklistCommands.{method}"
        kwargs = default_channel_kwargs if "channel" in method else default_role_kwargs()
        if "user" in method:
            kwargs = default_member_kwargs()
        register_kwargs(spec, kwargs)

    boost_methods = {
        "add_role_boost": "add_role_boost_command",
        "add_channel_boost": "add_channel_boost_command",
        "add_user_boost": "add_user_boost_command",
        "remove_role_boost": "remove_role_boost_command",
        "remove_channel_boost": "remove_channel_boost_command",
        "remove_user_boost": "remove_user_boost_command",
        "show_boosts": "show_boosts_command",
        "calculate_user_channel_boost": "calculate_user_channel_boost_command",
    }
    register_method_commands("level", "LevelBoostCommands", boost_methods)
    register_kwargs("level.LevelBoostCommands.add_role_boost", lambda: {**default_role_kwargs(), "boost": 2.0, "additive": False})
    register_kwargs(
        "level.LevelBoostCommands.add_channel_boost", lambda: {**default_channel_kwargs(), "boost": 2.0, "additive": False}
    )
    register_kwargs(
        "level.LevelBoostCommands.add_user_boost", lambda: {**default_member_kwargs(), "boost": 2.0, "additive": False}
    )
    register_kwargs("level.LevelBoostCommands.remove_role_boost", default_role_kwargs)
    register_kwargs("level.LevelBoostCommands.remove_channel_boost", default_channel_kwargs)
    register_kwargs("level.LevelBoostCommands.remove_user_boost", default_member_kwargs)
    register_kwargs(
        "level.LevelBoostCommands.calculate_user_channel_boost",
        lambda: {**default_member_kwargs(), **default_channel_kwargs()},
    )

    config_methods = {
        "disablelevelsystem": "disableLevelSystemCommand",
        "enablelevelsystem": "enableLevelSystemCommand",
        "changelevelupmessage": "changeLevelupMessageCommand",
        "disablelevelupmessage": "disableLevelupMessageCommand",
        "enablelevelupmessage": "enableLevelupMessageCommand",
        "setlevelupchannel": "setLevelupChannelCommand",
        "changexpscaling": "change_xp_scaling_command",
        "showxpscalings": "show_xp_scalings",
        "addlevelrole": "add_level_role_command",
        "removelevelrole": "remove_level_role_command",
        "showlevelroles": "show_level_roles_command",
        "give_xp": "give_xp_command",
        "take_xp": "take_xp_command",
        "settextcooldown": "set_text_cooldown_command",
        "setvoicecooldown": "set_voice_cooldown_command",
    }
    register_method_commands("level", "LevelConfigCommands", config_methods)
    register_kwargs("level.LevelConfigCommands.changelevelupmessage", lambda: {"newmessage": "Welcome {user}!"})
    register_kwargs(
        "level.LevelConfigCommands.changexpscaling", lambda: {"scaling": "linear", "customformula": None}
    )
    register_kwargs("level.LevelConfigCommands.addlevelrole", lambda: {**default_role_kwargs(), "level": 5})
    register_kwargs("level.LevelConfigCommands.removelevelrole", default_role_kwargs)
    register_kwargs("level.LevelConfigCommands.give_xp", lambda: {**default_member_kwargs(), "amount": 100})
    register_kwargs("level.LevelConfigCommands.take_xp", lambda: {**default_member_kwargs(), "amount": 50})
    register_kwargs("level.LevelConfigCommands.setlevelupchannel", default_channel_kwargs)

    register_method_commands(
        "level",
        "levelCommands",
        {
            "rankcard": "show_rankcard_command",
            "set_background": "set_background_command",
            "leaderboard": "leaderboard_command",
        },
    )
    register_kwargs("level.levelCommands.set_background", default_image_kwargs)
