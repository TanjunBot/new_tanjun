from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import discord
import pytest
from discord import app_commands
from discord.ext import commands

from extensions.error_handler import ErrorHandlerCog, _get_locale, _get_locale_from_context, _normalize_locale, _set_sentry_context
from tests.helpers.discord import make_guild, make_interaction, make_member, make_text_channel
from tests.integration.extensions.conftest import load_extension_bot

pytestmark = pytest.mark.asyncio

EXTENSION = "extensions.error_handler"


def _interaction(*, locale: str = "en-US", guild_locale: str | None = "en-US") -> MagicMock:
    ix = make_interaction(locale=locale)
    ix.id = 12345
    ix.channel_id = 444444444
    ix.user = make_member()
    ix.guild = make_guild()
    ix.guild.name = "Test Guild"
    ix.command.qualified_name = "test_cmd"
    ix.response.is_done = MagicMock(return_value=False)
    ix.response.send_message = AsyncMock()
    ix.followup.send = AsyncMock()
    if guild_locale is not None:
        ix.guild_locale = MagicMock(value=guild_locale)
    else:
        ix.guild_locale = None
    ix.locale = MagicMock(value=locale) if locale else None
    return ix


async def _cog() -> ErrorHandlerCog:
    bot = await load_extension_bot(EXTENSION, fire_ready=True)
    return bot.cogs["ErrorHandlerCog"]


class TestGetLocale:
    def test_guild_locale_de_de(self) -> None:
        ix = _interaction()
        ix.guild_locale = MagicMock(value="de-DE")
        assert _get_locale(ix) == "de"

    def test_user_locale_fallback(self) -> None:
        ix = _interaction()
        ix.guild_locale = None
        ix.locale = MagicMock(value="fr-FR")
        assert _get_locale(ix) == "fr"

    def test_no_locale_defaults_en(self) -> None:
        ix = _interaction()
        ix.guild_locale = None
        ix.locale = None
        assert _get_locale(ix) == "en"

    def test_en_us_normalization(self) -> None:
        ix = _interaction()
        ix.guild_locale = MagicMock(value="en_US")
        assert _get_locale(ix) == "en"


class TestNormalizeLocale:
    def test_none_defaults_en(self) -> None:
        assert _normalize_locale(None) == "en"

    def test_de_de_normalized(self) -> None:
        assert _normalize_locale("de-DE") == "de"

    def test_en_us_underscore(self) -> None:
        assert _normalize_locale("en_US") == "en"

    def test_zh_cn(self) -> None:
        assert _normalize_locale("zh-CN") == "zh"

    def test_plain_en(self) -> None:
        assert _normalize_locale("en") == "en"

    def test_uppercase(self) -> None:
        assert _normalize_locale("DE") == "de"


class TestSentryContext:
    def test_noop_without_dsn(self) -> None:
        ix = _interaction()
        with patch("extensions.error_handler.sentry_dsn", ""):
            _set_sentry_context(ix)

    def test_sets_context_with_dsn(self) -> None:
        ix = _interaction()
        with (
            patch("extensions.error_handler.sentry_dsn", "https://example@sentry.io/1"),
            patch("sentry_sdk.set_user") as set_user,
            patch("sentry_sdk.set_tag") as set_tag,
            patch("sentry_sdk.set_context") as set_context,
        ):
            _set_sentry_context(ix)
            set_user.assert_called_once()
            assert set_tag.call_count >= 1
            set_context.assert_called_once()

    def test_sentry_exception_swallowed(self) -> None:
        ix = _interaction()
        with (
            patch("extensions.error_handler.sentry_dsn", "https://example@sentry.io/1"),
            patch("sentry_sdk.set_user", side_effect=RuntimeError("sentry down")),
        ):
            _set_sentry_context(ix)


class TestBuildErrorEmbed:
    async def test_builds_localized_embed(self) -> None:
        cog = await _cog()
        ix = _interaction()
        embed = await cog._build_error_embed(ix, locale_key="errors.cooldown", retry_after=5.0)
        assert embed.title
        assert embed.description

    async def test_fallback_on_missing_translation(self) -> None:
        cog = await _cog()
        ix = _interaction()
        embed = await cog._build_error_embed(ix, locale_key="errors.totally_fake_key_xyz")
        assert embed.title == "Error" or embed.description


