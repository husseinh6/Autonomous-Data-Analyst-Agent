"""
Validation / self-check layer — week 4.

A second, separate Claude call reviewing whether a generated SQL query's
result actually answers the question asked, plus deterministic checks
(row-count sanity, table relevance, SELECT-only enforcement).


"""
import re

from db.connection import get_schema
from agent.client import get_client

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
    
    
    
    
def check_answers_question(question, sql):
    client = get_client()

    prompt = f"""You generated SQL to answer a question. Review it with
fresh eyes, as if someone else wrote it.

Question: {question}
SQL: {sql}

Does this SQL query actually answer the question being asked? Consider
whether it uses the right columns and the right logic, not just whether
it runs without error.

Respond with ONLY one word, "yes" or "no", followed by a short reason
on the next line.
"""

    response = client.messages.create(
        model="claude-sonnet-5",
        max_tokens=256,
        messages=[{"role": "user", "content": prompt}],
    )
    review = next(block.text for block in response.content if block.type == "text")
    return review    
    
    
    
    
def validate(question, sql, columns, rows):
    row_result = check_row_count(rows)
    table_result = check_table_relevance(question, sql)
    llm_result = check_answers_question(question, sql)

    llm_answer = llm_result.strip().split()[0].lower()

    if llm_answer == "no":
        risk = "high"
    elif "warning" in row_result or "warning" in table_result:
        risk = "medium"
    else:
        risk = "low"

    return {
        "risk": risk,
        "row_check": row_result,
        "table_check": table_result,
        "llm_check": llm_result,
    }    
    
    



def check_drop_severity(column, profile_col, action):
    if action != "drop":
        return "ok"
    missing_pct = profile_col["Missing values percentage"]
    if missing_pct < 20:
        return f"warning: dropping '{column}', which is only {missing_pct}% missing — dropping a mostly-complete column may be too aggressive"
    return "ok"
    
    
    
    
def check_cleaning_decision(column, profile_col, recommendation):
    client = get_client()

    prompt = f"""Here you have the column, its profile info and recommended action in this following order.

Column: {column}
Profile info: {profile_col}
Recommended action: {recommendation}

Do you think this is sound decision given the actual data?

Respond with ONLY one word, "yes" or "no", followed by a short reason
on the next line.
"""

    response = client.messages.create(
        model="claude-sonnet-5",
        max_tokens=256,
        messages=[{"role": "user", "content": prompt}],
    )
    review = next(block.text for block in response.content if block.type == "text")
    return review    
    
    
 
 
def validate_cleaning(column, profile_col, recommendation):
    action = recommendation["action"]
    drop_check = check_drop_severity(column, profile_col, action)
    llm_check = check_cleaning_decision(column, profile_col, recommendation)

    llm_answer = llm_check.strip().split()[0].lower()

    if llm_answer == "no":
        risk = "high"
    elif "warning" in drop_check:
        risk = "medium"
    else:
        risk = "low"

    return {
        "risk": risk,
        "drop_check": drop_check,
        "llm_check": llm_check,
    }    
    
    
    
    
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
    question = "Which business has the highest star rating?"
    sql = "SELECT name, review_count FROM business ORDER BY review_count DESC LIMIT 1"
    columns, rows = run_sql_query(sql)
    result = validate(question, sql, columns, rows)
    print(result)
    question2 = "Which city has the most businesses?"
    sql2 = "SELECT city, COUNT(*) AS business_count FROM business GROUP BY city ORDER BY business_count DESC LIMIT 1"
    columns2, rows2 = run_sql_query(sql2)
    result2 = validate(question2, sql2, columns2, rows2)
    print(result2)
    fake_profile_col = {"Missing values percentage": 0.0}
    print(check_drop_severity("stars", fake_profile_col, "drop"))
    fake_recommendation = {"action": "drop", "reason": "3 outliers detected", "risk": "medium"}
    print(validate_cleaning("stars", fake_profile_col, fake_recommendation))
    fake_recommendation2 = {"action": "reformat", "reason": "3 outliers, cap using IQR bounds", "risk": "low"}
    print(validate_cleaning("stars", fake_profile_col, fake_recommendation2))
    question3 = "Give me the name and star rating of the most-reviewed business."
    sql3 = "SELECT name FROM business ORDER BY review_count DESC LIMIT 1"
    columns3, rows3 = run_sql_query(sql3)
    print(validate(question3, sql3, columns3, rows3))
    