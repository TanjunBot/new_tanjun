"""Health check framework for Tanjun bot - compatibility shim.

Re-exports from the health package for backwards compatibility.

New code should import from the ``health`` package directly.
This shim will be removed after all imports have been migrated.
"""

from health.checks import HealthCheck, HealthCheckResult, HealthStatus
from health.checks.database import DatabaseHealthCheck
from health.checks.locales import LocaleFileHealthCheck
from health.checks.openai import OpenAIHealthCheck
from health.checks.twitch import TwitchAPIHealthCheck

__all__ = [
    "DatabaseHealthCheck",
    "HealthCheck",
    "HealthCheckResult",
    "HealthStatus",
    "LocaleFileHealthCheck",
    "OpenAIHealthCheck",
    "TwitchAPIHealthCheck",
]
