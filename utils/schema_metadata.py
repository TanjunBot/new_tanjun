from __future__ import annotations

import re

from typing import Any, cast

from sqlalchemy import Column, MetaData, Table
from sqlalchemy.types import (
    BIGINT,
    DECIMAL,
    INTEGER,
    JSON,
    SMALLINT,
    TEXT,
    TIMESTAMP,
    TypeEngine,
    VARCHAR,
)

from table_def_models.table_def import ColumnDef

_TYPE_MAP: list[tuple[re.Pattern[str], object]] = [
    (re.compile(r"^BIGINT", re.I), BIGINT),
    (re.compile(r"^INT UNSIGNED", re.I), INTEGER),
    (re.compile(r"^INT", re.I), INTEGER),
    (re.compile(r"^MEDIUMINT UNSIGNED", re.I), INTEGER),
    (re.compile(r"^SMALLINT UNSIGNED", re.I), SMALLINT),
    (re.compile(r"^TINYINT", re.I), SMALLINT),
    (re.compile(r"^DECIMAL", re.I), DECIMAL),
    (re.compile(r"^VARCHAR\((\d+)\)", re.I), None),
    (re.compile(r"^TEXT", re.I), TEXT),
    (re.compile(r"^JSON", re.I), JSON),
    (re.compile(r"^TIMESTAMP", re.I), TIMESTAMP),
    (re.compile(r"^DATETIME", re.I), TIMESTAMP),
    (re.compile(r"^ENUM", re.I), VARCHAR(255)),
]


def sql_type_to_sa(column: ColumnDef) -> TypeEngine[Any]:
    sql_type = column.sql_type.strip()
    for pattern, sa_type in _TYPE_MAP:
        match = pattern.match(sql_type)
        if not match:
            continue
        if sa_type is None:
            length = int(match.group(1))
            return VARCHAR(length)
        if isinstance(sa_type, type):
            return cast(TypeEngine[Any], sa_type())
        return cast(TypeEngine[Any], sa_type)
    return VARCHAR(255)


def build_metadata() -> MetaData:
    from api import get_table_defs

    metadata = MetaData()
    for table_def in get_table_defs().values():
        cols = [
            Column(col_def.name, sql_type_to_sa(col_def), primary_key=col_def.primary_key)
            for col_def in table_def.columns
        ]
        Table(table_def.name, metadata, *cols)
    return metadata


def expected_columns_by_table() -> dict[str, list[str]]:
    from api import get_table_defs

    return {name: [c.name for c in tdef.columns] for name, tdef in get_table_defs().items()}
