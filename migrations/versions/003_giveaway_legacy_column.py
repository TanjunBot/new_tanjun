"""Add giveaway_id to legacy giveaway tables that predate the current schema."""

from __future__ import annotations

from collections.abc import Sequence

from alembic import op
from sqlalchemy import text

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
)


def _execute_idempotent(sql: str) -> None:
    conn = op.get_bind()
    try:
        conn.execute(text(sql))
    except Exception as exc:
        if any(fragment in str(exc).lower() for fragment in _BENIGN):
            return
        raise


def upgrade() -> None:
    conn = op.get_bind()
    result = conn.execute(
        text(
            "SELECT COUNT(*) FROM information_schema.columns "
            "WHERE table_schema = DATABASE() AND table_name = 'giveaway' AND column_name = 'giveaway_id'"
        )
    )
    row = result.fetchone()
    if row and row[0]:
        return

    exists = conn.execute(
        text(
            "SELECT COUNT(*) FROM information_schema.tables "
            "WHERE table_schema = DATABASE() AND table_name = 'giveaway'"
        )
    ).fetchone()
    if not exists or not exists[0]:
        return

    _execute_idempotent("ALTER TABLE `giveaway` DROP PRIMARY KEY")
    _execute_idempotent(
        "ALTER TABLE `giveaway` ADD COLUMN `giveaway_id` INT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY FIRST"
    )


def downgrade() -> None:
    pass
