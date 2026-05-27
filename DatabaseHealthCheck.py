"""Database connectivity health check for Tanjun bot.

Validates:
1. Pool exists: bot._pool is not None
2. Connection works: pool.acquire() succeeds
3. Query executes: SELECT 1 returns results
4. Pool utilization: Not near maxsize (warn if >80% utilized)
"""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

from health.checks import HealthCheck, HealthCheckResult, HealthStatus

if TYPE_CHECKING:
    from asyncmy import Pool


class DatabaseHealthCheck(HealthCheck):
    """Health check for the MySQL database connection pool."""

    @property
    def name(self) -> str:
        return "Database"

    @property
    def critical(self) -> bool:
        return True  # Bot cannot function without DB

    async def run(self) -> HealthCheckResult:
        pool = self._get_pool()
        if pool is None:
            return HealthCheckResult(
                check_name=self.name,
                status=HealthStatus.CRITICAL,
                message="Database pool is None. Pool was not initialized.",
            )

        details: dict[str, object] = {}

        try:
            # Check pool utilization
            pool_size = pool.size
            pool_maxsize = pool.maxsize
            pool_freesize = pool.freesize
            active = max(0, pool_size - pool_freesize)

            details["pool_size"] = pool_size
            details["pool_maxsize"] = pool_maxsize
            details["pool_freesize"] = pool.freesize
            details["pool_active"] = active

            utilization = (active / pool_maxsize) * 100 if pool_maxsize > 0 else 0

            # Acquire a connection and run SELECT 1
            async with pool.acquire() as conn:
                async with conn.cursor() as cursor:
                    await cursor.execute("SELECT 1")
                    result = await cursor.fetchone()
                    if not result or result[0] != 1:
                        return HealthCheckResult(
                            check_name=self.name,
                            status=HealthStatus.CRITICAL,
                            message="SELECT 1 returned unexpected result.",
                        )

            details["utilization_pct"] = round(utilization, 1)

            if utilization > 80:
                return HealthCheckResult(
                    check_name=self.name,
                    status=HealthStatus.DEGRADED,
                    message=(
                        f"Database pool utilization is high ({utilization:.1f}%): "
                        f"{active}/{pool_maxsize} connections active."
                    ),
                    details=details,
                )

            return HealthCheckResult(
                check_name=self.name,
                status=HealthStatus.HEALTHY,
                message="Database pool is connected and queries execute successfully.",
                details=details,
            )

        except asyncio.TimeoutError:
            return HealthCheckResult(
                check_name=self.name,
                status=HealthStatus.CRITICAL,
                message="Timed out acquiring database connection.",
            )
        except Exception as e:
            return HealthCheckResult(
                check_name=self.name,
                status=HealthStatus.CRITICAL,
                message=f"Database connection failed: {e}",
            )

    @staticmethod
    def _get_pool() -> Pool | None:
        """Get the database pool from the bot instance."""
        from api import _get_pool

        return _get_pool()
