import mysql.connector
from config import database_ip, database_password, database_user, database_schema
import json

def create_tables():
    tables = {}
    tables['warnings'] = (
        "CREATE TABLE IF NOT EXISTS `warnings` ("
        "  `id` INT AUTO_INCREMENT PRIMARY KEY,"
        "  `guild_id` BIGINT NOT NULL,"
        "  `user_id` BIGINT NOT NULL,"
        "  `reason` VARCHAR(255),"
        "  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP"
        ") ENGINE=InnoDB"
    )
    tables['channel_overwrites'] = (
        "CREATE TABLE IF NOT EXISTS `channel_overwrites` ("
        "  `id` INT AUTO_INCREMENT PRIMARY KEY,"
        "  `channel_id` BIGINT NOT NULL,"
        "  `role_id` BIGINT NOT NULL,"
        "  `overwrites` JSON,"
        "  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP"
        ") ENGINE=InnoDB"
    )
    
    connection = mysql.connector.connect(
        host=database_ip,
        user=database_user,
        password=database_password,
        database=database_schema
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
        database=database_schema
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
        database=database_schema
    )
    cursor = connection.cursor()
    cursor.execute(query, params)
    connection.commit()
    cursor.close()
    connection.close()

def add_warning(guild_id, user_id, reason):
    query = "INSERT INTO warnings (guild_id, user_id, reason) VALUES (%s, %s, %s)"
    params = (guild_id, user_id, reason)
    execute_action(query, params)

def get_warnings(guild_id, user_id):
    query = "SELECT COUNT(*), GROUP_CONCAT(reason SEPARATOR '|') FROM warnings WHERE guild_id = %s AND user_id = %s"
    params = (guild_id, user_id)
    result = execute_query(query, params)
    count, reasons = result[0]
    reasons_list = reasons.split('|') if reasons else []
    return count, reasons_list

def clear_warnings(guild_id, user_id):
    query = "DELETE FROM warnings WHERE guild_id = %s AND user_id = %s"
    params = (guild_id, user_id)
    execute_action(query, params)

def get_detailed_warnings(guild_id, user_id):
    query = "SELECT id, reason, created_at FROM warnings WHERE guild_id = %s AND user_id = %s ORDER BY created_at DESC"
    params = (guild_id, user_id)
    result = execute_query(query, params)
    return [(row[0], row[1], row[2]) for row in result]

def remove_warning(warning_id):
    query = "DELETE FROM warnings WHERE id = %s"
    params = (warning_id,)
    execute_action(query, params)

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