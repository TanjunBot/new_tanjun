import ast
import datetime
import gzip
import math
import operator
import operator as op
import os
import random
import re
import tempfile
from collections.abc import (
    Callable,
    Mapping,  # For reply in commandInfo
)
from collections.abc import Coroutine as ABCCoroutine
from difflib import SequenceMatcher
from typing import (
    Any,
    Protocol,
    Self,
    TypeVar,
)

import aiohttp  # type: ignore[import-not-found]
import discord  # type: ignore[import-not-found]
from github import Github  # type: ignore[import-not-found]
from pyparsing import (  # type: ignore[import-not-found]
    CaselessLiteral,
    Combine,
    Forward,
    Literal,
    ParseResults,  # Import ParseResults for type hinting
    Suppress,  # Import Suppress
    Word,
    ZeroOrMore,
    alphas,
    nums,
)
from pyparsing import (
    Optional as PyParsingOptional,
)

# Assuming config.py exists and these variables are defined
# For the purpose of this script, I'll define them as Optional[str]
# In a real scenario, they would be loaded from your config file.
GithubAuthToken: str | None = "YOUR_GITHUB_TOKEN"  # str
ImgBBApiKey: str | None = "YOUR_IMGBB_API_KEY"  # str
bytebin_password: str | None = "YOUR_BYTEBIN_PASSWORD"  # str
bytebin_url: str | None = "YOUR_BYTEBIN_URL"  # str
bytebin_username: str | None = "YOUR_BYTEBIN_USERNAME"  # str
tenorAPIKey: str | None = "YOUR_TENOR_API_KEY"  # str
tenorCKey: str | None = "YOUR_TENOR_CLIENT_KEY"  # str


class EmbedProxy:
    def __init__(self, layer: dict[str, Any]):
        self.__dict__.update(layer)

    def __len__(self) -> int:
        return len(self.__dict__)

    def __repr__(self) -> str:
        inner: str = ", ".join((f"{k}={v!r}" for k, v in self.__dict__.items() if not k.startswith("_")))
        return f"EmbedProxy({inner})"

    def __getattr__(self, attr: str) -> Any:
        # Simplified to use get, which returns None if attr is not found.
        return self.__dict__.get(attr)

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


