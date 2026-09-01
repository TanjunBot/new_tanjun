"""Legacy repairs: guild-scoped FK parents and welcome/leave keys."""

from __future__ import annotations

from collections.abc import Sequence

from alembic import op
from sqlalchemy import text
from sqlalchemy.engine import Connection

revision: str = "004_schema_fk_and_guild_keys"
down_revision: str | None = "003_giveaway_legacy_column"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

_BENIGN = (
    "duplicate column",
    "duplicate key name",
    "multiple primary key",
    "already exists",
    "can't drop",
    "doesn't exist",
    "does not exist",
    "check that column/key exists",
)


def _execute_idempotent(sql: str) -> None:
    conn = op.get_bind()
    try:
        conn.execute(text(sql))
    except Exception as exc:
        if any(fragment in str(exc).lower() for fragment in _BENIGN):
            return
        raise


def _primary_key_columns(conn: Connection, table: str) -> list[str]:
    rows = conn.execute(
        text(
            "SELECT column_name FROM information_schema.statistics "
            "WHERE table_schema = DATABASE() AND table_name = :table AND index_name = 'PRIMARY' "
            "ORDER BY seq_in_index"
        ),
        {"table": table},
    ).fetchall()
    return [row[0] for row in rows]


def _has_column(conn: Connection, table: str, column: str) -> bool:
    row = conn.execute(
        text(
            "SELECT COUNT(*) FROM information_schema.columns "
            "WHERE table_schema = DATABASE() AND table_name = :table AND column_name = :column"
        ),
        {"table": table, "column": column},
    ).fetchone()
    return bool(row and row[0])


def _has_unique_guild_id(conn: Connection, table: str) -> bool:
    row = conn.execute(
        text(
            "SELECT COUNT(*) FROM information_schema.statistics "
            "WHERE table_schema = DATABASE() AND table_name = :table AND index_name = 'uk_guild_id' "
            "AND non_unique = 0"
        ),
        {"table": table},
    ).fetchone()
    return bool(row and row[0])


def _dedupe_guild_config_table(table: str) -> None:
    conn = op.get_bind()
    exists = conn.execute(
        text(
            "SELECT COUNT(*) FROM information_schema.tables "
            "WHERE table_schema = DATABASE() AND table_name = :table"
        ),
        {"table": table},
    ).fetchone()
    if not exists or not exists[0]:
        return

    _execute_idempotent(
        f"DELETE t1 FROM `{table}` t1 "
        f"INNER JOIN `{table}` t2 ON t1.guild_id = t2.guild_id AND t1.channel_id > t2.channel_id"
    )

    pk_cols = _primary_key_columns(conn, table)
    if pk_cols == ["guild_id"]:
        return

    _execute_idempotent(f"ALTER TABLE `{table}` DROP PRIMARY KEY")
    _execute_idempotent(f"ALTER TABLE `{table}` ADD PRIMARY KEY (`guild_id`)")


def _normalize_guild_id_column(conn: Connection, table: str) -> None:
    if _has_column(conn, table, "guild_id"):
        return
    if _has_column(conn, table, "guildId"):
        _execute_idempotent(
            f"ALTER TABLE `{table}` CHANGE COLUMN `guildId` `guild_id` VARCHAR(20) DEFAULT NULL"
        )


def _ensure_guild_id_column(
    conn: Connection, table: str, child_table: str | None, child_fk_column: str | None
) -> None:
    _normalize_guild_id_column(conn, table)
    if not _has_column(conn, table, "guild_id"):
        _execute_idempotent(f"ALTER TABLE `{table}` ADD COLUMN `guild_id` VARCHAR(20) DEFAULT NULL")

    if child_table and child_fk_column:
        _normalize_guild_id_column(conn, child_table)
        conn.execute(
            text(
                f"UPDATE `{table}` parent "
                f"INNER JOIN ("
                f"  SELECT `{child_fk_column}` AS parent_id, MIN(`guild_id`) AS guild_id "
                f"  FROM `{child_table}` WHERE `guild_id` IS NOT NULL "
                f"  GROUP BY `{child_fk_column}`"
                f") child ON parent.`id` = child.parent_id "
                f"SET parent.`guild_id` = child.guild_id "
                f"WHERE parent.`guild_id` IS NULL"
            )
        )

    conn.execute(text(f"DELETE FROM `{table}` WHERE `guild_id` IS NULL"))


def _drop_foreign_keys_to(conn: Connection, child_table: str, parent_table: str) -> None:
    rows = conn.execute(
        text(
            "SELECT DISTINCT constraint_name FROM information_schema.key_column_usage "
            "WHERE table_schema = DATABASE() AND table_name = :child "
            "AND referenced_table_name = :parent"
        ),
        {"child": child_table, "parent": parent_table},
    ).fetchall()
    for (constraint_name,) in rows:
        _execute_idempotent(f"ALTER TABLE `{child_table}` DROP FOREIGN KEY `{constraint_name}`")


def _repair_guild_scoped_parent(table: str, child_table: str, fk_columns: tuple[str, str]) -> None:
    conn = op.get_bind()
    exists = conn.execute(
        text(
            "SELECT COUNT(*) FROM information_schema.tables "
            "WHERE table_schema = DATABASE() AND table_name = :table"
        ),
        {"table": table},
    ).fetchone()
    if not exists or not exists[0]:
        return

    pk_cols = _primary_key_columns(conn, table)
    if pk_cols == ["id"] and _has_unique_guild_id(conn, table):
        return

    child_exists = conn.execute(
        text(
            "SELECT COUNT(*) FROM information_schema.tables "
            "WHERE table_schema = DATABASE() AND table_name = :table"
        ),
        {"table": child_table},
    ).fetchone()
    if child_exists and child_exists[0]:
        _drop_foreign_keys_to(conn, child_table, table)

    child_fk_column = fk_columns[1] if child_exists and child_exists[0] else None
    _ensure_guild_id_column(conn, table, child_table if child_exists and child_exists[0] else None, child_fk_column)

    _execute_idempotent(f"ALTER TABLE `{table}` MODIFY COLUMN `guild_id` VARCHAR(20) NOT NULL")
    if pk_cols == ["guild_id", "id"]:
        _execute_idempotent(f"ALTER TABLE `{table}` DROP PRIMARY KEY")
        _execute_idempotent(f"ALTER TABLE `{table}` ADD PRIMARY KEY (`id`)")
    elif pk_cols != ["id"]:
        _execute_idempotent(f"ALTER TABLE `{table}` DROP PRIMARY KEY")
        _execute_idempotent(f"ALTER TABLE `{table}` ADD PRIMARY KEY (`id`)")

    _execute_idempotent(
        f"ALTER TABLE `{table}` ADD UNIQUE KEY `uk_guild_id` (`guild_id`, `id`)"
    )

    if child_exists and child_exists[0]:
        _execute_idempotent(
            f"ALTER TABLE `{child_table}` ADD CONSTRAINT `{child_table}_parent_fk` "
            f"FOREIGN KEY (`{fk_columns[0]}`, `{fk_columns[1]}`) "
            f"REFERENCES `{table}` (`guild_id`, `id`) ON DELETE CASCADE ON UPDATE CASCADE"
        )


def upgrade() -> None:
    _dedupe_guild_config_table("welcome_channel")
    _dedupe_guild_config_table("leave_channel")
    _repair_guild_scoped_parent("triggerMessages", "triggerMessagesChannel", ("guild_id", "triggerId"))
    _repair_guild_scoped_parent("ticketMessages", "tickets", ("guild_id", "ticketMessageId"))


def downgrade() -> None:
    pass
