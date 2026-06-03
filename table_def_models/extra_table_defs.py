from __future__ import annotations

from table_def_models.table_def import TableDef, col, fk, idx


def register_extra_table_defs(registry: dict[str, TableDef]) -> None:
    registry["giveaway"] = TableDef(
        name="giveaway",
        columns=[
            col("giveaway_id", "INT UNSIGNED", pk=True, ai=True),
            col("guild_id", "VARCHAR(20)", nullable=False),
            col("title", "VARCHAR(128)", nullable=False),
            col("description", "VARCHAR(1024)"),
            col("winners", "TINYINT(4)", default="1"),
            col("withButton", "TINYINT(1)", default="1"),
            col("customName", "VARCHAR(32)"),
            col("sponsor", "VARCHAR(20)"),
            col("price", "VARCHAR(64)"),
            col("message", "VARCHAR(128)"),
            col("endtime", "DATETIME", nullable=False),
            col("starttime", "DATETIME"),
            col("started", "TINYINT(1)", default="0"),
            col("ended", "TINYINT(1)", default="0"),
            col("newMessageRequirement", "SMALLINT UNSIGNED"),
            col("dayRequirement", "SMALLINT UNSIGNED"),
            col("voiceRequirement", "SMALLINT UNSIGNED"),
            col("sendFailed", "TINYINT(1)", default="0"),
            col("channel_id", "VARCHAR(20)"),
            col("messageId", "VARCHAR(20)", default="'pending'"),
            col("created_at", "TIMESTAMP", default="CURRENT_TIMESTAMP"),
        ],
        indices=[idx("idx_giveaway_ended_endtime", "ended", "endtime")],
    )
    registry["giveaway_channelRequirement"] = TableDef(
        name="giveaway_channelRequirement",
        primary_key=["giveaway_id", "channel_id"],
        columns=[
            col("giveaway_id", "INT UNSIGNED", nullable=False),
            col("channel_id", "VARCHAR(20)"),
            col("amount", "SMALLINT UNSIGNED"),
        ],
    )
    registry["giveawayVoiceTime"] = TableDef(
        name="giveawayVoiceTime",
        primary_key=["giveaway_id", "user_id"],
        columns=[
            col("giveaway_id", "INT UNSIGNED", nullable=False),
            col("user_id", "VARCHAR(20)"),
            col("voiceMinutes", "MEDIUMINT UNSIGNED", default="0"),
        ],
    )
    registry["giveawayNewMessage"] = TableDef(
        name="giveawayNewMessage",
        primary_key=["giveaway_id", "user_id"],
        columns=[
            col("giveaway_id", "INT UNSIGNED", nullable=False),
            col("user_id", "VARCHAR(20)"),
            col("messages", "MEDIUMINT UNSIGNED"),
        ],
    )
    registry["giveaway_channelMessages"] = TableDef(
        name="giveaway_channelMessages",
        primary_key=["giveaway_id", "channel_id", "user_id"],
        columns=[
            col("giveaway_id", "INT UNSIGNED", nullable=False),
            col("channel_id", "VARCHAR(20)"),
            col("user_id", "VARCHAR(20)"),
            col("amount", "MEDIUMINT UNSIGNED", default="0"),
        ],
    )
    registry["aiSituations"] = TableDef(
        name="aiSituations",
        columns=[
            col("user_id", "VARCHAR(20)", pk=True),
            col("situation", "VARCHAR(4000)", default="NULL"),
            col("name", "VARCHAR(15)", default="NULL"),
            col("created_at", "TIMESTAMP", default="CURRENT_TIMESTAMP"),
            col("temperature", "DECIMAL(3, 2)", default="1"),
            col("top_p", "DECIMAL(3, 2)", default="1"),
            col("frequency_penalty", "DECIMAL(3, 2)", default="0"),
            col("presence_penalty", "DECIMAL(3, 2)", default="0"),
            col("unlocked", "TINYINT(1)", default="0"),
        ],
    )
    registry["claimedBoosterChannel"] = TableDef(
        name="claimedBoosterChannel",
        primary_key=["user_id", "channel_id"],
        columns=[
            col("user_id", "VARCHAR(20)", nullable=False),
            col("channel_id", "VARCHAR(20)"),
            col("guild_id", "VARCHAR(20)"),
        ],
    )
    registry["claimedBoosterRole"] = TableDef(
        name="claimedBoosterRole",
        primary_key=["user_id", "role_id"],
        columns=[
            col("user_id", "VARCHAR(20)", nullable=False),
            col("role_id", "VARCHAR(20)"),
            col("guild_id", "VARCHAR(20)"),
        ],
    )
    _log_flags_default_one = (
        "automodRuleCreate",
        "automodRuleUpdate",
        "automodRuleDelete",
        "guild_channelDelete",
        "guild_channelCreate",
        "guild_channelUpdate",
        "guildUpdate",
        "inviteCreate",
        "memberJoin",
        "memberLeave",
        "memberUpdate",
        "userUpdate",
        "memberBan",
        "memberUnban",
        "presenceUpdate",
        "messageEdit",
        "messageDelete",
        "guildRoleCreate",
        "guildRoleDelete",
        "guildRoleUpdate",
    )
    _log_flags_default_zero = ("automodAction", "inviteDelete", "reactionAdd", "reactionRemove")
    log_cols = [col("guild_id", "VARCHAR(20)", pk=True)]
    for flag in _log_flags_default_one:
        log_cols.append(col(flag, "TINYINT(1)", default="1"))
    for flag in _log_flags_default_zero:
        log_cols.append(col(flag, "TINYINT(1)", default="0"))
    registry["log_enables"] = TableDef(name="log_enables", columns=log_cols)
    registry["scheduledMessages"] = TableDef(
        name="scheduledMessages",
        columns=[
            col("messageId", "BIGINT", pk=True, ai=True),
            col("guild_id", "VARCHAR(20)"),
            col("channel_id", "VARCHAR(20)"),
            col("user_id", "VARCHAR(20)", nullable=False),
            col("content", "VARCHAR(1024)", nullable=False),
            col("send_time", "DATETIME", nullable=False),
            col("repeatInterval", "MEDIUMINT UNSIGNED"),
            col("repeatAmount", "MEDIUMINT UNSIGNED"),
            col("attachments", "TEXT"),
            col("discord_message_id", "VARCHAR(20)", default="NULL"),
            col("created_at", "TIMESTAMP", default="CURRENT_TIMESTAMP"),
        ],
        indices=[
            idx("idx_sendtime", "send_time"),
            idx("idx_user", "user_id"),
            idx("idx_guild", "guild_id"),
            idx("idx_discord_message", "discord_message_id"),
        ],
    )
    registry["reports"] = TableDef(
        name="reports",
        columns=[
            col("id", "INT", pk=True, ai=True),
            col("guild_id", "VARCHAR(20)"),
            col("user_id", "VARCHAR(20)"),
            col("reporterId", "VARCHAR(20)"),
            col("reason", "VARCHAR(1024)"),
            col("created_at", "TIMESTAMP", default="CURRENT_TIMESTAMP"),
            col("status", "VARCHAR(20)", default="'pending'"),
            col("status_updated_at", "TIMESTAMP", default="NULL"),
            col("status_updated_by", "VARCHAR(20)", default="NULL"),
            col("status_note", "VARCHAR(1024)", default="NULL"),
            col("anonymous", "TINYINT(1)", default="0"),
        ],
        indices=[idx("idx_status", "status"), idx("idx_guild", "guild_id")],
    )
    registry["report_evidence"] = TableDef(
        name="report_evidence",
        columns=[
            col("id", "INT", pk=True, ai=True),
            col("guild_id", "VARCHAR(20)"),
            col("report_id", "INT"),
            col("url", "VARCHAR(2048)"),
            col("filename", "VARCHAR(255)", default="NULL"),
            col("uploaded_by", "VARCHAR(20)", default="NULL"),
            col("uploaded_at", "TIMESTAMP", default="CURRENT_TIMESTAMP"),
        ],
        indices=[idx("idx_report", "guild_id", "report_id")],
        foreign_keys=[fk(["report_id"], "reports", ["id"])],
    )
    registry["report_mod_actions"] = TableDef(
        name="report_mod_actions",
        columns=[
            col("id", "INT", pk=True, ai=True),
            col("guild_id", "VARCHAR(20)"),
            col("report_id", "INT"),
            col("action_type", "VARCHAR(20)"),
            col("target_id", "VARCHAR(20)"),
            col("performed_by", "VARCHAR(20)"),
            col("details", "VARCHAR(1024)", default="NULL"),
            col("created_at", "TIMESTAMP", default="CURRENT_TIMESTAMP"),
        ],
        indices=[idx("idx_report", "guild_id", "report_id")],
        foreign_keys=[fk(["report_id"], "reports", ["id"])],
    )
    registry["report_anonymity"] = TableDef(
        name="report_anonymity",
        columns=[
            col("guild_id", "VARCHAR(20)", pk=True),
            col("enabled", "TINYINT(1)", default="0"),
        ],
    )
    registry["report_notification_optout"] = TableDef(
        name="report_notification_optout",
        primary_key=["guild_id", "user_id"],
        columns=[
            col("guild_id", "VARCHAR(20)", nullable=False),
            col("user_id", "VARCHAR(20)", nullable=False),
        ],
    )
    registry["triggerMessages"] = TableDef(
        name="triggerMessages",
        columns=[
            col("id", "INT", pk=True, ai=True),
            col("guild_id", "VARCHAR(20)"),
            col("trigger", "VARCHAR(128)"),
            col("response", "VARCHAR(1024)"),
            col("case_sensitive", "TINYINT(1)", default="0"),
        ],
        indices=[idx("idx_guild", "guild_id")],
    )
    registry["triggerMessagesChannel"] = TableDef(
        name="triggerMessagesChannel",
        primary_key=["guild_id", "channel_id", "triggerId"],
        columns=[
            col("guild_id", "VARCHAR(20)", nullable=False),
            col("channel_id", "VARCHAR(20)"),
            col("triggerId", "INT", nullable=False),
        ],
        foreign_keys=[fk(["guild_id", "triggerId"], "triggerMessages", ["guild_id", "id"])],
    )
    registry["ticketMessages"] = TableDef(
        name="ticketMessages",
        columns=[
            col("id", "INT", pk=True, ai=True),
            col("guild_id", "VARCHAR(20)"),
            col("channel_id", "VARCHAR(20)"),
            col("introduction", "VARCHAR(1024)"),
            col("pingRole", "VARCHAR(20)"),
            col("name", "VARCHAR(128)"),
            col("description", "VARCHAR(1024)"),
            col("summaryChannelId", "VARCHAR(20)"),
        ],
        indices=[idx("idx_guild", "guild_id")],
    )
    registry["tickets"] = TableDef(
        name="tickets",
        primary_key=["guild_id", "channel_id", "ticketMessageId"],
        columns=[
            col("guild_id", "VARCHAR(20)", nullable=False),
            col("openerId", "VARCHAR(20)"),
            col("openedAt", "TIMESTAMP", default="CURRENT_TIMESTAMP"),
            col("closed", "TINYINT(1)", default="0"),
            col("closedAt", "TIMESTAMP", default="NULL"),
            col("closedBy", "VARCHAR(20)", default="NULL"),
            col("channel_id", "VARCHAR(20)"),
            col("ticketMessageId", "INT", nullable=False),
        ],
        foreign_keys=[fk(["guild_id", "ticketMessageId"], "ticketMessages", ["guild_id", "id"])],
    )
    registry["wordle_stats"] = TableDef(
        name="wordle_stats",
        primary_key=["user_id", "guild_id"],
        columns=[
            col("user_id", "VARCHAR(20)", nullable=False),
            col("guild_id", "VARCHAR(20)", nullable=False),
            col("games_played", "INT UNSIGNED", default="0"),
            col("games_won", "INT UNSIGNED", default="0"),
            col("current_streak", "INT UNSIGNED", default="0"),
            col("max_streak", "INT UNSIGNED", default="0"),
            col("guess_distribution", "VARCHAR(64)", default="'0,0,0,0,0,0'"),
            col("hard_mode_games_played", "INT UNSIGNED", default="0"),
            col("hard_mode_games_won", "INT UNSIGNED", default="0"),
        ],
    )
    registry["welcome_channel"] = TableDef(
        name="welcome_channel",
        primary_key=["channel_id", "guild_id"],
        columns=[
            col("channel_id", "VARCHAR(20)", nullable=False),
            col("guild_id", "VARCHAR(20)"),
            col("message", "VARCHAR(1024)", default="NULL"),
            col("imageBackground", "VARCHAR(255)", default="NULL"),
        ],
    )
    registry["leave_channel"] = TableDef(
        name="leave_channel",
        primary_key=["channel_id", "guild_id"],
        columns=[
            col("channel_id", "VARCHAR(20)", nullable=False),
            col("guild_id", "VARCHAR(20)"),
            col("message", "VARCHAR(1024)", default="NULL"),
            col("imageBackground", "VARCHAR(255)", default="NULL"),
        ],
    )
    registry["dynamicslowmode"] = TableDef(
        name="dynamicslowmode",
        columns=[
            col("guild_id", "VARCHAR(20)"),
            col("channel_id", "VARCHAR(20)", pk=True),
            col("messages", "INT"),
            col("per", "INT"),
            col("resetafter", "INT"),
            col("cashedSlowmode", "INT"),
        ],
    )
    registry["dynamicslowmode_messages"] = TableDef(
        name="dynamicslowmode_messages",
        columns=[
            col("id", "INT", pk=True, ai=True),
            col("channel_id", "VARCHAR(20)"),
            col("messageId", "VARCHAR(20)"),
            col("send_time", "DATETIME"),
        ],
        indices=[
            idx("idx_channel", "channel_id"),
            idx("idx_message", "messageId"),
            idx("idx_sendtime", "send_time"),
        ],
        foreign_keys=[fk(["channel_id"], "dynamicslowmode", ["channel_id"])],
    )
    registry["twitchOnlineNotification"] = TableDef(
        name="twitchOnlineNotification",
        columns=[
            col("id", "INT", pk=True, ai=True),
            col("channel_id", "VARCHAR(20)"),
            col("guild_id", "VARCHAR(20)"),
            col("twitchUuid", "VARCHAR(64)"),
            col("twitchName", "VARCHAR(128)"),
            col("notification_message", "VARCHAR(1024)", default="NULL"),
        ],
        indices=[idx("idx_channel", "channel_id"), idx("idx_guild", "guild_id")],
    )
