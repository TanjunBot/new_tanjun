import mysql.connector
from config import database_ip, database_password, database_user, database_schema
import json
from typing import Optional, List, Dict
from utility import get_xp_for_level, get_level_for_xp


def create_tables():
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

    connection = mysql.connector.connect(
        host=database_ip,
        user=database_user,
        password=database_password,
        database=database_schema,
    )
    cursor = connection.cursor()

    for table_name in tables:
        table_query = tables[table_name]
        cursor.execute(table_query)

    connection.commit()
    cursor.close()
    connection.close()


connection = mysql.connector.connect(
    host=database_ip,
    user=database_user,
    password=database_password,
    database=database_schema,
)
cursor = connection.cursor()


def execute_query(query, params=None):
    cursor.execute(query, params)
    result = cursor.fetchall()
    connection.commit()
    return result


def execute_action(query, params=None):
    connection = mysql.connector.connect(
        host=database_ip,
        user=database_user,
        password=database_password,
        database=database_schema,
    )
    cursor = connection.cursor()
    cursor.execute(query, params)
    connection.commit()
    cursor.close()
    connection.close()


def add_warning(guild_id, user_id, reason, expiration_date=None):
    query = "INSERT INTO warnings (guild_id, user_id, reason, expires_at) VALUES (%s, %s, %s, %s)"
    params = (guild_id, user_id, reason, expiration_date)
    execute_action(query, params)


def get_warnings(guild_id, user_id):
    query = "SELECT COUNT(*), GROUP_CONCAT(reason SEPARATOR '|') FROM warnings WHERE guild_id = %s AND user_id = %s AND (expires_at IS NULL OR expires_at > NOW())"
    params = (guild_id, user_id)
    result = execute_query(query, params)
    count, reasons = result[0]
    reasons_list = reasons.split("|") if reasons else []
    return count, reasons_list


def clear_warnings(guild_id, user_id):
    query = "DELETE FROM warnings WHERE guild_id = %s AND user_id = %s"
    params = (guild_id, user_id)
    execute_action(query, params)


def get_detailed_warnings(guild_id, user_id):
    query = "SELECT id, reason, created_at, expires_at FROM warnings WHERE guild_id = %s AND user_id = %s ORDER BY created_at DESC"
    params = (guild_id, user_id)
    result = execute_query(query, params)
    return [(row[0], row[1], row[2], row[3]) for row in result]


def remove_warning(warning_id):
    query = "DELETE FROM warnings WHERE id = %s"
    params = (warning_id,)
    execute_action(query, params)


