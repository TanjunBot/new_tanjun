from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class LayerKind(StrEnum):
    BEHAVIOR_SPEC = "behavior_spec"
    INTEGRATION = "integration"
    UNIT_LOGIC = "unit_logic"
    UNIT_EXTENSION = "unit_extension"
    E2E_LIVE = "e2e_live"


class AssertionDepth(StrEnum):
    INVOKED = "invoked"
    DEFERRED = "deferred"
    OUTCOME = "outcome"
    OUTPUT = "output"
    LIVE_EMBED = "live_embed"

    @classmethod
    def rank(cls, depth: AssertionDepth) -> int:
        order = {
            cls.INVOKED: 0,
            cls.DEFERRED: 1,
            cls.OUTCOME: 2,
            cls.OUTPUT: 3,
            cls.LIVE_EMBED: 4,
        }
        return order[depth]


@dataclass(frozen=True)
class CoverageCell:
    tree_path: str
    layer: LayerKind
    dimensions: dict[str, str]
    assertion_depth: AssertionDepth
    source: str = ""

    def key(self) -> tuple[Any, ...]:
        return (
            self.tree_path,
            self.layer,
            tuple(sorted(self.dimensions.items())),
        )

    def matches_expected(self, expected: CoverageCell) -> bool:
        if self.tree_path != expected.tree_path or self.layer != expected.layer:
            return False
        return all(self.dimensions.get(k) == v for k, v in expected.dimensions.items())


@dataclass(frozen=True)
class CommandInventoryEntry:
    tree_path: str
    root_group: str
    extension: str = ""
    method_name: str = ""
    has_permission_checks: bool = False
    parameters: dict[str, list[str]] = field(default_factory=dict)


@dataclass
class LayerSummary:
    layer: LayerKind
    expected: int
    covered: int
    missing: list[CoverageCell] = field(default_factory=list)

    @property
    def percent(self) -> float:
        if self.expected == 0:
            return 100.0
        return 100.0 * self.covered / self.expected


@dataclass
class CommandPathSummary:
    tree_path: str
    root_group: str
    expected: int
    covered: int
    missing: list[CoverageCell] = field(default_factory=list)

    @property
    def percent(self) -> float:
        if self.expected == 0:
            return 100.0
        return 100.0 * self.covered / self.expected


@dataclass
class GroupCoverageSummary:
    root_group: str
    tree_paths: list[str]
    layers: list[LayerSummary]
    permission_denial_expected: int = 0
    permission_denial_covered: int = 0
    permission_denial_missing: list[str] = field(default_factory=list)

    @property
    def permission_denial_percent(self) -> float:
        if self.permission_denial_expected == 0:
            return 100.0
        return 100.0 * self.permission_denial_covered / self.permission_denial_expected


@dataclass
class CoverageReport:
    inventory: list[CommandInventoryEntry]
    expected: list[CoverageCell]
    actual: list[CoverageCell]
    groups: list[GroupCoverageSummary]
    commands: list[CommandPathSummary] = field(default_factory=list)
    paths_with_any_test: int = 0
    total_manifest_paths: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "total_manifest_paths": self.total_manifest_paths,
            "paths_with_any_test": self.paths_with_any_test,
            "commands": [
                {
                    "tree_path": cmd.tree_path,
                    "root_group": cmd.root_group,
                    "expected": cmd.expected,
                    "covered": cmd.covered,
                    "percent": round(cmd.percent, 1),
                    "missing_count": len(cmd.missing),
                }
                for cmd in self.commands
            ],
            "groups": [
                {
                    "root_group": g.root_group,
                    "tree_paths": g.tree_paths,
                    "layers": [
                        {
                            "layer": layer.layer.value,
                            "expected": layer.expected,
                            "covered": layer.covered,
                            "percent": round(layer.percent, 1),
                            "missing_count": len(layer.missing),
                            "missing_sample": [
                                {
                                    "tree_path": c.tree_path,
                                    "dimensions": c.dimensions,
                                }
                                for c in layer.missing[:10]
                            ],
                        }
                        for layer in g.layers
                    ],
                    "permission_denial": {
                        "expected": g.permission_denial_expected,
                        "covered": g.permission_denial_covered,
                        "percent": round(g.permission_denial_percent, 1),
                        "missing": g.permission_denial_missing,
                    },
                }
                for g in self.groups
            ],
        }


@dataclass(frozen=True)
class ThresholdViolation:
    check_id: str
    message: str
