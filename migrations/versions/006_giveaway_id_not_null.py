"""Ensure giveaway.giveaway_id is NOT NULL AUTO_INCREMENT after legacy renames."""

from __future__ import annotations

from collections.abc import Sequence

from alembic import op
from sqlalchemy import text
from sqlalchemy.engine import Connection

revision: str = "006_giveaway_id_not_null"
down_revision: str | None = "005_legacy_camelcase_columns"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

_BENIGN = (
    "duplicate column",
    "multiple primary key",
    "already exists",
    "doesn't exist",
    "does not exist",
    "check that column/key exists",
    "can't drop",
)


def _execute_idempotent(sql: str) -> None:
    conn = op.get_bind()
    try:
        conn.execute(text(sql))
    except Exception as exc:
        if any(fragment in str(exc).lower() for fragment in _BENIGN):
            return
        raise


def _table_exists(conn: Connection, table: str) -> bool:
    row = conn.execute(
        text(
            "SELECT COUNT(*) FROM information_schema.tables "
            "WHERE table_schema = DATABASE() AND table_name = :table"
        ),
        {"table": table},
    ).fetchone()
    return bool(row and row[0])


def _has_column(conn: Connection, table: str, column: str) -> bool:
    row = conn.execute(
        text(
            "SELECT COUNT(*) FROM information_schema.columns "
            "WHERE table_schema = DATABASE() AND table_name = :table AND column_name = :column"
        ),
        {"table": table, "column": column},
    ).fetchone()
    return bool(row and row[0])


def _column_nullable(conn: Connection, table: str, column: str) -> bool | None:
    row = conn.execute(
        text(
            "SELECT is_nullable FROM information_schema.columns "
            "WHERE table_schema = DATABASE() AND table_name = :table AND column_name = :column"
        ),
        {"table": table, "column": column},
    ).fetchone()
    if not row:
        return None
    return bool(row[0] == "YES")


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


def _auto_increment_columns(conn: Connection, table: str) -> list[str]:
    rows = conn.execute(
        text(
            "SELECT column_name FROM information_schema.columns "
            "WHERE table_schema = DATABASE() AND table_name = :table "
            "AND extra LIKE '%auto_increment%'"
        ),
        {"table": table},
    ).fetchall()
    return [row[0] for row in rows]


def _strip_auto_increment(conn: Connection, table: str, column: str) -> None:
    row = conn.execute(
        text(
            "SELECT column_type, is_nullable FROM information_schema.columns "
            "WHERE table_schema = DATABASE() AND table_name = :table AND column_name = :column"
        ),
        {"table": table, "column": column},
    ).fetchone()
    if not row:
        return
    nullable = "NULL" if row[1] == "YES" else "NOT NULL"
    _execute_idempotent(f"ALTER TABLE `{table}` MODIFY COLUMN `{column}` {row[0]} {nullable}")


def _assign_remaining_giveaway_ids(conn: Connection) -> None:
    row = conn.execute(text("SELECT COALESCE(MAX(`giveaway_id`), 0) FROM `giveaway`")).fetchone()
    start = int(row[0]) if row else 0
    conn.execute(text(f"SET @giveaway_row := {start}"))
    conn.execute(
        text(
            "UPDATE `giveaway` SET `giveaway_id` = (@giveaway_row := @giveaway_row + 1) "
            "WHERE `giveaway_id` IS NULL ORDER BY `guild_id`, `endtime`"
        )
    )


def upgrade() -> None:
    conn = op.get_bind()
    if not _table_exists(conn, "giveaway") or not _has_column(conn, "giveaway", "giveaway_id"):
        return

    if _has_column(conn, "giveaway", "giveawayId"):
        conn.execute(
            text(
                "UPDATE `giveaway` SET `giveaway_id` = `giveawayId` "
                "WHERE `giveaway_id` IS NULL AND `giveawayId` IS NOT NULL"
            )
        )
        _execute_idempotent("ALTER TABLE `giveaway` DROP COLUMN `giveawayId`")

    for legacy in ("id", "giveawayId"):
        if legacy != "giveaway_id" and _has_column(conn, "giveaway", legacy):
            pk_cols = _primary_key_columns(conn, "giveaway")
            if pk_cols == [legacy]:
                _execute_idempotent("ALTER TABLE `giveaway` DROP PRIMARY KEY")
            elif legacy in pk_cols:
                _execute_idempotent("ALTER TABLE `giveaway` DROP PRIMARY KEY")
            conn.execute(
                text(f"UPDATE `giveaway` SET `giveaway_id` = `{legacy}` WHERE `giveaway_id` IS NULL")
            )
            _execute_idempotent(f"ALTER TABLE `giveaway` DROP COLUMN `{legacy}`")

    _assign_remaining_giveaway_ids(conn)

    for column in _auto_increment_columns(conn, "giveaway"):
        if column != "giveaway_id":
            _strip_auto_increment(conn, "giveaway", column)

    pk_cols = _primary_key_columns(conn, "giveaway")
    needs_pk = pk_cols != ["giveaway_id"]
    needs_not_null = _column_nullable(conn, "giveaway", "giveaway_id") is not False
    if needs_pk:
        _execute_idempotent("ALTER TABLE `giveaway` DROP PRIMARY KEY")
    if needs_pk or needs_not_null:
        _execute_idempotent(
            "ALTER TABLE `giveaway` MODIFY COLUMN `giveaway_id` INT UNSIGNED NOT NULL "
            "AUTO_INCREMENT PRIMARY KEY"
        )


def downgrade() -> None:
    pass
