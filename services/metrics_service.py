"""Prometheus metrics for Tanjun Bot.

Provides a shared metrics registry and labels for:
- Command usage counts (by name)
- Database query latency
- Shard latency and heartbeats
- Message processing throughput
- Memory/CPU usage of the bot process
"""

from __future__ import annotations

import logging
import os

from prometheus_client import Counter, Gauge, Histogram

logger = logging.getLogger(__name__)

# ── Prometheus Registry (using default) ──────────────────────────────────────

_NAMESPACE = "tanjun"

# ── Command metrics ──────────────────────────────────────────────────────────

command_usage = Counter(
    name="tanjun_command_usage_total",
    namespace=_NAMESPACE,
    subsystem="commands",
    documentation="Total number of command invocations by name and status.",
    labelnames=["command", "guild_id", "status"],
)

command_duration = Histogram(
    name="tanjun_command_duration_seconds",
    namespace=_NAMESPACE,
    subsystem="commands",
    documentation="Command execution duration in seconds.",
    labelnames=["command"],
    buckets=(0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0, 60.0),
)

# ── Database metrics ─────────────────────────────────────────────────────────

db_query_duration = Histogram(
    name="tanjun_db_query_duration_seconds",
    namespace=_NAMESPACE,
    subsystem="database",
    documentation="Database query duration in seconds.",
    labelnames=["operation"],
    buckets=(0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0),
)

db_query_errors = Counter(
    name="tanjun_db_query_errors_total",
    namespace=_NAMESPACE,
    subsystem="database",
    documentation="Total number of database query errors by operation.",
    labelnames=["operation"],
)

db_pool_size = Gauge(
    name="tanjun_db_pool_size",
    namespace=_NAMESPACE,
    subsystem="database",
    documentation="Current database connection pool size (min/max/used).",
    labelnames=["type"],
)

# ── Shard / Gateway metrics ──────────────────────────────────────────────────

shard_latency = Gauge(
    name="tanjun_shard_latency_seconds",
    namespace=_NAMESPACE,
    subsystem="gateway",
    documentation="WebSocket latency for each shard in seconds.",
    labelnames=["shard_id"],
)

shard_connected = Gauge(
    name="tanjun_shard_connected",
    namespace=_NAMESPACE,
    subsystem="gateway",
    documentation="Whether each shard is connected (1) or not (0).",
    labelnames=["shard_id"],
)

guild_count = Gauge(
    name="tanjun_guild_count",
    namespace=_NAMESPACE,
    subsystem="bot",
    documentation="Total number of guilds the bot is in.",
)

user_count = Gauge(
    name="tanjun_user_count",
    namespace=_NAMESPACE,
    subsystem="bot",
    documentation="Total number of users visible to the bot.",
)

# ── Message processing metrics ───────────────────────────────────────────────

messages_processed = Counter(
    name="tanjun_messages_processed_total",
    namespace=_NAMESPACE,
    subsystem="messages",
    documentation="Total number of messages processed by the bot.",
    labelnames=["guild_id"],
)

message_processing_duration = Histogram(
    name="tanjun_message_processing_duration_seconds",
    namespace=_NAMESPACE,
    subsystem="messages",
    documentation="Time spent processing each message event.",
    buckets=(0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0),
)

# ── System metrics (process-level) ───────────────────────────────────────────

process_memory_bytes = Gauge(
    name="tanjun_process_memory_bytes",
    namespace=_NAMESPACE,
    subsystem="system",
    documentation="Current resident memory usage of the bot process in bytes.",
)

process_cpu_seconds = Gauge(
    name="tanjun_process_cpu_seconds_total",
    namespace=_NAMESPACE,
    subsystem="system",
    documentation="Total CPU time consumed by the bot process in seconds (user + system).",
)

process_open_fds = Gauge(
    name="tanjun_process_open_fds",
    namespace=_NAMESPACE,
    subsystem="system",
    documentation="Number of open file descriptors.",
)

process_threads = Gauge(
    name="tanjun_process_threads",
    namespace=_NAMESPACE,
    subsystem="system",
    documentation="Number of threads in the bot process.",
)

# ── Uptime / info ────────────────────────────────────────────────────────────

bot_start_time = Gauge(
    name="tanjun_bot_start_time_seconds",
    namespace=_NAMESPACE,
    subsystem="bot",
    documentation="Unix timestamp of when the bot started.",
)


# ── Health / loop metrics ────────────────────────────────────────────────────

loop_running = Gauge(
    name="tanjun_loop_running",
    namespace=_NAMESPACE,
    subsystem="loops",
    documentation="Whether a background loop is running (1) or not (0).",
    labelnames=["loop_name"],
)

loop_iteration_duration = Histogram(
    name="tanjun_loop_iteration_duration_seconds",
    namespace=_NAMESPACE,
    subsystem="loops",
    documentation="Duration of each background loop iteration.",
    labelnames=["loop_name"],
    buckets=(0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0),
)

loop_iteration_errors = Counter(
    name="tanjun_loop_iteration_errors_total",
    namespace=_NAMESPACE,
    subsystem="loops",
    documentation="Total number of errors in background loop iterations.",
    labelnames=["loop_name"],
)


# ── Utility functions ────────────────────────────────────────────────────────


def _get_process_stats() -> dict[str, float]:
    """Read process resource usage from /proc/self/status and /proc/self/stat.

    Returns a dict with 'memory_bytes', 'cpu_user_seconds', 'cpu_system_seconds',
    'threads', 'open_fds'.
    """
    stats: dict[str, float] = {}
    try:
        with open("/proc/self/stat") as f:
            parts = f.read().split()
            # man 5 proc: fields 14 (utime) and 15 (stime) (zero-indexed 13, 14)
            # Divide by clock ticks per second to get seconds.
            clk_tck = os.sysconf("SC_CLK_TCK") if os.name == "posix" else 100
            utime = int(parts[13]) / clk_tck
            stime = int(parts[14]) / clk_tck
            stats["cpu_user_seconds"] = utime
            stats["cpu_system_seconds"] = stime
            stats["cpu_seconds_total"] = utime + stime
            # num_threads at field 20 (zero-indexed 19)
            stats["threads"] = float(parts[19]) if len(parts) > 19 else 0.0
    except (FileNotFoundError, IndexError, ValueError):
        pass

    try:
        with open("/proc/self/status") as f:
            for line in f:
                if line.startswith("VmRSS:"):
                    # VmRSS is in kB
                    stats["memory_bytes"] = float(line.split()[1]) * 1024
                elif line.startswith("Threads:"):
                    stats["threads"] = float(line.split()[1])
    except (FileNotFoundError, ValueError):
        pass

    try:
        stats["open_fds"] = float(len(os.listdir("/proc/self/fd")))
    except (FileNotFoundError, PermissionError):
        pass

    return stats


def update_process_metrics() -> None:
    """Refresh process-level gauges from /proc."""
    proc_stats = _get_process_stats()
    if "memory_bytes" in proc_stats:
        process_memory_bytes.set(proc_stats["memory_bytes"])
    if "cpu_seconds_total" in proc_stats:
        process_cpu_seconds.set(proc_stats["cpu_seconds_total"])
    if "open_fds" in proc_stats:
        process_open_fds.set(proc_stats["open_fds"])
    if "threads" in proc_stats:
        process_threads.set(proc_stats["threads"])
