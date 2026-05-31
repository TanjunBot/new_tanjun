"""Prometheus Metrics Extension for Tanjun Bot.

Exposes an internal HTTP endpoint (port 8000) with Prometheus metrics.
Instruments command usage, DB latency, shard health, message throughput,
memory/CPU, and background loop health.
"""

from __future__ import annotations

import logging
import time
from typing import Any

import discord
from aiohttp import web
from discord.ext import commands, tasks

from config import metrics_port
from services.metrics_service import (
    bot_start_time,
    command_duration,
    command_usage,
    db_pool_size,
    guild_count,
    loop_iteration_duration,
    loop_iteration_errors,
    loop_running,
    messages_processed,
    shard_connected,
    shard_latency,
    update_process_metrics,
    user_count,
)

logger = logging.getLogger(__name__)


class PrometheusMetricsCog(commands.Cog):
    """Hooks into bot lifecycle events to export Prometheus metrics."""

    def __init__(self, bot: commands.AutoShardedBot) -> None:
        self.bot = bot
        self._runner: web.AppRunner | None = None
        self._site: web.TCPSite | None = None
        self._start_time: float = 0.0

    # ── Lifecycle ────────────────────────────────────────────────────────────

    async def cog_load(self) -> None:
        """Start the HTTP metrics server and background collection tasks."""
        self._start_time = time.time()
        bot_start_time.set(self._start_time)

        await self._start_http_server()
        if self._site is not None:
            logger.info("Prometheus metrics HTTP server started on port %s", metrics_port)
        else:
            logger.warning("Prometheus metrics HTTP server disabled (port %s unavailable)", metrics_port)

        # Start background metrics collection.
        self.collect_system_metrics.start()
        self.collect_shard_metrics.start()
        self.collect_db_pool_metrics.start()

    async def cog_unload(self) -> None:
        """Stop background tasks and HTTP server."""
        self.collect_system_metrics.cancel()
        self.collect_shard_metrics.cancel()
        self.collect_db_pool_metrics.cancel()
        if self._runner:
            try:
                await self._runner.cleanup()
            except Exception:
                logger.exception("Error cleaning up Prometheus HTTP runner")
            self._runner = None
            self._site = None
            logger.info("Prometheus metrics HTTP server stopped")

    # ── HTTP server for Prometheus scraping ──────────────────────────────────

    async def _start_http_server(self) -> None:
        """Start the aiohttp-based Prometheus metrics endpoint."""
        app = web.Application()

        async def metrics_handler(request: web.Request) -> web.Response:
            from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

            # Update process metrics synchronously before serving.
            update_process_metrics()
            data = generate_latest()
            return web.Response(body=data, headers={"Content-Type": CONTENT_TYPE_LATEST})

        async def health_handler(request: web.Request) -> web.Response:
            return web.Response(text="OK", content_type="text/plain")

        app.router.add_get("/metrics", metrics_handler)
        app.router.add_get("/health", health_handler)

        self._runner = web.AppRunner(app)
        await self._runner.setup()
        self._site = web.TCPSite(self._runner, "0.0.0.0", metrics_port)
        try:
            await self._site.start()
        except OSError as e:
            await self._runner.cleanup()
            self._runner = None
            self._site = None
            logger.warning(
                "Could not bind Prometheus metrics to 0.0.0.0:%s (%s); metrics HTTP disabled",
                metrics_port,
                e,
            )
            return
        logger.info("Prometheus /metrics endpoint ready on 0.0.0.0:%s", metrics_port)

    # ── Background collection tasks ──────────────────────────────────────────

    @tasks.loop(seconds=30)
    async def collect_system_metrics(self) -> None:
        """Collect and update process/system-level metrics."""
        set_loop_running("collect_system_metrics", True)
        start = time.monotonic()
        error = False
        try:
            update_process_metrics()
        except Exception:
            logger.exception("Failed to update system metrics")
            error = True
        finally:
            duration = time.monotonic() - start
            record_loop_iteration("collect_system_metrics", duration, error=error)
            set_loop_running("collect_system_metrics", False)

    @tasks.loop(seconds=60)
    async def collect_shard_metrics(self) -> None:
        """Collect and update shard-level metrics."""
        set_loop_running("collect_shard_metrics", True)
        start = time.monotonic()
        error = False
        try:
            shards = getattr(self.bot, "shards", {})
            for shard_id, shard in shards.items():
                try:
                    latency = shard.latency
                    shard_latency.labels(shard_id=str(shard_id)).set(latency or 0.0)
                    shard_connected.labels(shard_id=str(shard_id)).set(1.0 if shard.is_connected() else 0.0)
                except Exception:
                    shard_connected.labels(shard_id=str(shard_id)).set(0.0)

            # Update guild/user counts.
            try:
                guild_count.set(len(self.bot.guilds))
            except Exception:
                pass

            try:
                user_count.set(len(self.bot.users))
            except Exception:
                pass
        except Exception:
            logger.exception("Failed to update shard metrics")
            error = True
        finally:
            duration = time.monotonic() - start
            record_loop_iteration("collect_shard_metrics", duration, error=error)
            set_loop_running("collect_shard_metrics", False)

    @tasks.loop(seconds=60)
    async def collect_db_pool_metrics(self) -> None:
        """Collect and update database connection pool metrics."""
        set_loop_running("collect_db_pool_metrics", True)
        start = time.monotonic()
        error = False
        try:
            pool = getattr(self.bot, "_pool", None)
            if pool is not None:
                # asyncmy Pool has .minsize, .maxsize, .size (current open conns)
                minsize = getattr(pool, "minsize", 0)
                maxsize = getattr(pool, "maxsize", 0)
                cur_size = getattr(pool, "size", 0)
                db_pool_size.labels(type="min").set(minsize)
                db_pool_size.labels(type="max").set(maxsize)
                db_pool_size.labels(type="current").set(cur_size)
        except Exception:
            logger.exception("Failed to update DB pool metrics")
            error = True
        finally:
            duration = time.monotonic() - start
            record_loop_iteration("collect_db_pool_metrics", duration, error=error)
            set_loop_running("collect_db_pool_metrics", False)

    # ── Event hooks ──────────────────────────────────────────────────────────

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        """Count processed messages for throughput metrics."""
        if message.author.bot:
            return
        if message.guild is None:
            return

        messages_processed.labels(guild_id=str(message.guild.id)).inc()

    @commands.Cog.listener()
    async def on_app_command_completion(
        self,
        interaction: discord.Interaction,
        command: discord.app_commands.Command[Any, Any, Any] | None,
    ) -> None:
        """Record command usage metrics on completion."""
        try:
            cmd_name = command.qualified_name if command else "unknown"
            guild_id = str(interaction.guild_id) if interaction.guild_id else "dm"
            command_usage.labels(command=cmd_name, guild_id=guild_id, status="success").inc()
        except Exception:
            pass

    @commands.Cog.listener()
    async def on_command_completion(self, ctx: commands.Context[Any]) -> None:
        """Record prefix command usage metrics on completion."""
        try:
            cmd_name = ctx.command.qualified_name if ctx.command else "unknown"
            guild_id = str(ctx.guild.id) if ctx.guild else "dm"
            command_usage.labels(command=cmd_name, guild_id=guild_id, status="success").inc()
        except Exception:
            pass