def set_warn_config(
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
    execute_action(query, params)


def get_warn_config(guild_id):
    query = "SELECT * FROM warn_config WHERE guild_id = %s"
    params = (guild_id,)
    result = execute_query(query, params)
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


def save_channel_overwrites(channel_id, role_id, overwrites):
    query = "INSERT INTO channel_overwrites (channel_id, role_id, overwrites) VALUES (%s, %s, %s)"
    params = (channel_id, role_id, json.dumps(overwrites))
    execute_action(query, params)


def get_channel_overwrites(channel_id):
    query = "SELECT role_id, overwrites FROM channel_overwrites WHERE channel_id = %s"
    params = (channel_id,)
    result = execute_query(query, params)
    return {row[0]: json.loads(row[1]) for row in result}


def clear_channel_overwrites(channel_id):
    query = "DELETE FROM channel_overwrites WHERE channel_id = %s"
    params = (channel_id,)
    execute_action(query, params)


def check_if_opted_out(user_id):
    query = "SELECT * FROM message_tracking_opt_out WHERE user_id = %s"
    params = (user_id,)
    result = execute_query(query, params)
    return len(result) > 0


def opt_out(user_id):
    query = "INSERT INTO message_tracking_opt_out (user_id) VALUES (%s)"
    params = (user_id,)
    execute_action(query, params)


def opt_in(user_id):
    query = "DELETE FROM message_tracking_opt_out WHERE user_id = %s"
    params = (user_id,)
    execute_action(query, params)


def set_counting_progress(channel_id, progress, guild_id):
    query = "INSERT INTO counting (channel_id, progress, guild_id) VALUES (%s, %s, %s) ON DUPLICATE KEY UPDATE progress = VALUES(progress)"
    params = (channel_id, progress, guild_id)
    execute_action(query, params)


def get_counting_channel_amount(guild_id):
    query = "SELECT COUNT(progress) FROM counting WHERE guild_id = %s"
    params = (guild_id,)
    result = execute_query(query, params)
    return len(result) if result else 0


def get_counting_progress(channel_id):
    query = "SELECT progress FROM counting WHERE channel_id = %s"
    params = (channel_id,)
    result = execute_query(query, params)
    return result[0][0] if result else None


def increase_counting_progress(channel_id, last_counter_id):
    query = "UPDATE counting SET progress = progress + 1, last_counter_id = %s WHERE channel_id = %s"
    params = (last_counter_id, channel_id)
    execute_action(query, params)


def get_last_counter_id(channel_id):
    query = "SELECT last_counter_id FROM counting WHERE channel_id = %s"
    params = (channel_id,)
    result = execute_query(query, params)
    return result[0][0] if result else None


def clear_counting(channel_id):
    query = "DELETE FROM counting WHERE channel_id = %s"
    params = (channel_id,)
    execute_action(query, params)


def set_counting_challenge_progress(channel_id, progress, guild_id):
    query = "INSERT INTO counting_challenge (channel_id, progress, guild_id) VALUES (%s, %s, %s) ON DUPLICATE KEY UPDATE progress = VALUES(progress)"
    params = (channel_id, progress, guild_id)
    execute_action(query, params)


def get_counting_challenge_progress(channel_id):
    query = "SELECT progress FROM counting_challenge WHERE channel_id = %s"
    params = (channel_id,)
    result = execute_query(query, params)
    return result[0][0] if result else None


def increase_counting_challenge_progress(channel_id, last_counter_id):
    query = "UPDATE counting_challenge SET progress = progress + 1, last_counter_id = %s WHERE channel_id = %s"
    params = (last_counter_id, channel_id)
    execute_action(query, params)


def get_last_challenge_counter_id(channel_id):
    query = "SELECT last_counter_id FROM counting_challenge WHERE channel_id = %s"
    params = (channel_id,)
    result = execute_query(query, params)
    return result[0][0] if result else None


def clear_counting_challenge(channel_id):
    query = "DELETE FROM counting_challenge WHERE channel_id = %s"
    params = (channel_id,)
    execute_action(query, params)


def get_counting_challenge_channel_amount(guild_id):
    query = "SELECT COUNT(progress) FROM counting_challenge WHERE guild_id = %s"
    params = (guild_id,)
    result = execute_query(query, params)
    return len(result) if result else 0


def set_counting_mode(channel_id, progress, mode, guild_id):
    query = "INSERT INTO counting_modes (channel_id, progress, mode, guild_id) VALUES (%s, %s, %s, %s) ON DUPLICATE KEY UPDATE progress = VALUES(progress), mode = VALUES(mode)"
    params = (channel_id, progress, mode, guild_id)
    execute_action(query, params)


def get_counting_mode_mode(channel_id):
    query = "SELECT mode FROM counting_modes WHERE channel_id = %s"
    params = (channel_id,)
    result = execute_query(query, params)
    return result[0] if result else None


def get_counting_mode_progress(channel_id):
    query = "SELECT progress FROM counting_modes WHERE channel_id = %s"
    params = (channel_id,)
    result = execute_query(query, params)
    return result[0][0] if result else None


def increase_counting_mode_progress(channel_id, last_counter_id):
    query = "UPDATE counting_modes SET progress = progress + 1, last_counter_id = %s WHERE channel_id = %s"
    params = (last_counter_id, channel_id)
    execute_action(query, params)


def get_last_mode_counter_id(channel_id):
    query = "SELECT last_counter_id FROM counting_modes WHERE channel_id = %s"
    params = (channel_id,)
    result = execute_query(query, params)
    return result[0][0] if result else None


def clear_counting_mode(channel_id):
    query = "DELETE FROM counting_modes WHERE channel_id = %s"
    params = (channel_id,)
    execute_action(query, params)


def get_counting_mode_mode(channel_id):
    query = "SELECT mode FROM counting_modes WHERE channel_id = %s"
    params = (channel_id,)
    result = execute_query(query, params)
    return result[0][0] if result else None


def get_counting_mode_channel_amount(guild_id):
    query = "SELECT COUNT(progress) FROM counting_modes WHERE guild_id = %s"
    params = (guild_id,)
    result = execute_query(query, params)
    return len(result) if result else 0


def set_counting_mode_progress(channel_id, progress, guild_id, mode, goal, counter_id):
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
    execute_action(query, params)


def get_counting_mode_mode(channel_id):
    query = "SELECT mode FROM counting_modes WHERE channel_id = %s"
    params = (channel_id,)
    result = execute_query(query, params)
    return result[0][0] if result else None


def get_count_mode_goal(channel_id):
    query = "SELECT goal FROM counting_modes WHERE channel_id = %s"
    params = (channel_id,)
    result = execute_query(query, params)
    return result[0][0] if result else None


def get_wordchain_word(channel_id):
    query = "SELECT word FROM wordchain WHERE channel_id = %s"
    params = (channel_id,)
    result = execute_query(query, params)
    return result[0][0] if result else None


def set_wordchain_word(channel_id, word, guild_id, worder_id):
    query = "INSERT INTO wordchain (channel_id, word, last_user_id, guild_id) VALUES (%s, %s, %s, %s) ON DUPLICATE KEY UPDATE word = %s, last_user_id = %s"
    params = (channel_id, word, worder_id, guild_id, word, worder_id)
    execute_action(query, params)


def get_wordchain_last_user_id(channel_id):
    query = "SELECT last_user_id FROM wordchain WHERE channel_id = %s"
    params = (channel_id,)
    result = execute_query(query, params)
    return result[0][0] if result else None


def clear_wordchain(channel_id):
    query = "DELETE FROM wordchain WHERE channel_id = %s"
    params = (channel_id,)
    execute_action(query, params)


def set_level_system_status(guild_id: str, active: bool):
    query = """
    INSERT INTO levelConfig (guild_id, active) 
    VALUES (%s, %s) 
    ON DUPLICATE KEY UPDATE active = VALUES(active)
    """
    params = (guild_id, active)
    execute_action(query, params)


def get_level_system_status(guild_id: str) -> bool:
    query = "SELECT active FROM levelConfig WHERE guild_id = %s"
    params = (guild_id,)
    result = execute_query(query, params)
    return result[0][0] if result else True  # Default to True if no record exists


def delete_level_system_data(guild_id: str):
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
        execute_action(query, (guild_id,))


def set_levelup_message_status(guild_id: str, status: bool):
    query = """
    INSERT INTO levelConfig (guild_id, levelUpMessageActive) 
    VALUES (%s, %s) 
    ON DUPLICATE KEY UPDATE levelUpMessageActive = VALUES(levelUpMessageActive)
    """
    params = (guild_id, status)
    execute_action(query, params)


def get_levelup_message_status(guild_id: str) -> bool:
    query = "SELECT levelUpMessageActive FROM levelConfig WHERE guild_id = %s"
    params = (guild_id,)
    result = execute_query(query, params)
    return result[0][0] if result else True  # Default to True if no record exists


def set_levelup_message(guild_id: str, message: str):
    query = """
    INSERT INTO levelConfig (guild_id, levelUpMessage) 
    VALUES (%s, %s) 
    ON DUPLICATE KEY UPDATE levelUpMessage = VALUES(levelUpMessage)
    """
    params = (guild_id, message)
    execute_action(query, params)


def get_levelup_message(guild_id: str) -> str:
    query = "SELECT levelUpMessage FROM levelConfig WHERE guild_id = %s"
    params = (guild_id,)
    result = execute_query(query, params)
    return result[0][0] if result else None


def set_levelup_channel(guild_id: str, channel_id: Optional[str]):
    query = """
    INSERT INTO levelConfig (guild_id, levelUpChannelId) 
    VALUES (%s, %s) 
    ON DUPLICATE KEY UPDATE levelUpChannelId = VALUES(levelUpChannelId)
    """
    params = (guild_id, channel_id)
    execute_action(query, params)


def get_levelup_channel(guild_id: str) -> Optional[str]:
    query = "SELECT levelUpChannelId FROM levelConfig WHERE guild_id = %s"
    params = (guild_id,)
    result = execute_query(query, params)
    return result[0][0] if result else None


def set_xp_scaling(guild_id: str, scaling: str):
    query = """
    INSERT INTO levelConfig (guild_id, difficulty) 
    VALUES (%s, %s) 
    ON DUPLICATE KEY UPDATE difficulty = VALUES(difficulty)
    """
    params = (guild_id, scaling)
    execute_action(query, params)


def get_xp_scaling(guild_id: str) -> str:
    query = "SELECT difficulty FROM levelConfig WHERE guild_id = %s"
    params = (guild_id,)
    result = execute_query(query, params)
    return result[0][0] if result else "medium"


def set_custom_formula(guild_id: str, formula: str):
    query = """
    INSERT INTO levelConfig (guild_id, customFormula) 
    VALUES (%s, %s) 
    ON DUPLICATE KEY UPDATE customFormula = VALUES(customFormula)
    """
    params = (guild_id, formula)
    execute_action(query, params)


def get_custom_formula(guild_id: str) -> str:
    query = "SELECT customFormula FROM levelConfig WHERE guild_id = %s"
    params = (guild_id,)
    result = execute_query(query, params)
    return result[0][0] if result else None


def add_level_role(guild_id: str, role_id: str, level: int):
    query = """
    INSERT INTO levelRole (guild_id, role_id, level) 
    VALUES (%s, %s, %s) 
    ON DUPLICATE KEY UPDATE role_id = VALUES(role_id)
    """
    params = (guild_id, role_id, level)
    execute_action(query, params)


def get_level_role(guild_id: str, level: int) -> Optional[str]:
    query = "SELECT role_id FROM levelRole WHERE guild_id = %s AND level = %s"
    params = (guild_id, level)
    result = execute_query(query, params)
    return result[0][0] if result else None


def get_level_roles(guild_id: str) -> dict[int, str]:
    query = "SELECT level, role_id FROM levelRole WHERE guild_id = %s"
    params = (guild_id,)
    result = execute_query(query, params)
    return {row[0]: row[1] for row in result}


def add_level_role(guild_id: str, role_id: str, level: int):
    query = """
    INSERT INTO levelRole (guild_id, role_id, level) 
    VALUES (%s, %s, %s)
    """
    params = (guild_id, role_id, level)
    execute_action(query, params)


def remove_level_role(guild_id: str, role_id: str, level: int):
    query = """
    DELETE FROM levelRole 
    WHERE guild_id = %s AND role_id = %s AND level = %s
    """
    params = (guild_id, role_id, level)
    execute_action(query, params)


def get_level_roles(guild_id: str, level: int) -> List[str]:
    query = "SELECT role_id FROM levelRole WHERE guild_id = %s AND level = %s"
    params = (guild_id, level)
    result = execute_query(query, params)
    return [row[0] for row in result]


def get_all_level_roles(guild_id: str) -> Dict[int, List[str]]:
    query = "SELECT level, role_id FROM levelRole WHERE guild_id = %s ORDER BY level"
    params = (guild_id,)
    result = execute_query(query, params)
    level_roles = {}
    for level, role_id in result:
        if level not in level_roles:
            level_roles[level] = []
        level_roles[level].append(role_id)
    return level_roles


def add_role_boost(guild_id: str, role_id: str, boost: float, additive: bool):
    query = """
    INSERT INTO roleXpBoost (guild_id, role_id, boost, additive) 
    VALUES (%s, %s, %s, %s)
    ON DUPLICATE KEY UPDATE boost = VALUES(boost), additive = VALUES(additive)
    """
    params = (guild_id, role_id, boost, additive)
    execute_action(query, params)


def add_channel_boost(guild_id: str, channel_id: str, boost: float, additive: bool):
    query = """
    INSERT INTO channelXpBoost (guild_id, channel_id, boost, additive) 
    VALUES (%s, %s, %s, %s)
    ON DUPLICATE KEY UPDATE boost = VALUES(boost), additive = VALUES(additive)
    """
    params = (guild_id, channel_id, boost, additive)
    execute_action(query, params)


def add_user_boost(guild_id: str, user_id: str, boost: float, additive: bool):
    query = """
    INSERT INTO userXpBoost (guild_id, user_id, boost, additive) 
    VALUES (%s, %s, %s, %s)
    ON DUPLICATE KEY UPDATE boost = VALUES(boost), additive = VALUES(additive)
    """
    params = (guild_id, user_id, boost, additive)
    execute_action(query, params)


def remove_role_boost(guild_id: str, role_id: str):
    query = "DELETE FROM roleXpBoost WHERE guild_id = %s AND role_id = %s"
    params = (guild_id, role_id)
    execute_action(query, params)


def remove_channel_boost(guild_id: str, channel_id: str):
    query = "DELETE FROM channelXpBoost WHERE guild_id = %s AND channel_id = %s"
    params = (guild_id, channel_id)
    execute_action(query, params)


def remove_user_boost(guild_id: str, user_id: str):
    query = "DELETE FROM userXpBoost WHERE guild_id = %s AND user_id = %s"
    params = (guild_id, user_id)
    execute_action(query, params)


def get_all_boosts(guild_id: str):
    role_query = "SELECT role_id, boost, additive FROM roleXpBoost WHERE guild_id = %s"
    channel_query = (
        "SELECT channel_id, boost, additive FROM channelXpBoost WHERE guild_id = %s"
    )
    user_query = "SELECT user_id, boost, additive FROM userXpBoost WHERE guild_id = %s"

    roles = execute_query(role_query, (guild_id,))
    channels = execute_query(channel_query, (guild_id,))
    users = execute_query(user_query, (guild_id,))

    return {"roles": roles, "channels": channels, "users": users}


def get_user_boost(guild_id: str, user_id: str):
    query = (
        "SELECT boost, additive FROM userXpBoost WHERE guild_id = %s AND user_id = %s"
    )
    params = (guild_id, user_id)
    result = execute_query(query, params)
    return result[0] if result else None


def get_user_roles_boosts(guild_id: str, role_ids: List[str]):
    placeholders = ", ".join(["%s"] * len(role_ids))
    query = f"SELECT boost, additive FROM roleXpBoost WHERE guild_id = %s AND role_id IN ({placeholders})"
    params = (guild_id,) + tuple(role_ids)
    return execute_query(query, params)


def get_channel_boost(guild_id: str, channel_id: str):
    query = "SELECT boost, additive FROM channelXpBoost WHERE guild_id = %s AND channel_id = %s"
    params = (guild_id, channel_id)
    result = execute_query(query, params)
    return result[0] if result else None


def add_channel_to_blacklist(guild_id: str, channel_id: str, reason: str = None):
    query = """
    INSERT INTO blacklistedChannel (guild_id, channel_id, reason) 
    VALUES (%s, %s, %s)
    ON DUPLICATE KEY UPDATE reason = VALUES(reason)
    """
    params = (guild_id, channel_id, reason)
    execute_action(query, params)


def remove_channel_from_blacklist(guild_id: str, channel_id: str):
    query = "DELETE FROM blacklistedChannel WHERE guild_id = %s AND channel_id = %s"
    params = (guild_id, channel_id)
    execute_action(query, params)


def add_role_to_blacklist(guild_id: str, role_id: str, reason: str = None):
    query = """
    INSERT INTO blacklistedRole (guild_id, role_id, reason) 
    VALUES (%s, %s, %s)
    ON DUPLICATE KEY UPDATE reason = VALUES(reason)
    """
    params = (guild_id, role_id, reason)
    execute_action(query, params)


def remove_role_from_blacklist(guild_id: str, role_id: str):
    query = "DELETE FROM blacklistedRole WHERE guild_id = %s AND role_id = %s"
    params = (guild_id, role_id)
    execute_action(query, params)


def add_user_to_blacklist(guild_id: str, user_id: str, reason: str = None):
    query = """
    INSERT INTO blacklistedUser (guild_id, user_id, reason) 
    VALUES (%s, %s, %s)
    ON DUPLICATE KEY UPDATE reason = VALUES(reason)
    """
    params = (guild_id, user_id, reason)
    execute_action(query, params)


def remove_user_from_blacklist(guild_id: str, user_id: str):
    query = "DELETE FROM blacklistedUser WHERE guild_id = %s AND user_id = %s"
    params = (guild_id, user_id)
    execute_action(query, params)


def get_blacklist(guild_id: str):
    channels_query = (
        "SELECT channel_id, reason FROM blacklistedChannel WHERE guild_id = %s"
    )
    roles_query = "SELECT role_id, reason FROM blacklistedRole WHERE guild_id = %s"
    users_query = "SELECT user_id, reason FROM blacklistedUser WHERE guild_id = %s"

    channels = execute_query(channels_query, (guild_id,))
    roles = execute_query(roles_query, (guild_id,))
    users = execute_query(users_query, (guild_id,))

    return {"channels": channels, "roles": roles, "users": users}


def get_user_level_info(guild_id: str, user_id: str):
    query = """
    SELECT xp, customBackground FROM level 
    WHERE guild_id = %s AND user_id = %s
    """
    params = (guild_id, user_id)
    result = execute_query(query, params)
    scaling = get_xp_scaling(guild_id)
    custom_formula = get_custom_formula(guild_id)
    if result:
        xp, custom_background = result[0]
        level = get_level_for_xp(
            xp,
            scaling,
            custom_formula
        )
        xp_needed = get_xp_for_level(
            level,
            scaling,
            custom_formula
        ) 
        return {
            "xp": xp,
            "level": level,
            "xp_needed": xp_needed,
            "customBackground": custom_background,
        }
    return None


def set_custom_background(guild_id: str, user_id: str, background_url: str):
    query = """
    INSERT INTO level (guild_id, user_id, customBackground) 
    VALUES (%s, %s, %s)
    ON DUPLICATE KEY UPDATE customBackground = VALUES(customBackground)
    """
    params = (guild_id, user_id, background_url)
    execute_action(query, params)
