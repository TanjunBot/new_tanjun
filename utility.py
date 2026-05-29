import ast
import asyncio
import bisect
import collections
import concurrent.futures
import datetime
import enum
import gzip
import logging
import math
import operator as op
import random
import re

# Import Callable and Coroutine from typing
from collections.abc import Callable, Coroutine, Mapping
from difflib import SequenceMatcher
from typing import Annotated, Any, Self, TypeVar

import aiohttp
import discord
from aiohttp import ClientTimeout
from github import Github
from pydantic import BaseModel, ConfigDict, Field, StringConstraints
from pyparsing import (
    CaselessLiteral,
    Combine,
    Forward,
    Literal,
    Word,
    ZeroOrMore,
    alphas,
    nums,
)
from pyparsing import (
    Optional as Opt,
)

from config import (
    GithubAuthToken,
    ImgBBApiKey,
    bytebin_password,
    bytebin_url,
    bytebin_username,
    giphyAPIKey,
)
from utils.async_io import run_blocking


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


# Map of friendly keys to guild emoji names (from issue #1332).
# Maps friendly keys to the actual guild emoji names used in the Discord server.
EMOJI_MAP: dict[str, str] = {
    "checkmark": "check",
    "cross": "cross",
    "loading": "loading",
    "info": "info",
}


