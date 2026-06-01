from __future__ import annotations

from collections.abc import Callable
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import discord
import pytest
from discord import app_commands
from discord.ext import commands

from extensions.error_handler import ErrorHandlerCog
from tests.helpers.discord import make_guild, make_interaction, make_member, make_text_channel
from tests.integration.extensions.conftest import load_extension_bot
from utility import ErrorEmbedCategory

pytestmark = pytest.mark.asyncio

EXTENSION = "extensions.error_handler"


def _interaction(*, response_done: bool = False) -> MagicMock:
    ix = make_interaction(locale="en-US")
    ix.id = 12345
    ix.channel_id = 444444444
    ix.user = make_member()
    ix.guild = make_guild()
    ix.guild.name = "Test Guild"
    ix.command.qualified_name = "test_cmd"
    ix.guild_locale = MagicMock(value="en-US")
    ix.locale = MagicMock(value="en-US")
    ix.response.is_done = MagicMock(return_value=response_done)
    ix.response.send_message = AsyncMock()
    ix.followup.send = AsyncMock()
    return ix


async def _cog() -> ErrorHandlerCog:
    bot = await load_extension_bot(EXTENSION, fire_ready=True)
    return bot.cogs["ErrorHandlerCog"]


def _http_exception(status: int) -> discord.HTTPException:
    exc = discord.HTTPException(MagicMock(), "server error")
    exc.status = status
    return exc


@pytest.mark.parametrize(
    ("error_factory", "locale_key", "category"),
    [
        pytest.param(
            lambda: app_commands.CommandOnCooldown(retry_after=8.3),
            "errors.cooldown",
            ErrorEmbedCategory.RATE_LIMIT,
            id="cooldown",
        ),
        pytest.param(
            lambda: app_commands.MissingPermissions(["manage_messages", "ban_members"]),
            "errors.missing_permissions",
            ErrorEmbedCategory.PERMISSION,
            id="missing_permissions",
        ),
        pytest.param(
            lambda: app_commands.BotMissingPermissions(["send_messages"]),
            "errors.missing_permissions",
            ErrorEmbedCategory.PERMISSION,
            id="bot_missing_permissions",
        ),
        pytest.param(
            lambda: app_commands.CheckFailure("generic check failed"),
            "errors.missing_permissions",
            ErrorEmbedCategory.PERMISSION,
            id="check_failure",
        ),
        pytest.param(
            lambda: discord.Forbidden(MagicMock(), "forbidden"),
            "errors.forbidden",
            ErrorEmbedCategory.PERMISSION,
            id="forbidden",
        ),
        pytest.param(
            lambda: _http_exception(503),
            "errors.http_error",
            ErrorEmbedCategory.UNEXPECTED,
            id="http_exception",
        ),
        pytest.param(
            lambda: app_commands.TransformerError(MagicMock(), ValueError("bad input")),
            "errors.transformer_error",
            ErrorEmbedCategory.VALIDATION,
            id="transformer_error",
        ),
        pytest.param(
            lambda: RuntimeError("unexpected failure"),
            "errors.unexpected_error",
            ErrorEmbedCategory.UNEXPECTED,
            id="unknown",
        ),
    ],
)
async def test_on_app_command_error_matrix(
    error_factory: Callable[[], Exception],
    locale_key: str,
    category: ErrorEmbedCategory,
) -> None:
    cog = await _cog()
    ix = _interaction()
    error = error_factory()
    localized_keys: list[str] = []

    def _capture(_locale: str, key: str, **kwargs: Any) -> str:
        localized_keys.append(key)
        return key

    with (
        patch("extensions.error_handler.tanjunLocalizer.localize", side_effect=_capture),
        patch("extensions.error_handler.sentry_dsn", ""),
    ):
        await cog._on_app_command_error(ix, error)

    assert f"{locale_key}.title" in localized_keys
    assert f"{locale_key}.description" in localized_keys
    ix.response.send_message.assert_awaited_once()
    sent_embed = ix.response.send_message.await_args.kwargs["embed"]
    assert sent_embed.colour == category.value


async def test_command_not_found_sends_no_embed() -> None:
    cog = await _cog()
    ix = _interaction()
    with patch("extensions.error_handler.sentry_dsn", ""):
        await cog._on_app_command_error(ix, app_commands.CommandNotFound("missing", []))
    ix.response.send_message.assert_not_called()
    ix.followup.send.assert_not_called()


async def test_unknown_error_reports_to_sentry_when_configured() -> None:
    cog = await _cog()
    ix = _interaction()
    push_scope = MagicMock()
    push_scope.__enter__ = MagicMock(return_value=MagicMock())
    push_scope.__exit__ = MagicMock(return_value=False)

    with (
        patch("extensions.error_handler.sentry_dsn", "https://example@sentry.io/1"),
        patch("sentry_sdk.push_scope", return_value=push_scope),
        patch("extensions.error_handler.tanjunLocalizer.localize", side_effect=lambda _l, k, **kw: k),
    ):
        await cog._on_app_command_error(ix, RuntimeError("boom"))

    ix.response.send_message.assert_awaited_once()


