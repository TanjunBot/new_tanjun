"""Health check framework for Tanjun bot.

Provides base classes, a manager, and a notification helper
for startup validation and periodic health monitoring.
"""

from health.checks import HealthCheck, HealthCheckResult, HealthStatus
from health.checks.database import DatabaseHealthCheck
from health.checks.external import (
    BrawlStarsHealthCheck,
    BytebinHealthCheck,
    GIPHYHealthCheck,
    GitHubAPIHealthCheck,
    ImgBBHealthCheck,
)
from health.checks.locales import LocaleFileHealthCheck
from health.checks.openrouter import OpenRouterHealthCheck
from health.checks.twitch import TwitchAPIHealthCheck
from health.manager import HealthCheckManager
from health.notifier import notify_health_failures

__all__ = [
    "BrawlStarsHealthCheck",
    "BytebinHealthCheck",
    "DatabaseHealthCheck",
    "GIPHYHealthCheck",
    "GitHubAPIHealthCheck",
    "HealthCheck",
    "HealthCheckResult",
    "HealthStatus",
    "HealthCheckManager",
    "ImgBBHealthCheck",
    "LocaleFileHealthCheck",
    "OpenRouterHealthCheck",
    "TwitchAPIHealthCheck",
    "notify_health_failures",
]