async def get_icon_emoji(
    bot: discord.Client | discord.ext.commands.Bot,
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

    Parameters
    ----------
    bot:
        The bot client (used to look up ``bot.emojis``).
    emoji_name:
        The friendly key to look up (e.g. ``"checkmark"``), or a direct emoji name.
    fallback:
        Unicode fallback when the guild emoji isn't available.
        ``None`` means ``StatusIcon.INFO.value``.

    Returns
    -------
    str:
        A string safe for use in embed titles, field values, or
        message content.
    """
    # Look up the emoji name from the map, falling back to using the key directly
    actual_emoji_name = EMOJI_MAP.get(emoji_name, emoji_name)

    if emoji := discord.utils.get(bot.emojis, name=actual_emoji_name):
        return str(emoji)
    if fallback is not None:
        return fallback
    return StatusIcon.INFO.value


T = TypeVar("T")

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
        # Let Pydantic populate the declared fields via super().__init__
        super().__init__(**kwargs)
        self.colour = colour if colour is not None else color

    # --- Public API (backward-compatible with old TanjunEmbed) ---

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> Self:
        """Create a ``TanjunEmbed`` from a dict in Discord's embed format.

        Parameters
        -----------
        data: :class:`dict`
            The dictionary to convert into an embed.
        """
        kwargs: dict[str, Any] = {}
        for key in ("title", "type", "description", "url"):
            if key in data:
                kwargs[key] = str(data[key])

        if "color" in data:
            kwargs["colour"] = data["color"]
        if "timestamp" in data:
            kwargs["timestamp"] = discord.utils.parse_time(data["timestamp"])

        # Rich embed components
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

    def copy(self) -> Self:
        """Return a shallow copy of the embed."""
        return self.__class__(**self.model_dump())

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

    # --- colour / color property for backward compat ---

    @property
    def colour(self) -> int:
        return self._colour

    @colour.setter
    def colour(self, value: int | discord.Colour | EmbedColor | None) -> None:
        if value is None:
            self._colour = EmbedColor.BRAND.value
        elif isinstance(value, (discord.Colour, EmbedColor)):
            self._colour = value.value if isinstance(value, EmbedColor) else value.value
        elif isinstance(value, int):
            self._colour = value
        else:
            raise TypeError(
                f"Expected discord.Colour, int, or None but received {value.__class__.__name__} instead."
            )

    @property
    def color(self) -> int:
        return self.colour

    @color.setter
    def color(self, value: int | discord.Colour | EmbedColor | None) -> None:
        self.colour = value

    # --- Fluent-style builder methods ---

    def set_footer(self, *, text: object | None = None, icon_url: object | None = None) -> Self:
        """Set the footer for the embed content."""
        kwargs: dict[str, Any] = {}
        if text is not None:
            kwargs["text"] = str(text)
        if icon_url is not None:
            kwargs["icon_url"] = str(icon_url)
        self.footer = EmbedFooter(**kwargs) if kwargs else None
        return self

    def remove_footer(self) -> Self:
        """Clear embed's footer information."""
        self.footer = None
        return self

    def set_image(self, *, url: Any | None) -> Self:
        """Set the image for the embed content."""
        if url is None:
            self.image = None
        else:
            self.image = EmbedMedia(url=str(url))
        return self

    def set_thumbnail(self, *, url: Any | None) -> Self:
        """Set the thumbnail for the embed content."""
        if url is None:
            self.thumbnail = None
        else:
            self.thumbnail = EmbedMedia(url=str(url))
        return self

    def set_author(self, *, name: Any, url: Any | None = None, icon_url: Any | None = None) -> Self:
        """Set the author for the embed content."""
        kwargs: dict[str, Any] = {"name": str(name)}
        if url is not None:
            kwargs["url"] = str(url)
        if icon_url is not None:
            kwargs["icon_url"] = str(icon_url)
        self.author = EmbedAuthor(**kwargs)
        return self

    def remove_author(self) -> Self:
        """Clear embed's author information."""
        self.author = None
        return self

    def add_field(self, *, name: Any, value: Any, inline: bool | Any = True) -> Self:
        """Add a field to the embed object."""
        self.fields.append(
            EmbedField(name=str(name), value=str(value), inline=bool(inline))
        )
        return self

    def insert_field_at(self, index: int, *, name: Any, value: Any, inline: bool | Any = True) -> Self:
        """Insert a field before a specified index."""
        self.fields.insert(
            index,
            EmbedField(name=str(name), value=str(value), inline=bool(inline)),
        )
        return self

    def clear_fields(self) -> Self:
        """Remove all fields from this embed."""
        self.fields.clear()
        return self

    def remove_field(self, index: int) -> Self:
        """Remove a field at a specified index."""
        if 0 <= index < len(self.fields):
            self.fields.pop(index)
        return self

    def set_field_at(self, index: int, *, name: Any, value: Any, inline: bool | Any = True) -> Self:
        """Modify a field at the specified index."""
        if index < 0 or index >= len(self.fields):
            raise IndexError("field index out of range")
        self.fields[index] = EmbedField(name=str(name), value=str(value), inline=bool(inline))
        return self


class CommandInfo:
    def __init__(
        self,
        user: discord.abc.User,
        channel: discord.abc.GuildChannel,
        guild: discord.Guild,
        command: discord.app_commands.Command,
        locale: str,
        message: discord.Message,
        permissions: discord.Permissions,
        reply: Callable[..., Coroutine[Any, Any, Any]],
        client: discord.Client,
    ):
        self.user = user
        self.channel = channel
        self.guild = guild
        self.command = command
        self.locale = locale
        self.message = message
        self.permissions = permissions
        self.reply = reply
        self.client = client


command_info = CommandInfo


def cmp(a: int, b: int) -> int:
    return (a > b) - (a < b)


class NumericStringParser:
    """
    Most of this code comes from the fourFn.py pyparsing example

    """

    def pushFirst(self, strg, loc, toks) -> None:
        self.exprStack.append(toks[0])

    def pushUMinus(self, strg, loc, toks):
        if toks and toks[0] == "-":
            self.exprStack.append("unary -")

    def __init__(self):
        point = Literal(".")
        e = CaselessLiteral("E")
        fnumber = Combine(Word("+-" + nums, nums) + Opt(point + Opt(Word(nums))) + Opt(e + Word("+-" + nums, nums)))
        ident = Word(alphas, alphas + nums + "_$")

        plus, minus, mult, div = map(Literal, "+-*/")
        lpar, rpar = map(Literal, "()")
        addop = plus | minus
        multop = mult | div
        expop = Literal("^")

        expr = Forward()
        atom = (Opt("-") + (ident + lpar + expr + rpar | fnumber)).setParseAction(self.pushFirst) | (
            lpar + expr.suppress() + rpar
        ).setParseAction(self.pushUMinus)

        factor = Forward()
        factor << atom + ZeroOrMore((expop + factor).setParseAction(self.pushFirst))

        term = factor + ZeroOrMore((multop + factor).setParseAction(self.pushFirst))
        expr << term + ZeroOrMore((addop + term).setParseAction(self.pushFirst))

        self.bnf = expr
        self.exprStack = []

        # Function map
        self.fn = {
            "sin": math.sin,
            "cos": math.cos,
            "tan": math.tan,
            "asin": math.asin,
            "acos": math.acos,
            "atan": math.atan,
            "sinh": math.sinh,
            "cosh": math.cosh,
            "tanh": math.tanh,
            "asinh": math.asinh,
            "acosh": math.acosh,
            "atanh": math.atanh,
            "log": math.log,
            "log10": math.log10,
            "log2": math.log2,
            "exp": math.exp,
            "abs": abs,
            "trunc": math.trunc,
            "round": round,
            "sgn": lambda a: abs(a) > 1e-12 and cmp(a, 0) or 0,
            "sqrt": math.sqrt,
            "factorial": math.factorial,
            "degrees": math.degrees,
            "radians": math.radians,
            "ceil": math.ceil,
            "floor": math.floor,
            "pi": math.pi,
            "e": math.e,
            "fac": math.factorial,
        }

        # Operator map
        self.opn = {
            "+": op.add,
            "-": op.sub,
            "*": op.mul,
            "/": op.truediv,
            "^": op.pow,
        }

    def evaluateStack(self, s):
        op = s.pop()
        if op == "unary -":
            return -self.evaluateStack(s)
        if op in "+-*/^":
            op2 = self.evaluateStack(s)
            op1 = self.evaluateStack(s)
            return self.opn[op](op1, op2)
        elif op == "PI":
            return math.pi
        elif op == "E":
            return math.e
        elif op in self.fn:
            return self.fn[op](self.evaluateStack(s))
        elif op[0].isalpha():
            raise Exception(f"Invalid identifier: {op}")
        else:
            return float(op)

    def eval(self, num_string, parseAll=True):
        self.exprStack = []
        self.bnf.parseString(num_string, parseAll)
        val = self.evaluateStack(self.exprStack[:])
        return val


async def getGif(query: str, amount: int = 1, limit: int = 10) -> list[str]:
    try:
        async with aiohttp.ClientSession(timeout=ClientTimeout(total=10)) as session:

            async def fetch(url: str) -> dict | None:
                async with session.get(url) as response:
                    if response.status != 200:
                        return None
                    return await response.json()

            r = await fetch(
                f"https://api.giphy.com/v1/gifs/search?api_key={giphyAPIKey}&q={query}&limit={limit}&rating=pg"
            )

            if r is None:
                return []
            results = r.get("data", [])
            # nosec: B311
            random.shuffle(results)

            return [results[i]["images"]["downsized_medium"]["url"] for i in range(min(amount, len(results)))]
    except (TimeoutError, aiohttp.ClientError):
        return []


async def missingLocalization(locale: str) -> None:
    """Create a GitHub issue reporting a missing localization."""
    await run_blocking(_sync_create_missing_localization_issue, locale)


def _sync_create_missing_localization_issue(locale: str) -> None:
    g = Github(GithubAuthToken)
    repo = g.get_repo("TanjunBot/new_tanjun")
    label = repo.get_label("missing localization")
    repo.create_issue(
        title="Missing localization",
        body=f"Missing localization for {locale}",
        labels=[label],
    )


async def addFeedback(content: str, author: str) -> None:
    """Create a GitHub issue with user feedback."""
    await run_blocking(_sync_create_feedback_issue, content, author)


def _sync_create_feedback_issue(content: str, author: str) -> None:
    g = Github(GithubAuthToken)
    repo = g.get_repo("TanjunBot/new_tanjun")
    label = repo.get_label("Feedback")
    repo.create_issue(
        title="Feedback",
        body=f"# {author} has given Feedback:\n{content}",
        labels=[label],
    )


LEVEL_SCALINGS = {
    "easy": lambda level: 100 * level,
    "medium": lambda level: 100 * (level**1.5),
    "hard": lambda level: 100 * (level**2),
    "extreme": lambda level: 100 * (level**2.5),
}

# Inverse formulas for built-in scalings: O(1) lookups instead of O(log n) threshold scans.
# Each maps scaling name to a callable that computes level from xp.
_LEVEL_INVERSES: dict[str, Callable[[int], int]] = {
    "easy": lambda xp: xp // 100,
    "medium": lambda xp: int((xp / 100) ** (1 / 1.5)),
    "hard": lambda xp: int(math.sqrt(xp / 100)),
    "extreme": lambda xp: int((xp / 100) ** (1 / 2.5)),
}


def _invert_get_level_for_xp(xp: int, scaling: str) -> int:
    """Compute level directly via mathematical inverse of the standard scaling formula.

    This is O(1) — no iteration, no threshold list building.
    """
    # Guard against non-positive xp to prevent complex number results from power operations
    if xp <= 0:
        return 0
    level = _LEVEL_INVERSES.get(scaling, lambda _: 0)(xp)
    # Clamp to valid range: level must be >= 0 and the inverse may overshoot
    # the exact threshold boundary, so verify and step down/up if needed.
    if level < 0:
        return 0
    # Verify: ensure get_xp_for_level(level) <= xp < get_xp_for_level(level + 1)
    while get_xp_for_level(level + 1, scaling) <= xp and level < 10000:
        level += 1
    while level > 0 and get_xp_for_level(level, scaling) > xp:
        level -= 1
    return level


class LevelThresholdCache:
    """Pre-compute and cache level XP thresholds per (scaling, custom_formula) pair.

    For built-in scalings (easy/medium/hard/extreme) we use O(1) mathematical
    inversion. For custom formulas, we use binary search (O(log n)).
    The cache is only used for custom formulas.
    """

    _thresholds: collections.OrderedDict[tuple[str, str | None], tuple[list[int], int]] = collections.OrderedDict()
    _MAX_LEVEL = 10000
    _MAX_ENTRIES = 50  # Prevent unbounded growth: ~50 scaling/formula combos max
    _lock: asyncio.Lock = asyncio.Lock()

    @classmethod
    def get_level_for_xp(cls, xp: int, scaling: str, custom_formula: str | None = None) -> int:
        # Use O(1) mathematical inversion for known built-in scalings
        if scaling != "custom":
            return _invert_get_level_for_xp(xp, scaling)

        # Only custom formulas reach here: use binary search with threshold cache
        effective_formula = custom_formula
        key = (scaling, effective_formula)
        entry = cls._thresholds.get(key)
        thresholds: list[int] | None
        max_level: int
        if entry is not None:
            thresholds, max_level = entry
        else:
            thresholds = None
            max_level = cls._MAX_LEVEL

        if thresholds is None or thresholds[-1] < xp:
            # Build or extend thresholds if needed
            if thresholds is None:
                start_level = 1
                thresholds = []
                max_level = cls._MAX_LEVEL
            else:
                # Extend from current; don't rebuild from scratch
                if max_level >= cls._MAX_LEVEL and thresholds[-1] >= xp:
                    return bisect.bisect_right(thresholds, xp)
                start_level = len(thresholds) + 1
                max_level = cls._MAX_LEVEL
            for level in range(start_level, max_level + 1):
                thresholds.append(get_xp_for_level(level, scaling, effective_formula))
                if thresholds[-1] > xp and level >= start_level + 10:
                    max_level = level
                    break
            cls._thresholds[key] = (thresholds, max_level)
            # Evict oldest entries if cache exceeds limit
            while len(cls._thresholds) > cls._MAX_ENTRIES:
                cls._thresholds.popitem(last=False)
        return bisect.bisect_right(thresholds, xp)

    @classmethod
    async def get_level_for_xp_async(cls, xp: int, scaling: str, custom_formula: str | None = None) -> int:
        """Async version that runs CPU-bound formula evaluation in a thread executor.

        Only used for custom formulas (built-in scalings use the fast O(1) sync path).
        """
        # Only custom formulas reach here
        effective_formula = custom_formula
        key = (scaling, effective_formula)
        entry = cls._thresholds.get(key)
        thresholds: list[int] | None
        max_level: int
        if entry is not None:
            thresholds, max_level = entry
        else:
            thresholds = None
            max_level = cls._MAX_LEVEL

        if thresholds is None or thresholds[-1] < xp:
            # Build or extend thresholds if needed
            async with cls._lock:
                # Re-check after acquiring lock (another coroutine may have built it)
                entry = cls._thresholds.get(key)
                if entry is not None:
                    thresholds, max_level = entry
                    if thresholds is not None and thresholds[-1] >= xp:
                        return bisect.bisect_right(thresholds, xp)

                # Use local list to avoid mutating shared state during await
                if thresholds is None:
                    start_level = 1
                    new_thresholds = []
                    max_level = cls._MAX_LEVEL
                else:
                    # Extend from current; don't rebuild from scratch
                    if max_level >= cls._MAX_LEVEL and thresholds[-1] >= xp:
                        return bisect.bisect_right(thresholds, xp)
                    start_level = len(thresholds) + 1
                    new_thresholds = thresholds.copy()
                    max_level = cls._MAX_LEVEL
                for level in range(start_level, max_level + 1):
                    xp_needed = await get_xp_for_level_async(level, scaling, effective_formula)
                    new_thresholds.append(xp_needed)
                    if new_thresholds[-1] > xp and level >= start_level + 10:
                        max_level = level
                        break
                # Atomic assignment to shared cache
                cls._thresholds[key] = (new_thresholds, max_level)
                # Evict oldest entries if cache exceeds limit
                while len(cls._thresholds) > cls._MAX_ENTRIES:
                    cls._thresholds.popitem(last=False)
                thresholds = new_thresholds
        return bisect.bisect_right(thresholds, xp)


operators = {
    ast.Add: op.add,
    ast.Sub: op.sub,
    ast.Mult: op.mul,
    ast.Div: op.truediv,
    ast.Pow: op.pow,
    ast.BitXor: op.xor,
    ast.USub: op.neg,
    ast.Mod: op.mod,
}


def sqrt_n(x: float, n: float = 2) -> float:
    return x ** (1 / n)


def log_n(x: float, base: float = math.e) -> float:
    return math.log(x, base)


# Thread pool executor for CPU-bound formula evaluation
_eval_executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)


