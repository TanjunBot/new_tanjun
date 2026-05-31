"""Embed-related utilities: embed types, colors, builders, and the TanjunEmbed model.

Extracted from ``utility.py`` as part of refactoring (issue #1608).
"""

import datetime
import enum
from collections.abc import Mapping
from typing import AbstractSet, Annotated, Any, Self

import discord
from pydantic import BaseModel, ConfigDict, Field, StringConstraints


class EmbedColor(enum.IntEnum):
    """Standardized embed colors for semantic use across the bot."""

    BRAND = 0xCB33F5  # Default for info/neutral messages
    SUCCESS = 0x4BB543  # Green: success confirmations
    WARNING = 0xFFBF00  # Yellow: warnings, rate limits
    ERROR = 0xE74C3C  # Red: errors, failures
    INFO = 0x3498DB  # Blue: information
    TIMEOUT = 0x95A5A6  # Gray: disabled/timeout


class StatusIcon(enum.StrEnum):
    """Standardized status icons used across all embeds and messages.

    Use these instead of hardcoded Unicode emojis to keep icon usage
    consistent.  All values are Unicode fallbacks that render in any
    Discord client without needing Nitro or a guild emoji slot.
    """

    SUCCESS = "✅"
    ERROR = "❌"
    WARNING = "⚠️"
    INFO = "ℹ️"
    LOCK = "🔒"
    PENDING = "⏳"
    DENIED = "🚫"
    CROSS = "❌"
    ENABLED = "✅"
    DISABLED = "❌"


class ErrorEmbedCategory(enum.IntEnum):
    """Categories for error embeds, mapped to distinct colors for visual distinction."""

    PERMISSION = 0xE74C3C
    NOT_FOUND = 0xE67E22
    RATE_LIMIT = 0xF39C12
    VALIDATION = 0x9B59B6
    UNEXPECTED = 0xE74C3C
    TIMEOUT = 0x95A5A6


# Map of friendly keys to guild emoji names.
EMOJI_MAP: dict[str, str] = {
    "checkmark": "check",
    "cross": "cross",
    "loading": "loading",
    "info": "info",
}


async def get_icon_emoji(
    bot: discord.Client,
    emoji_name: str,
    *,
    fallback: str | None = None,
) -> str:
    """Get a Discord guild emoji by friendly key, falling back to a Unicode icon.

    Looks up the friendly key in ``EMOJI_MAP`` to find the actual guild emoji name.
    If the key is not in the map, uses the key directly as the emoji name.
    If the guild emoji is not found (or the bot object is unavailable),
    ``fallback`` is returned; if ``fallback`` is ``None``, ``StatusIcon.INFO``
    is used as the ultimate default.
    """
    actual_emoji_name = EMOJI_MAP.get(emoji_name, emoji_name)

    if emoji := discord.utils.get(bot.emojis, name=actual_emoji_name):
        return str(emoji)
    if fallback is not None:
        return fallback
    return StatusIcon.INFO.value


# ---------------------------------------------------------------------------
# Pydantic sub-models for embed components
# ---------------------------------------------------------------------------


class EmbedField(BaseModel):
    """A single field within a Discord embed."""

    model_config = ConfigDict(populate_by_name=True)

    name: Annotated[str, StringConstraints(max_length=256)]
    value: Annotated[str, StringConstraints(max_length=1024)]
    inline: bool = True


class EmbedFooter(BaseModel):
    """Footer section of a Discord embed."""

    text: Annotated[str, StringConstraints(max_length=2048)]
    icon_url: str | None = None
    proxy_icon_url: str | None = None


class EmbedMedia(BaseModel):
    """Image or thumbnail in a Discord embed."""

    url: str | None = None
    proxy_url: str | None = None
    height: int | None = None
    width: int | None = None


class EmbedVideo(BaseModel):
    """Video in a Discord embed."""

    url: str | None = None
    height: int | None = None
    width: int | None = None


class EmbedProvider(BaseModel):
    """Provider in a Discord embed."""

    name: str | None = None
    url: str | None = None


class EmbedAuthor(BaseModel):
    """Author section of a Discord embed."""

    name: Annotated[str, StringConstraints(max_length=256)] = ""
    url: str | None = None
    icon_url: str | None = None
    proxy_icon_url: str | None = None


