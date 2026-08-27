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


def generate_answer(question, columns, rows):
    client = get_client()

    prompt = f"""You were asked this question about a database: {question}

The query returned these columns: {columns}
And these rows: {rows}

Write a short, plain-English sentence answering the question, using the
actual data above. Do not mention SQL, columns, or rows — just answer
naturally, like a person would.
"""

    response = client.messages.create(
        model="claude-sonnet-5",
        max_tokens=256,
        messages=[{"role": "user", "content": prompt}],
    )
    answer = next(block.text for block in response.content if block.type == "text")
    return answer
    
    
    
import plotly.express as px

def build_chart(columns, rows):
    labels = []
    values = []
    for row in rows:
        labels.append(row[0])
        values.append(row[1])

    fig = px.bar(x=labels, y=values, labels={"x": columns[0], "y": columns[1]})
    return fig

if __name__ == "__main__":
    question = "What are the top 5 cities by number of businesses?"
    sql = generate_sql(question)
    from db.connection import run_sql_query

    columns, rows = run_sql_query(sql)
    answer = generate_answer(question, columns, rows)
    chart = build_chart(columns, rows)
    chart.show()
    print(answer)
    print(columns)
    print(rows)
    print(sql)