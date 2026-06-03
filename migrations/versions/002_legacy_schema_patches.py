"""Idempotent upgrades for long-lived databases created before current DDL."""

from __future__ import annotations

from collections.abc import Sequence

from alembic import op
from sqlalchemy import text

revision: str = "002_legacy_schema_patches"
down_revision: str | None = "001_initial_schema"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

_BENIGN = (
    "duplicate column",
    "duplicate key name",
    "already exists",
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


def upgrade() -> None:
    _execute_idempotent(
        "ALTER TABLE `scheduledMessages` ADD COLUMN `attachments` TEXT DEFAULT NULL AFTER `repeatAmount`"
    )
    _execute_idempotent(
        "ALTER TABLE `scheduledMessages` ADD COLUMN `discord_message_id` VARCHAR(20) DEFAULT NULL "
        "AFTER `attachments`"
    )
    _execute_idempotent(
        "ALTER TABLE `scheduledMessages` ADD INDEX `idx_discord_message` (`discord_message_id`)"
    )
    _execute_idempotent(
        "ALTER TABLE `reports` ADD COLUMN `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP"
    )
    _execute_idempotent(
        "ALTER TABLE `reports` ADD COLUMN `status` VARCHAR(20) DEFAULT 'pending' AFTER `created_at`"
    )
    _execute_idempotent(
        "ALTER TABLE `reports` ADD COLUMN `status_updated_at` TIMESTAMP DEFAULT NULL AFTER `status`"
    )
    _execute_idempotent(
        "ALTER TABLE `reports` ADD COLUMN `status_updated_by` VARCHAR(20) DEFAULT NULL "
        "AFTER `status_updated_at`"
    )
    _execute_idempotent(
        "ALTER TABLE `reports` ADD COLUMN `status_note` VARCHAR(1024) DEFAULT NULL AFTER `status_updated_by`"
    )
    _execute_idempotent(
        "ALTER TABLE `reports` ADD COLUMN `anonymous` TINYINT(1) DEFAULT 0 AFTER `status_note`"
    )
    _execute_idempotent("ALTER TABLE `reports` ADD INDEX `idx_status` (`status`)")
    _execute_idempotent("ALTER TABLE `reports` ADD INDEX `idx_guild` (`guild_id`)")
    _execute_idempotent(
        "ALTER TABLE `level` ADD INDEX `idx_level_guild_xp` (`guild_id`, `xp` DESC)"
    )
    _execute_idempotent(
        "ALTER TABLE `warnings` ADD INDEX `idx_warnings_user_guild` (`user_id`, `guild_id`)"
    )
    _execute_idempotent(
        "ALTER TABLE `giveaway` ADD INDEX `idx_giveaway_ended_endtime` (`ended`, `endtime`)"
    )


def downgrade() -> None:
    pass
