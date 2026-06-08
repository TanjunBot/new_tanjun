from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import yaml

from tests.helpers.command_coverage.models import CoverageReport, LayerKind, ThresholdViolation

ROOT = Path(__file__).resolve().parents[3]


def _load_thresholds(path: Path) -> dict[str, Any]:
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def _live_e2e_available() -> bool:
    token = os.getenv("TANJUN_TEST_BOT_TOKEN", "").strip()
    return bool(token)


def check_thresholds(
    report: CoverageReport,
    config_path: Path | None = None,
) -> list[ThresholdViolation]:
    config_path = config_path or (ROOT / "coverage" / "thresholds.yaml")
    config = _load_thresholds(config_path)
    defaults = config.get("defaults") or {}
    group_thresholds = config.get("groups") or {}
    global_cfg = config.get("global") or {}

    violations: list[ThresholdViolation] = []

    for group in report.groups:
        group_cfg = group_thresholds.get(group.root_group) or {}
        for layer_summary in group.layers:
            layer_name = layer_summary.layer.value
            if layer_summary.layer == LayerKind.E2E_LIVE and not _live_e2e_available():
                continue
            threshold = group_cfg.get(layer_name, defaults.get(layer_name))
            if threshold is None:
                continue
            if layer_summary.percent < float(threshold):
                violations.append(
                    ThresholdViolation(
                        check_id=f"{group.root_group}.{layer_name}",
                        message=(
                            f"{group.root_group} {layer_name}: "
                            f"{layer_summary.percent:.1f}% < {threshold}% "
                            f"({layer_summary.covered}/{layer_summary.expected})"
                        ),
                    )
                )

        denial_threshold = group_cfg.get("permission_denial", defaults.get("permission_denial"))
        if denial_threshold is not None and group.permission_denial_expected > 0:
            if group.permission_denial_percent < float(denial_threshold):
                violations.append(
                    ThresholdViolation(
                        check_id=f"{group.root_group}.permission_denial",
                        message=(
                            f"{group.root_group} permission_denial: "
                            f"{group.permission_denial_percent:.1f}% < {denial_threshold}% "
                            f"({group.permission_denial_covered}/{group.permission_denial_expected})"
                        ),
                    )
                )

    min_any = global_cfg.get("min_manifest_paths_with_any_test")
    if min_any is not None and report.total_manifest_paths > 0:
        percent = 100.0 * report.paths_with_any_test / report.total_manifest_paths
        if percent < float(min_any):
            violations.append(
                ThresholdViolation(
                    check_id="global.min_manifest_paths_with_any_test",
                    message=(
                        f"manifest paths with any test: {percent:.1f}% < {min_any}% "
                        f"({report.paths_with_any_test}/{report.total_manifest_paths})"
                    ),
                )
            )

    min_command = global_cfg.get("min_command_coverage")
    if min_command is not None:
        for command in report.commands:
            if command.percent < float(min_command):
                leaf = command.tree_path.rsplit(" ", 1)[-1]
                violations.append(
                    ThresholdViolation(
                        check_id=f"command.{leaf}",
                        message=(
                            f"{command.tree_path}: {command.percent:.1f}% < {min_command}% "
                            f"({command.covered}/{command.expected})"
                        ),
                    )
                )

    return violations
