"""Unit tests for container startup entrypoint."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

ROOT = Path(__file__).resolve().parents[3]


def _load_entrypoint():
    path = ROOT / "scripts" / "docker_entrypoint.py"
    spec = importlib.util.spec_from_file_location("docker_entrypoint", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules["docker_entrypoint"] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def entrypoint():
    return _load_entrypoint()


pytestmark = pytest.mark.unit


def test_wait_for_database_succeeds_on_first_attempt(entrypoint) -> None:
    engine = MagicMock()
    connection = MagicMock()
    engine.connect.return_value.__enter__ = MagicMock(return_value=connection)
    engine.connect.return_value.__exit__ = MagicMock(return_value=None)

    with (
        patch.object(entrypoint, "time"),
        patch("sqlalchemy.create_engine", return_value=engine),
        patch("utils.db_migration.get_database_url", return_value="mysql+pymysql://u:p@h/db"),
    ):
        entrypoint._wait_for_database()

    connection.execute.assert_called_once()


def test_wait_for_database_retries_then_raises(entrypoint) -> None:
    engine = MagicMock()
    engine.connect.side_effect = OSError("connection refused")

    with (
        patch.object(entrypoint, "time"),
        patch.object(entrypoint, "_DB_WAIT_ATTEMPTS", 2),
        patch("sqlalchemy.create_engine", return_value=engine),
        patch("utils.db_migration.get_database_url", return_value="mysql+pymysql://u:p@h/db"),
        pytest.raises(RuntimeError, match="Database not reachable"),
    ):
        entrypoint._wait_for_database()

    assert engine.connect.call_count == 2


def test_main_runs_wait_migrate_and_exec(entrypoint) -> None:
    with (
        patch.object(entrypoint, "_wait_for_database") as wait_db,
        patch("utils.db_migration.ensure_database_schema") as ensure,
        patch.object(entrypoint.os, "chdir"),
        patch.object(entrypoint.os, "execvp") as execvp,
    ):
        entrypoint.main()

    wait_db.assert_called_once()
    ensure.assert_called_once()
    execvp.assert_called_once()
    assert execvp.call_args[0][1][1] == "main.py"
