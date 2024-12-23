from __future__ import division
import discord
from typing import (
    Any,
    Dict,
    List,
    Mapping,
    Optional,
    Protocol,
    TYPE_CHECKING,
    TypeVar,
    Union,
)
import datetime
from pyparsing import (
    Literal,
    CaselessLiteral,
    Word,
    Optional as Opt,
    Combine,
    Group,
    ZeroOrMore,
    Forward,
    nums,
    alphas,
    oneOf,
)
import math
import operator
from config import (
    tenorAPIKey,
    tenorCKey,
    GithubAuthToken,
    bytebin_url,
    bytebin_password,
    bytebin_username,
)
import aiohttp
import random
import re
from github import Github
import ast
import operator as op
import cmath
import tempfile
import os
from config import ImgBBApiKey
import base64
import json
import gzip
from difflib import SequenceMatcher


class EmbedProxy:
    def __init__(self, layer: Dict[str, Any]):
        self.__dict__.update(layer)

    def __len__(self) -> int:
        return len(self.__dict__)

    def __repr__(self) -> str:
        inner = ", ".join(
            (f"{k}={v!r}" for k, v in self.__dict__.items() if not k.startswith("_"))
        )
        return f"EmbedProxy({inner})"

    def __getattr__(self, attr: str) -> None:
        return None

    def __eq__(self, other: object) -> bool:
        return isinstance(other, EmbedProxy) and self.__dict__ == other.__dict__


from typing_extensions import Self

T = TypeVar("T")


class _EmbedFooterProxy(Protocol):
    text: Optional[str]
    icon_url: Optional[str]


class _EmbedFieldProxy(Protocol):
    name: Optional[str]
    value: Optional[str]
    inline: bool


class _EmbedMediaProxy(Protocol):
    url: Optional[str]
    proxy_url: Optional[str]
    height: Optional[int]
    width: Optional[int]


class _EmbedVideoProxy(Protocol):
    url: Optional[str]
    height: Optional[int]
    width: Optional[int]


class _EmbedProviderProxy(Protocol):
    name: Optional[str]
    url: Optional[str]


class _EmbedAuthorProxy(Protocol):
    name: Optional[str]
    url: Optional[str]
    icon_url: Optional[str]
    proxy_icon_url: Optional[str]


