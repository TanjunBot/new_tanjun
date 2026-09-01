from __future__ import annotations

from diagnostics.registry import all_specs
from tests.helpers.command_coverage.models import AssertionDepth, CoverageCell, LayerKind


def collect_behavior_spec_cells() -> list[CoverageCell]:
    cells: list[CoverageCell] = []
    for spec in all_specs():
        if spec.skip_reason or not spec.tree_path:
            continue
        cells.append(
            CoverageCell(
                tree_path=spec.tree_path,
                layer=LayerKind.BEHAVIOR_SPEC,
                dimensions={},
                assertion_depth=AssertionDepth.DEFERRED,
                source=f"behavior_spec:{spec.id}",
            )
        )
    return cells
