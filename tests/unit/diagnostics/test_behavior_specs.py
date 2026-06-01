from __future__ import annotations

from unittest.mock import MagicMock

import pytest

pytestmark = pytest.mark.asyncio


async def test_all_specs_returns_list() -> None:
    """all_specs() returns a list (may be empty or have specs depending on env)."""
    from diagnostics.registry import all_specs

    specs = all_specs()
    assert isinstance(specs, list)


async def test_run_spec_skips_specs_with_reason() -> None:
    """run_spec returns a skipped outcome when spec has skip_reason."""
    from diagnostics.models import CommandBehaviorSpec, CheckOutcome
    from diagnostics.registry import run_spec

    spec = CommandBehaviorSpec(
        id="test.skip_me",
        extension="extensions.administration",
        group_cls=MagicMock,
        method_name="test_bot",
        skip_reason="Testing skip behavior",
    )
    outcome = await run_spec(spec, MagicMock())
    assert isinstance(outcome, CheckOutcome)
    assert outcome.skipped


async def test_phase_result_counts() -> None:
    """PhaseResult correctly tracks passed/failed/skipped."""
    from diagnostics.models import CheckOutcome, PhaseResult

    phase = PhaseResult("test", "Test Phase")
    phase.outcomes.append(CheckOutcome("check.a", True, "OK"))
    phase.outcomes.append(CheckOutcome("check.b", False, "FAIL"))
    phase.outcomes.append(CheckOutcome("check.c", True, "SKIPPED", skipped=True))

    assert phase.passed == 1
    assert phase.failed == 1
    assert phase.skipped == 1


async def test_diagnostics_summary_ok() -> None:
    """DiagnosticsSummary.ok is True when nothing failed."""
    from diagnostics.models import CheckOutcome, DiagnosticsSummary, PhaseResult

    s = DiagnosticsSummary()
    p = PhaseResult("test", "Test")
    p.outcomes.append(CheckOutcome("a", True))
    p.outcomes.append(CheckOutcome("b", True))
    p.outcomes.append(CheckOutcome("c", True, skipped=True))
    s.phases.append(p)
    assert s.ok
    assert s.total_passed == 2
    assert s.total_failed == 0
    assert s.total_skipped == 1


async def test_diagnostics_summary_failed() -> None:
    """DiagnosticsSummary.ok is False when anything failed."""
    from diagnostics.models import CheckOutcome, DiagnosticsSummary, PhaseResult

    s = DiagnosticsSummary()
    p = PhaseResult("test", "Test")
    p.outcomes.append(CheckOutcome("a", True))
    p.outcomes.append(CheckOutcome("b", False, "boom"))
    s.phases.append(p)
    assert not s.ok
    assert s.total_failed == 1