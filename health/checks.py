"""Health check base classes for Tanjun bot.

Defines:
- HealthStatus enum
- HealthCheckResult dataclass
- HealthCheck abstract base class
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any


class HealthStatus(Enum):
    """Status of a health check."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    CRITICAL = "critical"
    UNKNOWN = "unknown"


@dataclass
class HealthCheckResult:
    """Result of a single health check."""
    check_name: str
    status: HealthStatus
    message: str
    details: dict[str, Any] | None = None
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class HealthCheck(ABC):
    """Abstract base class for all health checks."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable name of this health check."""
        ...

    @property
    @abstractmethod
    def critical(self) -> bool:
        """Whether failure of this check is critical for the bot."""
        ...

    @abstractmethod
    async def run(self) -> HealthCheckResult:
        """Execute the health check and return the result."""
        ...
