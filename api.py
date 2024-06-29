import aiomysql
import asyncmy
from config import database_ip, database_password, database_user, database_schema
import json
from typing import Optional, List, Dict
from utility import get_xp_for_level, get_level_for_xp
from datetime import datetime

pool = None


def set_pool(p):
    global pool
    pool = p


async def execute_query(p, query, params=None):
    if not pool:
        print("tryied to execute action without pool. Pool is not yet initialized. Returning...")
        return

    try:
        async with pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(query, params)
                result = await cursor.fetchall()
                return result
    except Exception as e:
        print(f"An error occurred during query execution: {e}")
        raise


async def execute_action(p, query, params=None):
    if not pool:
        print("tryied to execute action without pool. Pool is not yet initialized. Returning...")
        return
    try:
        async with pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(query, params)
                await conn.commit()
                return cursor.rowcount
    except Exception as e:
        print(f"An error occurred during action execution: {e}")
        raise


async def execute_insert_and_get_id(p, query, params=None):
    if not pool:
        print("tryied to execute action without pool. Pool is not yet initialized. Returning...")
        return
    try:
        async with pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(query, params)
                await conn.commit()
                await cursor.execute("SELECT LAST_INSERT_ID()")
                last_id = await cursor.fetchone()
                return last_id[0] if last_id else None
    except Exception as e:
        print(f"An error occurred during insert: {e}")
        raise