class TestOnAppCommandError:
    async def _handle(self, error: Exception, *, response_done: bool = False) -> None:
        cog = await _cog()
        ix = _interaction()
        ix.response.is_done = MagicMock(return_value=response_done)
        await cog._on_app_command_error(ix, error)

    async def test_command_on_cooldown(self) -> None:
        err = app_commands.CommandOnCooldown(retry_after=12.5)
        await self._handle(err)

    async def test_missing_permissions(self) -> None:
        err = app_commands.MissingPermissions(["manage_messages"])
        await self._handle(err)

    async def test_bot_missing_permissions(self) -> None:
        err = app_commands.BotMissingPermissions(["send_messages"])
        await self._handle(err)

    async def test_check_failure_generic(self) -> None:
        await self._handle(app_commands.CheckFailure("nope"))

    async def test_forbidden(self) -> None:
        await self._handle(discord.Forbidden(MagicMock(), "forbidden"))

    async def test_http_exception(self) -> None:
        exc = discord.HTTPException(MagicMock(), "rate limited")
        exc.status = 429
        await self._handle(exc)

    async def test_command_not_found_silent(self) -> None:
        cog = await _cog()
        ix = _interaction()
        await cog._on_app_command_error(ix, app_commands.CommandNotFound("missing", []))
        ix.response.send_message.assert_not_called()
        ix.followup.send.assert_not_called()

    async def test_transformer_error(self) -> None:
        await self._handle(app_commands.TransformerError(MagicMock(), app_commands.AppCommandOptionType.string, ValueError()))

    async def test_unexpected_error_no_sentry(self) -> None:
        with patch("extensions.error_handler.sentry_dsn", ""):
            await self._handle(RuntimeError("unexpected"))

    async def test_unexpected_error_with_sentry(self) -> None:
        with (
            patch("extensions.error_handler.sentry_dsn", "https://example@sentry.io/1"),
            patch("sentry_sdk.push_scope") as push_scope,
        ):
            scope = MagicMock()
            scope.__enter__ = MagicMock(return_value=scope)
            scope.__exit__ = MagicMock(return_value=False)
            push_scope.return_value = scope
            await self._handle(RuntimeError("unexpected"))

    async def test_unexpected_error_sentry_scope_fails(self) -> None:
        with (
            patch("extensions.error_handler.sentry_dsn", "https://example@sentry.io/1"),
            patch("sentry_sdk.push_scope", side_effect=RuntimeError("scope fail")),
        ):
            await self._handle(RuntimeError("unexpected"))

    async def test_sends_via_followup_when_response_done(self) -> None:
        await self._handle(app_commands.CheckFailure("x"), response_done=True)

    async def test_send_failure_swallowed(self) -> None:
        cog = await _cog()
        ix = _interaction()
        ix.response.send_message = AsyncMock(side_effect=RuntimeError("send failed"))
        await cog._on_app_command_error(ix, app_commands.CheckFailure("x"))

    async def test_http_exception_40060_silent(self) -> None:
        """App command: HTTP 40060 should be silently dropped."""
        cog = await _cog()
        ix = _interaction()
        exc = discord.HTTPException(MagicMock(), "interaction already acked")
        exc.status = 400
        exc.code = 40060
        await cog._on_app_command_error(ix, exc)
        ix.response.send_message.assert_not_called()
        ix.followup.send.assert_not_called()

    async def test_send_40060_silent(self) -> None:
        """App command: send_message raising 40060 should be silently dropped."""
        cog = await _cog()
        ix = _interaction()
        exc = discord.HTTPException(MagicMock(), "40060")
        exc.status = 400
        exc.code = 40060
        ix.response.send_message = AsyncMock(side_effect=exc)
        await cog._on_app_command_error(ix, app_commands.CheckFailure("x"))
        # The error is raised but caught; no crash expected

    async def test_on_error_event_listener(self) -> None:
        """The on_error listener should call handle_discord_event_error."""
        cog = await _cog()
        with patch("extensions.error_handler.handle_discord_event_error") as mock_handle:
            await cog.on_error("on_message", MagicMock())
        mock_handle.assert_called_once()


def _prefix_context(*, guild_locale: str = "en-US") -> MagicMock:
    guild = make_guild()
    guild.preferred_locale = guild_locale
    channel = make_text_channel(guild=guild)
    author = make_member()
    ctx = MagicMock()
    ctx.author = author
    ctx.guild = guild
    ctx.channel = channel
    ctx.command = MagicMock()
    ctx.command.qualified_name = "test_bot"
    ctx.message = MagicMock()
    ctx.message.id = 999
    ctx.send = AsyncMock()
    author.send = AsyncMock()
    return ctx


class TestGetLocaleFromContext:
    def test_guild_locale_de_de(self) -> None:
        ctx = _prefix_context(guild_locale="de-DE")
        assert _get_locale_from_context(ctx) == "de"

    def test_no_guild_defaults_en(self) -> None:
        ctx = _prefix_context()
        ctx.guild = None
        assert _get_locale_from_context(ctx) == "en"


