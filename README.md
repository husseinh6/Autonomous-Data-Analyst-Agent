# Autonomous Data Analyst Agent

AI agent that profiles and cleans a messy dataset, answers natural-language
questions about it by generating and executing SQL, and validates its own
output rather than presenting everything as equally trustworthy.

Built on the Claude API / Agent SDK. Deployed on Streamlit Community Cloud.

Full plan, decisions, and glossary: see `Plan.md` and `Technical Design.md`
in the project's Obsidian vault (not committed here — private working notes).

## Setup

\`\`\`bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # then fill in your real API key + DB credentials
streamlit run app.py
\`\`\`

## Status

Week 1, Day 1 — repo scaffolded, packages not yet installed locally.
