"""Tests for startup migration orchestration."""

from __future__ import annotations

import importlib.util
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

import tests.mock_config as mock_config

mock_config.patch_config_module()

from utils.db_migration import (  # noqa: E402
    DANGEROUSLY_DEBUG_PRINT_DATABASE_ENV,
    _revision_state,
    dangerously_debug_print_database_enabled,
    ensure_database_schema,
    format_database_connection_debug,
    get_database_url,
    log_database_connection_debug,
    resolve_database_connection_params,
    run_alembic_upgrade_head,
)

pytestmark = pytest.mark.unit

ROOT = Path(__file__).resolve().parents[3]
HEAD = "006_giveaway_id_not_null"


def _engine_context(connection: MagicMock) -> MagicMock:
    engine = MagicMock()
    engine.connect.return_value.__enter__ = MagicMock(return_value=connection)
    engine.connect.return_value.__exit__ = MagicMock(return_value=None)
    return engine


def test_stamps_head_when_schema_matches_but_alembic_untracked() -> None:
    cfg = MagicMock()
    with (
        patch("utils.db_migration._alembic_config", return_value=cfg),
        patch("utils.db_migration._revision_state", return_value=(None, HEAD)),
        patch("sqlalchemy.create_engine", return_value=MagicMock()),
        patch("utils.schema_conformance.schema_has_drift", return_value=[]),
        patch("alembic.command.stamp") as stamp,
        patch("alembic.command.upgrade") as upgrade,
    ):
        ensure_database_schema()

    stamp.assert_called_once_with(cfg, "head")
    upgrade.assert_not_called()


def test_upgrades_when_schema_has_drift() -> None:
    cfg = MagicMock()
    engine = _engine_context(MagicMock())

    with (
        patch("utils.db_migration._alembic_config", return_value=cfg),
        patch("utils.db_migration._revision_state", return_value=(None, HEAD)),
        patch("sqlalchemy.create_engine", return_value=engine),
        patch(
            "utils.schema_conformance.schema_has_drift",
            side_effect=[["table `giveaway` is missing"], []],
        ),
        patch("alembic.command.stamp") as stamp,
        patch("alembic.command.upgrade") as upgrade,
    ):
        ensure_database_schema()

    stamp.assert_not_called()
    upgrade.assert_called_once_with(cfg, "head")


def test_upgrades_when_revision_behind_even_without_drift() -> None:
    cfg = MagicMock()
    engine = _engine_context(MagicMock())

    with (
        patch("utils.db_migration._alembic_config", return_value=cfg),
        patch("utils.db_migration._revision_state", return_value=("001_initial_schema", HEAD)),
        patch("sqlalchemy.create_engine", return_value=engine),
        patch("utils.schema_conformance.schema_has_drift", return_value=[]),
        patch("alembic.command.stamp") as stamp,
        patch("alembic.command.upgrade") as upgrade,
    ):
        ensure_database_schema()

    stamp.assert_not_called()
    upgrade.assert_called_once_with(cfg, "head")


def test_no_op_when_already_at_head() -> None:
    cfg = MagicMock()
    with (
        patch("utils.db_migration._alembic_config", return_value=cfg),
        patch("utils.db_migration._revision_state", return_value=(HEAD, HEAD)),
        patch("sqlalchemy.create_engine", return_value=MagicMock()),
        patch("utils.schema_conformance.schema_has_drift", return_value=[]),
        patch("alembic.command.stamp") as stamp,
        patch("alembic.command.upgrade") as upgrade,
    ):
        ensure_database_schema()

    stamp.assert_not_called()
    upgrade.assert_not_called()


def test_raises_when_drift_at_head() -> None:
    cfg = MagicMock()
    engine = _engine_context(MagicMock())
    drift = ["table `giveaway` missing columns: giveaway_id"]

    with (
        patch("utils.db_migration._alembic_config", return_value=cfg),
        patch("utils.db_migration._revision_state", return_value=(HEAD, HEAD)),
        patch("sqlalchemy.create_engine", return_value=engine),
        patch("utils.schema_conformance.schema_has_drift", return_value=drift),
        pytest.raises(RuntimeError, match="Schema drift detected at Alembic head"),
    ):
        ensure_database_schema()


def test_raises_when_upgrade_leaves_drift() -> None:
    cfg = MagicMock()
    engine = _engine_context(MagicMock())
    remaining = ["table `reports` missing columns: status"]

    with (
        patch("utils.db_migration._alembic_config", return_value=cfg),
        patch("utils.db_migration._revision_state", return_value=(None, HEAD)),
        patch("sqlalchemy.create_engine", return_value=engine),
        patch("utils.schema_conformance.schema_has_drift", side_effect=[[remaining[0]], remaining]),
        patch("alembic.command.upgrade"),
        pytest.raises(RuntimeError, match="still incomplete after alembic upgrade"),
    ):
        ensure_database_schema()


def test_raises_when_no_alembic_head() -> None:
    cfg = MagicMock()
    with (
        patch("utils.db_migration._alembic_config", return_value=cfg),
        patch("utils.db_migration._revision_state", return_value=(None, None)),
        pytest.raises(RuntimeError, match="No Alembic head revision"),
    ):
        ensure_database_schema()


