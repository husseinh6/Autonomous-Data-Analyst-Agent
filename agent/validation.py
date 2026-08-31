"""
Validation / self-check layer — week 4.

A second, separate Claude call reviewing whether a generated SQL query's
result actually answers the question asked, plus deterministic checks
(row-count sanity, table relevance, SELECT-only enforcement).


"""
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
        if table_name.lower() in sql_lower:
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
    list1 = []
    list2 = []
    list3 = [1,2,3,4]
    for i in range(1000):
        list2.append(i)
    print(check_row_count(list1))
    print(check_row_count(list2))
    print(check_row_count(list3))
    question = "What is the busiest day of the week for check-ins?"
    sql = "SELECT COUNT(*) FROM tip"
    print(check_table_relevance(question, sql))
    
    
    
    