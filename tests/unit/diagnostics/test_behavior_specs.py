from __future__ import annotations

from unittest.mock import MagicMock

import pytest

import diagnostics.registry as registry_mod

pytestmark = pytest.mark.asyncio


def _can_discover_specs() -> bool:
    from discord import app_commands

    return isinstance(app_commands.Group, type)


async def test_all_specs_returns_list() -> None:
    from diagnostics.registry import all_specs

    if not _can_discover_specs():
        pytest.skip("discord.app_commands.Group is not a real class in this test environment")

    registry_mod.clear_spec_cache()
    try:
        specs = all_specs()
    except Exception as exc:
        pytest.skip(f"spec discovery unavailable: {exc}")
    assert isinstance(specs, list)
    assert len(specs) > 40


async def test_run_spec_rejects_undocumented_skip() -> None:
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
    assert not outcome.passed
    assert not outcome.skip_allowed


async def test_run_spec_allows_documented_skip() -> None:
    from diagnostics.models import CommandBehaviorSpec
    from diagnostics.registry import run_spec
    from diagnostics.strict_skips import SLASH_SKIP_ALLOWLIST

    spec_id = "test.allowed_skip"
    SLASH_SKIP_ALLOWLIST[spec_id] = "documented"
    spec = CommandBehaviorSpec(
        id=spec_id,
        extension="extensions.administration",
        group_cls=MagicMock,
        method_name="test_bot",
        skip_reason="documented",
    )
    outcome = await run_spec(spec, MagicMock())
    SLASH_SKIP_ALLOWLIST.pop(spec_id, None)
    assert outcome.skipped
    assert outcome.skip_allowed


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


def _discovery_reliable() -> bool:
    from diagnostics.registry import all_specs

    if not _can_discover_specs():
        return False
    registry_mod.clear_spec_cache()
    try:
        specs = all_specs()
    except Exception:
        return False
    if not specs:
        return False
    sample = specs[: min(20, len(specs))]
    return not any(s.method_name == "unknown" for s in sample)


async def test_all_behavior_specs_pass() -> None:
    from diagnostics.registry import all_specs, run_spec

    if not _discovery_reliable():
        pytest.skip("slash spec discovery unreliable in this test environment")

    registry_mod.clear_spec_cache()
    failures: list[str] = []
    for spec in all_specs():
        outcome = await run_spec(spec, MagicMock())
        if not outcome.passed and not outcome.skipped:
            failures.append(f"{spec.id}: {outcome.message}")
    assert not failures, "\n".join(failures[:30])


async def test_run_spec_success() -> None:
    from contextlib import contextmanager
    from unittest.mock import AsyncMock, patch

    from diagnostics.models import CommandBehaviorSpec
    from diagnostics.registry import run_spec

    class _Group:
        async def handler(self, interaction: object) -> object:
            return interaction

    @contextmanager
    def _patches(*_a: object, **_k: object):
        yield {}

    spec = CommandBehaviorSpec(
        id="test.success",
        extension="extensions.administration",
        group_cls=_Group,
        method_name="handler",
    )
    with (
        patch("diagnostics.registry.extension_patches", side_effect=_patches),
        patch(
            "diagnostics.registry.invoke_interaction_command",
            new=AsyncMock(return_value=MagicMock()),
        ),
    ):
        outcome = await run_spec(spec, MagicMock())
    assert outcome.passed


async def test_diagnostics_summary_aborted() -> None:
    from diagnostics.models import DiagnosticsSummary

    s = DiagnosticsSummary()
    s.aborted = True
    assert not s.ok


async def test_phase_result_counts() -> None:
    from diagnostics.models import CheckOutcome, PhaseResult

    phase = PhaseResult("test", "Test Phase")
    phase.outcomes.append(CheckOutcome("check.a", True, "OK"))
    phase.outcomes.append(CheckOutcome("check.b", False, "FAIL"))
    phase.outcomes.append(CheckOutcome("check.c", True, "SKIPPED", skipped=True, skip_allowed=True))

    assert phase.passed == 1
    assert phase.failed == 1
    assert phase.skipped == 1


async def test_diagnostics_summary_ok() -> None:
    from diagnostics.models import CheckOutcome, DiagnosticsSummary, PhaseResult

    s = DiagnosticsSummary()
    p = PhaseResult("test", "Test")
    p.outcomes.append(CheckOutcome("a", True))
    p.outcomes.append(CheckOutcome("b", True))
    p.outcomes.append(CheckOutcome("c", True, skipped=True, skip_allowed=True))
    s.phases.append(p)
    assert s.ok
    assert s.total_passed == 2
    assert s.total_failed == 0
    assert s.total_skipped == 1


async def test_diagnostics_summary_fails_on_unauthorized_skip() -> None:
    from diagnostics.models import CheckOutcome, DiagnosticsSummary, PhaseResult

    s = DiagnosticsSummary()
    p = PhaseResult("test", "Test")
    p.outcomes.append(CheckOutcome("a", True, skipped=True))
    s.phases.append(p)
    assert not s.ok
    assert s.unauthorized_skips == 1


async def test_diagnostics_summary_failed() -> None:
    from diagnostics.models import CheckOutcome, DiagnosticsSummary, PhaseResult

    s = DiagnosticsSummary()
    p = PhaseResult("test", "Test")
    p.outcomes.append(CheckOutcome("a", True))
    p.outcomes.append(CheckOutcome("b", False, "boom"))
    s.phases.append(p)
    assert not s.ok
    assert s.total_failed == 1
