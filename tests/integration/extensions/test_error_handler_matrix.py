from __future__ import annotations

from collections.abc import Callable
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import discord
import pytest
from discord import app_commands

from extensions.error_handler import ErrorHandlerCog
from tests.helpers.discord import make_guild, make_interaction, make_member
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


def _make_error(kind: str) -> Exception:
    if kind == "cooldown":
        return app_commands.CommandOnCooldown(retry_after=8.3)
    if kind == "missing_permissions":
        return app_commands.MissingPermissions(["manage_messages", "ban_members"])
    if kind == "not_found":
        return discord.NotFound(MagicMock(), "resource missing")
    if kind == "unknown":
        return RuntimeError("unexpected failure")
    raise ValueError(f"unknown error kind: {kind}")


@pytest.mark.parametrize(
    ("error_kind", "locale_key", "category"),
    [
        ("cooldown", "errors.cooldown", ErrorEmbedCategory.RATE_LIMIT),
        ("missing_permissions", "errors.missing_permissions", ErrorEmbedCategory.PERMISSION),
        ("not_found", "errors.unexpected_error", ErrorEmbedCategory.UNEXPECTED),
        ("unknown", "errors.unexpected_error", ErrorEmbedCategory.UNEXPECTED),
    ],
)
async def test_on_app_command_error_matrix(
    error_kind: str,
    locale_key: str,
    category: ErrorEmbedCategory,
) -> None:
    cog = await _cog()
    ix = _interaction()
    error = _make_error(error_kind)
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


@pytest.mark.parametrize(
    "error_factory",
    [
        pytest.param(lambda: app_commands.CommandOnCooldown(retry_after=1.0), id="cooldown"),
        pytest.param(lambda: app_commands.MissingPermissions(["kick_members"]), id="missing_permissions"),
        pytest.param(lambda: discord.NotFound(MagicMock(), "missing"), id="not_found"),
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
