"""Health check manager for Tanjun bot.

Orchestrates startup validation and periodic health monitoring.
"""
from __future__ import annotations

from locale_keys import locale
import asyncio
import logging
from typing import TYPE_CHECKING
from health.checks import HealthCheck, HealthCheckResult, HealthStatus
from health.notifier import notify_health_failures
if TYPE_CHECKING:
    from discord.ext import commands
logger = logging.getLogger(__name__)

class HealthCheckManager:
    """Manages registration and execution of health checks.

    Handles:
    - Registering health checks
    - Running all checks concurrently at startup
    - Periodic health monitoring during operation
    - Notifying failures to the designated Discord channel
    """

    def __init__(self, bot: commands.AutoShardedBot) -> None:
        self.bot = bot
        self._checks: list[HealthCheck] = []
        self._check_intervals: dict[str, int] = {}
        self._last_results: dict[str, HealthCheckResult] = {}
        self._running = False
        self._periodic_task: asyncio.Task[None] | None = None

    def register(self, check: HealthCheck, interval: int | None=None) -> None:
        """Register a health check.

        Args:
            check: The health check to register.
            interval: Optional interval in seconds for periodic checks.
                      If None, uses the default interval from start_periodic_checks.
        """
        self._checks.append(check)
        if interval is not None:
            self._check_intervals[check.name] = interval
        logger.info('Registered health check: %s (critical=%s, interval=%s)', check.name, check.critical, interval or 'default')

    async def run_all(self) -> list[HealthCheckResult]:
        """Run all registered checks concurrently and return results."""
        if not self._checks:
            logger.warning('No health checks registered')
            return []
        raw_results = await asyncio.gather(*(check.run() for check in self._checks), return_exceptions=True)
        results: list[HealthCheckResult] = []
        for check, raw in zip(self._checks, raw_results, strict=False):
            if isinstance(raw, BaseException):
                result = HealthCheckResult(check_name=check.name, status=HealthStatus.CRITICAL, message=f'Health check raised an unexpected exception: {raw}')
                logger.exception('Health check %s raised an exception', check.name, exc_info=(type(raw), raw, raw.__traceback__))
            else:
                result = raw
            self._last_results[result.check_name] = result
            results.append(result)
        return results

    async def run_startup_checks(self) -> tuple[bool, list[HealthCheckResult]]:
        """Run all checks at startup.

        Returns:
            A tuple of (ok, critical_failures) where ok is True if all
            critical checks passed, and critical_failures contains the
            HealthCheckResult for each failing critical check.
        """
        logger.info('Running startup health checks...')
        results = await self.run_all()
        critical_failures = [result for check, result in zip(self._checks, results, strict=False) if check.critical and result.status == HealthStatus.CRITICAL]
        degraded = [r for r in results if r.status == HealthStatus.DEGRADED]
        healthy = [r for r in results if r.status == HealthStatus.HEALTHY]
        logger.info('Health check summary: %d healthy, %d degraded, %d critical failures', len(healthy), len(degraded), len(critical_failures))
        for result in results:
            level = logging.WARNING if result.status != HealthStatus.HEALTHY else logging.INFO
            logger.log(level, '  [%s] %s: %s', result.status.value, result.check_name, result.message)
        if critical_failures:
            logger.error('FATAL: %d critical health check(s) failed. Bot cannot start.', len(critical_failures))
            return (False, critical_failures)
        return (True, [])

    async def notify_critical_failures(self) -> None:
        """Notify the designated Discord channel about critical startup failures."""
        critical_results = [r for r in self._last_results.values() if r.status == HealthStatus.CRITICAL]
        if critical_results:
            await notify_health_failures(self.bot, critical_results)

    async def start_periodic_checks(self, interval: int=300) -> None:
        """Start periodic health checks every *interval* seconds.

        Args:
            interval: Default seconds between check runs (default 300 = 5 minutes).
                      Individual checks may have custom intervals set via register().
        """
        if interval <= 0:
            raise ValueError('interval must be > 0')
        if self._running:
            logger.warning('Periodic health checks already running')
            return
        self._running = True
        logger.info('Starting periodic health checks (default_interval=%ds)', interval)
        last_run: dict[str, float] = {}

        async def _periodic_loop() -> None:
            while self._running:
                await asyncio.sleep(interval)
                try:
                    import time
                    current_time = time.time()
                    checks_to_run: list[HealthCheck] = []
                    for check in self._checks:
                        check_interval = self._check_intervals.get(check.name, interval)
                        last_run_time = last_run.get(check.name, 0)
                        if current_time - last_run_time >= check_interval:
                            checks_to_run.append(check)
                            last_run[check.name] = current_time
                    if checks_to_run:
                        raw_results = await asyncio.gather(*(check.run() for check in checks_to_run), return_exceptions=True)
                        results: list[HealthCheckResult] = []
                        for check, raw in zip(checks_to_run, raw_results, strict=False):
                            if isinstance(raw, BaseException):
                                result = HealthCheckResult(check_name=check.name, status=HealthStatus.CRITICAL, message=f'Health check raised an unexpected exception: {raw}')
                                logger.exception('Health check %s raised an exception', check.name, exc_info=(type(raw), raw, raw.__traceback__))
                            else:
                                result = raw
                            self._last_results[result.check_name] = result
                            results.append(result)
                        failures = [r for r in results if r.status in (HealthStatus.CRITICAL, HealthStatus.DEGRADED)]
                        if failures:
                            await notify_health_failures(self.bot, failures)
                except Exception:
                    logger.exception('Periodic health check iteration failed')
        self._periodic_task = asyncio.create_task(_periodic_loop())

    def stop_periodic_checks(self) -> None:
        """Stop periodic health checks."""
        self._running = False
        if self._periodic_task is not None:
            self._periodic_task.cancel()
            self._periodic_task = None
        logger.info('Periodic health checks stopped')
