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
from collections.abc import Mapping, Coroutine as ABCCoroutine # For reply in commandInfo
from difflib import SequenceMatcher
from typing import (
    Any,
    Callable,
    Dict,
    List,
    Optional,
    Protocol,
    Self,
    Tuple,
    Union,
    TypeVar,
)

import aiohttp
import discord
from github import Github # type: ignore[import-untyped]
from pyparsing import ( # type: ignore[import-untyped]
    CaselessLiteral,
    Combine,
    Forward,
    Literal,
    Word,
    ZeroOrMore,
    alphas,
    nums,
)
from pyparsing import ( # type: ignore[import-untyped]
    Optional as PyParsingOptional,
)

from config import (
    GithubAuthToken, # str
    ImgBBApiKey, # str
    bytebin_password, # str
    bytebin_url, # str
    bytebin_username, # str
    tenorAPIKey, # str
    tenorCKey, # str
)


class EmbedProxy:
    def __init__(self, layer: Dict[str, Any]):
        self.__dict__.update(layer)

    def __len__(self) -> int:
        return len(self.__dict__)

    def __repr__(self) -> str:
        inner: str = ", ".join((f"{k}={v!r}" for k, v in self.__dict__.items() if not k.startswith("_")))
        return f"EmbedProxy({inner})"

    def __getattr__(self, attr: str) -> Any:
        return self.__dict__.get(attr)

    def __eq__(self, other: object) -> bool:
        return isinstance(other, EmbedProxy) and self.__dict__ == other.__dict__


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

    title: Optional[str]
    url: Optional[str]
    type: str
    _timestamp: Optional[datetime.datetime]
    _colour: Optional[discord.Colour]
    _footer: Dict[str, str] # Stores footer data
    _image: Dict[str, str] # Stores image data
    _thumbnail: Dict[str, str] # Stores thumbnail data
    _video: Dict[str, Any] # Stores video data (can have url, height, width)
    _provider: Dict[str, str] # Stores provider data
    _author: Dict[str, str] # Stores author data
    _fields: List[Dict[str, Any]] # Stores a list of field dictionaries
    description: Optional[str]


    def __init__(
        self,
        *,
        colour: Optional[Union[int, discord.Colour]] = 0xCB33F5, # Hex color
        color: Optional[Union[int, discord.Colour]] = 0xCB33F5, # Hex color
        title: Optional[Any] = None,
        type: str = "rich",
        url: Optional[Any] = None,
        description: Optional[Any] = None,
        timestamp: Optional[datetime.datetime] = None,
    ):
        # Initialize attributes that might not be set by property setters immediately
        self._timestamp = None
        self._colour = None
        self._footer = {}
        self._image = {}
        self._thumbnail = {}
        self._video = {}
        self._provider = {}
        self._author = {}
        self._fields = []

        # Use the property setter for colour
        self.colour: Optional[Union[int, discord.Colour]] = colour if colour is not None else color # Explicitly type self.colour
        self.title = str(title) if title is not None else None
        self.type = type
        self.url = str(url) if url is not None else None
        self.description = str(description) if description is not None else None

        if timestamp is not None:
            self.timestamp: datetime.datetime = timestamp # Explicitly type self.timestamp

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> Self:
        self = cls.__new__(cls)

        # Initialize attributes to their default/empty states
        self.title = None
        self.type = "rich" # Default type
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
        self.type = data.get("type", "rich") # Provide default if not present
        self.description = str(data["description"]) if data.get("description") is not None else None
        self.url = str(data["url"]) if data.get("url") is not None else None


        if "color" in data and data["color"] is not None:
            try:
                self._colour = discord.Colour(value=int(data["color"]))
            except (ValueError, TypeError): # Handle potential errors if color is not a valid int
                 pass # Or log an error, or set a default

        if "timestamp" in data and data["timestamp"] is not None:
            try:
                self._timestamp = discord.utils.parse_time(str(data["timestamp"]))
            except Exception: # Catch more general exceptions from parse_time
                pass # Or log an error

        # For these attributes, we expect dictionaries or lists of dictionaries
        # If the data from `data[attr]` is not in the expected format,
        # it might lead to issues later. Consider adding validation or try-except blocks.
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
        for field in getattr(self, "_fields", []): # field is a dict
            total += len(str(field.get("name", ""))) + len(str(field.get("value", "")))

        try:
            footer_text: Optional[str] = self._footer.get("text")
            if footer_text:
                total += len(footer_text)
        except AttributeError: # _footer might not be initialized if from_dict had missing keys
            pass


        try:
            author_name: Optional[str] = self._author.get("name")
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
                self.colour, # Property access
                self.fields, # Property access
                self.timestamp, # Property access
                self.author, # Property access
                self.thumbnail, # Property access
                self.footer, # Property access
                self.image, # Property access
                self.provider, # Property access
                self.video, # Property access
            )
        )

    def __eq__(self, other: object) -> bool: # Changed from discord.Embed to object for broader comparison
        if not isinstance(other, tanjunEmbed): # Compare with tanjunEmbed
            return NotImplemented # Or False, depending on desired behavior

        # Comparing internal dicts directly can be problematic if order or exact types differ.
        # It's often better to compare the significant attributes.
        return self.to_dict() == other.to_dict()


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
            # It's good practice to ensure _colour is always a discord.Colour or None
            # If an invalid type is passed, either raise an error or set to None/default
            self._colour = None # Or raise TypeError
            # raise TypeError(f"Expected discord.Colour, int, or None but received {value.__class__.__name__} instead.")


    color = colour

    @property
    def timestamp(self) -> Optional[datetime.datetime]:
        return getattr(self, "_timestamp", None)

    @timestamp.setter
    def timestamp(self, value: Optional[datetime.datetime]) -> None:
        if isinstance(value, datetime.datetime):
            if value.tzinfo is None:
                self._timestamp = value.astimezone() # Make it timezone-aware
            else:
                self._timestamp = value
        elif value is None:
            self._timestamp = None
        else:
            self._timestamp = None # Or raise TypeError
            # raise TypeError(f"Expected datetime.datetime or None received {value.__class__.__name__} instead")

    @property
    def footer(self) -> _EmbedFooterProxy:
        return EmbedProxy(getattr(self, "_footer", {})) # type: ignore[return-value]

    def set_footer(self, *, text: Optional[Any] = None, icon_url: Optional[Any] = None) -> Self:
        self._footer = {}
        if text is not None:
            self._footer["text"] = str(text)

        if icon_url is not None:
            self._footer["icon_url"] = str(icon_url)

        return self

    def remove_footer(self) -> Self:
        self._footer = {} # Reset to empty dict
        return self

    @property
    def image(self) -> _EmbedMediaProxy:
        return EmbedProxy(getattr(self, "_image", {})) # type: ignore[return-value]

    def set_image(self, *, url: Optional[Any]) -> Self:
        if url is None:
            self._image = {} # Reset to empty dict
        else:
            self._image = {
                "url": str(url),
            }
        return self

    @property
    def thumbnail(self) -> _EmbedMediaProxy:
        return EmbedProxy(getattr(self, "_thumbnail", {})) # type: ignore[return-value]

    def set_thumbnail(self, *, url: Optional[Any]) -> Self:
        if url is None:
            self._thumbnail = {} # Reset to empty dict
        else:
            self._thumbnail = {
                "url": str(url),
            }
        return self

    @property
    def video(self) -> _EmbedVideoProxy:
        return EmbedProxy(getattr(self, "_video", {})) # type: ignore[return-value]

    @property
    def provider(self) -> _EmbedProviderProxy:
        return EmbedProxy(getattr(self, "_provider", {})) # type: ignore[return-value]

    @property
    def author(self) -> _EmbedAuthorProxy:
        return EmbedProxy(getattr(self, "_author", {})) # type: ignore[return-value]

    def set_author(self, *, name: Any, url: Optional[Any] = None, icon_url: Optional[Any] = None) -> Self:
        self._author = {
            "name": str(name),
        }
        if url is not None:
            self._author["url"] = str(url)
        if icon_url is not None:
            self._author["icon_url"] = str(icon_url)
        return self

    def remove_author(self) -> Self:
        self._author = {} # Reset to empty dict
        return self

    @property
    def fields(self) -> List[_EmbedFieldProxy]:
        return [EmbedProxy(d) for d in getattr(self, "_fields", [])] # type: ignore[return-value,misc]

    def add_field(self, *, name: Any, value: Any, inline: bool = True) -> Self:
        field: Dict[str, Any] = { # Explicitly type `field`
            "inline": inline,
            "name": str(name),
            "value": str(value),
        }
        if not hasattr(self, "_fields") or not isinstance(self._fields, list):
            self._fields = []
        self._fields.append(field)
        return self

    def insert_field_at(self, index: int, *, name: Any, value: Any, inline: bool = True) -> Self:
        field: Dict[str, Any] = { # Explicitly type `field`
            "inline": inline,
            "name": str(name),
            "value": str(value),
        }
        if not hasattr(self, "_fields") or not isinstance(self._fields, list):
            self._fields = [] # Initialize if not present

        # Ensure index is within bounds for insertion
        if 0 <= index <= len(self._fields):
            self._fields.insert(index, field)
        elif index < 0: # Handle negative index if desired, or raise error
            self._fields.insert(0, field) # Example: insert at beginning for any negative
        else: # index > len(self._fields)
            self._fields.append(field) # Example: append if index is too large
        return self

    def clear_fields(self) -> Self:
        self._fields = []
        return self

    def remove_field(self, index: int) -> Self:
        try:
            if hasattr(self, "_fields") and isinstance(self._fields, list):
                del self._fields[index]
        except IndexError: # Catch only IndexError
            pass
        return self

    def set_field_at(self, index: int, *, name: Any, value: Any, inline: bool = True) -> Self:
        if not hasattr(self, "_fields") or not isinstance(self._fields, list):
            raise IndexError("field index out of range, fields list not initialized")
        try:
            field_to_modify: Dict[str, Any] = self._fields[index] # Explicitly type
            field_to_modify["name"] = str(name)
            field_to_modify["value"] = str(value)
            field_to_modify["inline"] = inline
        except IndexError:
            raise IndexError("field index out of range")
        return self

    def to_dict(self) -> Dict[str, Any]: # Return type is a dictionary, similar to discord.EmbedData
        result: Dict[str, Any] = {}

        # Add attributes from __slots__ if they exist and start with '_'
        for key in self.__slots__:
            if key.startswith("_") and hasattr(self, key):
                # Ensure the attribute is not None or empty before adding
                attr_value = getattr(self, key)
                if attr_value is not None and (not isinstance(attr_value, (dict, list)) or attr_value):
                    result[key[1:]] = attr_value # Remove leading underscore

        # Handle specific transformations
        if self._colour is not None:
            result["color"] = self._colour.value
        else:
            result.pop("colour", None) # Remove if it was added from slots and is None

        if self._timestamp is not None:
            ts = self._timestamp
            if ts.tzinfo:
                result["timestamp"] = ts.astimezone(tz=datetime.timezone.utc).isoformat()
            else:
                # Assuming naive datetime is UTC, or local and needs conversion
                result["timestamp"] = ts.replace(tzinfo=datetime.timezone.utc).isoformat()
        else:
            result.pop("timestamp", None)


        # Add top-level attributes if they have values
        if self.type:
            result["type"] = self.type
        if self.description:
            result["description"] = self.description
        if self.url:
            result["url"] = self.url
        if self.title:
            result["title"] = self.title

        # Ensure fields are correctly formatted if they exist
        if "_fields" in result and result["_fields"]:
            result["fields"] = result.pop("_fields")
        elif not getattr(self, "_fields", []): # If _fields is empty or None, remove from dict
            result.pop("fields", None)


        return result


