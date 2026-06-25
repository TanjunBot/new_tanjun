from __future__ import annotations

from tests.helpers.command_coverage.models import AssertionDepth, CoverageCell, LayerKind


def _depth_for_layer(layer: LayerKind) -> AssertionDepth:
    mapping = {
        LayerKind.BEHAVIOR_SPEC: AssertionDepth.DEFERRED,
        LayerKind.INTEGRATION: AssertionDepth.OUTCOME,
        LayerKind.UNIT_LOGIC: AssertionDepth.OUTPUT,
        LayerKind.UNIT_EXTENSION: AssertionDepth.DEFERRED,
        LayerKind.E2E_LIVE: AssertionDepth.LIVE_EMBED,
    }
    return mapping[layer]


def _cells(cases, *, source: str) -> list[CoverageCell]:
    return [
        CoverageCell(
            tree_path=case.tree_path,
            layer=case.layer,
            dimensions=dict(case.dimensions),
            assertion_depth=_depth_for_layer(case.layer),
            source=source,
        )
        for case in cases
    ]


def collect_matrix_expected_cells() -> list[CoverageCell]:
    from tests.helpers.command_matrix.iterators import iter_matrix_cases
    from tests.helpers.command_matrix.loader import load_all_group_configs

    cells: list[CoverageCell] = []
    for group_name in load_all_group_configs():
        for layer in (
            LayerKind.UNIT_LOGIC,
            LayerKind.INTEGRATION,
            LayerKind.BEHAVIOR_SPEC,
            LayerKind.E2E_LIVE,
            LayerKind.UNIT_EXTENSION,
        ):
            cases = iter_matrix_cases(group_name, layer)
            if cases:
                cells.extend(_cells(cases, source=f"matrix:expected:{layer.value}"))
    return cells


def collect_matrix_declared_cells() -> list[CoverageCell]:
    from tests.helpers.command_matrix.iterators import (
        iter_behavior_spec_cases,
        iter_e2e_live_cases,
        iter_integration_cases,
        iter_unit_cases,
    )

    cells: list[CoverageCell] = []
    cells.extend(_cells(iter_unit_cases(), source="pytest:unit_matrix"))
    cells.extend(_cells(iter_integration_cases(), source="pytest:integration_matrix"))
    cells.extend(_cells(iter_behavior_spec_cases(), source="pytest:behavior_spec_matrix"))
    cells.extend(_cells(iter_e2e_live_cases(), source="pytest:e2e_live_matrix"))
    from tests.helpers.command_matrix.iterators import iter_matrix_cases
    from tests.helpers.command_matrix.loader import load_all_group_configs

    for group_name in load_all_group_configs():
        cases = iter_matrix_cases(group_name, LayerKind.UNIT_EXTENSION)
        if cases:
            cells.extend(_cells(cases, source="pytest:unit_extension_matrix"))
    return cells


def collect_matrix_passed_cells() -> list[CoverageCell]:
    from tests.helpers.command_coverage.collectors.pytest_registry import collect_registry_cells

    return [cell for cell in collect_registry_cells() if cell.source == "pytest:passed"]


def collect_matrix_executed_cells() -> list[CoverageCell]:
    passed = collect_matrix_passed_cells()
    if passed:
        return passed
    return collect_matrix_declared_cells()


def collect_matrix_cells() -> list[CoverageCell]:
    return collect_matrix_executed_cells()
