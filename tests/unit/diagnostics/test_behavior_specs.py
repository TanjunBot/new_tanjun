from __future__ import annotations

from unittest.mock import MagicMock

import pytest

import diagnostics.registry as registry_mod

pytestmark = pytest.mark.asyncio


def _can_discover_specs() -> bool:
    from discord import app_commands

    return isinstance(app_commands.Group, type)


def pytest_generate_tests(metafunc: pytest.Metafunc) -> None:
    if "behavior_spec" not in metafunc.fixturenames:
        return
    if not _can_discover_specs():
        return
    registry_mod._specs_cache = None
    from diagnostics.registry import all_specs

    specs = all_specs()
    metafunc.parametrize("behavior_spec", specs, ids=[s.id for s in specs])


async def test_all_specs_returns_list() -> None:
    from diagnostics.registry import all_specs

    if not _can_discover_specs():
        pytest.skip("discord.app_commands.Group is not a real class in this test environment")

    registry_mod._specs_cache = None
    specs = all_specs()
    assert isinstance(specs, list)
    assert len(specs) > 50


async def test_run_spec_skips_specs_with_reason() -> None:
    from diagnostics.models import CheckOutcome, CommandBehaviorSpec
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


async def test_run_spec_handles_unknown_spec() -> None:
    from diagnostics.models import CheckOutcome, CommandBehaviorSpec
    from diagnostics.registry import run_spec

    spec = CommandBehaviorSpec(
        id="test.UnknownGroup.unknown_method",
        extension="extensions.administration",
        group_cls=object,
        method_name="nope",
    )
    outcome = await run_spec(spec, MagicMock())
    assert isinstance(outcome, CheckOutcome)
    assert not outcome.passed


async def test_behavior_spec(behavior_spec: object) -> None:
    from diagnostics.registry import run_spec

    if not _can_discover_specs():
        pytest.skip("discord.app_commands.Group is not a real class in this test environment")

    outcome = await run_spec(behavior_spec, MagicMock())  # type: ignore[arg-type]
    assert outcome.passed or outcome.skipped, f"{behavior_spec.id}: {outcome.message}"  # type: ignore[attr-defined]


async def test_phase_result_counts() -> None:
    from diagnostics.models import CheckOutcome, PhaseResult

    phase = PhaseResult("test", "Test Phase")
    phase.outcomes.append(CheckOutcome("check.a", True, "OK"))
    phase.outcomes.append(CheckOutcome("check.b", False, "FAIL"))
    phase.outcomes.append(CheckOutcome("check.c", True, "SKIPPED", skipped=True))

    assert phase.passed == 1
    assert phase.failed == 1
    assert phase.skipped == 1


async def test_diagnostics_summary_ok() -> None:
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
    from diagnostics.models import CheckOutcome, DiagnosticsSummary, PhaseResult

    s = DiagnosticsSummary()
    p = PhaseResult("test", "Test")
    p.outcomes.append(CheckOutcome("a", True))
    p.outcomes.append(CheckOutcome("b", False, "boom"))
    s.phases.append(p)
    assert not s.ok
    assert s.total_failed == 1
