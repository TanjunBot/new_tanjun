from __future__ import annotations

import contextlib
from typing import TYPE_CHECKING, Any, Awaitable, Callable

from tests.helpers.live_e2e.models import CommandLiveCase

if TYPE_CHECKING:
    from tests.helpers.live_discord.session import LiveGuildSession

SetupHook = Callable[["LiveGuildSession", dict[str, Any]], Awaitable[None]]
TeardownHook = Callable[["LiveGuildSession", dict[str, Any]], Awaitable[None]]

_setup_hooks: dict[str, SetupHook] = {}
_teardown_hooks: dict[str, TeardownHook] = {}


def register_setup(name: str, hook: SetupHook) -> None:
    _setup_hooks[name] = hook


def register_teardown(name: str, hook: TeardownHook) -> None:
    _teardown_hooks[name] = hook


async def run_setup(name: str | None, session: LiveGuildSession, state: dict[str, Any]) -> None:
    if not name:
        return
    hook = _setup_hooks.get(name)
    if hook is None:
        return
    await hook(session, state)


async def run_teardown(name: str | None, session: LiveGuildSession, state: dict[str, Any]) -> None:
    if not name:
        return
    hook = _teardown_hooks.get(name)
    if hook is None:
        return
    await hook(session, state)


def _secondary_id(session: LiveGuildSession) -> str:
    return session.config.secondary_user_id or session.guild.owner_user_id


def _disposable_channel(session: LiveGuildSession) -> str:
    return session.config.disposable_channel_id or session.guild.channel_id


async def _invoke_path(
    session: LiveGuildSession,
    tree_path: str,
    *,
    option_overrides: dict[str, Any] | None = None,
    wait: bool = True,
) -> dict[str, Any] | None:
    from tests.helpers.live_e2e.registry import resolve_case_placeholders

    case = CommandLiveCase(tree_path=tree_path, option_overrides=dict(option_overrides or {}))
    case = resolve_case_placeholders(
        case,
        owner_user_id=session.guild.owner_user_id,
        secondary_user_id=session.config.secondary_user_id,
        bot_user_id=session.config.bot_user_id,
        main_channel_id=session.guild.channel_id,
        disposable_channel_id=session.config.disposable_channel_id,
    )
    if wait:
        return await session._command_executor.run_command_case(case)
    await session._command_executor.invoke_command(case)
    return None


async def _unban_user(session: LiveGuildSession, user_id: str) -> None:
    guild_id = session.guild.guild_id
    with contextlib.suppress(Exception):
        await session._bot_client.request(
            "DELETE",
            f"/guilds/{guild_id}/bans/{user_id}",
            expected=(204, 404),
        )


async def _remove_timeout(session: LiveGuildSession, user_id: str) -> None:
    guild_id = session.guild.guild_id
    with contextlib.suppress(Exception):
        await session._bot_client.request(
            "PATCH",
            f"/guilds/{guild_id}/members/{user_id}",
            json={"communication_disabled_until": None},
            expected=(200, 204, 404),
        )


async def _reset_nickname(session: LiveGuildSession, user_id: str) -> None:
    guild_id = session.guild.guild_id
    with contextlib.suppress(Exception):
        await session._bot_client.request(
            "PATCH",
            f"/guilds/{guild_id}/members/{user_id}",
            json={"nick": None},
            expected=(200, 204, 404),
        )


async def moderation_ban_setup(session: LiveGuildSession, state: dict[str, Any]) -> None:
    target = _secondary_id(session)
    state["moderation_target"] = target
    await _invoke_path(
        session,
        "admin_moderation_name admin_ban_name",
        option_overrides={"user": target},
        wait=False,
    )


async def moderation_unban_teardown(session: LiveGuildSession, state: dict[str, Any]) -> None:
    target = state.get("moderation_target") or _secondary_id(session)
    await _unban_user(session, target)


async def moderation_timeout_setup(session: LiveGuildSession, state: dict[str, Any]) -> None:
    target = _secondary_id(session)
    state["moderation_target"] = target
    await _invoke_path(
        session,
        "admin_moderation_name admin_timeout_name",
        option_overrides={"user": target, "duration": 60},
        wait=False,
    )


async def moderation_remove_timeout_teardown(session: LiveGuildSession, state: dict[str, Any]) -> None:
    target = state.get("moderation_target") or _secondary_id(session)
    await _remove_timeout(session, target)