class commandInfo:
    def __init__(
        self,
        user: discord.abc.User, # More specific than discord.User if it's from abc
        channel: discord.abc.GuildChannel,
        guild: discord.Guild,
        command: discord.app_commands.Command[Any, ..., Any], # Generic types for Command
        locale: str,
        message: discord.Message,
        permissions: discord.Permissions,
        reply: ABCCoroutine[Any, Any, discord.Message], # Coroutine that returns a Message
        client: discord.Client,
    ):
        self.user: discord.abc.User = user
        self.channel: discord.abc.GuildChannel = channel
        self.guild: discord.Guild = guild
        self.command: discord.app_commands.Command[Any, ..., Any] = command
        self.locale: str = locale
        self.message: discord.Message = message
        self.permissions: discord.Permissions = permissions
        self.reply: ABCCoroutine[Any, Any, discord.Message] = reply
        self.client: discord.Client = client


def cmp(a: Union[int, float], b: Union[int, float]) -> int: # Can compare floats too
    return (a > b) - (a < b)


class NumericStringParser:
    def __init__(self) -> None:
        self.exprStack: List[Any] = [] # Stack can hold numbers or operator strings
        self.bnf: Forward = self._setup_parser() # Setup parser in a separate method

        # Function map: Keys are strings, values are callable math functions
        self.fn: Dict[str, Callable[..., Union[float, int]]] = {
            "sin": math.sin, "cos": math.cos, "tan": math.tan,
            "asin": math.asin, "acos": math.acos, "atan": math.atan,
            "sinh": math.sinh, "cosh": math.cosh, "tanh": math.tanh,
            "asinh": math.asinh, "acosh": math.acosh, "atanh": math.atanh,
            "log": math.log, "log10": math.log10, "log2": math.log2,
            "exp": math.exp, "abs": abs, "trunc": math.trunc,
            "round": round, "sgn": lambda a: (abs(a) > 1e-12 and cmp(a, 0)) or 0, # type: ignore
            "sqrt": math.sqrt, "factorial": math.factorial, "degrees": math.degrees,
            "radians": math.radians, "ceil": math.ceil, "floor": math.floor,
            "pi": lambda: math.pi, "e": lambda: math.e, # Constants as 0-arg functions
            "fac": math.factorial,
        }

        # Operator map: Keys are operator strings, values are callable operators
        self.opn: Dict[str, Callable[[Union[float, int], Union[float, int]], Union[float, int]]] = {
            "+": operator.add, "-": operator.sub, "*": operator.mul,
            "/": operator.truediv, "^": operator.pow,
        }

    def _setup_parser(self) -> Forward:
        # Define grammar elements for parsing numeric strings
        point = Literal(".")
        e_literal = CaselessLiteral("E") # Renamed to avoid conflict with math.e
        # Ensure fnumber captures scientific notation correctly
        fnumber = Combine(Word("+-" + nums, nums) +
                          PyParsingOptional(point + PyParsingOptional(Word(nums))) +
                          PyParsingOptional(e_literal + Word("+-" + nums, nums)))
        ident = Word(alphas, alphas + nums + "_$")

        plus, minus, mult, div = map(Literal, "+-*/")
        lpar, rpar = map(Literal, "()")
        addop = plus | minus
        multop = mult | div
        expop = Literal("^")

        expr = Forward()
        # Atom can be a number, an identifier (function/constant), or a parenthesized expression
        # Need to handle function calls like ident(expr)
        # For now, assuming ident is a constant like 'pi' or 'e' if not followed by '('
        atom_contents = (
            (PyParsingOptional("-") + (ident + lpar + expr + rpar).setParseAction(self.pushFunctionCall) | fnumber)
        ).setParseAction(self.pushFirst) | \
        (lpar + expr.suppress() + rpar).setParseAction(self.pushUMinus) # This was original atom

        atom = PyParsingOptional(Literal("-")).setParseAction(self.pushUMinusSign) + \
               ( (ident + lpar + expr + rpar).setParseAction(self.pushFunctionCall) | \
                 ident.setParseAction(self.pushFirst) | \
                 fnumber.setParseAction(self.pushFirst) | \
                 (lpar + expr + rpar) )


        factor = Forward()
        factor << atom + ZeroOrMore((expop + factor).setParseAction(self.pushOperator))

        term = factor + ZeroOrMore((multop + factor).setParseAction(self.pushOperator))
        expr << term + ZeroOrMore((addop + term).setParseAction(self.pushOperator))

        return expr

    def pushFirst(self, s: str, loc: int, toks: List[str]) -> None: # s, loc, toks are standard pyparsing args
        self.exprStack.append(toks[0])

    def pushUMinus(self, s: str, loc: int, toks: List[str]) -> None:
        # This is for expressions like -(expr)
        if toks and toks[0] == '-': # Should check the token that indicates unary minus
            self.exprStack.append("unary -")
        # If it's just grouping like (expr), toks might be empty or contain the expr result
        # The original logic might need adjustment based on how pyparsing handles this.

    def pushUMinusSign(self, s: str, loc: int, toks: List[str]) -> None:
        # This is for when a '-' is parsed before a number/identifier
        if toks and toks[0] == '-':
            self.exprStack.append("unary -") # Push an indicator for unary minus

    def pushOperator(self, s: str, loc: int, toks: List[str]) -> None:
        self.exprStack.append(toks[0]) # Assuming the operator is the first token in the group


    def pushFunctionCall(self, s: str, loc: int, toks: List[str]) -> None:
        self.exprStack.append(toks[0]) # Push function name


    def evaluateStack(self, s: List[Any]) -> Union[float, int]: # Stack s
        if not s:
            raise ValueError("Evaluation stack is empty.")
        op: Any = s.pop() # op can be a number, operator string, or function name string

        if op == "unary -":
            if not s: raise ValueError("Stack empty for unary minus operand.")
            return -self.evaluateStack(s) # Recursive call for the operand
        elif isinstance(op, str) and op in self.opn: # Binary operator
            if len(s) < 2: raise ValueError(f"Stack needs two operands for operator {op}.")
            op2: Union[float, int] = self.evaluateStack(s) # op2 is popped first
            op1: Union[float, int] = self.evaluateStack(s) # op1 is popped next
            return self.opn[op](op1, op2)
        elif isinstance(op, str) and op in self.fn: # Function call
            func: Callable[..., Union[float, int]] = self.fn[op]
            # Determine number of arguments from function signature if possible, or assume fixed arity
            # For simplicity, let's assume functions take one argument unless they are constants
            if op in ["pi", "e"]: # 0-argument functions (constants)
                return func()
            else: # Assume 1-argument functions for now
                if not s: raise ValueError(f"Stack empty for argument to function {op}.")
                arg: Union[float, int] = self.evaluateStack(s)
                return func(arg) # type: ignore # We assume correct arity here
        elif isinstance(op, (int, float)): # If op is already a number
            return op
        elif isinstance(op, str): # Could be a number string from fnumber
            try:
                return float(op) # Try to convert to float
            except ValueError:
                raise Exception(f"Invalid token or identifier on stack: {op}")
        else:
            raise Exception(f"Unexpected item on stack: {op} of type {type(op)}")


    def eval(self, num_string: str, parseAll: bool = True) -> Union[float, int]:
        self.exprStack = []
        try:
            self.bnf.parseString(num_string, parseAll=parseAll)
        except Exception as e: # Catch pyparsing exceptions
            raise ValueError(f"Error parsing expression '{num_string}': {e}")

        if not self.exprStack:
            # Handle cases like empty string or string that parses to nothing
            # Or if parseString didn't populate exprStack due to parse actions
            raise ValueError(f"Expression '{num_string}' did not yield a calculable stack.")

        try:
            val: Union[float, int] = self.evaluateStack(self.exprStack[:]) # Evaluate a copy
            return val
        except ValueError as e: # Catch errors from evaluateStack (e.g. stack underflow)
            raise ValueError(f"Error evaluating expression '{num_string}': {e}")
        except Exception as e: # Catch other unexpected errors during evaluation
            raise Exception(f"Unexpected error evaluating '{num_string}': {e}")


