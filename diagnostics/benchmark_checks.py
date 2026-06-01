from __future__ import annotations

import asyncio
import json
import time
from pathlib import Path
from typing import Any

from diagnostics.benchmark_models import BenchmarkResult
from diagnostics.tree import collect_tree_paths, compare_tree_to_manifest, load_manifest
from localizer import tanjunLocalizer

_LOCALE_SAMPLE_KEYS = (
    "commands.admin.ban.error.description",
    "commands.admin.administration.test_bot.starting",
    "commands.admin.administration.update.updating",
    "commands.fun.boop.title",
    "commands.fun.hug.title",
    "commands.games.akinator.back",
    "commands.games.akinator.description",
    "commands.channel.dynamicslowmode.success.title",
    "commands.channel.dynamicslowmode.notSet.title",
    "commands.admin.administration.situation_not_found",
)

_MANIFEST_PATH = Path(__file__).resolve().parent / "manifest.json"


async def _timed(coro: Any) -> float:
    start = time.perf_counter()
    await coro
    return (time.perf_counter() - start) * 1000


async def benchmark_discord_roundtrip(ctx: Any, *, iterations: int = 5) -> BenchmarkResult:
    result = BenchmarkResult("discord.message_roundtrip")
    try:
        for _ in range(iterations):
            start = time.perf_counter()
            msg = await ctx.send("benchmark")
            await msg.edit(content="benchmark ok")
            result.samples_ms.append((time.perf_counter() - start) * 1000)
            await msg.delete()
    except Exception as exc:
        result.error = str(exc)
    return result


def benchmark_gateway_latency(bot: Any) -> BenchmarkResult:
    result = BenchmarkResult("discord.gateway_latency")
    latency = getattr(bot, "latency", None)
    if latency is None:
        result.error = "bot.latency unavailable"
        return result
    ms = round(latency * 1000, 2)
    result.samples_ms = [ms]
    shard_count = len(getattr(bot, "shards", {}) or {})
    result.detail = f"shards={shard_count}" if shard_count else "single shard"
    return result


async def benchmark_pool_acquire(bot: Any, *, iterations: int = 20) -> BenchmarkResult:
    result = BenchmarkResult("database.pool_acquire")
    pool = getattr(bot, "_pool", None)
    if pool is None:
        result.error = "Database pool not initialized"
        return result
    try:
        for _ in range(iterations):
            start = time.perf_counter()
            async with pool.acquire():
                pass
            result.samples_ms.append((time.perf_counter() - start) * 1000)
        pool_size = getattr(pool, "size", "?")
        pool_max = getattr(pool, "maxsize", "?")
        pool_free = getattr(pool, "freesize", "?")
        result.detail = f"pool size={pool_size} max={pool_max} free={pool_free}"
    except Exception as exc:
        result.error = str(exc)
    return result


async def _db_query(pool: Any, query: str, params: tuple[Any, ...] | None = None) -> None:
    async with pool.acquire() as conn, conn.cursor() as cursor:
        if params:
            await cursor.execute(query, params)
        else:
            await cursor.execute(query)
        await cursor.fetchall()


async def benchmark_select_one(bot: Any, *, iterations: int = 50) -> BenchmarkResult:
    result = BenchmarkResult("database.select_1")
    pool = getattr(bot, "_pool", None)
    if pool is None:
        result.error = "Database pool not initialized"
        return result
    try:
        for _ in range(iterations):
            result.samples_ms.append(await _timed(_db_query(pool, "SELECT 1")))
    except Exception as exc:
        result.error = str(exc)
    return result