async def eval_expr_async(expr: str, variables=None) -> float:
    """Async version of eval_expr that runs the CPU-bound AST evaluation in a thread executor."""
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(_eval_executor, eval_expr, expr, variables)


def eval_expr(expr: str, variables=None) -> float:
    if variables is None:
        variables = {}

    # Replace mathematical constants
    expr = expr.replace("pi", str(math.pi))
    expr = expr.replace("e", str(math.e))

    # Handle special functions with base notation
    expr = re.sub(r"log\[(\d+)\]\((.*?)\)", r"log_n(\2,\1)", expr)

    # Handle special functions
    expr = re.sub(r"sqrt\[(\d+)\]\((.*?)\)", r"sqrt_n(\2,\1)", expr)
    expr = re.sub(r"sqrt\((.*?)\)", r"sqrt_n(\1)", expr)
    expr = re.sub(r"nthroot\[(\d+)\]\((.*?)\)", r"sqrt_n(\2,\1)", expr)

    # Handle logarithms
    expr = re.sub(r"log2\((.*?)\)", r"log_n(\1,2)", expr)
    expr = re.sub(r"log10\((.*?)\)", r"log_n(\1,10)", expr)
    expr = re.sub(r"ln\((.*?)\)", r"log_n(\1)", expr)

    # Handle trigonometric functions
    expr = re.sub(r"sin\((.*?)\)", r"math.sin(\1)", expr)
    expr = re.sub(r"cos\((.*?)\)", r"math.cos(\1)", expr)
    expr = re.sub(r"tan\((.*?)\)", r"math.tan(\1)", expr)
    expr = re.sub(r"asin\((.*?)\)", r"math.asin(\1)", expr)
    expr = re.sub(r"acos\((.*?)\)", r"math.acos(\1)", expr)
    expr = re.sub(r"atan\((.*?)\)", r"math.atan(\1)", expr)

    # Handle floor and ceiling
    expr = re.sub(r"floor\((.*?)\)", r"math.floor(\1)", expr)
    expr = re.sub(r"ceil\((.*?)\)", r"math.ceil(\1)", expr)

    # Handle absolute value
    expr = re.sub(r"abs\((.*?)\)", r"abs(\1)", expr)

    return eval_(ast.parse(expr, mode="eval").body, variables)


