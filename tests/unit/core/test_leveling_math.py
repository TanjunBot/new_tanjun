"""Tests for leveling math and logic (XP formulas, expression evaluator, threshold cache).

Tests the pure math functions in utility.py related to the leveling system:
- get_xp_for_level, get_level_for_xp for all built-in scalings
- eval_expr for custom formula parsing
- LevelThresholdCache for caching behavior

These tests have no Discord dependency — they test the mathematical core.
"""

import math

import pytest

# These functions are imported via conftest which patches config and discord
from utility import (
    LevelThresholdCache,
    eval_expr,
    get_level_for_xp,
    get_level_for_xp_async,
    get_xp_for_level,
    get_xp_for_level_async,
)

# =============================================================================
# Scaling Tests: get_xp_for_level ↔ get_level_for_xp round-trip
# =============================================================================


class TestXpForLevel:
    """Tests for get_xp_for_level with built-in scalings."""

    SCALINGS = ["easy", "medium", "hard", "extreme"]

    def test_easy(self):
        """Easy scaling: 100 * level."""
        assert get_xp_for_level(1, "easy") == 100
        assert get_xp_for_level(10, "easy") == 1000
        assert get_xp_for_level(100, "easy") == 10000
        assert get_xp_for_level(5000, "easy") == 500000

    def test_medium(self):
        """Medium scaling: 100 * level**1.5."""
        assert get_xp_for_level(1, "medium") == 100
        assert get_xp_for_level(4, "medium") == 800  # 100 * 8 = 800
        assert get_xp_for_level(100, "medium") == 100000  # 100 * 1000 = 100000

    def test_hard(self):
        """Hard scaling: 100 * level**2."""
        assert get_xp_for_level(1, "hard") == 100
        assert get_xp_for_level(10, "hard") == 10000
        assert get_xp_for_level(100, "hard") == 1000000

    def test_extreme(self):
        """Extreme scaling: 100 * level**2.5."""
        assert get_xp_for_level(1, "extreme") == 100
        assert get_xp_for_level(10, "extreme") == 31622  # 100 * 316.227...

    def test_level_zero(self):
        """Level 0 should return 0 XP for all scalings."""
        for scaling in self.SCALINGS:
            assert get_xp_for_level(0, scaling) == 0, f"{scaling}: level 0 should give 0 XP"

    def test_negative_level(self):
        """Negative levels should return 0 XP."""
        assert get_xp_for_level(-1, "easy") == 0
        assert get_xp_for_level(-100, "medium") == 0

    def test_invalid_scaling_falls_back_to_medium(self):
        """Unknown scaling name should fall back to medium formula."""
        from utility import get_xp_for_level

        medium_xp = get_xp_for_level(10, "medium")
        fallback_xp = get_xp_for_level(10, "nonexistent")
        assert fallback_xp == medium_xp


class TestLevelForXp:
    """Tests for get_level_for_xp with built-in scalings."""

    SCALINGS = ["easy", "medium", "hard", "extreme"]
    TEST_LEVELS = [1, 5, 10, 25, 50, 100, 500, 1000, 5000, 10000]

    def test_easy_round_trip(self):
        """Easy scaling: get_level_for_xp(get_xp_for_level(l)) == l."""
        for level in self.TEST_LEVELS:
            xp = get_xp_for_level(level, "easy")
            computed = get_level_for_xp(xp, "easy")
            assert computed == level, f"easy: level={level}, xp={xp}, got level={computed}"

    def test_medium_round_trip(self):
        """Medium scaling: round-trip with ≤1 level imprecision (float exponent)."""
        for level in self.TEST_LEVELS:
            xp = get_xp_for_level(level, "medium")
            computed = get_level_for_xp(xp, "medium")
            assert abs(computed - level) <= 1, f"medium: level={level}, xp={xp}, got level={computed}"

    def test_hard_round_trip(self):
        """Hard scaling: round-trip with ≤1 level imprecision."""
        for level in self.TEST_LEVELS:
            xp = get_xp_for_level(level, "hard")
            computed = get_level_for_xp(xp, "hard")
            assert abs(computed - level) <= 1, f"hard: level={level}, xp={xp}, got level={computed}"

    def test_extreme_round_trip(self):
        """Extreme scaling: round-trip with ≤1 level imprecision."""
        for level in self.TEST_LEVELS:
            xp = get_xp_for_level(level, "extreme")
            computed = get_level_for_xp(xp, "extreme")
            assert abs(computed - level) <= 1, f"extreme: level={level}, xp={xp}, got level={computed}"

    def test_xp_zero_returns_zero(self):
        """0 XP = level 0 for all scalings."""
        for scaling in self.SCALINGS:
            assert get_level_for_xp(0, scaling) == 0, f"{scaling}: 0 XP should give level 0"

    def test_xp_one_returns_zero(self):
        """1 XP (below 100) = level 0 for all scalings."""
        for scaling in self.SCALINGS:
            assert get_level_for_xp(1, scaling) == 0, f"{scaling}: 1 XP should give level 0"

    def test_xp_large_proportional(self):
        """Easier scalings give higher levels for the same large XP."""
        levels = {
            "easy": get_level_for_xp(1_000_000, "easy"),
            "medium": get_level_for_xp(1_000_000, "medium"),
            "hard": get_level_for_xp(1_000_000, "hard"),
            "extreme": get_level_for_xp(1_000_000, "extreme"),
        }
        for scaling, level in levels.items():
            assert level > 0, f"{scaling}: should have positive level"
        assert levels["easy"] >= levels["medium"]
        assert levels["medium"] >= levels["hard"]
        assert levels["hard"] >= levels["extreme"]

    def test_negative_xp_returns_zero(self):
        """Negative XP should return level 0."""
        for scaling in self.SCALINGS:
            assert get_level_for_xp(-1, scaling) == 0, f"{scaling}: negative XP should give level 0"
            assert get_level_for_xp(-1000, scaling) == 0, f"{scaling}: very negative XP should give level 0"


