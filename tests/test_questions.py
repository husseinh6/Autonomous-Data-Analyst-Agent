"""
Fixed NL question test set — week 3 Friday.

Each question paired with the known-good SQL already written for the Yelp
project (see Code.md in the Obsidian vault), so agent answers can be
checked against a ground truth.


"""

from agent.sql_agent import generate_sql, generate_answer
from db.connection import run_sql_query

test_questions = [
    "Which city has the most businesses?",
    "Which state has the most businesses?",
    "Which business category has the highest average star rating, among categories with at least 100 businesses?",
    "How many reviews were left each year?",
    "What are the top 10 businesses by number of reviews?"
]

for question in test_questions:
    print("QUESTION:", question)
    sql = generate_sql(question)
    print("SQL:", sql)
    columns, rows = run_sql_query(sql)
    print("RESULT:", rows)
    answer = generate_answer(question, columns, rows)
    print("ANSWER:", answer)
    print("---")
