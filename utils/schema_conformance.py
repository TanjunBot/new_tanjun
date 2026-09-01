from __future__ import annotations

import re
from dataclasses import dataclass

from sqlalchemy import text
from sqlalchemy.engine import Connection

from table_def_models.table_def import ColumnDef, TableDef
from utils.schema_metadata import expected_columns_by_table


@dataclass(frozen=True)
class ColumnSpec:
    sql_type: str
    nullable: bool


def _effective_nullable(tdef: TableDef, col: ColumnDef) -> bool:
    if not col.nullable:
        return False
    if col.auto_increment or col.primary_key:
        return False
    if col.name in tdef._get_pk_col_names():
        return False
    return True


def expected_column_specs_by_table() -> dict[str, dict[str, ColumnSpec]]:
    from api import get_table_defs

    specs: dict[str, dict[str, ColumnSpec]] = {}
    for name, tdef in get_table_defs().items():
        specs[name] = {
            col.name: ColumnSpec(
                sql_type=_normalize_mysql_type(col.sql_type),
                nullable=_effective_nullable(tdef, col),
            )
            for col in tdef.columns
        }
    return specs


def _column_types_match(expected: str, actual: str) -> bool:
    if expected == actual:
        return True
    return expected == "json" and actual == "longtext"


def _normalize_mysql_type(column_type: str) -> str:
    normalized = column_type.strip().lower()
    normalized = re.sub(r"\s+", "", normalized)
    if normalized.startswith("tinyint"):
        return "tinyint"
    if normalized.startswith("smallint"):
        return "smallint"
    if normalized.startswith("mediumint"):
        return "mediumint"
    if normalized.startswith("bigint"):
        return "bigint"
    if normalized.startswith("int"):
        return "int"
    if normalized.startswith("varchar"):
        match = re.match(r"varchar\((\d+)\)", normalized)
        return f"varchar({match.group(1)})" if match else "varchar"
    if normalized.startswith("decimal"):
        match = re.match(r"decimal\((\d+),(\d+)\)", normalized)
        if match:
            return f"decimal({match.group(1)},{match.group(2)})"
        return "decimal"
    return normalized.split("(")[0]


def fetch_existing_columns_sync(connection: Connection) -> dict[str, set[str]]:
    rows = connection.execute(
        text(
            "SELECT table_name, column_name FROM information_schema.columns "
            "WHERE table_schema = DATABASE()"
        )
    ).fetchall()
    result: dict[str, set[str]] = {}
    for table_name, column_name in rows:
        result.setdefault(table_name, set()).add(column_name)
    return result


def fetch_existing_column_specs_sync(connection: Connection) -> dict[str, dict[str, ColumnSpec]]:
    rows = connection.execute(
        text(
            "SELECT table_name, column_name, column_type, is_nullable "
            "FROM information_schema.columns WHERE table_schema = DATABASE()"
        )
    ).fetchall()
    result: dict[str, dict[str, ColumnSpec]] = {}
    for table_name, column_name, column_type, is_nullable in rows:
        result.setdefault(table_name, {})[column_name] = ColumnSpec(
            sql_type=_normalize_mysql_type(column_type),
            nullable=is_nullable == "YES",
        )
    return result


def schema_has_drift(connection: Connection) -> list[str]:
    return find_schema_drift(fetch_existing_column_specs_sync(connection))


async def fetch_existing_columns(
    pool: object,
    *,
    schema_name: str | None = None,
) -> dict[str, set[str]]:
    db = schema_name
    if db is None:
        async with pool.acquire() as conn, conn.cursor() as cursor:
            await cursor.execute("SELECT DATABASE()")
            row = await cursor.fetchone()
            db = row[0] if row else None
    if not db:
        raise RuntimeError("Could not resolve database schema name")

    async with pool.acquire() as conn, conn.cursor() as cursor:
        await cursor.execute(
            "SELECT table_name, column_name FROM information_schema.columns "
            "WHERE table_schema = %s",
            (db,),
        )
        rows = await cursor.fetchall()

    result: dict[str, set[str]] = {}
    for table_name, column_name in rows:
        result.setdefault(table_name, set()).add(column_name)
    return result


def _compare_table_specs(
    table_name: str,
    expected: dict[str, ColumnSpec],
    actual: dict[str, ColumnSpec] | None,
) -> list[str]:
    errors: list[str] = []
    if actual is None:
        errors.append(f"table `{table_name}` is missing")
        return errors

    missing = [col for col in expected if col not in actual]
    if missing:
        errors.append(f"table `{table_name}` missing columns: {', '.join(missing)}")
        return errors

    for col_name, exp in expected.items():
        act = actual.get(col_name)
        if act is None:
            continue
        exp_type = _normalize_mysql_type(exp.sql_type)
        if not _column_types_match(exp_type, act.sql_type):
            errors.append(
                f"table `{table_name}` column `{col_name}` type mismatch: "
                f"expected {exp_type}, got {act.sql_type}"
            )
        if act.nullable != exp.nullable:
            errors.append(
                f"table `{table_name}` column `{col_name}` nullability mismatch: "
                f"expected {'NULL' if exp.nullable else 'NOT NULL'}, "
                f"got {'NULL' if act.nullable else 'NOT NULL'}"
            )
    return errors


def find_schema_drift(existing: dict[str, dict[str, ColumnSpec]]) -> list[str]:
    expected = expected_column_specs_by_table()
    errors: list[str] = []
    for table_name in sorted(expected):
        errors.extend(_compare_table_specs(table_name, expected[table_name], existing.get(table_name)))
    return errors


def load_schema_drift_errors() -> list[str]:
    from sqlalchemy import create_engine

    from utils.db_migration import get_database_url

    engine = create_engine(get_database_url(), pool_pre_ping=True)
    with engine.connect() as connection:
        return find_schema_drift(fetch_existing_column_specs_sync(connection))


async def assert_schema_conformance(pool: object, *, schema_name: str | None = None) -> None:
    del pool, schema_name
    errors = load_schema_drift_errors()
    if errors:
        raise AssertionError("Schema conformance failed:\n" + "\n".join(errors))
