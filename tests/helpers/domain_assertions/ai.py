from __future__ import annotations

from typing import Any

from tests.helpers.command_matrix.models import MatrixCase
from tests.helpers.domain_assertions.base import assert_default_embed, assert_no_error_markers, embed_text


def assert_ai_embed(embed: Any, case: MatrixCase) -> None:
    assert_default_embed(embed, case)
    text = embed_text(embed)
    assert_no_error_markers(text, case_id=case.id)
    if case.dimension("prompt_kind") != "empty":
        assert len(text.strip()) > 3, f"expected non-empty ai response for {case.id}"
