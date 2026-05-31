"""
MathService: Encapsulate numeric expression parsing/evaluation.

Extracts the NumericStringParser from utility.py into a proper service
with typed result models and a clear error hierarchy.

Replaces the hand-written pyparsing-based parser with the same logic
behind a typed interface, so all math commands go through one service.
"""

from __future__ import annotations

import functools
import math
import operator as op
import re
from collections.abc import Callable
from typing import Any

from pydantic import BaseModel
from pyparsing import (
    CaselessLiteral,
    Combine,
    Forward,
    Literal,
    Opt,
    Word,
    ZeroOrMore,
    alphas,
    nums,
)

# --- Type aliases ---

ParsedResult = float


# --- Pydantic models ---


class MathFunctionInfo(BaseModel):
    """Metadata about a built-in math function exposed by the service."""

    name: str
    description: str
    parameters: int


class MathResult(BaseModel):
    """Typed result of a math expression evaluation."""

    expression: str
    result: float
    error: str | None = None


class MathVariable(BaseModel):
    """A variable that can be provided to an expression evaluation."""

    name: str
    value: float


# --- Error hierarchy ---


class MathError(Exception):
    """Base exception for all math-service errors."""


class MathSyntaxError(MathError):
    """Raised when the expression cannot be parsed."""


class UndefinedVariable(MathError):
    """Raised when an undefined variable is referenced in the expression."""


class EvaluationError(MathError):
    """Raised when evaluation fails (e.g. division by zero)."""


# --- Service ---


