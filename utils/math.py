"""Math-related utilities: expression evaluator, level/XP calculations, and parsing.

Extracted from ``utility.py`` as part of refactoring (issue #1608).
"""

import ast
import asyncio
import bisect
import collections
import concurrent.futures
import math
import operator as op
import re
from collections.abc import Mapping

# Thread pool executor for CPU-bound formula evaluation (module-level singleton)
_eval_executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)


def cmp(a: int, b: int) -> int:
    return (a > b) - (a < b)


class NumericStringParser:
    """
    Most of this code comes from the fourFn.py pyparsing example
    """

    def __init__(self) -> None:
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
        from pyparsing import Optional as Opt

        self.exprStack = []

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
        atom = (Opt("-") + (ident + lpar + expr + rpar | fnumber)).setParseAction(self.push_first) | (
            lpar + expr.suppress() + rpar
        ).setParseAction(self.push_uminus)

        factor = Forward()
        factor << atom + ZeroOrMore((expop + factor).setParseAction(self.push_first))

        term = factor + ZeroOrMore((multop + factor).setParseAction(self.push_first))
        expr << term + ZeroOrMore((addop + term).setParseAction(self.push_first))

        self.bnf = expr

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

    def push_first(self, strg: str, loc: int, toks: object) -> None:
        self.exprStack.append(toks[0])  # type: ignore[index]

    def push_uminus(self, strg: str, loc: int, toks: object) -> None:
        if toks and toks[0] == "-":  # type: ignore[index]
            self.exprStack.append("unary -")

    def evaluate_stack(self, s: list) -> float:
        op_token = s.pop()
        if op_token == "unary -":
            return -self.evaluate_stack(s)
        if op_token in "+-*/^":
            op2 = self.evaluate_stack(s)
            op1 = self.evaluate_stack(s)
            return self.opn[op_token](op1, op2)
        elif op_token == "PI":
            return math.pi
        elif op_token == "E":
            return math.e
        elif op_token in self.fn:
            return self.fn[op_token](self.evaluate_stack(s))
        elif op_token[0].isalpha():
            raise Exception(f"Invalid identifier: {op_token}")
        else:
            return float(op_token)

    def eval(self, num_string: str, parse_all: bool = True) -> float:
        self.exprStack = []
        self.bnf.parseString(num_string, parseAll=parse_all)
        val = self.evaluate_stack(self.exprStack[:])
        return val


# ---------------------------------------------------------------------------
# AST-based expression evaluation
# ---------------------------------------------------------------------------

_operators = {
    ast.Add: op.add,
    ast.Sub: op.sub,
    ast.Mult: op.mul,
    ast.Div: op.truediv,
    ast.FloorDiv: op.floordiv,
    ast.Pow: op.pow,
    ast.BitXor: op.xor,
    ast.USub: op.neg,
    ast.Mod: op.mod,
}


def sqrt_n(x: float, n: float = 2) -> float:
    return x ** (1 / n)


def log_n(x: float, base: float = math.e) -> float:
    return math.log(x, base)


async def eval_expr_async(expr: str, variables: Mapping[str, float] | None = None) -> float:
    """Async version of eval_expr that runs the CPU-bound AST evaluation in a thread executor."""
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(_eval_executor, eval_expr, expr, variables)


def eval_expr(expr: str, variables: Mapping[str, float] | None = None) -> float:
    if variables is None:
        variables = {}

    expr = re.sub(r"\bpi\b", str(math.pi), expr)
    expr = re.sub(r"\be\b", str(math.e), expr)

    # Iteratively replace innermost function calls to handle nested calls correctly
    replacements = [
        (r"log\[(\d+)\]\(([^()]*)\)", r"log_n(\2,\1)"),
        (r"sqrt\[(\d+)\]\(([^()]*)\)", r"sqrt_n(\2,\1)"),
        (r"sqrt\(([^()]*)\)", r"sqrt_n(\1)"),
        (r"nthroot\[(\d+)\]\(([^()]*)\)", r"sqrt_n(\2,\1)"),
        (r"log2\(([^()]*)\)", r"log_n(\1,2)"),
        (r"log10\(([^()]*)\)", r"log_n(\1,10)"),
        (r"ln\(([^()]*)\)", r"log_n(\1)"),
        (r"sin\(([^()]*)\)", r"math.sin(\1)"),
        (r"cos\(([^()]*)\)", r"math.cos(\1)"),
        (r"tan\(([^()]*)\)", r"math.tan(\1)"),
        (r"asin\(([^()]*)\)", r"math.asin(\1)"),
        (r"acos\(([^()]*)\)", r"math.acos(\1)"),
        (r"atan\(([^()]*)\)", r"math.atan(\1)"),
        (r"floor\(([^()]*)\)", r"math.floor(\1)"),
        (r"ceil\(([^()]*)\)", r"math.ceil(\1)"),
        (r"abs\(([^()]*)\)", r"abs(\1)"),
    ]

    # Keep replacing until no more replacements are possible
    max_iterations = 100
    for _ in range(max_iterations):
        old_expr = expr
        for pattern, replacement in replacements:
            expr = re.sub(pattern, replacement, expr)
        if expr == old_expr:
            break

    return _eval_ast(ast.parse(expr, mode="eval").body, variables)


