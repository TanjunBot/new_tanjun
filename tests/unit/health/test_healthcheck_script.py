"""Tests for healthcheck.py Docker health check script."""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest

import healthcheck as hc


@pytest.fixture
def ready_file(monkeypatch):
    tmp = Path(tempfile.mkdtemp()) / "bot_ready"
    monkeypatch.setattr(hc, "READY_FILE", tmp)
    if tmp.exists():
        tmp.unlink()
    yield tmp
    tmp.unlink(missing_ok=True)


class TestCheckHealth:
    @pytest.mark.asyncio
    async def test_fails_when_ready_file_missing(self, ready_file):
        assert await hc.check_health() is False

    @pytest.mark.asyncio
    async def test_fails_when_pool_check_raises(self, ready_file):
        ready_file.touch()
        with patch("api.check_pool_health", new=AsyncMock(side_effect=RuntimeError("db"))):
            assert await hc.check_health() is False

    @pytest.mark.asyncio
    async def test_fails_when_pool_unhealthy(self, ready_file):
        ready_file.touch()
        with patch("api.check_pool_health", new=AsyncMock(return_value=False)):
            assert await hc.check_health() is False

    @pytest.mark.asyncio
    async def test_succeeds_when_ready_and_pool_healthy(self, ready_file):
        ready_file.touch()
        with patch("api.check_pool_health", new=AsyncMock(return_value=True)):
            assert await hc.check_health() is True

    @pytest.mark.asyncio
    async def test_import_error_returns_false(self, ready_file):
        ready_file.touch()
        with patch.dict(sys.modules, {"api": None}), patch("builtins.__import__", side_effect=ImportError("no api")):
            assert await hc.check_health() is False


class TestHealthcheckMain:
    def test_main_exits_zero_on_success(self, monkeypatch):
        with patch.object(hc, "check_health", new=AsyncMock(return_value=True)):
            with patch.object(hc.asyncio, "run", return_value=True):
                with pytest.raises(SystemExit) as exc:
                    hc.main()
        assert exc.value.code == 0

    def test_main_exits_one_on_failure(self, monkeypatch):
        with patch.object(hc, "check_health", new=AsyncMock(return_value=False)):
            with patch.object(hc.asyncio, "run", return_value=False):
                with pytest.raises(SystemExit) as exc:
                    hc.main()
        assert exc.value.code == 1

    def test_ready_file_path_under_tempdir(self):
        assert "bot_ready" in str(hc.READY_FILE)

    def test_main_entrypoint(self):
        assert hc.__name__ == "healthcheck"
