import mysql.connector
from config import database_ip, database_password, database_user, database_schema
import json


def create_tables():
    tables = {}
    tables["warnings"] = (
        "CREATE TABLE IF NOT EXISTS `warnings` ("
        "  `id` INT AUTO_INCREMENT PRIMARY KEY,"
        "  `guild_id` BIGINT NOT NULL,"
        "  `user_id` BIGINT NOT NULL,"
        "  `reason` VARCHAR(255),"
        "  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,"
        "  `expires_at` TIMESTAMP NULL,"
        "  `escalation_level` INT DEFAULT 0"
        ") ENGINE=InnoDB"
    )
    tables["warn_config"] = (
        "CREATE TABLE IF NOT EXISTS `warn_config` ("
        "  `guild_id` BIGINT PRIMARY KEY,"
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
        "  `channel_id` BIGINT NOT NULL,"
        "  `role_id` BIGINT NOT NULL,"
        "  `overwrites` JSON,"
        "  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP"
        ") ENGINE=InnoDB"
    )
    tables["message_tracking_opt_out"] = (
        "CREATE TABLE IF NOT EXISTS `message_tracking_opt_out` ("
        "  `user_id` VARCHAR(20) PRIMARY KEY"
        ") ENGINE=InnoDB"
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


def execute_query(query, params=None):
    connection = mysql.connector.connect(
        host=database_ip,
        user=database_user,
        password=database_password,
        database=database_schema,
    )
    cursor = connection.cursor()
    cursor.execute(query, params)
    result = cursor.fetchall()
    connection.commit()
    cursor.close()
    connection.close()
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