async def getGif(query: str, amount: int = 1, limit: int = 10) -> List[str]:
    async with aiohttp.ClientSession() as session:

        async def fetch(url: str) -> Optional[Dict[str, Any]]: # Return type is a dict or None
            async with session.get(url) as response:
                if response.status != 200:
                    # Log error or handle non-200 status
                    print(f"Tenor API request failed with status {response.status} for URL: {url}")
                    return None
                try:
                    return await response.json() # type: ignore # Assuming response.json() returns Dict[str, Any]
                except aiohttp.ContentTypeError:
                    # Log error if response is not JSON
                    print(f"Tenor API response was not JSON for URL: {url}. Response text: {await response.text()}")
                    return None


        request_url: str = f"https://tenor.googleapis.com/v2/search?q={query}&key={tenorAPIKey}&client_key={tenorCKey}&limit={limit}"
        r: Optional[Dict[str, Any]] = await fetch(request_url)


        if r is None or "results" not in r or not isinstance(r["results"], list):
            return [] # Return empty list if results are not as expected

        results_list: List[Dict[str, Any]] = r["results"]
        if not results_list:
            return []

        random.shuffle(results_list)

        gifs_found: List[str] = []
        for i in range(min(amount, len(results_list))): # Ensure we don't go out of bounds
            try:
                # Navigate the dictionary carefully
                media_formats = results_list[i].get("media_formats")
                if media_formats and isinstance(media_formats, dict):
                    medium_gif = media_formats.get("mediumgif")
                    if medium_gif and isinstance(medium_gif, dict):
                        url = medium_gif.get("url")
                        if isinstance(url, str):
                            gifs_found.append(url)
            except (KeyError, TypeError, AttributeError) as e:
                # Log error if the structure is not as expected
                print(f"Error processing Tenor result item: {results_list[i]}. Error: {e}")
                continue # Skip this item

        return gifs_found


