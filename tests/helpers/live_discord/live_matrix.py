from __future__ import annotations

from dataclasses import dataclass

from diagnostics.tree import load_manifest


@dataclass(frozen=True)
class LiveSmokeCase:
    tree_path: str

    @property
    def id(self) -> str:
        return self.tree_path.replace(" ", "_")

    @property
    def parts(self) -> tuple[str, ...]:
        return tuple(self.tree_path.split())


def iter_live_smoke_cases() -> list[LiveSmokeCase]:
    paths = load_manifest().get("paths") or []
    return [LiveSmokeCase(tree_path=path) for path in paths]
