import json
from collections.abc import Sequence
from datetime import datetime
from typing import Any, cast

import asyncmy  # type: ignore[import-untyped]

from config import database_ip, database_password, database_schema, database_user
from utility import get_level_for_xp, get_xp_for_level

pool: Any | None = None


def set_pool(p: Any) -> None:
    global pool
    pool = p


def check_pool_initialized() -> bool:
    return pool is not None


async def execute_query(query: str, params: Sequence[Any] | dict[str, Any] | None = None) -> list[tuple[Any, ...]] | None:
    if not pool:
        print(
            "Tried to execute action without pool. Pool is not yet initialized.Returning...\nquery: ",
            query,
        )
        return None

    try:
        connection = await asyncmy.connect(
            host=database_ip,
            user=database_user,
            password=database_password,
            db=database_schema,
        )
        async with connection.cursor() as cursor:
            await cursor.execute(query, params)
            result: list[tuple[Any, ...]] = await cursor.fetchall()
            return result
    except Exception as e:
        print(f"An error occurred during query execution: {e}\nquery: {query}\nparams: {params}")
        return None


async def execute_action(query: str, params: Sequence[Any] | dict[str, Any] | None = None) -> int | None:
    if not pool:
        print(
            ("Tried to execute action without pool. Pool is not yet initialized. Returning...\nquery: "),
            query,
        )
        return None
    try:
        connection = await asyncmy.connect(
            host=database_ip,
            user=database_user,
            password=database_password,
            db=database_schema,
        )
        async with connection.cursor() as cursor:
            await cursor.execute(query, params)
            await connection.commit()
            row_count: int = cursor.rowcount
            return row_count

    except Exception as e:
        print(f"An error occurred during action execution: {e}\nquery: {query}\nparams: {params}")
        return None


async def execute_insert_and_get_id(query: str, params: Sequence[Any] | dict[str, Any] | None = None) -> int | None:
    if not pool:
        return None
    try:
        connection = await asyncmy.connect(
            host=database_ip,
            user=database_user,
            password=database_password,
            db=database_schema,
        )
        async with connection.cursor() as cursor:
            await cursor.execute(query, params)
            await connection.commit()
            await cursor.execute("SELECT LAST_INSERT_ID()")
            last_id = await cursor.fetchone()
            return last_id[0] if last_id else None
    except Exception as e:
        print(f"An error occurred during insert: {e}\nquery: {query}\nparams: {params}")
        return None


