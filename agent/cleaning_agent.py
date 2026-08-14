"""
Cleaning agent — week 2.

Takes a profiling summary (from data/profiling.py) and asks Claude for a
structured JSON recommendation per column (impute/drop/reformat + reason +
risk level). Does not touch the raw dataframe directly.

Not yet implemented.
"""

import json
from client import get_client

def get_cleaning_recommendations(profile):
    client = get_client()
    prompt = f"""You are a data cleaning assistant. Here is a profile of a dataset:

{profile}

For each column, recommend one action: "impute", "drop", or "reformat".
Give a short reason and a risk level of "low", "medium", or "high".

Respond with ONLY valid JSON, nothing else — no explanation, no markdown
code fences. Use this exact structure:
{{"column_name": {{"action": "...", "reason": "...", "risk": "..."}}}}
"""
    response = client.messages.create(
        model="claude-sonnet-5",
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}],
    )
    reply_text = response.content[0].text
    return json.loads(reply_text)
    
    
if __name__ == "__main__":
    fake_profile = {
        "age": {"dtype": "float64", "missing_pct": 12.5, "n_unique": 40},
        "email": {"dtype": "object", "missing_pct": 0, "n_unique": 998},
    }
    result = get_cleaning_recommendations(fake_profile)
    print(result)