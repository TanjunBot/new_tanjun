from __future__ import annotations

from tests.helpers.command_coverage.collectors.behavior_specs import collect_behavior_spec_cells
from tests.helpers.command_coverage.collectors.e2e_live import collect_e2e_live_cells
from tests.helpers.command_coverage.collectors.matrix import (
    collect_matrix_cells,
    collect_matrix_declared_cells,
    collect_matrix_executed_cells,
    collect_matrix_expected_cells,
    collect_matrix_passed_cells,
)
from tests.helpers.command_coverage.collectors.profiles import collect_integration_profile_cells
from tests.helpers.command_coverage.collectors.pytest_registry import collect_registry_cells

__all__ = [
    "collect_all_cells",
    "collect_behavior_spec_cells",
    "collect_e2e_live_cells",
    "collect_matrix_cells",
    "collect_matrix_declared_cells",
    "collect_matrix_executed_cells",
    "collect_matrix_expected_cells",
    "collect_matrix_passed_cells",
    "collect_integration_profile_cells",
    "collect_registry_cells",
]


def collect_all_cells() -> list:
    from tests.helpers.command_coverage.models import CoverageCell

    cells: list[CoverageCell] = []
    cells.extend(collect_behavior_spec_cells())
    cells.extend(collect_matrix_cells())
    cells.extend(collect_integration_profile_cells())
    if not collect_matrix_passed_cells():
        cells.extend(collect_registry_cells())
    return cells
