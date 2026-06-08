from __future__ import annotations

from typing import Any

from tests.helpers.command_matrix.models import MatrixCase
from tests.helpers.domain_assertions.base import assert_default_embed, embed_text, skip_if_denial


def assert_games_embed(embed: Any, case: MatrixCase) -> None:
    assert_default_embed(embed, case)
    if skip_if_denial(embed, case):
        return
    text = embed_text(embed).lower()
    tokens = (
        "game", "play", "turn", "board", "opponent", "start", "match", "hangman",
        "guess", "question", "akinator", "flag", "ship", "connect", "tic", "tac",
    )
    assert any(token in text for token in tokens), f"expected game embed for {case.id}: {text!r}"
