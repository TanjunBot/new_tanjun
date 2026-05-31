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


_CREATE_TABLE_DEPENDENCIES = {
    "triggerMessagesChannel": ["triggerMessages"],
    "tickets": ["ticketMessages"],
    "dynamicslowmode_messages": ["dynamicslowmode"],
    "report_evidence": ["reports"],
    "report_mod_actions": ["reports"],
}

_FK_REF_RE = re.compile(r"REFERENCES\s+`(\w+)`", re.IGNORECASE)


def _dependency_batches(dependencies: dict[str, list[str]], table_names: set[str]) -> list[set[str]]:
    to_create = set(table_names)
    created: set[str] = set()
    batches: list[set[str]] = []
    while to_create:
        batch = {
            name
            for name in to_create
            if all(dep in created or dep not in to_create for dep in dependencies.get(name, []))
        }
        if not batch:
            raise RuntimeError(f"Cannot resolve table dependencies for: {to_create}")
        batches.append(batch)
        to_create -= batch
        created.update(batch)
    return batches


class TestCreateTablesDependencyOrder:
    def test_create_tables_dependencies_acyclic(self):
        table_names = set(get_table_definitions())
        batches = _dependency_batches(_CREATE_TABLE_DEPENDENCIES, table_names)
        assert batches
        ordered = [name for batch in batches for name in sorted(batch)]
        assert len(ordered) == len(set(ordered))

    def test_foreign_keys_reference_known_tables(self):
        tables = get_table_definitions()
        known = set(tables)
        for name, sql in tables.items():
            for ref in _FK_REF_RE.findall(sql):
                assert ref in known, f"{name} references unknown table {ref}"

    def test_batch_order_respects_dependencies(self):
        table_names = set(get_table_definitions())
        batches = _dependency_batches(_CREATE_TABLE_DEPENDENCIES, table_names)
        created: set[str] = set()
        for batch in batches:
            for name in batch:
                for dep in _CREATE_TABLE_DEPENDENCIES.get(name, []):
                    if dep in table_names:
                        assert dep in created, f"{name} scheduled before dependency {dep}"
            created.update(batch)
