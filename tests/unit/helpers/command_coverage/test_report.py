from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from tests.helpers.command_coverage.collectors.matrix import collect_matrix_declared_cells
from tests.helpers.command_coverage.inventory import root_group_for_path
from tests.helpers.command_coverage.models import LayerKind
from tests.helpers.command_coverage.report import build_coverage_report

ROOT = Path(__file__).resolve().parents[4]


def _funcmd_matrix_cells():
    return [
        cell
        for cell in collect_matrix_declared_cells()
        if root_group_for_path(cell.tree_path) == "funcmd_name"
    ]


def test_fun_group_unit_logic_fully_covered() -> None:
    actual = _funcmd_matrix_cells()
    report = build_coverage_report(actual=actual, filter_group="funcmd_name")
    unit = next(layer for layer in report.groups[0].layers if layer.layer == LayerKind.UNIT_LOGIC)
    assert unit.expected == 360
    assert unit.covered == 360


def test_coverage_gate_script_passes() -> None:
    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "report_command_coverage.py"),
            "--all",
            "--fail-under-config",
            str(ROOT / "coverage" / "thresholds.yaml"),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
