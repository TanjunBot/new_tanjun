"""Rename legacy camelCase columns to snake_case on long-lived production databases."""

from __future__ import annotations

from collections.abc import Sequence

from alembic import op
from sqlalchemy import text
from sqlalchemy.engine import Connection

revision: str = "005_legacy_camelcase_columns"
down_revision: str | None = "004_schema_fk_and_guild_keys"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

_BENIGN = (
    "duplicate column",
    "duplicate key name",
    "already exists",
    "doesn't exist",
    "does not exist",
    "check that column/key exists",
    "can't drop",
)

_LEGACY_RENAMES: dict[str, list[tuple[str, str]]] = {
    "afkMessages": [("userId", "user_id"), ("channelId", "channel_id")],
    "aiSituations": [("userId", "user_id"), ("createdAt", "created_at")],
    "aiToken": [("userId", "user_id")],
    "autopublish": [("channelId", "channel_id")],
    "blockedReporters": [("guildId", "guild_id"), ("userId", "user_id")],
    "boosterRole": [("guildId", "guild_id"), ("roleId", "role_id")],
    "brawlstarsLinkedAccounts": [("userId", "user_id")],
    "claimedBoosterChannel": [
        ("userId", "user_id"),
        ("channelId", "channel_id"),
        ("guildId", "guild_id"),
    ],
    "claimedBoosterRole": [
        ("userId", "user_id"),
        ("roleId", "role_id"),
        ("guildId", "guild_id"),
    ],
    "dynamicslowmode": [("guildId", "guild_id"), ("channelId", "channel_id")],
    "dynamicslowmode_messages": [("channelId", "channel_id"), ("sendTime", "send_time")],
    "feedbackBlocked": [("userId", "user_id")],
    "giveaway": [
        ("giveawayId", "giveaway_id"),
        ("guildId", "guild_id"),
        ("channelId", "channel_id"),
        ("createdAt", "created_at"),
    ],
    "giveawayBlacklistedRole": [("roleId", "role_id"), ("guildId", "guild_id")],
    "giveawayBlacklistedUser": [("userId", "user_id"), ("guildId", "guild_id")],
    "giveawayNewMessage": [("giveawayId", "giveaway_id"), ("userId", "user_id")],
    "giveawayParticipant": [("userId", "user_id"), ("giveawayId", "giveaway_id")],
    "giveawayRoleRequirement": [("roleId", "role_id"), ("giveawayId", "giveaway_id")],
    "giveawayVoiceTime": [("giveawayId", "giveaway_id"), ("userId", "user_id")],
    "levelConfig": [
        ("levelUpMessageActive", "level_up_messageActive"),
        ("levelUpMessage", "level_up_message"),
        ("levelUpChannelId", "level_up_channel_id"),
    ],
    "logBlacklistChannel": [("guildId", "guild_id"), ("channelId", "channel_id")],
    "logRoleBlacklist": [("guildId", "guild_id"), ("roleId", "role_id")],
    "logUserBlacklist": [("guildId", "guild_id"), ("userId", "user_id")],
    "mediaChannel": [("channelId", "channel_id"), ("guildId", "guild_id")],
    "reportchannel": [("guildId", "guild_id"), ("channelId", "channel_id")],
    "reports": [("guildId", "guild_id"), ("userId", "user_id")],
    "scheduledMessages": [
        ("guildId", "guild_id"),
        ("channelId", "channel_id"),
        ("userId", "user_id"),
        ("sendTime", "send_time"),
        ("createdAt", "created_at"),
    ],
    "ticketMessages": [("guildId", "guild_id"), ("channelId", "channel_id")],
    "tickets": [("guildId", "guild_id"), ("channelId", "channel_id")],
    "triggerMessages": [("guildId", "guild_id"), ("caseSensitive", "case_sensitive")],
    "triggerMessagesChannel": [("guildId", "guild_id"), ("channelId", "channel_id")],
    "twitchOnlineNotification": [
        ("channelId", "channel_id"),
        ("guildId", "guild_id"),
        ("notificationMessage", "notification_message"),
    ],
}


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


def _column_clause(conn: Connection, table: str, column: str) -> str | None:
    row = conn.execute(
        text(
            "SELECT column_type, is_nullable, column_default, extra "
            "FROM information_schema.columns "
            "WHERE table_schema = DATABASE() AND table_name = :table AND column_name = :column"
        ),
        {"table": table, "column": column},
    ).fetchone()
    if not row:
        return None
    col_type, is_nullable, col_default, extra = row
    nullable = "NULL" if is_nullable == "YES" else "NOT NULL"
    parts = [col_type, nullable]
    if col_default is not None:
        default = str(col_default)
        if default.upper() == "CURRENT_TIMESTAMP" or "current_timestamp" in default.lower():
            parts.append("DEFAULT CURRENT_TIMESTAMP")
        elif default.upper() != "NULL":
            parts.append(f"DEFAULT {default}")
    if extra:
        parts.append(extra)
    return " ".join(parts)


