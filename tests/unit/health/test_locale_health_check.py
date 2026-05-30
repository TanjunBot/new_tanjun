"""Tests for locale_file_health_check.py."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

import pytest
from health.checks.locales import LocaleFileHealthCheck

from health.checks import HealthStatus


class TestLocaleFileHealthCheck:
    @pytest.fixture
    def check(self) -> LocaleFileHealthCheck:
        return LocaleFileHealthCheck()

    def test_name_and_critical(self, check: LocaleFileHealthCheck):
        assert check.name == "Locale Files"
        assert check.critical is True

    @pytest.mark.asyncio
    async def test_healthy_with_real_locales(self, check: LocaleFileHealthCheck):
        result = await check.run()
        assert result.status in (HealthStatus.HEALTHY, HealthStatus.DEGRADED)

    @pytest.mark.asyncio
    async def test_missing_file_critical(self, check: LocaleFileHealthCheck):
        with patch.object(Path, "exists", return_value=False):
            result = await check.run()
        assert result.status == HealthStatus.CRITICAL
        assert "Missing files" in result.message

    @pytest.mark.asyncio
    async def test_invalid_json_critical(self, check: LocaleFileHealthCheck):
        def fake_exists(self):
            return True

        with (
            patch.object(Path, "exists", fake_exists),
            patch(
                "builtins.open",
                side_effect=[
                    __import__("io").StringIO("not json"),
                    __import__("io").StringIO("not json"),
                ],
            ),
            patch.object(Path, "open"),
        ):
            check_copy = LocaleFileHealthCheck()
            with patch.object(check_copy, "LOCALES", ["en"]):
                with patch("health.checks.locales.Path") as mock_path_cls:
                    mock_path = mock_path_cls.return_value.__truediv__.return_value
                    mock_path.exists.return_value = True
                    mock_path.open.return_value.__enter__ = lambda s: s
                    mock_path.open.return_value.__exit__ = lambda *a: None
                    with patch("json.load", side_effect=json.JSONDecodeError("err", "", 0)):
                        result = await check_copy.run()
        assert result.status == HealthStatus.CRITICAL
