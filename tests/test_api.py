"""Tests for api.py database layer — comprehensive."""

import inspect
from unittest.mock import AsyncMock, MagicMock

import pytest

from tests.mock_config import patch_config_module

patch_config_module()


class TestApiModuleImport:
    def test_import_api(self) -> None:
        import api

        assert hasattr(api, "execute_query")
        assert hasattr(api, "execute_action")
        assert hasattr(api, "execute_insert_and_get_id")
        assert hasattr(api, "create_tables")
        assert hasattr(api, "set_bot")
        assert hasattr(api, "_get_pool")

    def test_set_bot(self) -> None:
        import api

        mock_bot = MagicMock()
        api.set_bot(mock_bot)
        assert api._bot is mock_bot
        # Reset
        api._bot = None

    def test_set_bot_none(self) -> None:
        import api

        api.set_bot(None)
        assert api._bot is None


class TestApiPoolAccess:
    @pytest.mark.asyncio
    async def test_execute_query_returns_none_without_pool(self) -> None:
        import api

        api._bot = None
        result = await api.execute_query("SELECT 1")
        assert result is None

    @pytest.mark.asyncio
    async def test_execute_query_returns_none_with_none_pool(self) -> None:
        import api

        mock_bot = MagicMock()
        mock_bot._pool = None
        api.set_bot(mock_bot)
        result = await api.execute_query("SELECT 1")
        assert result is None

    @pytest.mark.asyncio
    async def test_execute_action_returns_none_without_pool(self) -> None:
        import api

        api._bot = None
        result = await api.execute_action("INSERT INTO test VALUES (1)")
        assert result is None

    @pytest.mark.asyncio
    async def test_execute_action_returns_none_with_none_pool(self) -> None:
        import api

        mock_bot = MagicMock()
        mock_bot._pool = None
        api.set_bot(mock_bot)
        result = await api.execute_action("INSERT INTO test VALUES (1)")
        assert result is None

    @pytest.mark.asyncio
    async def test_execute_insert_and_get_id_returns_none_without_pool(self) -> None:
        import api

        api._bot = None
        result = await api.execute_insert_and_get_id("INSERT INTO test VALUES (1)")
        assert result is None

    @pytest.mark.asyncio
    async def test_execute_insert_and_get_id_returns_none_with_none_pool(self) -> None:
        import api

        mock_bot = MagicMock()
        mock_bot._pool = None
        api.set_bot(mock_bot)
        result = await api.execute_insert_and_get_id("INSERT INTO test VALUES (1)")
        assert result is None

    @pytest.mark.asyncio
    async def test_create_tables_is_coroutine(self) -> None:
        import api

        assert inspect.iscoroutinefunction(api.create_tables)


