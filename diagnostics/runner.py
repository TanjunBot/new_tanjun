from __future__ import annotations
from locale_keys import locale
import asyncio
from collections import defaultdict
from datetime import UTC, datetime
from typing import Any
from discord.ext import commands
from diagnostics.coverage import check_duplicate_spec_ids, check_manifest_spec_coverage
from diagnostics.infra_checks import check_database, check_gateway_latency, check_ping
from diagnostics.locale_checks import check_locale_files, check_localizer_samples
from diagnostics.models import CheckOutcome, DiagnosticsSummary, PhaseResult
from diagnostics.registry import all_specs, run_spec
from diagnostics.tree import compare_tree_to_manifest
EXPECTED_COGS = frozenset({'AdminCog', 'AdministrationCog', 'AiCog', 'ChannelCog', 'ErrorHandlerCog', 'FunCog', 'GameCog', 'GiveawayCog', 'ImageCog', 'levelCog', 'ListenerCog', 'LoopCog', 'LogsCog', 'MathCog', 'MinigameCog', 'SetupWizardsCog', 'UtilityCog'})
CONCURRENCY = 8
SPEC_PROGRESS_INTERVAL = 10
PROGRESS_BAR_WIDTH = 12
_PHASE_PLAN: tuple[tuple[str, str], ...] = (('A', 'Infrastructure'), ('B', 'Platform health'), ('C', 'Background loops'), ('D', 'Command tree manifest'), ('E', 'Slash handler behaviors'), ('F', 'Extensions loaded'), ('G', 'Spec coverage'), ('H', 'Localization'))