def _eval_ast(node: ast.AST, variables: Mapping[str, float]) -> float:
    if isinstance(node, ast.Constant):
        return node.value
    elif isinstance(node, ast.BinOp):
        return _operators[type(node.op)](_eval_ast(node.left, variables), _eval_ast(node.right, variables))
    elif isinstance(node, ast.UnaryOp):
        return _operators[type(node.op)](_eval_ast(node.operand, variables))
    elif isinstance(node, ast.Call):
        if isinstance(node.func, ast.Attribute):
            if node.func.value.id == "math":
                func = getattr(math, node.func.attr)
                args = [_eval_ast(arg, variables) for arg in node.args]
                return func(*args)
        elif isinstance(node.func, ast.Name):
            if node.func.id == "sqrt_n":
                args = [_eval_ast(arg, variables) for arg in node.args]
                return sqrt_n(*args)
            elif node.func.id == "log_n":
                args = [_eval_ast(arg, variables) for arg in node.args]
                return log_n(*args)
            elif node.func.id == "abs":
                args = [_eval_ast(arg, variables) for arg in node.args]
                return abs(*args)
        raise TypeError(f"Unsupported function call: {node.func}")
    elif isinstance(node, ast.Name):
        if node.id in variables:
            return variables[node.id]
        raise NameError(f"Variable '{node.id}' is not defined")
    else:
        raise TypeError(f"Unsupported operation: {node}")


# ---------------------------------------------------------------------------
# Level / XP calculations
# ---------------------------------------------------------------------------

LEVEL_SCALINGS = {
    "easy": lambda level: 100 * level,
    "medium": lambda level: 100 * (level**1.5),
    "hard": lambda level: 100 * (level**2),
    "extreme": lambda level: 100 * (level**2.5),
}

# Inverse formulas for built-in scalings: O(1) lookups instead of O(log n) threshold scans.
_LEVEL_INVERSES: dict[str, callable] = {
    "easy": lambda xp: xp // 100,
    "medium": lambda xp: int((xp / 100) ** (1 / 1.5)),
    "hard": lambda xp: int(math.sqrt(xp / 100)),
    "extreme": lambda xp: int((xp / 100) ** (1 / 2.5)),
}


def _invert_get_level_for_xp(xp: int, scaling: str) -> int:
    """Compute level directly via mathematical inverse of the standard scaling formula.

    This is O(1) — no iteration, no threshold list building.
    """
    if xp <= 0:
        return 0
    level = _LEVEL_INVERSES.get(scaling, lambda _: 0)(xp)
    if level < 0:
        return 0
    while get_xp_for_level(level + 1, scaling) <= xp and level < 10000:
        level += 1
    while level > 0 and get_xp_for_level(level, scaling) > xp:
        level -= 1
    return level


class LevelThresholdCache:
    """Pre-compute and cache level XP thresholds per (scaling, custom_formula) pair."""

    _thresholds: collections.OrderedDict[tuple[str, str | None], tuple[list[int], int]] = collections.OrderedDict()
    _MAX_LEVEL = 10000
    _MAX_ENTRIES = 50
    _lock: asyncio.Lock | None = None

    @classmethod
    def _get_lock(cls) -> asyncio.Lock:
        if cls._lock is None:
            cls._lock = asyncio.Lock()
        return cls._lock

    @classmethod
    def get_level_for_xp(cls, xp: int, scaling: str, custom_formula: str | None = None) -> int:
        # Use O(1) mathematical inversion for known built-in scalings
        if scaling != "custom":
            return _invert_get_level_for_xp(xp, scaling)

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
            if thresholds is None:
                start_level = 1
                thresholds = []
                max_level = cls._MAX_LEVEL
            else:
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
            while len(cls._thresholds) > cls._MAX_ENTRIES:
                cls._thresholds.popitem(last=False)
        return bisect.bisect_right(thresholds, xp)

    @classmethod
    async def get_level_for_xp_async(cls, xp: int, scaling: str, custom_formula: str | None = None) -> int:
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
            async with cls._get_lock():
                entry = cls._thresholds.get(key)
                if entry is not None:
                    thresholds, max_level = entry
                    if thresholds is not None and thresholds[-1] >= xp:
                        return bisect.bisect_right(thresholds, xp)

                if thresholds is None:
                    start_level = 1
                    new_thresholds = []
                    max_level = cls._MAX_LEVEL
                else:
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
                cls._thresholds[key] = (new_thresholds, max_level)
                while len(cls._thresholds) > cls._MAX_ENTRIES:
                    cls._thresholds.popitem(last=False)
                thresholds = new_thresholds
        return bisect.bisect_right(thresholds, xp)


def get_xp_for_level(level: int, scaling: str, custom_formula: str | None = None) -> int:
    if level <= 0:
        return 0
    if scaling == "custom" and custom_formula:
        try:
            result = eval_expr(custom_formula, variables={"level": level})
        except Exception:
            return 0
    else:
        result = LEVEL_SCALINGS.get(scaling, LEVEL_SCALINGS["medium"])(level)
    if isinstance(result, complex):
        return 0
    return math.floor(result)


async def get_xp_for_level_async(level: int, scaling: str, custom_formula: str | None = None) -> int:
    """Async version of get_xp_for_level that runs CPU-bound formula evaluation in a thread executor."""
    if level <= 0:
        return 0
    if scaling == "custom" and custom_formula:
        try:
            result = await eval_expr_async(custom_formula, variables={"level": level})
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
    """Async version of get_level_for_xp for custom formulas."""
    if scaling != "custom":
        return get_level_for_xp(xp, scaling, custom_formula)
    return await LevelThresholdCache.get_level_for_xp_async(xp, scaling, custom_formula)
