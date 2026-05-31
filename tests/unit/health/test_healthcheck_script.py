"""Tests for healthcheck.py Docker health check script."""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

import healthcheck as hc


@pytest.fixture
def ready_file(monkeypatch):
    tmp = Path(tempfile.mkdtemp()) / "bot_ready"
    monkeypatch.setattr(hc, "READY_FILE", tmp)
    if tmp.exists():
        tmp.unlink()
    yield tmp
    if tmp.is_dir():
        tmp.rmdir()
    else:
        tmp.unlink(missing_ok=True)


class TestCheckHealth:
    def test_fails_when_ready_file_missing(self, ready_file):
        assert hc.check_health() is False

    def test_succeeds_when_ready_file_exists(self, ready_file):
        ready_file.touch()
        assert hc.check_health() is True

    def test_succeeds_when_metrics_health_ok(self, ready_file, monkeypatch):
        with patch.object(hc, "check_metrics_health", return_value=True):
            assert hc.check_health() is True

    def test_directory_named_bot_ready_is_not_ready(self, ready_file, monkeypatch):
        ready_file.mkdir()
        assert hc.check_health() is False


class TestHealthcheckMain:
    def test_main_exits_zero_on_success(self):
        with patch.object(hc, "check_health", return_value=True):
            with pytest.raises(SystemExit) as exc:
                hc.main()
        assert exc.value.code == 0

    def test_main_exits_one_on_failure(self):
        with patch.object(hc, "check_health", return_value=False):
            with pytest.raises(SystemExit) as exc:
                hc.main()
        assert exc.value.code == 1

    def test_ready_file_default_path(self):
        assert str(hc.READY_FILE).endswith(".bot_ready")

    def test_main_entrypoint(self):
        assert hc.__name__ == "healthcheck"