async def create_tables() -> None:
    tables: dict[str, str] = {}
    tables["warnings"] = (
        "CREATE TABLE IF NOT EXISTS `warnings` ("
        "  `id` INT AUTO_INCREMENT PRIMARY KEY,"
        "  `guild_id` VARCHAR(20) NOT NULL,"
        "  `user_id` VARCHAR(20) NOT NULL,"
        "  `reason` VARCHAR(255),"
        "  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,"
        "  `expires_at` TIMESTAMP NULL,"
        "  `created_by` VARCHAR(20) NOT NULL,"
        "  `escalation_level` INT DEFAULT 0"
        ") ENGINE=InnoDB"
    )
    tables["warn_config"] = (
        "CREATE TABLE IF NOT EXISTS `warn_config` ("
        "  `guild_id` VARCHAR(20) PRIMARY KEY,"
        "  `expiration_days` INT DEFAULT 0,"
        "  `timeout_threshold` INT DEFAULT 0,"
        "  `timeout_duration` INT DEFAULT 0,"
        "  `kick_threshold` INT DEFAULT 0,"
        "  `ban_threshold` INT DEFAULT 0"
        ") ENGINE=InnoDB"
    )
    tables["channel_overwrites"] = (
        "CREATE TABLE IF NOT EXISTS `channel_overwrites` ("
        "  `id` INT AUTO_INCREMENT PRIMARY KEY,"
        "  `channel_id` VARCHAR(20) NOT NULL,"
        "  `role_id` VARCHAR(20) NOT NULL,"
        "  `overwrites` JSON,"
        "  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP"
        ") ENGINE=InnoDB"
    )
    tables["message_tracking_opt_out"] = (
        "CREATE TABLE IF NOT EXISTS `message_tracking_opt_out` (  `user_id` VARCHAR(20) PRIMARY KEY) ENGINE=InnoDB"
    )
    tables["counting"] = (
        "CREATE TABLE IF NOT EXISTS `counting` ("
        "  `channel_id` VARCHAR(20) PRIMARY KEY,"
        "  `progress` INT UNSIGNED DEFAULT 0,"
        "  `last_counter_id` VARCHAR(20) DEFAULT NULL,"
        "  `guild_id` VARCHAR(20)"
        ") ENGINE=InnoDB"
    )
    tables["counting_challenge"] = (
        "CREATE TABLE IF NOT EXISTS `counting_challenge` ("
        "  `channel_id` VARCHAR(20) PRIMARY KEY,"
        "  `progress` INT UNSIGNED DEFAULT 0,"
        "  `last_counter_id` VARCHAR(20) DEFAULT NULL,"
        "  `guild_id` VARCHAR(20)"
        ") ENGINE=InnoDB"
    )
    tables["counting_modes"] = (
        "CREATE TABLE IF NOT EXISTS `counting_modes` ("
        "  `channel_id` VARCHAR(20) PRIMARY KEY,"
        "  `progress` INT DEFAULT 0,"
        "  `mode` TINYINT UNSIGNED DEFAULT 0,"
        "  `goal` INT,"
        "  `last_counter_id` VARCHAR(20) DEFAULT NULL,"
        "  `guild_id` VARCHAR(20)"
        ") ENGINE=InnoDB"
    )
    tables["wordchain"] = (
        "CREATE TABLE IF NOT EXISTS `wordchain` ("
        "  `channel_id` VARCHAR(20) PRIMARY KEY,"
        "  `word` VARCHAR(1028) DEFAULT NULL,"
        "  `last_user_id` VARCHAR(20) DEFAULT NULL,"
        "  `guild_id` VARCHAR(20)"
        ") ENGINE=InnoDB"
    )
    tables["level"] = (
        "CREATE TABLE IF NOT EXISTS `level` ("
        "  `user_id` VARCHAR(20) NOT NULL,"
        "  `guild_id` VARCHAR(20) NOT NULL,"
        "  `xp` INT UNSIGNED DEFAULT 0,"
        "  `customBackground` VARCHAR(255) DEFAULT NULL,"
        "  `last_xp_gain` DATETIME DEFAULT NOW(),"
        "  `last_voice_xp_gain` DATETIME DEFAULT NOW(),"
        "  PRIMARY KEY(`user_id`, `guild_id`)"
        ") ENGINE=InnoDB"
    )
    tables["blacklistedUser"] = (
        "CREATE TABLE IF NOT EXISTS `blacklistedUser` ("
        "  `user_id` VARCHAR(20) NOT NULL,"
        "  `guild_id` VARCHAR(20) NOT NULL,"
        "  `reason` VARCHAR(255) DEFAULT NULL,"
        "  `blacklisted_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,"
        "  PRIMARY KEY(`user_id`, `guild_id`)"
        ") ENGINE=InnoDB"
    )
    tables["blacklistedRole"] = (
        "CREATE TABLE IF NOT EXISTS `blacklistedRole` ("
        "  `role_id` VARCHAR(20) NOT NULL,"
        "  `guild_id` VARCHAR(20) NOT NULL,"
        "  `reason` VARCHAR(255) DEFAULT NULL,"
        "  `blacklisted_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,"
        "  PRIMARY KEY(`role_id`, `guild_id`)"
        ") ENGINE=InnoDB"
    )
    tables["blacklistedChannel"] = (
        "CREATE TABLE IF NOT EXISTS `blacklistedChannel` ("
        "  `channel_id` VARCHAR(20) NOT NULL,"
        "  `guild_id` VARCHAR(20) NOT NULL,"
        "  `reason` VARCHAR(255) DEFAULT NULL,"
        "  `blacklisted_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,"
        "  PRIMARY KEY(`channel_id`, `guild_id`)"
        ") ENGINE=InnoDB"
    )
    tables["userXpBoost"] = (
        "CREATE TABLE IF NOT EXISTS `userXpBoost` ("
        "  `user_id` VARCHAR(20) NOT NULL,"
        "  `guild_id` VARCHAR(20) NOT NULL,"
        "  `boost` DECIMAL(4, 2) UNSIGNED DEFAULT 1,"
        "  `additive` TINYINT(1) DEFAULT 0,"
        "  `boosted_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,"
        "  PRIMARY KEY(`user_id`, `guild_id`)"
        ") ENGINE=InnoDB"
    )
    tables["roleXpBoost"] = (
        "CREATE TABLE IF NOT EXISTS `roleXpBoost` ("
        "  `role_id` VARCHAR(20) NOT NULL,"
        "  `guild_id` VARCHAR(20) NOT NULL,"
        "  `boost` DECIMAL(4, 2) UNSIGNED DEFAULT 1,"
        "  `additive` TINYINT(1) DEFAULT 0,"
        "  `boosted_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,"
        "  PRIMARY KEY(`role_id`, `guild_id`)"
        ") ENGINE=InnoDB"
    )
    tables["channelXpBoost"] = (
        "CREATE TABLE IF NOT EXISTS `channelXpBoost` ("
        "  `channel_id` VARCHAR(20) NOT NULL,"
        "  `guild_id` VARCHAR(20) NOT NULL,"
        "  `boost` DECIMAL(4, 2) UNSIGNED DEFAULT 1,"
        "  `additive` TINYINT(1) DEFAULT 0,"
        "  `boosted_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,"
        "  PRIMARY KEY(`channel_id`, `guild_id`)"
        ") ENGINE=InnoDB"
    )
    tables["levelRole"] = (
        "CREATE TABLE IF NOT EXISTS `levelRole` ("
        "  `role_id` VARCHAR(20) NOT NULL,"
        "  `guild_id` VARCHAR(20) NOT NULL,"
        "  `level` INT UNSIGNED DEFAULT 0,"
        "  PRIMARY KEY(`role_id`, `guild_id`)"
        ") ENGINE=InnoDB"
    )
    tables["levelConfig"] = (
        "CREATE TABLE IF NOT EXISTS `levelConfig` ("
        "  `guild_id` VARCHAR(20) PRIMARY KEY,"
        "  `difficulty` ENUM('easy', 'medium', 'hard', 'extreme', 'custom') "
        "DEFAULT 'medium',"
        "  `customFormula` VARCHAR(255) DEFAULT NULL,"
        "  `levelUpMessageActive` TINYINT(1) DEFAULT 1,"
        "  `levelUpMessage` VARCHAR(1000) DEFAULT NULL,"
        "  `levelUpChannelId` VARCHAR(20) DEFAULT NULL,"
        "  `active` TINYINT(1) DEFAULT 1,"
        "  `textCooldown` INT DEFAULT 60,"
        "  `voiceCooldown` INT DEFAULT 60"
        ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;"
    )
    tables["giveaway"] = """
    CREATE TABLE IF NOT EXISTS `giveaway` (
        `giveawayId` INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
        `guildId` VARCHAR(20) NOT NULL,
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
        `channelId` VARCHAR(20),
        `messageId` VARCHAR(20) DEFAULT "pending",
        `createdAt` TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    ) ENGINE=InnoDB;
    """
    tables["giveawayChannelRequirement"] = """
    CREATE TABLE IF NOT EXISTS `giveawayChannelRequirement` (
        `giveawayId` INT UNSIGNED,
        `channelId` VARCHAR(20),
        `amount` SMALLINT UNSIGNED,
        PRIMARY KEY(`giveawayId`, `channelId`)
    ) ENGINE=InnoDB;
    """
    tables["giveawayParticipant"] = """
    CREATE TABLE IF NOT EXISTS `giveawayParticipant` (
        `userId` VARCHAR(20),
        `giveawayId` INT UNSIGNED,
        PRIMARY KEY(`userId`, `giveawayId`)
    ) ENGINE=InnoDB;
    """
    tables["giveawayRoleRequirement"] = """
    CREATE TABLE IF NOT EXISTS `giveawayRoleRequirement` (
        `roleId` VARCHAR(20),
        `giveawayId` INT UNSIGNED,
        PRIMARY KEY(`roleId`, `giveawayId`)
    ) ENGINE=InnoDB;
    """
    tables["giveawayVoiceTime"] = """
    CREATE TABLE IF NOT EXISTS `giveawayVoiceTime` (
        `giveawayId` INT UNSIGNED,
        `userId` VARCHAR(20),
        `voiceMinutes` MEDIUMINT UNSIGNED DEFAULT 0,
        PRIMARY KEY(`giveawayId`, `userId`)
    ) ENGINE=InnoDB;
    """
    tables["giveawayNewMessage"] = """
    CREATE TABLE IF NOT EXISTS `giveawayNewMessage` (
        `giveawayId` INT UNSIGNED,
        `userId` VARCHAR(20),
        `messages` MEDIUMINT UNSIGNED,
        PRIMARY KEY(`giveawayId`, `userId`)
    ) ENGINE=InnoDB;
    """
    tables["giveawayBlacklistedRole"] = """
    CREATE TABLE IF NOT EXISTS `giveawayBlacklistedRole` (
        `roleId` VARCHAR(20) PRIMARY KEY,
        `guildId` VARCHAR(20),
        `reason` VARCHAR(255) DEFAULT NULL
    ) ENGINE=InnoDB;
    """
    tables["giveawayBlacklistedUser"] = """
    CREATE TABLE IF NOT EXISTS `giveawayBlacklistedUser` (
        `userId` VARCHAR(20),
        `guildId` VARCHAR(20),
        `reason` VARCHAR(255) DEFAULT NULL,
        PRIMARY KEY(`userId`, `guildId`)
    ) ENGINE=InnoDB;
    """
    tables["giveawayChannelMessages"] = """
    CREATE TABLE IF NOT EXISTS `giveawayChannelMessages` (
        `giveawayId` INT UNSIGNED,
        `channelId` VARCHAR(20),
        `userId` VARCHAR(20),
        `amount` MEDIUMINT UNSIGNED DEFAULT 0,
        PRIMARY KEY(`giveawayId`, `channelId`, `userId`)
    ) ENGINE=InnoDB;
    """
    tables["aiToken"] = """
    CREATE TABLE IF NOT EXISTS `aiToken` (
        `freeToken` SMALLINT UNSIGNED DEFAULT 500,
        `plusToken` SMALLINT UNSIGNED DEFAULT 0,
        `paidToken` INT UNSIGNED DEFAULT 0,
        `usedToken` INT UNSIGNED DEFAULT 0,
        `userId` VARCHAR(20) PRIMARY KEY
    ) ENGINE=InnoDB;
    """
    tables["aiSituations"] = """
    CREATE TABLE IF NOT EXISTS `aiSituations` (
        `userId` VARCHAR(20) PRIMARY KEY,
        `situation` VARCHAR(4000) DEFAULT NULL,
        `name` VARCHAR(15) DEFAULT NULL,
        `createdAt` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        `temperature` DECIMAL(3, 2) DEFAULT 1,
        `top_p` DECIMAL(3, 2) DEFAULT 1,
        `frequency_penalty` DECIMAL(3, 2) DEFAULT 0,
        `presence_penalty` DECIMAL(3, 2) DEFAULT 0,
        `unlocked` TINYINT(1) DEFAULT 0
    ) ENGINE=InnoDB;
    """
    tables["autopublish"] = """
    CREATE TABLE IF NOT EXISTS `autopublish` (
        `channelId` VARCHAR(20) PRIMARY KEY
    ) ENGINE=InnoDB;
    """
    tables["feedbackBlocked"] = """
    CREATE TABLE IF NOT EXISTS `feedbackBlocked` (
        `userId` VARCHAR(20) PRIMARY KEY
    ) ENGINE=InnoDB;
    """
    tables["afkUsers"] = """
    CREATE TABLE IF NOT EXISTS `afkUsers` (
        `userId` VARCHAR(20) PRIMARY KEY,
        `reason` VARCHAR(1024)
    ) ENGINE=InnoDB;
    """
    tables["afkMessages"] = """
    CREATE TABLE IF NOT EXISTS `afkMessages` (
        `userId` VARCHAR(20),
        `messageId` VARCHAR(20),
        `channelId` VARCHAR(20),
        PRIMARY KEY(`userId`, `messageId`)
    ) ENGINE=InnoDB;
    """
    tables["boosterChannel"] = """
    CREATE TABLE IF NOT EXISTS `boosterChannel` (
        `guildId` VARCHAR(20),
        `channelId` VARCHAR(20),
        PRIMARY KEY(`guildId`, `channelId`)
    ) ENGINE=InnoDB;
    """
    tables["claimedBoosterChannel"] = """
    CREATE TABLE IF NOT EXISTS `claimedBoosterChannel` (
        `userId` VARCHAR(20),
        `channelId` VARCHAR(20),
        `guildId` VARCHAR(20),
        PRIMARY KEY(`userId`, `channelId`)
    ) ENGINE=InnoDB;
    """
    tables["boosterRole"] = """
    CREATE TABLE IF NOT EXISTS `boosterRole` (
        `guildId` VARCHAR(20),
        `roleId` VARCHAR(20),
        PRIMARY KEY(`guildId`, `roleId`)
    ) ENGINE=InnoDB;
    """
    tables["claimedBoosterRole"] = """
    CREATE TABLE IF NOT EXISTS `claimedBoosterRole` (
        `userId` VARCHAR(20),
        `roleId` VARCHAR(20),
        `guildId` VARCHAR(20),
        PRIMARY KEY(`userId`, `roleId`)
    ) ENGINE=InnoDB;
    """
    tables["logChannel"] = """
    CREATE TABLE IF NOT EXISTS `logChannel` (
        `guildId` VARCHAR(20),
        `channelId` VARCHAR(20),
        PRIMARY KEY(`guildId`, `channelId`)
    ) ENGINE=InnoDB;
    """
    tables["logChannelBlacklist"] = """
    CREATE TABLE IF NOT EXISTS `logChannelBlacklist` (
        `guildId` VARCHAR(20),
        `channelId` VARCHAR(20),
        PRIMARY KEY(`guildId`, `channelId`)
    ) ENGINE=InnoDB;
    """
    tables["logRoleBlacklist"] = """
    CREATE TABLE IF NOT EXISTS `logRoleBlacklist` (
        `guildId` VARCHAR(20),
        `roleId` VARCHAR(20),
        PRIMARY KEY(`guildId`, `roleId`)
    ) ENGINE=InnoDB;
    """
    tables["logBlacklistChannel"] = """
    CREATE TABLE IF NOT EXISTS `logBlacklistChannel` (
        `guildId` VARCHAR(20),
        `channelId` VARCHAR(20),
        PRIMARY KEY(`guildId`, `channelId`)
    ) ENGINE=InnoDB;
    """
    tables["logUserBlacklist"] = """
    CREATE TABLE IF NOT EXISTS `logUserBlacklist` (
        `guildId` VARCHAR(20),
        `userId` VARCHAR(20),
        PRIMARY KEY(`guildId`, `userId`)
    ) ENGINE=InnoDB;
    """
    tables["logEnables"] = """
    CREATE TABLE IF NOT EXISTS `logEnables` (
        `guildId` VARCHAR(20),
        `automodRuleCreate` TINYINT(1) DEFAULT 1,
        `automodRuleUpdate` TINYINT(1) DEFAULT 1,
        `automodRuleDelete` TINYINT(1) DEFAULT 1,
        `automodAction` TINYINT(1) DEFAULT 0,
        `guildChannelDelete` TINYINT(1) DEFAULT 1,
        `guildChannelCreate` TINYINT(1) DEFAULT 1,
        `guildChannelUpdate` TINYINT(1) DEFAULT 1,
        `guildUpdate` TINYINT(1) DEFAULT 1,
        `inviteCreate` TINYINT(1) DEFAULT 1,
        `inviteDelete` TINYINT(1) DEFAULT 0,
        `memberJoin` TINYINT(1) DEFAULT 1,
        `memberLeave` TINYINT(1) DEFAULT 1,
        `memberUpdate` TINYINT(1) DEFAULT 1,
        `userUpdate` TINYINT(1) DEFAULT 1,
        `memberBan` TINYINT(1) DEFAULT 1,
        `memberUnban` TINYINT(1) DEFAULT 1,
        `presenceUpdate` TINYINT(1) DEFAULT 1,
        `messageEdit` TINYINT(1) DEFAULT 1,
        `messageDelete` TINYINT(1) DEFAULT 1,
        `reactionAdd` TINYINT(1) DEFAULT 0,
        `reactionRemove` TINYINT(1) DEFAULT 0,
        `guildRoleCreate` TINYINT(1) DEFAULT 1,
        `guildRoleDelete` TINYINT(1) DEFAULT 1,
        `guildRoleUpdate` TINYINT(1) DEFAULT 1,
        PRIMARY KEY(`guildId`)
    ) ENGINE=InnoDB;
    """
    tables["scheduledMessages"] = """
    CREATE TABLE IF NOT EXISTS `scheduledMessages` (
        `messageId` BIGINT PRIMARY KEY AUTO_INCREMENT,
        `guildId` VARCHAR(20),
        `channelId` VARCHAR(20),
        `userId` VARCHAR(20) NOT NULL,
        `content` VARCHAR(1024) NOT NULL,
        `sendTime` DATETIME NOT NULL,
        `repeatInterval` MEDIUMINT UNSIGNED,
        `repeatAmount` MEDIUMINT UNSIGNED,
        `createdAt` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        INDEX `idx_sendtime` (sendTime),
        INDEX `idx_user` (userId),
        INDEX `idx_guild` (guildId)
    ) ENGINE=InnoDB;
    """
    tables["reports"] = """
    CREATE TABLE IF NOT EXISTS `reports` (
        `id` INT AUTO_INCREMENT,
        `guildId` VARCHAR(20),
        `userId` VARCHAR(20),
        `reporterId` VARCHAR(20),
        `reason` VARCHAR(1024),
        `createdAt` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        `accepted` TINYINT(1) DEFAULT 0,
        `acceptedAt` TIMESTAMP DEFAULT NULL,
        `acceptedBy` VARCHAR(20) DEFAULT NULL,
        `resolved` TINYINT(1) DEFAULT 0,
        `resolvedAt` TIMESTAMP DEFAULT NULL,
        `resolvedBy` VARCHAR(20) DEFAULT NULL,
        PRIMARY KEY(`id`)
    ) ENGINE=InnoDB;
    """
    tables["blockedReporters"] = """
    CREATE TABLE IF NOT EXISTS `blockedReporters` (
        `guildId` VARCHAR(20),
        `userId` VARCHAR(20),
        PRIMARY KEY(`guildId`, `userId`)
    ) ENGINE=InnoDB;
    """
    tables["reportchannel"] = """
    CREATE TABLE IF NOT EXISTS `reportchannel` (
        `guildId` VARCHAR(20),
        `channelId` VARCHAR(20),
        PRIMARY KEY(`guildId`, `channelId`)
    ) ENGINE=InnoDB;
    """
    tables["triggerMessages"] = """
    CREATE TABLE IF NOT EXISTS `triggerMessages` (
        `id` INT AUTO_INCREMENT,
        `guildId` VARCHAR(20),
        `trigger` VARCHAR(128),
        `response` VARCHAR(1024),
        `caseSensitive` TINYINT(1) DEFAULT 0,
        PRIMARY KEY(`id`),
        INDEX `idx_guild` (`guildId`)
    ) ENGINE=InnoDB;
    """
    tables["triggerMessagesChannel"] = """
    CREATE TABLE IF NOT EXISTS `triggerMessagesChannel` (
        `guildId` VARCHAR(20),
        `channelId` VARCHAR(20),
        `triggerId` INT,
        PRIMARY KEY(`guildId`, `channelId`, `triggerId`),
        FOREIGN KEY (`guildId`, `triggerId`)
            REFERENCES `triggerMessages`(`guildId`, `id`)
            ON DELETE CASCADE
    ) ENGINE=InnoDB;
    """
    tables["ticketMessages"] = """
    CREATE TABLE IF NOT EXISTS `ticketMessages` (
        `id` INT AUTO_INCREMENT,
        `guildId` VARCHAR(20),
        `channelId` VARCHAR(20),
        `introduction` VARCHAR(1024),
        `pingRole` VARCHAR(20),
        `name` VARCHAR(128),
        `description` VARCHAR(1024),
        `summaryChannelId` VARCHAR(20),
        PRIMARY KEY(`id`),
        INDEX `idx_guild` (`guildId`)
    ) ENGINE=InnoDB;
    """
    tables["tickets"] = """
    CREATE TABLE IF NOT EXISTS `tickets` (
        `guildId` VARCHAR(20),
        `openerId` VARCHAR(20),
        `openedAt` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        `closed` TINYINT(1) DEFAULT 0,
        `closedAt` TIMESTAMP DEFAULT NULL,
        `closedBy` VARCHAR(20) DEFAULT NULL,
        `channelId` VARCHAR(20),
        `ticketMessageId` INT,
        PRIMARY KEY(`guildId`, `channelId`, `ticketMessageId`),
        FOREIGN KEY (`guildId`, `ticketMessageId`)
            REFERENCES `ticketMessages`(`guildId`, `id`)
            ON DELETE CASCADE
    ) ENGINE=InnoDB;
    """
    tables["joinToCreateChannel"] = """
    CREATE TABLE IF NOT EXISTS `joinToCreateChannel` (
        `guildId` VARCHAR(20),
        `channelId` VARCHAR(20),
        PRIMARY KEY(`guildId`, `channelId`)
    ) ENGINE=InnoDB;
    """
    tables["mediaChannel"] = """
    CREATE TABLE IF NOT EXISTS `mediaChannel` (
        `channelId` VARCHAR(20),
        `guildId` VARCHAR(20),
        PRIMARY KEY(`channelId`)
    ) ENGINE=InnoDB;
    """
    tables["welcomeChannel"] = """
    CREATE TABLE IF NOT EXISTS `welcomeChannel` (
        `channelId` VARCHAR(20),
        `guildId` VARCHAR(20),
        `message` VARCHAR(1024) DEFAULT NULL,
        `imageBackground` VARCHAR(255) DEFAULT NULL,
        PRIMARY KEY(`channelId`, `guildId`)
    ) ENGINE=InnoDB;
    """
    tables["leaveChannel"] = """
    CREATE TABLE IF NOT EXISTS `leaveChannel` (
        `channelId` VARCHAR(20),
        `guildId` VARCHAR(20),
        `message` VARCHAR(1024) DEFAULT NULL,
        `imageBackground` VARCHAR(255) DEFAULT NULL,
        PRIMARY KEY(`channelId`, `guildId`)
    ) ENGINE=InnoDB;
    """
    tables["dynamicslowmode"] = """
    CREATE TABLE IF NOT EXISTS `dynamicslowmode` (
        `guildId` VARCHAR(20),
        `channelId` VARCHAR(20),
        `messages` INT,
        `per` INT,
        `resetafter` INT,
        `cashedSlowmode` INT,
        PRIMARY KEY(`channelId`)
    ) ENGINE=InnoDB;
    """
    tables["dynamicslowmode_messages"] = """
    CREATE TABLE IF NOT EXISTS `dynamicslowmode_messages` (
        `id` INT AUTO_INCREMENT,
        `channelId` VARCHAR(20),
        `messageId` VARCHAR(20),
        `sendTime` DATETIME,
        PRIMARY KEY(`id`),
        INDEX `idx_channel` (`channelId`),
        INDEX `idx_message` (`messageId`),
        INDEX `idx_sendtime` (`sendTime`),
        FOREIGN KEY (`channelId`)
            REFERENCES `dynamicslowmode`(`channelId`)
            ON DELETE CASCADE
    ) ENGINE=InnoDB;
    """
    tables["twitchOnlineNotification"] = """
    CREATE TABLE IF NOT EXISTS `twitchOnlineNotification` (
        `id` INT AUTO_INCREMENT,
        `channelId` VARCHAR(20),
        `guildId` VARCHAR(20),
        `twitchUuid` VARCHAR(64),
        `twitchName` VARCHAR(128),
        `notificationMessage` VARCHAR(1024) DEFAULT NULL,
        PRIMARY KEY(`id`),
        INDEX `idx_channel` (`channelId`),
        INDEX `idx_guild` (`guildId`)
    ) ENGINE=InnoDB;
    """
    tables["brawlstarsLinkedAccounts"] = """
    CREATE TABLE IF NOT EXISTS `brawlstarsLinkedAccounts` (
        `userId` VARCHAR(20),
        `brawlstarsTag` VARCHAR(20),
        PRIMARY KEY(`userId`)
    ) ENGINE=InnoDB;
    """

    for table_name in tables:
        table_query = tables[table_name]
        await execute_action(table_query)


