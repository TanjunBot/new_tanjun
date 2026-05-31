"""Tests for table_def_models and get_table_definitions()."""

from __future__ import annotations

import re

import pytest

import tests.mock_config as mock_config

mock_config.patch_config_module()

from api import get_table_definitions, get_table_defs  # noqa: E402

pytestmark = pytest.mark.unit

_CREATE_TABLE_RE = re.compile(
    r"CREATE TABLE IF NOT EXISTS `\w+`\s*\(.+\)\s*ENGINE=\w+",
    re.DOTALL | re.IGNORECASE,
)


class TestTableDefinitions:
    def test_every_table_produces_valid_sql(self):
        tables = get_table_definitions()
        assert len(tables) > 0
        for name, sql in tables.items():
            assert sql.strip(), f"empty SQL for {name}"
            assert _CREATE_TABLE_RE.search(sql), f"invalid DDL for {name}"

    def test_create_table_if_not_exists_in_output(self):
        for name, sql in get_table_definitions().items():
            assert "CREATE TABLE IF NOT EXISTS" in sql, f"missing IF NOT EXISTS for {name}"

    def test_table_def_models_to_sql(self):
        defs = get_table_defs()
        assert len(defs) > 0
        for name, tdef in defs.items():
            sql = tdef.to_sql()
            assert tdef.name == name
            assert "CREATE TABLE IF NOT EXISTS" in sql
            assert f"`{name}`" in sql
            assert "ENGINE=" in sql

    def test_table_def_column_rendering(self):
        from table_def_models.table_def import col

        column = col("user_id", "VARCHAR(20)", pk=True, nullable=False)
        assert "`user_id`" in column.to_sql()
        assert "VARCHAR(20)" in column.to_sql()
        assert "PRIMARY KEY" in column.to_sql()