class DiagnosticsRunner:

    def __init__(self, bot: commands.Bot, ctx: commands.Context, thread: Any, status_message: Any, locale: str='en') -> None:
        self.bot = bot
        self.ctx = ctx
        self.thread = thread
        self.status_message = status_message
        self.locale = locale
        self.summary = DiagnosticsSummary()
        self._spec_done = 0
        self._phase_total = len(_PHASE_PLAN)

    @staticmethod
    def _progress_bar(current: int, total: int, width: int=PROGRESS_BAR_WIDTH) -> str:
        if total <= 0:
            return f"[{'░' * width}] 0/0"
        filled = min(width, round(width * current / total))
        return f"[{'█' * filled}{'░' * (width - filled)}] {current}/{total}"

    async def _update_progress(self, phase_index: int, phase_title: str, detail: str='') -> None:
        bar = self._progress_bar(phase_index, self._phase_total)
        description = f'{bar}\n**Phase {phase_title}**'
        if detail:
            description = f'{description}\n{detail}'
        await self._update_parent('Bot Diagnostics', description)

    async def _thread_send(self, content: str) -> None:
        if len(content) > 1900:
            content = content[:1900] + '…'
        await self.thread.send(content)

    async def _thread_send_lines(self, lines: list[str]) -> None:
        if not lines:
            return
        chunk: list[str] = []
        size = 0
        for line in lines:
            line_len = len(line) + 1
            if chunk and size + line_len > 1900:
                await self._thread_send('\n'.join(chunk))
                chunk = []
                size = 0
            chunk.append(line)
            size += line_len
        if chunk:
            await self._thread_send('\n'.join(chunk))

    def _outcome_label(self, outcome: CheckOutcome) -> str:
        if outcome.skipped and outcome.skip_allowed:
            return 'SKIP'
        if outcome.skipped:
            return 'FAIL'
        return 'PASS' if outcome.passed else 'FAIL'

    def _format_outcome_line(self, outcome: CheckOutcome) -> str:
        label = self._outcome_label(outcome)
        detail = outcome.message or 'OK'
        return f'{label} `{outcome.check_id}`: {detail}'

    async def _report_phase(self, phase: PhaseResult, *, compact_passed: bool=False) -> None:
        header = f'**Phase {phase.phase_id}: {phase.title}** — {phase.passed} passed, {phase.failed} failed, {phase.skipped} skipped'
        await self._thread_send(header)
        lines: list[str] = []
        passed_by_group: dict[str, int] = defaultdict(int)
        for outcome in phase.outcomes:
            if outcome.passed and (not outcome.skipped):
                if compact_passed:
                    group = outcome.check_id.split('.', 1)[0]
                    passed_by_group[group] += 1
                else:
                    lines.append(self._format_outcome_line(outcome))
            else:
                lines.append(self._format_outcome_line(outcome))
        if compact_passed and passed_by_group:
            for group in sorted(passed_by_group):
                count = passed_by_group[group]
                lines.append(f"PASS `{group}`: {count} spec{('s' if count != 1 else '')}")
        await self._thread_send_lines(lines)

    async def _update_parent(self, title: str, description: str) -> None:
        from utility import tanjunEmbed
        await self.status_message.edit(embed=tanjunEmbed(title=title, description=description))

    async def run_all(self) -> DiagnosticsSummary:
        started = datetime.now(UTC).strftime('%Y-%m-%d %H:%M:%S UTC')
        await self._thread_send(f'Diagnostics run started at {started} (strict mode)')
        phase_runners = (self._run_phase_a_infra, self._run_phase_b_health, self._run_phase_c_loops, self._run_phase_d_tree, self._run_phase_e_handlers, self._run_phase_f_extensions, self._run_phase_g_coverage, self._run_phase_h_locales)
        for phase_index, ((phase_id, phase_title), phase_fn) in enumerate(zip(_PHASE_PLAN, phase_runners, strict=True), start=1):
            label = f'{phase_id}: {phase_title}'
            await self._update_progress(phase_index, label, 'Running…')
            try:
                await phase_fn(phase_index)
            except Exception as exc:
                self.summary.aborted = True
                self.summary.abort_message = str(exc)
                await self._thread_send(f'Phase {phase_id} ({phase_title}) aborted: {exc}')
                await self._update_progress(phase_index, label, f'Aborted: {exc}')
                break
        await self._finalize()
        return self.summary

    async def _run_phase_a_infra(self, phase_index: int) -> None:
        phase = PhaseResult('A', 'Infrastructure')
        await self._thread_send('## Phase A: Infrastructure')
        phase.outcomes.append(await check_ping(self.ctx))
        phase.outcomes.append(check_gateway_latency(self.bot))
        phase.outcomes.append(await check_database(self.bot))
        self.summary.phases.append(phase)
        await self._report_phase(phase)
        await self._update_progress(phase_index, 'A: Infrastructure', f'Complete — {phase.failed} failed')

    async def _run_phase_b_health(self, phase_index: int) -> None:
        phase = PhaseResult('B', 'Platform health')
        await self._thread_send('## Phase B: Platform health')
        manager = getattr(self.bot, 'health_manager', None)
        if manager is None:
            phase.outcomes.append(CheckOutcome('health.manager', False, 'health_manager not on bot'))
        else:
            from health.checks import HealthStatus
            try:
                results = await manager.run_all()
            except Exception as exc:
                phase.outcomes.append(CheckOutcome('health.manager', False, str(exc)))
            else:
                for result in results:
                    ok = result.status != HealthStatus.CRITICAL
                    phase.outcomes.append(CheckOutcome(f'health.{result.check_name}', ok, result.message))
        self.summary.phases.append(phase)
        await self._report_phase(phase)
        await self._update_progress(phase_index, 'B: Platform health', f'Complete — {phase.failed} failed')

    async def _run_phase_c_loops(self, phase_index: int) -> None:
        phase = PhaseResult('C', 'Background loops')
        await self._thread_send('## Phase C: Background loops')
        try:
            from extensions.health_check import BackgroundLoopHealthCheck
            check = BackgroundLoopHealthCheck(self.bot)
            result = await check.run()
            from health.checks import HealthStatus
            ok = result.status != HealthStatus.CRITICAL
            phase.outcomes.append(CheckOutcome('loops.background', ok, result.message))
        except Exception as exc:
            phase.outcomes.append(CheckOutcome('loops.background', False, str(exc)))
        self.summary.phases.append(phase)
        await self._report_phase(phase)
        await self._update_progress(phase_index, 'C: Background loops', f'Complete — {phase.failed} failed')

    async def _run_phase_d_tree(self, phase_index: int) -> None:
        phase = PhaseResult('D', 'Command tree manifest')
        await self._thread_send('## Phase D: Command tree manifest')
        try:
            missing, extra, missing_sub, extra_sub = compare_tree_to_manifest(self.bot)
        except Exception as exc:
            phase.outcomes.append(CheckOutcome('tree.manifest', False, str(exc)))
        else:
            if missing:
                for path in sorted(missing):
                    phase.outcomes.append(CheckOutcome(f'tree.missing.{path}', False, 'Not registered'))
            if extra:
                for path in sorted(extra):
                    phase.outcomes.append(CheckOutcome(f'tree.extra.{path}', False, 'Unexpected command in live tree'))
            if missing_sub:
                for name in sorted(missing_sub):
                    phase.outcomes.append(CheckOutcome(f'tree.subgroup.missing.{name}', False, 'Not registered'))
            if extra_sub:
                for name in sorted(extra_sub):
                    phase.outcomes.append(CheckOutcome(f'tree.subgroup.extra.{name}', False, 'Unexpected subgroup in live tree'))
            if not missing and (not extra) and (not missing_sub) and (not extra_sub):
                phase.outcomes.append(CheckOutcome('tree.manifest', True, 'Tree matches manifest'))
        self.summary.phases.append(phase)
        await self._report_phase(phase)
        await self._update_progress(phase_index, 'D: Command tree manifest', f'Complete — {phase.failed} failed')

    async def _run_phase_g_coverage(self, phase_index: int) -> None:
        phase = PhaseResult('G', 'Spec coverage')
        await self._thread_send('## Phase G: Spec coverage vs manifest')
        phase.outcomes.extend(check_manifest_spec_coverage())
        phase.outcomes.extend(check_duplicate_spec_ids())
        self.summary.phases.append(phase)
        await self._report_phase(phase)
        await self._update_progress(phase_index, 'G: Spec coverage', f'Complete — {phase.failed} failed')

    async def _run_phase_f_extensions(self, phase_index: int) -> None:
        phase = PhaseResult('F', 'Extensions loaded')
        await self._thread_send('## Phase F: Extensions loaded')
        loaded = set(self.bot.cogs.keys())
        for cog_name in sorted(EXPECTED_COGS):
            ok = cog_name in loaded
            phase.outcomes.append(CheckOutcome(f'cog.{cog_name}', ok, 'loaded' if ok else 'missing'))
        self.summary.phases.append(phase)
        await self._report_phase(phase)
        await self._update_progress(phase_index, 'F: Extensions loaded', f'Complete — {phase.failed} failed')

    async def _run_phase_e_handlers(self, phase_index: int) -> None:
        phase = PhaseResult('E', 'Slash handler behaviors')
        specs = all_specs()
        total = len(specs)
        await self._thread_send(f'## Phase E: Slash handler behaviors ({total} specs)')
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
                await self._update_progress(phase_index, 'E: Slash handler behaviors', f'Specs {self._spec_done}/{total} ({phase.failed} failed)')
        self.summary.phases.append(phase)
        await self._report_phase(phase, compact_passed=True)
        await self._update_progress(phase_index, 'E: Slash handler behaviors', f'Complete — {phase.failed} failed, {phase.skipped} skipped')

    async def _run_phase_h_locales(self, phase_index: int) -> None:
        phase = PhaseResult('H', 'Localization')
        await self._thread_send('## Phase H: Localization')
        phase.outcomes.extend(check_locale_files())
        phase.outcomes.extend(check_localizer_samples(self.locale))
        self.summary.phases.append(phase)
        await self._report_phase(phase, compact_passed=True)
        await self._update_progress(phase_index, 'H: Localization', f'Complete — {phase.failed} failed')

    async def _finalize(self) -> None:
        s = self.summary
        phase_lines = [f'- Phase {p.phase_id}: {p.passed} passed, {p.failed} failed, {p.skipped} skipped' for p in s.phases]
        lines = ['## Summary', *phase_lines, f'**Total:** {s.total_passed} passed, {s.total_failed} failed, {s.total_skipped} skipped', f'**Unauthorized skips:** {s.unauthorized_skips}']
        if s.aborted:
            lines.append(f'**Aborted:** {s.abort_message}')
        lines.append(f"**Status:** {('OK' if s.ok else 'FAILED')}")
        await self._thread_send('\n'.join(lines))
        from utility import error_embed, success_embed
        summary_lines = [f'Passed: {s.total_passed}', f'Failed: {s.total_failed}', f'Skipped (allowed): {s.total_skipped}', f'Unauthorized skips: {s.unauthorized_skips}']
        if s.aborted:
            summary_lines.append(f'Aborted: {s.abort_message}')
        summary_lines.append(f"Status: {('OK' if s.ok else 'FAILED')}")
        summary_body = '\n'.join(summary_lines)
        if s.ok:
            embed = success_embed(summary_body, title='Bot Diagnostics')
        else:
            embed = error_embed(summary_body, title='Bot Diagnostics')
        await self.status_message.edit(embed=embed)