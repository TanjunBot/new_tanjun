"""Global app command error handler.

Catches all unhandled application command errors and responds with localized
error embeds instead of Discord's generic "Interaction failed" message.
"""

import logging
import traceback
from typing import Any

import discord
from discord import app_commands
from discord.ext import commands

from localizer import tanjunLocalizer
from utility import ErrorEmbedCategory

logger = logging.getLogger(__name__)


def _get_locale(interaction: discord.Interaction) -> str:
    """Resolve a usable locale string from the interaction.

    Falls back to ``"en"`` when the interaction has no guild or locale.
    Normalizes locale strings to primary language subtag (e.g. "de-DE" -> "de").
    """
    locale_str = None
    if interaction.guild_locale is not None:
        locale_str = interaction.guild_locale.value
    # Fall back to user locale when guild locale is unavailable (DMs etc.)
    elif interaction.locale is not None:
        locale_str = interaction.locale.value

    if locale_str is None:
        return "en"

    # Normalize to primary language subtag: "de-DE" -> "de", "en_US" -> "en"
    primary_lang = str(locale_str).split('-')[0].split('_')[0].lower()
    return primary_lang if primary_lang else "en"


class ErrorHandlerCog(commands.Cog):
    """Cog that registers a global tree.on_error handler at startup."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        """Replace the default tree.on_error with our handler once the bot is ready."""
        self.bot.tree.on_error = self._on_app_command_error
        logger.info("Global app command error handler registered on ready.")

    async def _build_error_embed(
        self,
        interaction: discord.Interaction,
        category: ErrorEmbedCategory = ErrorEmbedCategory.UNEXPECTED,
        locale_key: str = "errors.unexpected_error",
        **kwargs: Any,
    ) -> discord.Embed:
        """Build a localized error embed for the given translation key.

        Parameters
        ----------
        interaction:
            The interaction to derive the locale and guild from.
        category:
            The error category to determine embed colour.
        locale_key:
            The dot-notation localizer key (e.g. ``"errors.cooldown"``).
        **kwargs:
            Extra substitution variables for the translation template.
        """
        locale = _get_locale(interaction)

        title_key = f"{locale_key}.title"
        desc_key = f"{locale_key}.description"

        title: str = tanjunLocalizer.localize(locale, title_key, **kwargs)
        description: str = tanjunLocalizer.localize(locale, desc_key, **kwargs)

        embed = discord.Embed(
            title=title if "no translation found" not in title.lower() else "Error",
            description=description if "no translation found" not in description.lower() else "An unexpected error occurred.",
            colour=category.value,
        )
        return embed

    async def _on_app_command_error(
        self,
        interaction: discord.Interaction,
        error: app_commands.AppCommandError,
    ) -> None:
        """Global error handler for all tree / slash command errors."""
        # Unwrap from CommandInvokeError if needed
        original = error.original if isinstance(error, app_commands.CommandInvokeError) else error

        # ── Known error types ──────────────────────────────────────────────

        if isinstance(original, app_commands.CommandOnCooldown):
            embed = await self._build_error_embed(
                interaction,
                ErrorEmbedCategory.RATE_LIMIT,
                "errors.cooldown",
                retry_after=round(original.retry_after, 1),
            )

        elif isinstance(original, app_commands.CheckFailure):
            # Covers MissingPermissions, BotMissingPermissions, etc.
            missing_permissions = None
            if isinstance(original, (app_commands.MissingPermissions, app_commands.BotMissingPermissions)):
                # Extract missing permissions and format as comma-separated list
                perms = getattr(original, 'missing_permissions', None)
                if perms:
                    missing_permissions = ", ".join(str(p).replace("_", " ").title() for p in perms)

            embed = await self._build_error_embed(
                interaction,
                ErrorEmbedCategory.PERMISSION,
                "errors.missing_permissions",
                missing_permissions=missing_permissions or "Unknown",
            )

        elif isinstance(original, discord.Forbidden):
            embed = await self._build_error_embed(
                interaction,
                ErrorEmbedCategory.PERMISSION,
                "errors.forbidden",
            )

        elif isinstance(original, discord.HTTPException):
            embed = await self._build_error_embed(
                interaction,
                ErrorEmbedCategory.UNEXPECTED,
                "errors.http_error",
                status_code=original.status,
            )

        elif isinstance(original, app_commands.CommandNotFound):
            # Silently drop – these are noise.
            return

        elif isinstance(original, app_commands.TransformerError):
            embed = await self._build_error_embed(
                interaction,
                ErrorEmbedCategory.VALIDATION,
                "errors.transformer_error",
            )

        elif isinstance(original, commands.CommandInvokeError):
            # This shouldn't normally reach here but just in case.
            traceback.print_exception(type(original), original, original.__traceback__)
            embed = await self._build_error_embed(
                interaction,
                ErrorEmbedCategory.UNEXPECTED,
                "errors.unexpected_error",
            )

        else:
            # Log unexpected errors with full traceback.
            logger.exception(
                "Unhandled app command error in %s: %s",
                interaction.command.qualified_name if interaction.command else "unknown",
                original,
            )
            traceback.print_exception(type(original), original, original.__traceback__)
            embed = await self._build_error_embed(
                interaction,
                ErrorEmbedCategory.UNEXPECTED,
                "errors.unexpected_error",
            )

        # ── Send the embed (graceful fallback) ─────────────────────────────
        try:
            if interaction.response.is_done():
                await interaction.followup.send(embed=embed, ephemeral=True)
            else:
                await interaction.response.send_message(embed=embed, ephemeral=True)
        except Exception:
            logger.exception("Failed to send error embed — giving up.")


async def setup(bot: commands.Bot) -> None:
    """Load the ErrorHandlerCog."""
    await bot.add_cog(ErrorHandlerCog(bot))
    logger.info("ErrorHandlerCog loaded.")
