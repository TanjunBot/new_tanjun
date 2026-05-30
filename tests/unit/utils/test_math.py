"""Tests for utils/math.py expression evaluation and level calculations."""

from __future__ import annotations

import pytest

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


class TestCmp:
    def test_greater(self):
        assert cmp(5, 3) == 1

    def test_less(self):
        assert cmp(3, 5) == -1

    def test_equal(self):
        assert cmp(5, 5) == 0


class TestSqrtN:
    def test_square_root(self):
        assert sqrt_n(16) == 4.0

    def test_cube_root(self):
        assert sqrt_n(27, 3) == pytest.approx(3.0)


class TestLogN:
    def test_natural_log(self):
        assert log_n(2.718281828) == pytest.approx(1.0, rel=0.01)

    def test_log_base_10(self):
        assert log_n(100, 10) == pytest.approx(2.0)


class TestEvalExpr:
    def test_simple_arithmetic(self):
        assert eval_expr("2 + 3") == 5

    def test_multiplication(self):
        assert eval_expr("4 * 5") == 20

    def test_power_is_bitwise_xor(self):
        assert eval_expr("2 ^ 3") == 1

    def test_with_variables(self):
        assert eval_expr("x + y", {"x": 10, "y": 5}) == 15

    def test_pi_substitution(self):
        result = eval_expr("pi")
        assert result == pytest.approx(3.14159, rel=0.001)

    def test_sqrt_function(self):
        assert eval_expr("sqrt(16)") == 4.0

    def test_sin_function(self):
        assert eval_expr("sin(0)") == pytest.approx(0.0)

    def test_undefined_variable_raises(self):
        with pytest.raises(NameError):
            eval_expr("unknown_var + 1")

    @pytest.mark.asyncio
    async def test_eval_expr_async(self):
        result = await eval_expr_async("2 + 2")
        assert result == 4


class TestNumericStringParser:
    @pytest.fixture
    def parser(self) -> NumericStringParser:
        return NumericStringParser()

    def test_basic_expression(self, parser: NumericStringParser):
        assert parser.eval("2 + 3") == 5

    def test_parentheses(self, parser: NumericStringParser):
        assert parser.eval("(2 + 3) * 4") == 20

    def test_sqrt_function(self, parser: NumericStringParser):
        assert parser.eval("sqrt(9)") == pytest.approx(3.0)

    def test_sin(self, parser: NumericStringParser):
        assert parser.eval("sin(0)") == pytest.approx(0.0)


class TestLevelCalculations:
    def test_level_scalings_exist(self):
        assert "easy" in LEVEL_SCALINGS
        assert "medium" in LEVEL_SCALINGS
        assert "hard" in LEVEL_SCALINGS
        assert "extreme" in LEVEL_SCALINGS

    def test_get_xp_for_level_easy(self):
        assert get_xp_for_level(1, "easy") == 100
        assert get_xp_for_level(2, "easy") == 200

    def test_get_xp_for_level_medium(self):
        xp = get_xp_for_level(5, "medium")
        assert xp > 0

    def test_get_level_for_xp_zero(self):
        assert get_level_for_xp(0, "easy") == 0

    def test_get_level_for_xp_roundtrip(self):
        xp = get_xp_for_level(10, "medium")
        level = get_level_for_xp(xp, "medium")
        assert level == 10

    @pytest.mark.asyncio
    async def test_get_xp_for_level_async(self):
        xp = await get_xp_for_level_async(3, "easy")
        assert xp == 300

    @pytest.mark.asyncio
    async def test_get_level_for_xp_async(self):
        level = await get_level_for_xp_async(500, "easy")
        assert level == 5


class TestLevelThresholdCache:
    def test_custom_formula_caching(self):
        LevelThresholdCache._thresholds.clear()
        level = LevelThresholdCache.get_level_for_xp(500, "custom", "100 * level")
        assert level >= 0

    @pytest.mark.asyncio
    async def test_async_custom_formula(self):
        LevelThresholdCache._thresholds.clear()
        level = await LevelThresholdCache.get_level_for_xp_async(500, "custom", "100 * level")
        assert level >= 0