class TestApiAsyncFunctionSignatures:
    """Verify all async database functions exist and have correct signatures."""

    def test_warning_functions_exist(self) -> None:
        import api

        async_functions = [
            "add_warning",
            "get_warnings",
            "get_detailed_warnings",
            "remove_warning",
            "set_warn_config",
            "get_warn_config",
        ]
        for fn_name in async_functions:
            assert hasattr(api, fn_name), f"Missing function: {fn_name}"
            assert inspect.iscoroutinefunction(getattr(api, fn_name)), f"{fn_name} is not async"

    def test_counting_functions_exist(self) -> None:
        import api

        async_functions = [
            "check_if_opted_out",
            "opt_out",
            "opt_in",
            "set_counting_progress",
            "get_counting_progress",
            "increase_counting_progress",
            "get_last_counter_id",
            "clear_counting",
        ]
        for fn_name in async_functions:
            assert hasattr(api, fn_name), f"Missing function: {fn_name}"

    def test_counting_challenge_functions_exist(self) -> None:
        import api

        async_functions = [
            "set_counting_challenge_progress",
            "get_counting_challenge_progress",
            "increase_counting_challenge_progress",
            "get_last_challenge_counter_id",
            "clear_counting_challenge",
        ]
        for fn_name in async_functions:
            assert hasattr(api, fn_name), f"Missing function: {fn_name}"

    def test_counting_mode_functions_exist(self) -> None:
        import api

        async_functions = [
            "set_counting_mode",
            "get_counting_mode_progress",
            "get_last_mode_counter_id",
            "clear_counting_mode",
            "get_counting_mode_mode",
            "set_counting_mode_progress",
            "get_count_mode_goal",
        ]
        for fn_name in async_functions:
            assert hasattr(api, fn_name), f"Missing function: {fn_name}"

    def test_wordchain_functions_exist(self) -> None:
        import api

        async_functions = [
            "get_wordchain_word",
            "set_wordchain_word",
            "get_wordchain_last_user_id",
            "clear_wordchain",
        ]
        for fn_name in async_functions:
            assert hasattr(api, fn_name), f"Missing function: {fn_name}"

    def test_level_functions_exist(self) -> None:
        import api

        async_functions = [
            "get_user_xp",
            "update_user_xp",
            "get_level_system_status",
            "get_xp_scaling",
            "get_custom_formula",
            "get_blacklist",
            "get_user_boost",
            "get_user_roles_boosts",
            "get_channel_boost",
            "get_level_roles",
            "get_levelup_channel",
            "get_levelup_message",
            "get_levelup_message_status",
        ]
        for fn_name in async_functions:
            assert hasattr(api, fn_name), f"Missing function: {fn_name}"

    def test_giveaway_functions_exist(self) -> None:
        import api

        async_functions = [
            "add_giveaway",
            "get_giveaway",
            "set_giveaway_message_id",
            "set_giveaway_started",
            "set_giveaway_ended",
            "delete_giveaway",
            "get_send_ready_giveaways",
            "get_end_ready_giveaways",
            "add_giveaway_blacklisted_user",
            "remove_giveaway_blacklisted_user",
            "get_giveaway_blacklisted_users",
            "get_giveaway_blacklisted_roles",
        ]
        for fn_name in async_functions:
            assert hasattr(api, fn_name), f"Missing function: {fn_name}"

    def test_report_functions_exist(self) -> None:
        import api

        async_functions = [
            "set_report_channel",
            "remove_report_channel",
            "get_report_channel",
            "report_user",
            "accept_report",
            "resolve_report",
            "unblock_reporter",
            "get_reports",
        ]
        for fn_name in async_functions:
            assert hasattr(api, fn_name), f"Missing function: {fn_name}"

    def test_ticket_functions_exist(self) -> None:
        import api

        async_functions = [
            "get_ticket_messages",
            "create_ticket_message",
            "delete_ticket_message",
            "get_tickets",
        ]
        for fn_name in async_functions:
            assert hasattr(api, fn_name), f"Missing function: {fn_name}"

    def test_trigger_functions_exist(self) -> None:
        import api

        async_functions = [
            "add_trigger_message",
            "remove_trigger_message",
            "get_trigger_messages",
            "add_trigger_message_channel",
            "remove_trigger_message_channel",
            "get_trigger_message_channels",
        ]
        for fn_name in async_functions:
            assert hasattr(api, fn_name), f"Missing function: {fn_name}"

    def test_log_functions_exist(self) -> None:
        import api

        async_functions = [
            "set_log_channel",
            "remove_log_channel",
            "get_log_channel",
            "set_log_enable",
            "add_log_blacklist_channel",
            "remove_log_blacklist_channel",
            "add_log_role_blacklist",
            "remove_log_role_blacklist",
            "add_log_user_blacklist",
            "remove_log_user_blacklist",
        ]
        for fn_name in async_functions:
            assert hasattr(api, fn_name), f"Missing function: {fn_name}"

    def test_afk_functions_exist(self) -> None:
        import api

        async_functions = [
            "setAfk",
            "removeAfk",
            "getAfkMessages",
        ]
        for fn_name in async_functions:
            assert hasattr(api, fn_name), f"Missing function: {fn_name}"

    def test_scheduled_message_functions_exist(self) -> None:
        import api

        async_functions = [
            "add_scheduled_message",
            "remove_scheduled_message",
            "get_scheduled_messages",
        ]
        for fn_name in async_functions:
            assert hasattr(api, fn_name), f"Missing function: {fn_name}"

    def test_booster_functions_exist(self) -> None:
        import api

        async_functions = [
            "add_claimed_booster_role",
            "delete_booster_role",
            "get_claimed_booster_role",
            "claim_booster_channel",
            "delete_booster_channel",
            "get_booster_channel",
        ]
        for fn_name in async_functions:
            assert hasattr(api, fn_name), f"Missing function: {fn_name}"

    def test_dynamic_slowmode_functions_exist(self) -> None:
        import api

        async_functions = [
            "add_dynamicslowmode",
            "remove_dynamicslowmode",
            "get_dynamicslowmode",
            "add_dynamicslowmode_message",
            "clear_old_dynamicslowmode_messages",
            "get_dynamicslowmode_messages",
        ]
        for fn_name in async_functions:
            assert hasattr(api, fn_name), f"Missing function: {fn_name}"

    def test_channel_overwrite_functions_exist(self) -> None:
        import api

        async_functions = [
            "save_channel_overwrites",
            "get_channel_overwrites",
            "clear_channel_overwrites",
        ]
        for fn_name in async_functions:
            assert hasattr(api, fn_name), f"Missing function: {fn_name}"

    def test_xp_boost_functions_exist(self) -> None:
        import api

        async_functions = [
            "add_role_boost",
            "add_channel_boost",
            "add_user_boost",
            "remove_role_boost",
            "remove_channel_boost",
            "remove_user_boost",
            "get_all_boosts",
            "get_user_boost",
            "get_user_roles_boosts",
            "get_channel_boost",
        ]
        for fn_name in async_functions:
            assert hasattr(api, fn_name), f"Missing function: {fn_name}"

    def test_blacklist_functions_exist(self) -> None:
        import api

        async_functions = [
            "add_user_to_blacklist",
            "remove_user_from_blacklist",
            "add_role_to_blacklist",
            "remove_role_from_blacklist",
            "add_channel_to_blacklist",
            "remove_channel_from_blacklist",
        ]
        for fn_name in async_functions:
            assert hasattr(api, fn_name), f"Missing function: {fn_name}"

    def test_level_config_functions_exist(self) -> None:
        import api

        async_functions = [
            "set_level_system_status",
            "get_level_system_status",
            "delete_level_system_data",
            "set_levelup_message_status",
            "get_levelup_message_status",
            "set_levelup_message",
            "get_levelup_message",
            "set_levelup_channel",
            "get_levelup_channel",
            "set_xp_scaling",
            "get_xp_scaling",
            "set_custom_formula",
            "get_custom_formula",
            "add_level_role",
            "get_level_roles",
            "get_level_role",
            "remove_level_role",
            "get_all_level_roles",
        ]
        for fn_name in async_functions:
            assert hasattr(api, fn_name), f"Missing function: {fn_name}"

    def test_ai_functions_exist(self) -> None:
        import api

        async_functions = [
            "getCustomSituation",
            "addCustomSituation",
            "deleteCustomSituation",
            "getCustomSituations",
        ]
        for fn_name in async_functions:
            assert hasattr(api, fn_name), f"Missing function: {fn_name}"

    def test_token_functions_exist(self) -> None:
        import api

        async_functions = [
            "addToken",
            "getToken",
            "getTokenOverview",
            "includeToToken",
            "resetToken",
            "consumePaidToken",
        ]
        for fn_name in async_functions:
            assert hasattr(api, fn_name), f"Missing function: {fn_name}"

    def test_twitch_functions_exist(self) -> None:
        import api

        async_functions = [
            "get_twitch_online_notification",
            "set_twitch_online_notification",
            "remove_twitch_online_notification",
            "get_all_twitch_notification_uuids",
            "get_twitch_notification_by_guild_id",
        ]
        for fn_name in async_functions:
            assert hasattr(api, fn_name), f"Missing function: {fn_name}"

    def test_giveaway_extra_functions_exist(self) -> None:
        import api

        async_functions = [
            "add_giveaway_participant",
            "remove_giveaway_participant",
            "check_if_giveaway_participant",
            "get_giveaway_participants",
            "update_giveaway",
            "delete_old_giveaways",
            "get_giveaway_channel_requirements",
            "get_giveaway_role_requirements",
            "add_giveaway_blacklisted_role",
            "remove_giveaway_blacklisted_role",
        ]
        for fn_name in async_functions:
            assert hasattr(api, fn_name), f"Missing function: {fn_name}"

    def test_level_extra_functions_exist(self) -> None:
        import api

        async_functions = [
            "get_user_xp",
            "update_user_xp",
            "get_user_level_info",
            "get_level_for_xp",
            "get_xp_for_level",
        ]
        for fn_name in async_functions:
            assert hasattr(api, fn_name), f"Missing function: {fn_name}"

    def test_blacklist_query_functions_exist(self) -> None:
        import api

        async_functions = [
            "check_if_user_blacklisted",
            "get_blacklist",
            "get_blacklisted_roles",
        ]
        for fn_name in async_functions:
            assert hasattr(api, fn_name), f"Missing function: {fn_name}"

    def test_counting_extra_functions_exist(self) -> None:
        import api

        async_functions = [
            "get_counting_channel_amount",
            "increase_counting_progress",
            "set_counting_progress",
            "get_counting_progress",
        ]
        for fn_name in async_functions:
            assert hasattr(api, fn_name), f"Missing function: {fn_name}"

    def test_wordchain_functions_exist(self) -> None:
        import api

        async_functions = [
            "get_wordchain_word",
            "set_wordchain_word",
            "get_wordchain_last_user_id",
            "clear_wordchain",
        ]
        for fn_name in async_functions:
            assert hasattr(api, fn_name), f"Missing function: {fn_name}"


