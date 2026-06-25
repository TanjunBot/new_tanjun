from __future__ import annotations

from tests.helpers.live_e2e.cases._helpers import case

_MODERATION_TARGET = {"user": "__secondary__"}

OVERRIDES = {
    "admin_channels_name admin_lock_name": case(
        "admin_channels_name admin_lock_name",
        teardown="admin.unlock_channel",
    ),
    "admin_channels_name admin_nuke_name": case(
        "admin_channels_name admin_nuke_name",
        option_overrides={"channel": "__disposable__"},
        response_kind="any",
    ),
    "admin_channels_name admin_slowmode_name": case(
        "admin_channels_name admin_slowmode_name",
        option_overrides={"seconds": 5, "channel": "__disposable__"},
        teardown="admin.reset_slowmode",
    ),
    "admin_channels_name admin_unlock_name": case(
        "admin_channels_name admin_unlock_name",
        setup="admin.lock_channel",
    ),
    "admin_moderation_name admin_ban_name": case(
        "admin_moderation_name admin_ban_name",
        option_overrides=_MODERATION_TARGET,
        teardown="moderation.unban",
    ),
    "admin_moderation_name admin_kick_name": case(
        "admin_moderation_name admin_kick_name",
        option_overrides=_MODERATION_TARGET,
    ),
    "admin_moderation_name admin_nickname_name": case(
        "admin_moderation_name admin_nickname_name",
        option_overrides={**_MODERATION_TARGET, "nickname": "e2e-nick"},
        teardown="moderation.reset_nickname",
    ),
    "admin_moderation_name admin_removetimeout_name": case(
        "admin_moderation_name admin_removetimeout_name",
        option_overrides=_MODERATION_TARGET,
        setup="moderation.timeout",
    ),
    "admin_moderation_name admin_timeout_name": case(
        "admin_moderation_name admin_timeout_name",
        option_overrides={**_MODERATION_TARGET, "duration": 60},
        teardown="moderation.remove_timeout",
    ),
    "admin_moderation_name admin_unban_name": case(
        "admin_moderation_name admin_unban_name",
        option_overrides=_MODERATION_TARGET,
        setup="moderation.ban",
    ),
    "admin_purgegroup_name admin_purge_name": case(
        "admin_purgegroup_name admin_purge_name",
        option_overrides={"amount": 5, "channel": "__disposable__"},
        setup="admin.seed_messages",
    ),
    "admin_rolemanage_name admin_createrole_name": case(
        "admin_rolemanage_name admin_createrole_name",
        option_overrides={"name": "e2e-temp-role"},
        teardown="admin.delete_temp_role",
    ),
    "admin_rolemanage_name admin_deleterole_name": case(
        "admin_rolemanage_name admin_deleterole_name",
        setup="admin.create_temp_role",
    ),
    "admin_role_name admin_addrole_name": case(
        "admin_role_name admin_addrole_name",
        setup="admin.create_temp_role",
        option_overrides={"user": "__secondary__"},
        teardown="admin.remove_temp_role",
    ),
    "admin_role_name admin_removerole_name": case(
        "admin_role_name admin_removerole_name",
        setup="admin.assign_temp_role",
        option_overrides={"user": "__secondary__"},
        teardown="admin.delete_temp_role",
    ),
    "admin_messaging_name admin_embed_name": case(
        "admin_messaging_name admin_embed_name",
        option_overrides={"title": "e2e", "description": "test"},
    ),
    "admin_messaging_name admin_say_name": case(
        "admin_messaging_name admin_say_name",
        option_overrides={"content": "e2e test"},
        response_kind="any",
    ),
    "admin_localegroup_name admin_setlocale_name": case(
        "admin_localegroup_name admin_setlocale_name",
        option_overrides={"locale": "en-US"},
    ),
    "admin_warn_name admin_warn_add_name": case(
        "admin_warn_name admin_warn_add_name",
        option_overrides={**_MODERATION_TARGET, "reason": "e2e"},
    ),
}
