"""Tests for the expression evaluator in utility.py (eval_expr/eval_).

These functions do pure math evaluation — no Discord dependency.
"""

import pytest

from utility import eval_expr


class TestEvalExpr:
    def test_basic_arithmetic(self):
        assert eval_expr("1 + 2") == 3.0
        assert eval_expr("10 - 4") == 6.0
        assert eval_expr("3 * 7") == 21.0
        assert eval_expr("20 / 5") == 4.0

    def test_order_of_operations(self):
        assert eval_expr("2 + 3 * 4") == 14.0
        assert eval_expr("(2 + 3) * 4") == 20.0
        assert eval_expr("10 - 2 * 3 + 4") == 8.0

    def test_exponentiation(self):
        assert eval_expr("2 ** 3") == 8.0
        assert eval_expr("10 ** 2") == 100.0

    def test_modulo(self):
        assert eval_expr("10 % 3") == 1.0
        assert eval_expr("17 % 5") == 2.0

    def test_variables(self):
        assert eval_expr("x + 1", {"x": 5}) == 6.0
        assert eval_expr("x * y", {"x": 3, "y": 4}) == 12.0

    def test_complex_expressions(self):
        result = eval_expr("sqrt(16)")
        assert result == 4.0
        result = eval_expr("sin(0)")
        assert result == 0.0
        result = eval_expr("cos(0)")
        assert result == 1.0

    def test_floor_division(self):
        assert eval_expr("10 // 3") == 3.0
        assert eval_expr("20 // 6") == 3.0

    def test_negative_numbers(self):
        assert eval_expr("-5 + 3") == -2.0
        assert eval_expr("10 + -3") == 7.0

    def test_float_results(self):
        assert eval_expr("10 / 4") == 2.5
        assert eval_expr("1 / 3") == pytest.approx(0.333, rel=1e-3)

    def test_invalid_expressions(self):
        with pytest.raises(Exception):
            eval_expr("")
        with pytest.raises(Exception):
            eval_expr("not_a_thing(42)")
