from __future__ import annotations

from sqlalchemy import text
from sqlalchemy.engine import Connection

from utils.schema_metadata import expected_columns_by_table


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


def schema_has_drift(connection: Connection) -> list[str]:
    return find_schema_drift(fetch_existing_columns_sync(connection))


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


def find_schema_drift(existing: dict[str, set[str]]) -> list[str]:
    expected = expected_columns_by_table()
    errors: list[str] = []
    for table_name, columns in sorted(expected.items()):
        actual = existing.get(table_name)
        if actual is None:
            errors.append(f"table `{table_name}` is missing")
            continue
        missing = [col for col in columns if col not in actual]
        if missing:
            errors.append(f"table `{table_name}` missing columns: {', '.join(missing)}")
    return errors


async def assert_schema_conformance(pool: object, *, schema_name: str | None = None) -> None:
    existing = await fetch_existing_columns(pool, schema_name=schema_name)
    errors = find_schema_drift(existing)
    if errors:
        raise AssertionError("Schema conformance failed:\n" + "\n".join(errors))