def get_highest_exponent(polynomial: str) -> int:
    polynomial = polynomial.replace(" ", "")
    term_pattern = re.compile(r"([+-]?\d*\.?\d*)(x(?:(?:\^)(\d+))?)?")

    terms: List[Tuple[str, str, str, str]] = term_pattern.findall(polynomial)

    highest_exponent: int = 0

    for term_match in terms:

        coefficient_str, x_part, _, exponent_str = term_match

        if not coefficient_str and not x_part: # Skip empty matches (e.g. from multiple signs)
            continue

        if x_part: # If 'x' is present in the term
            if exponent_str: # If there's an explicit exponent (e.g., x^2, x^5)
                try:
                    current_exponent = int(exponent_str)
                    highest_exponent = max(highest_exponent, current_exponent)
                except ValueError:
                    pass # Should not happen if regex is correct
            elif 'x' in x_part: # If 'x' is present but no '^' (e.g., 'x', implies x^1)
                highest_exponent = max(highest_exponent, 1)
        # If no 'x' part (e.g., a constant like "5"), its exponent regarding x is 0.
        # `highest_exponent` initialized to 0 handles this.

    return highest_exponent


def checkIfHasPro(guildid: int) -> bool:
    # Placeholder logic, actual implementation would check a database or config
    if guildid == 0: # Example: 0 is not a valid guild ID for pro
        return False
    # In a real scenario, you might query a database:
    # return db.is_guild_pro(guildid)
    return True # Default to true for placeholder


def checkIfhasPlus(userid: int) -> bool:
    # Placeholder logic
    if userid == 0: # Example: 0 is not a valid user ID for plus
        return False
    # return db.is_user_plus(userid)
    return True # Default to true for placeholder


def missingLocalization(locale: str) -> None:
    try:
        g: Github = Github(GithubAuthToken) # type: ignore[no-untyped-call]
        repo = g.get_repo("TanjunBot/new_tanjun") # type: ignore[no-untyped-call]
        label = repo.get_label("missing localization") # type: ignore[no-untyped-call]
        repo.create_issue( # type: ignore[no-untyped-call]
            title=f"Missing localization for {locale}", # Use f-string for clarity
            body=f"Missing localization for {locale}",
            labels=[label],
        )
    except Exception as e:
        # Log the error, as this function failing should not crash the bot
        print(f"Error creating GitHub issue for missing localization '{locale}': {e}")


def addFeedback(content: str, author: str) -> None:
    try:
        g: Github = Github(GithubAuthToken) # type: ignore[no-untyped-call]
        repo = g.get_repo("TanjunBot/new_tanjun") # type: ignore[no-untyped-call]
        label = repo.get_label("Feedback") # type: ignore[no-untyped-call]
        repo.create_issue( # type: ignore[no-untyped-call]
            title=f"Feedback from {author}", # More descriptive title
            body=f"# Feedback from {author}:\n\n{content}", # Ensure markdown formatting for body
            labels=[label],
        )
    except Exception as e:
        print(f"Error creating GitHub issue for feedback from '{author}': {e}")


# Type for the lambda functions used in LEVEL_SCALINGS
LevelScalingFunc = Callable[[int], float] # Takes level (int), returns XP (float before floor)

LEVEL_SCALINGS: Dict[str, LevelScalingFunc] = {
    "easy": lambda level: 100 * level,
    "medium": lambda level: 100 * (level**1.5),
    "hard": lambda level: 100 * (level**2),
    "extreme": lambda level: 100 * (level**2.5),
}

# Type for operators dictionary
OperatorFunc = Callable[[Any, Any], Any] # Generic for binary operators
UnaryOperatorFunc = Callable[[Any], Any] # Generic for unary operators

operators_map: Dict[type, Union[OperatorFunc, UnaryOperatorFunc]] = { # Renamed to avoid conflict
    ast.Add: op.add, ast.Sub: op.sub, ast.Mult: op.mul,
    ast.Div: op.truediv, ast.Pow: op.pow, ast.BitXor: op.xor,
    ast.USub: op.neg, ast.Mod: op.mod,
}


def sqrt_n(x: float, n: float = 2.0) -> float: # n should also be float for consistency
    if n == 0:
        raise ValueError("The root degree n cannot be zero.")
    if x < 0 and n % 2 == 0: # Even root of a negative number
        # Or return float('nan') or handle as per requirements
        raise ValueError("Cannot compute even root of a negative number with real numbers.")
    return x ** (1.0 / n)


def log_n(x: float, base: float = math.e) -> float:
    if x <= 0:
        raise ValueError("Logarithm undefined for non-positive values.")
    if base <= 0 or base == 1:
        raise ValueError("Logarithm base must be positive and not equal to 1.")
    return math.log(x, base)


# Variables dict for eval_expr and eval_
VariablesType = Dict[str, Union[float, int, Callable[..., Any]]]


def eval_expr(expr: str, variables: Optional[VariablesType] = None) -> Union[float, int, complex]: # Can return complex
    if variables is None:
        variables = {}

    # Augment variables with math functions and constants for security and control
    # This local_vars will be passed to the actual eval_ function.
    local_vars: VariablesType = {
        "pi": math.pi, "e": math.e,
        "sin": math.sin, "cos": math.cos, "tan": math.tan,
        "asin": math.asin, "acos": math.acos, "atan": math.atan,
        "log": log_n, # Use our safe log_n
        "log10": lambda x: log_n(x, 10),
        "log2": lambda x: log_n(x, 2),
        "ln": lambda x: log_n(x, math.e),
        "sqrt": sqrt_n, # Use our safe sqrt_n
        "nthroot": sqrt_n,
        "abs": abs, "floor": math.floor, "ceil": math.ceil,
        "pow": pow,
        # Add other functions/constants as needed
    }
    local_vars.update(variables) # User-provided variables can override defaults if names clash

    try:
        # Ensure the expression is safe before parsing
        # (This is a complex topic, ast.parse itself doesn't execute code)
        parsed_ast = ast.parse(expr, mode="eval").body
        return eval_(parsed_ast, local_vars)
    except SyntaxError as e:
        raise ValueError(f"Syntax error in expression: {expr}. Details: {e}")
    except TypeError as e: # Catch type errors from operations (e.g. unsupported operand types)
        raise ValueError(f"Type error during evaluation of: {expr}. Details: {e}")
    except NameError as e: # Catch undefined variables/functions
        raise NameError(f"Name error in expression: {expr}. Details: {e}")
    except Exception as e: # Catch-all for other evaluation errors
        # Log this error with more detail for debugging
        print(f"Unexpected error evaluating expression '{expr}': {type(e).__name__}: {e}")
        raise


