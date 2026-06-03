"""Frozen DDL for revision 001_initial_schema (do not edit; regenerate via scripts/generate_initial_schema_snapshot.py)."""

from __future__ import annotations

CREATE_ORDER: list[str] = [
    "afkMessages",
    "afk_users",
    "aiSituations",
    "aiToken",
    "autopublish",
    "blacklistedChannel",
    "blacklistedUser",
    "blacklisted_role",
    "blockedReporters",
    "boosterRole",
    "booster_channel",
    "brawlstarsLinkedAccounts",
    "channelXpBoost",
    "channel_overwrites",
    "claimedBoosterChannel",
    "claimedBoosterRole",
    "counting",
    "counting_challenge",
    "counting_modes",
    "dynamicslowmode",
    "feedbackBlocked",
    "giveaway",
    "giveawayBlacklistedRole",
    "giveawayBlacklistedUser",
    "giveawayNewMessage",
    "giveawayParticipant",
    "giveawayRoleRequirement",
    "giveawayVoiceTime",
    "giveaway_channelMessages",
    "giveaway_channelRequirement",
    "join_to_create_channel",
    "leave_channel",
    "level",
    "levelConfig",
    "levelRole",
    "logBlacklistChannel",
    "logCategoryBlacklist",
    "logRoleBlacklist",
    "logUserBlacklist",
    "logVoiceBlacklist",
    "log_channel",
    "log_channel_blacklist",
    "log_enables",
    "mediaChannel",
    "message_tracking_opt_out",
    "report_anonymity",
    "report_notification_optout",
    "reportchannel",
    "reports",
    "roleXpBoost",
    "scheduledMessages",
    "ticketMessages",
    "triggerMessages",
    "twitchOnlineNotification",
    "userXpBoost",
    "warn_config",
    "warnings",
    "welcome_channel",
    "wordchain",
    "wordle_stats",
    "dynamicslowmode_messages",
    "report_evidence",
    "report_mod_actions",
    "tickets",
    "triggerMessagesChannel",
]