def test_run_alembic_upgrade_head_delegates_to_ensure() -> None:
    with patch("utils.db_migration.ensure_database_schema") as ensure:
        run_alembic_upgrade_head()
    ensure.assert_called_once()


def test_get_database_url_uses_test_env_vars(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("TANJUN_TEST_DB_HOST", "db.example")
    monkeypatch.setenv("TANJUN_TEST_DB_PORT", "3308")
    monkeypatch.setenv("TANJUN_TEST_DB_USER", "u")
    monkeypatch.setenv("TANJUN_TEST_DB_PASSWORD", "@")
    monkeypatch.setenv("TANJUN_TEST_DB_NAME", "mydb")

    url = get_database_url()

    assert "db.example:3308/mydb" in url
    assert "u:" in url
    assert "%40" in url


def test_revision_state_returns_none_when_version_table_missing() -> None:
    cfg = MagicMock()
    connection = MagicMock()
    context = MagicMock()
    context.get_current_revision.side_effect = Exception("no alembic_version")
    engine = MagicMock()
    engine.connect.return_value.__enter__.return_value = connection

    with (
        patch("alembic.script.ScriptDirectory.from_config") as script_dir,
        patch("sqlalchemy.create_engine", return_value=engine),
        patch("alembic.runtime.migration.MigrationContext.configure", return_value=context),
    ):
        script_dir.return_value.get_current_head.return_value = HEAD
        current, head = _revision_state(cfg)

    assert current is None
    assert head == HEAD


def test_get_database_url_falls_back_to_settings() -> None:
    settings = MagicMock()
    settings.database_ip = "127.0.0.1"
    settings.database_port = 3306
    settings.database_user = "root"
    settings.database_password.get_secret_value.return_value = ""
    settings.database_schema = "tanjun"
    with (
        patch("utils.db_migration._first_env", return_value=None),
        patch("config.settings", settings),
    ):
        url = get_database_url()
    assert "127.0.0.1:3306/tanjun" in url
    assert "@127.0.0.1" in url


def test_resolve_database_connection_params_from_test_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("TANJUN_TEST_DB_HOST", "db.example")
    monkeypatch.setenv("TANJUN_TEST_DB_PORT", "3308")
    monkeypatch.setenv("TANJUN_TEST_DB_USER", "u")
    monkeypatch.setenv("TANJUN_TEST_DB_PASSWORD", "secret")
    monkeypatch.setenv("TANJUN_TEST_DB_NAME", "mydb")

    params = resolve_database_connection_params()

    assert params.host == "db.example"
    assert params.port == 3308
    assert params.user == "u"
    assert params.password == "secret"
    assert params.database == "mydb"
    assert params.sources["host"] == "TANJUN_TEST_DB_HOST"


def test_dangerously_debug_print_database_enabled(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv(DANGEROUSLY_DEBUG_PRINT_DATABASE_ENV, raising=False)
    assert not dangerously_debug_print_database_enabled()

    monkeypatch.setenv(DANGEROUSLY_DEBUG_PRINT_DATABASE_ENV, "true")
    assert dangerously_debug_print_database_enabled()


def test_log_database_connection_debug_prints_when_enabled(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setenv("TANJUN_TEST_DB_HOST", "debug-host")
    monkeypatch.setenv("TANJUN_TEST_DB_PORT", "3306")
    monkeypatch.setenv("TANJUN_TEST_DB_USER", "u")
    monkeypatch.setenv("TANJUN_TEST_DB_PASSWORD", "p")
    monkeypatch.setenv("TANJUN_TEST_DB_NAME", "db")
    monkeypatch.setenv(DANGEROUSLY_DEBUG_PRINT_DATABASE_ENV, "1")

    log_database_connection_debug(context="unit test")

    captured = capsys.readouterr()
    assert "debug-host" in captured.err
    assert "TANJUN_TEST_DB_HOST" in captured.err
    assert "password=SET (length=1)" in captured.err
    assert "***" in captured.err


def test_format_database_connection_debug_masks_password() -> None:
    from utils.db_migration import DatabaseConnectionParams

    params = DatabaseConnectionParams(
        host="h",
        port=3306,
        user="u",
        password="secret",
        database="d",
        sources={
            "host": "database_ip",
            "port": "database_port",
            "user": "database_user",
            "password": "database_password",
            "database": "database_schema",
        },
    )
    text = format_database_connection_debug(params, context="ctx")
    assert "secret" not in text
    assert "***" in text


def test_get_database_url_raises_without_credentials(monkeypatch: pytest.MonkeyPatch) -> None:
    import builtins

    real_import = builtins.__import__

    def block_config_import(name, globals=None, locals=None, fromlist=(), level=0):
        if name == "config":
            raise ImportError("no config")
        return real_import(name, globals, locals, fromlist, level)

    monkeypatch.setattr("utils.db_migration._first_env", lambda *args, **kwargs: kwargs.get("default"))
    with (
        patch.object(builtins, "__import__", side_effect=block_config_import),
        pytest.raises(RuntimeError, match="Database credentials missing"),
    ):
        get_database_url()
