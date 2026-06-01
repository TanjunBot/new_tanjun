from __future__ import annotations

import asyncio
from collections import defaultdict
from datetime import UTC, datetime
from typing import Any

from discord.ext import commands

from diagnostics.infra_checks import check_database, check_ping
from diagnostics.models import CheckOutcome, DiagnosticsSummary, PhaseResult
from diagnostics.registry import all_specs, run_spec
from diagnostics.tree import compare_tree_to_manifest

EXPECTED_COGS = frozenset(
    {
        "AdminCog",
        "AdministrationCog",
        "AiCog",
        "ChannelCog",
        "ErrorHandlerCog",
        "FunCog",
        "GameCog",
        "GiveawayCog",
        "ImageCog",
        "levelCog",
        "ListenerCog",
        "LoopCog",
        "LogsCog",
        "MathCog",
        "MinigameCog",
        "SetupWizardsCog",
        "UtilityCog",
    }
)

CONCURRENCY = 8
SPEC_PROGRESS_INTERVAL = 10


class DiagnosticsRunner:
    def __init__(
        self,
        bot: commands.Bot,
        ctx: commands.Context,
        thread: Any,
        status_message: Any,
        locale: str = "en",
    ) -> None:
        self.bot = bot
        self.ctx = ctx
        self.thread = thread
        self.status_message = status_message
        self.locale = locale
        self.summary = DiagnosticsSummary()
        self._spec_done = 0

    async def _thread_send(self, content: str) -> None:
        if len(content) > 1900:
            content = content[:1900] + "…"
        await self.thread.send(content)

    async def _thread_send_lines(self, lines: list[str]) -> None:
        if not lines:
            return
        chunk: list[str] = []
        size = 0
        for line in lines:
            line_len = len(line) + 1
            if chunk and size + line_len > 1900:
                await self._thread_send("\n".join(chunk))
                chunk = []
                size = 0
            chunk.append(line)
            size += line_len
        if chunk:
            await self._thread_send("\n".join(chunk))

    def _outcome_label(self, outcome: CheckOutcome) -> str:
        if outcome.skipped and outcome.passed:
            return "WARN"
        if outcome.skipped:
            return "SKIP"
        return "PASS" if outcome.passed else "FAIL"

    def _format_outcome_line(self, outcome: CheckOutcome) -> str:
        label = self._outcome_label(outcome)
        detail = outcome.message or "OK"
        return f"{label} `{outcome.check_id}`: {detail}"

    async def _report_phase(self, phase: PhaseResult, *, compact_passed: bool = False) -> None:
        header = (
            f"**Phase {phase.phase_id}: {phase.title}** — "
            f"{phase.passed} passed, {phase.failed} failed, {phase.skipped} skipped"
        )
        await self._thread_send(header)

        lines: list[str] = []
        passed_by_group: dict[str, int] = defaultdict(int)

        for outcome in phase.outcomes:
            if outcome.passed and not outcome.skipped:
                if compact_passed:
                    group = outcome.check_id.split(".", 1)[0]
                    passed_by_group[group] += 1
                else:
                    lines.append(self._format_outcome_line(outcome))
            else:
                lines.append(self._format_outcome_line(outcome))

        if compact_passed and passed_by_group:
            for group in sorted(passed_by_group):
                count = passed_by_group[group]
                lines.append(f"PASS `{group}`: {count} spec{'s' if count != 1 else ''}")

        await self._thread_send_lines(lines)

    async def _update_parent(self, title: str, description: str) -> None:
        from utility import tanjunEmbed

        await self.status_message.edit(embed=tanjunEmbed(title=title, description=description))

    async def run_all(self) -> DiagnosticsSummary:
        started = datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S UTC")
        await self._thread_send(f"Diagnostics run started at {started}")

        for phase_fn in (
            self._run_phase_a_infra,
            self._run_phase_b_health,
            self._run_phase_c_loops,
            self._run_phase_d_tree,
            self._run_phase_f_extensions,
            self._run_phase_e_handlers,
        ):
            try:
                await phase_fn()
            except Exception as exc:
                await self._thread_send(f"Phase `{phase_fn.__name__}` aborted: {exc}")

        await self._finalize()
        return self.summary

    async def _run_phase_a_infra(self) -> None:
        phase = PhaseResult("A", "Infrastructure")
        await self._thread_send("## Phase A: Infrastructure")

        phase.outcomes.append(await check_ping(self.ctx))
        phase.outcomes.append(await check_database(self.bot))

        self.summary.phases.append(phase)
        await self._report_phase(phase)
        await self._update_parent("Bot Diagnostics", f"Phase A complete — {phase.failed} failed")

    async def _run_phase_b_health(self) -> None:
        phase = PhaseResult("B", "Platform health")
        await self._thread_send("## Phase B: Platform health")

        manager = getattr(self.bot, "health_manager", None)
        if manager is None:
            phase.outcomes.append(CheckOutcome("health.manager", False, "health_manager not on bot"))
        else:
            from health.checks import HealthStatus

            try:
                results = await manager.run_all()
            except Exception as exc:
                phase.outcomes.append(CheckOutcome("health.manager", False, str(exc)))
            else:
                for result in results:
                    ok = result.status != HealthStatus.CRITICAL
                    phase.outcomes.append(
                        CheckOutcome(
                            f"health.{result.check_name}",
                            ok,
                            result.message,
                        )
                    )

        self.summary.phases.append(phase)
        await self._report_phase(phase)
        await self._update_parent("Bot Diagnostics", f"Phase B complete — {phase.failed} failed")

    async def _run_phase_c_loops(self) -> None:
        phase = PhaseResult("C", "Background loops")
        await self._thread_send("## Phase C: Background loops")

        try:
            from extensions.health_check import BackgroundLoopHealthCheck

            check = BackgroundLoopHealthCheck(self.bot)
            result = await check.run()
            from health.checks import HealthStatus

            ok = result.status != HealthStatus.CRITICAL
            phase.outcomes.append(CheckOutcome("loops.background", ok, result.message))
        except Exception as exc:
            phase.outcomes.append(CheckOutcome("loops.background", False, str(exc)))

        self.summary.phases.append(phase)
        await self._report_phase(phase)

    async def _run_phase_d_tree(self) -> None:
        phase = PhaseResult("D", "Command tree manifest")
        await self._thread_send("## Phase D: Command tree manifest")

        try:
            missing, extra, missing_sub, extra_sub = compare_tree_to_manifest(self.bot)
        except Exception as exc:
            phase.outcomes.append(CheckOutcome("tree.manifest", False, str(exc)))
        else:
            if missing:
                for path in sorted(missing):
                    phase.outcomes.append(CheckOutcome(f"tree.missing.{path}", False, "Not registered"))
            if extra:
                for path in sorted(extra):
                    phase.outcomes.append(
                        CheckOutcome(f"tree.extra.{path}", True, "Unexpected command", skipped=True)
                    )
            if missing_sub:
                for name in sorted(missing_sub):
                    phase.outcomes.append(CheckOutcome(f"tree.subgroup.missing.{name}", False, "Not registered"))
            if extra_sub:
                for name in sorted(extra_sub):
                    phase.outcomes.append(
                        CheckOutcome(f"tree.subgroup.extra.{name}", True, "Unexpected subgroup", skipped=True)
                    )
            if not missing and not extra and not missing_sub and not extra_sub:
                phase.outcomes.append(CheckOutcome("tree.manifest", True, "Tree matches manifest"))

        self.summary.phases.append(phase)
        await self._report_phase(phase)

    async def _run_phase_f_extensions(self) -> None:
        phase = PhaseResult("F", "Extensions loaded")
        await self._thread_send("## Phase F: Extensions loaded")

        loaded = set(self.bot.cogs.keys())
        for cog_name in sorted(EXPECTED_COGS):
            ok = cog_name in loaded
            phase.outcomes.append(CheckOutcome(f"cog.{cog_name}", ok, "loaded" if ok else "missing"))

        self.summary.phases.append(phase)
        await self._report_phase(phase)

    async def _run_phase_e_handlers(self) -> None:
        phase = PhaseResult("E", "Handler behaviors")
        specs = all_specs()
        total = len(specs)
        await self._thread_send(f"## Phase E: Handler behaviors ({total} specs)")

        sem = asyncio.Semaphore(CONCURRENCY)

        async def _run_one(spec: Any) -> CheckOutcome:
            async with sem:
                return await run_spec(spec, self.bot)

        tasks = [asyncio.create_task(_run_one(spec)) for spec in specs]

        for coro in asyncio.as_completed(tasks):
            outcome = await coro
            phase.outcomes.append(outcome)
            self._spec_done += 1
            if self._spec_done % SPEC_PROGRESS_INTERVAL == 0:
                await self._update_parent(
                    "Bot Diagnostics",
                    f"Phase E: {self._spec_done}/{total} specs ({phase.failed} failed)",
                )

        self.summary.phases.append(phase)
        await self._report_phase(phase, compact_passed=True)
        await self._update_parent("Bot Diagnostics", f"Phase E complete — {phase.failed} failed, {phase.skipped} skipped")

    async def _finalize(self) -> None:
        s = self.summary
        phase_lines = [
            f"- Phase {p.phase_id}: {p.passed} passed, {p.failed} failed, {p.skipped} skipped"
            for p in s.phases
        ]
        lines = [
            "## Summary",
            *phase_lines,
            f"**Total:** {s.total_passed} passed, {s.total_failed} failed, {s.total_skipped} skipped",
            f"**Status:** {'OK' if s.ok else 'FAILED'}",
        ]
        await self._thread_send("\n".join(lines))

        from utility import error_embed, success_embed

        summary_body = "\n".join(
            [
                f"Passed: {s.total_passed}",
                f"Failed: {s.total_failed}",
                f"Skipped: {s.total_skipped}",
                f"Status: {'OK' if s.ok else 'FAILED'}",
            ]
        )
        if s.ok:
            embed = success_embed(summary_body, title="Bot Diagnostics")
        else:
            embed = error_embed(summary_body, title="Bot Diagnostics")
        await self.status_message.edit(embed=embed)