async def moderation_reset_nickname_teardown(session: LiveGuildSession, state: dict[str, Any]) -> None:
    target = state.get("moderation_target") or _secondary_id(session)
    await _reset_nickname(session, target)


async def admin_lock_channel_setup(session: LiveGuildSession, state: dict[str, Any]) -> None:
    await _invoke_path(session, "admin_channels_name admin_lock_name", wait=False)


async def admin_unlock_channel_teardown(session: LiveGuildSession, state: dict[str, Any]) -> None:
    del state
    await _invoke_path(session, "admin_channels_name admin_unlock_name", wait=False)


async def admin_reset_slowmode_teardown(session: LiveGuildSession, state: dict[str, Any]) -> None:
    del state
    channel = _disposable_channel(session)
    await _invoke_path(
        session,
        "admin_channels_name admin_slowmode_name",
        option_overrides={"seconds": 0, "channel": channel},
        wait=False,
    )


async def channel_welcome_set_setup(session: LiveGuildSession, state: dict[str, Any]) -> None:
    del state
    await _invoke_path(
        session,
        "channel_name channel_welcome_name channel_w_name",
        option_overrides={"channel": session.guild.channel_id},
        wait=False,
    )


async def channel_welcome_remove_teardown(session: LiveGuildSession, state: dict[str, Any]) -> None:
    del state
    await _invoke_path(session, "channel_name channel_welcome_name channel_w_remove_name", wait=False)


async def channel_farewell_set_setup(session: LiveGuildSession, state: dict[str, Any]) -> None:
    del state
    await _invoke_path(
        session,
        "channel_name channel_farewell_name channel_farewell_set_ch_name",
        option_overrides={"channel": session.guild.channel_id},
        wait=False,
    )


async def channel_farewell_remove_teardown(session: LiveGuildSession, state: dict[str, Any]) -> None:
    del state
    await _invoke_path(
        session,
        "channel_name channel_farewell_name channel_farewell_remove_ch_name",
        wait=False,
    )


async def channel_media_set_setup(session: LiveGuildSession, state: dict[str, Any]) -> None:
    del state
    await _invoke_path(
        session,
        "channel_name channel_media_name channel_media_name",
        option_overrides={"channel": session.guild.channel_id},
        wait=False,
    )


async def channel_media_remove_teardown(session: LiveGuildSession, state: dict[str, Any]) -> None:
    del state
    await _invoke_path(session, "channel_name channel_media_name channel_mediaremove_name", wait=False)


async def channel_ds_add_setup(session: LiveGuildSession, state: dict[str, Any]) -> None:
    del state
    await _invoke_path(
        session,
        "channel_name channel_ds_name channel_ds_add_name",
        option_overrides={"channel": session.guild.channel_id, "seconds": 30},
        wait=False,
    )


async def channel_ds_remove_teardown(session: LiveGuildSession, state: dict[str, Any]) -> None:
    del state
    await _invoke_path(session, "channel_name channel_ds_name channel_ds_remove_name", wait=False)


async def level_enable_setup(session: LiveGuildSession, state: dict[str, Any]) -> None:
    del state
    await _invoke_path(session, "level_config_name level_enable_name", wait=False)


async def level_disable_teardown(session: LiveGuildSession, state: dict[str, Any]) -> None:
    del state
    await _invoke_path(session, "level_config_name level_disable_name", wait=False)


async def logs_configure_setup(session: LiveGuildSession, state: dict[str, Any]) -> None:
    del state
    await _invoke_path(session, "logs_name logs_configure_name", wait=False)


async def logs_remove_teardown(session: LiveGuildSession, state: dict[str, Any]) -> None:
    del state
    await _invoke_path(session, "logs_name logs_remove_name", wait=False)


async def minigames_set_counting_setup(session: LiveGuildSession, state: dict[str, Any]) -> None:
    del state
    await _invoke_path(
        session,
        "minigame_name minigames_countingcmds_name minigames_setcountingch_name",
        option_overrides={"channel": session.guild.channel_id},
        wait=False,
    )


async def minigames_remove_counting_teardown(session: LiveGuildSession, state: dict[str, Any]) -> None:
    del state
    await _invoke_path(
        session,
        "minigame_name minigames_countingcmds_name minigames_removecountingch_name",
        wait=False,
    )