def eval_(node, variables):
    if isinstance(node, ast.Constant):
        return node.value
    elif isinstance(node, ast.BinOp):
        return operators[type(node.op)](eval_(node.left, variables), eval_(node.right, variables))
    elif isinstance(node, ast.UnaryOp):
        return operators[type(node.op)](eval_(node.operand, variables))
    elif isinstance(node, ast.Call):
        if isinstance(node.func, ast.Attribute):
            if node.func.value.id == "math":
                func = getattr(math, node.func.attr)
                args = [eval_(arg, variables) for arg in node.args]
                return func(*args)
        elif isinstance(node.func, ast.Name):
            if node.func.id == "sqrt_n":
                args = [eval_(arg, variables) for arg in node.args]
                return sqrt_n(*args)
            elif node.func.id == "log_n":
                args = [eval_(arg, variables) for arg in node.args]
                return log_n(*args)
            elif node.func.id == "abs":
                args = [eval_(arg, variables) for arg in node.args]
                return abs(*args)
        raise TypeError(f"Unsupported function call: {node.func}")
    elif isinstance(node, ast.Name):
        if node.id in variables:
            return variables[node.id]
        raise NameError(f"Variable '{node.id}' is not defined")
    else:
        raise TypeError(f"Unsupported operation: {node}")


