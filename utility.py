"""
``utility.py`` — backward-compatible re-export module.

This module has been split into focused sub-modules under ``utils/``:

- ``utils/embeds.py`` — ``EmbedColor``, ``StatusIcon``, ``TanjunEmbed``, embed builders
- ``utils/math.py`` — ``NumericStringParser``, ``eval_expr``, level/XP calculations
- ``utils/time.py`` — relative time string helpers
- ``utils/http.py`` — ``getGif``, ``upload_image_to_imgbb``, ``upload_to_tanjun_logs``
- ``utils/github.py`` — ``missingLocalization``, ``addFeedback``
- ``utils/async_io.py`` — ``run_blocking``

All public symbols are re-exported here for backward compatibility.
New code should import from the specific ``utils.*`` modules instead.
"""

# ruff: noqa: F401, F403

import logging
from difflib import SequenceMatcher as _SequenceMatcher
from typing import Any

import discord

# Re-export from sub-modules
from utils.async_io import run_blocking
from utils.embeds import (
    EMOJI_MAP,
    EmbedAuthor,
    EmbedColor,
    EmbedField,
    EmbedFooter,
    EmbedMedia,
    EmbedProvider,
    EmbedVideo,
    ErrorEmbedCategory,
    StatusIcon,
    TanjunEmbed,
    categorized_error_embed,
    categorized_info_embed,
    categorized_success_embed,
    categorized_warning_embed,
    embed_or_wrap,
    error_embed,
    get_icon_emoji,
    info_embed,
    success_embed,
    tanjunEmbed,
    warning_embed,
)
from utils.github import addFeedback, missingLocalization
from utils.http import getGif, upload_image_to_imgbb, upload_to_tanjun_logs
from utils.math import (
    LEVEL_SCALINGS,
    LevelThresholdCache,
    NumericStringParser,
    cmp,
    eval_expr,
    eval_expr_async,
    get_level_for_xp,
    get_level_for_xp_async,
    get_xp_for_level,
    get_xp_for_level_async,
    log_n,
    sqrt_n,
)
from utils.time import (
    date_time_to_timestamp,
    dateToRelativeTimeStr,
    isoTimeToDate,
    relativeTimeStrToDate,
    relativeTimeToSeconds,
)

# ---------------------------------------------------------------------------
# Misc helpers (not moved to sub-modules)
# ---------------------------------------------------------------------------


def check_if_str_is_hex_color(color: str) -> bool:
    try:
        int(color, 16)
        return True
    except ValueError:
        return False


def draw_text_with_outline(  # noqa: ANN001
    draw: object,
    position: tuple[int, int],
    text: str,
    font: object,
    text_color: object,
    outline_color: object,
) -> None:
    x, y = position
    draw.text((x - 1, y - 1), text, font=font, fill=outline_color)
    draw.text((x + 1, y - 1), text, font=font, fill=outline_color)
    draw.text((x - 1, y + 1), text, font=font, fill=outline_color)
    draw.text((x + 1, y + 1), text, font=font, fill=outline_color)
    draw.text(position, text, font=font, fill=text_color)


def similar(a: str, b: str) -> float:
    return _SequenceMatcher(None, a, b).ratio()


def add_thousands_separator(number: int) -> str:
    return f"{number:,}".replace(",", " ")


addThousandsSeparator = add_thousands_separator  # noqa: N816


# ---------------------------------------------------------------------------
# CommandInfo — originally a Pydantic model in utility.py.
# ---------------------------------------------------------------------------


class CommandInfo:
    """CommandInfo class that accepts keyword arguments for Discord command metadata."""

    def __init__(self, **kwargs: Any) -> None:
        self.user = kwargs.get("user")
        self.channel = kwargs.get("channel")
        self.guild = kwargs.get("guild")
        self.command = kwargs.get("command")
        self.locale = kwargs.get("locale")
        self.message = kwargs.get("message")
        self.permissions = kwargs.get("permissions")
        self.reply = kwargs.get("reply")
        self.client = kwargs.get("client")


command_info: type = CommandInfo


# ---------------------------------------------------------------------------
# SafeInteraction — kept in utility.py for simplicity
# ---------------------------------------------------------------------------