class TanjunEmbed(BaseModel):
    """Represents a Discord embed, backed by Pydantic for validation.

    This is a drop-in replacement for the old hand-written ``TanjunEmbed``
    class.  It exposes the same fluent-style builder methods (``set_footer``,
    ``add_field``, etc.) and the same ``to_dict()`` method used by
    ``discord.py``'s ``send(embed=...)``.

    Use ``to_discord_embed()`` to obtain a native ``discord.Embed`` when
    you need to pass the embed to API methods that expect one.

    .. container:: operations

        .. describe:: len(x)

            Returns the total size of the embed.
            Useful for checking if it's within the 6000 character limit.

        .. describe:: bool(b)

            Returns whether the embed has any data set.
    """

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        populate_by_name=True,
        validate_assignment=False,
        extra="forbid",
    )

    # Core embed fields (colour/color is stored in _colour via __init__)
    title: Annotated[str | None, StringConstraints(max_length=256)] = None
    description: Annotated[str | None, StringConstraints(max_length=4096)] = None
    url: str | None = None
    type: str = "rich"
    timestamp: datetime.datetime | None = None

    # Rich embed components
    fields: list[EmbedField] = Field(default_factory=list)
    footer: EmbedFooter | None = None
    image: EmbedMedia | None = None
    thumbnail: EmbedMedia | None = None
    video: EmbedVideo | None = None
    provider: EmbedProvider | None = None
    author: EmbedAuthor | None = None

    # Private: colour storage (accessed via .colour / .color property)
    _colour: int = 0xCB33F5

    def __init__(
        self,
        *,
        colour: int | discord.Colour | EmbedColor | None = None,
        color: int | discord.Colour | EmbedColor | None = None,
        **kwargs: Any,
    ):
        super().__init__(**kwargs)
        value = colour if colour is not None else color
        if isinstance(value, discord.Colour):
            self._colour = value.value
        elif isinstance(value, EmbedColor):
            self._colour = value.value
        elif isinstance(value, int):
            self._colour = value
        else:
            self._colour = 0xCB33F5

    # --- Public API (backward-compatible) ---

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> Self:
        """Create a ``TanjunEmbed`` from a dict in Discord's embed format."""
        kwargs: dict[str, Any] = {}
        for key in ("title", "type", "description", "url"):
            if key in data:
                kwargs[key] = str(data[key])

        if "color" in data:
            kwargs["colour"] = data["color"]
        if "timestamp" in data:
            kwargs["timestamp"] = discord.utils.parse_time(data["timestamp"])

        for attr, pydantic_cls in (
            ("thumbnail", EmbedMedia),
            ("video", EmbedVideo),
            ("provider", EmbedProvider),
            ("author", EmbedAuthor),
            ("image", EmbedMedia),
            ("footer", EmbedFooter),
        ):
            if attr in data:
                kwargs[attr] = pydantic_cls(**data[attr])

        if "fields" in data:
            kwargs["fields"] = [EmbedField(**f) for f in data["fields"]]

        return cls(**kwargs)

    def to_dict(self) -> dict:
        """Convert this embed to a dict in Discord's embed format."""
        result: dict[str, Any] = {}

        if self.title:
            result["title"] = self.title
        if self.description:
            result["description"] = self.description
        if self.url:
            result["url"] = self.url
        result["type"] = self.type
        result["color"] = self.colour

        if self.timestamp is not None:
            ts = self.timestamp
            if ts.tzinfo:
                result["timestamp"] = ts.astimezone(tz=datetime.UTC).isoformat()
            else:
                result["timestamp"] = ts.replace(tzinfo=datetime.UTC).isoformat()

        if self.footer is not None:
            result["footer"] = self.footer.model_dump(exclude_none=True)
        if self.image is not None:
            result["image"] = self.image.model_dump(exclude_none=True)
        if self.thumbnail is not None:
            result["thumbnail"] = self.thumbnail.model_dump(exclude_none=True)
        if self.video is not None:
            result["video"] = self.video.model_dump(exclude_none=True)
        if self.provider is not None:
            result["provider"] = self.provider.model_dump(exclude_none=True)
        if self.author is not None:
            result["author"] = self.author.model_dump(exclude_none=True)
        if self.fields:
            result["fields"] = [f.model_dump() for f in self.fields]

        return result

    def to_discord_embed(self) -> discord.Embed:
        """Convert to a native ``discord.Embed`` for use with Discord API methods."""
        embed = discord.Embed(
            title=self.title,
            description=self.description,
            url=self.url,
            colour=self.colour,
            timestamp=self.timestamp,
        )
        if self.footer is not None:
            embed.set_footer(text=self.footer.text, icon_url=self.footer.icon_url)
        if self.image is not None and self.image.url:
            embed.set_image(url=self.image.url)
        if self.thumbnail is not None and self.thumbnail.url:
            embed.set_thumbnail(url=self.thumbnail.url)
        if self.author is not None:
            embed.set_author(
                name=self.author.name,
                url=self.author.url,
                icon_url=self.author.icon_url,
            )
        for field in self.fields:
            embed.add_field(name=field.name, value=field.value, inline=field.inline)
        return embed

    def copy(
        self,
        *,
        include: AbstractSet[int] | AbstractSet[str] | Mapping[int, Any] | Mapping[str, Any] | None = None,
        exclude: AbstractSet[int] | AbstractSet[str] | Mapping[int, Any] | Mapping[str, Any] | None = None,
        update: dict[str, Any] | None = None,
        deep: bool = False,
    ) -> Self:
        """Return a shallow copy of the embed."""
        data = self.model_dump()
        data["colour"] = self._colour
        return self.__class__(**data)

    def __len__(self) -> int:
        total = len(self.title or "") + len(self.description or "")
        for field in self.fields:
            total += len(field.name) + len(field.value)
        if self.footer is not None:
            total += len(self.footer.text)
        if self.author is not None:
            total += len(self.author.name)
        return total

    def __bool__(self) -> bool:
        return any(
            (
                self.title,
                self.url,
                self.description,
                self.colour != 0xCB33F5,
                bool(self.fields),
                self.timestamp is not None,
                self.author is not None,
                self.thumbnail is not None,
                self.footer is not None,
                self.image is not None,
                self.provider is not None,
                self.video is not None,
            )
        )

    # --- colour / color property ---

    @property
    def colour(self) -> int:
        return self._colour

    @colour.setter
    def colour(self, value: int | discord.Colour | EmbedColor | None) -> None:  # type: ignore[assignment]
        if value is None:
            self._colour = EmbedColor.BRAND.value
        elif isinstance(value, (discord.Colour, EmbedColor)):
            self._colour = value.value if isinstance(value, EmbedColor) else value.value
        elif isinstance(value, int):
            self._colour = value
        else:
            raise TypeError(f"Expected discord.Colour, int, or None but received {value.__class__.__name__} instead.")

    @property
    def color(self) -> int:
        return self.colour

    @color.setter
    def color(self, value: int | discord.Colour | EmbedColor | None) -> None:
        self.colour = value  # type: ignore[assignment]

    # --- Fluent-style builder methods ---

    def set_footer(self, *, text: object | None = None, icon_url: object | None = None) -> Self:
        kwargs: dict[str, Any] = {}
        if text is not None:
            kwargs["text"] = str(text)
        if icon_url is not None:
            kwargs["icon_url"] = str(icon_url)
        self.footer = EmbedFooter(**kwargs) if kwargs else None
        return self

    def remove_footer(self) -> Self:
        self.footer = None
        return self

    def set_image(self, *, url: object | None) -> Self:
        if url is None:
            self.image = None
        else:
            self.image = EmbedMedia(url=str(url))
        return self

    def set_thumbnail(self, *, url: object | None) -> Self:
        if url is None:
            self.thumbnail = None
        else:
            self.thumbnail = EmbedMedia(url=str(url))
        return self

    def set_author(self, *, name: object, url: object | None = None, icon_url: object | None = None) -> Self:
        kwargs: dict[str, Any] = {"name": str(name)}
        if url is not None:
            kwargs["url"] = str(url)
        if icon_url is not None:
            kwargs["icon_url"] = str(icon_url)
        self.author = EmbedAuthor(**kwargs)
        return self

    def remove_author(self) -> Self:
        self.author = None
        return self

    def add_field(self, *, name: object, value: object, inline: bool | object = True) -> Self:
        self.fields.append(EmbedField(name=str(name), value=str(value), inline=bool(inline)))
        return self

    def insert_field_at(self, index: int, *, name: object, value: object, inline: bool | object = True) -> Self:
        self.fields.insert(
            index,
            EmbedField(name=str(name), value=str(value), inline=bool(inline)),
        )
        return self

    def clear_fields(self) -> Self:
        self.fields.clear()
        return self

    def remove_field(self, index: int) -> Self:
        if 0 <= index < len(self.fields):
            self.fields.pop(index)
        return self

    def set_field_at(self, index: int, *, name: object, value: object, inline: bool | object = True) -> Self:
        if index < 0 or index >= len(self.fields):
            raise IndexError("field index out of range")
        self.fields[index] = EmbedField(name=str(name), value=str(value), inline=bool(inline))
        return self


