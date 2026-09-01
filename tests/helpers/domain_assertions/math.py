from __future__ import annotations

from typing import Any

from tests.helpers.command_matrix.models import MatrixCase
from tests.helpers.domain_assertions.base import assert_default_embed, embed_text


def assert_math_embed(embed: Any, case: MatrixCase) -> None:
    assert_default_embed(embed, case)
    text = embed_text(embed)
    command = case.dimension("command")
    expression = case.dimension("expression")
    if expression == "invalid" and command == "calc":
        assert "error" in text.lower() or "invalid" in text.lower() or "zero" in text.lower(), (
            f"expected error marker for {case.id}: {text!r}"
        )
        return
    if command == "calc":
        assert "4" in text or "2" in text, f"expected numeric result for {case.id}: {text!r}"
    elif command == "calculator":
        assert "calculator" in text.lower(), f"expected calculator embed for {case.id}: {text!r}"
    elif command == "faculty":
        assert "120" in text or "5" in text, f"expected faculty result for {case.id}: {text!r}"
    elif command == "num2word":
        assert "forty" in text.lower() or "42" in text, f"expected num2word result for {case.id}: {text!r}"
    elif command == "randomnumber":
        assert "random" in text.lower(), f"expected random number output for {case.id}: {text!r}"
    elif command == "plotfunction":
        assert "plot" in text.lower() or "function" in text.lower(), f"expected plot output for {case.id}: {text!r}"
