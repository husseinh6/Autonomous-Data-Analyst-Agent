"""
Autonomous Data Analyst Agent — Streamlit entrypoint.

Two capabilities, wired into one app:
1. Upload a messy CSV -> get a data-quality report + cleaned dataset,
   every change logged with a reason (data/profiling.py, agent/
   cleaning_agent.py, data/cleaning.py, audit/logger.py).
2. Ask a natural-language question about the Yelp database -> get a
   plain-English answer + chart, generated SQL run behind the scenes
   with guardrails (agent/sql_agent.py, db/connection.py).
"""
import os
import tempfile
import streamlit as st

# --- Bridge Streamlit Cloud's secrets into os.environ ---
# Locally, .env + python-dotenv populate os.environ, and every module
# below reads config via os.getenv(...). Streamlit Community Cloud has no
# .env file — secrets live in st.secrets instead, and don't become
# os.environ automatically. Copying them over here means the exact same
# os.getenv(...) calls work unchanged in both places. Locally, st.secrets
# is just empty (no secrets.toml file), so this block does nothing and
# .env keeps working exactly as before.
try:
	has_secrets = len(st.secrets) > 0
except Exception:
	# No secrets.toml at all (normal for local dev) — some Streamlit
	# versions raise here instead of just returning empty. Either way,
	# no secrets to bridge, so fall through to the local .env path.
	has_secrets = False

if has_secrets:
	for key, value in st.secrets.items():
		os.environ[key] = str(value)

	# mysql-connector-python's ssl_ca needs a file *path*, not raw PEM
	# text, so write the cert content (stored as a secret) to a temp file
	# once at startup and point DB_SSL_CA at that file.
	if "DB_SSL_CA_CONTENT" in st.secrets:
		ca_file = tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".pem")
		ca_file.write(st.secrets["DB_SSL_CA_CONTENT"])
		ca_file.close()
		os.environ["DB_SSL_CA"] = ca_file.name

import pandas as pd
from data.profiling import profile_dataset
from agent.cleaning_agent import get_cleaning_recommendations
from data.cleaning import apply_cleaning
from audit.logger import write_audit_log
from data.report import generate_report
from agent.sql_agent import generate_sql, generate_answer, build_chart
from db.connection import run_sql_query
from agent.validation import validate

st.title("Autonomous Data Analyst Agent")
st.caption("Upload a messy CSV for automatic profiling and cleaning, or ask a question about the Yelp database in plain English — no SQL required.")

st.header("1. Clean a dataset")
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

	st.subheader("Data-quality report")
	changes_table = pd.DataFrame(changes)
	st.dataframe(changes_table)

	with st.expander("Full text report"):
		st.text(report)

	st.subheader("Cleaned data")
	st.dataframe(clean_df)

st.header("2. Ask a question")
question = st.text_input("Ask a question about the Yelp database")
if st.button("Get answer"):
	sql = generate_sql(question)
	columns, rows = run_sql_query(sql)
	answer = generate_answer(question, columns, rows)
	chart = build_chart(columns, rows)
	validation_result = validate(question, sql, columns, rows)

	st.subheader("Answer")
	st.write(answer)
	st.plotly_chart(chart)

	if validation_result["risk"] == "high":
		reason_only = validation_result["llm_check"].split("\n", 1)[1]
		st.error(f"Low confidence in this answer: {reason_only}")
	elif validation_result["risk"] == "medium":
		st.warning("Some concerns with this answer — worth double-checking.")

	with st.expander("Generated SQL"):
		st.code(sql, language="sql")
