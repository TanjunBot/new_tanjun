from __future__ import annotations

import pytest

from tests.helpers.command_matrix.models import MatrixCase
from tests.helpers.domain_assertions.base import assert_live_response_outcome


def _case(*, permission: str = "admin", expression: str = "valid") -> MatrixCase:
    return MatrixCase(
        group="math_name",
        tree_path="math_name math_calc_name",
        dimensions={"permission": permission, "expression": expression, "command": "calc"},
        layer="e2e_live",
    )


def test_live_response_accepts_successful_admin_calc() -> None:
    result = {
        "embed": {
            "title": "Result",
            "description": "2+2 = 4",
            "fields": [],
        }
    }
    assert assert_live_response_outcome(result, _case()) is False


def test_live_response_rejects_bot_permission_failure_for_admin_case() -> None:
    result = {
        "embed": {
            "title": "Missing permissions",
            "description": "The bot was unable to ban the member.",
            "fields": [],
        }
    }
    with pytest.raises(AssertionError, match="permission failure"):
        assert_live_response_outcome(result, _case())


def test_live_response_accepts_expected_user_denial_for_restricted_case() -> None:
    result = {
        "embed": {
            "title": "Permission Denied",
            "description": "You do not have the required permissions to ban members.",
            "fields": [],
        }
    }
    assert assert_live_response_outcome(result, _case(permission="restricted")) is True


def test_live_response_accepts_calc_error_for_invalid_expression() -> None:
    result = {
        "embed": {
            "title": "Calculation error",
            "description": "Division by zero",
            "fields": [],
        }
    }
    assert assert_live_response_outcome(result, _case(expression="invalid")) is False