# =============================================================================
# Custom Formula Tests
# =============================================================================


class TestCustomFormula:
    """Tests for leveling with custom formulas."""

    def test_linear_custom(self):
        """Custom formula equivalent to 'easy' scaling: 100 * level."""
        formula = "100 * level"
        assert get_xp_for_level(10, "custom", formula) == 1000
        assert get_xp_for_level(100, "custom", formula) == 10000

    def test_quadratic_custom(self):
        """Custom quadratic formula: 50 * level ** 2."""
        formula = "50 * level ** 2"
        assert get_xp_for_level(10, "custom", formula) == 5000
        assert get_xp_for_level(5, "custom", formula) == 1250

    def test_with_sqrt(self):
        """Custom formula with sqrt."""
        formula = "200 * sqrt(level)"
        assert get_xp_for_level(100, "custom", formula) == 2000
        assert get_xp_for_level(1, "custom", formula) == 200

    def test_with_ln(self):
        """Custom formula with natural log."""
        formula = "100 * ln(level + 1) * level"
        # level=1: 100 * ln(2) * 1 ≈ 69.3 → floor = 69
        assert get_xp_for_level(1, "custom", formula) == 69
        # level=10: 100 * ln(11) * 10 ≈ 2397.9 → floor = 2397
        assert get_xp_for_level(10, "custom", formula) == 2397

    def test_broken_formula_returns_zero(self):
        """Malformed custom formulas should return 0."""
        assert get_xp_for_level(10, "custom", "undefined_var + level") == 0
        assert get_xp_for_level(10, "custom", "1/0") == 0
        # Empty string is not malformed — it falls back to medium scaling
        # so we expect a non-zero result
        assert get_xp_for_level(10, "custom", "") > 0

    def test_level_for_custom_xp(self):
        """Test get_level_for_xp with custom formula."""
        formula = "100 * level ** 2"
        # Level 10 needs 100 * 100 = 10000 XP
        assert get_xp_for_level(10, "custom", formula) == 10000
        # Level threshold for 5000 XP should be level 7
        # (level 7 = 4900, level 8 = 6400)
        assert get_level_for_xp(5000, "custom", formula) == 7
        # Level threshold for 10000 XP should be level 10
        assert get_level_for_xp(10000, "custom", formula) == 10

    def test_custom_round_trip(self):
        """Round-trip: get_level_for_xp(get_xp_for_level(l)) ≈ l for custom."""
        formula = "100 * level"
        for level in [1, 5, 10, 50, 100, 500, 1000]:
            xp = get_xp_for_level(level, "custom", formula)
            computed = get_level_for_xp(xp, "custom", formula)
            assert computed == level, f"custom: level={level}, xp={xp}, got level={computed}"


# =============================================================================
# Expression Parser Tests (eval_expr)
# =============================================================================


