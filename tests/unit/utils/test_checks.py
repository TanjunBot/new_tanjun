from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from tests.helpers.discord import (
    make_command_info,
    make_guild,
    make_member,
    make_permissions,
    make_target_member,
    make_text_channel,
)
from utils.checks import (
    can_moderate,
    check_bot_hierarchy,
    check_bot_permission,
    check_executor_hierarchy,
    check_user_permission,
    send_check_failure,
)
from utils.embeds import ErrorEmbedCategory


class TestCheckUserPermission:
    def test_non_member_fails(self):
        info = make_command_info(user=MagicMock())
        result = check_user_permission(info, "ban_members")
        assert result == ("missingPermission", ErrorEmbedCategory.PERMISSION, True)

    def test_missing_guild_permission(self):
        member = make_member()
        member.guild_permissions = make_permissions(ban_members=False)
        info = make_command_info(user=member)
        result = check_user_permission(info, "ban_members", use_guild_permissions=True)
        assert result is not None
        assert result[0] == "missingPermission"

    def test_has_guild_permission(self):
        member = make_member()
        member.guild_permissions = make_permissions(ban_members=True)
        info = make_command_info(user=member)
        assert check_user_permission(info, "ban_members", use_guild_permissions=True) is None

    def test_missing_channel_permission(self):
        member = make_member()
        channel = make_text_channel()
        channel.permissions_for = MagicMock(return_value=make_permissions(manage_messages=False))
        info = make_command_info(user=member, channel=channel)
        result = check_user_permission(info, "manage_messages")
        assert result is not None

    def test_has_channel_permission(self):
        member = make_member()
        channel = make_text_channel()
        channel.permissions_for = MagicMock(return_value=make_permissions(manage_messages=True))
        info = make_command_info(user=member, channel=channel)
        assert check_user_permission(info, "manage_messages") is None

    def test_uses_explicit_channel(self):
        member = make_member()
        invocation_channel = make_text_channel()
        invocation_channel.permissions_for = MagicMock(return_value=make_permissions(manage_messages=False))
        target_channel = make_text_channel()
        target_channel.permissions_for = MagicMock(return_value=make_permissions(manage_messages=True))
        info = make_command_info(user=member, channel=invocation_channel)
        assert check_user_permission(info, "manage_messages", channel=target_channel) is None

    def test_channel_without_permissions_for(self):
        member = make_member()
        channel = MagicMock(spec=[])
        info = make_command_info(user=member, channel=channel)
        result = check_user_permission(info, "manage_messages")
        assert result == ("missingPermission", ErrorEmbedCategory.PERMISSION, True)


class TestCheckBotPermission:
    def test_missing_guild_raises(self):
        from utility import CommandInfo

        info = CommandInfo(
            user=make_member(),
            guild=None,
            channel=make_text_channel(),
            locale="en-US",
            client=MagicMock(),
            command=MagicMock(),
            message=None,
            permissions=MagicMock(),
        )
        with pytest.raises(ValueError, match="Guild is missing"):
            check_bot_permission(info, "ban_members")

    def test_missing_guild_permission(self):
        guild = make_guild(me_permissions=make_permissions(ban_members=False))
        info = make_command_info(guild=guild)
        result = check_bot_permission(info, "ban_members")
        assert result == ("missingPermissionBot", ErrorEmbedCategory.PERMISSION, True)

    def test_has_guild_permission(self):
        guild = make_guild(me_permissions=make_permissions(ban_members=True))
        info = make_command_info(guild=guild)
        assert check_bot_permission(info, "ban_members") is None

    def test_channel_permission(self):
        guild = make_guild()
        channel = make_text_channel(guild=guild)
        channel.permissions_for = MagicMock(return_value=make_permissions(manage_messages=True))
        info = make_command_info(guild=guild, channel=channel)
        assert check_bot_permission(info, "manage_messages", channel=channel) is None


class TestCheckExecutorHierarchy:
    def test_non_member_passes(self):
        info = make_command_info(user=MagicMock())
        target = make_target_member(top_role_position=99)
        assert check_executor_hierarchy(info, target) is None

    def test_target_too_high(self):
        executor = make_member(top_role_position=2)
        target = make_target_member(top_role_position=5)
        info = make_command_info(user=executor)
        result = check_executor_hierarchy(info, target)
        assert result == ("targetTooHigh", ErrorEmbedCategory.PERMISSION, False)

    def test_hierarchy_ok(self):
        executor = make_member(top_role_position=10)
        target = make_target_member(top_role_position=2)
        info = make_command_info(user=executor)
        assert check_executor_hierarchy(info, target) is None


