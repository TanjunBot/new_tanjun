import ast
import asyncio
import bisect
import collections
import concurrent.futures
import contextlib
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
from typing import Any, Protocol, Self, TypeVar

from pydantic import BaseModel, ConfigDict

import aiohttp
import discord
from aiohttp import ClientTimeout
from github import Github
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


class EmbedProxy:
    def __init__(self, layer: dict[str, Any]):
        self.__dict__.update(layer)

    def __len__(self) -> int:
        return len(self.__dict__)

    def __repr__(self) -> str:
        inner = ", ".join((f"{k}={v!r}" for k, v in self.__dict__.items() if not k.startswith("_")))
        return f"EmbedProxy({inner})"

    def __getattr__(self, attr: str) -> None:
        return None

    def __eq__(self, other: object) -> bool:
        return isinstance(other, EmbedProxy) and self.__dict__ == other.__dict__


T = TypeVar("T")


class _EmbedFooterProxy(Protocol):
    text: str | None
    icon_url: str | None


class _EmbedFieldProxy(Protocol):
    name: str | None
    value: str | None
    inline: bool


class _EmbedMediaProxy(Protocol):
    url: str | None
    proxy_url: str | None
    height: int | None
    width: int | None


class _EmbedVideoProxy(Protocol):
    url: str | None
    height: int | None
    width: int | None


class _EmbedProviderProxy(Protocol):
    name: str | None
    url: str | None


class _EmbedAuthorProxy(Protocol):
    name: str | None
    url: str | None
    icon_url: str | None
    proxy_icon_url: str | None