def get_xp_for_level(level: int, scaling: str, custom_formula: str | None = None) -> int:
    if level <= 0:
        return 0
    if scaling == "custom" and custom_formula:
        try:
            result = eval_expr(custom_formula.replace("level", str(level)))
        except Exception:
            return 0  # Return 0 if there's an error in the custom formula
    else:
        result = LEVEL_SCALINGS.get(scaling, LEVEL_SCALINGS["medium"])(level)
    if isinstance(result, complex):
        return 0  # Optionally handle or raise an error for complex results
    return math.floor(result)


async def get_xp_for_level_async(level: int, scaling: str, custom_formula: str | None = None) -> int:
    """Async version of get_xp_for_level that runs CPU-bound formula evaluation in a thread executor."""
    if level <= 0:
        return 0
    if scaling == "custom" and custom_formula:
        try:
            result = await eval_expr_async(custom_formula.replace("level", str(level)))
        except Exception:
            return 0
    else:
        result = LEVEL_SCALINGS.get(scaling, LEVEL_SCALINGS["medium"])(level)
    if isinstance(result, complex):
        return 0
    return math.floor(result)


def get_level_for_xp(xp: int, scaling: str, custom_formula: str | None = None) -> int:
    """Get the level for a given XP value.

    For built-in scalings (easy/medium/hard/extreme) this uses O(1) mathematical
    inversion of the formula. For custom formulas, binary search is used.
    """
    return LevelThresholdCache.get_level_for_xp(xp, scaling, custom_formula)


