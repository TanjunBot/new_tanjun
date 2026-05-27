"""Health check framework for Tanjun bot.

Provides base classes, a manager, and a notification helper
for startup validation and periodic health monitoring.
"""

from health.checks import HealthCheck, HealthCheckResult, HealthStatus
from health.manager import HealthCheckManager
from health.notifier import notify_health_failures

__all__ = [
    "HealthCheck",
    "HealthCheckResult",
    "HealthStatus",
    "HealthCheckManager",
    "notify_health_failures",
]
