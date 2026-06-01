from __future__ import annotations

import keyword
import re
from typing import Any

from locale_keys._tree import locale as root

_IDENT_RE = re.compile(r"^[a-zA-Z_][a-zA-Z0-9_]*$")


def field_name(segment: str) -> str:
    if _IDENT_RE.match(segment.strip('"')):
        name = segment.strip('"')
    else:
        name = re.sub(r"[^a-zA-Z0-9_]", "_", segment.strip('"'))
        if not name:
            name = "key"
        if name[0].isdigit():
            name = f"_{name}"
    if keyword.iskeyword(name):
        name = f"{name}_"
    return name


def at(path: str) -> Any:
    node: Any = root
    for part in path.split("."):
        node = getattr(node, field_name(part))
    return node