async def benchmark_parallel_select_one(bot: Any, *, batch_size: int = 16, batches: int = 3) -> BenchmarkResult:
    result = BenchmarkResult("database.parallel_select_1")
    pool = getattr(bot, "_pool", None)
    if pool is None:
        result.error = "Database pool not initialized"
        return result

    async def _batch() -> float:
        start = time.perf_counter()
        await asyncio.gather(*(_db_query(pool, "SELECT 1") for _ in range(batch_size)))
        return (time.perf_counter() - start) * 1000

    try:
        for _ in range(batches):
            result.samples_ms.append(await _batch())
        result.detail = f"{batch_size} concurrent queries per batch"
    except Exception as exc:
        result.error = str(exc)
    return result


async def benchmark_level_config_count(bot: Any) -> BenchmarkResult:
    result = BenchmarkResult("database.level_config_count")
    pool = getattr(bot, "_pool", None)
    if pool is None:
        result.error = "Database pool not initialized"
        return result
    try:
        for _ in range(5):
            start = time.perf_counter()
            async with pool.acquire() as conn, conn.cursor() as cursor:
                await cursor.execute("SELECT COUNT(*) FROM levelConfig")
                row = await cursor.fetchone()
            elapsed = (time.perf_counter() - start) * 1000
            result.samples_ms.append(elapsed)
            if row:
                result.detail = f"rows={row[0]}"
    except Exception as exc:
        result.error = str(exc)
    return result


async def benchmark_guild_level_config(bot: Any, guild_id: int | None) -> BenchmarkResult:
    result = BenchmarkResult("database.guild_level_config")
    if guild_id is None:
        result.error = "No guild context for guild-scoped query"
        return result
    pool = getattr(bot, "_pool", None)
    if pool is None:
        result.error = "Database pool not initialized"
        return result
    query = """
    SELECT guild_id, active, difficulty, customFormula, level_up_messageActive,
           level_up_message, level_up_channel_id, textCooldown, voiceCooldown
    FROM levelConfig WHERE guild_id = %s
    """
    try:
        for _ in range(10):
            result.samples_ms.append(await _timed(_db_query(pool, query, (str(guild_id),))))
    except Exception as exc:
        result.error = str(exc)
    return result


def benchmark_localization(locale: str, *, iterations: int = 3) -> BenchmarkResult:
    result = BenchmarkResult("localization.sample_keys")
    keys = list(_LOCALE_SAMPLE_KEYS)
    try:
        for _ in range(iterations):
            start = time.perf_counter()
            for key in keys:
                tanjunLocalizer.localize(locale, key)
            result.samples_ms.append((time.perf_counter() - start) * 1000)
        result.detail = f"{len(keys)} keys x {iterations} passes"
    except Exception as exc:
        result.error = str(exc)
    return result


def benchmark_locale_file_load() -> BenchmarkResult:
    result = BenchmarkResult("localization.locale_file_load")
    locales_dir = Path(__file__).resolve().parents[1] / "locales"
    paths = sorted(locales_dir.glob("*.json"))
    if not paths:
        result.error = "No locale files found"
        return result
    try:
        for path in paths[:5]:
            start = time.perf_counter()
            json.loads(path.read_text(encoding="utf-8"))
            result.samples_ms.append((time.perf_counter() - start) * 1000)
        result.detail = f"loaded {min(5, len(paths))}/{len(paths)} locale files"
    except Exception as exc:
        result.error = str(exc)
    return result


def benchmark_command_tree(bot: Any) -> BenchmarkResult:
    result = BenchmarkResult("commands.tree_enumerate")
    try:
        for _ in range(5):
            start = time.perf_counter()
            paths = collect_tree_paths(bot)
            result.samples_ms.append((time.perf_counter() - start) * 1000)
        result.detail = f"{len(paths)} slash command paths"
    except Exception as exc:
        result.error = str(exc)
    return result


def benchmark_manifest_compare(bot: Any) -> BenchmarkResult:
    result = BenchmarkResult("commands.manifest_compare")
    try:
        for _ in range(5):
            start = time.perf_counter()
            compare_tree_to_manifest(bot)
            result.samples_ms.append((time.perf_counter() - start) * 1000)
        manifest = load_manifest()
        path_count = len(manifest.get("paths") or [])
        result.detail = f"manifest paths={path_count}"
    except Exception as exc:
        result.error = str(exc)
    return result