# ── Standalone utilities for external instrumentation ─────────────────────────


def record_db_query(operation: str, duration: float, error: bool = False) -> None:
    """Record a database query duration and optionally an error.

    Called from api.py _execute_with_retry or similar.
    """
    try:
        from services.metrics_service import db_query_duration, db_query_errors

        db_query_duration.labels(operation=operation).observe(duration)
        if error:
            db_query_errors.labels(operation=operation).inc()
    except Exception:
        logger.exception("Failed to record DB query metric")


def record_command_execution(command_name: str, duration: float) -> None:
    """Record a command's execution duration.

    Called from command wrappers / error handlers.
    """
    command_duration.labels(command=command_name).observe(duration)


def record_loop_iteration(loop_name: str, duration: float, error: bool = False) -> None:
    """Record a background loop iteration duration.

    Called from loop wrappers.
    """
    loop_iteration_duration.labels(loop_name=loop_name).observe(duration)
    if error:
        loop_iteration_errors.labels(loop_name=loop_name).inc()


def set_loop_running(loop_name: str, running: bool) -> None:
    """Set the running gauge for a background loop."""
    loop_running.labels(loop_name=loop_name).set(1.0 if running else 0.0)


async def setup(bot: commands.AutoShardedBot) -> None:
    await bot.add_cog(PrometheusMetricsCog(bot))