def eval_(node: ast.AST, variables: VariablesType) -> Union[float, int, complex]: # Can return complex
    if isinstance(node, ast.Num): # Deprecated in Python 3.8, use ast.Constant
        return node.n # type: ignore
    elif isinstance(node, ast.Constant): # For Python 3.8+
        return node.value # type: ignore
    elif isinstance(node, ast.BinOp):
        left_val = eval_(node.left, variables)
        right_val = eval_(node.right, variables)
        op_type = type(node.op)
        if op_type in operators_map:
            return operators_map[op_type](left_val, right_val) # type: ignore
        raise TypeError(f"Unsupported binary operator: {op_type}")
    elif isinstance(node, ast.UnaryOp):
        operand_val = eval_(node.operand, variables)
        op_type = type(node.op)
        if op_type in operators_map:
            return operators_map[op_type](operand_val) # type: ignore
        raise TypeError(f"Unsupported unary operator: {op_type}")
    elif isinstance(node, ast.Call):
        func_name_node = node.func
        # Resolve function name
        func_to_call: Optional[Callable[..., Any]] = None
        if isinstance(func_name_node, ast.Name): # e.g. my_func(...)
            if func_name_node.id in variables:
                func_to_call = variables[func_name_node.id]
            else:
                raise NameError(f"Function '{func_name_node.id}' is not defined in variables.")
        # Add ast.Attribute if you want to support obj.method(...) from variables
        # elif isinstance(func_name_node, ast.Attribute):
            # ... logic to get method from object in variables ...

        if not func_to_call or not callable(func_to_call):
            func_id_str = ast.dump(func_name_node) # Get a string representation for error
            raise TypeError(f"'{func_id_str}' is not a callable function.")

        args = [eval_(arg, variables) for arg in node.args]
        # Handle keywords if your functions use them:
        # kwargs = {kw.arg: eval_(kw.value, variables) for kw in node.keywords}
        try:
            return func_to_call(*args) # Add **kwargs if handling keywords
        except TypeError as e: # Mismatch in arguments
            raise TypeError(f"Error calling function '{getattr(func_to_call, '__name__', 'unknown_func')}': {e}")

    elif isinstance(node, ast.Name): # Variable lookup
        if node.id in variables:
            val = variables[node.id]
            if callable(val): # If a variable holds a function, it should be called via ast.Call
                raise TypeError(f"Variable '{node.id}' holds a function but was not called. Use {node.id}(...).")
            return val
        raise NameError(f"Variable '{node.id}' is not defined.")
    else:
        raise TypeError(f"Unsupported AST node type: {type(node).__name__}")


def get_xp_for_level(level: int, scaling: str, custom_formula: Optional[str] = None) -> int:
    if level <= 0:
        return 0

    result: Union[float, int, complex] # Can be complex from eval_expr

    if scaling == "custom" and custom_formula:
        try:
            # Pass 'level' as a variable to eval_expr
            result = eval_expr(custom_formula, variables={"level": level})
        except (ValueError, NameError, TypeError, Exception) as e: # Catch specific errors from eval_expr
            # Log the error for debugging the custom formula
            print(f"Error evaluating custom XP formula '{custom_formula}' for level {level}: {e}")
            return 0  # Return 0 or handle error appropriately
    elif scaling in LEVEL_SCALINGS:
        result = LEVEL_SCALINGS[scaling](level)
    else: # Default scaling if 'scaling' key is invalid
        print(f"Warning: Unknown XP scaling '{scaling}'. Using 'medium'.")
        result = LEVEL_SCALINGS["medium"](level)

    if isinstance(result, complex):
        # Decide how to handle complex results (e.g., take real part, error, or return 0)
        print(f"Warning: Custom XP formula resulted in a complex number ({result}). Using real part or 0.")
        return math.floor(result.real) if result.real is not None else 0
    elif isinstance(result, (float, int)):
        if math.isinf(result) or math.isnan(result):
            print(f"Warning: XP calculation resulted in {result}. Returning 0.")
            return 0
        return math.floor(result)
    else:
        # Should not happen if eval_expr and LEVEL_SCALINGS return numeric types
        print(f"Warning: XP calculation resulted in non-numeric type: {type(result)}. Returning 0.")
        return 0


def get_level_for_xp(xp: int, scaling: str, custom_formula: Optional[str] = None) -> int:
    if xp < 0: return 0 # XP cannot be negative for level calculation

    # Optimization: if xp is 0, level is 0 (or 1, depending on system, assuming 0 here)
    if xp == 0:
        xp_for_level_1 = get_xp_for_level(1, scaling, custom_formula)
        if xp < xp_for_level_1 : # If XP for level 1 is > 0, then 0 XP means level 0.
            return 0
        # If XP for level 1 is 0 (e.g. bad formula), this needs careful handling.
        # For now, assume get_xp_for_level(1, ...) > 0 for valid setups.


    # Binary search for the level
    # Max level can be quite high, adjust if necessary
    # Low starts at 1 because level 0 is handled, or if get_xp_for_level(0) is base.
    low: int = 1
    # Estimate a reasonable high bound. If XP scales quadratically (hard),
    # level ~ sqrt(xp/100). For 10^9 XP, level ~ sqrt(10^7) ~ 3162.
    # For level**2.5, level ~ (xp/100)**(1/2.5). For 10^9 XP, level ~ (10^7)**0.4 ~ 630.
    # A high cap like 20000 should be safe for most practical XP values.
    # If custom formulas can yield very low XP per level, this might need adjustment or a dynamic high.
    high: int = 200000 # Increased upper bound for safety with various formulas
    level: int = 0 # Stores the highest level found so far whose XP requirement is <= current XP

    # We are looking for the highest level 'L' such that get_xp_for_level(L) <= xp
    # And get_xp_for_level(L+1) > xp

    # Edge case: If XP is less than XP needed for level 1, level is 0.
    xp_for_lvl_1 = get_xp_for_level(1, scaling, custom_formula)
    if xp < xp_for_lvl_1:
        return 0 # Or 1 if level 1 is the minimum displayable level with 0 XP.

    # Binary search for the level
    # `ans` will store the highest level `l` such that `get_xp_for_level(l) <= xp`
    ans: int = 0
    search_low: int = 1
    search_high: int = high # Use the defined high cap

    while search_low <= search_high:
        mid: int = (search_low + search_high) // 2
        if mid == 0 : # Should not happen if search_low starts at 1
            search_low = 1
            continue
        xp_needed_for_mid: int = get_xp_for_level(mid, scaling, custom_formula)

        if xp_needed_for_mid <= xp:
            # `mid` is a possible level, try for a higher one
            ans = mid
            search_low = mid + 1
        else:
            # `mid` is too high, try a lower one
            search_high = mid - 1
    return ans


def relativeTimeStrToDate(time_string: str) -> datetime.datetime:
    if not time_string.strip(): # Check if string is empty or whitespace
        return datetime.datetime.now(datetime.timezone.utc) # Use timezone-aware now

    # Regular expression to match time units like "1d", "2h", "30m", "10s"
    pattern = r"(\d+)\s*([smhd])" # Optional space after number
    matches: List[Tuple[str, str]] = re.findall(pattern, time_string.lower())

    if not matches:
        # Could raise ValueError or return now() if no valid units found
        # print(f"Warning: No valid time units found in '{time_string}'. Returning current time.")
        return datetime.datetime.now(datetime.timezone.utc)

    delta_kwargs: Dict[str, int] = {"days": 0, "hours": 0, "minutes": 0, "seconds": 0}

    for value_str, unit in matches:
        try:
            value: int = int(value_str)
            if unit == "s":
                delta_kwargs["seconds"] += value
            elif unit == "m":
                delta_kwargs["minutes"] += value
            elif unit == "h":
                delta_kwargs["hours"] += value
            elif unit == "d":
                delta_kwargs["days"] += value
        except ValueError:
            # Should not happen with the regex, but good for safety
            print(f"Warning: Invalid number '{value_str}' in time string '{time_string}'.")
            continue

    delta = datetime.timedelta(**delta_kwargs) # type: ignore # timedelta accepts these kwargs
    return datetime.datetime.now(datetime.timezone.utc) + delta