async def add_warning(
    guild_id: int | str, user_id: str | int, reason: str, expiration_date: datetime, created_by: str | int
) -> None:
    query = "INSERT INTO warnings (guild_id, user_id, reason, expires_at, created_by) VALUES (%s, %s, %s, %s, %s)"
    params = (guild_id, user_id, reason, expiration_date, created_by)
    await execute_action(query, params)


async def get_warnings(guild_id: int | str, user_id: str | int | None = None) -> list[tuple[Any, ...]] | None:
    if user_id:
        query = "SELECT * FROM warnings WHERE guild_id = %s AND user_id = %s AND (expires_at IS NULL OR expires_at > NOW())"
        params = (guild_id, user_id)
        result = await execute_query(query, params)
        return result
    else:
        query = "SELECT * FROM warnings WHERE guild_id = %s AND (expires_at IS NULL OR expires_at > NOW())"
        params = cast(Any, (guild_id,))
        result = await execute_query(query, params)
        return result


async def get_detailed_warnings(guild_id: int | str, user_id: str | int) -> list[tuple[Any, ...]] | None:
    query = (
        "SELECT id, reason, created_at, expires_at, created_by "
        "FROM warnings WHERE guild_id = %s AND user_id = %s "
        "ORDER BY created_at DESC"
    )
    params = (guild_id, user_id)
    result = await execute_query(query, params)
    if result:
        return [(row[0], row[1], row[2], row[3], row[4]) for row in result]
    return None


async def remove_warning(warning_id: int) -> None:
    query = "DELETE FROM warnings WHERE id = %s"
    params = (warning_id,)
    await execute_action(query, params)


async def set_warn_config(
    guild_id: int | str,
    expiration_days: int,
    timeout_threshold: int,
    timeout_duration: int,
    kick_threshold: int,
    ban_threshold: int,
) -> None:
    query = (
        "INSERT INTO warn_config (guild_id, expiration_days, "
        "timeout_threshold, timeout_duration, "
        "kick_threshold, ban_threshold) "
        "VALUES (%s, %s, %s, %s, %s, %s) "
        "ON DUPLICATE KEY UPDATE "
        "expiration_days = VALUES(expiration_days), "
        "timeout_threshold = VALUES(timeout_threshold), "
        "timeout_duration = VALUES(timeout_duration), "
        "kick_threshold = VALUES(kick_threshold), "
        "ban_threshold = VALUES(ban_threshold)"
    )
    params = (
        guild_id,
        expiration_days,
        timeout_threshold,
        timeout_duration,
        kick_threshold,
        ban_threshold,
    )
    await execute_action(query, params)


async def get_warn_config(guild_id: int | str) -> dict[str, int] | None:
    query = "SELECT * FROM warn_config WHERE guild_id = %s"
    params = (guild_id,)
    result = await execute_query(query, params)
    if result:
        (
            _,
            expiration_days,
            timeout_threshold,
            timeout_duration,
            kick_threshold,
            ban_threshold,
        ) = result[0]
        return {
            "expiration_days": expiration_days,
            "timeout_threshold": timeout_threshold,
            "timeout_duration": timeout_duration,
            "kick_threshold": kick_threshold,
            "ban_threshold": ban_threshold,
        }
    else:
        return None


async def save_channel_overwrites(channel_id: int | str, role_id: str | int, overwrites: str) -> None:
    query = "INSERT INTO channel_overwrites (channel_id, role_id, overwrites) VALUES (%s, %s, %s)"
    params = (channel_id, role_id, json.dumps(overwrites))
    await execute_action(query, params)


async def get_channel_overwrites(channel_id: int | str) -> dict[str, Any] | None:
    query = "SELECT role_id, overwrites FROM channel_overwrites WHERE channel_id = %s"
    params = (channel_id,)
    result = await execute_query(query, params)
    if result:
        return {row[0]: json.loads(row[1]) for row in result}
    return None


async def clear_channel_overwrites(channel_id: int | str) -> None:
    query = "DELETE FROM channel_overwrites WHERE channel_id = %s"
    params = (channel_id,)
    await execute_action(query, params)


async def check_if_opted_out(user_id: str | int) -> bool:
    query = "SELECT * FROM message_tracking_opt_out WHERE user_id = %s"
    params = (user_id,)
    result = await execute_query(query, params)
    return result is not None and len(result) > 0


async def opt_out(user_id: str | int) -> None:
    query = "INSERT INTO message_tracking_opt_out (user_id) VALUES (%s)"
    params = (user_id,)
    await execute_action(query, params)


async def opt_in(user_id: str | int) -> None:
    query = "DELETE FROM message_tracking_opt_out WHERE user_id = %s"
    params = (user_id,)
    await execute_action(query, params)


async def set_counting_progress(channel_id: int | str, progress: int, guild_id: int | str) -> None:
    query = "INSERT INTO counting (channel_id, progress, guild_id) VALUES (%s, %s, %s) ON DUPLICATE KEY UPDATE progress = %s"
    params = (channel_id, progress, guild_id, progress)
    await execute_action(query, params)


async def get_counting_channel_amount(guild_id: int | str) -> int:
    query = "SELECT COUNT(progress) FROM counting WHERE guild_id = %s"
    params = (guild_id,)
    result = await execute_query(query, params)
    return len(result) if result else 0


async def get_counting_progress(channel_id: int | str) -> int | None:
    query = "SELECT progress FROM counting WHERE channel_id = %s"
    params = (channel_id,)
    result = await execute_query(query, params)
    return result[0][0] if result else None


async def increase_counting_progress(channel_id: int | str, last_counter_id: str | int) -> None:
    query = "UPDATE counting SET progress = progress + 1, last_counter_id = %s WHERE channel_id = %s"
    params = (last_counter_id, channel_id)
    await execute_action(query, params)


async def get_last_counter_id(channel_id: int | str) -> str | None:
    query = "SELECT last_counter_id FROM counting WHERE channel_id = %s"
    params = (channel_id,)
    result = await execute_query(query, params)
    return result[0][0] if result else None


async def clear_counting(channel_id: int | str) -> None:
    query = "DELETE FROM counting WHERE channel_id = %s"
    params = (channel_id,)
    await execute_action(query, params)


async def set_counting_challenge_progress(channel_id: int | str, progress: int) -> None:
    query = "INSERT INTO counting_challenge (channel_id, progress) VALUES (%s, %s) ON DUPLICATE KEY UPDATE progress = %s"
    params = (channel_id, progress, progress)
    await execute_action(query, params)


async def get_counting_challenge_progress(channel_id: int | str) -> int | None:
    query = "SELECT progress FROM counting_challenge WHERE channel_id = %s"
    params = (channel_id,)
    result = await execute_query(query, params)
    return result[0][0] if result else None


async def increase_counting_challenge_progress(channel_id: int | str, last_counter_id: str | int) -> None:
    query = "UPDATE counting_challenge SET progress = progress + 1, last_counter_id = %s WHERE channel_id = %s"
    params = (last_counter_id, channel_id)
    query = "UPDATE counting_challenge SET progress = progress + 1, last_counter_id = %s WHERE channel_id = %s"
    params = (last_counter_id, channel_id)
    await execute_action(query, params)


async def get_last_challenge_counter_id(channel_id: int | str) -> str | None:
    query = "SELECT last_counter_id FROM counting_challenge WHERE channel_id = %s"
    params = (channel_id,)
    result = await execute_query(query, params)
    query = "DELETE FROM counting_challenge WHERE channel_id = %s"
    params = (channel_id,)
    return result[0][0] if result else None


async def clear_counting_challenge(channel_id: int | str) -> None:
    query = "DELETE FROM counting_challenge WHERE channel_id = %s"
    params = (channel_id,)
    await execute_action(query, params)
    await execute_action(query, params)


async def get_counting_challenge_channel_amount(guild_id: int | str) -> int:
    query = "SELECT COUNT(progress) FROM counting_challenge WHERE guild_id = %s"
    params = (guild_id,)
    result = await execute_query(query, params)
    result = await execute_query(query, params)
    return result[0][0] if result else 0


async def set_counting_mode(channel_id: int | str | int, progress: int, mode: int, guild_id: int | str | int) -> None:
    query = "INSERT INTO counting_modes (channel_id, progress, mode, guild_id) VALUES (%s, %s, %s, %s) ON DUPLICATE KEY UPDATE progress = VALUES(progress), mode = VALUES(mode)"
    params = (channel_id, progress, mode, guild_id, progress, mode)
    await execute_action(query, params)


async def get_counting_mode_progress(channel_id: int | str | int) -> int | None:
    query = "SELECT progress FROM counting_modes WHERE channel_id = %s"
    params = (channel_id,)
    result = await execute_query(query, params)
    return result[0][0] if result else None


async def get_last_mode_counter_id(channel_id: int | str | int) -> str | None:
    query = "SELECT last_counter_id FROM counting_modes WHERE channel_id = %s"
    params = (channel_id,)
    result = await execute_query(query, params)
    return result[0][0] if result else None


async def clear_counting_mode(channel_id: int | str | int) -> None:
    query = "DELETE FROM counting_modes WHERE channel_id = %s"
    params = (channel_id,)
    await execute_action(query, params)


async def get_counting_mode_mode(channel_id: int | str | int) -> int | None:
    query = "SELECT mode FROM counting_modes WHERE channel_id s= %s"
    params = (channel_id,)
    result = await execute_query(query, params)
    return result[0][0] if result else None


async def set_counting_mode_progress(
    channel_id: int | str | int, progress: int, guild_id: int | str | int, mode: int, goal: int, counter_id: str | int
) -> None:
    query = "INSERT INTO counting_modes (channel_id, progress, guild_id, mode, goal, last_counter_id) VALUES (%s, %s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE progress = %s, last_counter_id = %s"
    params = (
        channel_id,
        progress,
        guild_id,
        mode,
        goal,
        counter_id,
        progress,
        counter_id,
    )
    await execute_action(query, params)


async def get_count_mode_goal(channel_id: int | str | int) -> str | None:
    query = "SELECT goal FROM counting_modes WHERE channel_id = %s"
    params = (channel_id,)
    result = await execute_query(query, params)
    return result[0][0] if result else None


async def get_wordchain_word(channel_id: int | str | int) -> str | None:
    query = "SELECT word FROM wordchain WHERE channel_id = %s"
    params = (channel_id,)
    result = await execute_query(query, params)
    return result[0][0] if result else None


async def set_wordchain_word(channel_id: int | str | int, word: str, guild_id: int | str | int, worder_id: str | int) -> None:
    query = "INSERT INTO wordchain (channel_id, word, last_user_id, guild_id) VALUES (%s, %s, %s, %s) ON DUPLICATE KEY UPDATE word = %s, last_user_id = %s"
    params = (channel_id, word, worder_id, guild_id, word, worder_id)
    await execute_action(query, params)


async def get_wordchain_last_user_id(channel_id: int | str | int) -> str | None:
    query = "SELECT last_user_id FROM wordchain WHERE channel_id = %s"
    params = (channel_id,)
    result = await execute_query(query, params)
    return result[0][0] if result else None


async def clear_wordchain(channel_id: int | str | int) -> None:
    query = "DELETE FROM wordchain WHERE channel_id = %s"
    params = (channel_id,)
    await execute_action(query, params)


