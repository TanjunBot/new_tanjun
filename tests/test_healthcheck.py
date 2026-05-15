"""Tests for healthcheck.py — comprehensive."""
from pathlib import Path
from unittest.mock import patch

import pytest

from tests.mock_config import patch_config_module

patch_config_module()

from healthcheck import main, READY_FILE


class TestHealthcheckMain:
    @patch.object(Path, "exists", return_value=True)
    def test_exits_0_when_ready_file_exists(self, mock_exists):
        with pytest.raises(SystemExit) as exc_info:
            main()
        assert exc_info.value.code == 0

    @patch.object(Path, "exists", return_value=False)
    def test_exits_1_when_ready_file_missing(self, mock_exists):
        with pytest.raises(SystemExit) as exc_info:
            main()
        assert exc_info.value.code == 1

    def test_ready_file_constant(self):
        assert READY_FILE == Path("/tmp/bot_ready")

    def test_ready_file_is_absolute_path(self):
        assert READY_FILE.is_absolute()

    def test_ready_file_str_representation(self):
        assert str(READY_FILE) == "/tmp/bot_ready"

    @patch.object(Path, "exists", return_value=True)
    def test_healthy_exit_code_is_zero(self, mock_exists):
        with pytest.raises(SystemExit) as exc_info:
            main()
        assert exc_info.value.code == 0

    @patch.object(Path, "exists", return_value=False)
    def test_unhealthy_exit_code_is_one(self, mock_exists):
        with pytest.raises(SystemExit) as exc_info:
            main()
        assert exc_info.value.code == 1

    @patch.object(Path, "exists", return_value=True)
    def test_healthy_does_not_return_normally(self, mock_exists):
        """main() should sys.exit, not return normally."""
        with pytest.raises(SystemExit):
            main()

    @patch.object(Path, "exists", return_value=False)
    def test_unhealthy_does_not_return_normally(self, mock_exists):
        with pytest.raises(SystemExit):
            main()

    @patch.object(Path, "exists", return_value=True)
    def test_multiple_consecutive_checks(self, mock_exists):
        """Health check should work consistently across multiple calls."""
        for _ in range(5):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 0