def relativeTimeToSeconds(time_string: str) -> int:
    if not time_string.strip():
        return 0

    pattern = r"(\d+)\s*([smhd])"
    matches: List[Tuple[str, str]] = re.findall(pattern, time_string.lower())

    if not matches:
        return 0 # Or raise error

    total_seconds: int = 0
    for value_str, unit in matches:
        try:
            value: int = int(value_str)
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


def dateToRelativeTimeStr(date_obj: datetime.datetime) -> str: # Renamed 'date' to 'date_obj'
    # Ensure both dates are timezone-aware for correct comparison, preferably UTC
    now_utc = datetime.datetime.now(datetime.timezone.utc)
    date_obj_utc = date_obj.astimezone(datetime.timezone.utc) if date_obj.tzinfo else date_obj.replace(tzinfo=datetime.timezone.utc)


    delta: datetime.timedelta = date_obj_utc - now_utc

    # If the date is in the past, the delta will be negative.
    # Decide how to represent this (e.g., "ago" or just negative components if desired)
    # For now, let's assume we want positive components for a future date.
    # If date_obj_utc < now_utc, it means it's in the past.
    # The components will be negative or 0.
    # If we want to show "X time ago", we'd use abs(delta).

    if delta.total_seconds() < 0:
        # Handle past dates, e.g., return "in the past" or format with "ago"
        # For this function, let's assume it's for future dates or "now"
        # If we need to show "ago", then: delta = now_utc - date_obj_utc
        return "now" # Or an empty string, or specific "past" marker

    days: int = delta.days
    remaining_seconds: int = delta.seconds # Seconds part of the timedelta (0 to 86399)

    hours: int = remaining_seconds // 3600
    minutes: int = (remaining_seconds % 3600) // 60
    seconds: int = remaining_seconds % 60

    components: List[str] = []
    if days > 0:
        components.append(f"{days}d")
    if hours > 0:
        components.append(f"{hours}h")
    if minutes > 0:
        components.append(f"{minutes}m")
    if seconds > 0: # Only show seconds if it's the smallest unit or other units are zero
        components.append(f"{seconds}s")

    if not components: # If all are zero (date is now or very close)
        return "now"

    return " ".join(components)


class MockInteraction(discord.Interaction): # type: ignore[misc] # discord.Interaction might have type issues with User defined classes
    def __init__(self, bot: discord.Client, guild: discord.Guild, channel: discord.TextChannel, user: discord.User):
        # Mock required data for discord.Interaction constructor
        # This is highly dependent on discord.py's internal structure and might break
        mock_state = bot._connection # type: ignore # Accessing protected member
        mock_data: Dict[str, Any] = {
            "id": discord.utils.snowflake_time(datetime.datetime.now(datetime.timezone.utc)).timestamp() * 1000, # Mock snowflake ID
            "application_id": bot.application_id or 0,
            "type": discord.InteractionType.application_command.value,
            "data": {}, # Mock command data
            "guild_id": guild.id if guild else None,
            "channel_id": channel.id if channel else None,
            # User can be complex, try to mock essential parts or use a real User object if available
            "member": { # If it's a guild interaction
                "user": {"id": user.id, "username": user.name, "discriminator": user.discriminator, "avatar": user.avatar},
                "nick": getattr(user, 'nick', None), "roles": [], "joined_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                "deaf": False, "mute": False
            } if guild and isinstance(user, discord.Member) else None,
            "user": { # If it's a DM interaction or user is not a member
                 "id": user.id, "username": user.name, "discriminator": user.discriminator, "avatar": user.avatar
            } if not (guild and isinstance(user, discord.Member)) else None,
            "token": "mock_interaction_token_xxxxxxxxxxxx", # Must be a valid format if used by discord.py
            "version": 1,
        }
        super().__init__(data=mock_data, state=mock_state) # type: ignore

        # Override attributes as needed, some might be properties
        self._guild = guild # type: ignore
        self._channel = channel # type: ignore
        self._user = user # type: ignore
        # self.locale = "en-US" # Set by super() if not in data
        # self.guild_locale = "en-US" # Set by super() if not in data
        self.client: discord.Client = bot # Already an attribute of Interaction

        # Mock the response object
        self._response_issued: bool = False # Track if response has been issued
        self.response: MockInteractionResponse = MockInteractionResponse(self) # type: ignore

        # Mock followup webhook
        # This is a simplified mock. A real Webhook is more complex.
        # If followup is used extensively, this mock might need to be more detailed.
        # The data for from_state usually comes from the interaction payload itself.
        followup_data = {
            "application_id": str(self.application_id),
            "token": self.token, # Use the token from the interaction
            "id": str(self.id), # Interaction ID
            # Webhook specific fields if needed by from_state, e.g. type, channel_id, guild_id
            "type": 3, # Application command webhook type
            "channel_id": str(channel.id) if channel else None,
            "guild_id": str(guild.id) if guild else None,
        }
        # self.followup = discord.Webhook.from_state(data=followup_data, state=mock_state) # type: ignore
        # For a simpler mock if from_state is problematic:
        self.followup = MockWebhook(state=mock_state, application_id=self.application_id, token=self.token) # type: ignore

    @property # Ensure these are properties if discord.Interaction expects them to be
    def guild(self) -> Optional[discord.Guild]:
        return self._guild # type: ignore

    @property
    def channel(self) -> Optional[discord.abc.MessageableChannel]: # Or more specific channel type
        return self._channel # type: ignore

    @property
    def user(self) -> Optional[Union[discord.User, discord.Member]]:
        return self._user # type: ignore


    async def original_response(self) -> discord.Message: # Should return discord.Message
        if hasattr(self.response, 'message') and self.response.message:
            return self.response.message
        # This might need to fetch the message if discord.py does that
        # For a mock, returning the stored message is usually enough
        raise discord.NotFound("Original response message not found or not sent.")


