"""
Validation / self-check layer — week 4.

A second, separate Claude call reviewing whether a generated SQL query's
result actually answers the question asked, plus deterministic checks
(row-count sanity, table relevance, SELECT-only enforcement).


"""
import re

from db.connection import get_schema

def check_row_count(rows, row_limit=1000):
    if len(rows) == 0:
        return "warning: query returned 0 rows"
    if len(rows) == row_limit:
        return "warning: results may be truncated at the row limit"
    return "ok"
    
    
def check_table_relevance(question, sql):
    schema = get_schema()
    sql_lower = sql.lower()

    tables_used = []
    for table_name in schema:
        pattern = r"\b" + table_name.lower() + r"\b"
        if re.search(pattern, sql_lower):
            tables_used.append(table_name)

    flagged = []
    for table_name in tables_used:
        keywords = table_name.split("_")
        relevant = False
        for word in keywords:
            if word in question.lower():
                relevant = True
        if not relevant:
            flagged.append(table_name)

    if flagged:
        return f"warning: these tables don't obviously relate to the question: {flagged}"
    return "ok"   
    
    
    
if __name__ == "__main__":
    from db.connection import run_sql_query

    seeded_tests = [
    {
        "label": "wrong join",
        "question": "What is the average star rating per city?",
        "sql": "SELECT business.city, AVG(business.stars) FROM business JOIN tip ON business.business_id = tip.business_id GROUP BY business.city",
    },
    {
        "label": "Impossible filter → zero rows",
        "question": "Which businesses have a star rating above 10?",
        "sql": "SELECT name FROM business WHERE stars > 10",
    },
    {
        "label": "Doesn't actually answer the question",
        "question": "Which business has the highest star rating?",
        "sql": "SELECT name, review_count FROM business ORDER BY review_count DESC LIMIT 1",
    }
    ]

    for test in seeded_tests:
       print(test["label"])
       columns, rows = run_sql_query(test["sql"])
       print("row check:", check_row_count(rows))
       print("table check:", check_table_relevance(test["question"], test["sql"]))
       print("---")
    
    
    
    