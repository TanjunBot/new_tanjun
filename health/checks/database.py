"""Database connectivity health check for Tanjun bot.

Validates:
1. Pool exists: bot._pool is not None
2. Database reachable: standalone connection + SELECT 1 (does not use the pool)
3. Pool utilization: warn if >80% of maxsize connections are active
"""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

from health.checks import HealthCheck, HealthCheckResult, HealthStatus

if TYPE_CHECKING:
    from asyncmy import Pool


async def _ping_database() -> None:
    import asyncmy

    from config import settings

    conn = await asyncio.wait_for(
        asyncmy.connect(
            host=settings.database_ip,
            port=settings.database_port,
            user=settings.database_user,
            password=settings.database_password.get_secret_value(),
            db=settings.database_schema,
            connect_timeout=5,
        ),
        timeout=8,
    )
    try:
        async with conn.cursor() as cursor:
            await asyncio.wait_for(cursor.execute("SELECT 1"), timeout=5)
            result = await cursor.fetchone()
            if not result or result[0] != 1:
                raise ValueError("SELECT 1 returned unexpected result")
    finally:
        conn.close()


class DatabaseHealthCheck(HealthCheck):
    """Health check for the MySQL database connection pool."""

    @property
    def name(self) -> str:
        return "Database"

    @property
    def critical(self) -> bool:
        return True

    async def run(self) -> HealthCheckResult:
        pool = self._get_pool()
        if pool is None:
            return HealthCheckResult(
                check_name=self.name,
                status=HealthStatus.CRITICAL,
                message="Database pool is None. Pool was not initialized.",
            )

        details: dict[str, object] = {}
        pool_size = pool.size
        pool_maxsize = pool.maxsize
        pool_freesize = pool.freesize
        active = max(0, pool_size - pool_freesize)

        details["pool_size"] = pool_size
        details["pool_maxsize"] = pool_maxsize
        details["pool_freesize"] = pool_freesize
        details["pool_active"] = active

        utilization = (active / pool_maxsize) * 100 if pool_maxsize > 0 else 0
        details["utilization_pct"] = round(utilization, 1)

        try:
            await _ping_database()
        except TimeoutError:
            return HealthCheckResult(
                check_name=self.name,
                status=HealthStatus.CRITICAL,
                message="Timed out connecting to database.",
                details=details,
            )
        except Exception as e:
            return HealthCheckResult(
                check_name=self.name,
                status=HealthStatus.CRITICAL,
                message=f"Database connection failed: {e}",
                details=details,
            )

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
            message="Database is reachable and the connection pool is initialized.",
            details=details,
        )

    @staticmethod
    def _get_pool() -> Pool | None:
        from api import _get_pool

        return _get_pool()