async def create_tables():
    tables = {}
    tables["warnings"] = (
        "CREATE TABLE IF NOT EXISTS `warnings` ("
        "  `id` INT AUTO_INCREMENT PRIMARY KEY,"
        "  `guild_id` VARCHAR(20) NOT NULL,"
        "  `user_id` VARCHAR(20) NOT NULL,"
        "  `reason` VARCHAR(255),"
        "  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,"
        "  `expires_at` TIMESTAMP NULL,"
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
        "CREATE TABLE IF NOT EXISTS `message_tracking_opt_out` ("
        "  `user_id` VARCHAR(20) PRIMARY KEY"
        ") ENGINE=InnoDB"
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
        "  `difficulty` ENUM('easy', 'medium', 'hard', 'extreme', 'custom') DEFAULT 'medium',"
        "  `customFormula` VARCHAR(255) DEFAULT NULL,"
        "  `levelUpMessageActive` TINYINT(1) DEFAULT 1,"
        "  `levelUpMessage` VARCHAR(1000) DEFAULT NULL,"
        "  `levelUpChannelId` VARCHAR(20) DEFAULT NULL,"
        "  `active` TINYINT(1) DEFAULT 1,"
        "  `textCooldown` INT DEFAULT 60,"
        "  `voiceCooldown` INT DEFAULT 60"
        ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;"
    )
    tables[
        "giveaway"
    ] = """
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
    tables[
        "giveawayChannelRequirement"
    ] = """
    CREATE TABLE IF NOT EXISTS `giveawayChannelRequirement` (
        `giveawayId` INT UNSIGNED,
        `channelId` VARCHAR(20),
        `amount` SMALLINT UNSIGNED,
        PRIMARY KEY(`giveawayId`, `channelId`)
    ) ENGINE=InnoDB;
    """
    tables[
        "giveawayParticipant"
    ] = """
    CREATE TABLE IF NOT EXISTS `giveawayParticipant` (
        `userId` VARCHAR(20),
        `giveawayId` INT UNSIGNED,
        PRIMARY KEY(`userId`, `giveawayId`)
    ) ENGINE=InnoDB;
    """
    tables[
        "giveawayRoleRequirement"
    ] = """
    CREATE TABLE IF NOT EXISTS `giveawayRoleRequirement` (
        `roleId` VARCHAR(20),
        `giveawayId` INT UNSIGNED,
        PRIMARY KEY(`roleId`, `giveawayId`)
    ) ENGINE=InnoDB;
    """
    tables[
        "giveawayVoiceTime"
    ] = """
    CREATE TABLE IF NOT EXISTS `giveawayVoiceTime` (
        `giveawayId` INT UNSIGNED,
        `userId` VARCHAR(20),
        `voiceMinutes` MEDIUMINT UNSIGNED DEFAULT 0,
        PRIMARY KEY(`giveawayId`, `userId`)
    ) ENGINE=InnoDB;
    """
    tables[
        "giveawayNewMessage"
    ] = """
    CREATE TABLE IF NOT EXISTS `giveawayNewMessage` (
        `giveawayId` INT UNSIGNED,
        `userId` VARCHAR(20),
        `messages` MEDIUMINT UNSIGNED,
        PRIMARY KEY(`giveawayId`, `userId`)
    ) ENGINE=InnoDB;
    """
    tables[
        "giveawayBlacklistedRole"
    ] = """
    CREATE TABLE IF NOT EXISTS `giveawayBlacklistedRole` (
        `roleId` VARCHAR(20) PRIMARY KEY,
        `guildId` VARCHAR(20),
        PRIMARY KEY(`userId`, `guildId`)
    ) ENGINE=InnoDB;
    """
    tables[
        "giveawayBlacklistedUser"
    ] = """
    CREATE TABLE IF NOT EXISTS `giveawayBlacklistedUser` (
        `userId` VARCHAR(20),
        `guildId` VARCHAR(20),
        PRIMARY KEY(`userId`, `guildId`)
    ) ENGINE=InnoDB;
    """
    tables[
        "giveawayChannelMessages"
    ] = """
    CREATE TABLE IF NOT EXISTS `giveawayChannelMessages` (
        `giveawayId` INT UNSIGNED,
        `channelId` VARCHAR(20),
        `userId` VARCHAR(20),
        `amount` MEDIUMINT UNSIGNED DEFAULT 0,
        PRIMARY KEY(`giveawayId`, `channelId`, `userId`)
    ) ENGINE=InnoDB;
    """

    for table_name in tables:
        table_query = tables[table_name]
        await execute_action(pool, table_query)


async def add_warning(guild_id, user_id, reason, expiration_date=None):
    query = "INSERT INTO warnings (guild_id, user_id, reason, expires_at) VALUES (%s, %s, %s, %s)"
    params = (guild_id, user_id, reason, expiration_date)
    await execute_action(pool, query, params)


async def get_warnings(guild_id, user_id):
    query = "SELECT COUNT(*), GROUP_CONCAT(reason SEPARATOR '|') FROM warnings WHERE guild_id = %s AND user_id = %s AND (expires_at IS NULL OR expires_at > NOW())"
    params = (guild_id, user_id)
    result = await execute_query(pool, query, params)
    count, reasons = result[0]
    reasons_list = reasons.split("|") if reasons else []
    return count, reasons_list


async def get_detailed_warnings(guild_id, user_id):
    query = "SELECT id, reason, created_at, expires_at FROM warnings WHERE guild_id = %s AND user_id = %s ORDER BY created_at DESC"
    params = (guild_id, user_id)
    result = await execute_query(pool, query, params)
    return [(row[0], row[1], row[2], row[3]) for row in result]


async def remove_warning(warning_id):
    query = "DELETE FROM warnings WHERE id = %s"
    params = (warning_id,)
    await execute_action(pool, query, params)


async def set_warn_config(
    guild_id,
    expiration_days,
    timeout_threshold,
    timeout_duration,
    kick_threshold,
    ban_threshold,
):
    query = (
        "INSERT INTO warn_config (guild_id, expiration_days, timeout_threshold, timeout_duration, kick_threshold, ban_threshold) "
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
    await execute_action(pool, query, params)


async def get_warn_config(guild_id):
    query = "SELECT * FROM warn_config WHERE guild_id = %s"
    params = (guild_id,)
    result = await execute_query(pool, query, params)
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


async def save_channel_overwrites(channel_id, role_id, overwrites):
    query = "INSERT INTO channel_overwrites (channel_id, role_id, overwrites) VALUES (%s, %s, %s)"
    params = (channel_id, role_id, json.dumps(overwrites))
    await execute_action(pool, query, params)


async def get_channel_overwrites(channel_id):
    query = "SELECT role_id, overwrites FROM channel_overwrites WHERE channel_id = %s"
    params = (channel_id,)
    result = await execute_query(pool, query, params)
    return {row[0]: json.loads(row[1]) for row in result}


async def clear_channel_overwrites(channel_id):
    query = "DELETE FROM channel_overwrites WHERE channel_id = %s"
    params = (channel_id,)
    await execute_action(pool, query, params)


async def check_if_opted_out(user_id):
    query = "SELECT * FROM message_tracking_opt_out WHERE user_id = %s"
    params = (user_id,)
    result = await execute_query(pool, query, params)
    print(result)
    return len(result) > 0


async def opt_out(user_id):
    query = "INSERT INTO message_tracking_opt_out (user_id) VALUES (%s)"
    params = (user_id,)
    await execute_action(pool, query, params)


async def opt_in(user_id):
    query = "DELETE FROM message_tracking_opt_out WHERE user_id = %s"
    params = (user_id,)
    await execute_action(pool, query, params)


async def set_counting_progress(channel_id, progress, guild_id):
    query = "INSERT INTO counting (channel_id, progress, guild_id) VALUES (%s, %s, %s) ON DUPLICATE KEY UPDATE progress = VALUES(progress)"
    params = (channel_id, progress, guild_id)
    await execute_action(pool, query, params)


async def get_counting_channel_amount(guild_id):
    query = "SELECT COUNT(progress) FROM counting WHERE guild_id = %s"
    params = (guild_id,)
    result = await execute_query(pool, query, params)
    return len(result) if result else 0


async def get_counting_progress(channel_id):
    query = "SELECT progress FROM counting WHERE channel_id = %s"
    params = (channel_id,)
    result = await execute_query(pool, query, params)
    return result[0][0] if result else None


async def increase_counting_progress(channel_id, last_counter_id):
    query = "UPDATE counting SET progress = progress + 1, last_counter_id = %s WHERE channel_id = %s"
    params = (last_counter_id, channel_id)
    await execute_action(pool, query, params)


async def get_last_counter_id(channel_id):
    query = "SELECT last_counter_id FROM counting WHERE channel_id = %s"
    params = (channel_id,)
    result = await execute_query(pool, query, params)
    return result[0][0] if result else None


async def clear_counting(channel_id):
    query = "DELETE FROM counting WHERE channel_id = %s"
    params = (channel_id,)
    await execute_action(pool, query, params)


async def set_counting_challenge_progress(channel_id, progress, guild_id):
    query = "INSERT INTO counting_challenge (channel_id, progress, guild_id) VALUES (%s, %s, %s) ON DUPLICATE KEY UPDATE progress = VALUES(progress)"
    params = (channel_id, progress, guild_id)
    await execute_action(pool, query, params)


async def get_counting_challenge_progress(channel_id):
    query = "SELECT progress FROM counting_challenge WHERE channel_id = %s"
    params = (channel_id,)
    result = await execute_query(pool, query, params)
    return result[0][0] if result else None


async def increase_counting_challenge_progress(channel_id, last_counter_id):
    query = "UPDATE counting_challenge SET progress = progress + 1, last_counter_id = %s WHERE channel_id = %s"
    params = (last_counter_id, channel_id)
    await execute_action(pool, query, params)


async def get_last_challenge_counter_id(channel_id):
    query = "SELECT last_counter_id FROM counting_challenge WHERE channel_id = %s"
    params = (channel_id,)
    result = await execute_query(pool, query, params)
    return result[0][0] if result else None


async def clear_counting_challenge(channel_id):
    query = "DELETE FROM counting_challenge WHERE channel_id = %s"
    params = (channel_id,)
    await execute_action(pool, query, params)


async def get_counting_challenge_channel_amount(guild_id):
    query = "SELECT COUNT(progress) FROM counting_challenge WHERE guild_id = %s"
    params = (guild_id,)
    result = await execute_query(pool, query, params)
    return len(result) if result else 0


async def set_counting_mode(channel_id, progress, mode, guild_id):
    query = "INSERT INTO counting_modes (channel_id, progress, mode, guild_id) VALUES (%s, %s, %s, %s) ON DUPLICATE KEY UPDATE progress = VALUES(progress), mode = VALUES(mode)"
    params = (channel_id, progress, mode, guild_id)
    await execute_action(pool, query, params)


async def get_counting_mode_mode(channel_id):
    query = "SELECT mode FROM counting_modes WHERE channel_id = %s"
    params = (channel_id,)
    result = await execute_query(pool, query, params)
    return result[0] if result else None


async def get_counting_mode_progress(channel_id):
    query = "SELECT progress FROM counting_modes WHERE channel_id = %s"
    params = (channel_id,)
    result = await execute_query(pool, query, params)
    return result[0][0] if result else None


async def get_last_mode_counter_id(channel_id):
    query = "SELECT last_counter_id FROM counting_modes WHERE channel_id = %s"
    params = (channel_id,)
    result = await execute_query(pool, query, params)
    return result[0][0] if result else None


async def clear_counting_mode(channel_id):
    query = "DELETE FROM counting_modes WHERE channel_id = %s"
    params = (channel_id,)
    await execute_action(pool, query, params)


async def get_counting_mode_mode(channel_id):
    query = "SELECT mode FROM counting_modes WHERE channel_id = %s"
    params = (channel_id,)
    result = await execute_query(pool, query, params)
    return result[0][0] if result else None


async def set_counting_mode_progress(
    channel_id, progress, guild_id, mode, goal, counter_id
):
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
    await execute_action(pool, query, params)


async def get_counting_mode_mode(channel_id):
    query = "SELECT mode FROM counting_modes WHERE channel_id = %s"
    params = (channel_id,)
    result = await execute_query(pool, query, params)
    return result[0][0] if result else None


async def get_count_mode_goal(channel_id):
    query = "SELECT goal FROM counting_modes WHERE channel_id = %s"
    params = (channel_id,)
    result = await execute_query(pool, query, params)
    return result[0][0] if result else None


async def get_wordchain_word(channel_id):
    query = "SELECT word FROM wordchain WHERE channel_id = %s"
    params = (channel_id,)
    result = await execute_query(pool, query, params)
    return result[0][0] if result else None


async def set_wordchain_word(channel_id, word, guild_id, worder_id):
    query = "INSERT INTO wordchain (channel_id, word, last_user_id, guild_id) VALUES (%s, %s, %s, %s) ON DUPLICATE KEY UPDATE word = %s, last_user_id = %s"
    params = (channel_id, word, worder_id, guild_id, word, worder_id)
    await execute_action(pool, query, params)


async def get_wordchain_last_user_id(channel_id):
    query = "SELECT last_user_id FROM wordchain WHERE channel_id = %s"
    params = (channel_id,)
    result = await execute_query(pool, query, params)
    return result[0][0] if result else None


async def clear_wordchain(channel_id):
    query = "DELETE FROM wordchain WHERE channel_id = %s"
    params = (channel_id,)
    await execute_action(pool, query, params)


async def set_level_system_status(guild_id: str, active: bool):
    query = """
    INSERT INTO levelConfig (guild_id, active) 
    VALUES (%s, %s) 
    ON DUPLICATE KEY UPDATE active = VALUES(active)
    """
    params = (guild_id, active)
    await execute_action(pool, query, params)


async def get_level_system_status(guild_id: str) -> bool:
    query = "SELECT active FROM levelConfig WHERE guild_id = %s"
    params = (guild_id,)
    result = await execute_query(pool, query, params)
    return result[0][0] if result else True


async def delete_level_system_data(guild_id: str):
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
        await execute_action(pool, query, params)


async def set_levelup_message_status(guild_id: str, status: bool):
    query = """
    INSERT INTO levelConfig (guild_id, levelUpMessageActive) 
    VALUES (%s, %s) 
    ON DUPLICATE KEY UPDATE levelUpMessageActive = VALUES(levelUpMessageActive)
    """
    params = (guild_id, status)
    await execute_action(pool, query, params)


async def get_levelup_message_status(guild_id: str) -> bool:
    query = "SELECT levelUpMessageActive FROM levelConfig WHERE guild_id = %s"
    params = (guild_id,)
    result = await execute_query(pool, query, params)
    return result[0][0] if result else True  # DEFAULT to True if no record exists


async def set_levelup_message(guild_id: str, message: str):
    query = """
    INSERT INTO levelConfig (guild_id, levelUpMessage) 
    VALUES (%s, %s) 
    ON DUPLICATE KEY UPDATE levelUpMessage = VALUES(levelUpMessage)
    """
    params = (guild_id, message)
    await execute_action(pool, query, params)


async def get_levelup_message(guild_id: str) -> str:
    query = "SELECT levelUpMessage FROM levelConfig WHERE guild_id = %s"
    params = (guild_id,)
    result = await execute_query(pool, query, params)
    return result[0][0] if result else None


async def set_levelup_channel(guild_id: str, channel_id: Optional[str]):
    query = """
    INSERT INTO levelConfig (guild_id, levelUpChannelId) 
    VALUES (%s, %s) 
    ON DUPLICATE KEY UPDATE levelUpChannelId = VALUES(levelUpChannelId)
    """
    params = (guild_id, channel_id)
    await execute_action(pool, query, params)


async def get_levelup_channel(guild_id: str) -> Optional[str]:
    query = "SELECT levelUpChannelId FROM levelConfig WHERE guild_id = %s"
    params = (guild_id,)
    result = await execute_query(pool, query, params)
    return result[0][0] if result else None


async def set_xp_scaling(guild_id: str, scaling: str):
    query = """
    INSERT INTO levelConfig (guild_id, difficulty) 
    VALUES (%s, %s) 
    ON DUPLICATE KEY UPDATE difficulty = VALUES(difficulty)
    """
    params = (guild_id, scaling)
    await execute_action(pool, query, params)


async def get_xp_scaling(guild_id: str) -> str:
    query = "SELECT difficulty FROM levelConfig WHERE guild_id = %s"
    params = (guild_id,)
    result = await execute_query(pool, query, params)
    return result[0][0] if result else "medium"


async def set_custom_formula(guild_id: str, formula: str):
    query = """
    INSERT INTO levelConfig (guild_id, customFormula) 
    VALUES (%s, %s) 
    ON DUPLICATE KEY UPDATE customFormula = VALUES(customFormula)
    """
    params = (guild_id, formula)
    await execute_action(pool, query, params)


async def get_custom_formula(guild_id: str) -> str:
    query = "SELECT customFormula FROM levelConfig WHERE guild_id = %s"
    params = (guild_id,)
    result = await execute_query(pool, query, params)
    return result[0][0] if result else None


async def add_level_role(guild_id: str, role_id: str, level: int):
    query = """
    INSERT INTO levelRole (guild_id, role_id, level) 
    VALUES (%s, %s, %s) 
    ON DUPLICATE KEY UPDATE role_id = VALUES(role_id)
    """
    params = (guild_id, role_id, level)
    await execute_action(pool, query, params)


async def get_level_roles(guild_id: str) -> dict[int, str]:
    query = "SELECT level, role_id FROM levelRole WHERE guild_id = %s"
    params = (guild_id,)
    result = await execute_query(pool, query, params)
    return {row[0]: row[1] for row in result}


async def add_level_role(guild_id: str, role_id: str, level: int):
    query = """
    INSERT INTO levelRole (guild_id, role_id, level) 
    VALUES (%s, %s, %s)
    """
    params = (guild_id, role_id, level)
    await execute_action(pool, query, params)


async def remove_level_role(guild_id: str, role_id: str, level: int):
    query = """
    DELETE FROM levelRole 
    WHERE guild_id = %s AND role_id = %s AND level = %s
    """
    params = (guild_id, role_id, level)
    await execute_action(pool, query, params)


async def get_level_roles(guild_id: str, level: int) -> List[str]:
    query = "SELECT role_id FROM levelRole WHERE guild_id = %s AND level <= %s"
    params = (guild_id, level)
    result = await execute_query(pool, query, params)
    return [row[0] for row in result]


async def get_all_level_roles(guild_id: str) -> Dict[int, List[str]]:
    query = "SELECT level, role_id FROM levelRole WHERE guild_id = %s ORDER BY level"
    params = (guild_id,)
    result = await execute_query(pool, query, params)
    level_roles = {}
    for level, role_id in result:
        if level not in level_roles:
            level_roles[level] = []
        level_roles[level].append(role_id)
    return level_roles


async def add_role_boost(guild_id: str, role_id: str, boost: float, additive: bool):
    query = """
    INSERT INTO roleXpBoost (guild_id, role_id, boost, additive) 
    VALUES (%s, %s, %s, %s)
    ON DUPLICATE KEY UPDATE boost = VALUES(boost), additive = VALUES(additive)
    """
    params = (guild_id, role_id, boost, additive)
    await execute_action(pool, query, params)


async def add_channel_boost(
    guild_id: str, channel_id: str, boost: float, additive: bool
):
    query = """
    INSERT INTO channelXpBoost (guild_id, channel_id, boost, additive) 
    VALUES (%s, %s, %s, %s)
    ON DUPLICATE KEY UPDATE boost = VALUES(boost), additive = VALUES(additive)
    """
    params = (guild_id, channel_id, boost, additive)
    await execute_action(pool, query, params)


async def add_user_boost(guild_id: str, user_id: str, boost: float, additive: bool):
    query = """
    INSERT INTO userXpBoost (guild_id, user_id, boost, additive) 
    VALUES (%s, %s, %s, %s)
    ON DUPLICATE KEY UPDATE boost = VALUES(boost), additive = VALUES(additive)
    """
    params = (guild_id, user_id, boost, additive)
    await execute_action(pool, query, params)


async def remove_role_boost(guild_id: str, role_id: str):
    query = "DELETE FROM roleXpBoost WHERE guild_id = %s AND role_id = %s"
    params = (guild_id, role_id)
    await execute_action(pool, query, params)


async def remove_channel_boost(guild_id: str, channel_id: str):
    query = "DELETE FROM channelXpBoost WHERE guild_id = %s AND channel_id = %s"
    params = (guild_id, channel_id)
    await execute_action(pool, query, params)


async def remove_user_boost(guild_id: str, user_id: str):
    query = "DELETE FROM userXpBoost WHERE guild_id = %s AND user_id = %s"
    params = (guild_id, user_id)
    await execute_action(pool, query, params)


async def get_all_boosts(guild_id: str):
    role_query = "SELECT role_id, boost, additive FROM roleXpBoost WHERE guild_id = %s"
    channel_query = (
        "SELECT channel_id, boost, additive FROM channelXpBoost WHERE guild_id = %s"
    )
    user_query = "SELECT user_id, boost, additive FROM userXpBoost WHERE guild_id = %s"

    roles = await execute_query(pool, role_query, (guild_id,))
    channels = await execute_query(pool, channel_query, (guild_id,))
    users = await execute_query(pool, user_query, (guild_id,))

    return {"roles": roles, "channels": channels, "users": users}


async def get_user_boost(guild_id: str, user_id: str):
    query = (
        "SELECT boost, additive FROM userXpBoost WHERE guild_id = %s AND user_id = %s"
    )
    params = (guild_id, user_id)
    result = await execute_query(pool, query, params)
    return result[0] if result else None


async def get_user_roles_boosts(guild_id: str, role_ids: List[str]):
    placeholders = ", ".join(["%s"] * len(role_ids))
    query = f"SELECT boost, additive FROM roleXpBoost WHERE guild_id = %s AND role_id IN ({placeholders})"
    params = (guild_id,) + tuple(role_ids)
    result = await execute_query(pool, query, params)


async def get_channel_boost(guild_id: str, channel_id: str):
    query = "SELECT boost, additive FROM channelXpBoost WHERE guild_id = %s AND channel_id = %s"
    params = (guild_id, channel_id)
    result = await execute_query(pool, query, params)
    return result[0] if result else None


async def add_channel_to_blacklist(guild_id: str, channel_id: str, reason: str = None):
    query = """
    INSERT INTO blacklistedChannel (guild_id, channel_id, reason) 
    VALUES (%s, %s, %s)
    ON DUPLICATE KEY UPDATE reason = VALUES(reason)
    """
    params = (guild_id, channel_id, reason)
    await execute_action(pool, query, params)


async def remove_channel_from_blacklist(guild_id: str, channel_id: str):
    query = "DELETE FROM blacklistedChannel WHERE guild_id = %s AND channel_id = %s"
    params = (guild_id, channel_id)
    await execute_action(pool, query, params)


async def add_role_to_blacklist(guild_id: str, role_id: str, reason: str = None):
    query = """
    INSERT INTO blacklistedRole (guild_id, role_id, reason) 
    VALUES (%s, %s, %s)
    ON DUPLICATE KEY UPDATE reason = VALUES(reason)
    """
    params = (guild_id, role_id, reason)
    await execute_action(pool, query, params)


async def remove_role_from_blacklist(guild_id: str, role_id: str):
    query = "DELETE FROM blacklistedRole WHERE guild_id = %s AND role_id = %s"
    params = (guild_id, role_id)
    await execute_action(pool, query, params)


async def add_user_to_blacklist(guild_id: str, user_id: str, reason: str = None):
    query = """
    INSERT INTO blacklistedUser (guild_id, user_id, reason) 
    VALUES (%s, %s, %s)
    ON DUPLICATE KEY UPDATE reason = VALUES(reason)
    """
    params = (guild_id, user_id, reason)
    await execute_action(pool, query, params)


async def remove_user_from_blacklist(guild_id: str, user_id: str):
    query = "DELETE FROM blacklistedUser WHERE guild_id = %s AND user_id = %s"
    params = (guild_id, user_id)
    await execute_action(pool, query, params)


async def get_blacklist(guild_id: str):
    channels_query = (
        "SELECT channel_id, reason FROM blacklistedChannel WHERE guild_id = %s"
    )
    roles_query = "SELECT role_id, reason FROM blacklistedRole WHERE guild_id = %s"
    users_query = "SELECT user_id, reason FROM blacklistedUser WHERE guild_id = %s"

    channels = await execute_query(pool, channels_query, (guild_id,))
    roles = await execute_query(pool, roles_query, (guild_id,))
    users = await execute_query(pool, users_query, (guild_id,))

    return {"channels": channels, "roles": roles, "users": users}


async def get_user_level_info(guild_id: str, user_id: str):
    query = """
    SELECT xp, customBackground FROM level 
    WHERE guild_id = %s AND user_id = %s
    """
    params = (guild_id, user_id)
    result = await execute_query(pool, query, params)
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


async def set_custom_background(guild_id: str, user_id: str, background_url: str):
    query = """
    INSERT INTO level (guild_id, user_id, customBackground) 
    VALUES (%s, %s, %s)
    ON DUPLICATE KEY UPDATE customBackground = VALUES(customBackground)
    """
    params = (guild_id, user_id, background_url)
    await execute_action(pool, query, params)


async def get_user_xp(guild_id: str, user_id: str):
    query = "SELECT xp FROM level WHERE guild_id = %s AND user_id = %s"
    params = (guild_id, user_id)
    result = await execute_query(pool, query, params)
    return result[0][0] if result else None


async def update_user_xp(guild_id: str, user_id: str, xp: int, respect_cooldown = False):
    if respect_cooldown:
        query = """
        INSERT INTO level (guild_id, user_id, xp, last_xp_gain)
        VALUES (%s, %s, %s, NOW())
        ON DUPLICATE KEY UPDATE
            xp = CASE
                WHEN TIMESTAMPDIFF(SECOND, last_xp_gain, NOW()) >= GREATEST(1, (SELECT textCooldown FROM levelConfig WHERE guild_id = %s))
                THEN xp + %s
                ELSE xp
            END,
            last_xp_gain = CASE
                WHEN TIMESTAMPDIFF(SECOND, last_xp_gain, NOW()) >= GREATEST(1, (SELECT textCooldown FROM levelConfig WHERE guild_id = %s))
                THEN NOW()
                ELSE last_xp_gain
            END;
        """
        params = (guild_id, user_id, xp, guild_id, xp, guild_id)
        await execute_action(pool, query, params)
    else:
        query = "INSERT INTO level (guild_id, user_id, xp) VALUES (%s, %s, %s) ON DUPLICATE KEY UPDATE xp = xp + %s"
        params = (guild_id, user_id, xp, xp)
        await execute_action(pool, query, params)
async def update_user_xp_from_voice(guild_id: str, user_id: str, xp: int, respect_cooldown = False):
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
        params = (guild_id, user_id, xp, guild_id, xp, guild_id)
        await execute_action(pool, query, params)
    else:
        query = "INSERT INTO level (guild_id, user_id, xp) VALUES (%s, %s, %s) ON DUPLICATE KEY UPDATE xp = xp + %s"
        params = (guild_id, user_id, xp, xp)
        await execute_action(pool, query, params)

async def add_giveaway(
    guild_id: str,
    title: str,
    description: str,
    winners: int,
    with_button: bool,
    channel_id: str,
    custom_name: Optional[str],
    sponsor: Optional[str],
    price: Optional[str],
    message: Optional[str],
    endtime: datetime,
    starttime: Optional[datetime],
    new_message_requirement: Optional[int],
    day_requirement: Optional[int],
    channel_requirements: Dict[str, int],
    role_requirement: List[str],
    voice_requirement: Optional[int],
):
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
    giveawayId = await execute_insert_and_get_id(pool, query, params)

    query = """
    INSERT INTO giveawayChannelRequirement (giveawayId, channelId, amount)
    VALUES (%s, %s, %s)
    """
    try:
        for channel_id, amount in channel_requirements.items():
            params = (giveawayId, channel_id, amount)
            await execute_action(pool, query, params)
    except:
        pass
    query = """
    INSERT INTO giveawayRoleRequirement (roleId, giveawayId)
    VALUES (%s, %s)
    """
    for role_id in role_requirement:
        params = (role_id, giveawayId)
        await execute_action(pool, query, params)

    return giveawayId


async def set_giveaway_message_id(giveaway_id: int, message_id: int):
    query = "UPDATE giveaway SET messageId = %s WHERE giveawayId = %s"
    params = (message_id, giveaway_id)
    await execute_action(pool, query, params)


async def get_giveaway(giveaway_id: int):
    query = "SELECT * FROM giveaway WHERE giveawayId = %s"
    params = (giveaway_id,)
    result = await execute_query(pool, query, params)
    return result[0] if result else None


async def get_giveaway_channel_requirements(giveaway_id: int):
    query = (
        "SELECT channelId, amount FROM giveawayChannelRequirement WHERE giveawayId = %s"
    )
    params = (giveaway_id,)
    result = await execute_query(pool, query, params)
    return result


async def get_giveaway_role_requirements(giveaway_id: int):
    query = "SELECT roleId FROM giveawayRoleRequirement WHERE giveawayId = %s"
    params = (giveaway_id,)
    result = await execute_query(pool, query, params)
    return [row[0] for row in result]


async def set_giveaway_started(giveaway_id: int):
    query = "UPDATE giveaway SET started = 1 WHERE giveawayId = %s"
    params = (giveaway_id,)
    await execute_action(pool, query, params)


async def set_giveaway_ended(giveaway_id: int):
    query = "UPDATE giveaway SET ended = 1 WHERE giveawayId = %s"
    params = (giveaway_id,)
    await execute_action(pool, query, params)


async def delete_old_giveaways():
    query = "DELETE FROM giveaway WHERE ended = 1 AND endtime < NOW() - INTERVAL 1 WEEK"
    await execute_action(pool, query)


async def get_giveaway_participants(giveaway_id: int):
    query = "SELECT userId FROM giveawayParticipant WHERE giveawayId = %s"
    params = (giveaway_id,)
    result = await execute_query(pool, query, params)
    return [row[0] for row in result]


async def get_new_messages(giveaway_id: int, user_id: str):
    query = (
        "SELECT messages FROM giveawayNewMessage WHERE giveawayId = %s AND userId = %s"
    )
    params = (giveaway_id, user_id)
    result = await execute_query(pool, query, params)
    return result[0][0] if result else None


async def get_new_messages_channel(giveaway_id: int, channel_id: str, user_id: str):
    query = "SELECT messages FROM giveawayChannelMessages WHERE giveawayId = %s AND channelId = %s AND userId = %s"
    params = (giveaway_id, channel_id, user_id)
    result = await execute_query(pool, query, params)
    return result[0][0] if result else None


async def get_voice_time(giveaway_id: int, user_id: str):
    query = "SELECT voiceMinutes FROM giveawayVoiceTime WHERE giveawayId = %s AND userId = %s"
    params = (giveaway_id, user_id)
    result = await execute_query(pool, query, params)
    return result[0][0] if result else None


async def get_blacklisted_roles(guild_id: str):
    query = (
        "SELECT roleId, reason, expire FROM giveawayBlacklistedRole WHERE guildId = %s"
    )
    params = (guild_id,)
    result = await execute_query(pool, query, params)
    return result


async def check_if_user_blacklisted(guild_id: str, user_id: str):
    query = "SELECT * FROM giveawayBlacklistedUser WHERE guildId = %s AND userId = %s"
    params = (guild_id, user_id)
    result = await execute_query(pool, query, params)
    return len(result) > 0


async def check_if_giveaway_participant(giveaway_id: int, user_id: str):
    query = "SELECT * FROM giveawayParticipant WHERE giveawayId = %s AND userId = %s"
    params = (giveaway_id, user_id)
    result = await execute_query(pool, query, params)
    return len(result) > 0


async def remove_giveaway_participant(giveaway_id: int, user_id: str):
    query = "DELETE FROM giveawayParticipant WHERE giveawayId = %s AND userId = %s"
    params = (giveaway_id, user_id)
    await execute_action(pool, query, params)

async def add_giveaway_participant(giveaway_id: int, user_id: str):
    query = "INSERT INTO giveawayParticipant (userId, giveawayId) VALUES (%s, %s)"
    params = (user_id, giveaway_id)
    await execute_action(pool, query, params)


async def get_send_ready_giveaways():
    query = "SELECT giveawayId FROM giveaway WHERE started = 0 AND starttime < NOW()"
    result = await execute_query(pool, query)
    return result


async def add_giveaway_voice_minutes_if_needed(user_id, guild_id):
    query = "SELECT giveawayId FROM giveaway WHERE guildId = %s AND voiceRequirement IS NOT NULL"
    params = (guild_id,)
    result = await execute_query(pool, query, params)
    for giveaway_id in result:
        query = "INSERT INTO giveawayVoiceTime (giveawayId, userId, voiceMinutes) VALUES (%s, %s, 0) ON DUPLICATE KEY UPDATE voiceMinutes = voiceMinutes + 1"
        params = (giveaway_id, user_id)
        await execute_action(pool, query, params)


async def add_giveaway_new_message_if_needed(user_id, guild_id):
    query = "SELECT giveawayId FROM giveaway WHERE guildId = %s AND newMessageRequirement IS NOT NULL"
    params = (guild_id,)
    result = await execute_query(pool, query, params)
    for giveaway_id in result:
        query = "INSERT INTO giveawayNewMessage (giveawayId, userId, messages) VALUES (%s, %s, 0) ON DUPLICATE KEY UPDATE messages = messages + 1"
        params = (giveaway_id, user_id)
        await execute_action(pool, query, params)


async def add_giveaway_new_message_channel_if_needed(user_id, guild_id, channel_id):
    query = "SELECT giveawayId FROM giveaway WHERE guildId = %s AND newMessageRequirement IS NOT NULL"
    params = (guild_id,)
    result = await execute_query(pool, query, params)
    for giveaway_id in result:
        query = "INSERT INTO giveawayChannelMessages (giveawayId, channelId, userId, amount) VALUES (%s, %s, %s, 0) ON DUPLICATE KEY UPDATE amount = amount + 1"
        params = (giveaway_id, channel_id, user_id)
        await execute_action(pool, query, params)


async def get_end_ready_giveaways():
    query = "SELECT giveawayId FROM giveaway WHERE ended = 0 AND endtime < NOW() AND started = 1 AND messageId <> 'pending'"
    result = await execute_query(pool, query)
    return result

async def add_giveaway_blacklisted_user(guild_id: str, user_id: str):
    query = "INSERT INTO giveawayBlacklistedUser (guildId, userId) VALUES (%s, %s)"
    params = (guild_id, user_id)
    await execute_action(pool, query, params)

async def add_giveaway_blacklisted_role(guild_id: str, role_id: str):
    query = "INSERT INTO giveawayBlacklistedRole (guildId, roleId) VALUES (%s, %s)"
    params = (guild_id, role_id)
    await execute_action(pool, query, params)

async def remove_giveaway_blacklisted_user(guild_id: str, user_id: str):
    query = "DELETE FROM giveawayBlacklistedUser WHERE guildId = %s AND userId = %s"
    params = (guild_id, user_id)
    await execute_action(pool, query, params)

async def remove_giveaway_blacklisted_role(guild_id: str, role_id: str):
    query = "DELETE FROM giveawayBlacklistedRole WHERE guildId = %s AND roleId = %s"
    params = (guild_id, role_id)
    await execute_action(pool, query, params)

async def get_giveaway_blacklisted_users(guild_id: str):
    query = "SELECT userId, reason, expire FROM giveawayBlacklistedUser WHERE guildId = %s"
    params = (guild_id,)
    result = await execute_query(pool, query, params)
    return result

async def get_giveaway_blacklisted_roles(guild_id: str):
    query = "SELECT roleId, reason, expire FROM giveawayBlacklistedRole WHERE guildId = %s"
    params = (guild_id,)
    result = await execute_query(pool, query, params)
    return result

async def delete_giveaway(giveaway_id: int):
    query = "DELETE FROM giveaway WHERE giveawayId = %s"
    params = (giveaway_id,)
    await execute_action(pool, query, params)

async def set_giveaway_endtime(giveaway_id: int, endtime: datetime):
    query = "UPDATE giveaway SET endtime = %s WHERE giveawayId = %s"
    params = (endtime, giveaway_id)
    await execute_action(pool, query, params)

async def update_giveaway(
    giveaway_id: int,
    guild_id: str,
    title: str,
    description: str,
    winners: int,
    with_button: bool,
    custom_name: Optional[str],
    sponsor: Optional[str],
    price: Optional[str],
    message: Optional[str],
    endtime: datetime,
    starttime: Optional[datetime],
    new_message_requirement: Optional[int],
    day_requirement: Optional[int],
    channel_requirements: Dict[str, int],
    role_requirement: List[str],
    voice_requirement: Optional[int],
    channel_id: str,
):
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
        giveaway_id
    )
    await execute_action(pool, query, params)

    await execute_action(pool, "DELETE FROM giveawayChannelRequirement WHERE giveawayId = %s", (giveaway_id,))
    if channel_requirements is not None and len(channel_requirements) > 0 and channel_requirements != {}:
        for channel_id, amount in channel_requirements.items():
            query = "INSERT INTO giveawayChannelRequirement (giveawayId, channelId, amount) VALUES (%s, %s, %s)"
            params = (giveaway_id, channel_id, amount)
            await execute_action(pool, query, params)

    await execute_action(pool, "DELETE FROM giveawayRoleRequirement WHERE giveawayId = %s", (giveaway_id,))
    for role_id in role_requirement:
        query = "INSERT INTO giveawayRoleRequirement (roleId, giveawayId) VALUES (%s, %s)"
        params = (role_id, giveaway_id)
        await execute_action(pool, query, params)

async def set_text_cooldown(guild_id: str, cooldown: int):
    query = """
    INSERT INTO levelConfig (guild_id, textCooldown) 
    VALUES (%s, %s) 
    ON DUPLICATE KEY UPDATE textCooldown = VALUES(textCooldown)
    """
    params = (guild_id, cooldown)
    await execute_action(pool, query, params)

async def set_voice_cooldown(guild_id: str, cooldown: int):
    query = """
    INSERT INTO levelConfig (guild_id, voiceCooldown) 
    VALUES (%s, %s) 
    ON DUPLICATE KEY UPDATE voiceCooldown = VALUES(voiceCooldown)
    """
    params = (guild_id, cooldown)
    await execute_action(pool, query, params)

async def get_text_cooldown(guild_id: str) -> int:
    query = "SELECT textCooldown FROM levelConfig WHERE guild_id = %s"
    params = (guild_id,)
    result = await execute_query(pool, query, params)
    return result[0][0] if result else 60  # Default to 60 seconds if not set

async def get_voice_cooldown(guild_id: str) -> int:
    query = "SELECT voiceCooldown FROM levelConfig WHERE guild_id = %s"
    params = (guild_id,)
    result = await execute_query(pool, query, params)
    return result[0][0] if result else 60  # Default to 60 seconds if not set
