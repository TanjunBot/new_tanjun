from __future__ import annotations

from tests.helpers.command_coverage.models import CoverageCell

_REGISTRY: list[CoverageCell] = []


def coverage_case(cell: CoverageCell):
    def decorator(func):
        _REGISTRY.append(cell)
        func.__coverage_cell__ = cell  # type: ignore[attr-defined]
        return func

    return decorator


def register_coverage_cell(cell: CoverageCell) -> None:
    _REGISTRY.append(cell)


def collect_registry_cells() -> list[CoverageCell]:
    return list(_REGISTRY)