async def get_level_for_xp_async(xp: int, scaling: str, custom_formula: str | None = None) -> int:
    """Async version of get_level_for_xp for custom formulas.

    For built-in scalings, delegates to the O(1) sync version.
    For custom formulas, uses the async eval to prevent event loop blocking.
    """
    if scaling != "custom":
        return get_level_for_xp(xp, scaling, custom_formula)
    return await LevelThresholdCache.get_level_for_xp_async(xp, scaling, custom_formula)


def relativeTimeStrToDate(time_string: str) -> datetime.datetime:
    if not time_string:
        return datetime.datetime.now()

    # Regular expression to match time units
    pattern = r"(\d+)([smhd])"
    matches = re.findall(pattern, time_string.lower())

    if not matches:
        return datetime.datetime.now()

    # Initialize timedelta components
    days = hours = minutes = seconds = 0

    for value, unit in matches:
        value = int(value)
        if unit == "s":
            seconds += value
        elif unit == "m":
            minutes += value
        elif unit == "h":
            hours += value
        elif unit == "d":
            days += value

    # Create timedelta and add to current time
    delta = datetime.timedelta(days=days, hours=hours, minutes=minutes, seconds=seconds)
    return datetime.datetime.now() + delta


def relativeTimeToSeconds(time_string: str) -> int:
    if not time_string:
        return 0

    # Regular expression to match time units
    pattern = r"(\d+)([smhd])"
    matches = re.findall(pattern, time_string.lower())

    if not matches:
        return 0

    # Initialize timedelta components
    days = hours = minutes = seconds = 0

    for value, unit in matches:
        value = int(value)
        if unit == "s":
            seconds += value
        elif unit == "m":
            minutes += value
        elif unit == "h":
            hours += value
        elif unit == "d":
            days += value

    # Create timedelta and add to current time
    delta = datetime.timedelta(days=days, hours=hours, minutes=minutes, seconds=seconds)
    return delta.total_seconds()


def dateToRelativeTimeStr(date: datetime.datetime) -> str:
    start_date = datetime.datetime.now()
    # Calculate the difference between the two dates
    delta = date - start_date

    # Extract days, seconds from delta
    days = delta.days
    seconds = delta.seconds

    # Calculate hours, minutes and the remaining seconds
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60

    # Create a list to hold each component that is non-zero
    components = []
    if days:
        components.append(f"{days}d")
    if hours:
        components.append(f"{hours}h")
    if minutes:
        components.append(f"{minutes}m")
    if seconds:
        components.append(f"{seconds}s")

    # Join all non-zero components with spaces
    return " ".join(components)