class TestCheckBotHierarchy:
    def test_missing_guild_raises(self):
        from utility import CommandInfo

        info = CommandInfo(
            user=make_member(),
            guild=None,
            channel=make_text_channel(),
            locale="en-US",
            client=MagicMock(),
            command=MagicMock(),
            message=None,
            permissions=MagicMock(),
        )
        with pytest.raises(ValueError, match="Guild is missing"):
            check_bot_hierarchy(info, make_target_member())

    def test_bot_too_low(self):
        guild = make_guild(me_top_role_position=2)
        target = make_target_member(top_role_position=5)
        info = make_command_info(guild=guild)
        result = check_bot_hierarchy(info, target)
        assert result == ("targetTooHigh", ErrorEmbedCategory.PERMISSION, False)

    def test_bot_hierarchy_ok(self):
        guild = make_guild(me_top_role_position=50)
        target = make_target_member(top_role_position=2)
        info = make_command_info(guild=guild)
        assert check_bot_hierarchy(info, target) is None


class TestCanModerate:
    def test_user_permission_failure(self):
        member = make_member()
        member.guild_permissions = make_permissions(kick_members=False)
        guild = make_guild(me_permissions=make_permissions(kick_members=True), me_top_role_position=50)
        info = make_command_info(user=member, guild=guild)
        target = make_target_member(top_role_position=1)
        result = can_moderate(info, target, "kick_members", "kick_members")
        assert result is not None
        assert result[0] == "missingPermission"

    def test_bot_permission_failure(self):
        member = make_member()
        member.guild_permissions = make_permissions(kick_members=True)
        guild = make_guild(me_permissions=make_permissions(kick_members=False), me_top_role_position=50)
        info = make_command_info(user=member, guild=guild)
        target = make_target_member(top_role_position=1)
        result = can_moderate(info, target, "kick_members", "kick_members")
        assert result == ("missingPermissionBot", ErrorEmbedCategory.PERMISSION, True)

    def test_executor_hierarchy_failure(self):
        member = make_member(top_role_position=2)
        member.guild_permissions = make_permissions(kick_members=True)
        guild = make_guild(me_permissions=make_permissions(kick_members=True), me_top_role_position=50)
        info = make_command_info(user=member, guild=guild)
        target = make_target_member(top_role_position=5)
        result = can_moderate(info, target, "kick_members", "kick_members")
        assert result == ("targetTooHigh", ErrorEmbedCategory.PERMISSION, False)

    def test_all_pass(self):
        member = make_member(top_role_position=10)
        member.guild_permissions = make_permissions(kick_members=True)
        guild = make_guild(me_permissions=make_permissions(kick_members=True), me_top_role_position=50)
        info = make_command_info(user=member, guild=guild)
        target = make_target_member(top_role_position=2)
        assert can_moderate(info, target, "kick_members", "kick_members") is None


class TestDmContext:
    def test_dm_user_missing_permission(self):
        user = MagicMock()
        info = make_command_info(user=user, guild=None)
        result = check_user_permission(info, "ban_members", use_guild_permissions=True)
        assert result == ("missingPermission", ErrorEmbedCategory.PERMISSION, True)

    def test_dm_can_moderate_fails_on_user_permission(self):
        user = MagicMock()
        info = make_command_info(user=user, guild=None)
        target = make_target_member()
        result = can_moderate(info, target, "kick_members", "kick_members")
        assert result == ("missingPermission", ErrorEmbedCategory.PERMISSION, True)


class TestManagedRolesAndEqualHierarchy:
    def test_equal_executor_target_top_role_fails(self):
        executor = make_member(top_role_position=7)
        target = make_target_member(top_role_position=7)
        info = make_command_info(user=executor)
        result = check_executor_hierarchy(info, target)
        assert result == ("targetTooHigh", ErrorEmbedCategory.PERMISSION, False)

    def test_equal_bot_target_top_role_fails(self):
        guild = make_guild(me_top_role_position=7)
        target = make_target_member(top_role_position=7)
        info = make_command_info(guild=guild)
        result = check_bot_hierarchy(info, target)
        assert result == ("targetTooHigh", ErrorEmbedCategory.PERMISSION, False)

    def test_managed_role_position_still_blocks_executor(self):
        executor = make_member(top_role_position=3)
        target = make_target_member(top_role_position=8)
        target.top_role.managed = True
        info = make_command_info(user=executor)
        result = check_executor_hierarchy(info, target)
        assert result == ("targetTooHigh", ErrorEmbedCategory.PERMISSION, False)