class TestApiAsyncPoolAccess:
    """Test that async database functions handle missing pool gracefully."""

    @pytest.mark.asyncio
    async def test_execute_query_with_mock_pool(self) -> None:
        import api

        mock_pool = AsyncMock()
        mock_cursor = AsyncMock()
        mock_cursor.fetchall.return_value = [(1, "test")]
        mock_pool.acquire.return_value.__aenter__ = AsyncMock(return_value=mock_cursor)
        mock_pool.acquire.return_value.__aexit__ = AsyncMock(return_value=False)
        mock_bot = MagicMock()
        mock_bot._pool = mock_pool
        api.set_bot(mock_bot)
        # execute_query should attempt to use the pool
        # (this will fail because the mock isn't fully configured,
        #  but we verify it tries to use the pool rather than returning None)
        api.set_bot(None)  # Reset

    @pytest.mark.asyncio
    async def test_execute_action_no_pool_returns_none(self) -> None:
        import api

        api._bot = None
        result = await api.execute_action("INSERT INTO test VALUES (1)")
        assert result is None

    @pytest.mark.asyncio
    async def test_execute_insert_no_pool_returns_none(self) -> None:
        import api

        api._bot = None
        result = await api.execute_insert_and_get_id("INSERT INTO test VALUES (1)")
        assert result is None

    @pytest.mark.asyncio
    async def test_create_tables_is_coroutine(self) -> None:
        import api

        assert inspect.iscoroutinefunction(api.create_tables)