async def set_level_system_status(guild_id: int | str | int, active: bool) -> None:
    query = """
    INSERT INTO levelConfig (guild_id, active)
    VALUES (%s, %s)
    ON DUPLICATE KEY UPDATE active = VALUES(active)
    """
    params = (guild_id, active)
    await execute_action(query, params)


async def get_level_system_status(guild_id: int | str | int) -> bool:
    query = "SELECT active FROM levelConfig WHERE guild_id = %s"
    params = (guild_id,)
    result = await execute_query(query, params)
    return result[0][0] if result else True


async def delete_level_system_data(guild_id: int | str | int) -> None:
    tables = [
        "level",
        "blacklistedUser",
        "blacklistedRole",
        "blacklistedChannel",
        "userXpBoost",
        "roleXpBoost",
        "channelXpBoost",
        "levelRole",
        "levelConfig",
    ]
    for table in tables:
        query = f"DELETE FROM {table} WHERE guild_id = %s"
        params = (guild_id,)
        await execute_action(query, params)


async def set_levelup_message_status(guild_id: int | str | int, status: bool) -> None:
    query = """
    INSERT INTO levelConfig (guild_id, levelUpMessageActive)
    VALUES (%s, %s)
    ON DUPLICATE KEY UPDATE levelUpMessageActive = VALUES(levelUpMessageActive)
    """
    params = (guild_id, status)
    await execute_action(query, params)


async def get_levelup_message_status(guild_id: int | str | int) -> bool:
    query = "SELECT levelUpMessageActive FROM levelConfig WHERE guild_id = %s"
    params = (guild_id,)
    result = await execute_query(query, params)
    return result[0][0] if result else True  # DEFAULT to True if no record exists


async def set_levelup_message(guild_id: int | str | int, message: str) -> None:
    query = """
    INSERT INTO levelConfig (guild_id, levelUpMessage)
    VALUES (%s, %s)
    ON DUPLICATE KEY UPDATE levelUpMessage = VALUES(levelUpMessage)
    """
    params = (guild_id, message)
    await execute_action(query, params)


async def get_levelup_message(guild_id: int | str | int) -> str | None:
    query = "SELECT levelUpMessage FROM levelConfig WHERE guild_id = %s"
    params = (guild_id,)
    result = await execute_query(query, params)
    return result[0][0] if result else None


async def set_levelup_channel(guild_id: int | str | int, channel_id: int | str | int | None) -> None:
    query = """
    INSERT INTO levelConfig (guild_id, levelUpChannelId)
    VALUES (%s, %s)
    ON DUPLICATE KEY UPDATE levelUpChannelId = VALUES(levelUpChannelId)
    """
    params = (guild_id, channel_id)
    await execute_action(query, params)


async def get_levelup_channel(guild_id: int | str | int) -> str | None:
    query = "SELECT levelUpChannelId FROM levelConfig WHERE guild_id = %s"
    params = (guild_id,)
    result = await execute_query(query, params)
    return result[0][0] if result else None


async def set_xp_scaling(guild_id: int | str | int, scaling: str) -> None:
    query = """
    INSERT INTO levelConfig (guild_id, difficulty)
    VALUES (%s, %s)
    ON DUPLICATE KEY UPDATE difficulty = VALUES(difficulty)
    """
    params = (guild_id, scaling)
    await execute_action(query, params)


async def get_xp_scaling(guild_id: int | str | int) -> str:
    query = "SELECT difficulty FROM levelConfig WHERE guild_id = %s"
    params = (guild_id,)
    result = await execute_query(query, params)
    return result[0][0] if result else "medium"


async def set_custom_formula(guild_id: int | str | int, formula: str) -> None:
    query = """
    INSERT INTO levelConfig (guild_id, customFormula)
    VALUES (%s, %s)
    ON DUPLICATE KEY UPDATE customFormula = VALUES(customFormula)
    """
    params = (guild_id, formula)
    await execute_action(query, params)


async def get_custom_formula(guild_id: int | str | int) -> str | None:
    query = "SELECT customFormula FROM levelConfig WHERE guild_id = %s"
    params = (guild_id,)
    result = await execute_query(query, params)
    return result[0][0] if result else None


async def add_level_role(guild_id: int | str | int, role_id: int | str | int, level: int) -> None:
    query = """
    INSERT INTO levelRole (guild_id, role_id, level)
    VALUES (%s, %s, %s)
    ON DUPLICATE KEY UPDATE role_id = VALUES(role_id)
    """
    params = (guild_id, role_id, level)
    await execute_action(query, params)


async def get_level_roles(guild_id: int | str | int) -> list[tuple[Any, ...]]:
    query = "SELECT level, role_id FROM levelRole WHERE guild_id = %s"
    params = (guild_id,)
    result = await execute_query(query, params)
    return result if result else []


async def get_level_role(guild_id: int | str | int, role_id: int | str | int) -> int | None:
    query = "SELECT level FROM levelRole WHERE guild_id = %s AND role_id = %s"
    params = (guild_id, role_id)
    result = await execute_query(query, params)
    return result[0][0] if result else None


async def remove_level_role(guild_id: int | str | int, role_id: int | str | int) -> None:
    query = """
    DELETE FROM levelRole
    WHERE guild_id = %s AND role_id = %s
    """
    params = (guild_id, role_id)
    await execute_action(query, params)


async def get_all_level_roles(guild_id: int | str | int) -> dict[int, list[str]]:
    query = "SELECT level, role_id FROM levelRole WHERE guild_id = %s ORDER BY level"
    params = (guild_id,)
    result = await execute_query(query, params)
    level_roles: dict[int, list[str]] = {}
    if result:
        for level, role_id in result:
            if level not in level_roles:
                level_roles[level] = []
            level_roles[level].append(role_id)
    return level_roles


async def add_role_boost(guild_id: int | str | int, role_id: int | str | int, boost: float, additive: bool) -> None:
    query = """
    INSERT INTO roleXpBoost (guild_id, role_id, boost, additive)
    VALUES (%s, %s, %s, %s)
    ON DUPLICATE KEY UPDATE boost = VALUES(boost), additive = VALUES(additive)
    """
    params = (guild_id, role_id, boost, additive)
    await execute_action(query, params)


async def add_channel_boost(guild_id: int | str | int, channel_id: int | str | int, boost: float, additive: bool) -> None:
    query = """
    INSERT INTO channelXpBoost (guild_id, channel_id, boost, additive)
    VALUES (%s, %s, %s, %s)
    ON DUPLICATE KEY UPDATE boost = VALUES(boost), additive = VALUES(additive)
    """
    params = (guild_id, channel_id, boost, additive)
    await execute_action(query, params)


async def add_user_boost(guild_id: int | str | int, user_id: int | str | int, boost: float, additive: bool) -> None:
    query = """
    INSERT INTO userXpBoost (guild_id, user_id, boost, additive)
    VALUES (%s, %s, %s, %s)
    ON DUPLICATE KEY UPDATE boost = VALUES(boost), additive = VALUES(additive)
    """
    params = (guild_id, user_id, boost, additive)
    await execute_action(query, params)


async def remove_role_boost(guild_id: int | str | int, role_id: int | str | int) -> None:
    query = "DELETE FROM roleXpBoost WHERE guild_id = %s AND role_id = %s"
    params = (guild_id, role_id)
    await execute_action(query, params)


async def remove_channel_boost(guild_id: int | str | int, channel_id: int | str | int) -> None:
    query = "DELETE FROM channelXpBoost WHERE guild_id = %s AND channel_id = %s"
    params = (guild_id, channel_id)
    await execute_action(query, params)


async def remove_user_boost(guild_id: int | str | int, user_id: int | str | int) -> None:
    query = "DELETE FROM userXpBoost WHERE guild_id = %s AND user_id = %s"
    params = (guild_id, user_id)
    await execute_action(query, params)


async def get_all_boosts(guild_id: int | str | int) -> dict[str, list[tuple[Any, ...]]]:
    role_query = "SELECT role_id, boost, additive FROM roleXpBoost WHERE guild_id = %s"
    channel_query = "SELECT channel_id, boost, additive FROM channelXpBoost WHERE guild_id = %s"
    user_query = "SELECT user_id, boost, additive FROM userXpBoost WHERE guild_id = %s"

    roles = await execute_query(role_query, (guild_id,))
    channels = await execute_query(channel_query, (guild_id,))
    users = await execute_query(user_query, (guild_id,))

    return {"roles": roles or [], "channels": channels or [], "users": users or []}


async def get_user_boost(guild_id: int | str | int, user_id: int | str | int) -> tuple[Any, ...] | None:
    query = "SELECT boost, additive FROM userXpBoost WHERE guild_id = %s AND user_id = %s"
    params = (guild_id, user_id)
    result = await execute_query(query, params)
    return result[0] if result else None


async def get_user_roles_boosts(guild_id: int | str | int, role_ids: list[str]) -> list[tuple[Any, ...]]:
    if not role_ids:
        return []
    query = "SELECT boost, additive FROM roleXpBoost WHERE guild_id = %s AND role_id IN %s"
    params = (guild_id, tuple(role_ids))
    result = await execute_query(query, params)
    return result if result else []


async def get_channel_boost(guild_id: int | str | int, channel_id: int | str | int) -> tuple[Any, ...] | None:
    query = "SELECT boost, additive FROM channelXpBoost WHERE guild_id = %s AND channel_id = %s"
    params = (guild_id, channel_id)
    result = await execute_query(query, params)
    return result[0] if result else None


async def add_channel_to_blacklist(guild_id: int | str | int, channel_id: int | str | int, reason: str | None = None) -> None:
    query = """
    INSERT INTO blacklistedChannel (guild_id, channel_id, reason)
    VALUES (%s, %s, %s)
    ON DUPLICATE KEY UPDATE reason = VALUES(reason)
    """
    params = (guild_id, channel_id, reason)
    await execute_action(query, params)


async def remove_channel_from_blacklist(guild_id: int | str | int, channel_id: int | str | int) -> None:
    query = "DELETE FROM blacklistedChannel WHERE guild_id = %s AND channel_id = %s"
    params = (guild_id, channel_id)
    await execute_action(query, params)


async def add_role_to_blacklist(guild_id: int | str | int, role_id: int | str | int, reason: str | None = None) -> None:
    query = """
    INSERT INTO blacklistedRole (guild_id, role_id, reason)
    VALUES (%s, %s, %s)
    ON DUPLICATE KEY UPDATE reason = VALUES(reason)
    """
    params = (guild_id, role_id, reason)
    await execute_action(query, params)


async def remove_role_from_blacklist(guild_id: int | str | int, role_id: int | str | int) -> None:
    query = "DELETE FROM blacklistedRole WHERE guild_id = %s AND role_id = %s"
    params = (guild_id, role_id)
    await execute_action(query, params)


async def add_user_to_blacklist(guild_id: int | str | int, user_id: int | str | int, reason: str | None = None) -> None:
    query = """
    INSERT INTO blacklistedUser (guild_id, user_id, reason)
    VALUES (%s, %s, %s)
    ON DUPLICATE KEY UPDATE reason = VALUES(reason)
    """
    params = (guild_id, user_id, reason)
    await execute_action(query, params)


async def remove_user_from_blacklist(guild_id: int | str | int, user_id: int | str | int) -> None:
    query = "DELETE FROM blacklistedUser WHERE guild_id = %s AND user_id = %s"
    params = (guild_id, user_id)
    await execute_action(query, params)


async def get_blacklist(guild_id: int | str | int) -> dict[str, list[tuple[Any, ...]]]:
    channels_query = "SELECT channel_id, reason FROM blacklistedChannel WHERE guild_id = %s"
    roles_query = "SELECT role_id, reason FROM blacklistedRole WHERE guild_id = %s"
    users_query = "SELECT user_id, reason FROM blacklistedUser WHERE guild_id = %s"

    channels = await execute_query(channels_query, (guild_id,))
    roles = await execute_query(roles_query, (guild_id,))
    users = await execute_query(users_query, (guild_id,))

    return {"channels": channels or [], "roles": roles or [], "users": users or []}


async def get_user_level_info(guild_id: int | str, user_id: int | str) -> dict[str, Any] | None:
    query = """
    SELECT xp, customBackground FROM level
    WHERE guild_id = %s AND user_id = %s
    """
    params = (guild_id, user_id)
    result = await execute_query(query, params)
    scaling = await get_xp_scaling(guild_id)
    custom_formula = await get_custom_formula(guild_id)
    if result:
        xp, custom_background = result[0]
        level = get_level_for_xp(xp, scaling, custom_formula)
        xp_needed = get_xp_for_level(level, scaling, custom_formula)
        xp_for_last_level_needed = get_xp_for_level(level - 1, scaling, custom_formula)
        return {
            "xp": xp - xp_for_last_level_needed,
            "level": level,
            "xp_needed": xp_needed,
            "customBackground": custom_background,
        }
    return None


async def set_custom_background(guild_id: int | str, user_id: int | str, background_url: str) -> None:
    query = """
    INSERT INTO level (guild_id, user_id, customBackground)
    VALUES (%s, %s, %s)
    ON DUPLICATE KEY UPDATE customBackground = VALUES(customBackground)
    """
    params = (guild_id, user_id, background_url)
    await execute_action(query, params)


async def get_user_xp(guild_id: int | str, user_id: int | str) -> int | None:
    query = "SELECT xp FROM level WHERE guild_id = %s AND user_id = %s"
    params = (guild_id, user_id)
    result = await execute_query(query, params)
    return result[0][0] if result else None