# ========================================================================
# Embed builder helpers
# ========================================================================
#
# The original utility.py had both "categorized" embeds (accepting a
# ErrorEmbedCategory enum) and "simple" embeds (accepting a description
# string and optional title).
#
# We expose both:
#
#   - categorized_error_embed(category, title, description)
#   - categorized_success_embed(title, description)
#   - categorized_warning_embed(title, description)
#
# and (default / simpler):
#
#   - error_embed(description, title="Error")
#   - success_embed(description, title="Success")
#   - warning_embed(description, title="Warning")
# ========================================================================


# --- Categorized embed builders (original signature) ---


def categorized_error_embed(
    category: ErrorEmbedCategory,
    title: str,
    description: str,
) -> TanjunEmbed:
    """Build a standardized error embed with proper color for the given category."""
    return TanjunEmbed(
        colour=category.value,
        title=title,
        description=description,
    )


def categorized_success_embed(
    title: str,
    description: str,
) -> TanjunEmbed:
    """Build a standardized success embed."""
    return TanjunEmbed(
        colour=EmbedColor.SUCCESS,
        title=title,
        description=description,
    )


def categorized_warning_embed(
    title: str,
    description: str,
) -> TanjunEmbed:
    """Build a standardized warning embed."""
    return TanjunEmbed(
        colour=EmbedColor.WARNING,
        title=title,
        description=description,
    )


