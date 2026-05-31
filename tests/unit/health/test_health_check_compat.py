"""Tests for health package public exports."""

from __future__ import annotations

import health


class TestHealthPackageExports:
    def test_exports_health_check_base_classes(self):
        assert health.HealthCheck is not None
        assert health.HealthCheckResult is not None
        assert health.HealthStatus is not None

    def test_exports_concrete_checks(self):
        assert health.DatabaseHealthCheck is not None
        assert health.LocaleFileHealthCheck is not None
        assert health.OpenRouterHealthCheck is not None
        assert health.TwitchAPIHealthCheck is not None

    def test_all_list_matches_exports(self):
        for name in health.__all__:
            assert hasattr(health, name)

    def test_health_status_from_reexport(self):
        assert health.HealthStatus.HEALTHY.value == "healthy"