async def update_user_xp(guild_id: int | str, user_id: int | str, xp: int, respect_cooldown: bool = False) -> None:
    if respect_cooldown:
        query = """
    INSERT INTO level (guild_id, user_id, xp, last_xp_gain)
    VALUES (%s, %s, %s, NOW())
    ON DUPLICATE KEY UPDATE
        xp = CASE
            WHEN TIMESTAMPDIFF(SECOND, last_xp_gain, NOW()) >= GREATEST(1, COALESCE((SELECT textCooldown FROM levelConfig WHERE guild_id = %s), 1))
            THEN xp + %s
            ELSE xp
        END,
        last_xp_gain = CASE
            WHEN TIMESTAMPDIFF(SECOND, last_xp_gain, NOW()) >= GREATEST(1, COALESCE((SELECT textCooldown FROM levelConfig WHERE guild_id = %s), 1))
            THEN NOW()
            ELSE last_xp_gain
        END;
        """
        params = cast(Any, (guild_id, user_id, xp, guild_id, xp, guild_id))
        await execute_action(query, params)
    else:
        query = "INSERT INTO level (guild_id, user_id, xp) VALUES (%s, %s, %s) ON DUPLICATE KEY UPDATE xp = xp + %s"
        params = (guild_id, user_id, xp, xp)
        await execute_action(query, params)


async def update_user_xp_from_voice(guild_id: int | str, user_id: int | str, xp: int, respect_cooldown: bool = False) -> None:
    if respect_cooldown:
        query = """
        INSERT INTO level (guild_id, user_id, xp, last_voice_xp_gain)
        VALUES (%s, %s, %s, NOW())
        ON DUPLICATE KEY UPDATE
            xp = CASE
                WHEN TIMESTAMPDIFF(SECOND, last_voice_xp_gain, NOW()) >= GREATEST(5, (SELECT voiceCooldown FROM levelConfig WHERE guild_id = %s))
                THEN xp + %s
                ELSE xp
            END,
            last_voice_xp_gain = CASE
                WHEN TIMESTAMPDIFF(SECOND, last_voice_xp_gain, NOW()) >= GREATEST(5, (SELECT voiceCooldown FROM levelConfig WHERE guild_id = %s))
                THEN NOW()
                ELSE last_voice_xp_gain
            END;
        """
        params = cast(Any, (guild_id, user_id, xp, guild_id, xp, guild_id))
        await execute_action(query, params)
    else:
        query = "INSERT INTO level (guild_id, user_id, xp) VALUES (%s, %s, %s) ON DUPLICATE KEY UPDATE xp = xp + %s"
        params = (guild_id, user_id, xp, xp)
        await execute_action(query, params)


async def add_giveaway(
    guild_id: int | str,
    title: str,
    description: str,
    winners: int,
    with_button: bool,
    channel_id: int | str,
    custom_name: str | None,
    sponsor: str | None,
    price: str | None,
    message: str | None,
    endtime: datetime,
    starttime: datetime | None,
    new_message_requirement: int | None,
    day_requirement: int | None,
    channel_requirements: dict[str, int],
    role_requirement: list[str],
    voice_requirement: int | None,
) -> int | None:
    query = """
    INSERT INTO giveaway (
        guildId, title, description, winners, withButton, customName, sponsor, price, message,
        endtime, starttime, newMessageRequirement, dayRequirement, voiceRequirement, channelId
    )
    VALUES (
        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
    )

    """
    params = (
        guild_id,
        title,
        description,
        winners,
        with_button,
        custom_name,
        sponsor,
        price,
        message,
        endtime,
        starttime,
        new_message_requirement,
        day_requirement,
        voice_requirement,
        channel_id,
    )
    giveawayId = await execute_insert_and_get_id(query, params)

    if giveawayId:
        query = """
        INSERT INTO giveawayChannelRequirement (giveawayId, channelId, amount)
        VALUES (%s, %s, %s)
        """
        for channel_id, amount in channel_requirements.items():
            params = cast(Any, (giveawayId, channel_id, amount))
            await execute_action(query, params)
        query = """
        INSERT INTO giveawayRoleRequirement (roleId, giveawayId)
        VALUES (%s, %s)
        """
        for role_id in role_requirement:
            params = cast(Any, (role_id, giveawayId))
            await execute_action(query, params)

    return giveawayId


async def set_giveaway_message_id(giveaway_id: int, message_id: int) -> None:
    query = "UPDATE giveaway SET messageId = %s WHERE giveawayId = %s"
    params = (message_id, giveaway_id)
    await execute_action(query, params)


async def get_giveaway(giveaway_id: int) -> tuple[Any, ...] | None:
    query = "SELECT * FROM giveaway WHERE giveawayId = %s"
    params = (giveaway_id,)
    result = await execute_query(query, params)
    return result[0] if result else None


async def get_giveaway_channel_requirements(giveaway_id: int) -> list[tuple[Any, ...]] | None:
    query = "SELECT channelId, amount FROM giveawayChannelRequirement WHERE giveawayId = %s"
    params = (giveaway_id,)
    result = await execute_query(query, params)
    return result


async def get_giveaway_role_requirements(giveaway_id: int) -> list[str]:
    query = "SELECT roleId FROM giveawayRoleRequirement WHERE giveawayId = %s"
    params = (giveaway_id,)
    result = await execute_query(query, params)
    return [row[0] for row in result] if result else []


async def set_giveaway_started(giveaway_id: int) -> None:
    query = "UPDATE giveaway SET started = 1 WHERE giveawayId = %s"
    params = (giveaway_id,)
    await execute_action(query, params)


async def set_giveaway_ended(giveaway_id: int) -> None:
    query = "UPDATE giveaway SET ended = 1 WHERE giveawayId = %s"
    params = (giveaway_id,)
    await execute_action(query, params)


async def delete_old_giveaways() -> None:
    query = "DELETE FROM giveaway WHERE ended = 1 AND endtime < NOW() - INTERVAL 1 WEEK"
    await execute_action(query)


async def get_giveaway_participants(giveaway_id: int) -> list[str]:
    query = "SELECT userId FROM giveawayParticipant WHERE giveawayId = %s"
    params = (giveaway_id,)
    result = await execute_query(query, params)
    return [row[0] for row in result] if result else []


async def get_new_messages(giveaway_id: int, user_id: int | str) -> int | None:
    query = "SELECT messages FROM giveawayNewMessage WHERE giveawayId = %s AND userId = %s"
    params = (giveaway_id, user_id)
    result = await execute_query(query, params)
    return result[0][0] if result else None


async def get_new_messages_channel(giveaway_id: int, channel_id: int | str, user_id: int | str) -> int | None:
    query = "SELECT amount FROM giveawayChannelMessages WHERE giveawayId = %s AND channelId = %s AND userId = %s"
    params = (giveaway_id, channel_id, user_id)
    result = await execute_query(query, params)
    return result[0][0] if result else None


async def get_voice_time(giveaway_id: int, user_id: int | str) -> int | None:
    query = "SELECT voiceMinutes FROM giveawayVoiceTime WHERE giveawayId = %s AND userId = %s"
    params = (giveaway_id, user_id)
    result = await execute_query(query, params)
    return result[0][0] if result else None


async def get_blacklisted_roles(guild_id: int | str) -> list[tuple[Any, ...]] | None:
    query = "SELECT roleId, reason FROM giveawayBlacklistedRole WHERE guildId = %s"
    params = (guild_id,)
    result = await execute_query(query, params)
    return result


async def check_if_user_blacklisted(guild_id: int | str, user_id: int | str) -> bool:
    query = "SELECT * FROM giveawayBlacklistedUser WHERE guildId = %s AND userId = %s"
    params = (guild_id, user_id)
    result = await execute_query(query, params)
    return bool(result and len(result) > 0)


async def check_if_giveaway_participant(giveaway_id: int, user_id: int | str) -> bool:
    query = "SELECT * FROM giveawayParticipant WHERE giveawayId = %s AND userId = %s"
    params = (giveaway_id, user_id)
    result = await execute_query(query, params)
    return bool(result and len(result) > 0)


async def remove_giveaway_participant(giveaway_id: int, user_id: int | str) -> None:
    query = "DELETE FROM giveawayParticipant WHERE giveawayId = %s AND userId = %s"
    params = (giveaway_id, user_id)
    await execute_action(query, params)


async def add_giveaway_participant(giveaway_id: int, user_id: int | str) -> None:
    query = "INSERT INTO giveawayParticipant (userId, giveawayId) VALUES (%s, %s)"
    params = (user_id, giveaway_id)
    await execute_action(query, params)


async def get_send_ready_giveaways() -> list[tuple[Any, ...]] | None:
    query = "SELECT giveawayId FROM giveaway WHERE started = 0 AND starttime < NOW()"
    result = await execute_query(query)
    return result


async def add_giveaway_voice_minutes_if_needed(user_id: int | str, guild_id: int | str) -> None:
    query = "SELECT giveawayId FROM giveaway WHERE guildId = %s AND voiceRequirement IS NOT NULL"
    params: tuple[Any, ...] = (guild_id,)
    result = await execute_query(query, params)
    if result:
        for giveaway_id in result:
            query = "INSERT INTO giveawayVoiceTime (giveawayId, userId, voiceMinutes) VALUES (%s, %s, 0) ON DUPLICATE KEY UPDATE voiceMinutes = voiceMinutes + 1"
            params = (giveaway_id[0], user_id)
            await execute_action(query, params)


async def add_giveaway_new_message_if_needed(user_id: int | str, guild_id: int | str) -> None:
    query = "SELECT giveawayId FROM giveaway WHERE guildId = %s AND newMessageRequirement IS NOT NULL"
    params: tuple[Any, ...] = (guild_id,)
    result = await execute_query(query, params)
    if result:
        for giveaway_id in result:
            query = "INSERT INTO giveawayNewMessage (giveawayId, userId, messages) VALUES (%s, %s, 0) ON DUPLICATE KEY UPDATE messages = messages + 1"
            params = (giveaway_id[0], user_id)
            await execute_action(query, params)


async def add_giveaway_new_message_channel_if_needed(user_id: int | str, guild_id: int | str, channel_id: int | str) -> None:
    query = "SELECT giveawayId FROM giveaway WHERE guildId = %s AND newMessageRequirement IS NOT NULL"
    params: tuple[Any, ...] = (guild_id,)
    result = await execute_query(query, params)
    if result:
        for giveaway_id in result:
            query = "INSERT INTO giveawayChannelMessages (giveawayId, channelId, userId, amount) VALUES (%s, %s, %s, 0) ON DUPLICATE KEY UPDATE amount = amount + 1"
            params = (giveaway_id[0], channel_id, user_id)
            await execute_action(query, params)


async def get_end_ready_giveaways() -> list[tuple[Any, ...]] | None:
    query = "SELECT giveawayId FROM giveaway WHERE ended = 0 AND endtime < NOW() AND started = 1 AND messageId <> 'pending'"
    result = await execute_query(query)
    return result


async def add_giveaway_blacklisted_user(guild_id: int | str, user_id: int | str) -> None:
    query = "INSERT INTO giveawayBlacklistedUser (guildId, userId) VALUES (%s, %s)"
    params = (guild_id, user_id)
    await execute_action(query, params)


async def add_giveaway_blacklisted_role(guild_id: int | str, role_id: int | str) -> None:
    query = "INSERT INTO giveawayBlacklistedRole (guildId, roleId) VALUES (%s, %s)"
    params = (guild_id, role_id)
    await execute_action(query, params)


async def remove_giveaway_blacklisted_user(guild_id: int | str, user_id: int | str) -> None:
    query = "DELETE FROM giveawayBlacklistedUser WHERE guildId = %s AND userId = %s"
    params = (guild_id, user_id)
    await execute_action(query, params)


async def remove_giveaway_blacklisted_role(guild_id: int | str, role_id: int | str) -> None:
    query = "DELETE FROM giveawayBlacklistedRole WHERE guildId = %s AND roleId = %s"
    params = (guild_id, role_id)
    await execute_action(query, params)


async def get_giveaway_blacklisted_users(guild_id: int | str) -> list[tuple[Any, ...]] | None:
    query = "SELECT userId, reason FROM giveawayBlacklistedUser WHERE guildId = %s"
    params = (guild_id,)
    result = await execute_query(query, params)
    return result


async def get_giveaway_blacklisted_roles(guild_id: int | str) -> list[tuple[Any, ...]] | None:
    query = "SELECT roleId, reason FROM giveawayBlacklistedRole WHERE guildId = %s"
    params = (guild_id,)
    result = await execute_query(query, params)
    return result


async def delete_giveaway(giveaway_id: int) -> None:
    query = "DELETE FROM giveaway WHERE giveawayId = %s"
    params = (giveaway_id,)
    await execute_action(query, params)


async def set_giveaway_endtime(giveaway_id: int, endtime: datetime) -> None:
    query = "UPDATE giveaway SET endtime = %s WHERE giveawayId = %s"
    params = (endtime, giveaway_id)
    await execute_action(query, params)