TABLE_DDL: dict[str, str] = {
    "afkMessages": """CREATE TABLE IF NOT EXISTS `afkMessages` (
  `user_id` VARCHAR(20) NOT NULL,
  `messageId` VARCHAR(20) NOT NULL,
  `channel_id` VARCHAR(20),
  PRIMARY KEY (`user_id`, `messageId`)
) ENGINE=InnoDB
DEFAULT CHARSET=utf8mb4""",
    "afk_users": """CREATE TABLE IF NOT EXISTS `afk_users` (
  `user_id` VARCHAR(20),
  `reason` VARCHAR(1024),
  PRIMARY KEY (`user_id`)
) ENGINE=InnoDB
DEFAULT CHARSET=utf8mb4""",
    "aiSituations": """CREATE TABLE IF NOT EXISTS `aiSituations` (
  `user_id` VARCHAR(20),
  `situation` VARCHAR(4000) DEFAULT NULL,
  `name` VARCHAR(15) DEFAULT NULL,
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  `temperature` DECIMAL(3, 2) DEFAULT 1,
  `top_p` DECIMAL(3, 2) DEFAULT 1,
  `frequency_penalty` DECIMAL(3, 2) DEFAULT 0,
  `presence_penalty` DECIMAL(3, 2) DEFAULT 0,
  `unlocked` TINYINT(1) DEFAULT 0,
  PRIMARY KEY (`user_id`)
) ENGINE=InnoDB
DEFAULT CHARSET=utf8mb4""",
    "aiToken": """CREATE TABLE IF NOT EXISTS `aiToken` (
  `freeToken` SMALLINT UNSIGNED DEFAULT 500,
  `plusToken` SMALLINT UNSIGNED DEFAULT 0,
  `paidToken` INT UNSIGNED DEFAULT 0,
  `usedToken` INT UNSIGNED DEFAULT 0,
  `user_id` VARCHAR(20),
  PRIMARY KEY (`user_id`)
) ENGINE=InnoDB
DEFAULT CHARSET=utf8mb4""",
    "autopublish": """CREATE TABLE IF NOT EXISTS `autopublish` (
  `channel_id` VARCHAR(20),
  PRIMARY KEY (`channel_id`)
) ENGINE=InnoDB
DEFAULT CHARSET=utf8mb4""",
    "blacklistedChannel": """CREATE TABLE IF NOT EXISTS `blacklistedChannel` (
  `channel_id` VARCHAR(20) NOT NULL,
  `guild_id` VARCHAR(20) NOT NULL,
  `reason` VARCHAR(255) DEFAULT NULL,
  `blacklisted_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`channel_id`, `guild_id`)
) ENGINE=InnoDB
DEFAULT CHARSET=utf8mb4""",
    "blacklistedUser": """CREATE TABLE IF NOT EXISTS `blacklistedUser` (
  `user_id` VARCHAR(20) NOT NULL,
  `guild_id` VARCHAR(20) NOT NULL,
  `reason` VARCHAR(255) DEFAULT NULL,
  `blacklisted_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`user_id`, `guild_id`)
) ENGINE=InnoDB
DEFAULT CHARSET=utf8mb4""",
    "blacklisted_role": """CREATE TABLE IF NOT EXISTS `blacklisted_role` (
  `role_id` VARCHAR(20) NOT NULL,
  `guild_id` VARCHAR(20) NOT NULL,
  `reason` VARCHAR(255) DEFAULT NULL,
  `blacklisted_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`role_id`, `guild_id`)
) ENGINE=InnoDB
DEFAULT CHARSET=utf8mb4""",
    "blockedReporters": """CREATE TABLE IF NOT EXISTS `blockedReporters` (
  `guild_id` VARCHAR(20) NOT NULL,
  `user_id` VARCHAR(20) NOT NULL,
  PRIMARY KEY (`guild_id`, `user_id`)
) ENGINE=InnoDB
DEFAULT CHARSET=utf8mb4""",
    "boosterRole": """CREATE TABLE IF NOT EXISTS `boosterRole` (
  `guild_id` VARCHAR(20) NOT NULL,
  `role_id` VARCHAR(20) NOT NULL,
  PRIMARY KEY (`guild_id`, `role_id`)
) ENGINE=InnoDB
DEFAULT CHARSET=utf8mb4""",
    "booster_channel": """CREATE TABLE IF NOT EXISTS `booster_channel` (
  `guild_id` VARCHAR(20) NOT NULL,
  `channel_id` VARCHAR(20) NOT NULL,
  PRIMARY KEY (`guild_id`, `channel_id`)
) ENGINE=InnoDB
DEFAULT CHARSET=utf8mb4""",
    "brawlstarsLinkedAccounts": """CREATE TABLE IF NOT EXISTS `brawlstarsLinkedAccounts` (
  `user_id` VARCHAR(20),
  `brawlstarsTag` VARCHAR(20),
  PRIMARY KEY (`user_id`)
) ENGINE=InnoDB
DEFAULT CHARSET=utf8mb4""",
    "channelXpBoost": """CREATE TABLE IF NOT EXISTS `channelXpBoost` (
  `channel_id` VARCHAR(20) NOT NULL,
  `guild_id` VARCHAR(20) NOT NULL,
  `boost` DECIMAL(4, 2) UNSIGNED DEFAULT 1,
  `additive` TINYINT(1) DEFAULT 0,
  `boosted_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`channel_id`, `guild_id`)
) ENGINE=InnoDB
DEFAULT CHARSET=utf8mb4""",
    "channel_overwrites": """CREATE TABLE IF NOT EXISTS `channel_overwrites` (
  `id` INT AUTO_INCREMENT,
  `channel_id` VARCHAR(20) NOT NULL,
  `role_id` VARCHAR(20) NOT NULL,
  `overwrites` JSON,
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB
DEFAULT CHARSET=utf8mb4""",
    "claimedBoosterChannel": """CREATE TABLE IF NOT EXISTS `claimedBoosterChannel` (
  `user_id` VARCHAR(20) NOT NULL,
  `channel_id` VARCHAR(20),
  `guild_id` VARCHAR(20),
  PRIMARY KEY (`user_id`, `channel_id`)
) ENGINE=InnoDB
DEFAULT CHARSET=utf8mb4""",
    "claimedBoosterRole": """CREATE TABLE IF NOT EXISTS `claimedBoosterRole` (
  `user_id` VARCHAR(20) NOT NULL,
  `role_id` VARCHAR(20),
  `guild_id` VARCHAR(20),
  PRIMARY KEY (`user_id`, `role_id`)
) ENGINE=InnoDB
DEFAULT CHARSET=utf8mb4""",
    "counting": """CREATE TABLE IF NOT EXISTS `counting` (
  `channel_id` VARCHAR(20),
  `progress` INT UNSIGNED DEFAULT 0,
  `last_counter_id` VARCHAR(20) DEFAULT NULL,
  `guild_id` VARCHAR(20),
  PRIMARY KEY (`channel_id`)
) ENGINE=InnoDB
DEFAULT CHARSET=utf8mb4""",
    "counting_challenge": """CREATE TABLE IF NOT EXISTS `counting_challenge` (
  `channel_id` VARCHAR(20),
  `progress` INT UNSIGNED DEFAULT 0,
  `last_counter_id` VARCHAR(20) DEFAULT NULL,
  `guild_id` VARCHAR(20),
  PRIMARY KEY (`channel_id`)
) ENGINE=InnoDB
DEFAULT CHARSET=utf8mb4""",
    "counting_modes": """CREATE TABLE IF NOT EXISTS `counting_modes` (
  `channel_id` VARCHAR(20),
  `progress` INT DEFAULT 0,
  `mode` TINYINT UNSIGNED DEFAULT 0,
  `goal` INT,
  `last_counter_id` VARCHAR(20) DEFAULT NULL,
  `guild_id` VARCHAR(20),
  PRIMARY KEY (`channel_id`)
) ENGINE=InnoDB
DEFAULT CHARSET=utf8mb4""",
    "dynamicslowmode": """CREATE TABLE IF NOT EXISTS `dynamicslowmode` (
  `guild_id` VARCHAR(20),
  `channel_id` VARCHAR(20),
  `messages` INT,
  `per` INT,
  `resetafter` INT,
  `cashedSlowmode` INT,
  PRIMARY KEY (`channel_id`)
) ENGINE=InnoDB
DEFAULT CHARSET=utf8mb4""",
    "feedbackBlocked": """CREATE TABLE IF NOT EXISTS `feedbackBlocked` (
  `user_id` VARCHAR(20),
  PRIMARY KEY (`user_id`)
) ENGINE=InnoDB
DEFAULT CHARSET=utf8mb4""",
    "giveaway": """CREATE TABLE IF NOT EXISTS `giveaway` (
  `giveaway_id` INT UNSIGNED AUTO_INCREMENT,
  `guild_id` VARCHAR(20) NOT NULL,
  `title` VARCHAR(128) NOT NULL,
  `description` VARCHAR(1024),
  `winners` TINYINT(4) DEFAULT 1,
  `withButton` TINYINT(1) DEFAULT 1,
  `customName` VARCHAR(32),
  `sponsor` VARCHAR(20),
  `price` VARCHAR(64),
  `message` VARCHAR(128),
  `endtime` DATETIME NOT NULL,
  `starttime` DATETIME,
  `started` TINYINT(1) DEFAULT 0,
  `ended` TINYINT(1) DEFAULT 0,
  `newMessageRequirement` SMALLINT UNSIGNED,
  `dayRequirement` SMALLINT UNSIGNED,
  `voiceRequirement` SMALLINT UNSIGNED,
  `sendFailed` TINYINT(1) DEFAULT 0,
  `channel_id` VARCHAR(20),
  `messageId` VARCHAR(20) DEFAULT 'pending',
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`giveaway_id`),
  INDEX `idx_giveaway_ended_endtime` (`ended`, `endtime`)
) ENGINE=InnoDB
DEFAULT CHARSET=utf8mb4""",
    "giveawayBlacklistedRole": """CREATE TABLE IF NOT EXISTS `giveawayBlacklistedRole` (
  `role_id` VARCHAR(20),
  `guild_id` VARCHAR(20),
  `reason` VARCHAR(255) DEFAULT NULL,
  PRIMARY KEY (`role_id`)
) ENGINE=InnoDB
DEFAULT CHARSET=utf8mb4""",
    "giveawayBlacklistedUser": """CREATE TABLE IF NOT EXISTS `giveawayBlacklistedUser` (
  `user_id` VARCHAR(20) NOT NULL,
  `guild_id` VARCHAR(20) NOT NULL,
  `reason` VARCHAR(255) DEFAULT NULL,
  PRIMARY KEY (`user_id`, `guild_id`)
) ENGINE=InnoDB
DEFAULT CHARSET=utf8mb4""",
    "giveawayNewMessage": """CREATE TABLE IF NOT EXISTS `giveawayNewMessage` (
  `giveaway_id` INT UNSIGNED NOT NULL,
  `user_id` VARCHAR(20),
  `messages` MEDIUMINT UNSIGNED,
  PRIMARY KEY (`giveaway_id`, `user_id`)
) ENGINE=InnoDB
DEFAULT CHARSET=utf8mb4""",
    "giveawayParticipant": """CREATE TABLE IF NOT EXISTS `giveawayParticipant` (
  `user_id` VARCHAR(20) NOT NULL,
  `giveaway_id` INT UNSIGNED NOT NULL,
  PRIMARY KEY (`user_id`, `giveaway_id`)
) ENGINE=InnoDB
DEFAULT CHARSET=utf8mb4""",
    "giveawayRoleRequirement": """CREATE TABLE IF NOT EXISTS `giveawayRoleRequirement` (
  `role_id` VARCHAR(20) NOT NULL,
  `giveaway_id` INT UNSIGNED NOT NULL,
  PRIMARY KEY (`role_id`, `giveaway_id`)
) ENGINE=InnoDB
DEFAULT CHARSET=utf8mb4""",
    "giveawayVoiceTime": """CREATE TABLE IF NOT EXISTS `giveawayVoiceTime` (
  `giveaway_id` INT UNSIGNED NOT NULL,
  `user_id` VARCHAR(20),
  `voiceMinutes` MEDIUMINT UNSIGNED DEFAULT 0,
  PRIMARY KEY (`giveaway_id`, `user_id`)
) ENGINE=InnoDB
DEFAULT CHARSET=utf8mb4""",
    "giveaway_channelMessages": """CREATE TABLE IF NOT EXISTS `giveaway_channelMessages` (
  `giveaway_id` INT UNSIGNED NOT NULL,
  `channel_id` VARCHAR(20),
  `user_id` VARCHAR(20),
  `amount` MEDIUMINT UNSIGNED DEFAULT 0,
  PRIMARY KEY (`giveaway_id`, `channel_id`, `user_id`)
) ENGINE=InnoDB
DEFAULT CHARSET=utf8mb4""",
    "giveaway_channelRequirement": """CREATE TABLE IF NOT EXISTS `giveaway_channelRequirement` (
  `giveaway_id` INT UNSIGNED NOT NULL,
  `channel_id` VARCHAR(20),
  `amount` SMALLINT UNSIGNED,
  PRIMARY KEY (`giveaway_id`, `channel_id`)
) ENGINE=InnoDB
DEFAULT CHARSET=utf8mb4""",
    "join_to_create_channel": """CREATE TABLE IF NOT EXISTS `join_to_create_channel` (
  `guild_id` VARCHAR(20) NOT NULL,
  `channel_id` VARCHAR(20) NOT NULL,
  PRIMARY KEY (`guild_id`, `channel_id`)
) ENGINE=InnoDB
DEFAULT CHARSET=utf8mb4""",
    "leave_channel": """CREATE TABLE IF NOT EXISTS `leave_channel` (
  `guild_id` VARCHAR(20) NOT NULL,
  `channel_id` VARCHAR(20),
  `message` VARCHAR(1024) DEFAULT NULL,
  `imageBackground` VARCHAR(255) DEFAULT NULL,
  PRIMARY KEY (`guild_id`)
) ENGINE=InnoDB
DEFAULT CHARSET=utf8mb4""",
    "level": """CREATE TABLE IF NOT EXISTS `level` (
  `user_id` VARCHAR(20) NOT NULL,
  `guild_id` VARCHAR(20) NOT NULL,
  `xp` INT UNSIGNED DEFAULT 0,
  `customBackground` VARCHAR(255) DEFAULT NULL,
  `last_xp_gain` DATETIME DEFAULT NOW(),
  `last_voice_xp_gain` DATETIME DEFAULT NOW(),
  PRIMARY KEY (`user_id`, `guild_id`),
  INDEX `idx_level_guild_xp` (`guild_id`, `xp` DESC)
) ENGINE=InnoDB
DEFAULT CHARSET=utf8mb4""",
    "levelConfig": """CREATE TABLE IF NOT EXISTS `levelConfig` (
  `guild_id` VARCHAR(20),
  `difficulty` ENUM('easy', 'medium', 'hard', 'extreme', 'custom') DEFAULT 'medium',
  `customFormula` VARCHAR(255) DEFAULT NULL,
  `level_up_messageActive` TINYINT(1) DEFAULT 1,
  `level_up_message` VARCHAR(1000) DEFAULT NULL,
  `level_up_channel_id` VARCHAR(20) DEFAULT NULL,
  `active` TINYINT(1) DEFAULT 1,
  `textCooldown` INT DEFAULT 60,
  `voiceCooldown` INT DEFAULT 60,
  PRIMARY KEY (`guild_id`)
) ENGINE=InnoDB
DEFAULT CHARSET=utf8mb4""",
    "levelRole": """CREATE TABLE IF NOT EXISTS `levelRole` (
  `role_id` VARCHAR(20) NOT NULL,
  `guild_id` VARCHAR(20) NOT NULL,
  `level` INT UNSIGNED DEFAULT 0,
  PRIMARY KEY (`role_id`, `guild_id`)
) ENGINE=InnoDB
DEFAULT CHARSET=utf8mb4""",
    "logBlacklistChannel": """CREATE TABLE IF NOT EXISTS `logBlacklistChannel` (
  `guild_id` VARCHAR(20) NOT NULL,
  `channel_id` VARCHAR(20) NOT NULL,
  PRIMARY KEY (`guild_id`, `channel_id`)
) ENGINE=InnoDB
DEFAULT CHARSET=utf8mb4""",
    "logCategoryBlacklist": """CREATE TABLE IF NOT EXISTS `logCategoryBlacklist` (
  `guild_id` VARCHAR(20) NOT NULL,
  `channel_id` VARCHAR(20) NOT NULL,
  PRIMARY KEY (`guild_id`, `channel_id`)
) ENGINE=InnoDB
DEFAULT CHARSET=utf8mb4""",
    "logRoleBlacklist": """CREATE TABLE IF NOT EXISTS `logRoleBlacklist` (
  `guild_id` VARCHAR(20) NOT NULL,
  `role_id` VARCHAR(20) NOT NULL,
  PRIMARY KEY (`guild_id`, `role_id`)
) ENGINE=InnoDB
DEFAULT CHARSET=utf8mb4""",
    "logUserBlacklist": """CREATE TABLE IF NOT EXISTS `logUserBlacklist` (
  `guild_id` VARCHAR(20) NOT NULL,
  `user_id` VARCHAR(20) NOT NULL,
  PRIMARY KEY (`guild_id`, `user_id`)
) ENGINE=InnoDB
DEFAULT CHARSET=utf8mb4""",
    "logVoiceBlacklist": """CREATE TABLE IF NOT EXISTS `logVoiceBlacklist` (
  `guild_id` VARCHAR(20) NOT NULL,
  `channel_id` VARCHAR(20) NOT NULL,
  PRIMARY KEY (`guild_id`, `channel_id`)
) ENGINE=InnoDB
DEFAULT CHARSET=utf8mb4""",
    "log_channel": """CREATE TABLE IF NOT EXISTS `log_channel` (
  `guild_id` VARCHAR(20) NOT NULL,
  `channel_id` VARCHAR(20) NOT NULL,
  PRIMARY KEY (`guild_id`, `channel_id`)
) ENGINE=InnoDB
DEFAULT CHARSET=utf8mb4""",
    "log_channel_blacklist": """CREATE TABLE IF NOT EXISTS `log_channel_blacklist` (
  `guild_id` VARCHAR(20) NOT NULL,
  `channel_id` VARCHAR(20) NOT NULL,
  PRIMARY KEY (`guild_id`, `channel_id`)
) ENGINE=InnoDB
DEFAULT CHARSET=utf8mb4""",
    "log_enables": """CREATE TABLE IF NOT EXISTS `log_enables` (
  `guild_id` VARCHAR(20),
  `automodRuleCreate` TINYINT(1) DEFAULT 1,
  `automodRuleUpdate` TINYINT(1) DEFAULT 1,
  `automodRuleDelete` TINYINT(1) DEFAULT 1,
  `guild_channelDelete` TINYINT(1) DEFAULT 1,
  `guild_channelCreate` TINYINT(1) DEFAULT 1,
  `guild_channelUpdate` TINYINT(1) DEFAULT 1,
  `guildUpdate` TINYINT(1) DEFAULT 1,
  `inviteCreate` TINYINT(1) DEFAULT 1,
  `memberJoin` TINYINT(1) DEFAULT 1,
  `memberLeave` TINYINT(1) DEFAULT 1,
  `memberUpdate` TINYINT(1) DEFAULT 1,
  `userUpdate` TINYINT(1) DEFAULT 1,
  `memberBan` TINYINT(1) DEFAULT 1,
  `memberUnban` TINYINT(1) DEFAULT 1,
  `presenceUpdate` TINYINT(1) DEFAULT 1,
  `messageEdit` TINYINT(1) DEFAULT 1,
  `messageDelete` TINYINT(1) DEFAULT 1,
  `guildRoleCreate` TINYINT(1) DEFAULT 1,
  `guildRoleDelete` TINYINT(1) DEFAULT 1,
  `guildRoleUpdate` TINYINT(1) DEFAULT 1,
  `automodAction` TINYINT(1) DEFAULT 0,
  `inviteDelete` TINYINT(1) DEFAULT 0,
  `reactionAdd` TINYINT(1) DEFAULT 0,
  `reactionRemove` TINYINT(1) DEFAULT 0,
  PRIMARY KEY (`guild_id`)
) ENGINE=InnoDB
DEFAULT CHARSET=utf8mb4""",
    "mediaChannel": """CREATE TABLE IF NOT EXISTS `mediaChannel` (
  `channel_id` VARCHAR(20),
  `guild_id` VARCHAR(20),
  PRIMARY KEY (`channel_id`)
) ENGINE=InnoDB
DEFAULT CHARSET=utf8mb4""",
    "message_tracking_opt_out": """CREATE TABLE IF NOT EXISTS `message_tracking_opt_out` (
  `user_id` VARCHAR(20),
  PRIMARY KEY (`user_id`)
) ENGINE=InnoDB
DEFAULT CHARSET=utf8mb4""",
    "report_anonymity": """CREATE TABLE IF NOT EXISTS `report_anonymity` (
  `guild_id` VARCHAR(20),
  `enabled` TINYINT(1) DEFAULT 0,
  PRIMARY KEY (`guild_id`)
) ENGINE=InnoDB
DEFAULT CHARSET=utf8mb4""",
    "report_notification_optout": """CREATE TABLE IF NOT EXISTS `report_notification_optout` (
  `guild_id` VARCHAR(20) NOT NULL,
  `user_id` VARCHAR(20) NOT NULL,
  PRIMARY KEY (`guild_id`, `user_id`)
) ENGINE=InnoDB
DEFAULT CHARSET=utf8mb4""",
    "reportchannel": """CREATE TABLE IF NOT EXISTS `reportchannel` (
  `guild_id` VARCHAR(20) NOT NULL,
  `channel_id` VARCHAR(20) NOT NULL,
  PRIMARY KEY (`guild_id`, `channel_id`)
) ENGINE=InnoDB
DEFAULT CHARSET=utf8mb4""",
    "reports": """CREATE TABLE IF NOT EXISTS `reports` (
  `id` INT AUTO_INCREMENT,
  `guild_id` VARCHAR(20),
  `user_id` VARCHAR(20),
  `reporterId` VARCHAR(20),
  `reason` VARCHAR(1024),
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  `status` VARCHAR(20) DEFAULT 'pending',
  `status_updated_at` TIMESTAMP DEFAULT NULL,
  `status_updated_by` VARCHAR(20) DEFAULT NULL,
  `status_note` VARCHAR(1024) DEFAULT NULL,
  `anonymous` TINYINT(1) DEFAULT 0,
  PRIMARY KEY (`id`),
  INDEX `idx_status` (`status`),
  INDEX `idx_guild` (`guild_id`)
) ENGINE=InnoDB
DEFAULT CHARSET=utf8mb4""",
    "roleXpBoost": """CREATE TABLE IF NOT EXISTS `roleXpBoost` (
  `role_id` VARCHAR(20) NOT NULL,
  `guild_id` VARCHAR(20) NOT NULL,
  `boost` DECIMAL(4, 2) UNSIGNED DEFAULT 1,
  `additive` TINYINT(1) DEFAULT 0,
  `boosted_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`role_id`, `guild_id`)
) ENGINE=InnoDB
DEFAULT CHARSET=utf8mb4""",
    "scheduledMessages": """CREATE TABLE IF NOT EXISTS `scheduledMessages` (
  `messageId` BIGINT AUTO_INCREMENT,
  `guild_id` VARCHAR(20),
  `channel_id` VARCHAR(20),
  `user_id` VARCHAR(20) NOT NULL,
  `content` VARCHAR(1024) NOT NULL,
  `send_time` DATETIME NOT NULL,
  `repeatInterval` MEDIUMINT UNSIGNED,
  `repeatAmount` MEDIUMINT UNSIGNED,
  `attachments` TEXT,
  `discord_message_id` VARCHAR(20) DEFAULT NULL,
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`messageId`),
  INDEX `idx_sendtime` (`send_time`),
  INDEX `idx_user` (`user_id`),
  INDEX `idx_guild` (`guild_id`),
  INDEX `idx_discord_message` (`discord_message_id`)
) ENGINE=InnoDB
DEFAULT CHARSET=utf8mb4""",
    "ticketMessages": """CREATE TABLE IF NOT EXISTS `ticketMessages` (
  `id` INT AUTO_INCREMENT,
  `guild_id` VARCHAR(20) NOT NULL,
  `channel_id` VARCHAR(20),
  `introduction` VARCHAR(1024),
  `pingRole` VARCHAR(20),
  `name` VARCHAR(128),
  `description` VARCHAR(1024),
  `summaryChannelId` VARCHAR(20),
  PRIMARY KEY (`guild_id`, `id`),
  INDEX `idx_guild` (`guild_id`)
) ENGINE=InnoDB
DEFAULT CHARSET=utf8mb4""",
    "triggerMessages": """CREATE TABLE IF NOT EXISTS `triggerMessages` (
  `id` INT AUTO_INCREMENT,
  `guild_id` VARCHAR(20) NOT NULL,
  `trigger` VARCHAR(128),
  `response` VARCHAR(1024),
  `case_sensitive` TINYINT(1) DEFAULT 0,
  PRIMARY KEY (`guild_id`, `id`),
  INDEX `idx_guild` (`guild_id`)
) ENGINE=InnoDB
DEFAULT CHARSET=utf8mb4""",
    "twitchOnlineNotification": """CREATE TABLE IF NOT EXISTS `twitchOnlineNotification` (
  `id` INT AUTO_INCREMENT,
  `channel_id` VARCHAR(20),
  `guild_id` VARCHAR(20),
  `twitchUuid` VARCHAR(64),
  `twitchName` VARCHAR(128),
  `notification_message` VARCHAR(1024) DEFAULT NULL,
  PRIMARY KEY (`id`),
  INDEX `idx_channel` (`channel_id`),
  INDEX `idx_guild` (`guild_id`)
) ENGINE=InnoDB
DEFAULT CHARSET=utf8mb4""",
    "userXpBoost": """CREATE TABLE IF NOT EXISTS `userXpBoost` (
  `user_id` VARCHAR(20) NOT NULL,
  `guild_id` VARCHAR(20) NOT NULL,
  `boost` DECIMAL(4, 2) UNSIGNED DEFAULT 1,
  `additive` TINYINT(1) DEFAULT 0,
  `boosted_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`user_id`, `guild_id`)
) ENGINE=InnoDB
DEFAULT CHARSET=utf8mb4""",
    "warn_config": """CREATE TABLE IF NOT EXISTS `warn_config` (
  `guild_id` VARCHAR(20),
  `expiration_days` INT DEFAULT 0,
  `timeout_threshold` INT DEFAULT 0,
  `timeout_duration` INT DEFAULT 0,
  `kick_threshold` INT DEFAULT 0,
  `ban_threshold` INT DEFAULT 0,
  PRIMARY KEY (`guild_id`)
) ENGINE=InnoDB
DEFAULT CHARSET=utf8mb4""",
    "warnings": """CREATE TABLE IF NOT EXISTS `warnings` (
  `id` INT AUTO_INCREMENT,
  `guild_id` VARCHAR(20) NOT NULL,
  `user_id` VARCHAR(20) NOT NULL,
  `reason` VARCHAR(255),
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  `expires_at` TIMESTAMP DEFAULT NULL,
  `created_by` VARCHAR(20) NOT NULL,
  `escalation_level` INT DEFAULT 0,
  PRIMARY KEY (`id`),
  INDEX `idx_warnings_user_guild` (`user_id`, `guild_id`)
) ENGINE=InnoDB
DEFAULT CHARSET=utf8mb4""",
    "welcome_channel": """CREATE TABLE IF NOT EXISTS `welcome_channel` (
  `guild_id` VARCHAR(20) NOT NULL,
  `channel_id` VARCHAR(20),
  `message` VARCHAR(1024) DEFAULT NULL,
  `imageBackground` VARCHAR(255) DEFAULT NULL,
  PRIMARY KEY (`guild_id`)
) ENGINE=InnoDB
DEFAULT CHARSET=utf8mb4""",
    "wordchain": """CREATE TABLE IF NOT EXISTS `wordchain` (
  `channel_id` VARCHAR(20),
  `word` VARCHAR(1028) DEFAULT NULL,
  `last_user_id` VARCHAR(20) DEFAULT NULL,
  `guild_id` VARCHAR(20),
  PRIMARY KEY (`channel_id`)
) ENGINE=InnoDB
DEFAULT CHARSET=utf8mb4""",
    "wordle_stats": """CREATE TABLE IF NOT EXISTS `wordle_stats` (
  `user_id` VARCHAR(20) NOT NULL,
  `guild_id` VARCHAR(20) NOT NULL,
  `games_played` INT UNSIGNED DEFAULT 0,
  `games_won` INT UNSIGNED DEFAULT 0,
  `current_streak` INT UNSIGNED DEFAULT 0,
  `max_streak` INT UNSIGNED DEFAULT 0,
  `guess_distribution` VARCHAR(64) DEFAULT '0,0,0,0,0,0',
  `hard_mode_games_played` INT UNSIGNED DEFAULT 0,
  `hard_mode_games_won` INT UNSIGNED DEFAULT 0,
  PRIMARY KEY (`user_id`, `guild_id`)
) ENGINE=InnoDB
DEFAULT CHARSET=utf8mb4""",
    "dynamicslowmode_messages": """CREATE TABLE IF NOT EXISTS `dynamicslowmode_messages` (
  `id` INT AUTO_INCREMENT,
  `channel_id` VARCHAR(20),
  `messageId` VARCHAR(20),
  `send_time` DATETIME,
  PRIMARY KEY (`id`),
  INDEX `idx_channel` (`channel_id`),
  INDEX `idx_message` (`messageId`),
  INDEX `idx_sendtime` (`send_time`),
  FOREIGN KEY (`channel_id`) REFERENCES `dynamicslowmode` (`channel_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB
DEFAULT CHARSET=utf8mb4""",
    "report_evidence": """CREATE TABLE IF NOT EXISTS `report_evidence` (
  `id` INT AUTO_INCREMENT,
  `guild_id` VARCHAR(20),
  `report_id` INT,
  `url` VARCHAR(2048),
  `filename` VARCHAR(255) DEFAULT NULL,
  `uploaded_by` VARCHAR(20) DEFAULT NULL,
  `uploaded_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  INDEX `idx_report` (`guild_id`, `report_id`),
  FOREIGN KEY (`report_id`) REFERENCES `reports` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB
DEFAULT CHARSET=utf8mb4""",
    "report_mod_actions": """CREATE TABLE IF NOT EXISTS `report_mod_actions` (
  `id` INT AUTO_INCREMENT,
  `guild_id` VARCHAR(20),
  `report_id` INT,
  `action_type` VARCHAR(20),
  `target_id` VARCHAR(20),
  `performed_by` VARCHAR(20),
  `details` VARCHAR(1024) DEFAULT NULL,
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  INDEX `idx_report` (`guild_id`, `report_id`),
  FOREIGN KEY (`report_id`) REFERENCES `reports` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB
DEFAULT CHARSET=utf8mb4""",
    "tickets": """CREATE TABLE IF NOT EXISTS `tickets` (
  `guild_id` VARCHAR(20) NOT NULL,
  `openerId` VARCHAR(20),
  `openedAt` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  `closed` TINYINT(1) DEFAULT 0,
  `closedAt` TIMESTAMP DEFAULT NULL,
  `closedBy` VARCHAR(20) DEFAULT NULL,
  `channel_id` VARCHAR(20),
  `ticketMessageId` INT NOT NULL,
  PRIMARY KEY (`guild_id`, `channel_id`, `ticketMessageId`),
  FOREIGN KEY (`guild_id`, `ticketMessageId`) REFERENCES `ticketMessages` (`guild_id`, `id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB
DEFAULT CHARSET=utf8mb4""",
    "triggerMessagesChannel": """CREATE TABLE IF NOT EXISTS `triggerMessagesChannel` (
  `guild_id` VARCHAR(20) NOT NULL,
  `channel_id` VARCHAR(20),
  `triggerId` INT NOT NULL,
  PRIMARY KEY (`guild_id`, `channel_id`, `triggerId`),
  FOREIGN KEY (`guild_id`, `triggerId`) REFERENCES `triggerMessages` (`guild_id`, `id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB
DEFAULT CHARSET=utf8mb4""",
}