def _drop_foreign_keys_on(conn: Connection, table: str) -> None:
    rows = conn.execute(
        text(
            "SELECT DISTINCT constraint_name FROM information_schema.table_constraints "
            "WHERE table_schema = DATABASE() AND table_name = :table AND constraint_type = 'FOREIGN KEY'"
        ),
        {"table": table},
    ).fetchall()
    for (constraint_name,) in rows:
        _execute_idempotent(f"ALTER TABLE `{table}` DROP FOREIGN KEY `{constraint_name}`")


def _drop_foreign_keys_referencing(conn: Connection, referenced_table: str) -> None:
    rows = conn.execute(
        text(
            "SELECT DISTINCT table_name, constraint_name FROM information_schema.key_column_usage "
            "WHERE table_schema = DATABASE() AND referenced_table_name = :parent"
        ),
        {"parent": referenced_table},
    ).fetchall()
    for child_table, constraint_name in rows:
        _execute_idempotent(f"ALTER TABLE `{child_table}` DROP FOREIGN KEY `{constraint_name}`")


def _rename_column(conn: Connection, table: str, old_name: str, new_name: str) -> None:
    if _has_column(conn, table, new_name) or not _has_column(conn, table, old_name):
        return
    clause = _column_clause(conn, table, old_name)
    if not clause:
        return
    _execute_idempotent(
        f"ALTER TABLE `{table}` CHANGE COLUMN `{old_name}` `{new_name}` {clause}"
    )


def _restore_foreign_keys(conn: Connection) -> None:
    if _table_exists(conn, "dynamicslowmode") and _table_exists(conn, "dynamicslowmode_messages"):
        if _has_column(conn, "dynamicslowmode_messages", "channel_id") and _has_column(
            conn, "dynamicslowmode", "channel_id"
        ):
            _execute_idempotent(
                "ALTER TABLE `dynamicslowmode_messages` ADD CONSTRAINT `dynamicslowmode_messages_channel_fk` "
                "FOREIGN KEY (`channel_id`) REFERENCES `dynamicslowmode` (`channel_id`) "
                "ON DELETE CASCADE ON UPDATE CASCADE"
            )

    if _table_exists(conn, "triggerMessages") and _table_exists(conn, "triggerMessagesChannel"):
        trigger_ok = _has_column(conn, "triggerMessages", "guild_id") and _has_column(
            conn, "triggerMessages", "id"
        )
        channel_ok = _has_column(conn, "triggerMessagesChannel", "guild_id") and _has_column(
            conn, "triggerMessagesChannel", "triggerId"
        )
        if trigger_ok and channel_ok:
            _execute_idempotent(
                "ALTER TABLE `triggerMessagesChannel` ADD CONSTRAINT `triggerMessagesChannel_parent_fk` "
                "FOREIGN KEY (`guild_id`, `triggerId`) REFERENCES `triggerMessages` (`guild_id`, `id`) "
                "ON DELETE CASCADE ON UPDATE CASCADE"
            )

    if _table_exists(conn, "ticketMessages") and _table_exists(conn, "tickets"):
        ticket_msg_ok = _has_column(conn, "ticketMessages", "guild_id") and _has_column(
            conn, "ticketMessages", "id"
        )
        tickets_ok = _has_column(conn, "tickets", "guild_id") and _has_column(
            conn, "tickets", "ticketMessageId"
        )
        if ticket_msg_ok and tickets_ok:
            _execute_idempotent(
                "ALTER TABLE `tickets` ADD CONSTRAINT `tickets_parent_fk` "
                "FOREIGN KEY (`guild_id`, `ticketMessageId`) REFERENCES `ticketMessages` (`guild_id`, `id`) "
                "ON DELETE CASCADE ON UPDATE CASCADE"
            )


def upgrade() -> None:
    conn = op.get_bind()
    tables = [t for t in _LEGACY_RENAMES if _table_exists(conn, t)]

    for table in tables:
        _drop_foreign_keys_referencing(conn, table)
    for table in tables:
        _drop_foreign_keys_on(conn, table)

    for table, renames in _LEGACY_RENAMES.items():
        if not _table_exists(conn, table):
            continue
        for old_name, new_name in renames:
            _rename_column(conn, table, old_name, new_name)

    _restore_foreign_keys(conn)


def downgrade() -> None:
    pass
