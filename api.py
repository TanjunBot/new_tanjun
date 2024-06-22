import mysql.connector
from config import database_ip, database_password, database_user, database_schema

def create_tables():
    tables = {}
    tables['warnings'] = (
        "CREATE TABLE IF NOT EXISTS `warnings` ("
        "  `id` INT AUTO_INCREMENT PRIMARY KEY,"
        "  `user_id` BIGINT NOT NULL,"
        "  `reason` VARCHAR(255),"
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

def add_warning(user_id, reason):
    query = "INSERT INTO warnings (user_id, reason) VALUES (%s, %s)"
    params = (user_id, reason)
    execute_query(query, params)

def get_warnings(user_id):
    query = "SELECT COUNT(*) FROM warnings WHERE user_id = %s"
    params = (user_id,)
    result = execute_query(query, params)
    return result[0][0]

def clear_warnings(user_id):
    query = "DELETE FROM warnings WHERE user_id = %s"
    params = (user_id,)
    execute_query(query, params)