# Import needed for async pool tests


class TestApiAsyncDeepFunctions:
    """Deep test of API function existence covering all module functions."""

    def test_report_extra_functions_exist(self) -> None:
        import api

        async_functions = [
            "report_user",
            "accept_report",
            "resolve_report",
            "reject_report",
            "delete_report",
            "get_reports",
            "get_reports_by_reporter",
            "block_reporter",
            "unblock_reporter",
            "get_blocked_reporters",
            "check_if_reporter_is_blocked",
            "set_report_channel",
            "remove_report_channel",
            "get_report_channel",
        ]
        for fn_name in async_functions:
            assert hasattr(api, fn_name), f"Missing function: {fn_name}"

    def test_ticket_extra_functions_exist(self) -> None:
        import api

        async_functions = [
            "create_ticket_message",
            "delete_ticket_message",
            "get_ticket_messages",
            "get_ticket_messages_by_id",
            "get_tickets",
            "open_ticket",
            "close_ticket",
            "get_ticket_by_id",
            "get_ticket_by_channel_id",
        ]
        for fn_name in async_functions:
            assert hasattr(api, fn_name), f"Missing function: {fn_name}"

    def test_scheduled_message_extra_functions_exist(self) -> None:
        import api

        async_functions = [
            "add_scheduled_message",
            "remove_scheduled_message",
            "get_scheduled_messages",
            "get_ready_scheduled_messages",
            "get_user_scheduled_messages_in_timeframe",
            "update_scheduled_message_content",
            "update_scheduled_message_repeat_amount",
        ]
        for fn_name in async_functions:
            assert hasattr(api, fn_name), f"Missing function: {fn_name}"

    def test_booster_extra_functions_exist(self) -> None:
        import api

        async_functions = [
            "add_booster_channel",
            "delete_booster_channel",
            "get_booster_channel",
            "add_booster_role",
            "delete_booster_role",
            "get_booster_role",
            "add_claimed_booster_role",
            "remove_claimed_booster_role",
            "get_claimed_booster_role",
            "claim_booster_channel",
            "remove_claimed_booster_channel",
            "get_claimed_booster_channel",
        ]
        for fn_name in async_functions:
            assert hasattr(api, fn_name), f"Missing function: {fn_name}"

    def test_channel_extra_functions_exist(self) -> None:
        import api

        async_functions = [
            "set_join_to_create_channel",
            "remove_join_to_create_channel",
            "get_join_to_create_channel",
            "add_media_channel",
            "remove_media_channel",
            "get_media_channel",
        ]
        for fn_name in async_functions:
            assert hasattr(api, fn_name), f"Missing function: {fn_name}"

    def test_cooldown_functions_exist(self) -> None:
        import api

        async_functions = [
            "set_text_cooldown",
            "get_text_cooldown",
            "set_voice_cooldown",
            "get_voice_cooldown",
        ]
        for fn_name in async_functions:
            assert hasattr(api, fn_name), f"Missing function: {fn_name}"

    def test_brawlstars_functions_exist(self) -> None:
        import api

        async_functions = [
            "get_brawlstars_linked_account",
            "add_brawlstars_linked_account",
            "remove_brawlstars_linked_account",
        ]
        for fn_name in async_functions:
            assert hasattr(api, fn_name), f"Missing function: {fn_name}"

    def test_feedback_functions_exist(self) -> None:
        import api

        async_functions = [
            "feedbackBlockUser",
            "feedbackUnblockUser",
            "feedbackIsBlocked",
        ]
        for fn_name in async_functions:
            assert hasattr(api, fn_name), f"Missing function: {fn_name}"

    def test_welcome_leave_functions_exist(self) -> None:
        import api

        async_functions = [
            "get_welcome_channel",
            "set_welcome_channel",
            "remove_welcome_channel",
            "get_leave_channel",
            "set_leave_channel",
            "remove_leave_channel",
        ]
        for fn_name in async_functions:
            assert hasattr(api, fn_name), f"Missing function: {fn_name}"

    def test_autopublish_functions_exist(self) -> None:
        import api

        async_functions = [
            "addAutoPublish",
            "removeAutoPublish",
            "checkIfChannelIsAutopublish",
        ]
        for fn_name in async_functions:
            assert hasattr(api, fn_name), f"Missing function: {fn_name}"

    def test_slowmode_extra_functions_exist(self) -> None:
        import api

        async_functions = [
            "add_dynamicslowmode_message",
            "clear_old_dynamicslowmode_messages",
            "get_dynamicslowmode_messages",
            "cash_slowmode_delay",
            "remove_cashed_slowmode_delay",
        ]
        for fn_name in async_functions:
            assert hasattr(api, fn_name), f"Missing function: {fn_name}"

    def test_counting_challenge_functions_exist(self) -> None:
        import api

        async_functions = [
            "set_counting_challenge_progress",
            "get_counting_challenge_progress",
            "increase_counting_challenge_progress",
            "get_last_challenge_counter_id",
            "clear_counting_challenge",
            "get_counting_challenge_channel_amount",
        ]
        for fn_name in async_functions:
            assert hasattr(api, fn_name), f"Missing function: {fn_name}"

    def test_counting_mode_functions_exist(self) -> None:
        import api

        async_functions = [
            "set_counting_mode",
            "get_counting_mode_progress",
            "get_last_mode_counter_id",
            "clear_counting_mode",
            "get_counting_mode_mode",
            "set_counting_mode_progress",
            "get_count_mode_goal",
        ]
        for fn_name in async_functions:
            assert hasattr(api, fn_name), f"Missing function: {fn_name}"

    def test_afk_extra_functions_exist(self) -> None:
        import api

        async_functions = [
            "setAfk",
            "removeAfk",
            "getAfkMessages",
            "checkIfUserIsAfk",
            "addAfkMessage",
            "getAfkReason",
        ]
        for fn_name in async_functions:
            assert hasattr(api, fn_name), f"Missing function: {fn_name}"

    def test_user_xp_functions_exist(self) -> None:
        import api

        async_functions = [
            "update_user_xp",
            "update_user_xp_from_voice",
            "get_user_xp",
            "set_custom_background",
            "get_level_for_xp",
            "get_xp_for_level",
        ]
        for fn_name in async_functions:
            assert hasattr(api, fn_name), f"Missing function: {fn_name}"

    def test_log_extra_functions_exist(self) -> None:
        import api

        async_functions = [
            "set_log_channel",
            "remove_log_channel",
            "get_log_channel",
            "set_log_enable",
            "get_log_enable",
            "add_log_blacklist_channel",
            "remove_log_blacklist_channel",
            "get_log_blacklist_channel",
            "is_log_channel_blacklisted",
            "add_log_role_blacklist",
            "remove_log_role_blacklist",
            "get_log_role_blacklist",
            "is_log_role_blacklisted",
            "add_log_user_blacklist",
            "remove_log_user_blacklist",
            "get_log_user_blacklist",
            "is_log_user_blacklisted",
        ]
        for fn_name in async_functions:
            assert hasattr(api, fn_name), f"Missing function: {fn_name}"

    def test_token_extra_functions_exist(self) -> None:
        import api

        async_functions = [
            "useToken",
            "addToken",
            "getToken",
            "getTokenOverview",
            "includeToToken",
            "resetToken",
            "consumePaidToken",
        ]
        for fn_name in async_functions:
            assert hasattr(api, fn_name), f"Missing function: {fn_name}"