class tanjunEmbed:
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
        colour: Optional[Union[int, discord.Colour]] = 0xCB33F5,
        color: Optional[Union[int, discord.Colour]] = 0xCB33F5,
        title: Optional[Any] = None,
        type="rich",
        url: Optional[Any] = None,
        description: Optional[Any] = None,
        timestamp: Optional[datetime.datetime] = None,
    ):

        self.colour = colour if colour is not None else color
        self.title: Optional[str] = title
        self.type = type
        self.url: Optional[str] = url
        self.description: Optional[str] = description

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

        try:
            self._colour = discord.Colour(value=data["color"])
        except KeyError:
            pass

        try:
            self._timestamp = discord.utils.parse_time(data["timestamp"])
        except KeyError:
            pass

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

    def __eq__(self, other: discord.Embed) -> bool:
        return isinstance(other, discord.Embed) and (
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
    def colour(self) -> Optional[discord.Colour]:
        return getattr(self, "_colour", None)

    @colour.setter
    def colour(self, value: Optional[Union[int, discord.Colour]]) -> None:
        if value is None:
            self._colour = None
        elif isinstance(value, discord.Colour):
            self._colour = value
        elif isinstance(value, int):
            self._colour = discord.Colour(value=value)
        else:
            raise TypeError(
                f"Expected discord.Colour, int, or None but received {value.__class__.__name__} instead."
            )

    color = colour

    @property
    def timestamp(self) -> Optional[datetime.datetime]:
        return getattr(self, "_timestamp", None)

    @timestamp.setter
    def timestamp(self, value: Optional[datetime.datetime]) -> None:
        if isinstance(value, datetime.datetime):
            if value.tzinfo is None:
                value = value.astimezone()
            self._timestamp = value
        elif value is None:
            self._timestamp = None
        else:
            raise TypeError(
                f"Expected datetime.datetime or None received {value.__class__.__name__} instead"
            )

    @property
    def footer(self) -> _EmbedFooterProxy:
        """Returns an ``EmbedProxy`` denoting the footer contents.

        See :meth:`set_footer` for possible values you can access.

        If the attribute has no value then ``None`` is returned.
        """
        # Lying to the type checker for better developer UX.
        return EmbedProxy(getattr(self, "_footer", {}))  # type: ignore

    def set_footer(
        self, *, text: Optional[Any] = None, icon_url: Optional[Any] = None
    ) -> Self:
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
        try:
            del self._footer
        except AttributeError:
            pass

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

    def set_image(self, *, url: Optional[Any]) -> Self:
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
                del self._image
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

    def set_thumbnail(self, *, url: Optional[Any]) -> Self:
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
                del self._thumbnail
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

    def set_author(
        self, *, name: Any, url: Optional[Any] = None, icon_url: Optional[Any] = None
    ) -> Self:
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
        try:
            del self._author
        except AttributeError:
            pass

        return self

    @property
    def fields(self) -> List[_EmbedFieldProxy]:
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
            self._fields.append(field)
        except AttributeError:
            self._fields = [field]

        return self

    def insert_field_at(
        self, index: int, *, name: Any, value: Any, inline: bool = True
    ) -> Self:
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
        try:
            del self._fields[index]
        except (AttributeError, IndexError):
            pass

        return self

    def set_field_at(
        self, index: int, *, name: Any, value: Any, inline: bool = True
    ) -> Self:
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

    def to_dict(self) -> discord.Embed:
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
                    result["timestamp"] = timestamp.astimezone(
                        tz=datetime.timezone.utc
                    ).isoformat()
                else:
                    result["timestamp"] = timestamp.replace(
                        tzinfo=datetime.timezone.utc
                    ).isoformat()

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


class commandInfo:
    def __init__(
        self,
        user: discord.abc.User,
        channel: discord.abc.GuildChannel,
        guild: discord.Guild,
        command: discord.app_commands.Command,
        locale: str,
        message: discord.Message,
        permissions: discord.Permissions,
        reply,
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


def cmp(a, b):
    return (a > b) - (a < b)


class NumericStringParser(object):
    """
    Most of this code comes from the fourFn.py pyparsing example

    """

    def pushFirst(self, strg, loc, toks):
        self.exprStack.append(toks[0])

    def pushUMinus(self, strg, loc, toks):
        if toks and toks[0] == "-":
            self.exprStack.append("unary -")

    def __init__(self):
        point = Literal(".")
        e = CaselessLiteral("E")
        fnumber = Combine(
            Word("+-" + nums, nums)
            + Opt(point + Opt(Word(nums)))
            + Opt(e + Word("+-" + nums, nums))
        )
        ident = Word(alphas, alphas + nums + "_$")

        plus, minus, mult, div = map(Literal, "+-*/")
        lpar, rpar = map(Literal, "()")
        addop = plus | minus
        multop = mult | div
        expop = Literal("^")

        expr = Forward()
        atom = (Opt("-") + (ident + lpar + expr + rpar | fnumber)).setParseAction(
            self.pushFirst
        ) | (lpar + expr.suppress() + rpar).setParseAction(self.pushUMinus)

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
            "+": operator.add,
            "-": operator.sub,
            "*": operator.mul,
            "/": operator.truediv,
            "^": operator.pow,
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
        results = self.bnf.parseString(num_string, parseAll)
        val = self.evaluateStack(self.exprStack[:])
        return val


async def getGif(query: str, amount: int = 1, limit: int = 10):
    async with aiohttp.ClientSession() as session:

        async def fetch(url):
            async with session.get(url) as response:
                if response.status != 200:
                    return None
                return await response.json()

        r = await fetch(
            "https://tenor.googleapis.com/v2/search?q=%s&key=%s&client_key=%s&limit=%s"
            % (query, tenorAPIKey, tenorCKey, limit)
        )

        if r is None:
            return []
        # nosec: B311
        random.shuffle(r["results"])

        return [
            r["results"][i]["media_formats"]["mediumgif"]["url"] for i in range(amount)
        ]


def get_highest_exponent(polynomial):
    # Remove spaces
    polynomial = polynomial.replace(" ", "")

    # Regular expression to match terms
    term_pattern = re.compile(r"([+-]?\d*)(x(\^(\d+))?)?")

    # Find all matches
    terms = term_pattern.findall(polynomial)

    highest_exponent = 0

    for term in terms:
        coefficient, variable, _, exponent = term

        if variable:  # term contains 'x'
            if exponent:  # term contains 'x^n'
                highest_exponent = max(highest_exponent, int(exponent))
            else:  # term is 'x' which is x^1
                highest_exponent = max(highest_exponent, 1)

    return highest_exponent


def checkIfHasPro(guildid: int):
    if guildid == 0:
        return False
    return True


def checkIfhasPlus(userid: int):
    if userid == 0:
        return False
    return True


def missingLocalization(locale: str):
    g = Github(GithubAuthToken)
    repo = g.get_repo("TanjunBot/new-Tanjun")
    label = repo.get_label("missing localization")
    repo.create_issue(
        title="Missing localization",
        body=f"Missing localization for {locale}",
        labels=[label],
    )


def addFeedback(content, author):
    g = Github(GithubAuthToken)
    repo = g.get_repo("TanjunBot/new-Tanjun")
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

# Define allowed operators
operators = {
    ast.Add: op.add,
    ast.Sub: op.sub,
    ast.Mult: op.mul,
    ast.Div: op.truediv,
    ast.Pow: op.pow,
    ast.BitXor: op.xor,
    ast.USub: op.neg,
}


def eval_expr(expr):
    return eval_(ast.parse(expr, mode="eval").body)


def eval_(node):
    if isinstance(node, ast.Num):
        return node.n
    elif isinstance(node, ast.BinOp):
        return operators[type(node.op)](eval_(node.left), eval_(node.right))
    elif isinstance(node, ast.UnaryOp):
        return operators[type(node.op)](eval_(node.operand))
    else:
        raise TypeError(node)


def get_xp_for_level(level: int, scaling: str, custom_formula: str = None) -> int:
    if level <= 0:
        return 0
    if scaling == "custom" and custom_formula:
        try:
            result = eval_expr(custom_formula.replace("level", str(level)))
        except:
            return 0  # Return 0 if there's an error in the custom formula
    else:
        result = LEVEL_SCALINGS.get(scaling, LEVEL_SCALINGS["medium"])(level)
    if isinstance(result, complex):
        return 0  # Optionally handle or raise an error for complex results
    return math.floor(result)


def get_level_for_xp(xp: int, scaling: str, custom_formula: str = None) -> int:
    low, high = 1, 10000  # Assuming a high range cap for levels
    while low < high:
        mid = (low + high) // 2
        if get_xp_for_level(mid, scaling, custom_formula) > xp:
            high = mid
        else:
            low = mid + 1
    return low


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


class MockInteraction(discord.Interaction):
    def __init__(self, bot, guild, channel, user):
        # Initialize base Interaction with required parameters
        super().__init__(data={}, state=bot._connection)

        # Set required attributes
        self.type = discord.InteractionType.application_command
        self.id = 0  # Mock ID
        self.application_id = bot.application_id or 0
        self.guild = guild
        self.channel = channel
        self.user = user
        self.locale = "en-US"
        self.guild_locale = "en-US"
        self.client = bot

        # Mock the response object
        self._response = False
        self.response = MockInteractionResponse(self)
        self.followup = discord.Webhook.from_state(
            data={
                "application_id": self.application_id,
                "token": "mock_token",
                "id": self.id,
            },
            state=bot._connection,
        )

    # Override the original_response method to store the message
    async def original_response(self):
        return self.response.message


class MockInteractionResponse:
    def __init__(self, interaction):
        self.interaction = interaction
        self.message = None  # This will store the message sent

    async def send_message(self, content=None, embed=None, **kwargs):
        # Simulate sending a message
        self.message = discord.Message(
            state=self.interaction._state,
            channel=self.interaction.channel,
            data={
                "id": 1234567890,  # Mock message ID
                "content": content or "",
                "embeds": [embed.to_dict()] if embed else [],
                "channel_id": self.interaction.channel.id,
                "author": {
                    "id": self.interaction.client.user.id,
                    "username": self.interaction.client.user.name,
                    "discriminator": self.interaction.client.user.discriminator,
                    "bot": True,
                },
            },
        )

    async def delete_original_response(self):
        # Simulate deleting the message
        if self.message:
            # Here we can assume the message is deleted
            self.message = None

    # Implement other response methods as needed
    async def defer(self, **kwargs):
        pass

    async def edit_message(self, **kwargs):
        pass


def create_mock_interaction(self):
    guild = self.bot.guilds[0]  # Use the first guild the bot is connected to
    channel = guild.text_channels[0]  # Use the first text channel
    user = guild.me  # Use the bot as the user
    return MockInteraction(self.bot, guild, channel, user)


def date_time_to_timestamp(date: datetime.datetime) -> int:
    return int(date.timestamp())


async def upload_image_to_imgbb(image_bytes: bytes, file_extension: str) -> dict:
    # Create a temporary file with the appropriate file extension
    with tempfile.NamedTemporaryFile(
        delete=False, suffix="." + file_extension, mode="wb"
    ) as temp_file:
        temp_file.write(image_bytes)
        temp_file_path = temp_file.name

    # Upload the image to ImgBB
    async with aiohttp.ClientSession() as session:
        with open(temp_file_path, "rb") as image_file:
            form_data = aiohttp.FormData()
            form_data.add_field("key", ImgBBApiKey)
            form_data.add_field("image", image_file)
            form_data.add_field("name", f"tbg")

            async with session.post(
                "https://api.imgbb.com/1/upload", data=form_data
            ) as response:
                response_data = await response.json()

    # Optionally, delete the temporary file if you want to clean up
    os.remove(temp_file_path)

    return response_data


async def upload_to_tanjun_logs(content: str) -> str:
    compressed_content = gzip.compress(content.encode("utf-8"))
    url = bytebin_url
    username = bytebin_username
    password = bytebin_password

    async with aiohttp.ClientSession() as session:
        auth = aiohttp.BasicAuth(username, password)
        headers = {"Content-Type": "text/html", "Content-Encoding": "gzip"}

        async with session.post(
            url + "/post", data=compressed_content, headers=headers, auth=auth
        ) as response:
            if response.status == 201:
                response_data = await response.json()
                if "key" in response_data:
                    return f"{bytebin_url}/{response_data['key']}"
                else:
                    print("Unexpected response format:", response_data)
                    return None
            else:
                print(
                    f"Request failed with status {response.status}: {await response.text()}"
                )
                return None


def check_if_str_is_hex_color(color: str) -> bool:
    try:
        int(color, 16)
        return True
    except:
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
