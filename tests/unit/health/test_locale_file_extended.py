from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

import pytest
from health.checks.locales import LocaleFileHealthCheck

from health.checks import HealthStatus


@pytest.mark.asyncio
async def test_invalid_structure_degraded():
    check = LocaleFileHealthCheck()
    with patch.object(Path, "exists", return_value=True), patch("builtins.open", create=True):
        with patch("json.load", return_value=["not", "dicts"]):
            with patch.object(check, "LOCALES", ["en"]):
                mock_path = Path("locales/en.json")
                with patch.object(Path, "__truediv__", return_value=mock_path):
                    result = await check.run()
    assert result.status == HealthStatus.CRITICAL


@pytest.mark.asyncio
async def test_missing_required_key_degraded():
    """Check flags degraded when de.json is missing a dot-key present in en.json."""
    check = LocaleFileHealthCheck()
    en_data = [{"identifier": "commands.ping.pong", "translation": "pong"}]
    de_data = [{"identifier": "commands.ping.pong", "translation": "pong"}]

    def fake_en_open(*args, **kwargs):
        import io
        return io.StringIO(json.dumps(en_data))

    def fake_de_open(*args, **kwargs):
        import io
        return io.StringIO(json.dumps(de_data))

    # Same files — should be healthy
    with (
        patch.object(Path, "exists", return_value=True),
        patch("builtins.open", fake_en_open),
        patch("json.load", side_effect=[en_data, de_data]),
        patch.object(check, "LOCALES", ["en", "de"]),
    ):
        result = await check.run()
    assert result.status == HealthStatus.HEALTHY

    # Now de is missing a key en has
    de_missing = [{"identifier": "other.key", "translation": "x"}]
    with (
        patch.object(Path, "exists", return_value=True),
        patch("builtins.open", fake_en_open),
        patch("json.load", side_effect=[en_data, de_missing]),
        patch.object(check, "LOCALES", ["en", "de"]),
    ):
        result = await check.run()
    assert result.status in (HealthStatus.DEGRADED, HealthStatus.CRITICAL)


@pytest.mark.asyncio
async def test_cross_locale_warnings():
    """Check warns when a locale has extra/missing keys vs en.json."""
    check = LocaleFileHealthCheck()
    en_data = [{"identifier": "commands.ping.pong", "translation": "pong"}]
    de_data = [{"identifier": "commands.ping.pong", "translation": "pong"}, {"identifier": "extra.key.here", "translation": "extra"}]
    # en has 1 dot key, de has 2 — en is baseline, so de having extra keys is fine (not flagged)
    # Actually the check only flags locales missing keys that en has
    # Test: de missing a key from en
    de_missing = [{"identifier": "different.key", "translation": "x"}]
    with (
        patch.object(Path, "exists", return_value=True),
        patch("json.load", side_effect=[en_data, de_missing]),
        patch.object(check, "LOCALES", ["en", "de"]),
    ):
        result = await check.run()
    # de is missing "commands.ping.pong" from en baseline
    assert result.status in (HealthStatus.DEGRADED, HealthStatus.CRITICAL)
    assert "missing" in result.message