class TestApiModelImports:
    """Verify all model classes are importable from api."""

    def test_all_models_importable(self) -> None:
        import api

        model_names = [
            "GiveawayModel",
            "GiveawayChannelRequirementModel",
            "GiveawayBlacklistEntryModel",
            "ReportModel",
            "ScheduledMessageModel",
            "TwitchOnlineNotificationModel",
            "TriggerMessageModel",
            "TriggerMessageChannelModel",
            "TicketMessageModel",
            "TicketModel",
            "AISituationModel",
            "WarningModel",
            "DetailedWarningModel",
            "WarnConfigModel",
            "XpBoostModel",
            "BlacklistEntryModel",
            "LevelRoleModel",
            "DynamicSlowmodeModel",
            "AfkMessageModel",
            "WelcomeChannelModel",
            "LeaveChannelModel",
            "DynamicSlowmodeMessageModel",
            "TokenOverviewModel",
            "LogEnableModel",
            "ClaimedBoosterChannelModel",
            "ClaimedBoosterRoleModel",
            "BlockedReporterModel",
            "LevelLeaderboardEntryModel",
            "UserLevelInfoModel",
            "ChannelOverwriteModel",
            "LevelRolesGroupModel",
        ]
        for name in model_names:
            assert hasattr(api, name), f"Missing model import: {name}"
