"""
Cleaning agent — week 2.

Takes a profiling summary (from data/profiling.py) and asks Claude for a
structured JSON recommendation per column (impute/drop/reformat + reason +
risk level). Does not touch the raw dataframe directly.

Not yet implemented.
"""

import json
from agent.client import get_client

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
    max_attempts = 3
    for attempt in range(max_attempts):
        response = client.messages.create(
            model="claude-sonnet-5",
            max_tokens=2048,
            messages=[{"role": "user", "content": prompt}],
        )
        reply_text = next(block.text for block in response.content if block.type == "text")
        try:
            return json.loads(reply_text)
        except json.JSONDecodeError:
            if attempt == max_attempts - 1:
                raise
            continue
    
    
if __name__ == "__main__":
    import pandas as pd
    from data.profiling import profile_dataset

    df = pd.read_csv("top_reviewed_businesses.csv")
    profile = profile_dataset(df)
    result = get_cleaning_recommendations(profile)
    print(result)