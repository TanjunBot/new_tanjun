from __future__ import annotations

import asyncio
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

    async def _update_parent(self, title: str, description: str) -> None:
        from utility import tanjunEmbed

        await self.status_message.edit(embed=tanjunEmbed(title=title, description=description))

    async def run_all(self) -> DiagnosticsSummary:
        started = datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S UTC")
        await self._thread_send(f"Diagnostics run started at {started}")

        await self._run_phase_a_infra()
        await self._run_phase_b_health()
        await self._run_phase_c_loops()
        await self._run_phase_d_tree()
        await self._run_phase_f_extensions()
        await self._run_phase_e_handlers()

        await self._finalize()
        return self.summary

    async def _run_phase_a_infra(self) -> None:
        phase = PhaseResult("A", "Infrastructure")
        await self._thread_send("## Phase A: Infrastructure")

        ping = await check_ping(self.ctx)
        phase.outcomes.append(ping)
        if not ping.passed:
            await self._thread_send(f"FAIL `{ping.check_id}`: {ping.message}")

        db = await check_database(self.bot)
        phase.outcomes.append(db)
        if not db.passed:
            await self._thread_send(f"FAIL `{db.check_id}`: {db.message}")

        self.summary.phases.append(phase)
        await self._update_parent("Bot Diagnostics", f"Phase A complete — {phase.failed} failed")

    async def _run_phase_b_health(self) -> None:
        phase = PhaseResult("B", "Platform health")
        await self._thread_send("## Phase B: Platform health")

        manager = getattr(self.bot, "health_manager", None)
        if manager is None:
            phase.outcomes.append(CheckOutcome("health.manager", False, "health_manager not on bot"))
        else:
            from health.checks import HealthStatus

            results = await manager.run_all()
            for result in results:
                ok = result.status != HealthStatus.CRITICAL
                phase.outcomes.append(
                    CheckOutcome(
                        f"health.{result.check_name}",
                        ok,
                        result.message,
                    )
                )
                if not ok:
                    await self._thread_send(f"FAIL `health.{result.check_name}`: {result.message}")

        self.summary.phases.append(phase)
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
            if not ok:
                await self._thread_send(f"FAIL `loops.background`: {result.message}")
        except Exception as exc:
            phase.outcomes.append(CheckOutcome("loops.background", False, str(exc)))
            await self._thread_send(f"FAIL `loops.background`: {exc}")

        self.summary.phases.append(phase)

    async def _run_phase_d_tree(self) -> None:
        phase = PhaseResult("D", "Command tree manifest")
        await self._thread_send("## Phase D: Command tree manifest")

        missing, extra = compare_tree_to_manifest(self.bot)
        if missing:
            for path in sorted(missing):
                phase.outcomes.append(CheckOutcome(f"tree.missing.{path}", False, "Not registered"))
                await self._thread_send(f"FAIL tree missing: `{path}`")
        if extra:
            for path in sorted(extra):
                phase.outcomes.append(CheckOutcome(f"tree.extra.{path}", False, "Unexpected command"))
                await self._thread_send(f"WARN tree extra: `{path}`")
        if not missing and not extra:
            phase.outcomes.append(CheckOutcome("tree.manifest", True, "Tree matches manifest"))

        self.summary.phases.append(phase)

    async def _run_phase_f_extensions(self) -> None:
        phase = PhaseResult("F", "Extensions loaded")
        await self._thread_send("## Phase F: Extensions loaded")

        loaded = set(self.bot.cogs.keys())
        for cog_name in sorted(EXPECTED_COGS):
            ok = cog_name in loaded
            phase.outcomes.append(CheckOutcome(f"cog.{cog_name}", ok, "loaded" if ok else "missing"))
            if not ok:
                await self._thread_send(f"FAIL cog missing: `{cog_name}`")

        self.summary.phases.append(phase)

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
            if not outcome.passed and not outcome.skipped:
                await self._thread_send(f"FAIL `{outcome.check_id}`: {outcome.message}")
            if self._spec_done % SPEC_PROGRESS_INTERVAL == 0:
                await self._update_parent(
                    "Bot Diagnostics",
                    f"Phase E: {self._spec_done}/{total} specs ({phase.failed} failed)",
                )

        self.summary.phases.append(phase)
        await self._update_parent("Bot Diagnostics", f"Phase E complete — {phase.failed} failed, {phase.skipped} skipped")

    async def _finalize(self) -> None:
        s = self.summary
        lines = [
            "## Summary",
            f"Passed: {s.total_passed}",
            f"Failed: {s.total_failed}",
            f"Skipped: {s.total_skipped}",
            f"Status: {'OK' if s.ok else 'FAILED'}",
        ]
        await self._thread_send("\n".join(lines))

        from utility import error_embed, success_embed

        if s.ok:
            embed = success_embed("\n".join(lines[1:]), title="Bot Diagnostics")
        else:
            embed = error_embed("\n".join(lines[1:]), title="Bot Diagnostics")
        await self.status_message.edit(embed=embed)