class TestExpressionParser:
    """Tests for the eval_expr function used in custom formulas.

    NOTE: `^` in this evaluator is bitwise XOR (Python's default behavior),
    not exponentiation. Use `**` for power operations.
    """

    # ── Basic arithmetic ─────────────────────────────────────────────────

    def test_addition(self):
        assert eval_expr("3 + 5") == 8.0
        assert eval_expr("10 + 20 + 30") == 60.0

    def test_subtraction(self):
        assert eval_expr("10 - 3") == 7.0
        assert eval_expr("100 - 50 - 20") == 30.0

    def test_multiplication(self):
        assert eval_expr("4 * 5") == 20.0
        assert eval_expr("2 * 3 * 4") == 24.0

    def test_division(self):
        assert eval_expr("10 / 2") == 5.0
        assert eval_expr("1 / 3") == pytest.approx(0.3333333333, rel=1e-9)

    def test_exponentiation(self):
        assert eval_expr("2 ** 3") == 8.0
        assert eval_expr("10 ** 2") == 100.0
        assert eval_expr("5 ** 0") == 1.0

    def test_modulo(self):
        assert eval_expr("10 % 3") == 1.0
        assert eval_expr("17 % 5") == 2.0

    def test_operator_precedence(self):
        assert eval_expr("2 + 3 * 4") == 14.0
        assert eval_expr("(2 + 3) * 4") == 20.0
        assert eval_expr("10 - 2 * 3 + 4") == 8.0
        assert eval_expr("2 * 3 ** 2") == 18.0  # exponent before multiplication

    def test_negative_value(self):
        assert eval_expr("-5") == -5.0
        assert eval_expr("-(3 + 4)") == -7.0

    def test_nested_parentheses(self):
        assert eval_expr("((2 + 3) * (4 + 1))") == 25.0

    # ── Advanced functions ──────────────────────────────────────────────

    def test_sqrt(self):
        assert eval_expr("sqrt(16)") == 4.0
        assert eval_expr("sqrt(0)") == 0.0
        assert eval_expr("sqrt(2)") == pytest.approx(1.41421356, rel=1e-6)

    def test_sqrt_with_root(self):
        """sqrt[n](x) for n-th root."""
        assert eval_expr("sqrt[3](27)") == 3.0
        assert eval_expr("sqrt[4](16)") == 2.0

    def test_nthroot(self):
        """nthroot[n](x) for n-th root."""
        assert eval_expr("nthroot[3](27)") == 3.0
        assert eval_expr("nthroot[2](16)") == 4.0

    def test_ln(self):
        """Natural logarithm via ln()."""
        assert eval_expr("ln(1)") == 0.0
        assert eval_expr("ln(e)") == 1.0
        assert eval_expr("ln(100)") == pytest.approx(4.605170, rel=1e-5)

    def test_log_with_base(self):
        """log[base](x) for arbitrary base."""
        assert eval_expr("log[10](100)") == 2.0
        assert eval_expr("log[2](8)") == 3.0

    def test_log2(self):
        assert eval_expr("log2(8)") == 3.0
        assert eval_expr("log2(1024)") == 10.0

    def test_log10(self):
        # log_n may have floating-point imprecision (2.999... vs 3.0)
        assert eval_expr("log10(1000)") == pytest.approx(3.0, rel=1e-9)
        assert eval_expr("log10(1)") == 0.0

    def test_sin(self):
        assert eval_expr("sin(0)") == 0.0
        assert eval_expr("sin(pi / 2)") == pytest.approx(1.0, rel=1e-5)

    def test_cos(self):
        assert eval_expr("cos(0)") == 1.0
        assert eval_expr("cos(pi)") == pytest.approx(-1.0, rel=1e-5)

    def test_tan(self):
        assert eval_expr("tan(0)") == 0.0
        assert eval_expr("tan(pi / 4)") == pytest.approx(1.0, rel=1e-5)

    def test_floor(self):
        assert eval_expr("floor(3.7)") == 3
        assert eval_expr("floor(-1.5)") == -2

    def test_ceil(self):
        assert eval_expr("ceil(3.2)") == 4
        assert eval_expr("ceil(-1.5)") == -1

    def test_abs(self):
        assert eval_expr("abs(-5)") == 5
        assert eval_expr("abs(3)") == 3
        assert eval_expr("abs(0)") == 0

    def test_pi_constant(self):
        assert eval_expr("pi") == pytest.approx(math.pi, rel=1e-10)

    def test_e_constant(self):
        assert eval_expr("e") == pytest.approx(math.e, rel=1e-10)

    # ── Variable injection ──────────────────────────────────────────────

    def test_variable_replacement(self):
        result = eval_expr("x + 5", {"x": 10})
        assert result == 15.0

    def test_variable_in_level_formula(self):
        """Variable 'level' should work without 'e' replacement bug."""
        result = eval_expr("100 * level ** 2", {"level": 5})
        assert result == 2500.0

    def test_multiple_variables(self):
        result = eval_expr("a * b + c", {"a": 2, "b": 3, "c": 4})
        assert result == 10.0

    def test_undefined_variable_raises(self):
        with pytest.raises(NameError):
            eval_expr("x + 1", {})

    # ── Error handling ──────────────────────────────────────────────────

    def test_empty_expression_raises(self):
        with pytest.raises(SyntaxError):
            eval_expr("")

    def test_invalid_syntax_raises(self):
        with pytest.raises(SyntaxError):
            eval_expr("+++")

    def test_unsupported_function_raises(self):
        with pytest.raises(TypeError):
            eval_expr("bad_function(42)")

    def test_malformed_expression_raises(self):
        with pytest.raises(SyntaxError):
            eval_expr("2 + ")

    def test_zero_result(self):
        assert eval_expr("0") == 0.0
        assert eval_expr("0 * 1000000") == 0.0


