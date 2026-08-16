"""
Dataset profiling — week 1 (Thu Aug 13).

Plain pandas, no LLM involved: missing %, dtypes, duplicate count, outlier
flags per column. Output feeds the cleaning agent's prompt.
"""
import pandas as pd


def profile_dataset(df):
	profile = {}
	rows, columns = df.shape
	num_dupl = df.duplicated().sum()
	profile = {"Total Rows": rows, "Total columns": columns, "Number of duplicates": num_dupl}
	for i in df.columns:
		col_type = df[i].dtype
		num_missing = df[i].isnull().sum()
		miss_perc = (num_missing / rows)*100
		num_unique = df[i].nunique()
		num_out = None
		if pd.api.types.is_numeric_dtype(df[i]):
			Q1 = df[i].quantile(0.25)
			Q3 = df[i].quantile(0.75)
			num_out = (df[i] < Q1 - 1.5*(Q3-Q1)).sum() + (df[i] > Q3 + 1.5*(Q3-Q1)).sum()
			
		profile[i] = {"Column Type": col_type, "Missing values": num_missing, "Missing values percentage": miss_perc, "Number of unique values": num_unique, "Number of outliers": num_out} 
	return profile

if __name__ == "__main__":
	print(profile_dataset(pd.read_csv("top_reviewed_businesses.csv")))