class MockInteractionResponse(discord.InteractionResponse): # type: ignore[misc]
    def __init__(self, interaction: MockInteraction): # Takes MockInteraction
        super().__init__(interaction) # type: ignore
        self.interaction: MockInteraction = interaction # Store our MockInteraction
        self.message: Optional[discord.Message] = None

    async def send_message(self, content: Optional[str] = None, *, embed: Optional[tanjunEmbed] = None, **kwargs: Any) -> None:
        if self.interaction._response_issued: # type: ignore
            raise discord.InteractionResponded(self.interaction) # type: ignore

        # Simulate sending a message and store it
        # Create a mock discord.Message object
        # This is a simplified Message mock. Real one is more complex.
        message_data: Dict[str, Any] = {
            "id": discord.utils.time_snowflake(datetime.datetime.now(datetime.timezone.utc)),
            "channel_id": self.interaction.channel.id if self.interaction.channel else 0,
            "guild_id": self.interaction.guild.id if self.interaction.guild else None,
            "content": content or "",
            "embeds": [embed.to_dict()] if embed else [],
            "author": { # Mock bot user as author
                "id": self.interaction.client.user.id if self.interaction.client and self.interaction.client.user else 0,
                "username": self.interaction.client.user.name if self.interaction.client and self.interaction.client.user else "MockBot",
                "discriminator": self.interaction.client.user.discriminator if self.interaction.client and self.interaction.client.user else "0000",
                "bot": True,
                "avatar": None,
            },
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "edited_timestamp": None, "tts": False, "mention_everyone": False,
            "mentions": [], "mention_roles": [], "mention_channels": [],
            "attachments": [], "pinned": False, "type": discord.MessageType.default.value,
            "webhook_id": None, # Important for interaction responses
        }
        if self.interaction.channel:
            self.message = discord.Message(state=self.interaction._state, channel=self.interaction.channel, data=message_data) # type: ignore
        else:
            # Cannot create a message without a channel context in discord.py's model
            # This part of the mock might need adjustment based on how it's used
            # For now, let's assume channel is always present for send_message
            print("Warning: MockInteractionResponse.send_message called without a channel.")
            self.message = None # Or raise an error

        self.interaction._response_issued = True # type: ignore
        # In a real scenario, this would make an API call.
        # print(f"Mock: Sent message: content='{content}', embed='{embed is not None}'")

    async def delete_original_response(self) -> None:
        # Simulate deleting the message
        if not self.interaction._response_issued or not self.message: # type: ignore
            # Behavior if no response to delete (discord.py might raise NotFound)
            # print("Mock: No original response to delete.")
            raise discord.NotFound("No original response to delete.") # type: ignore
        # print(f"Mock: Deleted original response (message ID: {self.message.id}).")
        self.message = None
        # This doesn't un-set _response_issued, as an interaction can only be responded to once.
        # Deleting is an action on that response.

    async def defer(self, *, thinking: bool = False, ephemeral: bool = False) -> None:
        if self.interaction._response_issued: # type: ignore
            raise discord.InteractionResponded(self.interaction) # type: ignore
        # print(f"Mock: Interaction deferred (thinking={thinking}, ephemeral={ephemeral}).")
        self.interaction._response_issued = True # type: ignore

    async def edit_message(self, **kwargs: Any) -> None: # Should be edit_original_response?
                                                      # discord.InteractionResponse has edit_message
        if not self.interaction._response_issued or not self.message: # type: ignore
            # print("Mock: No original message to edit.")
            # This should typically raise an error if trying to edit before responding.
            # Or, if it's meant to edit the *original* message that triggered a component interaction,
            # the logic is different. Assuming it edits the message sent by send_message.
            raise discord.HTTPException(None, "Cannot edit a message that has not been sent.") # type: ignore

        # Simulate editing the stored message
        content = kwargs.get("content")
        embed = kwargs.get("embed")
        if content is not None and self.message:
            self.message.content = content # type: ignore
        if embed is not None and self.message: # embed can be None to remove it
            self.message.embeds = [embed.to_dict()] if embed else [] # type: ignore
        elif "embed" in kwargs and kwargs["embed"] is None and self.message: # Explicitly removing embed
             self.message.embeds = [] # type: ignore

        # print(f"Mock: Edited message (ID: {self.message.id if self.message else 'N/A'}). New content='{content}', new embed='{embed is not None}'")


# Simplified Mock Webhook for followup
class MockWebhook:
    def __init__(self, state: Any, application_id: int, token: str):
        self._state = state
        self.application_id: int = application_id
        self.token: str = token
        self.id: int = 0 # Mock webhook ID

    async def send(self, content: Optional[str] = None, *, embed: Optional[tanjunEmbed] = None, **kwargs: Any) -> discord.Message:
        # Simulate sending a followup message
        # print(f"Mock Webhook: Sent followup: content='{content}', embed='{embed is not None}'")
        # Return a mock message
        message_data: Dict[str, Any] = {
            "id": discord.utils.time_snowflake(datetime.datetime.now(datetime.timezone.utc)),
            "channel_id": 0, # Followups might not have a channel in the same way
            "content": content or "",
            "embeds": [embed.to_dict()] if embed else [],
            "author": {"id": self.application_id, "username": "MockApp", "discriminator": "0000", "bot": True, "avatar": None},
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "webhook_id": str(self.id), # Should be the webhook's ID
             # ... other necessary message fields
        }
        # This is tricky because a Message needs a channel and state.
        # For a deep mock, you'd need to simulate this more accurately.
        # For a shallow mock, just returning a dict or a very basic object might suffice.
        # However, if the code *uses* the returned Message object's methods/attributes, it needs to be more complete.
        # Let's assume for now that a very basic object is enough, or that the user
        # will adapt this mock further if needed.
        # This will likely fail if the calling code expects a full discord.Message from a webhook.
        # A more robust mock would create a Message with a mock channel or handle this.
        # For now, raising NotImplementedError or returning a very basic mock.
        # raise NotImplementedError("MockWebhook.send returning a full discord.Message is complex to mock simply.")
        # A slightly better mock:
        mock_msg = discord.Message(state=self._state, channel=None, data=message_data) # type: ignore # channel=None is problematic
        return mock_msg # type: ignore

    async def edit_message(self, message_id: int, **kwargs: Any) -> discord.Message:
        # print(f"Mock Webhook: Edited message {message_id} with {kwargs}")
        # Return a mock message
        # Similar complexity as send() for returning a realistic Message object.
        raise NotImplementedError("MockWebhook.edit_message not fully implemented for returning discord.Message.")

    async def delete_message(self, message_id: int) -> None:
        # print(f"Mock Webhook: Deleted message {message_id}")
        pass


def create_mock_interaction(bot_instance: discord.Client) -> MockInteraction: # Parameter name changed for clarity
    # Ensure the bot is connected and has guilds/channels
    if not bot_instance.guilds:
        raise ValueError("Bot is not connected to any guilds to create a mock interaction.")
    guild: discord.Guild = bot_instance.guilds[0]

    if not guild.text_channels:
        raise ValueError(f"Guild '{guild.name}' has no text channels for mock interaction.")
    channel: discord.TextChannel = guild.text_channels[0] # type: ignore # Ensure it's a TextChannel

    # Use the bot's own user, or a mock user if needed
    user: Optional[discord.ClientUser] = bot_instance.user
    if not user:
        raise ValueError("Bot has no user object (not logged in fully?).")

    return MockInteraction(bot_instance, guild, channel, user) # type: ignore


def date_time_to_timestamp(date: datetime.datetime) -> int:
    # Ensures the datetime is offset-aware, assuming UTC if naive.
    if date.tzinfo is None:
        # Assuming naive datetime is in local time, convert to UTC then timestamp
        # Or, if naive datetime is intended as UTC: date = date.replace(tzinfo=datetime.timezone.utc)
        # For consistency, let's assume naive should be treated as local and converted.
        # However, timestamp() on naive datetime uses local system timezone, which might be desired.
        # If UTC is always the target for naive, uncomment the replace line.
        # date = date.replace(tzinfo=datetime.timezone.utc) # If naive is UTC
        pass # .timestamp() on naive uses local timezone.

    return int(date.timestamp())