async def minigames_set_wordchain_setup(session: LiveGuildSession, state: dict[str, Any]) -> None:
    del state
    await _invoke_path(
        session,
        "minigame_name minigames_wordchaincmds_name minigames_setwordcainch_name",
        option_overrides={"channel": session.guild.channel_id},
        wait=False,
    )


async def minigames_remove_wordchain_teardown(session: LiveGuildSession, state: dict[str, Any]) -> None:
    del state
    await _invoke_path(
        session,
        "minigame_name minigames_wordchaincmds_name minigames_removewordchch_name",
        wait=False,
    )


async def admin_create_temp_role_setup(session: LiveGuildSession, state: dict[str, Any]) -> None:
    guild_id = session.guild.guild_id
    response = await session._bot_client.request(
        "POST",
        f"/guilds/{guild_id}/roles",
        json={"name": "e2e-temp-role", "permissions": "0"},
        expected=(200,),
    )
    state["temp_role_id"] = str(response.get("id", ""))


async def admin_delete_temp_role_teardown(session: LiveGuildSession, state: dict[str, Any]) -> None:
    role_id = state.get("temp_role_id")
    if not role_id:
        return
    guild_id = session.guild.guild_id
    with contextlib.suppress(Exception):
        await session._bot_client.request(
            "DELETE",
            f"/guilds/{guild_id}/roles/{role_id}",
            expected=(204, 404),
        )


async def giveaway_start_setup(session: LiveGuildSession, state: dict[str, Any]) -> None:
    result = await _invoke_path(
        session,
        "giveaway_name giveaway_start_name",
        option_overrides={"duration": 120, "winners": 1, "prize": "e2e prize"},
    )
    state["giveaway_message_id"] = (result or {}).get("message_id")


async def giveaway_end_teardown(session: LiveGuildSession, state: dict[str, Any]) -> None:
    message_id = state.get("giveaway_message_id")
    if message_id:
        await _invoke_path(
            session,
            "giveaway_name giveaway_end_name",
            option_overrides={"message_id": message_id},
            wait=False,
        )


async def level_enable_with_xp_setup(session: LiveGuildSession, state: dict[str, Any]) -> None:
    await _invoke_path(session, "level_config_name level_enable_name", wait=False)
    state["level_enabled"] = True


async def utility_clear_afk_teardown(session: LiveGuildSession, state: dict[str, Any]) -> None:
    del state
    await _invoke_path(session, "utilitycmd_name utility_afk_name", option_overrides={"status": ""}, wait=False)


async def admin_seed_messages_setup(session: LiveGuildSession, state: dict[str, Any]) -> None:
    channel_id = _disposable_channel(session)
    state["seed_channel_id"] = channel_id
    for i in range(3):
        with contextlib.suppress(Exception):
            await session._bot_client.request(
                "POST",
                f"/channels/{channel_id}/messages",
                json={"content": f"e2e seed {i}"},
                expected=(200,),
            )


async def admin_assign_temp_role_setup(session: LiveGuildSession, state: dict[str, Any]) -> None:
    if not state.get("temp_role_id"):
        await admin_create_temp_role_setup(session, state)
    role_id = state.get("temp_role_id")
    user_id = _secondary_id(session)
    guild_id = session.guild.guild_id
    state["assigned_role_user"] = user_id
    if role_id:
        with contextlib.suppress(Exception):
            await session._bot_client.request(
                "PUT",
                f"/guilds/{guild_id}/members/{user_id}/roles/{role_id}",
                expected=(204,),
            )


async def admin_remove_temp_role_teardown(session: LiveGuildSession, state: dict[str, Any]) -> None:
    role_id = state.get("temp_role_id")
    user_id = state.get("assigned_role_user") or _secondary_id(session)
    guild_id = session.guild.guild_id
    if role_id:
        with contextlib.suppress(Exception):
            await session._bot_client.request(
                "DELETE",
                f"/guilds/{guild_id}/members/{user_id}/roles/{role_id}",
                expected=(204, 404),
            )


async def giveaway_ended_setup(session: LiveGuildSession, state: dict[str, Any]) -> None:
    await giveaway_start_setup(session, state)
    message_id = state.get("giveaway_message_id")
    if message_id:
        await _invoke_path(
            session,
            "giveaway_name giveaway_end_name",
            option_overrides={"message_id": message_id},
            wait=False,
        )
        state["giveaway_ended"] = True