async def update_giveaway(
    giveaway_id: int,
    guild_id: int | str,
    title: str,
    description: str,
    winners: int,
    with_button: bool,
    custom_name: str | None,
    sponsor: str | None,
    price: str | None,
    message: str | None,
    endtime: datetime,
    starttime: datetime | None,
    new_message_requirement: int | None,
    day_requirement: int | None,
    channel_requirements: dict[str, int],
    role_requirement: list[str],
    voice_requirement: int | None,
    channel_id: int | str,
) -> None:
    query = """
    UPDATE giveaway SET
        guildId = %s,
        title = %s,
        description = %s,
        winners = %s,
        withButton = %s,
        customName = %s,
        sponsor = %s,
        price = %s,
        message = %s,
        endtime = %s,
        starttime = %s,
        newMessageRequirement = %s,
        dayRequirement = %s,
        voiceRequirement = %s,
        channelId = %s
    WHERE giveawayId = %s
    """
    params: tuple[Any, ...] = (
        guild_id,
        title,
        description,
        winners,
        with_button,
        custom_name,
        sponsor,
        price,
        message,
        endtime,
        starttime,
        new_message_requirement,
        day_requirement,
        voice_requirement,
        channel_id,
        giveaway_id,
    )
    await execute_action(query, params)

    await execute_action(
        "DELETE FROM giveawayChannelRequirement WHERE giveawayId = %s",
        (giveaway_id,),
    )
    if channel_requirements is not None and len(channel_requirements) > 0 and channel_requirements != {}:
        for channel_id, amount in channel_requirements.items():
            query = "INSERT INTO giveawayChannelRequirement (giveawayId, channelId, amount) VALUES (%s, %s, %s)"
            params = (giveaway_id, channel_id, amount)
            await execute_action(query, params)

    await execute_action(
        "DELETE FROM giveawayRoleRequirement WHERE giveawayId = %s",
        (giveaway_id,),
    )
    for role_id in role_requirement:
        query = "INSERT INTO giveawayRoleRequirement (roleId, giveawayId) VALUES (%s, %s)"
        params = (role_id, giveaway_id)
        await execute_action(query, params)


async def set_text_cooldown(guild_id: int | str, cooldown: int) -> None:
    query = """
    INSERT INTO levelConfig (guild_id, textCooldown)
    VALUES (%s, %s)
    ON DUPLICATE KEY UPDATE textCooldown = VALUES(textCooldown)
    """
    params = (guild_id, cooldown)
    await execute_action(query, params)


async def set_voice_cooldown(guild_id: int | str, cooldown: int) -> None:
    query = """
    INSERT INTO levelConfig (guild_id, voiceCooldown)
    VALUES (%s, %s)
    ON DUPLICATE KEY UPDATE voiceCooldown = VALUES(voiceCooldown)
    """
    params = (guild_id, cooldown)
    await execute_action(query, params)


async def get_text_cooldown(guild_id: int | str) -> int:
    query = "SELECT textCooldown FROM levelConfig WHERE guild_id = %s"
    params = (guild_id,)
    result = await execute_query(query, params)
    return result[0][0] if result else 60  # Default to 60 seconds if not set


async def get_voice_cooldown(guild_id: int | str) -> int:
    query = "SELECT voiceCooldown FROM levelConfig WHERE guild_id = %s"
    params = (guild_id,)
    result = await execute_query(query, params)
    return result[0][0] if result else 60  # Default to 60 seconds if not set


async def useToken(user_id: int | str, amount: int) -> None:
    query = """
    UPDATE aiToken
    SET freeToken = CASE
                        WHEN freeToken >= %s THEN freeToken - %s
                        ELSE freeToken
                    END,
        usedToken = CASE
                        WHEN freeToken >= %s THEN usedToken + %s
                        ELSE usedToken
                    END
    WHERE userId = %s AND freeToken >= %s;
    UPDATE aiToken
    SET plusToken = CASE
                        WHEN freeToken < %s AND plusToken >= %s THEN plusToken - %s
                        ELSE plusToken
                    END,
        usedToken = CASE
                        WHEN freeToken < %s AND plusToken >= %s THEN usedToken + %s
                        ELSE usedToken
                    END
    WHERE userId = %s AND freeToken < %s AND plusToken >= %s;
    UPDATE aiToken
    SET paidToken = CASE
                        WHEN freeToken < %s AND plusToken < %s AND paidToken >= %s THEN paidToken - %s
                        ELSE paidToken
                    END,
        usedToken = CASE
                        WHEN freeToken < %s AND plusToken < %s AND paidToken >= %s THEN usedToken + %s
                        ELSE usedToken
                    END
    WHERE userId = %s AND freeToken < %s AND plusToken < %s AND paidToken >= %s;
    """
    params = (
        amount,
        amount,
        amount,
        amount,
        user_id,
        amount,
        amount,
        amount,
        amount,
        amount,
        amount,
        amount,
        user_id,
        amount,
        amount,
        amount,
        amount,
        amount,
        amount,
        amount,
        amount,
        amount,
        amount,
        user_id,
        amount,
        amount,
        amount,
    )

    await execute_action(query, params)


async def addToken(user_id: int | str, amount: int) -> None:
    query = """
    INSERT INTO aiToken (userId, paidToken)
    VALUES (%s, %s)
    ON DUPLICATE KEY
    UPDATE paidToken = paidToken + %s
    """
    params = (user_id, amount, amount)
    await execute_action(query, params)


async def getToken(user_id: int | str) -> int:
    query = "SELECT freeToken, plusToken, paidToken FROM aiToken WHERE userId = %s"
    params = (user_id,)
    result = await execute_query(query, params)
    token = result[0] if result else None
    tokenSum = token[0] + token[1] + token[2] if token else 0
    return tokenSum


async def getTokenOverview(user_id: int | str) -> tuple[Any, ...] | None:
    query = "SELECT freeToken, plusToken, paidToken, usedToken FROM aiToken WHERE userId = %s"
    params = (user_id,)
    result = await execute_query(query, params)
    return result[0] if result else None


async def includeToToken(user_id: int | str) -> None:
    query = "INSERT INTO aiToken (userId) VALUES (%s)"
    params = (user_id,)
    await execute_action(query, params)


class Entitlement:
    userId: str


async def resetToken(entitlements: list[Entitlement] | None = None) -> None:
    query = "UPDATE aiToken SET freeToken = 500"
    await execute_action(query)
    if entitlements is not None:
        for entitlement in entitlements:
            query = "UPDATE aiToken SET plusToken = 2000 WHERE userId = %s"
            params = entitlement.userId
            await execute_action(query, params)


async def consumePaidToken(user_id: int | str, amount: int) -> None:
    query = "UPDATE aiToken SET paidToken = paidToken + %s WHERE userId = %s"
    params = (amount, user_id)
    await execute_action(query, params)


async def getLevelLeaderboard(guild_id: int | str) -> list[tuple[Any, ...]] | None:
    query = "SELECT user_id, xp FROM level WHERE guild_id = %s ORDER BY xp DESC"
    params = (guild_id,)
    result = await execute_query(query, params)
    return result


async def addCustomSituation(
    user_id: int | str,
    situation: str,
    name: str,
    temperature: float,
    top_p: float,
    frequency_penalty: float,
    presence_penalty: float,
) -> int | None:
    query = """
    INSERT INTO aiSituations (userId, situation, name, temperature, top_p, frequency_penalty, presence_penalty)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    params = (
        user_id,
        situation,
        name,
        temperature,
        top_p,
        frequency_penalty,
        presence_penalty,
    )
    return await execute_action(query, params)


async def getCustomSituations() -> list[tuple[Any, ...]]:
    query = "SELECT name FROM aiSituations where unlocked = 1"
    result = await execute_query(query)
    return result if result else []


async def getCustomSituation(name: str) -> tuple[Any, ...] | None:
    query = "SELECT * FROM aiSituations WHERE name = %s"
    params = (name,)
    result = await execute_query(query, params)
    return result[0] if result else None


async def getCustomSituationFromUser(user_id: int | str) -> tuple[Any, ...] | None:
    query = "SELECT * FROM aiSituations WHERE userId = %s"
    params = (user_id,)
    result = await execute_query(query, params)
    return result[0] if result else None


async def deleteCustomSituation(user_id: int | str) -> None:
    query = "DELETE FROM aiSituations WHERE userId = %s"
    params = (user_id,)
    await execute_action(query, params)


async def unlockCustomSituation(user_id: int | str) -> None:
    query = "UPDATE aiSituations SET unlocked = 1 WHERE userId = %s"
    params = (user_id,)
    await execute_action(query, params)


async def addAutoPublish(channel_id: int | str) -> int | None:
    query = """
    INSERT INTO autopublish (channelId)
    VALUES (%s)
    """
    params = (channel_id,)
    return await execute_action(query, params)


async def checkIfChannelIsAutopublish(channel_id: int | str) -> bool:
    query = "SELECT * FROM autopublish WHERE channelId = %s"
    params = (channel_id,)
    result = await execute_query(query, params)
    return bool(result and len(result) > 0)


async def removeAutoPublish(channel_id: int | str) -> None:
    query = "DELETE FROM autopublish WHERE channelId = %s"
    params = (channel_id,)
    await execute_action(query, params)


async def feedbackBlockUser(user_id: int | str) -> None:
    query = "INSERT INTO feedbackBlocked (userId) VALUES (%s)"
    params = (user_id,)
    await execute_action(query, params)


async def feedbackUnblockUser(user_id: int | str) -> None:
    query = "DELETE FROM feedbackBlocked WHERE userId = %s"
    params = (user_id,)
    await execute_action(query, params)


async def feedbackIsBlocked(user_id: int | str) -> bool:
    query = "SELECT * FROM feedbackBlocked WHERE userId = %s"
    params = (user_id,)
    result = await execute_query(query, params)
    return bool(result and len(result) > 0)


async def setAfk(user_id: int | str, reason: str) -> None:
    query = """
    INSERT INTO afkUsers (userId, reason)
    VALUES (%s, %s)
    """
    params = (user_id, reason)
    await execute_action(query, params)


async def removeAfk(user_id: int | str) -> None:
    query = "DELETE FROM afkUsers WHERE userId = %s"
    params = (user_id,)
    await execute_action(query, params)
    query = "DELETE FROM afkMessages WHERE userId = %s"
    await execute_action(query, params)


async def checkIfUserIsAfk(user_id: int | str) -> bool:
    query = "SELECT * FROM afkUsers WHERE userId = %s"
    params = (user_id,)
    result = await execute_query(query, params)
    return bool(result and len(result) > 0)


async def addAfkMessage(user_id: int | str, message_id: str, channel_id: int | str) -> None:
    query = """
    INSERT INTO afkMessages (userId, messageId, channelId)
    VALUES (%s, %s, %s)
    """
    params = (user_id, message_id, channel_id)
    await execute_action(query, params)


async def getAfkMessages(user_id: int | str) -> list[tuple[Any, ...]] | None:
    query = "SELECT messageId, channelId FROM afkMessages WHERE userId = %s"
    params = (user_id,)
    result = await execute_query(query, params)
    return result


async def getAfkReason(user_id: int | str) -> str | None:
    query = "SELECT reason FROM afkUsers WHERE userId = %s"
    params = (user_id,)
    result = await execute_query(query, params)
    return result[0][0] if result else None


async def add_booster_channel(guild_id: int | str, channel_id: int | str) -> None:
    query = "INSERT INTO boosterChannel (guildId, channelId) VALUES (%s, %s)"
    params = (guild_id, channel_id)
    await execute_action(query, params)


async def delete_booster_channel(guild_id: int | str, channel_id: int | str) -> None:
    query = "DELETE FROM boosterChannel WHERE guildId = %s AND channelId = %s"
    params = (guild_id, channel_id)
    await execute_action(query, params)


async def get_booster_channel(guild_id: int | str) -> str | None:
    query = "SELECT channelId FROM boosterChannel WHERE guildId = %s"
    params = (guild_id,)
    result = await execute_query(query, params)
    return result[0][0] if result else None


async def claim_booster_channel(user_id: int | str, channel_id: int | str, guild_id: int | str) -> None:
    query = "INSERT INTO claimedBoosterChannel (userId, channelId, guildId) VALUES (%s, %s, %s)"
    params = (user_id, channel_id, guild_id)
    await execute_action(query, params)


async def remove_claimed_booster_channel(user_id: int | str, guild_id: int | str) -> None:
    query = "DELETE FROM claimedBoosterChannel WHERE userId = %s AND guildId = %s"
    params = (user_id, guild_id)
    await execute_action(query, params)


async def get_claimed_booster_channel(
    user_id: str | None = None, guild_id: int | str| None = None
) -> str | list[tuple[Any, ...]] | None:
    if user_id:
        query = (
            "SELECT channelId FROM claimedBoosterChannel WHERE userId = %s AND guildId = %s"
            if guild_id
            else "SELECT * FROM claimedBoosterChannel WHERE userId = %s"
        )
        params = (user_id, guild_id) if guild_id else (user_id,)
        result = await execute_query(query, params)
        return result[0][0] if result else None
    else:
        query = "SELECT * FROM claimedBoosterChannel"
        result = await execute_query(query)
        return result if result else []


async def add_booster_role(guild_id: int | str, role_id: int | str) -> None:
    query = "INSERT INTO boosterRole (guildId, roleId) VALUES (%s, %s)"
    params = (guild_id, role_id)
    await execute_action(query, params)


async def get_booster_role(guild_id: int | str) -> str | None:
    query = "SELECT roleId FROM boosterRole WHERE guildId = %s"
    params = (guild_id,)
    result = await execute_query(query, params)
    return result[0][0] if result else None


async def delete_booster_role(guild_id: int | str) -> None:
    query = "DELETE FROM boosterRole WHERE guildId = %s"
    params = (guild_id,)
    await execute_action(query, params)


async def add_claimed_booster_role(user_id: int | str, role_id: int | str, guild_id: int | str) -> None:
    query = "INSERT INTO claimedBoosterRole (userId, roleId, guildId) VALUES (%s, %s, %s)"
    params = (user_id, role_id, guild_id)
    await execute_action(query, params)


async def remove_claimed_booster_role(user_id: int | str, guild_id: int | str) -> None:
    query = "DELETE FROM claimedBoosterRole WHERE userId = %s AND guildId = %s"
    params = (user_id, guild_id)
    await execute_action(query, params)


async def get_claimed_booster_role(
    user_id: int | str | None = None, guild_id: int | str| None = None
) -> str | list[tuple[Any, ...]] | None:
    if user_id:
        query = (
            "SELECT roleId FROM claimedBoosterRole WHERE userId = %s AND guildId = %s"
            if guild_id
            else "SELECT * FROM claimedBoosterRole WHERE userId = %s"
        )
        params = (user_id, guild_id) if guild_id else (user_id,)
        result = await execute_query(query, params)
        return result[0][0] if result else None
    else:
        query = "SELECT * FROM claimedBoosterRole"
        result = await execute_query(query)
        return result if result else []


async def set_log_channel(guild_id: int | str, channel_id: int | str) -> None:
    query = "INSERT INTO logChannel (guildId, channelId) VALUES (%s, %s)"
    params: tuple[Any, ...] = (guild_id, channel_id)
    if len(await get_log_enable(guild_id)) == 35:
        query = "REPLACE INTO logEnables (guildId) VALUES (%s)"
        params = (guild_id,)
    await execute_action(query, params)


async def remove_log_channel(guild_id: int | str) -> None:
    query = "DELETE FROM logChannel WHERE guildId = %s"
    params = (guild_id,)
    await execute_action(query, params)


async def add_log_blacklist_channel(guild_id: int | str, channel_id: int | str) -> None:
    query = "INSERT INTO logBlacklistChannel (guildId, channelId) VALUES (%s, %s)"
    params = (guild_id, channel_id)
    await execute_action(query, params)


async def remove_log_blacklist_channel(guild_id: int | str, channel_id: int | str) -> None:
    query = "DELETE FROM logBlacklistChannel WHERE guildId = %s AND channelId = %s"
    params = (guild_id, channel_id)
    await execute_action(query, params)


async def get_log_blacklist_channel(guild_id: int | str) -> list[tuple[Any, ...]]:
    query = "SELECT channelId FROM logBlacklistChannel WHERE guildId = %s"
    params = (guild_id,)
    result = await execute_query(query, params)
    return result if result else []


async def is_log_channel_blacklisted(guild_id: int | str, channel_id: int | str) -> tuple[Any, ...] | None:
    query = "SELECT channelId FROM logBlacklistChannel WHERE guildId = %s AND channelId = %s"
    params = (guild_id, channel_id)
    result = await execute_query(query, params)
    return result[0] if result else None


async def add_log_role_blacklist(guild_id: int | str, role_id: int | str) -> None:
    query = "INSERT INTO logRoleBlacklist (guildId, roleId) VALUES (%s, %s)"
    params = (guild_id, role_id)
    await execute_action(query, params)


async def remove_log_role_blacklist(guild_id: int | str, role_id: int | str) -> None:
    query = "DELETE FROM logRoleBlacklist WHERE guildId = %s AND roleId = %s"
    params = (guild_id, role_id)
    await execute_action(query, params)


async def get_log_role_blacklist(guild_id: int | str) -> list[tuple[Any, ...]]:
    query = "SELECT roleId FROM logRoleBlacklist WHERE guildId = %s"
    params = (guild_id,)
    result = await execute_query(query, params)
    return result if result else []


async def is_log_role_blacklisted(guild_id: int | str, role_id: int | str) -> tuple[Any, ...] | None:
    query = "SELECT roleId FROM logRoleBlacklist WHERE guildId = %s AND roleId = %s"
    params = (guild_id, role_id)
    result = await execute_query(query, params)
    return result[0] if result else None


async def add_log_user_blacklist(guild_id: int | str, user_id: int | str) -> None:
    query = "INSERT INTO logUserBlacklist (guildId, userId) VALUES (%s, %s)"
    params = (guild_id, user_id)
    await execute_action(query, params)


async def remove_log_user_blacklist(guild_id: int | str, user_id: int | str) -> None:
    query = "DELETE FROM logUserBlacklist WHERE guildId = %s AND userId = %s"
    params = (guild_id, user_id)
    await execute_action(query, params)


async def get_log_user_blacklist(guild_id: int | str) -> list[tuple[Any, ...]]:
    query = "SELECT userId FROM logUserBlacklist WHERE guildId = %s"
    params = (guild_id,)
    result = await execute_query(query, params)
    return result if result else []


async def is_log_user_blacklisted(guild_id: int | str, user_id: int | str) -> tuple[Any, ...] | None:
    query = "SELECT userId FROM logUserBlacklist WHERE guildId = %s AND userId = %s"
    params = (guild_id, user_id)
    result = await execute_query(query, params)
    return result[0] if result else None


async def get_log_channel(guild_id: int | str) -> str | None:
    query = "SELECT channelId FROM logChannel WHERE guildId = %s"
    params = (guild_id,)
    print("query: ", query)
    print("params: ", params)
    result = await execute_query(query, params)
    return result[0][0] if result else None


async def set_log_enable(guild_id: int | str, **kwargs: bool | None) -> None:
    query = "UPDATE logEnables SET "
    end_query = " WHERE guildId = %s"
    params: list[Any] = []

    for key, value in kwargs.items():
        if value is not None:
            query += f"{key} = %s, "
            params.append(value)

    if not params:
        return

    params.append(guild_id)
    query = query.rstrip(", ") + end_query

    await execute_action(query, tuple(params))


async def get_log_enable(guild_id: int | str) -> tuple[Any, ...] | list[int]:
    query = "SELECT * FROM logEnables WHERE guildId = %s"
    params = (guild_id,)
    result = await execute_query(query, params)
    return result[0] if result and result[0] else [0 for _ in range(35)]


async def add_scheduled_message(
    guild_id: int | str| None,
    channel_id: int | str| None,
    user_id: int | str,
    content: str,
    send_time: datetime,
    repeat_interval: int | None = None,
    repeat_amount: int | None = None,
) -> None:
    query = """
    INSERT INTO scheduledMessages
    (guildId, channelId, userId, content, sendTime, repeatInterval, repeatAmount)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    params = (guild_id, channel_id, user_id, content, send_time, repeat_interval, repeat_amount)
    await execute_action(query, params)