async def upload_image_to_imgbb(image_bytes: bytes, file_extension: str) -> Optional[Dict[str, Any]]: # Return can be None
    # Create a temporary file with the appropriate file extension
    # Ensure file_extension does not start with a dot
    clean_extension = file_extension.lstrip('.')
    temp_file_path: str = "" # Initialize

    try:
        # Using NamedTemporaryFile correctly with 'delete=False' and manual removal
        with tempfile.NamedTemporaryFile(delete=False, suffix="." + clean_extension, mode="wb") as temp_file:
            temp_file.write(image_bytes)
            temp_file_path = temp_file.name

        # Upload the image to ImgBB
        async with aiohttp.ClientSession() as session:
            form_data = aiohttp.FormData()
            form_data.add_field("key", ImgBBApiKey) # ImgBBApiKey should be str
            # Provide filename for the 'image' field for better server-side handling
            form_data.add_field("image", open(temp_file_path, "rb"), filename=f"tbg.{clean_extension}")
            # "name" field in ImgBB API is for the album, not the image itself.
            # If you mean image title, it's often part of the image field or a separate param.
            # The API docs say "name: The name of the file, this is automatically detected if not set"
            # So, explicitly setting "name" for the file might not be needed if filename is in content-disposition.
            # form_data.add_field("name", "tbg") # This might be for album or ignored

            async with session.post("https://api.imgbb.com/1/upload", data=form_data) as response:
                if response.status == 200: # ImgBB success is 200
                    response_data: Dict[str, Any] = await response.json() # type: ignore
                    return response_data
                else:
                    # Log error details
                    error_text = await response.text()
                    print(f"ImgBB upload failed. Status: {response.status}, Response: {error_text}")
                    return None
    except FileNotFoundError:
        print(f"Error: Temporary file {temp_file_path} not found during ImgBB upload.")
        return None
    except Exception as e: # Catch other potential errors (e.g., network issues)
        print(f"An error occurred during ImgBB upload: {e}")
        return None
    finally:
        # Ensure the temporary file is deleted
        if temp_file_path and os.path.exists(temp_file_path):
            try:
                os.remove(temp_file_path)
            except OSError as e: # Catch error if removal fails
                print(f"Error deleting temporary file {temp_file_path}: {e}")


async def upload_to_tanjun_logs(content: str) -> Optional[str]: # Return can be None
    try:
        compressed_content: bytes = gzip.compress(content.encode("utf-8"))
        # Ensure bytebin_url, bytebin_username, bytebin_password are strings
        url: str = str(bytebin_url)
        username: str = str(bytebin_username)
        password: str = str(bytebin_password)

        async with aiohttp.ClientSession() as session:
            auth = aiohttp.BasicAuth(login=username, password=password)
            headers = {"Content-Type": "application/octet-stream", "Content-Encoding": "gzip"} # text/html might not be right for gzip
                                                                                          # application/octet-stream is safer for binary

            # Ensure URL ends with /post or adjust as per bytebin API
            post_url = url.rstrip('/') + "/post"

            async with session.post(post_url, data=compressed_content, headers=headers, auth=auth) as response:
                if response.status == 201: # Bytebin typically returns 201 Created
                    try:
                        response_data: Dict[str, Any] = await response.json() # type: ignore
                        if "key" in response_data and isinstance(response_data["key"], str):
                            return f"{url.rstrip('/')}/{response_data['key']}"
                        else:
                            print(f"Bytebin upload: 'key' not found or not string in response: {response_data}")
                            return None
                    except aiohttp.ContentTypeError:
                        # If response is not JSON, but still 201, it might be plain text key
                        key_text: str = await response.text()
                        if key_text: # Assuming the key is the entire body
                             return f"{url.rstrip('/')}/{key_text.strip()}"
                        print(f"Bytebin upload: Response was 201 but not JSON and no text key: {await response.text()}")
                        return None
                else:
                    print(f"Bytebin upload failed. Status: {response.status}, Response: {await response.text()}")
                    return None
    except Exception as e:
        print(f"An error occurred during log upload to Bytebin: {e}")
        return None


def check_if_str_is_hex_color(color_str: str) -> bool: # Renamed param
    # Basic check for common hex color formats (e.g., "#RRGGBB", "RRGGBB", "#RGB", "RGB")
    # More robust validation might be needed for strict adherence to CSS hex color specs.
    color_str = color_str.lstrip('#') # Remove leading # if present
    if not all(c in "0123456789abcdefABCDEF" for c in color_str):
        return False # Contains invalid hex characters
    length = len(color_str)
    if length not in (3, 6): # Valid lengths are 3 (RGB) or 6 (RRGGBB)
        return False
    # This doesn't use int(color_str, 16) directly for validation logic,
    # but rather checks format and characters. int() would succeed for "0" or "1A".
    return True


def draw_text_with_outline(
    draw: Any, # Should be ImageDraw.Draw object from Pillow
    position: Tuple[int, int],
    text: str,
    font: Any, # Should be an ImageFont object from Pillow
    text_color: Union[str, Tuple[int, int, int], Tuple[int, int, int, int]], # Color name or tuple
    outline_color: Union[str, Tuple[int, int, int], Tuple[int, int, int, int]]
) -> None:
    x, y = position
    # Outline offsets (adjust for desired thickness)
    outline_offset: int = 1 # Example: 1 pixel offset

    # Draw outline by drawing text at slightly offset positions
    for dx in range(-outline_offset, outline_offset + 1):
        for dy in range(-outline_offset, outline_offset + 1):
            if dx == 0 and dy == 0: # Skip the center position for outline
                continue
            # Simple square outline. For smoother, consider more points or specific stroke methods if available.
            draw.text((x + dx, y + dy), text, font=font, fill=outline_color)

    # Draw the main text on top
    draw.text(position, text, font=font, fill=text_color)


def isoTimeToDate(isoTime: str) -> datetime.datetime:
    try:
        # datetime.fromisoformat handles ISO 8601 strings
        # It supports timezone offsets like +00:00, Z, etc.
        # If no timezone info, it creates a naive datetime.
        dt_obj = datetime.datetime.fromisoformat(isoTime)
        # If you want to ensure it's timezone-aware (e.g., UTC by default if naive):
        # if dt_obj.tzinfo is None:
        #     dt_obj = dt_obj.replace(tzinfo=datetime.timezone.utc)
        return dt_obj
    except ValueError as e:
        # Handle cases where isoTime is not a valid ISO format string
        print(f"Error parsing ISO time string '{isoTime}': {e}")
        # Depending on requirements, either raise the error, or return a default/None
        raise # Or return datetime.datetime.now(datetime.timezone.utc) or None


def similar(a: str, b: str) -> float: # SequenceMatcher takes str, returns float
    return SequenceMatcher(None, a, b).ratio()


def addThousandsSeparator(number: Union[int, float], separator: str = " ") -> str: # Can take float, custom separator
    # Using f-string formatting for thousands separator (locale-dependent for comma/dot)
    # To force a specific separator like space, we need to replace.
    if isinstance(number, int):
        return f"{number:,}".replace(",", separator)
    elif isinstance(number, float):
        # Decide on float precision if necessary, e.g., "{:.2f}" for 2 decimal places
        return f"{number:,}".replace(",", separator) # Default float formatting
    else:
        raise TypeError("Input number must be an integer or float.")