class MathService:
    """
    Typed expression evaluator with Pydantic result models.

    Wraps a pyparsing-based parser that supports:
    - Basic arithmetic: +, -, *, /, ^
    - Functions: sin, cos, tan, log, sqrt, factorial, etc.
    - Constants: pi, e
    - Variables: provided at evaluation time
    """

    def __init__(self) -> None:
        self._build_parser()

    def evaluate(self, expression: str, variables: dict[str, float] | None = None) -> MathResult:
        """
        Evaluate a mathematical expression and return a typed result.

        Args:
            expression: The expression string to evaluate.
            variables: Optional mapping of variable names to values.

        Returns:
            A MathResult with the result or error information.
        """
        try:
            value = self._eval(expression, variables or {})
            return MathResult(expression=expression, result=round(value, 10), error=None)
        except MathError as math_error:
            return MathResult(expression=expression, result=0.0, error=str(math_error))
        except Exception as exc:
            return MathResult(expression=expression, result=0.0, error=str(exc))

    def get_functions(self) -> list[MathFunctionInfo]:
        """Return metadata for all built-in math functions."""
        return [
            MathFunctionInfo(name="sin", description="Sine (radians)", parameters=1),
            MathFunctionInfo(name="cos", description="Cosine (radians)", parameters=1),
            MathFunctionInfo(name="tan", description="Tangent (radians)", parameters=1),
            MathFunctionInfo(name="asin", description="Arc sine", parameters=1),
            MathFunctionInfo(name="acos", description="Arc cosine", parameters=1),
            MathFunctionInfo(name="atan", description="Arc tangent", parameters=1),
            MathFunctionInfo(name="sinh", description="Hyperbolic sine", parameters=1),
            MathFunctionInfo(name="cosh", description="Hyperbolic cosine", parameters=1),
            MathFunctionInfo(name="tanh", description="Hyperbolic tangent", parameters=1),
            MathFunctionInfo(name="asinh", description="Inverse hyperbolic sine", parameters=1),
            MathFunctionInfo(name="acosh", description="Inverse hyperbolic cosine", parameters=1),
            MathFunctionInfo(name="atanh", description="Inverse hyperbolic tangent", parameters=1),
            MathFunctionInfo(name="log", description="Natural logarithm", parameters=1),
            MathFunctionInfo(name="log10", description="Base-10 logarithm", parameters=1),
            MathFunctionInfo(name="log2", description="Base-2 logarithm", parameters=1),
            MathFunctionInfo(name="exp", description="Exponential (e^x)", parameters=1),
            MathFunctionInfo(name="abs", description="Absolute value", parameters=1),
            MathFunctionInfo(name="trunc", description="Truncate to integer", parameters=1),
            MathFunctionInfo(name="round", description="Round to nearest integer", parameters=1),
            MathFunctionInfo(name="sgn", description="Sign function (-1, 0, 1)", parameters=1),
            MathFunctionInfo(name="sqrt", description="Square root", parameters=1),
            MathFunctionInfo(name="factorial", description="Factorial", parameters=1),
            MathFunctionInfo(name="fac", description="Factorial (alias)", parameters=1),
            MathFunctionInfo(name="degrees", description="Convert radians to degrees", parameters=1),
            MathFunctionInfo(name="radians", description="Convert degrees to radians", parameters=1),
            MathFunctionInfo(name="ceil", description="Ceiling", parameters=1),
            MathFunctionInfo(name="floor", description="Floor", parameters=1),
        ]

    # -- Internal parser implementation --

    def _build_parser(self) -> None:
        """Set up the pyparsing grammar (function and operator maps only)."""
        # Function map
        self._fn: dict[str, Callable[[float], float]] = {
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
            "trunc": lambda x: float(math.trunc(x)),
            "round": lambda x: float(round(x)),
            "sgn": lambda a: abs(a) > 1e-12 and float(self._cmp(a, 0)) or 0.0,
            "sqrt": math.sqrt,
            "factorial": lambda x: float(math.factorial(int(x))),
            "degrees": math.degrees,
            "radians": math.radians,
            "ceil": lambda x: float(math.ceil(x)),
            "floor": lambda x: float(math.floor(x)),
            "fac": lambda x: float(math.factorial(int(x))),
        }

        # Constants lookup (non-callable values)
        self._constants: dict[str, float] = {
            "pi": math.pi,
            "e": math.e,
        }

        # Operator map
        self._opn: dict[str, Callable[[float, float], float]] = {
            "+": op.add,
            "-": op.sub,
            "*": op.mul,
            "/": op.truediv,
            "^": op.pow,
        }

    @staticmethod
    def _cmp(a: float, b: float) -> int:
        return (a > b) - (a < b)

    def _push_first(self, stack: list[Any], _strg: str, _loc: int, toks: Any) -> None:
        stack.append(toks[0])

    def _push_uminus(self, stack: list[Any], _strg: str, _loc: int, toks: Any) -> None:
        if toks and toks[0] == "-":
            stack.append("unary -")

    def _evaluate_stack(self, s: list[Any]) -> float:
        op = s.pop()
        if op == "unary -":
            return -self._evaluate_stack(s)
        if op in "+-*/^":
            op2 = self._evaluate_stack(s)
            op1 = self._evaluate_stack(s)
            return self._opn[op](op1, op2)
        if op == "PI":
            return math.pi
        if op == "E":
            return math.e
        if op in self._fn:
            return self._fn[op](self._evaluate_stack(s))
        if op in self._constants:
            return self._constants[op]
        if op[0].isalpha():
            raise UndefinedVariable(f"Unknown identifier: {op}")
        # Handle variables that are numbers
        try:
            return float(op)
        except (ValueError, TypeError):
            raise UndefinedVariable(f"Unknown identifier: {op}") from None

    def _eval(self, expression: str, variables: dict[str, float] | None = None) -> float:
        """Evaluate expression with optional variable substitution."""
        vars_dict = variables or {}

        if vars_dict:
            # Substitute variable names with their values using word boundaries
            substituted = expression
            for name, value in vars_dict.items():
                pattern = r"\b" + re.escape(name) + r"\b"
                substituted = re.sub(pattern, str(value), substituted)
            expression = substituted

        expr_stack: list[Any] = []

        # Create a temporary parser with local stack bindings
        point = Literal(".")
        e_lit = CaselessLiteral("E")
        fnumber = Combine(Word("+-" + nums, nums) + Opt(point + Opt(Word(nums))) + Opt(e_lit + Word("+-" + nums, nums)))
        ident = Word(alphas, alphas + nums + "_$")

        plus, minus, mult, div = map(Literal, "+-*/")
        lpar, rpar = map(Literal, "()")
        addop = plus | minus
        multop = mult | div
        expop = Literal("^")

        expr = Forward()
        atom = (Literal("-") + (ident + lpar + expr + rpar | fnumber | lpar + expr.suppress() + rpar)).setParseAction(
            functools.partial(self._push_uminus, expr_stack)
        ) | (ident + lpar + expr + rpar | fnumber | lpar + expr.suppress() + rpar).setParseAction(
            functools.partial(self._push_first, expr_stack)
        )

        factor = Forward()
        factor << atom + ZeroOrMore((expop + factor).setParseAction(functools.partial(self._push_first, expr_stack)))

        term = factor + ZeroOrMore((multop + factor).setParseAction(functools.partial(self._push_first, expr_stack)))
        expr << term + ZeroOrMore((addop + term).setParseAction(functools.partial(self._push_first, expr_stack)))

        try:
            _ = expr.parseString(expression, parseAll=True)
        except Exception as exc:
            raise MathSyntaxError(f"Failed to parse expression: {exc}") from exc

        try:
            return self._evaluate_stack(expr_stack[:])
        except ZeroDivisionError as exc:
            raise EvaluationError(f"Division by zero: {exc}") from exc
        except OverflowError as exc:
            raise EvaluationError(f"Numeric overflow: {exc}") from exc
        except Exception as exc:
            if isinstance(exc, MathError):
                raise
            raise EvaluationError(str(exc)) from exc
