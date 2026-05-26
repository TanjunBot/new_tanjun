"""Health check framework for Tanjun bot.

Defines the base classes for all health checks:
- HealthCheck: abstract base class
- HealthCheckResult: result container
- HealthStatus: status enum
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class HealthStatus(Enum):
    """Status of a health check."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    CRITICAL = "critical"


@dataclass
class HealthCheckResult:
    """Result of a single health check."""
    check_name: str
    status: HealthStatus
    message: str
    details: dict[str, Any] | None = None


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
