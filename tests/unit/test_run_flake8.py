from __future__ import annotations

from unittest.mock import MagicMock, patch

import importlib

import run_flake8


def test_recursion_limit_set():
    assert run_flake8.sys.getrecursionlimit() >= 10000


@patch("subprocess.run")
def test_module_runs_flake8_on_reload(mock_run):
    mock_run.return_value = MagicMock(returncode=0)
    importlib.reload(run_flake8)
    assert mock_run.call_count >= 2