@pytest.mark.parametrize(
    "error_factory",
    [
        pytest.param(lambda: app_commands.CommandOnCooldown(retry_after=1.0), id="cooldown"),
        pytest.param(lambda: app_commands.MissingPermissions(["kick_members"]), id="missing_permissions"),
        pytest.param(lambda: discord.Forbidden(MagicMock(), "forbidden"), id="forbidden"),
        pytest.param(lambda: ValueError("unknown"), id="unknown"),
    ],
)
async def test_matrix_sends_via_followup_when_response_done(
    error_factory: Callable[[], Exception],
) -> None:
    cog = await _cog()
    ix = _interaction(response_done=True)
    with patch("extensions.error_handler.sentry_dsn", ""):
        await cog._on_app_command_error(ix, error_factory())
    ix.followup.send.assert_awaited_once()
    ix.response.send_message.assert_not_called()


def _prefix_context() -> MagicMock:
    guild = make_guild()
    guild.preferred_locale = "en-US"
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
    return ctx


@pytest.mark.parametrize(
    ("error_factory", "locale_key", "category"),
    [
        pytest.param(
            lambda: commands.CommandOnCooldown(retry_after=8.3),
            "errors.cooldown",
            ErrorEmbedCategory.RATE_LIMIT,
            id="cooldown",
        ),
        pytest.param(
            lambda: commands.MissingPermissions(["manage_messages"]),
            "errors.missing_permissions",
            ErrorEmbedCategory.PERMISSION,
            id="missing_permissions",
        ),
        pytest.param(
            lambda: commands.BotMissingPermissions(["send_messages"]),
            "errors.missing_permissions",
            ErrorEmbedCategory.PERMISSION,
            id="bot_missing_permissions",
        ),
        pytest.param(
            lambda: commands.CheckFailure("generic check failed"),
            "errors.missing_permissions",
            ErrorEmbedCategory.PERMISSION,
            id="check_failure",
        ),
        pytest.param(
            lambda: discord.Forbidden(MagicMock(), "forbidden"),
            "errors.forbidden",
            ErrorEmbedCategory.PERMISSION,
            id="forbidden",
        ),
        pytest.param(
            lambda: commands.CommandInvokeError(discord.Forbidden(MagicMock(), "forbidden")),
            "errors.forbidden",
            ErrorEmbedCategory.PERMISSION,
            id="invoke_forbidden",
        ),
        pytest.param(
            lambda: _http_exception(503),
            "errors.http_error",
            ErrorEmbedCategory.UNEXPECTED,
            id="http_exception",
        ),
        pytest.param(
            lambda: commands.BadArgument("bad input"),
            "errors.transformer_error",
            ErrorEmbedCategory.VALIDATION,
            id="bad_argument",
        ),
        pytest.param(
            lambda: RuntimeError("unexpected failure"),
            "errors.unexpected_error",
            ErrorEmbedCategory.UNEXPECTED,
            id="unknown",
        ),
    ],
)
async def test_on_prefix_command_error_matrix(
    error_factory: Callable[[], Exception],
    locale_key: str,
    category: ErrorEmbedCategory,
) -> None:
    cog = await _cog()
    ctx = _prefix_context()
    error = error_factory()
    localized_keys: list[str] = []

    def _capture(_locale: str, key: str, **kwargs: Any) -> str:
        localized_keys.append(key)
        return key

    with (
        patch("extensions.error_handler.tanjunLocalizer.localize", side_effect=_capture),
        patch("extensions.error_handler.sentry_dsn", ""),
    ):
        await cog._on_prefix_command_error(ctx, error)

    assert f"{locale_key}.title" in localized_keys
    assert f"{locale_key}.description" in localized_keys
    ctx.send.assert_awaited_once()
    sent_embed = ctx.send.await_args.kwargs["embed"]
    assert sent_embed.colour == category.value


async def test_prefix_command_not_found_sends_no_embed() -> None:
    cog = await _cog()
    ctx = _prefix_context()
    with patch("extensions.error_handler.sentry_dsn", ""):
        await cog._on_prefix_command_error(ctx, commands.CommandNotFound("missing"))
    ctx.send.assert_not_called()


def _http_exception_40060() -> discord.HTTPException:
    exc = discord.HTTPException(MagicMock(), "already acknowledged")
    exc.status = 400
    exc.code = 40060
    return exc


async def test_slash_http_40060_original_silent() -> None:
    cog = await _cog()
    ix = _interaction()
    with patch("extensions.error_handler.sentry_dsn", ""):
        await cog._on_app_command_error(ix, _http_exception_40060())
    ix.response.send_message.assert_not_called()


async def test_slash_ephemeral_on_send() -> None:
    cog = await _cog()
    ix = _interaction()
    with patch("extensions.error_handler.sentry_dsn", ""):
        await cog._on_app_command_error(ix, app_commands.CheckFailure("x"))
    assert ix.response.send_message.await_args.kwargs.get("ephemeral") is True