class SafeInteraction:
    """Helper for safely responding to Discord interactions, preventing double-respond errors.

    Use instead of ``interaction.response.send_message()``,
    ``interaction.response.defer()``, and ``interaction.edit_original_response()``
    to handle race conditions when ``interaction_check`` or other code paths
    may have already responded.

    Usage::

        embed = utility.TanjunEmbed(title="Done", description="Operation complete.")
        await SafeInteraction.respond(interaction, embed=embed)
    """

    @staticmethod
    async def respond(
        interaction: discord.Interaction,
        embed: discord.Embed | None = None,
        content: str | None = None,
        ephemeral: bool = False,
        view: discord.ui.View | None = None,
    ) -> None:
        """Respond to an interaction, safely handling already-responded state."""
        kwargs: dict[str, Any] = {"ephemeral": ephemeral}
        if embed is not None:
            kwargs["embed"] = embed
        if content is not None:
            kwargs["content"] = content
        if view is not None:
            kwargs["view"] = view

        if interaction.response.is_done():
            await interaction.followup.send(**kwargs)
        else:
            try:
                await interaction.response.send_message(**kwargs)
            except discord.InteractionResponded:
                await interaction.followup.send(**kwargs)

    @staticmethod
    async def defer(
        interaction: discord.Interaction,
        ephemeral: bool = False,
    ) -> None:
        """Safely defer an interaction, skipping if already done."""
        if not interaction.response.is_done():
            try:
                await interaction.response.defer(ephemeral=ephemeral)
            except discord.InteractionResponded:
                pass

    @staticmethod
    async def edit(
        interaction: discord.Interaction,
        embed: discord.Embed | None = None,
        content: str | None = None,
        view: discord.ui.View | None = None,
    ) -> None:
        """Safely edit the original interaction response."""
        kwargs: dict[str, Any] = {}
        if embed is not None:
            kwargs["embed"] = embed
        if content is not None:
            kwargs["content"] = content
        if view is not None:
            kwargs["view"] = view

        if interaction.response.is_done():
            await interaction.edit_original_response(**kwargs)
        else:
            try:
                await interaction.response.send_message(**kwargs)
            except discord.InteractionResponded:
                await interaction.edit_original_response(**kwargs)


# ---------------------------------------------------------------------------
# DiscordSafe — kept in utility.py for simplicity
# ---------------------------------------------------------------------------


class DiscordSafe:
    """Safely call Discord API methods with proper error handling."""

    @staticmethod
    async def send(
        channel: discord.abc.Messageable,
        content: str | None = None,
        embed: discord.Embed | None = None,
    ) -> discord.Message | None:
        try:
            kwargs: dict[str, str | discord.Embed] = {}
            if content is not None:
                kwargs["content"] = content
            if embed is not None:
                kwargs["embed"] = embed
            return await channel.send(**kwargs)
        except discord.Forbidden:
            logging.warning("Cannot send message in %s: Forbidden", channel.id)
        except discord.HTTPException as e:
            logging.error("HTTP error sending message in %s: %s", channel.id, e.status)
        return None

    @staticmethod
    async def send_dm(user: discord.User | discord.Member, content: str) -> bool:
        try:
            await user.send(content)
            return True
        except discord.Forbidden:
            logging.warning("Cannot send DM to %s: Forbidden", user.id)
        except discord.HTTPException as e:
            logging.error("HTTP error sending DM to %s: %s", user.id, e.status)
        return False

    @staticmethod
    async def delete(message: discord.Message) -> bool:
        try:
            await message.delete()
            return True
        except discord.NotFound:
            return True
        except discord.Forbidden:
            logging.warning("Cannot delete message %s: Forbidden", message.id)
        except discord.HTTPException as e:
            logging.error("HTTP error deleting message %s: %s", message.id, e.status)
        return False

    @staticmethod
    async def reply(
        message: discord.Message,
        embed: discord.Embed | None = None,
        content: str | None = None,
    ) -> discord.Message | None:
        try:
            kwargs: dict[str, str | discord.Embed] = {}
            if content is not None:
                kwargs["content"] = content
            if embed is not None:
                kwargs["embed"] = embed
            return await message.reply(**kwargs)
        except discord.Forbidden:
            logging.warning("Cannot reply to %s: Forbidden", message.id)
        except discord.HTTPException as e:
            logging.error("HTTP error replying to %s: %s", message.id, e.status)
        return None

    @staticmethod
    async def add_reaction(message: discord.Message, emoji: str) -> bool:
        try:
            await message.add_reaction(emoji)
            return True
        except discord.Forbidden:
            logging.warning("Cannot add reaction to %s: Forbidden", message.id)
        except discord.NotFound:
            logging.warning(
                "Cannot add reaction '%s' to message %s: Message not found (already deleted)",
                emoji,
                message.id,
            )
        except discord.HTTPException as e:
            logging.warning(
                "HTTP error adding reaction '%s' to message %s: status=%s, text=%s",
                emoji,
                message.id,
                e.status,
                e.text,
            )
        return False
