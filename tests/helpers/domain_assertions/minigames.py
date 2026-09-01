from __future__ import annotations

from typing import Any

from tests.helpers.command_matrix.models import MatrixCase
from tests.helpers.domain_assertions.base import assert_default_embed, embed_text, is_denial_text


def assert_minigame_embed(embed: Any, case: MatrixCase) -> None:
    assert_default_embed(embed, case)
    text = embed_text(embed).lower()
    if case.dimension("permission") == "restricted":
        assert is_denial_text(text), f"expected minigame denial for {case.id}: {text!r}"
        return
    tokens = ("counting", "word", "chain", "channel", "configured", "minigame", "challenge", "mode")
    assert any(token in text for token in tokens), f"expected minigame output for {case.id}: {text!r}"
