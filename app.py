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

# Your code goes here.

st.title("Autonomous Agent Streamlit")
st.caption("Building the empty shell of the app: page loads, CSV upload button, blank results area. Just proving the plumbing works end to end.")
uploaded_file = st.file_uploader("Upload a CSV file", type="csv")
if uploaded_file == None:
	st.write("NO FILE UPLOADED")
else:
	st.write(f"{uploaded_file.name} UPLOADED SUCCESSFULLY")