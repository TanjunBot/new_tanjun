"""Tests for services/math.py MathService."""

from __future__ import annotations

from unittest.mock import patch

import pytest

from services.math import MathService


@pytest.fixture
def service() -> MathService:
    return MathService()


class TestMathService:
    def test_evaluate_simple(self, service: MathService):
        result = service.evaluate("2 + 3")
        assert result.error is None
        assert result.result == 5

    def test_evaluate_with_variables(self, service: MathService):
        result = service.evaluate("x * 2", {"x": 5})
        assert result.result == 10

    def test_evaluate_sqrt(self, service: MathService):
        result = service.evaluate("sqrt(16)")
        assert result.result == 4.0

    def test_evaluate_sin(self, service: MathService):
        result = service.evaluate("sin(0)")
        assert result.result == 0.0

    def test_evaluate_invalid_returns_error(self, service: MathService):
        result = service.evaluate("2 +")
        assert result.error is not None

    def test_get_functions(self, service: MathService):
        funcs = service.get_functions()
        assert len(funcs) > 0
        names = {f.name for f in funcs}
        assert "sin" in names
        assert "sqrt" in names

    def test_evaluate_power(self, service: MathService):
        result = service.evaluate("2 ^ 3")
        assert result.result == 8.0

    def test_evaluate_multiplication(self, service: MathService):
        result = service.evaluate("4 * 5")
        assert result.error is None
        assert result.result == 20

    def test_evaluate_division_by_zero(self, service: MathService):
        result = service.evaluate("1 / 0")
        assert result.error is not None

    def test_evaluate_sgn(self, service: MathService):
        result = service.evaluate("sgn(5)")
        assert result.result == 1

    def test_evaluate_degrees(self, service: MathService):
        result = service.evaluate("degrees(1)")
        assert result.error is None

    def test_evaluate_fac_error(self, service: MathService):
        result = service.evaluate("fac(5)")
        assert result.error is not None

    def test_evaluate_generic_exception(self, service: MathService):
        with patch.object(service, "_eval", side_effect=RuntimeError("boom")):
            result = service.evaluate("1 + 1")
        assert result.error == "boom"

    def test_cmp_helper(self, service: MathService):
        assert service._cmp(1.0, 0.0) == 1
        assert service._cmp(0.0, 1.0) == -1
