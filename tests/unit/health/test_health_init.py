"""Tests for health/__init__.py public API."""

from __future__ import annotations

import health


class TestHealthPackageInit:
    def test_exports_all_symbols(self):
        expected = {
            "BrawlStarsHealthCheck",
            "BytebinHealthCheck",
            "DatabaseHealthCheck",
            "GIPHYHealthCheck",
            "GitHubAPIHealthCheck",
            "HealthCheck",
            "HealthCheckManager",
            "HealthCheckResult",
            "HealthStatus",
            "ImgBBHealthCheck",
            "LocaleFileHealthCheck",
            "OpenAIHealthCheck",
            "TwitchAPIHealthCheck",
            "notify_health_failures",
        }
        assert set(health.__all__) == expected

    def test_importable_from_package(self):
        assert health.HealthCheckManager.__name__ == "HealthCheckManager"
        assert callable(health.notify_health_failures)
