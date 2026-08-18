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
            missing_count = clean_df[col].isnull().sum()
            if pd.api.types.is_numeric_dtype(clean_df[col]) == True:
                fill_value = clean_df[col].median()
                clean_df[col] = clean_df[col].fillna(fill_value)
                before_sample = f"{missing_count} missing values"
                after_sample = f"filled with median {fill_value}"
            else:
                fill_value = clean_df[col].mode()[0]
                clean_df[col] = clean_df[col].fillna(fill_value)
                before_sample = f"{missing_count} missing values"
                after_sample = f"filled with most common value '{fill_value}'"
        elif action == "drop":
            before_sample = "column present"
            clean_df = clean_df.drop(columns=[col])
            after_sample = "column removed"
        elif action == "reformat":
            if pd.api.types.is_numeric_dtype(clean_df[col]) == True:
                Q1 = clean_df[col].quantile(0.25)
                Q3 = clean_df[col].quantile(0.75)
                LC = Q1 - 1.5*(Q3-Q1)
                UC = Q3 + 1.5*(Q3-Q1)
                num_out = (clean_df[col] < LC).sum() + (clean_df[col] > UC).sum()
                min_df_before = clean_df[col].min()
                max_df_before = clean_df[col].max()
                clean_df[col] = clean_df[col].clip(lower=LC, upper=UC)
                min_df_after = clean_df[col].min()
                max_df_after = clean_df[col].max()
                before_sample = f"{num_out} outliers, min/max {min_df_before}/{max_df_before}"
                after_sample = f"min/max {min_df_after}/{max_df_after}"
            else:
                exp_bef = clean_df[col].iloc[0]
                clean_df[col] = clean_df[col].str.strip()
                clean_df[col] = clean_df[col].str.lower()
                exp_aft = clean_df[col].iloc[0]
                before_sample = f"first row: '{exp_bef}'"
                after_sample = f"first row: '{exp_aft}'"
        changes.append({
            "column": col,
            "action": action,
            "reason": info["reason"],
            "risk": info["risk"],
            "before_sample": before_sample,
            "after_sample": after_sample,
        })
    return clean_df, changes


if __name__ == "__main__":
    from data.profiling import profile_dataset
    from agent.cleaning_agent import get_cleaning_recommendations
    from audit.logger import write_audit_log

    df = pd.read_csv("top_reviewed_businesses.csv")
    profile = profile_dataset(df)
    recommendations = get_cleaning_recommendations(profile)
    clean_df, changes = apply_cleaning(df, recommendations)
    write_audit_log(changes)

    cols_to_check = [c for c in ["stars", "review_count"] if c in clean_df.columns]
    if cols_to_check:
        print("ORIGINAL:\n", df[cols_to_check].describe())
        print("CLEANED:\n", clean_df[cols_to_check].describe())
    else:
        print("stars and review_count were both dropped this run — nothing to compare.")

    print("CHANGES:", changes)
    print("CLEANED SHAPE:", clean_df.shape)