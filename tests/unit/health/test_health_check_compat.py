"""Tests for health_check.py backwards-compatibility re-exports."""

from __future__ import annotations

import health_check


class TestHealthCheckCompatModule:
    def test_exports_health_check_base_classes(self):
        assert health_check.HealthCheck is not None
        assert health_check.HealthCheckResult is not None
        assert health_check.HealthStatus is not None

    def test_exports_concrete_checks(self):
        assert health_check.DatabaseHealthCheck is not None
        assert health_check.LocaleFileHealthCheck is not None
        assert health_check.OpenAIHealthCheck is not None
        assert health_check.TwitchAPIHealthCheck is not None

    def test_all_list_matches_exports(self):
        for name in health_check.__all__:
            assert hasattr(health_check, name)

    def test_health_status_from_reexport(self):
        assert health_check.HealthStatus.HEALTHY.value == "healthy"