class TestChannelPermissionOverrides:
    def test_override_denies_when_guild_would_allow(self):
        member = make_member()
        member.guild_permissions = make_permissions(manage_messages=True)
        channel = make_text_channel()
        channel.permissions_for = MagicMock(return_value=make_permissions(manage_messages=False))
        info = make_command_info(user=member, channel=channel)
        result = check_user_permission(info, "manage_messages")
        assert result == ("missingPermission", ErrorEmbedCategory.PERMISSION, True)

    def test_override_grants_when_invocation_channel_denies(self):
        member = make_member()
        invocation = make_text_channel()
        invocation.permissions_for = MagicMock(return_value=make_permissions(manage_messages=False))
        override = make_text_channel()
        override.permissions_for = MagicMock(return_value=make_permissions(manage_messages=True))
        info = make_command_info(user=member, channel=invocation)
        assert check_user_permission(info, "manage_messages", channel=override) is None

    def test_bot_channel_override_denies(self):
        guild = make_guild(me_permissions=make_permissions(manage_messages=True))
        channel = make_text_channel(guild=guild)
        channel.permissions_for = MagicMock(return_value=make_permissions(manage_messages=False))
        info = make_command_info(guild=guild, channel=channel)
        result = check_bot_permission(info, "manage_messages", channel=channel)
        assert result == ("missingPermissionBot", ErrorEmbedCategory.PERMISSION, True)


class TestSendCheckFailure:
    @pytest.mark.asyncio
    async def test_none_result_returns_false(self):
        info = make_command_info()
        assert await send_check_failure(info, "kick", None) is False

    @pytest.mark.asyncio
    async def test_sends_error_embed(self):
        info = make_command_info()
        result = ("targetTooHigh", ErrorEmbedCategory.PERMISSION, False)
        with (
            patch("localizer.tanjunLocalizer.localize", side_effect=lambda _loc, key: key),
            patch("utils.checks.categorized_error_embed", return_value=MagicMock()) as mock_embed,
        ):
            sent = await send_check_failure(info, "kick", result)
        assert sent is True
        mock_embed.assert_called_once()
        info.reply.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_sends_warning_embed(self):
        info = make_command_info()
        result = ("missingPermission", ErrorEmbedCategory.PERMISSION, True)
        with (
            patch("localizer.tanjunLocalizer.localize", side_effect=lambda _loc, key: key),
            patch("utils.checks.categorized_warning_embed", return_value=MagicMock()) as mock_embed,
        ):
            sent = await send_check_failure(info, "ban", result)
        assert sent is True
        mock_embed.assert_called_once()
        info.reply.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_localize_keys_and_error_embed_path(self):
        info = make_command_info(locale="de-DE")
        result = ("targetTooHigh", ErrorEmbedCategory.PERMISSION, False)
        localized_keys: list[str] = []

        def _capture(_locale: str, key: str) -> str:
            localized_keys.append(key)
            return key

        embed = MagicMock()
        with (
            patch("localizer.tanjunLocalizer.localize", side_effect=_capture),
            patch("utils.checks.categorized_error_embed", return_value=embed) as mock_embed,
        ):
            await send_check_failure(info, "ban", result)

        assert localized_keys == [
            "commands.admin.ban.targetTooHigh.title",
            "commands.admin.ban.targetTooHigh.description",
        ]
        mock_embed.assert_called_once_with(
            ErrorEmbedCategory.PERMISSION,
            "commands.admin.ban.targetTooHigh.title",
            "commands.admin.ban.targetTooHigh.description",
        )
        info.reply.assert_awaited_once_with(embed=embed)

    @pytest.mark.asyncio
    async def test_localize_keys_and_warning_embed_path(self):
        info = make_command_info()
        result = ("missingPermissionBot", ErrorEmbedCategory.PERMISSION, True)
        localized_keys: list[str] = []

        def _capture(_locale: str, key: str) -> str:
            localized_keys.append(key)
            return key

        embed = MagicMock()
        with (
            patch("localizer.tanjunLocalizer.localize", side_effect=_capture),
            patch("utils.checks.categorized_warning_embed", return_value=embed) as mock_embed,
        ):
            await send_check_failure(info, "kick", result)

        assert localized_keys == [
            "commands.admin.kick.missingPermissionBot.title",
            "commands.admin.kick.missingPermissionBot.description",
        ]
        mock_embed.assert_called_once_with(
            "commands.admin.kick.missingPermissionBot.title",
            "commands.admin.kick.missingPermissionBot.description",
        )
        info.reply.assert_awaited_once_with(embed=embed)
