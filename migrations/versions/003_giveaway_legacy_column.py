"""Add giveaway_id to legacy giveaway tables that predate the current schema."""

from __future__ import annotations

from collections.abc import Sequence

from alembic import op
from sqlalchemy import text
from sqlalchemy.engine import Connection

revision: str = "003_giveaway_legacy_column"
down_revision: str | None = "002_legacy_schema_patches"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

_BENIGN = (
    "duplicate column",
    "multiple primary key",
    "already exists",
    "can't drop",
    "doesn't exist",
    "does not exist",
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
    if _has_column(conn, "giveaway", "giveaway_id"):
        return
    if not _table_exists(conn, "giveaway"):
        return

    ai_cols = _auto_increment_columns(conn, "giveaway")
    pk_cols = _primary_key_columns(conn, "giveaway")

    if not ai_cols:
        if pk_cols:
            _execute_idempotent("ALTER TABLE `giveaway` DROP PRIMARY KEY")
        _execute_idempotent(
            "ALTER TABLE `giveaway` ADD COLUMN `giveaway_id` INT UNSIGNED NOT NULL "
            "AUTO_INCREMENT PRIMARY KEY FIRST"
        )
        return

    _execute_idempotent("ALTER TABLE `giveaway` ADD COLUMN `giveaway_id` INT UNSIGNED NULL FIRST")

    source = ai_cols[0]
    if source != "giveaway_id":
        conn.execute(text(f"UPDATE `giveaway` SET `giveaway_id` = `{source}` WHERE `giveaway_id` IS NULL"))

    _assign_remaining_giveaway_ids(conn)

    for column in ai_cols:
        if column != "giveaway_id":
            _strip_auto_increment(conn, "giveaway", column)

    if pk_cols:
        _execute_idempotent("ALTER TABLE `giveaway` DROP PRIMARY KEY")

    _execute_idempotent(
        "ALTER TABLE `giveaway` MODIFY COLUMN `giveaway_id` INT UNSIGNED NOT NULL "
        "AUTO_INCREMENT PRIMARY KEY"
    )

    if source == "id" and _has_column(conn, "giveaway", "id"):
        _execute_idempotent("ALTER TABLE `giveaway` DROP COLUMN `id`")


def downgrade() -> None:
    pass
