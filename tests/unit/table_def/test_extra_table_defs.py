"""Tests for converted TableDef tables (formerly raw SQL)."""

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


def test_all_tables_use_table_def_only() -> None:
    defs = get_table_defs()
    tables = get_table_definitions()
    assert set(defs) == set(tables)
    assert len(defs) >= 60


def test_converted_tables_produce_valid_sql() -> None:
    for name in (
        "giveaway",
        "log_enables",
        "triggerMessages",
        "dynamicslowmode",
        "scheduledMessages",
        "reports",
    ):
        sql = get_table_definitions()[name]
        assert _CREATE_TABLE_RE.search(sql), f"invalid DDL for {name}"
