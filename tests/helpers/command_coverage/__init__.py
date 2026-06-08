from __future__ import annotations

from tests.helpers.command_coverage.models import CoverageCell, CoverageReport, LayerKind

__all__ = [
    "CoverageCell",
    "CoverageReport",
    "LayerKind",
    "build_coverage_report",
    "check_thresholds",
    "format_text_report",
]


def build_coverage_report(*args, **kwargs):
    from tests.helpers.command_coverage.report import build_coverage_report as _fn

    return _fn(*args, **kwargs)


def check_thresholds(*args, **kwargs):
    from tests.helpers.command_coverage.gate import check_thresholds as _fn

    return _fn(*args, **kwargs)


def format_text_report(*args, **kwargs):
    from tests.helpers.command_coverage.reporter import format_text_report as _fn

    return _fn(*args, **kwargs)
