from __future__ import annotations

from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from typing import Any


@dataclass
class CheckOutcome:
    check_id: str
    passed: bool
    message: str = ""
    skipped: bool = False
    skip_allowed: bool = False


@dataclass
class PhaseResult:
    phase_id: str
    title: str
    outcomes: list[CheckOutcome] = field(default_factory=list)

    @property
    def passed(self) -> int:
        return sum(1 for o in self.outcomes if o.passed and not o.skipped)

    @property
    def failed(self) -> int:
        return sum(
            1
            for o in self.outcomes
            if not o.passed and not (o.skipped and o.skip_allowed)
        )

    @property
    def skipped(self) -> int:
        return sum(1 for o in self.outcomes if o.skipped)


@dataclass
class DiagnosticsSummary:
    phases: list[PhaseResult] = field(default_factory=list)
    aborted: bool = False
    abort_message: str = ""

    @property
    def total_passed(self) -> int:
        return sum(p.passed for p in self.phases)

    @property
    def total_failed(self) -> int:
        return sum(p.failed for p in self.phases)

    @property
    def total_skipped(self) -> int:
        return sum(p.skipped for p in self.phases)

    @property
    def unauthorized_skips(self) -> int:
        return sum(
            1
            for phase in self.phases
            for outcome in phase.outcomes
            if outcome.skipped and not outcome.skip_allowed
        )

    @property
    def ok(self) -> bool:
        return (
            not self.aborted
            and self.total_failed == 0
            and self.unauthorized_skips == 0
        )


AssertionFn = Callable[[Any, dict[str, Any]], Awaitable[None]]
KwargsFactory = Callable[[], dict[str, Any]]


@dataclass
class CommandBehaviorSpec:
    id: str
    extension: str
    group_cls: type
    method_name: str
    tree_path: str = ""
    extra_kwargs: dict[str, Any] | KwargsFactory | None = None
    skip_reason: str | None = None
    assertions: AssertionFn | None = None
    patch_targets: tuple[str, ...] = ()
    patch_exclude: tuple[str, ...] = ()