class TanjunEmbed:
    """Represents a Discord embed.

    .. container:: operations

        .. describe:: len(x)

            Returns the total size of the embed.
            Useful for checking if it's within the 6000 character limit.

        .. describe:: bool(b)

            Returns whether the embed has any data set.

            .. versionadded:: 2.0

        .. describe:: x == y

            Checks if two embeds are equal.

            .. versionadded:: 2.0

    For ease of use, all parameters that expect a :class:`str` are implicitly
    casted to :class:`str` for you.

    .. versionchanged:: 2.0
        ``Embed.Empty`` has been removed in favour of ``None``.

    Attributes
    -----------
    title: Optional[:class:`str`]
        The title of the embed.
        This can be set during initialisation.
        Can only be up to 256 characters.
    type: :class:`str`
        The type of embed. Usually "rich".
        This can be set during initialisation.
        Possible strings for embed types can be found on discord's
        :ddocs:`api docs <resources/channel#embed-object-embed-types>`
    description: Optional[:class:`str`]
        The description of the embed.
        This can be set during initialisation.
        Can only be up to 4096 characters.
    url: Optional[:class:`str`]
        The URL of the embed.
        This can be set during initialisation.
    timestamp: Optional[:class:`datetime.datetime`]
        The timestamp of the embed content. This is an aware datetime.
        If a naive datetime is passed, it is converted to an aware
        datetime with the local timezone.
    colour: Optional[Union[:class:`Colour`, :class:`int`]]
        The colour code of the embed. Aliased to ``color`` as well.
        This can be set during initialisation.
    """

    __slots__ = (
        "title",
        "url",
        "type",
        "_timestamp",
        "_colour",
        "_footer",
        "_image",
        "_thumbnail",
        "_video",
        "_provider",
        "_author",
        "_fields",
        "description",
    )

    def __init__(
        self,
        *,
        colour: int | discord.Colour | EmbedColor | None = None,
        color: int | discord.Colour | EmbedColor | None = None,
        title: Any | None = None,
        type="rich",
        url: Any | None = None,
        description: Any | None = None,
        timestamp: datetime.datetime | None = None,
    ):
        self.colour = colour if colour is not None else color
        if self.colour is None:
            self.colour = EmbedColor.BRAND
        self.title: str | None = title
        self.type = type
        self.url: str | None = url
        self.description: str | None = description

        if self.title is not None:
            self.title = str(self.title)

        if self.description is not None:
            self.description = str(self.description)

        if self.url is not None:
            self.url = str(self.url)

        if timestamp is not None:
            self.timestamp = timestamp

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> Self:
        """Converts a :class:`dict` to a :class:`Embed` provided it is in the
        format that Discord expects it to be in.

        You can find out about this format in the :ddocs:`official Discord documentation <resources/channel#embed-object>`.

        Parameters
        -----------
        data: :class:`dict`
            The dictionary to convert into an embed.
        """
        # we are bypassing __init__ here since it doesn't apply here
        self = cls.__new__(cls)

        # fill in the basic fields

        self.title = data.get("title", None)
        self.type = data.get("type", None)
        self.description = data.get("description", None)
        self.url = data.get("url", None)

        if self.title is not None:
            self.title = str(self.title)

        if self.description is not None:
            self.description = str(self.description)

        if self.url is not None:
            self.url = str(self.url)

        # try to fill in the more rich fields

        with contextlib.suppress(KeyError):
            self._colour = discord.Colour(value=data["color"])

        with contextlib.suppress(KeyError):
            self._timestamp = discord.utils.parse_time(data["timestamp"])

        for attr in (
            "thumbnail",
            "video",
            "provider",
            "author",
            "fields",
            "image",
            "footer",
        ):
            try:
                value = data[attr]
            except KeyError:
                continue
            else:
                setattr(self, "_" + attr, value)

        return self

    def copy(self) -> Self:
        """Returns a shallow copy of the embed."""
        return self.__class__.from_dict(self.to_dict())

    def __len__(self) -> int:
        total = len(self.title or "") + len(self.description or "")
        for field in getattr(self, "_fields", []):
            total += len(field["name"]) + len(field["value"])

        try:
            footer_text = self._footer["text"]
        except (AttributeError, KeyError):
            pass
        else:
            total += len(footer_text)

        try:
            author = self._author
        except AttributeError:
            pass
        else:
            total += len(author["name"])

        return total

    def __bool__(self) -> bool:
        return any(
            (
                self.title,
                self.url,
                self.description,
                self.colour,
                self.fields,
                self.timestamp,
                self.author,
                self.thumbnail,
                self.footer,
                self.image,
                self.provider,
                self.video,
            )
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, TanjunEmbed):
            return NotImplemented
        return (
            self.type == other.type
            and self.title == other.title
            and self.url == other.url
            and self.description == other.description
            and self.colour == other.colour
            and self.fields == other.fields
            and self.timestamp == other.timestamp
            and self.author == other.author
            and self.thumbnail == other.thumbnail
            and self.footer == other.footer
            and self.image == other.image
            and self.provider == other.provider
            and self.video == other.video
        )

    @property
    def colour(self) -> discord.Colour | None:
        return getattr(self, "_colour", None)

    @colour.setter
    def colour(self, value: int | discord.Colour | None) -> None:
        if value is None:
            self._colour = None
        elif isinstance(value, discord.Colour):
            self._colour = value
        elif isinstance(value, int):
            self._colour = discord.Colour(value=value)
        else:
            raise TypeError(f"Expected discord.Colour, int, or None but received {value.__class__.__name__} instead.")

    color = colour

    @property
    def timestamp(self) -> datetime.datetime | None:
        return getattr(self, "_timestamp", None)

    @timestamp.setter
    def timestamp(self, value: datetime.datetime | None) -> None:
        if isinstance(value, datetime.datetime):
            if value.tzinfo is None:
                value = value.astimezone()
            self._timestamp = value
        elif value is None:
            self._timestamp = None
        else:
            raise TypeError(f"Expected datetime.datetime or None received {value.__class__.__name__} instead")

    @property
    def footer(self) -> _EmbedFooterProxy:
        """Returns an ``EmbedProxy`` denoting the footer contents.

        See :meth:`set_footer` for possible values you can access.

        If the attribute has no value then ``None`` is returned.
        """
        # Lying to the type checker for better developer UX.
        return EmbedProxy(getattr(self, "_footer", {}))  # type: ignore

    def set_footer(self, *, text: Any | None = None, icon_url: Any | None = None) -> Self:
        """Sets the footer for the embed content.

        This function returns the class instance to allow for fluent-style
        chaining.

        Parameters
        -----------
        text: :class:`str`
            The footer text. Can only be up to 2048 characters.
        icon_url: :class:`str`
            The URL of the footer icon. Only HTTP(S) is supported.
            Inline attachment URLs are also supported, see :ref:`local_image`.
        """

        self._footer = {}
        if text is not None:
            self._footer["text"] = str(text)

        if icon_url is not None:
            self._footer["icon_url"] = str(icon_url)

        return self

    def remove_footer(self) -> Self:
        """Clears embed's footer information.

        This function returns the class instance to allow for fluent-style
        chaining.

        .. versionadded:: 2.0
        """
        with contextlib.suppress(AttributeError):
            del self._footer

        return self

    @property
    def image(self) -> _EmbedMediaProxy:
        """Returns an ``EmbedProxy`` denoting the image contents.

        Possible attributes you can access are:

        - ``url``
        - ``proxy_url``
        - ``width``
        - ``height``

        If the attribute has no value then ``None`` is returned.
        """
        # Lying to the type checker for better developer UX.
        return EmbedProxy(getattr(self, "_image", {}))  # type: ignore

    def set_image(self, *, url: Any | None) -> Self:
        """Sets the image for the embed content.

        This function returns the class instance to allow for fluent-style
        chaining.

        Parameters
        -----------
        url: :class:`str`
            The source URL for the image. Only HTTP(S) is supported.
            Inline attachment URLs are also supported, see :ref:`local_image`.
        """

        if url is None:
            try:
                del self._image  # type: ignore
            except AttributeError:
                pass
        else:
            self._image = {
                "url": str(url),
            }

        return self

    @property
    def thumbnail(self) -> _EmbedMediaProxy:
        """Returns an ``EmbedProxy`` denoting the thumbnail contents.

        Possible attributes you can access are:

        - ``url``
        - ``proxy_url``
        - ``width``
        - ``height``

        If the attribute has no value then ``None`` is returned.
        """
        # Lying to the type checker for better developer UX.
        return EmbedProxy(getattr(self, "_thumbnail", {}))  # type: ignore

    def set_thumbnail(self, *, url: Any | None) -> Self:
        """Sets the thumbnail for the embed content.

        This function returns the class instance to allow for fluent-style
        chaining.

        .. versionchanged:: 1.4
            Passing ``None`` removes the thumbnail.

        Parameters
        -----------
        url: :class:`str`
            The source URL for the thumbnail. Only HTTP(S) is supported.
            Inline attachment URLs are also supported, see :ref:`local_image`.
        """

        if url is None:
            try:
                del self._thumbnail  # type: ignore
            except AttributeError:
                pass
        else:
            self._thumbnail = {
                "url": str(url),
            }

        return self

    @property
    def video(self) -> _EmbedVideoProxy:
        """Returns an ``EmbedProxy`` denoting the video contents.

        Possible attributes include:

        - ``url`` for the video URL.
        - ``height`` for the video height.
        - ``width`` for the video width.

        If the attribute has no value then ``None`` is returned.
        """
        # Lying to the type checker for better developer UX.
        return EmbedProxy(getattr(self, "_video", {}))  # type: ignore

    @property
    def provider(self) -> _EmbedProviderProxy:
        """Returns an ``EmbedProxy`` denoting the provider contents.

        The only attributes that might be accessed are ``name`` and ``url``.

        If the attribute has no value then ``None`` is returned.
        """
        # Lying to the type checker for better developer UX.
        return EmbedProxy(getattr(self, "_provider", {}))  # type: ignore

    @property
    def author(self) -> _EmbedAuthorProxy:
        """Returns an ``EmbedProxy`` denoting the author contents.

        See :meth:`set_author` for possible values you can access.

        If the attribute has no value then ``None`` is returned.
        """
        # Lying to the type checker for better developer UX.
        return EmbedProxy(getattr(self, "_author", {}))  # type: ignore

    def set_author(self, *, name: Any, url: Any | None = None, icon_url: Any | None = None) -> Self:
        """Sets the author for the embed content.

        This function returns the class instance to allow for fluent-style
        chaining.

        Parameters
        -----------
        name: :class:`str`
            The name of the author. Can only be up to 256 characters.
        url: :class:`str`
            The URL for the author.
        icon_url: :class:`str`
            The URL of the author icon. Only HTTP(S) is supported.
            Inline attachment URLs are also supported, see :ref:`local_image`.
        """

        self._author = {
            "name": str(name),
        }

        if url is not None:
            self._author["url"] = str(url)

        if icon_url is not None:
            self._author["icon_url"] = str(icon_url)

        return self

    def remove_author(self) -> Self:
        """Clears embed's author information.

        This function returns the class instance to allow for fluent-style
        chaining.

        .. versionadded:: 1.4
        """
        with contextlib.suppress(AttributeError):
            del self._author

        return self

    @property
    def fields(self) -> list[_EmbedFieldProxy]:
        """List[``EmbedProxy``]: Returns a :class:`list` of ``EmbedProxy`` denoting the field contents.

        See :meth:`add_field` for possible values you can access.

        If the attribute has no value then ``None`` is returned.
        """
        # Lying to the type checker for better developer UX.
        return [EmbedProxy(d) for d in getattr(self, "_fields", [])]  # type: ignore

    def add_field(self, *, name: Any, value: Any, inline: bool = True) -> Self:
        """Adds a field to the embed object.

        This function returns the class instance to allow for fluent-style
        chaining. Can only be up to 25 fields.

        Parameters
        -----------
        name: :class:`str`
            The name of the field. Can only be up to 256 characters.
        value: :class:`str`
            The value of the field. Can only be up to 1024 characters.
        inline: :class:`bool`
            Whether the field should be displayed inline.
        """

        field = {
            "inline": inline,
            "name": str(name),
            "value": str(value),
        }

        try:
            self._fields.append(field)  # type: ignore
        except AttributeError:
            self._fields = [field]

        return self

    def insert_field_at(self, index: int, *, name: Any, value: Any, inline: bool = True) -> Self:
        """Inserts a field before a specified index to the embed.

        This function returns the class instance to allow for fluent-style
        chaining. Can only be up to 25 fields.

        .. versionadded:: 1.2

        Parameters
        -----------
        index: :class:`int`
            The index of where to insert the field.
        name: :class:`str`
            The name of the field. Can only be up to 256 characters.
        value: :class:`str`
            The value of the field. Can only be up to 1024 characters.
        inline: :class:`bool`
            Whether the field should be displayed inline.
        """

        field = {
            "inline": inline,
            "name": str(name),
            "value": str(value),
        }

        try:
            self._fields.insert(index, field)
        except AttributeError:
            self._fields = [field]

        return self

    def clear_fields(self) -> Self:
        """Removes all fields from this embed.

        This function returns the class instance to allow for fluent-style
        chaining.

        .. versionchanged:: 2.0
            This function now returns the class instance.
        """
        try:
            self._fields.clear()
        except AttributeError:
            self._fields = []

        return self

    def remove_field(self, index: int) -> Self:
        """Removes a field at a specified index.

        If the index is invalid or out of bounds then the error is
        silently swallowed.

        This function returns the class instance to allow for fluent-style
        chaining.

        .. note::

            When deleting a field by index, the index of the other fields
            shift to fill the gap just like a regular list.

        .. versionchanged:: 2.0
            This function now returns the class instance.

        Parameters
        -----------
        index: :class:`int`
            The index of the field to remove.
        """
        with contextlib.suppress(AttributeError, IndexError):
            del self._fields[index]

        return self

    def set_field_at(self, index: int, *, name: Any, value: Any, inline: bool = True) -> Self:
        """Modifies a field to the embed object.

        The index must point to a valid pre-existing field. Can only be up to 25 fields.

        This function returns the class instance to allow for fluent-style
        chaining.

        Parameters
        -----------
        index: :class:`int`
            The index of the field to modify.
        name: :class:`str`
            The name of the field. Can only be up to 256 characters.
        value: :class:`str`
            The value of the field. Can only be up to 1024 characters.
        inline: :class:`bool`
            Whether the field should be displayed inline.

        Raises
        -------
        IndexError
            An invalid index was provided.
        """

        try:
            field = self._fields[index]
        except (TypeError, IndexError, AttributeError):
            raise IndexError("field index out of range")

        field["name"] = str(name)
        field["value"] = str(value)
        field["inline"] = inline
        return self

    def to_dict(self) -> dict:
        """Converts this embed object into a dict."""

        # add in the raw data into the dict
        # fmt: off
        result = {
            key[1:]: getattr(self, key)
            for key in self.__slots__
            if key[0] == '_' and hasattr(self, key)
        }
        # fmt: on

        # deal with basic convenience wrappers

        try:
            colour = result.pop("colour")
        except KeyError:
            pass
        else:
            if colour:
                result["color"] = colour.value

        try:
            timestamp = result.pop("timestamp")
        except KeyError:
            pass
        else:
            if timestamp:
                if timestamp.tzinfo:
                    result["timestamp"] = timestamp.astimezone(tz=datetime.UTC).isoformat()
                else:
                    result["timestamp"] = timestamp.replace(tzinfo=datetime.UTC).isoformat()

        # add in the non raw attribute ones
        if self.type:
            result["type"] = self.type

        if self.description:
            result["description"] = self.description

        if self.url:
            result["url"] = self.url

        if self.title:
            result["title"] = self.title

        return result  # type: ignore # This payload is equivalent to the EmbedData type


class CommandInfo(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    user: discord.abc.User
    channel: discord.abc.GuildChannel
    guild: discord.Guild
    command: discord.app_commands.Command
    locale: discord.Locale
    message: discord.Message | None = None
    permissions: discord.Permissions = discord.Permissions()
    reply: Callable[..., Coroutine[Any, Any, Any]] | None = None
    client: discord.Client


command_info: type[CommandInfo] = CommandInfo


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