def benchmark_manifest_json_parse(*, iterations: int = 100) -> BenchmarkResult:
    result = BenchmarkResult("io.manifest_json_parse")
    if not _MANIFEST_PATH.is_file():
        result.error = "manifest.json missing"
        return result
    raw = _MANIFEST_PATH.read_text(encoding="utf-8")
    try:
        for _ in range(iterations):
            start = time.perf_counter()
            json.loads(raw)
            result.samples_ms.append((time.perf_counter() - start) * 1000)
        result.detail = f"{len(raw)} bytes x {iterations}"
    except Exception as exc:
        result.error = str(exc)
    return result


def benchmark_prefix_commands(bot: Any) -> BenchmarkResult:
    result = BenchmarkResult("commands.prefix_enumerate")
    try:
        for _ in range(5):
            start = time.perf_counter()
            count = sum(len(cog.get_commands()) for cog in bot.cogs.values())
            result.samples_ms.append((time.perf_counter() - start) * 1000)
        result.detail = f"{count} prefix commands"
    except Exception as exc:
        result.error = str(exc)
    return result


async def benchmark_health_checks(bot: Any) -> list[BenchmarkResult]:
    results: list[BenchmarkResult] = []
    manager = getattr(bot, "health_manager", None)
    if manager is None:
        r = BenchmarkResult("health.manager")
        r.error = "health_manager not on bot"
        return [r]
    for check in manager._checks:
        bench = BenchmarkResult(f"health.{check.name}")
        try:
            bench.samples_ms.append(await _timed(check.run()))
        except Exception as exc:
            bench.error = str(exc)
        results.append(bench)
    return results


async def benchmark_handler_specs(bot: Any, *, concurrency: int = 8) -> BenchmarkResult:
    from diagnostics.registry import all_specs, run_spec

    result = BenchmarkResult("handlers.all_specs")
    try:
        specs = all_specs()
    except Exception as exc:
        result.error = f"Could not load specs: {exc}"
        return result

    sem = asyncio.Semaphore(concurrency)
    times: list[float] = []
    failures = 0

    async def _run_one(spec: Any) -> None:
        nonlocal failures
        async with sem:
            start = time.perf_counter()
            try:
                outcome = await asyncio.wait_for(run_spec(spec, bot), timeout=30.0)
                if not outcome.passed and not outcome.skipped:
                    failures += 1
            except Exception:
                failures += 1
            times.append((time.perf_counter() - start) * 1000)

    wall_start = time.perf_counter()
    await asyncio.gather(*(_run_one(spec) for spec in specs))
    wall_ms = (time.perf_counter() - wall_start) * 1000
    result.samples_ms = times
    result.detail = f"{len(specs)} specs, wall={round(wall_ms, 2)}ms, failures={failures}"
    return result


async def benchmark_event_loop_yield(*, iterations: int = 100) -> BenchmarkResult:
    result = BenchmarkResult("runtime.event_loop_yield")
    try:
        for _ in range(iterations):
            start = time.perf_counter()
            await asyncio.sleep(0)
            result.samples_ms.append((time.perf_counter() - start) * 1000)
    except Exception as exc:
        result.error = str(exc)
    return result


async def benchmark_async_gather_tasks(*, task_count: int = 50) -> BenchmarkResult:
    result = BenchmarkResult("runtime.async_gather")

    async def _noop() -> int:
        await asyncio.sleep(0)
        return 1

    try:
        for _ in range(5):
            start = time.perf_counter()
            await asyncio.gather(*(_noop() for _ in range(task_count)))
            result.samples_ms.append((time.perf_counter() - start) * 1000)
        result.detail = f"{task_count} no-op tasks"
    except Exception as exc:
        result.error = str(exc)
    return result