def categorized_info_embed(
    title: str,
    description: str,
) -> TanjunEmbed:
    """Build a standardized info embed."""
    return TanjunEmbed(
        colour=EmbedColor.INFO,
        title=title,
        description=description,
    )


# --- Simple embed builders (default; used by most of the codebase) ---


def embed_or_wrap(
    text: str,
    title: str | None = None,
    colour: int | discord.Colour | EmbedColor | None = None,
) -> TanjunEmbed:
    """Wrap a plain-text message in a standard embed.

    Use this when migrating plain ``ctx.send(content=...)`` or
    ``channel.send(content=...)`` calls to embeds.
    """
    if colour is None:
        colour = EmbedColor.BRAND
    return TanjunEmbed(title=title, description=text, colour=colour)


def error_embed(
    description: str,
    title: str | None = None,
) -> TanjunEmbed:
    """Create a standardised error embed with red colouring.

    This is the simple version used by most of the codebase.
    For the category-based version, see :func:`categorized_error_embed`.
    """
    if title is None:
        title = "Error"
    return TanjunEmbed(title=title, description=description, colour=EmbedColor.ERROR)


def success_embed(
    description: str,
    title: str | None = None,
) -> TanjunEmbed:
    """Create a standardised success embed with green colouring.

    This is the simple version used by most of the codebase.
    For the category-based version, see :func:`categorized_success_embed`.
    """
    if title is None:
        title = "Success"
    return TanjunEmbed(title=title, description=description, colour=EmbedColor.SUCCESS)


def warning_embed(
    description: str,
    title: str | None = None,
) -> TanjunEmbed:
    """Create a standardised warning embed with yellow colouring.

    This is the simple version used by most of the codebase.
    For the category-based version, see :func:`categorized_warning_embed`.
    """
    if title is None:
        title = "Warning"
    return TanjunEmbed(title=title, description=description, colour=EmbedColor.WARNING)


def info_embed(
    description: str,
    title: str | None = None,
) -> TanjunEmbed:
    """Create a standardised info embed with blue colouring.

    This is the simple version used by most of the codebase.
    For the category-based version, see :func:`categorized_info_embed`.
    """
    if title is None:
        title = "Info"
    return TanjunEmbed(title=title, description=description, colour=EmbedColor.INFO)


# Backward-compatible alias
tanjunEmbed = TanjunEmbed  # noqa: N816
