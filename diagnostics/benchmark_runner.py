from __future__ import annotations
from locale_keys import locale
import time
from datetime import UTC, datetime
from typing import Any
from discord.ext import commands
from diagnostics.benchmark_checks import benchmark_async_gather_tasks, benchmark_command_tree, benchmark_discord_roundtrip, benchmark_event_loop_yield, benchmark_gateway_latency, benchmark_guild_level_config, benchmark_handler_specs, benchmark_health_checks, benchmark_level_config_count, benchmark_locale_file_load, benchmark_localization, benchmark_manifest_compare, benchmark_manifest_json_parse, benchmark_parallel_select_one, benchmark_pool_acquire, benchmark_prefix_commands, benchmark_select_one
from diagnostics.benchmark_models import BenchmarkPhase, BenchmarkResult, BenchmarkSummary

class BenchmarkRunner:

    def __init__(self, bot: commands.Bot, ctx: commands.Context, thread: Any, status_message: Any, locale: str='en') -> None:
        self.bot = bot
        self.ctx = ctx
        self.thread = thread
        self.status_message = status_message
        self.locale = locale
        self.summary = BenchmarkSummary()
        self._guild_id = ctx.guild.id if ctx.guild else None

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

    async def _update_parent(self, title: str, description: str) -> None:
        from utility import tanjunEmbed
        await self.status_message.edit(embed=tanjunEmbed(title=title, description=description))

    async def _report_phase(self, phase: BenchmarkPhase) -> None:
        header = f'**Phase {phase.phase_id}: {phase.title}**'
        await self._thread_send(header)
        lines = [r.summary() for r in phase.results]
        await self._thread_send_lines(lines)

    async def run_all(self) -> BenchmarkSummary:
        wall_start = time.perf_counter()
        started = datetime.now(UTC).strftime('%Y-%m-%d %H:%M:%S UTC')
        await self._thread_send(f'Benchmark run started at {started}')
        for phase_fn in (self._run_phase_a_discord, self._run_phase_b_database, self._run_phase_c_localization_io, self._run_phase_d_commands, self._run_phase_e_health, self._run_phase_f_handlers, self._run_phase_g_runtime):
            try:
                await phase_fn()
            except Exception as exc:
                await self._thread_send(f'Phase `{phase_fn.__name__}` aborted: {exc}')
        self.summary.total_wall_ms = round((time.perf_counter() - wall_start) * 1000, 2)
        await self._finalize()
        return self.summary

    async def _run_phase_a_discord(self) -> None:
        phase = BenchmarkPhase('A', 'Discord & gateway')
        await self._thread_send('## Phase A: Discord & gateway')
        await self._update_parent('Bot Benchmarks', 'Phase A: Discord & gateway…')
        phase.results.append(benchmark_gateway_latency(self.bot))
        phase.results.append(await benchmark_discord_roundtrip(self.ctx))
        self.summary.phases.append(phase)
        await self._report_phase(phase)

    async def _run_phase_b_database(self) -> None:
        phase = BenchmarkPhase('B', 'Database')
        await self._thread_send('## Phase B: Database')
        await self._update_parent('Bot Benchmarks', 'Phase B: Database…')
        phase.results.extend([await benchmark_pool_acquire(self.bot), await benchmark_select_one(self.bot), await benchmark_parallel_select_one(self.bot), await benchmark_level_config_count(self.bot), await benchmark_guild_level_config(self.bot, self._guild_id)])
        self.summary.phases.append(phase)
        await self._report_phase(phase)

    async def _run_phase_c_localization_io(self) -> None:
        phase = BenchmarkPhase('C', 'Localization & I/O')
        await self._thread_send('## Phase C: Localization & I/O')
        await self._update_parent('Bot Benchmarks', 'Phase C: Localization & I/O…')
        phase.results.append(benchmark_localization(self.locale))
        phase.results.append(benchmark_locale_file_load())
        phase.results.append(benchmark_manifest_json_parse())
        self.summary.phases.append(phase)
        await self._report_phase(phase)

    async def _run_phase_d_commands(self) -> None:
        phase = BenchmarkPhase('D', 'Command surface')
        await self._thread_send('## Phase D: Command surface')
        await self._update_parent('Bot Benchmarks', 'Phase D: Command surface…')
        phase.results.extend([benchmark_command_tree(self.bot), benchmark_manifest_compare(self.bot), benchmark_prefix_commands(self.bot)])
        self.summary.phases.append(phase)
        await self._report_phase(phase)

    async def _run_phase_e_health(self) -> None:
        phase = BenchmarkPhase('E', 'Health checks')
        await self._thread_send('## Phase E: Health checks')
        await self._update_parent('Bot Benchmarks', 'Phase E: Health checks…')
        phase.results.extend(await benchmark_health_checks(self.bot))
        self.summary.phases.append(phase)
        await self._report_phase(phase)

    async def _run_phase_f_handlers(self) -> None:
        phase = BenchmarkPhase('F', 'Handler harness (all specs)')
        await self._thread_send('## Phase F: Handler harness — timing every behavior spec')
        await self._update_parent('Bot Benchmarks', 'Phase F: Handler harness (may take several minutes)…')
        phase.results.append(await benchmark_handler_specs(self.bot))
        self.summary.phases.append(phase)
        await self._report_phase(phase)

    async def _run_phase_g_runtime(self) -> None:
        phase = BenchmarkPhase('G', 'Async runtime')
        await self._thread_send('## Phase G: Async runtime')
        await self._update_parent('Bot Benchmarks', 'Phase G: Async runtime…')
        phase.results.extend([await benchmark_event_loop_yield(), await benchmark_async_gather_tasks()])
        self.summary.phases.append(phase)
        await self._report_phase(phase)

    async def _finalize(self) -> None:
        s = self.summary
        phase_lines = [f'- Phase {p.phase_id} ({p.title}): {len(p.results)} benchmarks' for p in s.phases]
        lines = ['## Summary', *phase_lines, f'**Benchmarks:** {s.bench_count}', f'**Errors:** {s.error_count}', f'**Total wall time:** {s.total_wall_ms}ms']
        await self._thread_send('\n'.join(lines))
        from utility import success_embed, warning_embed
        summary_body = '\n'.join([f'Benchmarks run: {s.bench_count}', f'Errors: {s.error_count}', f'Wall time: {s.total_wall_ms}ms', 'See thread for per-phase timings.'])
        if s.error_count:
            embed = warning_embed(summary_body, title='Bot Benchmarks')
        else:
            embed = success_embed(summary_body, title='Bot Benchmarks')
        await self.status_message.edit(embed=embed)