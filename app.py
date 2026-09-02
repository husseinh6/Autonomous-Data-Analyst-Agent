"""
Autonomous Data Analyst Agent — Streamlit entrypoint.

Today's task (Tue Aug 11, Week 1): page loads, upload button, blank
results area. No profiling/cleaning/agent logic yet.

TODO (Hamsa, Tue Aug 11):
1. Give the page a title and a short caption.
2. Add a file uploader that only accepts .csv files.
3. Below it, show a placeholder message if nothing's been uploaded yet,
   or a "received: <filename>" message if something has.
"""
import streamlit as st
import pandas as pd
from data.profiling import profile_dataset
from agent.cleaning_agent import get_cleaning_recommendations
from data.cleaning import apply_cleaning
from audit.logger import write_audit_log
from data.report import generate_report

# Your code goes here.

st.title("Autonomous Agent Streamlit")
st.caption("Building the empty shell of the app: page loads, CSV upload button, blank results area. Just proving the plumbing works end to end.")
uploaded_file = st.file_uploader("Upload a CSV file", type="csv")
if uploaded_file == None:
	st.write("NO FILE UPLOADED")
else:
	df = pd.read_csv(uploaded_file)
	profile = profile_dataset(df)
	recommendations = get_cleaning_recommendations(profile)
	clean_df, changes = apply_cleaning(df, recommendations)
	report = generate_report(profile, changes)
	write_audit_log(changes)
	st.text(report)
	st.dataframe(clean_df)
