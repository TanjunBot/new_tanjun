from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from tests.helpers.command_coverage.models import LayerKind


@dataclass(frozen=True)
class MatrixCase:
    group: str
    tree_path: str
    dimensions: dict[str, str]
    layer: LayerKind
    meta: dict[str, Any] = field(default_factory=dict)

    @property
    def id(self) -> str:
        parts = [self.tree_path.replace(" ", "_")]
        for key in sorted(self.dimensions):
            parts.append(f"{key}={self.dimensions[key]}")
        return "-".join(parts)

    @property
    def command_slug(self) -> str:
        return self.tree_path.split()[-1]

    def dimension(self, key: str, default: str = "") -> str:
        return self.dimensions.get(key, default)
