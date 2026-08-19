"""
Data-quality report generation — week 2 (Wed Aug 19).

Turns a profile (from data/profiling.py) and a changes list (from
data/cleaning.py's apply_cleaning) into one readable text report —
what was found per column, and what was done about it. No new
analysis here, just presenting what's already been computed elsewhere
in a form a human can actually read.

Not yet implemented.
"""


def generate_report(profile, changes):
	list_of_lines =[]
	list_of_lines.append(f"Rows: {profile['Total Rows']}, Columns: {profile['Total columns']}, Duplicates: {profile['Number of duplicates']}")
	for change in changes:
		col = change["column"]
		profile_col = profile[col]
		list_of_lines.append(f"Column name: {col}, number of missing values: {profile_col['Missing values']}, Percentage of missing values: {profile_col['Missing values percentage']}, Number of unique values: {profile_col['Number of unique values']}, Number of outliers: {profile_col['Number of outliers']}, Action taken: {change['action']}, Reason: {change['reason']}, Risk: {change['risk']}, Before the sample: {change['before_sample']}, After the sample: {change['after_sample']}")
		
	
	list_of_lines = "\n".join(list_of_lines)
	return list_of_lines
	
	
	
if __name__ == "__main__":
    from data.profiling import profile_dataset
    from agent.cleaning_agent import get_cleaning_recommendations
    from data.cleaning import apply_cleaning
    import pandas as pd

    df = pd.read_csv("top_reviewed_businesses.csv")
    profile = profile_dataset(df)
    recommendations = get_cleaning_recommendations(profile)
    clean_df, changes = apply_cleaning(df, recommendations)

    report = generate_report(profile, changes)
    print(report)