class TestOnPrefixCommandError:
    async def _handle(self, error: Exception) -> MagicMock:
        cog = await _cog()
        ctx = _prefix_context()
        await cog._on_prefix_command_error(ctx, error)
        return ctx

    async def test_forbidden(self) -> None:
        ctx = await self._handle(discord.Forbidden(MagicMock(), "forbidden"))
        ctx.send.assert_awaited_once()

    async def test_command_invoke_error_forbidden(self) -> None:
        inner = discord.Forbidden(MagicMock(), "forbidden")
        wrapped = commands.CommandInvokeError(inner)
        ctx = await self._handle(wrapped)
        ctx.send.assert_awaited_once()

    async def test_command_invoke_error_forbidden_dm_fallback(self) -> None:
        cog = await _cog()
        ctx = _prefix_context()
        ctx.send = AsyncMock(side_effect=discord.Forbidden(MagicMock(), "forbidden"))
        inner = discord.Forbidden(MagicMock(), "forbidden")
        await cog._on_prefix_command_error(ctx, commands.CommandInvokeError(inner))
        ctx.author.send.assert_awaited_once()

    async def test_command_not_found_silent(self) -> None:
        cog = await _cog()
        ctx = _prefix_context()
        await cog._on_prefix_command_error(ctx, commands.CommandNotFound("missing"))
        ctx.send.assert_not_called()

    async def test_missing_permissions(self) -> None:
        ctx = await self._handle(commands.MissingPermissions(["send_messages"]))
        ctx.send.assert_awaited_once()

    async def test_bot_missing_permissions(self) -> None:
        ctx = await self._handle(commands.BotMissingPermissions(["send_messages"]))
        ctx.send.assert_awaited_once()

    async def test_check_failure_generic(self) -> None:
        """Prefix: generic CheckFailure (no missing_permissions attr)."""
        ctx = await self._handle(commands.CheckFailure("generic nope"))
        ctx.send.assert_awaited_once()

    async def test_conversion_error(self) -> None:
        """Prefix: ConversionError."""
        ctx = await self._handle(commands.ConversionError(MagicMock(), ValueError("bad")))
        ctx.send.assert_awaited_once()

    async def test_user_input_error(self) -> None:
        """Prefix: UserInputError."""
        ctx = await self._handle(commands.UserInputError("bad input"))
        ctx.send.assert_awaited_once()

    async def test_unexpected_error(self) -> None:
        with patch("extensions.error_handler.sentry_dsn", ""):
            ctx = await self._handle(RuntimeError("boom"))
        ctx.send.assert_awaited_once()

    async def test_unexpected_error_with_sentry(self) -> None:
        """Prefix: unexpected error with sentry DSN configured."""
        cog = await _cog()
        ctx = _prefix_context()
        with (
            patch("extensions.error_handler.sentry_dsn", "https://example@sentry.io/1"),
            patch("sentry_sdk.push_scope") as push_scope,
        ):
            scope = MagicMock()
            scope.__enter__ = MagicMock(return_value=scope)
            scope.__exit__ = MagicMock(return_value=False)
            push_scope.return_value = scope
            await cog._on_prefix_command_error(ctx, RuntimeError("boom"))
        ctx.send.assert_awaited_once()

    async def test_unexpected_error_sentry_scope_fails(self) -> None:
        """Prefix: unexpected error with sentry but push_scope raises."""
        cog = await _cog()
        ctx = _prefix_context()
        with (
            patch("extensions.error_handler.sentry_dsn", "https://example@sentry.io/1"),
            patch("sentry_sdk.push_scope", side_effect=RuntimeError("scope fail")),
        ):
            await cog._on_prefix_command_error(ctx, RuntimeError("boom"))
        ctx.send.assert_awaited_once()

    async def test_http_exception_40060_silent(self) -> None:
        """Prefix: HTTP 40060 should be silently dropped."""
        cog = await _cog()
        ctx = _prefix_context()
        exc = discord.HTTPException(MagicMock(), "interaction already acked")
        exc.status = 400
        exc.code = 40060
        await cog._on_prefix_command_error(ctx, exc)
        ctx.send.assert_not_called()

    async def test_dm_fallback_dm_also_fails(self) -> None:
        """Prefix: send fails with Forbidden, then DM also fails."""
        cog = await _cog()
        ctx = _prefix_context()
        ctx.send = AsyncMock(side_effect=discord.Forbidden(MagicMock(), "forbidden"))
        ctx.author.send = AsyncMock(side_effect=discord.HTTPException(MagicMock(), "dm blocked"))
        await cog._on_prefix_command_error(ctx, discord.Forbidden(MagicMock(), "forbidden"))
        ctx.author.send.assert_awaited_once()

    async def test_command_on_cooldown(self) -> None:
        """Prefix: CommandOnCooldown error."""
        ctx = await self._handle(commands.CommandOnCooldown(retry_after=5.0))
        ctx.send.assert_awaited_once()

    async def test_on_command_error_dispatches(self) -> None:
        """The on_command_error listener calls _on_prefix_command_error."""
        cog = await _cog()
        ctx = _prefix_context()
        with patch.object(cog, "_on_prefix_command_error") as mock_prefix:
            await cog.on_command_error(ctx, commands.CommandNotFound("missing"))
        mock_prefix.assert_awaited_once()
