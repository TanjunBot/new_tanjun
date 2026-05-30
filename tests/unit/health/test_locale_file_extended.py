from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

import pytest

from health.checks import HealthStatus
from locale_file_health_check import LocaleFileHealthCheck


@pytest.mark.asyncio
async def test_invalid_structure_degraded():
    check = LocaleFileHealthCheck()
    with patch.object(Path, "exists", return_value=True):
        with patch("builtins.open", create=True):
            with patch("json.load", return_value=["not", "dicts"]):
                with patch.object(check, "LOCALES", ["en"]):
                    mock_path = Path("locales/en.json")
                    with patch.object(Path, "__truediv__", return_value=mock_path):
                        result = await check.run()
    assert result.status == HealthStatus.CRITICAL


@pytest.mark.asyncio
async def test_missing_required_key_degraded():
    check = LocaleFileHealthCheck()
    data = [{"identifier": "other.key", "translation": "x"}]

    def fake_open(*args, **kwargs):
        import io

        return io.StringIO(json.dumps(data))

    with patch.object(Path, "exists", return_value=True), patch("builtins.open", fake_open), patch(
        "json.load", return_value=data
    ):
        with patch.object(check, "LOCALES", ["en", "de"]):
            result = await check.run()
    assert result.status in (HealthStatus.DEGRADED, HealthStatus.CRITICAL)


@pytest.mark.asyncio
async def test_cross_locale_warnings():
    check = LocaleFileHealthCheck()
    base = [{"identifier": k, "translation": k} for k in LocaleFileHealthCheck.REQUIRED_KEYS]
    en_data = base + [{"identifier": "extra.key", "translation": "x"}]
    de_data = list(base)

    with patch.object(Path, "exists", return_value=True), patch("json.load", side_effect=[en_data, de_data]):
        result = await check.run()
    assert result.status == HealthStatus.HEALTHY
    assert "Warnings" in result.message or (result.details and "warnings" in result.details)
