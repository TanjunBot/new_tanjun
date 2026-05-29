"""Health check framework for Tanjun bot.

Re-exports from the health package for backwards compatibility.

Defines the base classes for all health checks:
- HealthCheck: abstract base class
- HealthCheckResult: result container
- HealthStatus: status enum

New code should import from the ``health`` package directly.
"""

from health.checks import HealthCheck, HealthCheckResult, HealthStatus
from health.checks.database_check import DatabaseHealthCheck
from health.checks.openai_check import OpenAIHealthCheck
from health.checks.twitch_check import TwitchAPIHealthCheck
from locale_file_health_check import LocaleFileHealthCheck

__all__ = [
    "DatabaseHealthCheck",
    "HealthCheck",
    "HealthCheckResult",
    "HealthStatus",
    "LocaleFileHealthCheck",
    "OpenAIHealthCheck",
    "TwitchAPIHealthCheck",
]
