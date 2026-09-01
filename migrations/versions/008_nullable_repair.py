"""Repair welcome/leave channel_id nullability when 007 was stamped without applying."""

from __future__ import annotations

from collections.abc import Sequence

from alembic import op
from sqlalchemy import text
from sqlalchemy.engine import Connection

revision: str = "008_nullable_repair"
down_revision: str | None = "007_channel_id_nullable"
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


def upgrade() -> None:
    conn = op.get_bind()
    for table in ("welcome_channel", "leave_channel"):
        if _table_exists(conn, table) and _has_column(conn, table, "channel_id"):
            _execute_idempotent(
                f"ALTER TABLE `{table}` MODIFY COLUMN `channel_id` VARCHAR(20) NULL"
            )


def downgrade() -> None:
    pass
