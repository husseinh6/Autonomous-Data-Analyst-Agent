"""
NL-to-SQL agent — week 3.

Takes a natural-language question, generates SQL grounded in the DB schema
(via db/connection.py get_schema), executes it read-only, and returns a
plain-English answer + chart spec.


"""
from agent.client import get_client
from db.connection import get_schema

def generate_sql(question):
    schema = get_schema()
    client = get_client()

    prompt = f"""You are a SQL assistant. Here is the schema of a MySQL database:

{schema}

Given this schema, write a single SQL SELECT query that answers the
following question:

{question}

Respond with ONLY the SQL query, nothing else — no explanation, no
markdown code fences, no semicolon-terminated multiple statements.
"""

    response = client.messages.create(
        model="claude-sonnet-5",
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}],
    )
    sql_query = next(block.text for block in response.content if block.type == "text")
    sql_query = sql_query.replace("```sql", "").replace("```", "").strip()
    return sql_query


if __name__ == "__main__":
    question = "Which city has the most businesses?"
    sql = generate_sql(question)
    from db.connection import run_sql_query

    columns, rows = run_sql_query(sql)
    print(columns)
    print(rows)
    print(sql)