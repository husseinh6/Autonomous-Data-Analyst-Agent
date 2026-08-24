"""
MySQL connection + schema introspection.

Read-only connection to yelp_db (local for dev, trimmed cloud subset for
the deployed demo — see Technical Design.md Section 1). Dedicated
read-only DB user only; SELECT-only enforced at both the DB grant level
and in application code.


"""

import os
from dotenv import load_dotenv
import mysql.connector

def get_connection():
    load_dotenv()
    host = os.getenv("DB_HOST")      
    user = os.getenv("DB_USER")
    password = os.getenv("DB_PASSWORD")
    database = os.getenv("DB_NAME")

    conn = mysql.connector.connect(
        host=host,
        user=user,
        password=password,
        database=database,
    )
    return conn
    
    
    
    
    
def get_schema():
    conn = get_connection()
    cursor = conn.cursor()

    sql = """
        SELECT table_name, column_name, data_type
        FROM information_schema.columns
        WHERE table_schema = 'yelp_db'
    """
    cursor.execute(sql)
    rows = cursor.fetchall()

    schema = {}
    for row in rows:
        table_name, column_name, data_type = row
        if table_name in schema:
            tuple_add = (column_name, data_type)
            schema[table_name].append(tuple_add)
        else:
            schema[table_name] = [(column_name, data_type)]

    cursor.close()
    conn.close()
    return schema
    
    
if __name__ == "__main__":
    conn = get_connection()
    print(conn)
    print("Connected:", conn.is_connected())
    schema = get_schema()
    print(schema)
    conn.close()