async def get_scheduled_messages(user_id: int | str) -> list[tuple[Any, ...]] | None:
    query = """
    SELECT * FROM scheduledMessages
    WHERE userId = %s
    ORDER BY sendTime ASC
    """
    params = (user_id,)
    return await execute_query(query, params)


async def remove_scheduled_message(message_id: int) -> None:
    query = "DELETE FROM scheduledMessages WHERE messageId = %s"
    params = (message_id,)
    await execute_action(query, params)


async def get_user_scheduled_messages_in_timeframe(
    user_id: int | str,
    start_time: datetime,
    end_time: datetime,
    guild_id: int | str | None = None,
) -> list[tuple[Any, ...]] | None:
    query = """
    SELECT * FROM scheduledMessages
    WHERE userId = %s
    AND sendTime BETWEEN %s AND %s
    """
    params = [user_id, start_time, end_time]

    if guild_id:
        query += " AND guildId = %s"
        params.append(guild_id)

    return await execute_query(query, tuple(params))


async def update_scheduled_message_content(message_id: int, new_content: str) -> None:
    query = "UPDATE scheduledMessages SET content = %s WHERE referenceMessageId = %s"
    params = (new_content, message_id)
    await execute_action(query, params)


async def update_scheduled_message_repeat_amount(message_id: int, repeat_amount: int) -> None:
    query = "UPDATE scheduledMessages SET repeatAmount = %s WHERE referenceMessageId = %s"
    params = (repeat_amount, message_id)
    await execute_action(query, params)


async def get_ready_scheduled_messages() -> list[tuple[Any, ...]] | None:
    query = "SELECT * FROM scheduledMessages WHERE sendTime <= NOW()"
    res = await execute_query(query)
    return res


async def report_user(
    guild_id: int | str,
    user_id: int | str,
    reporter_id: int | str,
    reason: str,
    is_moderator: bool = False,
) -> int | None:
    if is_moderator:
        query = "INSERT INTO reports (guildId, userId, reporterId, reason, accepted, acceptedAt, acceptedBy) VALUES (%s, %s, %s, %s, %s, %s, %s)"
        params: tuple[Any, ...] = (
            guild_id,
            user_id,
            reporter_id,
            reason,
            1,
            datetime.now(),
            reporter_id,
        )
    else:
        query = "INSERT INTO reports (guildId, userId, reporterId, reason) VALUES (%s, %s, %s, %s)"
        params = (guild_id, user_id, reporter_id, reason)
    report_id = await execute_action(query, params)
    return report_id


async def accept_report(guild_id: int | str, report_id: int | str) -> None:
    query = "UPDATE reports SET accepted = 1, acceptedAt = NOW(), acceptedBy = %s WHERE id = %s"
    params = (guild_id, report_id)
    await execute_action(query, params)


async def reject_report(guild_id: int | str, report_id: str) -> None:
    query = "UPDATE reports SET accepted = 0, acceptedAt = NOW(), acceptedBy = %s WHERE id = %s"
    params = (guild_id, report_id)
    await execute_action(query, params)


async def resolve_report(guild_id: int | str, report_id: str) -> None:
    query = "UPDATE reports SET resolved = 1 WHERE guildId = %s AND id = %s"
    params = (guild_id, report_id)
    await execute_action(query, params)


async def delete_report(guild_id: int | str, report_id: str) -> None:
    query = "DELETE FROM reports WHERE guildId = %s AND id = %s"
    params = (guild_id, report_id)
    await execute_action(query, params)


async def get_reports(guild_id: int | str, user_id: str | None = None) -> list[tuple[Any, ...]]:
    query = """
        SELECT id, guildId, userId, reporterId, reason,
               UNIX_TIMESTAMP(createdAt) as createdAt,
               accepted,
               UNIX_TIMESTAMP(acceptedAt) as acceptedAt,
               acceptedBy,
               resolved,
               UNIX_TIMESTAMP(resolvedAt) as resolvedAt,
               resolvedBy
        FROM reports WHERE guildId = %s
    """
    params = [guild_id]
    if user_id:
        query += " AND userId = %s"
        params.append(user_id)

    result = await execute_query(query, tuple(params))
    return result if result else []


async def get_reports_by_reporter(guild_id: int | str, reporter_id: int | str) -> list[tuple[Any, ...]] | None:
    query = "SELECT * FROM reports WHERE guildId = %s AND reporterId = %s"
    params = (guild_id, reporter_id)
    return await execute_query(query, params)


async def block_reporter(guild_id: int | str, reporter_id: int | str) -> None:
    query = "INSERT INTO blockedReporters (guildId, userId) VALUES (%s, %s)"
    params = (guild_id, reporter_id)
    await execute_action(query, params)


async def unblock_reporter(guild_id: int | str, reporter_id: int | str) -> None:
    query = "DELETE FROM blockedReporters WHERE guildId = %s AND userId = %s"
    params = (guild_id, reporter_id)
    await execute_action(query, params)


async def get_blocked_reporters(guild_id: int | str) -> list[tuple[Any, ...]] | None:
    query = "SELECT * FROM blockedReporters WHERE guildId = %s"
    params = (guild_id,)
    return await execute_query(query, params)


async def check_if_reporter_is_blocked(guild_id: int | str, reporter_id: int | str) -> list[tuple[Any, ...]] | None:
    query = "SELECT * FROM blockedReporters WHERE guildId = %s AND userId = %s"
    params = (guild_id, reporter_id)
    return await execute_query(query, params)


async def get_report_channel(guild_id: int | str) -> tuple[Any, ...] | None:
    query = "SELECT channelId FROM reportchannel WHERE guildId = %s"
    params = (guild_id,)
    result = await execute_query(query, params)
    return result[0] if result else None


async def set_report_channel(guild_id: int | str, channel_id: int | str) -> None:
    query = "INSERT INTO reportchannel (guildId, channelId) VALUES (%s, %s)"
    params = (guild_id, channel_id)
    await execute_action(query, params)


async def remove_report_channel(guild_id: int | str) -> None:
    query = "DELETE FROM reportchannel WHERE guildId = %s"
    params = (guild_id,)
    await execute_action(query, params)


async def get_trigger_messages(guild_id: int | str) -> list[tuple[Any, ...]] | None:
    query = "SELECT * FROM triggerMessages WHERE guildId = %s"
    params = (guild_id,)
    return await execute_query(query, params)


async def add_trigger_message(guild_id: int | str, trigger: str, response: str, caseSensitive: bool = False) -> None:
    query = "INSERT INTO triggerMessages (guildId, `trigger`, response, caseSensitive) VALUES (%s, %s, %s, %s)"
    params = (guild_id, trigger, response, caseSensitive)
    await execute_action(query, params)


async def remove_trigger_message(guild_id: int | str, trigger: str) -> None:
    query = "DELETE FROM triggerMessages WHERE guildId = %s AND `trigger` = %s"
    params = (guild_id, trigger)
    await execute_action(query, params)


