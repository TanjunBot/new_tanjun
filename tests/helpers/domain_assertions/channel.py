from __future__ import annotations

from typing import Any

from tests.helpers.command_matrix.models import MatrixCase
from tests.helpers.domain_assertions.base import assert_default_embed, embed_text, skip_if_denial


def assert_channel_embed(embed: Any, case: MatrixCase) -> None:
    assert_default_embed(embed, case)
    if skip_if_denial(embed, case):
        return
    text = embed_text(embed).lower()
    tokens = ("channel", "welcome", "farewell", "configured", "set", "removed", "media", "permission")
    assert any(token in text for token in tokens), f"expected channel config output for {case.id}: {text!r}"
