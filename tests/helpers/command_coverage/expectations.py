from __future__ import annotations

import itertools
from pathlib import Path
from typing import Any

import yaml

from tests.helpers.command_coverage.inventory import (
    build_inventory,
    detect_permission_checks_for_paths,
    manifest_paths,
    root_group_for_path,
)
from tests.helpers.command_coverage.models import AssertionDepth, CoverageCell, LayerKind

ROOT = Path(__file__).resolve().parents[3]
OVERRIDES_PATH = ROOT / "coverage" / "overrides.yaml"


def _load_yaml(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def _expand_axes(
    dimensions: dict[str, list[str]],
    axes: list[str],
    defaults: dict[str, str] | None = None,
    overrides: dict[str, list[str]] | None = None,
) -> list[dict[str, str]]:
    defaults = defaults or {}
    overrides = overrides or {}
    values: list[list[str]] = []
    for axis in axes:
        if axis in overrides:
            values.append(list(overrides[axis]))
        else:
            values.append(list(dimensions[axis]))
    cells: list[dict[str, str]] = []
    for combo in itertools.product(*values):
        cell = dict(defaults)
        cell.update(dict(zip(axes, combo)))
        cells.append(cell)
    return cells


def _path_from_template(template: str, dimensions: dict[str, str]) -> str:
    try:
        return template.format(**dimensions)
    except KeyError:
        return template


def _cells_for_layer_spec(
    *,
    group_name: str,
    layer: LayerKind,
    layer_specs: list[dict[str, Any]],
    dimensions: dict[str, list[str]],
    path_template: str,
    tree_paths: list[str] | None = None,
    per_path: bool = True,
) -> list[CoverageCell]:
    from tests.helpers.command_matrix.loader import _tree_paths_for_group

    config = {
        "path_template": path_template,
        "dimensions": dimensions,
        "tree_paths": tree_paths,
        "per_path": per_path,
    }
    tree_paths = _tree_paths_for_group(group_name, config)
    cells: list[CoverageCell] = []
    for spec in layer_specs:
        axes = list(spec.get("axes") or spec.get("product") or [])
        defaults = dict(spec.get("defaults") or spec.get("fixed") or {})
        overrides = dict(spec.get("overrides") or {})
        spec_per_path = spec.get("per_path", per_path)
        for dim_values in _expand_axes(dimensions, axes, defaults, overrides):
            if path_template and "{" in path_template and any(k in path_template for k in dim_values):
                tree_path = _path_from_template(path_template, dim_values)
                cells.append(
                    CoverageCell(
                        tree_path=tree_path,
                        layer=layer,
                        dimensions=dict(dim_values),
                        assertion_depth=_default_depth_for_layer(layer),
                        source=f"override:{group_name}",
                    )
                )
            elif spec_per_path:
                for tree_path in tree_paths:
                    cells.append(
                        CoverageCell(
                            tree_path=tree_path,
                            layer=layer,
                            dimensions=dict(dim_values),
                            assertion_depth=_default_depth_for_layer(layer),
                            source=f"override:{group_name}",
                        )
                    )
            elif tree_paths:
                cells.append(
                    CoverageCell(
                        tree_path=tree_paths[0],
                        layer=layer,
                        dimensions=dict(dim_values),
                        assertion_depth=_default_depth_for_layer(layer),
                        source=f"override:{group_name}",
                    )
                )
    return cells


def _default_depth_for_layer(layer: LayerKind) -> AssertionDepth:
    mapping = {
        LayerKind.BEHAVIOR_SPEC: AssertionDepth.DEFERRED,
        LayerKind.INTEGRATION: AssertionDepth.OUTCOME,
        LayerKind.UNIT_LOGIC: AssertionDepth.OUTPUT,
        LayerKind.UNIT_EXTENSION: AssertionDepth.DEFERRED,
        LayerKind.E2E_LIVE: AssertionDepth.LIVE_EMBED,
    }
    return mapping[layer]


def _auto_defaults_for_path(
    tree_path: str,
    *,
    has_permission_checks: bool,
    has_integration_test: bool,
) -> list[CoverageCell]:
    cells: list[CoverageCell] = []
    cells.append(
        CoverageCell(
            tree_path=tree_path,
            layer=LayerKind.BEHAVIOR_SPEC,
            dimensions={},
            assertion_depth=AssertionDepth.DEFERRED,
            source="auto",
        )
    )
    if has_permission_checks:
        profiles = ["admin", "restricted"]
    elif has_integration_test:
        profiles = ["admin"]
    else:
        return cells
    for profile in profiles:
        cells.append(
            CoverageCell(
                tree_path=tree_path,
                layer=LayerKind.INTEGRATION,
                dimensions={"permission": profile},
                assertion_depth=AssertionDepth.OUTCOME,
                source="auto",
            )
        )
    return cells


def build_expected_cells(
    *,
    integration_paths: set[str] | None = None,
    permission_paths: dict[str, bool] | None = None,
) -> list[CoverageCell]:
    integration_paths = integration_paths or set()
    permission_paths = permission_paths or detect_permission_checks_for_paths()
    overrides = _load_yaml(OVERRIDES_PATH)
    group_configs = overrides.get("groups") or {}

    cells: list[CoverageCell] = []
    configured_paths: set[str] = set()

    for group_name, config in group_configs.items():
        dimensions = {k: list(v) for k, v in (config.get("dimensions") or {}).items()}
        path_template = config.get("path_template") or ""
        tree_paths = config.get("tree_paths")
        if not path_template and not tree_paths:
            path_template = f"{group_name} {{command}}_name"
        per_path = bool(config.get("per_path", True))
        layers = config.get("layers") or config.get("layer_map") or {}
        for layer_name, layer_specs in layers.items():
            layer = LayerKind(layer_name)
            if not isinstance(layer_specs, list):
                layer_specs = [layer_specs]
            layer_cells = _cells_for_layer_spec(
                group_name=group_name,
                layer=layer,
                layer_specs=layer_specs,
                dimensions=dimensions,
                path_template=path_template,
                tree_paths=list(tree_paths) if tree_paths else None,
                per_path=per_path,
            )
            cells.extend(layer_cells)
            configured_paths.update(c.tree_path for c in layer_cells)

    for tree_path in manifest_paths():
        if any(c.tree_path == tree_path for c in cells):
            continue
        if root_group_for_path(tree_path) in group_configs:
            continue
        cells.extend(
            _auto_defaults_for_path(
                tree_path,
                has_permission_checks=permission_paths.get(tree_path, False),
                has_integration_test=tree_path in integration_paths,
            )
        )

    return cells


def build_report_groups(expected: list[CoverageCell]) -> list[str]:
    roots = sorted({root_group_for_path(c.tree_path) for c in expected})
    return roots
