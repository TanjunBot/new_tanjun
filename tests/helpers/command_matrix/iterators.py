from __future__ import annotations

import fnmatch
import os

from diagnostics.tree import load_manifest

from tests.helpers.command_coverage.models import LayerKind
from tests.helpers.command_matrix.loader import load_all_group_configs
from tests.helpers.command_matrix.models import MatrixCase
from tests.helpers.command_matrix.loader import iter_group_cases as _iter_group_cases


def iter_all_groups() -> list[str]:
    return list(load_manifest().get("roots") or [])


def iter_matrix_cases(group: str, layer: LayerKind) -> list[MatrixCase]:
    return _iter_group_cases(group, layer)


def iter_unit_cases(group: str | None = None) -> list[MatrixCase]:
    return _collect(LayerKind.UNIT_LOGIC, group)


def iter_integration_cases(group: str | None = None) -> list[MatrixCase]:
    return _collect(LayerKind.INTEGRATION, group)


def iter_behavior_spec_cases(group: str | None = None) -> list[MatrixCase]:
    return _collect(LayerKind.BEHAVIOR_SPEC, group)


def iter_e2e_live_cases(group: str | None = None) -> list[MatrixCase]:
    return _collect(LayerKind.E2E_LIVE, group)


def _collect(layer: LayerKind, group: str | None) -> list[MatrixCase]:
    groups = [group] if group else iter_all_groups()
    cases: list[MatrixCase] = []
    for name in groups:
        cases.extend(_iter_group_cases(name, layer))
    if layer == LayerKind.E2E_LIVE:
        domain_filter = os.getenv("TANJUN_E2E_DOMAIN_FILTER", "").strip()
        if domain_filter:
            cases = [c for c in cases if domain_filter in c.group or domain_filter in c.tree_path]
        case_filter = os.getenv("TANJUN_E2E_CASE_FILTER", "").strip()
        if case_filter:
            cases = [
                c
                for c in cases
                if case_filter in c.id or fnmatch.fnmatch(c.id, case_filter)
            ]
    return cases


def iter_all_e2e_live_cases() -> list[MatrixCase]:
    return iter_e2e_live_cases()
