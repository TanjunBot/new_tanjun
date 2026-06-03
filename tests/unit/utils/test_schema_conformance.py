"""Unit tests for schema drift detection."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

import tests.mock_config as mock_config

mock_config.patch_config_module()

from utils.schema_conformance import (  # noqa: E402
    ColumnSpec,
    _compare_table_specs,
    _normalize_mysql_type,
    assert_schema_conformance,
    fetch_existing_columns,
    fetch_existing_columns_sync,
    fetch_existing_column_specs_sync,
    find_schema_drift,
    load_schema_drift_errors,
    schema_has_drift,
)

pytestmark = pytest.mark.unit


def test_find_schema_drift_reports_missing_table() -> None:
    existing = {"warnings": {"id": ColumnSpec("int", True)}}
    errors = find_schema_drift(existing)
    assert any("table `level` is missing" in err for err in errors)


def test_find_schema_drift_reports_missing_columns() -> None:
    from api import get_table_defs

    table = "mediaChannel"
    specs = {
        col.name: ColumnSpec(col.sql_type.lower(), col.nullable) for col in get_table_defs()[table].columns
    }
    specs.pop("guild_id")
    errors = find_schema_drift({table: specs})
    assert any("mediaChannel" in err and "guild_id" in err for err in errors)


def test_find_schema_drift_reports_nullability_mismatch() -> None:
    from utils.schema_conformance import expected_column_specs_by_table

    table = "warnings"
    expected = expected_column_specs_by_table()[table]
    wrong = dict(expected)
    wrong["reason"] = ColumnSpec(expected["reason"].sql_type, not expected["reason"].nullable)
    errors = find_schema_drift({table: wrong})
    assert any("nullability mismatch" in err for err in errors)


def test_column_types_match_json_and_longtext() -> None:
    from utils.schema_conformance import _column_types_match

    assert _column_types_match("json", "longtext")
    assert not _column_types_match("json", "varchar(20)")


def test_compare_table_specs_skips_when_actual_column_missing_in_map() -> None:
    expected = {"id": ColumnSpec("int", False), "guild_id": ColumnSpec("varchar(20)", True)}
    actual = {"id": ColumnSpec("int", False)}
    errors = _compare_table_specs("warnings", expected, actual)
    assert any("missing columns" in err for err in errors)


def test_find_schema_drift_reports_type_mismatch() -> None:
    from utils.schema_conformance import expected_column_specs_by_table

    table = "warnings"
    expected = expected_column_specs_by_table()[table]
    wrong = {name: ColumnSpec("varchar(99)", spec.nullable) for name, spec in expected.items()}
    errors = find_schema_drift({table: wrong})
    assert any("type mismatch" in err for err in errors)


def test_find_schema_drift_empty_when_schema_complete() -> None:
    from utils.schema_conformance import expected_column_specs_by_table

    existing = expected_column_specs_by_table()
    assert find_schema_drift(existing) == []


def test_normalize_mysql_type_handles_bare_decimal_and_enum() -> None:
    assert _normalize_mysql_type("DECIMAL") == "decimal"
    assert _normalize_mysql_type("ENUM('a')") == "enum"


def test_fetch_existing_columns_sync_maps_rows() -> None:
    connection = MagicMock()
    connection.execute.return_value.fetchall.return_value = [
        ("warnings", "id"),
        ("warnings", "guild_id"),
    ]
    result = fetch_existing_columns_sync(connection)
    assert result == {"warnings": {"id", "guild_id"}}


def test_fetch_existing_column_specs_sync_maps_rows() -> None:
    connection = MagicMock()
    connection.execute.return_value.fetchall.return_value = [
        ("giveaway", "giveaway_id", "int unsigned", "NO"),
        ("giveaway", "guild_id", "varchar(20)", "YES"),
        ("warnings", "id", "int", "NO"),
    ]
    result = fetch_existing_column_specs_sync(connection)
    assert result["giveaway"]["giveaway_id"].sql_type == "int"
    assert result["warnings"]["id"].nullable is False


def test_schema_has_drift_delegates_to_find_schema_drift() -> None:
    connection = MagicMock()
    connection.execute.return_value.fetchall.return_value = []
    errors = schema_has_drift(connection)
    assert errors
    assert any("missing" in err for err in errors)


class _AsyncContext:
    def __init__(self, value: object) -> None:
        self._value = value

    async def __aenter__(self) -> object:
        return self._value

    async def __aexit__(self, *args: object) -> None:
        return None


def _pool_with_schema_rows(rows: list[tuple[str, str]], db_name: str = "tanjun_test") -> MagicMock:
    cursor = MagicMock()
    cursor.execute = AsyncMock()
    cursor.fetchone = AsyncMock(return_value=(db_name,))
    cursor.fetchall = AsyncMock(return_value=rows)
    conn = MagicMock()
    conn.cursor = MagicMock(return_value=_AsyncContext(cursor))
    pool = MagicMock()
    pool.acquire = MagicMock(return_value=_AsyncContext(conn))
    return pool


@pytest.mark.asyncio
async def test_fetch_existing_columns_reads_information_schema() -> None:
    pool = _pool_with_schema_rows([("warnings", "id")])

    result = await fetch_existing_columns(pool, schema_name="tanjun_test")

    assert result == {"warnings": {"id"}}


@pytest.mark.asyncio
async def test_fetch_existing_columns_resolves_database_from_pool() -> None:
    pool = _pool_with_schema_rows([("warnings", "id")])

    result = await fetch_existing_columns(pool)

    assert result == {"warnings": {"id"}}


@pytest.mark.asyncio
async def test_fetch_existing_columns_raises_when_database_unresolved() -> None:
    pool = _pool_with_schema_rows([], db_name="")

    with pytest.raises(RuntimeError, match="Could not resolve database"):
        await fetch_existing_columns(pool)


def test_compare_table_specs_continues_when_actual_column_is_none() -> None:
    errors = _compare_table_specs(
        "warnings",
        {"id": ColumnSpec("int", False)},
        {"id": None},  # type: ignore[arg-type]
    )
    assert errors == []


def test_load_schema_drift_errors_uses_sync_engine() -> None:
    connection = MagicMock()
    connection.execute.return_value.fetchall.return_value = []
    engine = MagicMock()
    engine.connect.return_value.__enter__.return_value = connection
    with patch("sqlalchemy.create_engine", return_value=engine), patch(
        "utils.db_migration.get_database_url",
        return_value="mysql+pymysql://u:p@localhost/db",
    ):
        errors = load_schema_drift_errors()
    assert errors


@pytest.mark.asyncio
async def test_assert_schema_conformance_raises_on_drift() -> None:
    with patch(
        "utils.schema_conformance.load_schema_drift_errors",
        return_value=["table `warnings` is missing"],
    ):
        with pytest.raises(AssertionError, match="Schema conformance failed"):
            await assert_schema_conformance(MagicMock())
