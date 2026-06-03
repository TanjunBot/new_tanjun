from __future__ import annotations

import logging
import re
from typing import Any

from table_def_models.table_def import ColumnDef, TableDef

_ALTER_TABLE_RE = re.compile(r"ALTER\s+TABLE\s+`([^`]+)`", re.IGNORECASE)
_BENIGN_MIGRATION_FRAGMENTS = (
    "column already exists",
    "duplicate column",
    "duplicate column name",
    "duplicate key name",
    "doesn't exist",
    "does not exist",
)


def extract_table_name_from_alter(sql: str) -> str | None:
    match = _ALTER_TABLE_RE.search(sql)
    return match.group(1) if match else None


def is_benign_migration_error(exc: BaseException) -> bool:
    exc_str = str(exc).lower()
    return any(fragment in exc_str for fragment in _BENIGN_MIGRATION_FRAGMENTS)


async def table_exists(table_name: str, bot: Any = None) -> bool:
    from api import execute_query

    rows = await execute_query(
        "SELECT 1 FROM information_schema.tables "
        "WHERE table_schema = DATABASE() AND table_name = %s LIMIT 1",
        (table_name,),
        bot,
    )
    return bool(rows)


async def column_exists(table_name: str, column_name: str, bot: Any = None) -> bool:
    from api import execute_query

    rows = await execute_query(
        "SELECT 1 FROM information_schema.columns "
        "WHERE table_schema = DATABASE() AND table_name = %s AND column_name = %s LIMIT 1",
        (table_name, column_name),
        bot,
    )
    return bool(rows)


async def ensure_table_from_ddl(ddl: str, bot: Any = None) -> None:
    from api import execute_action

    result = await execute_action(ddl, bot=bot)
    if result is None:
        logging.warning("ensure_table_from_ddl: execute_action returned None")


def _column_add_sql(table_name: str, column: ColumnDef) -> str:
    parts = [f"ALTER TABLE `{table_name}` ADD COLUMN `{column.name}` {column.sql_type}"]
    if column.default is not None:
        parts.append(f"DEFAULT {column.default}")
    elif not column.nullable and not column.primary_key:
        parts.append("NOT NULL")
    return " ".join(parts)


async def ensure_columns_from_table_def(table_def: TableDef, bot: Any = None) -> None:
    from api import execute_action

    if not await table_exists(table_def.name, bot):
        await ensure_table_from_ddl(table_def.to_sql(), bot)
        return

    for column in table_def.columns:
        if await column_exists(table_def.name, column.name, bot):
            continue
        try:
            await execute_action(_column_add_sql(table_def.name, column), bot=bot)
        except Exception as exc:
            if not is_benign_migration_error(exc):
                raise


async def ensure_table_schema(table_name: str, bot: Any = None) -> None:
    from api import get_table_defs, get_table_definitions

    defs = get_table_defs()
    if table_name in defs:
        await ensure_columns_from_table_def(defs[table_name], bot)
        return

    ddl_map = get_table_definitions()
    if table_name in ddl_map:
        if not await table_exists(table_name, bot):
            await ensure_table_from_ddl(ddl_map[table_name], bot)


async def run_alter_migration(sql: str, *, table_name: str | None = None, bot: Any = None) -> bool:
    from api import execute_action

    resolved_table = table_name or extract_table_name_from_alter(sql)
    if resolved_table and not await table_exists(resolved_table, bot):
        from api import get_table_definitions

        ddl_map = get_table_definitions()
        if resolved_table in ddl_map:
            await ensure_table_from_ddl(ddl_map[resolved_table], bot)
        if not await table_exists(resolved_table, bot):
            logging.warning("Skipping migration for missing table %s", resolved_table)
            return False

    try:
        result = await execute_action(sql, bot=bot)
        if result is None:
            logging.warning("Migration returned None (pool unavailable): %s", sql[:80])
            return False
        return True
    except Exception as exc:
        if is_benign_migration_error(exc):
            logging.debug("Migration skipped (already applied or benign): %s", sql[:80])
            return True
        logging.exception("Unexpected migration error: %s", sql[:80])
        raise


async def migrate_reports_status_columns(bot: Any = None) -> None:
    if not await table_exists("reports", bot):
        from api import get_table_definitions

        ddl_map = get_table_definitions()
        if "reports" not in ddl_map:
            logging.warning("reports table missing and no DDL available")
            return
        await ensure_table_from_ddl(ddl_map["reports"], bot)
        if not await table_exists("reports", bot):
            logging.warning("reports table still missing after CREATE")
            return

    if not await column_exists("reports", "created_at", bot):
        await run_alter_migration(
            "ALTER TABLE `reports` ADD COLUMN `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
            table_name="reports",
            bot=bot,
        )

    status_migrations = [
        (
            "status",
            "ALTER TABLE `reports` ADD COLUMN `status` VARCHAR(20) DEFAULT 'PENDING' AFTER `created_at`",
        ),
        (
            "status_updated_at",
            "ALTER TABLE `reports` ADD COLUMN `status_updated_at` TIMESTAMP DEFAULT NULL AFTER `status`",
        ),
        (
            "status_updated_by",
            "ALTER TABLE `reports` ADD COLUMN `status_updated_by` VARCHAR(20) DEFAULT NULL "
            "AFTER `status_updated_at`",
        ),
        (
            "idx_status",
            "ALTER TABLE `reports` ADD INDEX `idx_status` (`status`)",
        ),
    ]
    for column_name, sql in status_migrations:
        if column_name.startswith("idx_"):
            await run_alter_migration(sql, table_name="reports", bot=bot)
        elif not await column_exists("reports", column_name, bot):
            await run_alter_migration(sql, table_name="reports", bot=bot)


async def run_startup_migrations(bot: Any = None) -> None:
    """Deprecated: schema changes are applied via Alembic (utils.db_migration)."""
    del bot
