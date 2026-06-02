from __future__ import annotations

from contextlib import ExitStack
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from diagnostics.models import CheckOutcome, DiagnosticsSummary, PhaseResult
from diagnostics.runner import DiagnosticsRunner, _PHASE_PLAN


def _make_runner() -> DiagnosticsRunner:
    bot = MagicMock()
    ctx = MagicMock()
    thread = MagicMock()
    thread.send = AsyncMock()
    status = MagicMock()
    status.edit = AsyncMock()
    return DiagnosticsRunner(bot, ctx, thread, status, locale="en")


def test_progress_bar_zero_total() -> None:
    assert "[░░░░░░░░░░░░] 0/0" in DiagnosticsRunner._progress_bar(0, 0)


def test_progress_bar_full() -> None:
    bar = DiagnosticsRunner._progress_bar(9, 9)
    assert "9/9" in bar
    assert "█" in bar


@pytest.mark.asyncio
async def test_thread_send_truncates_long_content() -> None:
    runner = _make_runner()
    await runner._thread_send("x" * 2000)
    sent = runner.thread.send.await_args[0][0]
    assert len(sent) <= 1901
    assert sent.endswith("…")


@pytest.mark.asyncio
async def test_thread_send_lines_chunks() -> None:
    runner = _make_runner()
    await runner._thread_send_lines(["a" * 1000, "b" * 1000])
    assert runner.thread.send.await_count >= 2


@pytest.mark.asyncio
async def test_report_phase_compact_passed_groups() -> None:
    runner = _make_runner()
    phase = PhaseResult("E", "Slash handler behaviors")
    phase.outcomes.append(CheckOutcome("prefix.admin.sync", True, "OK"))
    phase.outcomes.append(CheckOutcome("prefix.admin.fail", False, "boom"))
    await runner._report_phase(phase, compact_passed=True)
    combined = " ".join(call[0][0] for call in runner.thread.send.await_args_list)
    assert "FAIL" in combined


@pytest.mark.asyncio
async def test_run_all_happy_path() -> None:
    runner = _make_runner()

    async def _fake_phase(_idx: int) -> None:
        phase = PhaseResult("X", "Test")
        phase.outcomes.append(CheckOutcome("x.ok", True, "OK"))
        runner.summary.phases.append(phase)

    phase_attrs = (
        "_run_phase_a_infra",
        "_run_phase_b_health",
        "_run_phase_c_loops",
        "_run_phase_d_tree",
        "_run_phase_e_handlers",
        "_run_phase_f_extensions",
        "_run_phase_i_prefix",
        "_run_phase_g_coverage",
        "_run_phase_h_locales",
    )
    with ExitStack() as stack:
        for attr in phase_attrs:
            stack.enter_context(patch.object(DiagnosticsRunner, attr, side_effect=_fake_phase))
        summary = await runner.run_all()

    assert isinstance(summary, DiagnosticsSummary)
    assert not summary.aborted
    assert len(summary.phases) == len(_PHASE_PLAN)
    runner.status_message.edit.assert_awaited()


@pytest.mark.asyncio
async def test_run_all_aborts_on_phase_error() -> None:
    runner = _make_runner()

    async def _fail(_idx: int) -> None:
        raise RuntimeError("phase boom")

    with (
        patch.object(DiagnosticsRunner, "_run_phase_a_infra", side_effect=_fail),
        patch.object(DiagnosticsRunner, "_run_phase_b_health", new=AsyncMock()),
    ):
        summary = await runner.run_all()

    assert summary.aborted
    assert "phase boom" in summary.abort_message


@pytest.mark.asyncio
async def test_run_phase_i_prefix_calls_checks() -> None:
    runner = _make_runner()
    outcomes = [
        CheckOutcome("prefix.admin.sync", True, "OK"),
        CheckOutcome("prefix.admin.test_bot", True, "skip", skipped=True, skip_allowed=True),
    ]
    with patch(
        "diagnostics.runner.run_prefix_command_checks",
        new=AsyncMock(return_value=outcomes),
    ):
        await runner._run_phase_i_prefix(7)

    phase = runner.summary.phases[0]
    assert phase.phase_id == "I"
    assert phase.passed == 1
    assert phase.skipped == 1


def test_diagnostics_summary_aborted_not_ok() -> None:
    s = DiagnosticsSummary()
    s.aborted = True
    assert not s.ok