async def get_trigger_message_channels(guild_id: int | str, trigger_id: int) -> list[tuple[Any, ...]] | None:
    query = "SELECT * FROM triggerMessagesChannel WHERE guildId = %s AND triggerId = %s"
    params = (guild_id, trigger_id)
    return await execute_query(query, params)


async def get_trigger_messages_by_channel(guild_id: int | str, channel_id: int | str) -> list[tuple[Any, ...]] | None:
    query = "SELECT * FROM triggerMessagesChannel WHERE guildId = %s AND channelId = %s"
    params = (guild_id, channel_id)
    return await execute_query(query, params)


async def add_trigger_message_channel(guild_id: int | str, channel_id: int | str, trigger_id: int) -> None:
    query = "INSERT INTO triggerMessagesChannel (guildId, channelId, triggerId) VALUES (%s, %s, %s)"
    params = (guild_id, channel_id, trigger_id)
    await execute_action(query, params)


async def remove_trigger_message_channel(guild_id: int | str, channel_id: int | str, trigger_id: int) -> None:
    query = "DELETE FROM triggerMessagesChannel WHERE guildId = %s AND channelId = %s AND triggerId = %s"
    params = (guild_id, channel_id, trigger_id)
    await execute_action(query, params)


async def is_trigger_message(guild_id: int | str, trigger: str, channel_id: int | str) -> tuple[Any, ...] | None | None:
    query = """
        SELECT t.* FROM triggerMessages t
        LEFT JOIN triggerMessagesChannel tc ON t.id = tc.triggerId AND t.guildId = tc.guildId
        WHERE t.guildId = %s AND t.`trigger` LIKE %s
        AND (tc.channelId = %s)
    """
    params = (guild_id, trigger, channel_id)
    res = await execute_query(query, params)
    result = res[0] if res and res[0] else None
    if not result:
        return None
    if result[4]:  # caseSensitive check
        if trigger != result[2]:
            return None
    else:
        if trigger.lower() != str(result[2]).lower():
            return None
    return result


async def create_ticket_message(
    guild_id: int | str,
    channel_id: int | str,
    introduction: str,
    ping_role: str,
    name: str,
    description: str,
    summary_channel_id: int | str,
) -> int | None:
    query = "INSERT INTO ticketMessages (guildId, channelId, introduction, pingRole, name, description, summaryChannelId) VALUES (%s, %s, %s, %s, %s, %s, %s)"
    params = (
        guild_id,
        channel_id,
        introduction,
        ping_role,
        name,
        description,
        summary_channel_id,
    )
    return await execute_insert_and_get_id(query, params)


async def delete_ticket_message(guild_id: int | str, ticket_message_id: str) -> None:
    query = "DELETE FROM ticketMessages WHERE guildId = %s AND id = %s"
    params = (guild_id, ticket_message_id)
    await execute_action(query, params)


async def get_ticket_messages(guild_id: int | str) -> list[tuple[Any, ...]] | None:
    query = "SELECT * FROM ticketMessages WHERE guildId = %s"
    params = (guild_id,)
    return await execute_query(query, params)


async def get_ticket_messages_by_id(ticket_message_id: str) -> tuple[Any, ...] | None | None:
    query = "SELECT * FROM ticketMessages WHERE id = %s"
    params = (ticket_message_id,)
    res = await execute_query(query, params)
    return res[0] if res else None


async def open_ticket(guild_id: int | str, opener_id: str, ticket_message_id: str, channel_id: int | str) -> None:
    query = "INSERT INTO tickets (guildId, openerId, ticketMessageId, channelId) VALUES (%s, %s, %s, %s)"
    params = (guild_id, opener_id, ticket_message_id, channel_id)
    await execute_action(query, params)


async def close_ticket(guild_id: int | str, ticket_id: str) -> None:
    query = "UPDATE tickets SET closed = 1, closedAt = NOW(), closedBy = %s WHERE guildId = %s AND id = %s"
    params = (guild_id, ticket_id)
    await execute_action(query, params)


async def get_tickets(guild_id: int | str) -> list[tuple[Any, ...]] | None:
    query = """
        SELECT guildId, openerId,
               UNIX_TIMESTAMP(openedAt) as openedAt,
               closed,
               UNIX_TIMESTAMP(closedAt) as closedAt,
               closedBy, channelId, ticketMessageId
        FROM tickets WHERE guildId = %s
    """
    params = (guild_id,)
    return await execute_query(query, params)


async def get_ticket_by_id(guild_id: int | str, ticket_id: str, channel_id: int | str) -> tuple[Any, ...] | None:
    query = """
        SELECT guildId, openerId,
               UNIX_TIMESTAMP(openedAt) as openedAt,
               closed,
               UNIX_TIMESTAMP(closedAt) as closedAt,
               closedBy, channelId, ticketMessageId
        FROM tickets
        WHERE guildId = %s AND ticketMessageId = %s AND channelId = %s
    """
    params = (guild_id, ticket_id, channel_id)
    result = await execute_query(query, params)
    return result[0] if result else None


async def get_ticket_by_channel_id(guild_id: int | str, channel_id: int | str) -> tuple[Any, ...] | None:
    query = """
        SELECT guildId, openerId,
               UNIX_TIMESTAMP(openedAt) as openedAt,
               closed,
               UNIX_TIMESTAMP(closedAt) as closedAt,
               closedBy, channelId, ticketMessageId
        FROM tickets
        WHERE guildId = %s AND channelId = %s
    """
    params = (guild_id, channel_id)
    result = await execute_query(query, params)
    return result[0] if result else None


async def get_join_to_create_channel(channel_id: int | str) -> list[tuple[Any, ...]] | None:
    query = "SELECT * FROM joinToCreateChannel WHERE channelId = %s"
    params = (channel_id,)
    return await execute_query(query, params)


async def set_join_to_create_channel(guild_id: int | str, channel_id: int | str) -> None:
    query = "INSERT INTO joinToCreateChannel (guildId, channelId) VALUES (%s, %s)"
    params = (guild_id, channel_id)
    await execute_action(query, params)


async def remove_join_to_create_channel(guild_id: int | str) -> None:
    query = "DELETE FROM joinToCreateChannel WHERE guildId = %s"
    params = (guild_id,)
    await execute_action(query, params)


async def get_media_channel(channel_id: int | str) -> list[tuple[Any, ...]] | None:
    query = "SELECT * FROM mediaChannel WHERE channelId = %s"
    params = (channel_id,)
    return await execute_query(query, params)


async def add_media_channel(guild_id: int | str, channel_id: int | str) -> None:
    query = "INSERT INTO mediaChannel (guildId, channelId) VALUES (%s, %s)"
    params = (guild_id, channel_id)
    await execute_action(query, params)


async def remove_media_channel(guild_id: int | str, channel_id: int | str) -> None:
    query = "DELETE FROM mediaChannel WHERE guildId = %s AND channelId = %s"
    params = (guild_id, channel_id)
    await execute_action(query, params)


async def get_welcome_channel(guild_id: int | str) -> tuple[Any, ...] | None:
    query = "SELECT * FROM welcomeChannel WHERE guildId = %s"
    params = (guild_id,)
    result = await execute_query(query, params)
    return result[0] if result else None


async def set_welcome_channel(guild_id: int | str, channel_id: int | str, message: str, image_background: str) -> None:
    query = "INSERT INTO welcomeChannel (guildId, channelId, message, imageBackground) VALUES (%s, %s, %s, %s)"
    params = (guild_id, channel_id, message, image_background)
    await execute_action(query, params)


async def remove_welcome_channel(guild_id: int | str) -> None:
    query = "DELETE FROM welcomeChannel WHERE guildId = %s"
    params = (guild_id,)
    await execute_action(query, params)


async def get_leave_channel(guild_id: int | str) -> tuple[Any, ...] | None:
    query = "SELECT * FROM leaveChannel WHERE guildId = %s"
    params = (guild_id,)
    result = await execute_query(query, params)
    return result[0] if result else None


async def set_leave_channel(guild_id: int | str, channel_id: int | str, message: str, image_background: str) -> None:
    query = "INSERT INTO leaveChannel (guildId, channelId, message, imageBackground) VALUES (%s, %s, %s, %s)"
    params = (guild_id, channel_id, message, image_background)
    await execute_action(query, params)


async def remove_leave_channel(guild_id: int | str) -> None:
    query = "DELETE FROM leaveChannel WHERE guildId = %s"
    params = (guild_id,)
    await execute_action(query, params)


async def get_dynamicslowmode_channels(guild_id: int | str) -> list[tuple[Any, ...]] | None:
    query = "SELECT * FROM dynamicslowmode WHERE guildId = %s"
    params = (guild_id,)
    return await execute_query(query, params)


async def add_dynamicslowmode(guild_id: int | str, channel_id: int | str, messages: int, per: int, resetafter: int) -> None:
    query = "INSERT INTO dynamicslowmode (guildId, channelId, messages, per, resetafter) VALUES (%s, %s, %s, %s, %s)"
    params = (guild_id, channel_id, messages, per, resetafter)
    await execute_action(query, params)


async def remove_dynamicslowmode(guild_id: int | str, channel_id: int | str) -> None:
    query = "DELETE FROM dynamicslowmode WHERE guildId = %s AND channelId = %s"
    params = (guild_id, channel_id)
    await execute_action(query, params)


async def get_dynamicslowmode(channel_id: int | str) -> tuple[Any, ...] | None:
    query = "SELECT * FROM dynamicslowmode WHERE channelId = %s"
    params = (channel_id,)
    result = await execute_query(query, params)
    return result[0] if result else None


async def add_dynamicslowmode_message(channel_id: int | str, message_id: str, send_time: datetime) -> None:
    query = "INSERT INTO dynamicslowmode_messages (channelId, messageId, sendTime) VALUES (%s, %s, %s)"
    params = (channel_id, message_id, send_time)
    await execute_action(query, params)


async def clear_old_dynamicslowmode_messages(channel_id: int | str, send_time: datetime) -> None:
    # Only delete messages older than the specified time, ensuring UTC comparison
    query = "DELETE FROM dynamicslowmode_messages WHERE channelId = %s AND sendTime < %s"
    params = (channel_id, send_time)
    await execute_action(query, params)


async def get_dynamicslowmode_messages(channel_id: int | str) -> list[tuple[Any, ...]] | None:
    query = "SELECT * FROM dynamicslowmode_messages WHERE channelId = %s"
    params = (channel_id,)
    return await execute_query(query, params)


async def cash_slowmode_delay(channel_id: int | str, slowmode_delay: int) -> None:
    query = "UPDATE dynamicslowmode SET cashedSlowmode = %s WHERE channelId = %s"
    params = (slowmode_delay, channel_id)
    await execute_action(query, params)


async def remove_cashed_slowmode_delay(channel_id: int | str) -> None:
    query = "UPDATE dynamicslowmode SET cashedSlowmode = NULL WHERE channelId = %s"
    params = (channel_id,)
    await execute_action(query, params)


async def get_twitch_online_notification(channel_id: int | str) -> list[tuple[Any, ...]] | None:
    query = "SELECT * FROM twitchOnlineNotification WHERE channelId = %s"
    params = (channel_id,)
    return await execute_query(query, params)


async def set_twitch_online_notification(
    guild_id: int | str,
    channel_id: int | str,
    twitch_uuid: str,
    twitch_name: str,
    notification_message: str,
) -> None:
    print("adding twitch online notification")
    query = "INSERT INTO twitchOnlineNotification (guildId, channelId, twitchUuid, twitchName, notificationMessage) VALUES (%s, %s, %s, %s, %s)"
    params = (guild_id, channel_id, twitch_uuid, twitch_name, notification_message)
    await execute_action(query, params)
    print("added twitch online notification")


async def remove_twitch_online_notification(id: str) -> None:
    query = "DELETE FROM twitchOnlineNotification WHERE id = %s"
    params = (id,)
    await execute_action(query, params)


async def get_twitch_online_notification_by_twitch_uuid(twitch_uuid: str) -> tuple[Any, ...] | None:
    query = "SELECT * FROM twitchOnlineNotification WHERE twitchUuid = %s"
    params = (twitch_uuid,)
    result = await execute_query(query, params)
    return result[0] if result else None


async def get_all_twitch_notification_uuids() -> list[tuple[Any, ...]] | None:
    query = "SELECT twitchUuid FROM twitchOnlineNotification"
    return await execute_query(query, ())


async def get_twitch_notification_by_guild_id(guild_id: int | str) -> list[tuple[Any, ...]] | None:
    query = "SELECT * FROM twitchOnlineNotification WHERE guildId = %s"
    params = (guild_id,)
    return await execute_query(query, params)


async def get_brawlstars_linked_account(user_id: int | str) -> str | None:
    query = "SELECT brawlstarsTag FROM brawlstarsLinkedAccounts WHERE userId = %s"
    params = (user_id,)
    result = await execute_query(query, params)
    return result[0][0] if result else None


async def add_brawlstars_linked_account(user_id: int | str, brawlstars_tag: str) -> None:
    query = "INSERT INTO brawlstarsLinkedAccounts (userId, brawlstarsTag) VALUES (%s, %s)"
    params = (user_id, brawlstars_tag)
    await execute_action(query, params)


async def remove_brawlstars_linked_account(user_id: int | str) -> None:
    query = "DELETE FROM brawlstarsLinkedAccounts WHERE userId = %s"
    params = (user_id,)
    await execute_action(query, params)
