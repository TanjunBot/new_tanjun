from __future__ import annotations

from typing import Any

from tests.helpers.command_matrix.models import MatrixCase
from tests.helpers.domain_assertions.base import assert_default_embed, embed_text, skip_if_denial


def assert_image_embed(embed: Any, case: MatrixCase) -> None:
    assert_default_embed(embed, case)
    if skip_if_denial(embed, case):
        return
    text = embed_text(embed)
    image_url = getattr(embed, "image", None)
    has_image = bool(image_url and getattr(image_url, "url", None))
    tokens = ("http", "image", "attachment", "success", "compress", "resize", "filter", "smooth", "sharpen")
    assert has_image or any(token in text.lower() for token in tokens), (
        f"expected image output for {case.id}: {text!r}"
    )
