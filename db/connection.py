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
    
    
def run_sql_query(sql, row_limit=1000, timeout_ms=5000):
    sql_clean = sql.strip().rstrip(";")
    uppercase_sql = sql_clean.upper()
    if not uppercase_sql.startswith("SELECT"):
        raise ValueError("Only SELECT queries are allowed.")

    if ";" in sql_clean:  # a semicolon left in the middle means multiple statements
        raise ValueError("Multiple statements are not allowed.")

    if "LIMIT" not in sql_clean.upper():
        sql_clean = sql_clean + f" LIMIT {row_limit}"

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(f"SET SESSION MAX_EXECUTION_TIME={timeout_ms}")
    cursor.execute(sql_clean)
    rows = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]
    cursor.close()
    conn.close()
    return columns, rows    
    

    
if __name__ == "__main__":
    conn = get_connection()
    print(conn)
    print("Connected:", conn.is_connected())
    schema = get_schema()
    print(schema)
    columns, rows = run_sql_query("SELECT city, COUNT(*) FROM business GROUP BY city ORDER BY COUNT(*) DESC LIMIT 3")
    print(columns)
    print(rows)
    # test 1: does the LIMIT auto-inject when missing?
    columns, rows = run_sql_query("SELECT * FROM business")
    print("Row count with no LIMIT in query:", len(rows))

    # test 2: does a non-SELECT get rejected?
    try:
        run_sql_query("DELETE FROM business")
    except ValueError as e:
        print("Correctly rejected:", e)
    conn.close()