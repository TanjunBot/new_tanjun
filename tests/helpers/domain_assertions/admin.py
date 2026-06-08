from __future__ import annotations

from typing import Any

from tests.helpers.command_matrix.models import MatrixCase
from tests.helpers.domain_assertions.base import assert_default_embed, skip_if_denial


def assert_admin_embed(embed: Any, case: MatrixCase) -> None:
    assert_default_embed(embed, case)
    if skip_if_denial(embed, case):
        return