async def giveaway_bl_add_user_setup(session: LiveGuildSession, state: dict[str, Any]) -> None:
    user_id = _secondary_id(session)
    state["giveaway_bl_user"] = user_id
    await _invoke_path(
        session,
        "giveaway_name giveaway_blacklist_name giveaway_bl_add_user_name",
        option_overrides={"user": user_id},
        wait=False,
    )


async def giveaway_bl_remove_user_teardown(session: LiveGuildSession, state: dict[str, Any]) -> None:
    user_id = state.get("giveaway_bl_user") or _secondary_id(session)
    await _invoke_path(
        session,
        "giveaway_name giveaway_blacklist_name giveaway_bl_remove_user_name",
        option_overrides={"user": user_id},
        wait=False,
    )


async def level_blacklist_add_user_setup(session: LiveGuildSession, state: dict[str, Any]) -> None:
    await level_enable_setup(session, state)
    user_id = _secondary_id(session)
    state["level_bl_user"] = user_id
    await _invoke_path(
        session,
        "level_blacklist_name level_blacklist_addu_name",
        option_overrides={"user": user_id},
        wait=False,
    )


async def level_blacklist_remove_user_teardown(session: LiveGuildSession, state: dict[str, Any]) -> None:
    user_id = state.get("level_bl_user") or _secondary_id(session)
    await _invoke_path(
        session,
        "level_blacklist_name level_blacklist_removeu_name",
        option_overrides={"user": user_id},
        wait=False,
    )


async def level_clear_levelup_channel_teardown(session: LiveGuildSession, state: dict[str, Any]) -> None:
    del state
    await _invoke_path(session, "level_config_name level_setlevelupchannel_name", option_overrides={"channel": None}, wait=False)


async def level_boost_remove_user_teardown(session: LiveGuildSession, state: dict[str, Any]) -> None:
    user_id = state.get("boost_user") or session.guild.owner_user_id
    await _invoke_path(
        session,
        "level_boosts_name level_boosts_removeuser_name",
        option_overrides={"user": user_id},
        wait=False,
    )


async def utility_twitch_add_setup(session: LiveGuildSession, state: dict[str, Any]) -> None:
    state["twitch_name"] = "shroud"
    await _invoke_path(
        session,
        "utilitycmd_name utility_twitch_name utility_twitch_add_name",
        option_overrides={"twitchname": "shroud", "notificationmessage": "live"},
        wait=False,
    )


async def utility_twitch_remove_teardown(session: LiveGuildSession, state: dict[str, Any]) -> None:
    twitch = state.get("twitch_name", "shroud")
    await _invoke_path(
        session,
        "utilitycmd_name utility_twitch_name utility_twitch_remove_name",
        option_overrides={"twitchname": twitch},
        wait=False,
    )


async def utility_schedule_message_setup(session: LiveGuildSession, state: dict[str, Any]) -> None:
    await _invoke_path(
        session,
        "utility_scheduledmessage_name utility_schedulemessage_name",
        option_overrides={"content": "e2e scheduled", "sendin": "1h"},
        wait=False,
    )


async def utility_remove_scheduled_teardown(session: LiveGuildSession, state: dict[str, Any]) -> None:
    await _invoke_path(session, "utility_scheduledmessage_name utility_removescheduled_name", wait=False)


async def logs_blacklistc_add_setup(session: LiveGuildSession, state: dict[str, Any]) -> None:
    await logs_configure_setup(session, state)
    channel = session.guild.channel_id
    state["logs_bl_channel"] = channel
    await _invoke_path(
        session,
        "logs_name logs_blacklist_name logs_blacklistc_add_name",
        option_overrides={"channel": channel},
        wait=False,
    )


async def logs_blacklistc_remove_teardown(session: LiveGuildSession, state: dict[str, Any]) -> None:
    channel = state.get("logs_bl_channel") or session.guild.channel_id
    await _invoke_path(
        session,
        "logs_name logs_blacklist_name logs_blacklistc_remove_name",
        option_overrides={"channel": channel},
        wait=False,
    )


