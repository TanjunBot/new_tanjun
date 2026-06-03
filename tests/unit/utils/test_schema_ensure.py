from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest

import tests.mock_config as mock_config

mock_config.patch_config_module()

from table_def_models.table_def import ColumnDef, TableDef  # noqa: E402
from utils.schema_ensure import (  # noqa: E402
    column_exists,
    ensure_columns_from_table_def,
    ensure_table_from_ddl,
    is_benign_migration_error,
    table_exists,
)

pytestmark = pytest.mark.unit


@pytest.mark.asyncio
async def test_table_exists_and_column_exists() -> None:
    with patch("api.execute_query", new=AsyncMock(return_value=[(1,)])):
        assert await table_exists("warnings") is True
        assert await column_exists("warnings", "id") is True


@pytest.mark.asyncio
async def test_ensure_table_from_ddl_warns_when_execute_returns_none(caplog) -> None:
    with patch("api.execute_action", new=AsyncMock(return_value=None)):
        await ensure_table_from_ddl("CREATE TABLE x (id INT)")
    assert "execute_action returned None" in caplog.text


@pytest.mark.asyncio
async def test_ensure_columns_adds_missing_column() -> None:
    table_def = TableDef(
        name="mediaChannel",
        columns=[
            ColumnDef(name="channel_id", sql_type="VARCHAR(20)", primary_key=True),
            ColumnDef(name="guild_id", sql_type="VARCHAR(20)"),
        ],
    )
    with (
        patch("utils.schema_ensure.table_exists", new=AsyncMock(return_value=True)),
        patch("utils.schema_ensure.column_exists", new=AsyncMock(side_effect=[True, False])),
        patch("api.execute_action", new=AsyncMock()) as action,
    ):
        await ensure_columns_from_table_def(table_def)
    assert "ADD COLUMN" in action.await_args.args[0]


def test_is_benign_migration_error() -> None:
    assert is_benign_migration_error(Exception("Duplicate column name 'x'")) is True
    assert is_benign_migration_error(Exception("syntax error")) is False
