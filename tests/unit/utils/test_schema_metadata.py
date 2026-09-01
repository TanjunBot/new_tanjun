from __future__ import annotations

import pytest

import tests.mock_config as mock_config

mock_config.patch_config_module()

from table_def_models.table_def import ColumnDef  # noqa: E402
from utils.schema_metadata import (  # noqa: E402
    build_metadata,
    expected_columns_by_table,
    sql_type_to_sa,
)

pytestmark = pytest.mark.unit


def test_sql_type_to_sa_maps_common_types() -> None:
    assert sql_type_to_sa(ColumnDef(name="a", sql_type="BIGINT")).__class__.__name__ == "BIGINT"
    assert sql_type_to_sa(ColumnDef(name="b", sql_type="INT UNSIGNED")).__class__.__name__ == "INTEGER"
    assert sql_type_to_sa(ColumnDef(name="c", sql_type="VARCHAR(128)")).length == 128
    assert sql_type_to_sa(ColumnDef(name="d", sql_type="TEXT")).__class__.__name__ == "TEXT"
    assert sql_type_to_sa(ColumnDef(name="e", sql_type="ENUM('a')")).length == 255


def test_build_metadata_includes_known_table() -> None:
    metadata = build_metadata()
    assert "warnings" in metadata.tables


def test_expected_columns_by_table_matches_table_defs() -> None:
    from api import get_table_defs

    expected = expected_columns_by_table()
    for name, tdef in get_table_defs().items():
        assert expected[name] == [c.name for c in tdef.columns]
