"""Tests for health/checks.py base classes."""

from __future__ import annotations

from datetime import UTC, datetime

from health.checks import HealthCheck, HealthCheckResult, HealthStatus


class TestHealthStatus:
    def test_enum_values(self):
        assert HealthStatus.HEALTHY.value == "healthy"
        assert HealthStatus.DEGRADED.value == "degraded"
        assert HealthStatus.CRITICAL.value == "critical"
        assert HealthStatus.UNKNOWN.value == "unknown"


class TestHealthCheckResult:
    def test_creation(self):
        result = HealthCheckResult(
            check_name="Test",
            status=HealthStatus.HEALTHY,
            message="All good",
        )
        assert result.check_name == "Test"
        assert result.status == HealthStatus.HEALTHY
        assert result.details is None
        assert result.timestamp.tzinfo == UTC

    def test_with_details(self):
        result = HealthCheckResult(
            check_name="Test",
            status=HealthStatus.DEGRADED,
            message="Slow",
            details={"latency_ms": 500},
        )
        assert result.details["latency_ms"] == 500


class TestHealthCheckABC:
    def test_cannot_instantiate_abstract(self):
        import pytest

        with pytest.raises(TypeError):
            HealthCheck()

    def test_concrete_implementation(self):
        class DummyCheck(HealthCheck):
            @property
            def name(self) -> str:
                return "Dummy"

            @property
            def critical(self) -> bool:
                return False

            async def run(self) -> HealthCheckResult:
                return HealthCheckResult(self.name, HealthStatus.HEALTHY, "ok")

        check = DummyCheck()
        assert check.name == "Dummy"
        assert check.critical is False