def date_time_to_timestamp(date: datetime.datetime) -> int:
    return int(date.timestamp())


async def upload_image_to_imgbb(image_bytes: bytes, file_extension: str) -> dict:
    async with aiohttp.ClientSession(timeout=ClientTimeout(total=30)) as session:
        form_data = aiohttp.FormData()
        form_data.add_field("key", ImgBBApiKey)
        form_data.add_field("image", image_bytes, filename=f"upload.{file_extension}")
        form_data.add_field("name", "tbg")

        async with session.post("https://api.imgbb.com/1/upload", data=form_data) as response:
            response_data = await response.json()

    return response_data


async def upload_to_tanjun_logs(content: str) -> str:
    compressed_content = gzip.compress(content.encode("utf-8"))
    url = bytebin_url
    username = bytebin_username
    password = bytebin_password

    async with aiohttp.ClientSession(timeout=ClientTimeout(total=10)) as session:
        auth = aiohttp.BasicAuth(username, password)
        headers = {"Content-Type": "text/html", "Content-Encoding": "gzip"}

        async with session.post(url + "/post", data=compressed_content, headers=headers, auth=auth) as response:
            if response.status == 201:
                response_data = await response.json()
                if "key" in response_data:
                    return f"{bytebin_url}/{response_data['key']}"
                else:
                    print("Unexpected response format:", response_data)
                    return None
            else:
                print(f"Request failed with status {response.status}: {await response.text()}")
                return None


def check_if_str_is_hex_color(color: str) -> bool:
    try:
        int(color, 16)
        return True
    except ValueError:
        return False


def draw_text_with_outline(draw, position, text, font, text_color, outline_color):
    x, y = position
    # Draw outline
    draw.text((x - 1, y - 1), text, font=font, fill=outline_color)
    draw.text((x + 1, y - 1), text, font=font, fill=outline_color)
    draw.text((x - 1, y + 1), text, font=font, fill=outline_color)
    draw.text((x + 1, y + 1), text, font=font, fill=outline_color)
    # Draw text
    draw.text(position, text, font=font, fill=text_color)


def isoTimeToDate(isoTime: str) -> datetime.datetime:
    return datetime.datetime.fromisoformat(isoTime)


def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()


def addThousandsSeparator(number: int) -> str:
    return f"{number:,}".replace(",", " ")


class SafeInteraction:
    """Helper for safely responding to Discord interactions, preventing double-respond errors.

    Use instead of ``interaction.response.send_message()``,
    ``interaction.response.defer()``, and ``interaction.edit_original_response()``
    to handle race conditions when ``interaction_check`` or other code paths
    may have already responded.

    Usage::

        embed = utility.tanjunEmbed(title="Done", description="Operation complete.")
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
        """Respond to an interaction, safely handling already-responded state.

        If the interaction has already been responded to, this falls back to
        ``interaction.followup.send()`` instead of raising.
        """
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
                pass  # Already responded, silently ignore

    @staticmethod
    async def edit(
        interaction: discord.Interaction,
        embed: discord.Embed | None = None,
        content: str | None = None,
        view: discord.ui.View | None = None,
    ) -> None:
        """Safely edit the original interaction response.

        If the interaction has not yet been responded to, this sends an initial
        message instead of trying to edit a non-existent response.
        """
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


tanjunEmbed = TanjunEmbed
#: Backward-compatible alias so that ``from utility import tanjunEmbed`` still works.


class DiscordSafe:
    """Safely call Discord API methods with proper error handling.

    Wraps common Discord operations in try/except guards for Forbidden,
    NotFound, and HTTPException so that minigames and other features don't
    crash when permissions are revoked or network errors occur.
    """

    @staticmethod
    async def send(
        channel: discord.abc.Messageable,
        content: str | None = None,
        embed: discord.Embed | None = None,
    ) -> discord.Message | None:
        """Send a message, returning None if it fails."""
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
        """Send a DM, returning True on success."""
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
        """Delete a message, returning True if it was deleted or already gone."""
        try:
            await message.delete()
            return True
        except discord.NotFound:
            return True  # Already deleted
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
        """Reply to a message, returning None if it fails."""
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
        """Add a reaction, returning True on success."""
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
