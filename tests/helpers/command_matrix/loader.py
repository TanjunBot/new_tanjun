from __future__ import annotations

import itertools
from pathlib import Path
from typing import Any

import yaml

from diagnostics.tree import load_manifest
from tests.helpers.command_coverage.inventory import manifest_paths, root_group_for_path
from tests.helpers.command_matrix.models import MatrixCase
from tests.helpers.command_coverage.models import LayerKind

ROOT = Path(__file__).resolve().parents[3]
OVERRIDES_PATH = ROOT / "coverage" / "overrides.yaml"

PERMISSION_FULL = ["admin", "member", "restricted", "no_guild", "channel_deny_send", "channel_deny_embed"]
PERMISSION_BASIC = ["admin", "restricted"]
LOCALES = ["en-US", "de", "fr"]


def _load_yaml() -> dict[str, Any]:
    if not OVERRIDES_PATH.is_file():
        return {}
    return yaml.safe_load(OVERRIDES_PATH.read_text(encoding="utf-8")) or {}


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
        elif axis in dimensions:
            values.append(list(dimensions[axis]))
        else:
            values.append([defaults.get(axis, "")])
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


def _tree_paths_for_group(group_name: str, config: dict[str, Any]) -> list[str]:
    explicit = config.get("tree_paths")
    if explicit:
        return list(explicit)
    template = config.get("path_template")
    if not template:
        return [p for p in manifest_paths() if root_group_for_path(p) == group_name]
    dimensions = {k: list(v) for k, v in (config.get("dimensions") or {}).items()}
    if "command" in dimensions and "{command}" not in template:
        paths: list[str] = []
        for command in dimensions["command"]:
            paths.append(_path_from_template(template, {"command": command}))
        return paths
    paths_set: set[str] = set()
    axis_names = [k for k in dimensions if k not in {"permission", "locale", "target", "gif", "expression", "prompt_kind", "outcome", "attachment", "blacklist_kind", "wizard"}]
    if not axis_names:
        return [p for p in manifest_paths() if root_group_for_path(p) == group_name]
    for combo in itertools.product(*(dimensions[a] for a in axis_names)):
        dim_map = dict(zip(axis_names, combo))
        paths_set.add(_path_from_template(template, dim_map))
    return sorted(paths_set)


def _cases_for_layer(
    *,
    group_name: str,
    layer: LayerKind,
    config: dict[str, Any],
) -> list[MatrixCase]:
    dimensions = {k: list(v) for k, v in (config.get("dimensions") or {}).items()}
    path_template = config.get("path_template") or ""
    if not path_template and not config.get("tree_paths"):
        path_template = f"{group_name} {{command}}"
    layers = config.get("layers") or {}
    layer_specs = layers.get(layer.value) or layers.get(str(layer)) or []
    if not isinstance(layer_specs, list):
        layer_specs = [layer_specs]

    tree_paths = _tree_paths_for_group(group_name, config)
    per_path = bool(config.get("per_path", True))
    cases: list[MatrixCase] = []

    for spec in layer_specs:
        axes = list(spec.get("axes") or spec.get("product") or [])
        defaults = dict(spec.get("defaults") or spec.get("fixed") or {})
        overrides = dict(spec.get("overrides") or {})
        spec_per_path = spec.get("per_path", per_path)

        for dim_values in _expand_axes(dimensions, axes, defaults, overrides):
            path_axes = {k: v for k, v in dim_values.items() if k in dimensions and path_template and k in path_template}
            if path_template and path_axes and "{" in path_template:
                tree_path = _path_from_template(path_template, dim_values)
                cases.append(
                    MatrixCase(
                        group=group_name,
                        tree_path=tree_path,
                        dimensions=dict(dim_values),
                        layer=layer,
                    )
                )
            elif spec_per_path:
                for tree_path in tree_paths:
                    cases.append(
                        MatrixCase(
                            group=group_name,
                            tree_path=tree_path,
                            dimensions=dict(dim_values),
                            layer=layer,
                        )
                    )
            elif tree_paths:
                cases.append(
                    MatrixCase(
                        group=group_name,
                        tree_path=tree_paths[0],
                        dimensions=dict(dim_values),
                        layer=layer,
                    )
                )
    return cases


def load_group_config(group_name: str) -> dict[str, Any]:
    data = _load_yaml()
    groups = data.get("groups") or {}
    if group_name in groups:
        return dict(groups[group_name])
    return _default_group_config(group_name)


def load_all_group_configs() -> dict[str, dict[str, Any]]:
    data = _load_yaml()
    groups = dict(data.get("groups") or {})
    roots = load_manifest().get("roots") or []
    for root in roots:
        if root not in groups:
            groups[root] = _default_group_config(root)
    return groups


def _default_group_config(group_name: str) -> dict[str, Any]:
    paths = [p for p in manifest_paths() if root_group_for_path(p) == group_name]
    has_permission = group_name.startswith("admin_") or group_name in {
        "ai_name",
        "channel_name",
        "giveaway_name",
        "level_blacklist_name",
        "level_boosts_name",
        "level_config_name",
        "logs_name",
        "minigame_name",
    }
    permissions = PERMISSION_FULL if has_permission else PERMISSION_BASIC
    layers: dict[str, Any] = {
        "unit_logic": [{"axes": ["permission"], "per_path": True}],
        "integration": [{"axes": ["permission"], "per_path": True, "overrides": {"permission": ["admin"]}}],
        "behavior_spec": [{"axes": [], "per_path": True}],
        "e2e_live": [{"axes": ["permission"], "per_path": True, "overrides": {"permission": ["admin"]}}],
    }
    if group_name == "utility_help_name":
        layers = {
            "unit_logic": [{"axes": ["locale"], "per_path": True}],
            "integration": [{"axes": [], "per_path": True}],
            "behavior_spec": [{"axes": [], "per_path": True}],
            "e2e_live": [{"axes": ["locale"], "per_path": True, "overrides": {"locale": ["en-US"]}}],
        }
        return {
            "tree_paths": paths,
            "dimensions": {"locale": LOCALES, "permission": permissions},
            "per_path": True,
            "layers": layers,
        }
    if group_name == "math_name":
        return {
            "path_template": "math_name math_{command}_name",
            "dimensions": {
                "command": ["calc", "calculator", "faculty", "num2word", "plotfunction", "randomnumber"],
                "permission": permissions,
                "expression": ["valid", "invalid"],
            },
            "layers": {
                "unit_logic": [{"axes": ["command", "permission", "expression"]}],
                "integration": [{"axes": ["command"]}],
                "behavior_spec": [{"axes": ["command"]}],
                "e2e_live": [{"axes": ["command", "permission"], "overrides": {"permission": ["admin"], "expression": ["valid"]}}],
            },
        }
    return {
        "tree_paths": paths,
        "dimensions": {"permission": permissions},
        "per_path": True,
        "layers": layers,
    }


def iter_group_cases(group_name: str, layer: LayerKind) -> list[MatrixCase]:
    config = load_group_config(group_name)
    return _cases_for_layer(group_name=group_name, layer=layer, config=config)