# =============================================================================
# LevelThresholdCache Tests
# =============================================================================


class TestLevelThresholdCache:
    """Tests for LevelThresholdCache behavior with custom formulas."""

    def setup_method(self):
        """Clear cache before each test for isolation."""
        LevelThresholdCache._thresholds.clear()

    def test_builtin_scalings_skip_cache(self):
        """Built-in scalings use O(1) inversion, not the threshold cache."""
        get_level_for_xp(5000, "hard")
        custom_keys = [k for k in LevelThresholdCache._thresholds if k[0] == "custom"]
        assert len(custom_keys) == 0, "Built-in scalings should not use the threshold cache"

    def test_custom_formula_creates_cache_entry(self):
        """Custom formulas populate the cache."""
        get_level_for_xp(5000, "custom", "100 * level ** 2")
        assert len(LevelThresholdCache._thresholds) == 1

    def test_cache_reuses_entry(self):
        """Repeated calls with the same formula reuse cached thresholds."""
        formula = "100 * level ** 2"
        get_level_for_xp(5000, "custom", formula)
        count_before = len(LevelThresholdCache._thresholds)
        get_level_for_xp(6000, "custom", formula)
        count_after = len(LevelThresholdCache._thresholds)
        assert count_before == count_after

    def test_different_formulas_separate_entries(self):
        """Different formulas get separate entries."""
        get_level_for_xp(5000, "custom", "100 * level ** 2")
        get_level_for_xp(5000, "custom", "100 * level ** 3")
        assert len(LevelThresholdCache._thresholds) == 2

    def test_cache_eviction(self):
        """Cache evicts oldest entries when exceeding _MAX_ENTRIES."""
        for i in range(LevelThresholdCache._MAX_ENTRIES + 5):
            formula = f"{i + 1} * level"
            get_level_for_xp(1000, "custom", formula)
        assert len(LevelThresholdCache._thresholds) <= LevelThresholdCache._MAX_ENTRIES

    def test_xp_below_level_one(self):
        """Very low XP returns level 0."""
        formula = "100 * level"
        assert get_level_for_xp(0, "custom", formula) == 0
        assert get_level_for_xp(50, "custom", formula) == 0

    def test_xp_at_threshold(self):
        """XP at exact threshold returns correct level."""
        formula = "100 * level"
        assert get_level_for_xp(100, "custom", formula) == 1
        assert get_level_for_xp(500, "custom", formula) == 5
        assert get_level_for_xp(10000, "custom", formula) == 100

    def test_xp_between_thresholds(self):
        """XP between thresholds returns lower level."""
        formula = "100 * level"
        # Level 5 needs 500 XP, level 6 needs 600 XP
        assert get_level_for_xp(550, "custom", formula) == 5

    def test_max_level_cap(self):
        """XP well beyond MAX_LEVEL shouldn't exceed the cap."""
        level = get_level_for_xp(1_000_000_000, "custom", "1 * level")
        assert level <= LevelThresholdCache._MAX_LEVEL


# =============================================================================
# Async Version Tests
# =============================================================================


@pytest.mark.asyncio
class TestAsyncLeveling:
    """Tests for async versions of leveling functions."""

    async def test_async_get_xp_easy(self):
        result = await get_xp_for_level_async(10, "easy")
        assert result == 1000

    async def test_async_get_xp_custom(self):
        result = await get_xp_for_level_async(10, "custom", "100 * level")
        assert result == 1000

    async def test_async_get_level_easy(self):
        result = await get_level_for_xp_async(1000, "easy")
        assert result == 10

    async def test_async_get_level_custom(self):
        result = await get_level_for_xp_async(1000, "custom", "100 * level")
        assert result == 10

    async def test_async_custom_broken_formula(self):
        result = await get_xp_for_level_async(10, "custom", "1/0")
        assert result == 0

    async def test_async_negative_xp(self):
        result = await get_level_for_xp_async(-100, "easy")
        assert result == 0

    async def test_async_xp_zero(self):
        result = await get_xp_for_level_async(0, "hard")
        assert result == 0
