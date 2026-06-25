from __future__ import annotations

from typing import Any

from tests.helpers.command_matrix.models import MatrixCase
from tests.helpers.domain_assertions.base import assert_default_embed, embed_text, skip_if_denial


def assert_utility_embed(embed: Any, case: MatrixCase) -> None:
    assert_default_embed(embed, case)
    if skip_if_denial(embed, case):
        return
    text = embed_text(embed).lower()
    leaf = case.tree_path.rsplit(" ", 1)[-1]
    tokens = (
        "http", "avatar", "afk", "away", "banner", "feedback", "brawl", "player",
        "club", "event", "battle", "twitch", "report", "help", "booster", "scheduled",
        "linked", "not linked", "error", "success", "modal", "warnconfigmodal",
    )
    if not any(token in text for token in tokens):
        assert text.strip(), f"expected utility output for {case.id}: {text!r}"
