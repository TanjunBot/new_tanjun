from __future__ import annotations

from collections import defaultdict

from tests.helpers.command_coverage.collectors import collect_all_cells
from tests.helpers.command_coverage.expectations import build_expected_cells
from tests.helpers.command_coverage.inventory import (
    build_inventory,
    detect_permission_checks_for_paths,
    manifest_paths,
    root_group_for_path,
)
from tests.helpers.command_coverage.models import (
    AssertionDepth,
    CommandPathSummary,
    CoverageCell,
    CoverageReport,
    GroupCoverageSummary,
    LayerKind,
    LayerSummary,
)


def _integration_paths_from_actual(actual: list[CoverageCell]) -> set[str]:
    return {
        cell.tree_path
        for cell in actual
        if cell.layer == LayerKind.INTEGRATION
    }


def _infer_dimensions_from_path(tree_path: str) -> dict[str, str]:
    leaf = tree_path.rsplit(" ", 1)[-1]
    if leaf.startswith("fun_") and leaf.endswith("_name"):
        return {"action": leaf.removeprefix("fun_").removesuffix("_name")}
    return {}


def _is_covered(expected: CoverageCell, actual: list[CoverageCell]) -> bool:
    for cell in actual:
        if cell.tree_path != expected.tree_path or cell.layer != expected.layer:
            continue
        if cell.matches_expected(expected):
            return True
        if cell.dimensions:
            continue
        if expected.dimensions.get("variant") == "smoke" and not expected.dimensions.keys() - {"variant"}:
            return True
    return False


def _permission_denial_covered(tree_path: str, permission: str, actual: list[CoverageCell]) -> bool:
    for cell in actual:
        if cell.tree_path != tree_path or cell.layer != LayerKind.INTEGRATION:
            continue
        if cell.dimensions.get("permission") != permission:
            continue
        if AssertionDepth.rank(cell.assertion_depth) >= AssertionDepth.rank(AssertionDepth.OUTCOME):
            return True
    return False


def build_coverage_report(
    *,
    actual: list[CoverageCell] | None = None,
    expected: list[CoverageCell] | None = None,
    filter_group: str | None = None,
    filter_path: str | None = None,
    filter_layer: LayerKind | None = None,
) -> CoverageReport:
    actual = actual if actual is not None else collect_all_cells()
    permission_paths = detect_permission_checks_for_paths()
    if expected is None:
        expected = build_expected_cells(
            integration_paths=_integration_paths_from_actual(actual),
            permission_paths=permission_paths,
        )

    if filter_group:
        expected = [c for c in expected if root_group_for_path(c.tree_path) == filter_group]
        actual = [c for c in actual if root_group_for_path(c.tree_path) == filter_group]
    if filter_path:
        expected = [c for c in expected if c.tree_path == filter_path]
        actual = [c for c in actual if c.tree_path == filter_path]
    if filter_layer:
        expected = [c for c in expected if c.layer == filter_layer]
        actual = [c for c in actual if c.layer == filter_layer]

    paths = manifest_paths()
    paths_with_test = {
        cell.tree_path
        for cell in actual
        if cell.tree_path in paths
    }

    expected_by_group: dict[str, list[CoverageCell]] = defaultdict(list)
    for cell in expected:
        expected_by_group[root_group_for_path(cell.tree_path)].append(cell)

    groups: list[GroupCoverageSummary] = []
    for root_group in sorted(expected_by_group):
        group_expected = expected_by_group[root_group]
        group_paths = sorted({c.tree_path for c in group_expected})

        layer_names = sorted({c.layer for c in group_expected}, key=lambda layer: layer.value)
        layer_summaries: list[LayerSummary] = []
        for layer in layer_names:
            layer_expected = [c for c in group_expected if c.layer == layer]
            missing = [c for c in layer_expected if not _is_covered(c, actual)]
            layer_summaries.append(
                LayerSummary(
                    layer=layer,
                    expected=len(layer_expected),
                    covered=len(layer_expected) - len(missing),
                    missing=missing,
                )
            )

        denial_expected = 0
        denial_covered = 0
        denial_missing: list[str] = []
        for tree_path in group_paths:
            if not permission_paths.get(tree_path, False):
                continue
            for permission in ("restricted",):
                denial_expected += 1
                key = f"{tree_path}/{permission}"
                if _permission_denial_covered(tree_path, permission, actual):
                    denial_covered += 1
                else:
                    denial_missing.append(key)

        groups.append(
            GroupCoverageSummary(
                root_group=root_group,
                tree_paths=group_paths,
                layers=layer_summaries,
                permission_denial_expected=denial_expected,
                permission_denial_covered=denial_covered,
                permission_denial_missing=denial_missing,
            )
        )

    expected_by_path: dict[str, list[CoverageCell]] = defaultdict(list)
    for cell in expected:
        expected_by_path[cell.tree_path].append(cell)

    command_summaries: list[CommandPathSummary] = []
    for tree_path in sorted(expected_by_path):
        path_expected = expected_by_path[tree_path]
        missing = [c for c in path_expected if not _is_covered(c, actual)]
        command_summaries.append(
            CommandPathSummary(
                tree_path=tree_path,
                root_group=root_group_for_path(tree_path),
                expected=len(path_expected),
                covered=len(path_expected) - len(missing),
                missing=missing,
            )
        )

    return CoverageReport(
        inventory=build_inventory(),
        expected=expected,
        actual=actual,
        groups=groups,
        commands=command_summaries,
        paths_with_any_test=len(paths_with_test),
        total_manifest_paths=len(paths),
    )