async def ai_create_custom_setup(session: LiveGuildSession, state: dict[str, Any]) -> None:
    state["ai_custom_name"] = "e2ecustom"
    await _invoke_path(
        session,
        "ai_name ai_customsituations_name ai_createcustom_name",
        option_overrides={"name": "e2ecustom", "situation": "e2e custom personality"},
        wait=False,
    )


async def ai_delete_custom_teardown(session: LiveGuildSession, state: dict[str, Any]) -> None:
    name = state.get("ai_custom_name", "e2ecustom")
    await _invoke_path(
        session,
        "ai_name ai_customsituations_name ai_deletecustom_name",
        option_overrides={"name": name},
        wait=False,
    )


def _register_defaults() -> None:
    register_setup("moderation.ban", moderation_ban_setup)
    register_teardown("moderation.unban", moderation_unban_teardown)
    register_setup("moderation.timeout", moderation_timeout_setup)
    register_teardown("moderation.remove_timeout", moderation_remove_timeout_teardown)
    register_teardown("moderation.reset_nickname", moderation_reset_nickname_teardown)
    register_setup("admin.lock_channel", admin_lock_channel_setup)
    register_teardown("admin.unlock_channel", admin_unlock_channel_teardown)
    register_teardown("admin.reset_slowmode", admin_reset_slowmode_teardown)
    register_setup("channel.welcome_set", channel_welcome_set_setup)
    register_teardown("channel.welcome_remove", channel_welcome_remove_teardown)
    register_setup("channel.farewell_set", channel_farewell_set_setup)
    register_teardown("channel.farewell_remove", channel_farewell_remove_teardown)
    register_setup("channel.media_set", channel_media_set_setup)
    register_teardown("channel.media_remove", channel_media_remove_teardown)
    register_setup("channel.ds_add", channel_ds_add_setup)
    register_teardown("channel.ds_remove", channel_ds_remove_teardown)
    register_setup("level.enable", level_enable_setup)
    register_teardown("level.disable", level_disable_teardown)
    register_setup("logs.configure", logs_configure_setup)
    register_teardown("logs.remove", logs_remove_teardown)
    register_setup("minigames.set_counting", minigames_set_counting_setup)
    register_teardown("minigames.remove_counting", minigames_remove_counting_teardown)
    register_setup("minigames.set_wordchain", minigames_set_wordchain_setup)
    register_teardown("minigames.remove_wordchain", minigames_remove_wordchain_teardown)
    register_setup("admin.create_temp_role", admin_create_temp_role_setup)
    register_teardown("admin.delete_temp_role", admin_delete_temp_role_teardown)
    register_setup("giveaway.start", giveaway_start_setup)
    register_teardown("giveaway.end", giveaway_end_teardown)
    register_setup("level.enable_with_xp", level_enable_with_xp_setup)
    register_teardown("utility.clear_afk", utility_clear_afk_teardown)
    register_setup("admin.seed_messages", admin_seed_messages_setup)
    register_setup("admin.assign_temp_role", admin_assign_temp_role_setup)
    register_teardown("admin.remove_temp_role", admin_remove_temp_role_teardown)
    register_setup("giveaway.ended", giveaway_ended_setup)
    register_setup("giveaway.bl_add_user", giveaway_bl_add_user_setup)
    register_teardown("giveaway.bl_remove_user", giveaway_bl_remove_user_teardown)
    register_setup("level.blacklist_add_user", level_blacklist_add_user_setup)
    register_teardown("level.blacklist_remove_user", level_blacklist_remove_user_teardown)
    register_teardown("level.clear_levelup_channel", level_clear_levelup_channel_teardown)
    register_teardown("level.boost_remove_user", level_boost_remove_user_teardown)
    register_setup("utility.twitch_add", utility_twitch_add_setup)
    register_teardown("utility.twitch_remove", utility_twitch_remove_teardown)
    register_setup("utility.schedule_message", utility_schedule_message_setup)
    register_teardown("utility.remove_scheduled", utility_remove_scheduled_teardown)
    register_setup("logs.blacklistc_add", logs_blacklistc_add_setup)
    register_teardown("logs.blacklistc_remove", logs_blacklistc_remove_teardown)
    register_setup("ai.create_custom", ai_create_custom_setup)
    register_teardown("ai.delete_custom", ai_delete_custom_teardown)


_register_defaults()
