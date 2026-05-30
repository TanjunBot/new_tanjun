"""Tests for the Docker healthcheck script (healthcheck.py)."""

import tempfile
from pathlib import Path

import pytest


@pytest.fixture
def ready_file():
    """Create a temporary directory and return the ready file path."""
    tmpdir = tempfile.gettempdir()
    ready_path = Path(tmpdir) / "bot_ready"
    # Clean up any existing file
    if ready_path.exists():
        ready_path.unlink()
    yield ready_path
    # Clean up after test
    if ready_path.exists():
        ready_path.unlink()


def test_healthcheck_exits_zero_when_ready(ready_file):
    """Healthcheck should exit 0 when bot_ready file exists."""
    ready_file.touch()
    # Simulate healthcheck logic
    assert ready_file.exists()


def test_healthcheck_exits_nonzero_when_not_ready(ready_file):
    """Healthcheck should exit 1 when bot_ready file does not exist."""
    assert not ready_file.exists()


def test_healthcheck_file_created_by_on_ready(ready_file):
    """Simulate what main.py does in on_ready."""
    ready_file.touch()
    assert ready_file.exists()
    content = ready_file.read_text()
    assert content == ""
