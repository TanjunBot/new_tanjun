from __future__ import annotations

from typing import Protocol

from tests.helpers.command_coverage.models import CoverageCell


class CoverageCollector(Protocol):
    def collect(self) -> list[CoverageCell]: ...