class tanjunEmbed:
    """Represents a Discord embed.
    (Docstring remains the same)
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

    title: str | None
    url: str | None
    type: str
    _timestamp: datetime.datetime | None
    _colour: discord.Colour | None
    _footer: dict[str, str]  # Stores footer data
    _image: dict[str, str]  # Stores image data
    _thumbnail: dict[str, str]  # Stores thumbnail data
    _video: dict[str, Any]  # Stores video data (can have url, height, width)
    _provider: dict[str, str]  # Stores provider data
    _author: dict[str, str]  # Stores author data
    _fields: list[dict[str, Any]]  # Stores a list of field dictionaries
    description: str | None

    def __init__(
        self,
        *,
        colour: int | discord.Colour | None = 0xCB33F5,  # Hex color
        color: int | discord.Colour | None = 0xCB33F5,  # Hex color
        title: Any | None = None,
        type: str = "rich",  # noqa A002, shadows built-in
        url: Any | None = None,
        description: Any | None = None,
        timestamp: datetime.datetime | None = None,
    ):
        # Initialize attributes that might not be set by property setters immediately
        self._timestamp = None
        self._colour = None  # This will be set by the property setter
        self._footer = {}
        self._image = {}
        self._thumbnail = {}
        self._video = {}
        self._provider = {}
        self._author = {}
        self._fields = []

        current_colour = colour if colour is not None else color
        if current_colour is not None:
            self.colour = current_colour

        self.title = str(title) if title is not None else None
        self.type = type
        self.url = str(url) if url is not None else None
        self.description = str(description) if description is not None else None

        if timestamp is not None:
            self.timestamp: datetime.datetime = timestamp

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> Self:
        self = cls.__new__(cls)

        self.title = None
        self.type = "rich"
        self.description = None
        self.url = None
        self._colour = None
        self._timestamp = None
        self._thumbnail = {}
        self._video = {}
        self._provider = {}
        self._author = {}
        self._fields = []
        self._image = {}
        self._footer = {}

        self.title = str(data["title"]) if data.get("title") is not None else None
        self.type = data.get("type", "rich")
        self.description = str(data["description"]) if data.get("description") is not None else None
        self.url = str(data["url"]) if data.get("url") is not None else None

        if "color" in data and data["color"] is not None:
            try:
                self._colour = discord.Colour(value=int(data["color"]))
            except (ValueError, TypeError):
                pass

        if "timestamp" in data and data["timestamp"] is not None:
            try:
                self._timestamp = discord.utils.parse_time(str(data["timestamp"]))
            except Exception:
                pass

        self._thumbnail = data.get("thumbnail", {})
        self._video = data.get("video", {})
        self._provider = data.get("provider", {})
        self._author = data.get("author", {})
        self._fields = data.get("fields", [])
        self._image = data.get("image", {})
        self._footer = data.get("footer", {})

        return self

    def copy(self) -> Self:
        return self.__class__.from_dict(self.to_dict())

    def __len__(self) -> int:
        total: int = len(self.title or "") + len(self.description or "")
        for field in getattr(self, "_fields", []):
            total += len(str(field.get("name", ""))) + len(str(field.get("value", "")))

        try:
            footer_text: str | None = self._footer.get("text")
            if footer_text:
                total += len(footer_text)
        except AttributeError:
            pass

        try:
            author_name: str | None = self._author.get("name")
            if author_name:
                total += len(author_name)
        except AttributeError:
            pass

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
        if not isinstance(other, tanjunEmbed):
            return NotImplemented
        return self.to_dict() == other.to_dict()

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
            self._colour = None

    color = colour

    @property
    def timestamp(self) -> datetime.datetime | None:
        return getattr(self, "_timestamp", None)

    @timestamp.setter
    def timestamp(self, value: datetime.datetime | None) -> None:
        if isinstance(value, datetime.datetime):
            if value.tzinfo is None:
                self._timestamp = value.astimezone()
            else:
                self._timestamp = value
        elif value is None:
            self._timestamp = None

    @property
    def footer(self) -> _EmbedFooterProxy:
        return EmbedProxy(getattr(self, "_footer", {}))

    def set_footer(self, *, text: Any | None = None, icon_url: Any | None = None) -> Self:
        self._footer = {}
        if text is not None:
            self._footer["text"] = str(text)
        if icon_url is not None:
            self._footer["icon_url"] = str(icon_url)
        return self

    def remove_footer(self) -> Self:
        self._footer = {}
        return self

    @property
    def image(self) -> _EmbedMediaProxy:
        return EmbedProxy(getattr(self, "_image", {}))

    def set_image(self, *, url: Any | None) -> Self:
        if url is None:
            self._image = {}
        else:
            self._image = {"url": str(url)}
        return self

    @property
    def thumbnail(self) -> _EmbedMediaProxy:
        return EmbedProxy(getattr(self, "_thumbnail", {}))

    def set_thumbnail(self, *, url: Any | None) -> Self:
        if url is None:
            self._thumbnail = {}
        else:
            self._thumbnail = {"url": str(url)}
        return self

    @property
    def video(self) -> _EmbedVideoProxy:
        return EmbedProxy(getattr(self, "_video", {}))

    @property
    def provider(self) -> _EmbedProviderProxy:
        return EmbedProxy(getattr(self, "_provider", {}))

    @property
    def author(self) -> _EmbedAuthorProxy:
        return EmbedProxy(getattr(self, "_author", {}))

    def set_author(self, *, name: Any, url: Any | None = None, icon_url: Any | None = None) -> Self:
        self._author = {"name": str(name)}
        if url is not None:
            self._author["url"] = str(url)
        if icon_url is not None:
            self._author["icon_url"] = str(icon_url)
        return self

    def remove_author(self) -> Self:
        self._author = {}
        return self

    @property
    def fields(self) -> list[_EmbedFieldProxy]:
        return [EmbedProxy(d) for d in getattr(self, "_fields", [])]

    def add_field(self, *, name: Any, value: Any, inline: bool = True) -> Self:
        field: dict[str, Any] = {"inline": inline, "name": str(name), "value": str(value)}
        if not hasattr(self, "_fields") or not isinstance(self._fields, list):
            self._fields = []
        self._fields.append(field)
        return self

    def insert_field_at(self, index: int, *, name: Any, value: Any, inline: bool = True) -> Self:
        field: dict[str, Any] = {"inline": inline, "name": str(name), "value": str(value)}
        if not hasattr(self, "_fields") or not isinstance(self._fields, list):
            self._fields = []
        if 0 <= index <= len(self._fields):
            self._fields.insert(index, field)
        elif index < 0:
            self._fields.insert(0, field)
        else:
            self._fields.append(field)
        return self

    def clear_fields(self) -> Self:
        self._fields = []
        return self

    def remove_field(self, index: int) -> Self:
        try:
            if hasattr(self, "_fields") and isinstance(self._fields, list):
                del self._fields[index]
        except IndexError:
            pass
        return self

    def set_field_at(self, index: int, *, name: Any, value: Any, inline: bool = True) -> Self:
        if not hasattr(self, "_fields") or not isinstance(self._fields, list) or not self._fields:
            raise IndexError("field index out of range, fields list not initialized or empty")
        try:
            field_to_modify: dict[str, Any] = self._fields[index]
            field_to_modify["name"] = str(name)
            field_to_modify["value"] = str(value)
            field_to_modify["inline"] = inline
        except IndexError:
            raise IndexError("field index out of range")
        return self

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key in self.__slots__:
            if key.startswith("_") and hasattr(self, key):
                attr_value = getattr(self, key)
                if attr_value is not None and (not isinstance(attr_value, (dict, list)) or attr_value):
                    result[key[1:]] = attr_value
        if self._colour is not None:
            result["color"] = self._colour.value
        else:
            result.pop("colour", None)
            result.pop("color", None)
        if self._timestamp is not None:
            ts = self._timestamp
            if ts.tzinfo:
                result["timestamp"] = ts.astimezone(tz=datetime.UTC).isoformat()
            else:
                result["timestamp"] = ts.replace(tzinfo=datetime.UTC).isoformat()
        else:
            result.pop("timestamp", None)
        if self.type:
            result["type"] = self.type
        if self.description:
            result["description"] = self.description
        if self.url:
            result["url"] = self.url
        if self.title:
            result["title"] = self.title
        if "fields" in result and result["fields"]:
            pass
        elif not getattr(self, "_fields", []):
            result.pop("fields", None)
        elif "_fields" in result:
            result["fields"] = result.pop("_fields")
        return result


class commandInfo:
    def __init__(
        self,
        user: discord.abc.User,
        channel: discord.abc.GuildChannel,
        guild: discord.Guild,
        command: discord.app_commands.Command[Any, ..., Any],
        locale: str,
        message: discord.Message,
        permissions: discord.Permissions,
        reply: ABCCoroutine[Any, Any, discord.Message],
        client: discord.Client,
    ):
        self.user, self.channel, self.guild, self.command = user, channel, guild, command
        self.locale, self.message, self.permissions, self.reply, self.client = locale, message, permissions, reply, client


def cmp(a: int | float, b: int | float) -> int:
    return (a > b) - (a < b)


class NumericStringParser:
    def __init__(self) -> None:
        self.exprStack: list[Any] = []
        self.push_first_action: Callable[[ParseResults], None] = lambda pr: self.exprStack.append(pr[0])
        self.push_uminus_sign_action: Callable[[ParseResults], None] = (
            lambda pr: self.exprStack.append("unary -") if pr and pr[0] == "-" else None
        )
        self.push_operator_action: Callable[[ParseResults], None] = lambda pr: self.exprStack.append(pr[0])
        self.push_function_call_action: Callable[[ParseResults], None] = lambda pr: self.exprStack.append(pr[0])
        self.bnf: Forward = self._setup_parser()
        self.fn: dict[str, Callable[..., float | int]] = {
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
            "sgn": lambda a: (abs(a) > 1e-12 and cmp(a, 0)) or 0,
            "sqrt": math.sqrt,
            "factorial": math.factorial,
            "degrees": math.degrees,
            "radians": math.radians,
            "ceil": math.ceil,
            "floor": math.floor,
            "pi": lambda: math.pi,
            "e": lambda: math.e,
            "fac": math.factorial,
        }
        self.opn: dict[str, Callable[[float | int, float | int], float | int]] = {
            "+": operator.add,
            "-": operator.sub,
            "*": operator.mul,
            "/": operator.truediv,
            "^": operator.pow,
        }

    def _setup_parser(self) -> Forward:
        point, e_literal = Literal("."), CaselessLiteral("E")
        fnumber = Combine(
            Word("+-" + nums, nums)
            + PyParsingOptional(point + PyParsingOptional(Word(nums)))
            + PyParsingOptional(e_literal + Word("+-" + nums, nums))
        )
        ident = Word(alphas, alphas + nums + "_$")
        plus, minus, mult, div = map(Literal, "+-*/")
        lpar, rpar = map(Suppress, "()")
        addop, multop, expop = plus | minus, mult | div, Literal("^")
        expr = Forward()
        func_call = (ident + lpar + expr + rpar).setParseAction(self.push_function_call_action)
        atom = PyParsingOptional(Literal("-")).setParseAction(self.push_uminus_sign_action) + (
            func_call
            | ident.setParseAction(self.push_first_action)
            | fnumber.setParseAction(self.push_first_action)
            | (lpar + expr + rpar)
        )
        factor = Forward()
        factor << atom + ZeroOrMore((expop + factor).setParseAction(self.push_operator_action))
        term = factor + ZeroOrMore((multop + factor).setParseAction(self.push_operator_action))
        expr << term + ZeroOrMore((addop + term).setParseAction(self.push_operator_action))
        return expr

    def evaluateStack(self, s: list[Any]) -> float | int:
        if not s:
            raise ValueError("Evaluation stack is empty.")
        op: Any = s.pop()
        if op == "unary -":
            if not s:
                raise ValueError("Stack empty for unary minus operand.")
            return -self.evaluateStack(s)
        elif isinstance(op, str) and op in self.opn:
            if len(s) < 2:
                raise ValueError(f"Stack needs two operands for operator {op}.")
            op2, op1 = self.evaluateStack(s), self.evaluateStack(s)
            return self.opn[op](op1, op2)
        elif isinstance(op, str) and op in self.fn:
            func = self.fn[op]
            if op in ["pi", "e"]:
                return func()
            else:
                if not s:
                    raise ValueError(f"Stack empty for argument to function {op}.")
                arg = self.evaluateStack(s)
                return func(arg)
        elif isinstance(op, (int, float)):
            return op
        elif isinstance(op, str):
            try:
                return float(op)
            except ValueError:
                raise Exception(f"Invalid token or identifier on stack: {op}")
        else:
            raise Exception(f"Unexpected item on stack: {op} of type {type(op)}")

    def eval(self, num_string: str, parseAll: bool = True) -> float | int:
        self.exprStack = []
        try:
            self.bnf.parseString(num_string, parseAll=parseAll)
        except Exception as e:
            raise ValueError(f"Error parsing expression '{num_string}': {e}")
        if not self.exprStack:
            raise ValueError(f"Expression '{num_string}' did not yield a calculable stack.")
        try:
            return self.evaluateStack(self.exprStack[:])
        except ValueError as e:
            raise ValueError(f"Error evaluating expression '{num_string}': {e}")
        except Exception as e:
            raise Exception(f"Unexpected error evaluating '{num_string}': {e}")


async def getGif(query: str, amount: int = 1, limit: int = 10) -> list[str]:
    async with aiohttp.ClientSession() as session:

        async def fetch(url: str) -> dict[str, Any] | None:
            async with session.get(url) as response:
                if response.status != 200:
                    print(f"Tenor API request failed with status {response.status} for URL: {url}")
                    return None
                try:
                    return await response.json()  # type: ignore[no-any-return]
                except aiohttp.ContentTypeError:
                    print(f"Tenor API response was not JSON for URL: {url}. Response text: {await response.text()}")
                    return None

        if not tenorAPIKey or not tenorCKey:
            print("Tenor API key or Client Key is not configured.")
            return []
        request_url = (
            f"https://tenor.googleapis.com/v2/search?q={query}&key={tenorAPIKey}&client_key={tenorCKey}&limit={limit}"
        )
        r = await fetch(request_url)
        if r is None or "results" not in r or not isinstance(r["results"], list):
            return []
        results_list: list[dict[str, Any]] = r["results"]
        if not results_list:
            return []
        random.shuffle(results_list)
        gifs_found: list[str] = []
        for i in range(min(amount, len(results_list))):
            try:
                media_formats = results_list[i].get("media_formats")
                if media_formats and isinstance(media_formats, dict):
                    medium_gif = media_formats.get("mediumgif")
                    if medium_gif and isinstance(medium_gif, dict):
                        url_val = medium_gif.get("url")
                        if isinstance(url_val, str):
                            gifs_found.append(url_val)
            except (KeyError, TypeError, AttributeError) as e:
                print(f"Error processing Tenor result item: {results_list[i]}. Error: {e}")
        return gifs_found


def get_highest_exponent(polynomial: str) -> int:
    polynomial = polynomial.replace(" ", "")
    term_pattern = re.compile(r"([+-]?\d*\.?\d*)(x(?:(?:\^)(\d+))?)?")
    terms: list[tuple[str, str, str, str]] = term_pattern.findall(polynomial)
    highest_exponent: int = 0
    for coefficient_str, x_part, _, exponent_str in terms:
        if not coefficient_str and not x_part:
            continue
        if x_part:
            if exponent_str:
                try:
                    highest_exponent = max(highest_exponent, int(exponent_str))
                except ValueError:
                    pass
            elif "x" in x_part:
                highest_exponent = max(highest_exponent, 1)
    return highest_exponent


def checkIfHasPro(guildid: int) -> bool:
    return guildid != 0


def checkIfhasPlus(userid: int) -> bool:
    return userid != 0


def missingLocalization(locale: str) -> None:
    try:
        if not GithubAuthToken:
            print("GithubAuthToken not configured.")
            return
        g = Github(GithubAuthToken)
        repo = g.get_repo("TanjunBot/new_tanjun")
        label = repo.get_label("missing localization")
        repo.create_issue(
            title=f"Missing localization for {locale}", body=f"Missing localization for {locale}", labels=[label]
        )
    except Exception as e:
        print(f"Error creating GitHub issue for missing localization '{locale}': {e}")


def addFeedback(content: str, author: str) -> None:
    try:
        if not GithubAuthToken:
            print("GithubAuthToken not configured.")
            return
        g = Github(GithubAuthToken)
        repo = g.get_repo("TanjunBot/new_tanjun")
        label = repo.get_label("Feedback")
        repo.create_issue(title=f"Feedback from {author}", body=f"# Feedback from {author}:\n\n{content}", labels=[label])
    except Exception as e:
        print(f"Error creating GitHub issue for feedback from '{author}': {e}")


LevelScalingFunc = Callable[[int], float]
LEVEL_SCALINGS: dict[str, LevelScalingFunc] = {
    "easy": lambda lvl: 100 * lvl,
    "medium": lambda lvl: 100 * (lvl**1.5),
    "hard": lambda lvl: 100 * (lvl**2),
    "extreme": lambda lvl: 100 * (lvl**2.5),
}

OperatorFunc = Callable[[Any, Any], Any]
UnaryOperatorFunc = Callable[[Any], Any]
operators_map: dict[type[ast.AST], OperatorFunc | UnaryOperatorFunc] = {  # Changed key type to Type[ast.AST]
    ast.Add: op.add,
    ast.Sub: op.sub,
    ast.Mult: op.mul,
    ast.Div: op.truediv,
    ast.Pow: op.pow,
    ast.BitXor: op.xor,
    ast.USub: op.neg,
    ast.Mod: op.mod,
}


def sqrt_n(x: float, n: float = 2.0) -> float:
    if n == 0:
        raise ValueError("The root degree n cannot be zero.")
    if x < 0 and n % 2 == 0:
        raise ValueError("Cannot compute even root of a negative number with real numbers.")
    return float(x ** (1.0 / n))


def log_n(x: float, base: float = math.e) -> float:
    if x <= 0:
        raise ValueError("Logarithm undefined for non-positive values.")
    if base <= 0 or base == 1:
        raise ValueError("Logarithm base must be positive and not equal to 1.")
    return math.log(x, base)


VariablesType = dict[str, float | int | complex | Callable[..., Any]]  # Added complex


def eval_expr(expr: str, variables: VariablesType | None = None) -> float | int | complex:
    if variables is None:
        variables = {}
    local_vars: VariablesType = {
        "pi": math.pi,
        "e": math.e,
        "sin": math.sin,
        "cos": math.cos,
        "tan": math.tan,
        "asin": math.asin,
        "acos": math.acos,
        "atan": math.atan,
        "log": log_n,
        "log10": lambda x_val: log_n(x_val, 10),
        "log2": lambda x_val: log_n(x_val, 2),
        "ln": lambda x_val: log_n(x_val, math.e),
        "sqrt": sqrt_n,
        "nthroot": sqrt_n,
        "abs": abs,
        "floor": math.floor,
        "ceil": math.ceil,
        "pow": pow,
    }
    local_vars.update(variables)
    try:
        parsed_ast = ast.parse(expr, mode="eval").body
        return eval_(parsed_ast, local_vars)
    except SyntaxError as e:
        raise ValueError(f"Syntax error in expression: {expr}. Details: {e}")
    except TypeError as e:
        raise ValueError(f"Type error during evaluation of: {expr}. Details: {e}")
    except NameError as e:
        raise NameError(f"Name error in expression: {expr}. Details: {e}")
    except Exception as e:
        print(f"Unexpected error evaluating expression '{expr}': {type(e).__name__}: {e}")
        raise


def eval_(node: ast.AST, variables: VariablesType) -> float | int | complex:
    if isinstance(node, ast.Constant):
        if isinstance(node.value, (int, float, complex)):
            return node.value
        # elif isinstance(node.value, bool): return int(node.value) # Optional: handle bools
        else:
            raise TypeError(f"Unsupported constant type in expression: {type(node.value)} ({node.value!r})")
    elif isinstance(node, ast.Num):  # Deprecated
        return node.n
    elif isinstance(node, ast.BinOp):
        left_val, right_val = eval_(node.left, variables), eval_(node.right, variables)
        op_type = type(node.op)
        if op_type in operators_map:
            if not (isinstance(left_val, (int, float, complex)) and isinstance(right_val, (int, float, complex))):
                raise TypeError(f"Operands for {op_type} must be numeric. Got {type(left_val)} and {type(right_val)}")
            return operators_map[op_type](left_val, right_val)  # type: ignore[no-any-return, call-arg]
        raise TypeError(f"Unsupported binary operator: {op_type}")
    elif isinstance(node, ast.UnaryOp):
        operand_val = eval_(node.operand, variables)
        op_type = type(node.op)  # type: ignore[assignment]
        if op_type in operators_map:
            if not isinstance(operand_val, (int, float, complex)):
                raise TypeError(f"Operand for {op_type} must be numeric. Got {type(operand_val)}")
            return operators_map[op_type](operand_val)  # type: ignore[no-any-return, call-arg]
        raise TypeError(f"Unsupported unary operator: {op_type}")
    elif isinstance(node, ast.Call):
        func_name_node = node.func
        func_to_call: Callable[..., Any] | None = None
        func_id_str = "unknown_function"
        if isinstance(func_name_node, ast.Name):
            func_id_str = func_name_node.id
            if func_id_str in variables:
                potential_func = variables[func_id_str]
                if callable(potential_func):
                    func_to_call = potential_func
                else:
                    raise TypeError(f"'{func_id_str}' is not a callable function (type: {type(potential_func)}).")
            else:
                raise NameError(f"Function '{func_id_str}' is not defined in variables.")
        if not func_to_call:
            raise TypeError(f"'{func_id_str}' is not a callable function.")
        args = [eval_(arg, variables) for arg in node.args]
        try:
            return func_to_call(*args)  # type: ignore[no-any-return]
        except TypeError as e:
            raise TypeError(f"Error calling function '{getattr(func_to_call, '__name__', func_id_str)}': {e}")
    elif isinstance(node, ast.Name):
        if node.id in variables:
            val = variables[node.id]
            if callable(val):
                raise TypeError(f"Variable '{node.id}' holds a function but was not called. Use {node.id}(...).")
            if not isinstance(val, (int, float, complex)):  # Ensure it's numeric
                raise TypeError(f"Variable '{node.id}' is not a numeric value (type: {type(val)}).")
            return val
        raise NameError(f"Variable '{node.id}' is not defined.")
    else:
        raise TypeError(f"Unsupported AST node type: {type(node).__name__}")


def get_xp_for_level(level: int, scaling: str, custom_formula: str | None = None) -> int:
    if level <= 0:
        return 0
    result: float | int | complex
    if scaling == "custom" and custom_formula:
        try:
            result = eval_expr(custom_formula, variables={"level": level})
        except (ValueError, NameError, TypeError, Exception) as e:
            print(f"Error evaluating custom XP formula '{custom_formula}' for level {level}: {e}")
            return 0
    elif scaling in LEVEL_SCALINGS:
        result = LEVEL_SCALINGS[scaling](level)
    else:
        print(f"Warning: Unknown XP scaling '{scaling}'. Using 'medium'.")
        result = LEVEL_SCALINGS["medium"](level)

    if isinstance(result, complex):
        print(f"Warning: Custom XP formula resulted in a complex number ({result}). Using real part or 0.")
        return math.floor(result.real) if result.real is not None else 0
    elif isinstance(result, (float, int)):
        if math.isinf(result) or math.isnan(result):
            print(f"Warning: XP calculation resulted in {result}. Returning 0.")
            return 0
        return math.floor(result)


def get_level_for_xp(xp: int, scaling: str, custom_formula: str | None = None) -> int:
    if xp < 0:
        return 0

    # This initial block handles xp == 0 correctly based on xp needed for level 1
    # It makes the later (removed) block for `if xp < xp_for_lvl_1` redundant for the xp==0 case.
    if xp == 0:
        xp_for_level_1_val = get_xp_for_level(1, scaling, custom_formula)
        if xp < xp_for_level_1_val:  # Equivalent to 0 < xp_for_level_1_val
            return 0
        # If xp_for_level_1_val is 0 or negative, and xp is 0, proceed to binary search.
        # The binary search should then correctly determine the level (e.g. level 1 if xp_for_level(1) is 0)

    # If xp > 0, but still less than xp for level 1, it's level 0.
    # This check is important before binary search which assumes level >=1.
    # This was the block that had the "unreachable" error, now removed as the logic is consolidated.
    # xp_for_lvl_1_check = get_xp_for_level(1, scaling, custom_formula)
    # if xp < xp_for_lvl_1_check:
    #     return 0

    low, high, ans = 1, 200000, 0
    # Check if xp is less than what's needed for level 1 before starting binary search from level 1
    # This ensures that if xp is positive but very small, it correctly returns level 0.
    # This check was previously part of the "unreachable" code.
    # It's important to have it if the binary search starts assuming level 1.
    # However, if the `if xp == 0:` block handles it, and for `xp > 0` the binary search is okay,
    # this might still be slightly redundant or could be integrated better.
    # Let's test the flow:
    # xp = 5, get_xp_for_level(1) = 100.
    # xp < 0 is false. xp == 0 is false.
    # Binary search: low=1. ans=0.
    # mid=1. xp_needed_for_mid = 100.
    # xp_needed_for_mid (100) <= xp (5) is FALSE.
    # search_high becomes 0. Loop terminates. ans = 0. Correct.

    # xp = 0, get_xp_for_level(1) = 0
    # xp < 0 is false. xp == 0 is true.
    # xp_for_level_1_val = 0.
    # if 0 < 0 is false.
    # Binary search: low=1. ans=0.
    # mid=1. xp_needed_for_mid = 0.
    # if 0 <= 0 is true. ans = 1. search_low = 2.
    # This returns 1, which is correct if level 1 starts at 0 XP.

    # The initial `if xp == 0:` block seems sufficient. The unreachable code was indeed redundant.

    search_low, search_high = low, high
    while search_low <= search_high:
        mid = (search_low + search_high) // 2
        if mid == 0:
            search_low = 1
            continue  # Should not happen if low starts at 1
        xp_needed_for_mid = get_xp_for_level(mid, scaling, custom_formula)
        if xp_needed_for_mid <= xp:
            ans, search_low = mid, mid + 1
        else:
            search_high = mid - 1
    return ans


def relativeTimeStrToDate(time_string: str) -> datetime.datetime:
    if not time_string.strip():
        return datetime.datetime.now(datetime.UTC)
    pattern = r"(\d+)\s*([smhd])"
    matches = re.findall(pattern, time_string.lower())
    if not matches:
        return datetime.datetime.now(datetime.UTC)
    delta_kwargs: dict[str, int] = {"days": 0, "hours": 0, "minutes": 0, "seconds": 0}
    for value_str, unit in matches:
        try:
            value = int(value_str)
            if unit == "s":
                delta_kwargs["seconds"] += value
            elif unit == "m":
                delta_kwargs["minutes"] += value
            elif unit == "h":
                delta_kwargs["hours"] += value
            elif unit == "d":
                delta_kwargs["days"] += value
        except ValueError:
            print(f"Warning: Invalid number '{value_str}' in time string '{time_string}'.")
    return datetime.datetime.now(datetime.UTC) + datetime.timedelta(**delta_kwargs)


def relativeTimeToSeconds(time_string: str) -> int:
    if not time_string.strip():
        return 0
    pattern = r"(\d+)\s*([smhd])"
    matches = re.findall(pattern, time_string.lower())
    if not matches:
        return 0
    total_seconds = 0
    for value_str, unit in matches:
        try:
            value = int(value_str)
            if unit == "s":
                total_seconds += value
            elif unit == "m":
                total_seconds += value * 60
            elif unit == "h":
                total_seconds += value * 3600
            elif unit == "d":
                total_seconds += value * 86400
        except ValueError:
            continue
    return total_seconds


def dateToRelativeTimeStr(date_obj: datetime.datetime) -> str:
    now_utc = datetime.datetime.now(datetime.UTC)
    date_obj_utc = date_obj.astimezone(datetime.UTC) if date_obj.tzinfo else date_obj.replace(tzinfo=datetime.UTC)
    delta = date_obj_utc - now_utc
    if delta.total_seconds() < 0:
        return "now"
    days, rem_secs = delta.days, delta.seconds
    hours, rem_secs = rem_secs // 3600, rem_secs % 3600
    minutes, seconds = rem_secs // 60, rem_secs % 60
    components: list[str] = []
    if days > 0:
        components.append(f"{days}d")
    if hours > 0:
        components.append(f"{hours}h")
    if minutes > 0:
        components.append(f"{minutes}m")
    if seconds > 0:
        components.append(f"{seconds}s")
    return " ".join(components) if components else "now"


class InteractionClient(Protocol):
    user: discord.ClientUser | None
    application_id: int | None
    _connection: Any


class InteractionGuild(Protocol):
    id: int
    name: str


class InteractionChannel(Protocol):
    id: int


class InteractionUser(Protocol):
    id: int
    name: str
    discriminator: str
    avatar: str | None
    nick: str | None


class MockInteraction(discord.Interaction):
    def __init__(
        self, bot: InteractionClient, guild: InteractionGuild | None, channel: InteractionChannel | None, user: InteractionUser
    ):
        mock_snowflake_id = discord.utils.time_snowflake(datetime.datetime.now(datetime.UTC))
        mock_data: dict[str, Any] = {
            "id": mock_snowflake_id,
            "application_id": bot.application_id or 0,
            "type": discord.InteractionType.application_command.value,
            "data": {},
            "guild_id": guild.id if guild else None,
            "channel_id": channel.id if channel else None,
            "token": "mock_interaction_token_xxxxxxxxxxxx",
            "version": 1,
        }
        if guild and isinstance(user, discord.Member):
            mock_data["member"] = {
                "user": {"id": user.id, "username": user.name, "discriminator": user.discriminator, "avatar": user.avatar},
                "nick": getattr(user, "nick", None),
                "roles": [],
                "joined_at": datetime.datetime.now(datetime.UTC).isoformat(),
                "deaf": False,
                "mute": False,
            }
        else:
            mock_data["user"] = {
                "id": user.id,
                "username": user.name,
                "discriminator": user.discriminator,
                "avatar": user.avatar,
            }
        super().__init__(data=mock_data, state=bot._connection)
        self._mock_guild, self._mock_channel, self._mock_user = guild, channel, user
        self.client: InteractionClient = bot
        self._response_issued = False
        self.response: MockInteractionResponse = MockInteractionResponse(self)
        self.followup = MockWebhook(state=bot._connection, application_id=self.application_id, token=self.token)

    @property
    def guild(self) -> discord.Guild | None:
        return self._mock_guild

    @property
    def channel(self) -> discord.abc.MessageableChannel | None:
        return self._mock_channel

    @property
    def user(self) -> discord.User | discord.Member:
        return self._mock_user

    async def original_response(self) -> discord.InteractionMessage:
        if hasattr(self.response, "message") and self.response.message:
            return self.response.message
        raise discord.NotFound(None, "Original response message not found or not sent.")


class MockInteractionResponse(discord.InteractionResponse):
    def __init__(self, interaction: MockInteraction):
        super().__init__(interaction)
        self.interaction: MockInteraction = interaction
        self.message: discord.Message | None = None

    async def send_message(self, content: str | None = None, *, embed: tanjunEmbed | None = None, **kwargs: Any) -> None:
        if self.interaction._response_issued:
            raise discord.InteractionResponded(self.interaction)
        message_data: dict[str, Any] = {
            "id": discord.utils.time_snowflake(datetime.datetime.now(datetime.UTC)),
            "channel_id": self.interaction.channel.id if self.interaction.channel else 0,
            "guild_id": self.interaction.guild.id if self.interaction.guild else None,
            "content": content or "",
            "embeds": [embed.to_dict()] if embed else [],
            "author": {
                "id": self.interaction.client.user.id if self.interaction.client and self.interaction.client.user else 0,
                "username": self.interaction.client.user.name
                if self.interaction.client and self.interaction.client.user
                else "MockBot",
                "discriminator": self.interaction.client.user.discriminator
                if self.interaction.client and self.interaction.client.user
                else "0000",
                "bot": True,
                "avatar": None,
            },
            "timestamp": datetime.datetime.now(datetime.UTC).isoformat(),
            "edited_timestamp": None,
            "tts": False,
            "mention_everyone": False,
            "mentions": [],
            "mention_roles": [],
            "mention_channels": [],
            "attachments": [],
            "pinned": False,
            "type": discord.MessageType.default.value,
            "webhook_id": None,
        }
        if self.interaction.channel and hasattr(self.interaction, "_state"):
            self.message = discord.Message(state=self.interaction._state, channel=self.interaction.channel, data=message_data)
        else:
            self.message = None
        self.interaction._response_issued = True

    async def delete_original_response(self) -> None:
        if not self.interaction._response_issued or not self.message:
            raise discord.NotFound(None, "No original response to delete.")
        self.message = None

    async def defer(self, *, thinking: bool = False, ephemeral: bool = False) -> None:
        if self.interaction._response_issued:
            raise discord.InteractionResponded(self.interaction)
        self.interaction._response_issued = True

    async def edit_message(self, **kwargs: Any) -> None:
        if not self.interaction._response_issued or not self.message:
            raise discord.HTTPException(None, "Cannot edit a message that has not been sent.")
        content, embed_val = kwargs.get("content"), kwargs.get("embed")  # Renamed embed to embed_val
        if content is not None and self.message:
            self.message.content = content
        if "embed" in kwargs and self.message:
            self.message.embeds = [embed_val.to_dict()] if embed_val else []


class MockWebhook:
    def __init__(self, state: Any, application_id: int | None, token: str):
        self._state, self.application_id, self.token, self.id = state, application_id, token, 0

    async def send(self, content: str | None = None, *, embed: tanjunEmbed | None = None, **kwargs: Any) -> discord.Message:
        message_data: dict[str, Any] = {
            "id": discord.utils.time_snowflake(datetime.datetime.now(datetime.UTC)),
            "channel_id": 0,
            "content": content or "",
            "embeds": [embed.to_dict()] if embed else [],
            "author": {
                "id": self.application_id or 0,
                "username": "MockApp",
                "discriminator": "0000",
                "bot": True,
                "avatar": None,
            },
            "timestamp": datetime.datetime.now(datetime.UTC).isoformat(),
            "webhook_id": str(self.id),
        }
        mock_channel = None
        if hasattr(self._state, "Client") and self._state.Client and hasattr(self._state.Client, "get_channel"):
            mock_channel = self._state.Client.get_channel(0)
        return discord.Message(state=self._state, channel=mock_channel, data=message_data)

    async def edit_message(self, message_id: int, **kwargs: Any) -> discord.Message:
        raise NotImplementedError

    async def delete_message(self, message_id: int) -> None:
        pass


def create_mock_interaction(bot_instance: InteractionClient) -> MockInteraction:
    mock_guild = type("MockGuild", (), {"id": 12345, "name": "Mock Guild"})() if bot_instance else None
    mock_channel = type("MockChannel", (), {"id": 67890})() if bot_instance else None
    if not bot_instance or not bot_instance.user:
        raise ValueError("Bot instance or bot user is not valid.")
    mock_user_data = {
        "id": bot_instance.user.id,
        "name": bot_instance.user.name,
        "discriminator": bot_instance.user.discriminator,
        "avatar": bot_instance.user.avatar,
        "nick": getattr(bot_instance.user, "nick", None),
    }
    mock_user = type("MockUser", (), mock_user_data)()
    return MockInteraction(bot_instance, mock_guild, mock_channel, mock_user)


def date_time_to_timestamp(date: datetime.datetime) -> int:
    return int(date.timestamp())


async def upload_image_to_imgbb(image_bytes: bytes, file_extension: str) -> dict[str, Any] | None:
    clean_extension, temp_file_path = file_extension.lstrip("."), ""
    if not ImgBBApiKey:
        print("ImgBB API Key not configured.")
        return None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix="." + clean_extension, mode="wb") as temp_f:
            temp_f.write(image_bytes)
            temp_file_path = temp_f.name
        async with aiohttp.ClientSession() as session:
            form_data = aiohttp.FormData()
            form_data.add_field("key", ImgBBApiKey)
            if not os.path.exists(temp_file_path):
                print(f"Error: Temp file {temp_file_path} vanished.")
                return None
            with open(temp_file_path, "rb") as f_up:
                form_data.add_field("image", f_up, filename=f"tbg.{clean_extension}")
            async with session.post("https://api.imgbb.com/1/upload", data=form_data) as response:
                if response.status == 200:
                    return await response.json()  # type: ignore[no-any-return]
                else:
                    print(f"ImgBB upload failed. Status: {response.status}, Response: {await response.text()}")
                    return None
    except FileNotFoundError:
        print(f"Error: Temp file {temp_file_path} not found.")
        return None
    except Exception as e:
        print(f"An error occurred during ImgBB upload: {e}")
        return None
    finally:
        if temp_file_path and os.path.exists(temp_file_path):
            try:
                os.remove(temp_file_path)
            except OSError as e:
                print(f"Error deleting temporary file {temp_file_path}: {e}")


async def upload_to_tanjun_logs(content: str) -> str | None:
    if not all([bytebin_url, bytebin_username, bytebin_password]):
        print("Bytebin config missing.")
        return None
    try:
        compressed_content = gzip.compress(content.encode("utf-8"))
        url, username, password = str(bytebin_url), str(bytebin_username), str(bytebin_password)
        async with aiohttp.ClientSession() as session:
            auth, headers = (
                aiohttp.BasicAuth(username, password),
                {"Content-Type": "application/octet-stream", "Content-Encoding": "gzip"},
            )
            post_url = url.rstrip("/") + "/post"
            async with session.post(post_url, data=compressed_content, headers=headers, auth=auth) as response:
                if response.status == 201:
                    try:
                        resp_data = await response.json()
                        if "key" in resp_data and isinstance(resp_data["key"], str):
                            return f"{url.rstrip('/')}/{resp_data['key']}"
                        print(f"Bytebin: 'key' not found/string in response: {resp_data}")
                        return None
                    except aiohttp.ContentTypeError:
                        key_text = await response.text()
                        if key_text:
                            return f"{url.rstrip('/')}/{key_text.strip()}"
                        print(f"Bytebin: 201 but not JSON and no text key: {await response.text()}")
                        return None
                else:
                    print(f"Bytebin upload failed. Status: {response.status}, Response: {await response.text()}")
                    return None
    except Exception as e:
        print(f"An error occurred during log upload to Bytebin: {e}")
        return None


def check_if_str_is_hex_color(color_str: str) -> bool:
    processed_color_str = color_str.lstrip("#")
    if not all(c in "0123456789abcdefABCDEF" for c in processed_color_str):
        return False
    return len(processed_color_str) in (3, 6)


def draw_text_with_outline(
    draw: Any,
    position: tuple[int, int],
    text: str,
    font: Any,
    text_color: str | tuple[int, int, int] | tuple[int, int, int, int],
    outline_color: str | tuple[int, int, int] | tuple[int, int, int, int],
) -> None:
    x, y = position
    offset = 1
    for dx in range(-offset, offset + 1):
        for dy in range(-offset, offset + 1):
            if dx == 0 and dy == 0:
                continue
            draw.text((x + dx, y + dy), text, font=font, fill=outline_color)
    draw.text(position, text, font=font, fill=text_color)


def isoTimeToDate(isoTime: str) -> datetime.datetime:
    try:
        return datetime.datetime.fromisoformat(isoTime)
    except ValueError as e:
        print(f"Error parsing ISO time string '{isoTime}': {e}")
        raise


def similar(a: str, b: str) -> float:
    return SequenceMatcher(None, a, b).ratio()


def addThousandsSeparator(number: int | float, separator: str = " ") -> str:
    if isinstance(number, (int, float)):
        return f"{number:,}".replace(",", separator)
    raise TypeError("Input number must be an integer or float.")
