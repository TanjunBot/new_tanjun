from __future__ import annotations

from typing import Any

from tests.helpers.command_matrix.models import MatrixCase
from tests.helpers.domain_assertions.base import assert_default_embed, embed_text, skip_if_denial


def assert_setup_embed(embed: Any, case: MatrixCase) -> None:
    assert_default_embed(embed, case)
    if skip_if_denial(embed, case):
        return
    text = embed_text(embed).lower()
    assert any(token in text for token in ("setup", "wizard", "configure", "step", "level", "giveaway", "log")), (
        f"expected setup wizard output for {case.id}: {text!r}"
    )
