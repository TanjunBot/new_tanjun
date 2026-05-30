from __future__ import annotations

import sys
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from tests.helpers.discord import make_interaction
from utility import ErrorEmbedCategory

pytestmark = [pytest.mark.asyncio, pytest.mark.e2e]


def _app_commands():
    from tests.e2e.conftest import _ensure_app_command_errors

    _ensure_app_command_errors()
    return sys.modules["discord"].app_commands


async def test_get_locale_from_guild(error_cog):
    from extensions.error_handler import _get_locale

    interaction = make_interaction(locale="de-DE")
    interaction.guild_locale = MagicMock(value="de")
    assert _get_locale(interaction) == "de"


async def test_get_locale_defaults_to_en(error_cog):
    from extensions.error_handler import _get_locale

    interaction = make_interaction()
    interaction.guild_locale = None
    interaction.locale = None
    assert _get_locale(interaction) == "en"


async def test_get_locale_user_fallback(error_cog):
    from extensions.error_handler import _get_locale

    interaction = make_interaction()
    interaction.guild_locale = None
    interaction.locale = MagicMock(value="fr-FR")
    assert _get_locale(interaction) == "fr"


async def test_cooldown_error_sends_embed(error_cog):
    interaction = make_interaction()
    interaction.response.is_done = MagicMock(return_value=False)
    interaction.response.send_message = AsyncMock()
    error = _app_commands().CommandOnCooldown()
    error.retry_after = 5.0
    await error_cog._on_app_command_error(interaction, error)
    interaction.response.send_message.assert_awaited_once()


async def test_check_failure_sends_followup(error_cog):
    interaction = make_interaction()
    interaction.response.is_done = MagicMock(return_value=True)
    interaction.followup.send = AsyncMock()
    error = _app_commands().CheckFailure("no permission")
    await error_cog._on_app_command_error(interaction, error)
    interaction.followup.send.assert_awaited_once()


async def test_missing_permissions_error(error_cog):
    interaction = make_interaction()
    interaction.response.is_done = MagicMock(return_value=False)
    interaction.response.send_message = AsyncMock()
    error = _app_commands().MissingPermissions(["manage_messages"])
    await error_cog._on_app_command_error(interaction, error)
    interaction.response.send_message.assert_awaited_once()


async def test_bot_missing_permissions_error(error_cog):
    interaction = make_interaction()
    interaction.response.is_done = MagicMock(return_value=False)
    interaction.response.send_message = AsyncMock()
    error = _app_commands().BotMissingPermissions(["send_messages"])
    await error_cog._on_app_command_error(interaction, error)
    interaction.response.send_message.assert_awaited_once()


async def test_command_not_found_silent(error_cog):
    interaction = make_interaction()
    interaction.response.send_message = AsyncMock()
    error = _app_commands().CommandNotFound("missing")
    await error_cog._on_app_command_error(interaction, error)
    interaction.response.send_message.assert_not_awaited()


async def test_transformer_error_sends_embed(error_cog):
    interaction = make_interaction()
    interaction.response.is_done = MagicMock(return_value=False)
    interaction.response.send_message = AsyncMock()
    ac = _app_commands()
    error = ac.TransformerError(MagicMock(), MagicMock(), ValueError())
    await error_cog._on_app_command_error(interaction, error)
    interaction.response.send_message.assert_awaited_once()


async def test_command_invoke_error_unwraps(error_cog):
    interaction = make_interaction()
    interaction.response.is_done = MagicMock(return_value=False)
    interaction.response.send_message = AsyncMock()
    inner = RuntimeError("boom")
    wrapped = _app_commands().CommandInvokeError(inner)
    await error_cog._on_app_command_error(interaction, wrapped)
    interaction.response.send_message.assert_awaited_once()


async def test_unexpected_error_without_sentry(error_cog):
    interaction = make_interaction()
    interaction.response.is_done = MagicMock(return_value=False)
    interaction.response.send_message = AsyncMock()
    with patch("extensions.error_handler.sentry_dsn", ""):
        await error_cog._on_app_command_error(interaction, RuntimeError("unexpected"))
    interaction.response.send_message.assert_awaited_once()


async def test_on_ready_registers_tree_handler(e2e_bot, error_cog):
    await error_cog.on_ready()
    assert e2e_bot.tree.on_error == error_cog._on_app_command_error


async def test_build_error_embed(error_cog):
    interaction = make_interaction()
    embed = await error_cog._build_error_embed(
        interaction,
        ErrorEmbedCategory.UNEXPECTED,
        "errors.unexpected_error",
    )
    assert embed is not None


async def test_build_error_embed_cooldown_key(error_cog):
    interaction = make_interaction()
    embed = await error_cog._build_error_embed(
        interaction,
        ErrorEmbedCategory.RATE_LIMIT,
        "errors.cooldown",
        retry_after=3.0,
    )
    assert embed is not None


async def test_send_failure_swallowed(error_cog):
    interaction = make_interaction()
    interaction.response.is_done = MagicMock(return_value=False)
    interaction.response.send_message = AsyncMock(side_effect=RuntimeError("send failed"))
    await error_cog._on_app_command_error(interaction, _app_commands().CheckFailure("x"))


async def test_set_sentry_context_noop_without_dsn():
    from extensions.error_handler import _set_sentry_context

    interaction = make_interaction()
    with patch("extensions.error_handler.sentry_dsn", ""):
        _set_sentry_context(interaction)
