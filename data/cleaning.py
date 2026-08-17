"""
Cleaning execution — week 2.

Applies the cleaning agent's structured recommendations to the real
dataframe (impute, dedupe, reformat) and produces audit-trail entries for
every change made.

Not yet implemented.
"""
import numpy as np
import pandas as pd

def apply_cleaning(df, recommendations):
    clean_df = df.copy()
    clean_df = clean_df.drop_duplicates()
    changes = []

    for col, info in recommendations.items():
        action = info["action"]
        if action == "impute":
            if pd.api.types.is_numeric_dtype(clean_df[col]) == True:
                clean_df[col] = clean_df[col].fillna(clean_df[col].median())
            else:
                clean_df[col] = clean_df[col].fillna(clean_df[col].mode()[0])
        elif action == "drop":
            clean_df = clean_df.drop(columns=[col])
        elif action == "reformat":
            if pd.api.types.is_numeric_dtype(clean_df[col]) == True:
                Q1 = clean_df[col].quantile(0.25)
                Q3 = clean_df[col].quantile(0.75)
                LC = Q1 - 1.5*(Q3-Q1)
                UC = Q3 + 1.5*(Q3-Q1)
                clean_df[col] = clean_df[col].clip(lower=LC, upper=UC)
            else:
                clean_df[col] = clean_df[col].str.strip()
                clean_df[col] = clean_df[col].str.lower()
        changes.append({"column": col, "action": action, "reason": info["reason"]})
    return clean_df, changes


if __name__ == "__main__":
    import pandas as pd2  # not needed if you already import pandas as pd above
    from data.profiling import profile_dataset
    from agent.cleaning_agent import get_cleaning_recommendations

    df = pd.read_csv("top_reviewed_businesses.csv")
    profile = profile_dataset(df)
    recommendations = get_cleaning_recommendations(profile)
    clean_df, changes = apply_cleaning(df, recommendations)
    print("ORIGINAL:\n", df[["stars", "review_count"]].describe())
    print("CLEANED:\n", clean_df[["stars", "review_count"]].describe())

    print("CHANGES:", changes)
    print("CLEANED SHAPE:", clean_df.shape)