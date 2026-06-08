from __future__ import annotations

from tests.helpers.command_coverage.collectors.matrix import collect_matrix_cells
from tests.helpers.command_coverage.models import LayerKind


def collect_e2e_live_cells() -> list:
    return [c for c in collect_matrix_cells() if c.layer == LayerKind.E2E_LIVE]
