# Autonomous Data Analyst Agent

An AI agent that profiles and cleans a messy dataset, and answers natural-language
questions about a live MySQL database by generating and safely executing SQL — paired
with an independent validation layer that catches wrong joins, silently dropped
columns, and answers that don't actually answer the question, instead of presenting
every LLM output as equally trustworthy.

Built on the Claude API. Deployed on Streamlit Community Cloud.

**Live demo:** https://autonomous-data-analyst-agent-guzkkydpxcmsz6erwe9lpz.streamlit.app
*(the app and its database both auto-sleep after a period of inactivity on their free
tiers — if the link shows a "this app has gone to sleep" prompt, click it to wake it
up, and give it a minute)*

**Full case study, architecture, and an honest "where the agent got it wrong" section:**
see the [Notion write-up](https://app.notion.com/p/3db482119d8081f1b944f727e800a2f1).

## What it does

1. **Clean a dataset.** Upload any CSV → the agent profiles it (missing values,
   dtypes, duplicates, outliers), asks Claude for per-column cleaning
   recommendations, applies them, and logs every change with a reason to a JSONL
   audit trail — no black-box "trust me" cleaning.
2. **Ask a question.** Type a plain-English question about the Yelp Open Dataset →
   Claude generates SQL grounded in the real schema, runs it behind guardrails
   (SELECT-only, single-statement, row-limited, timed out, read-only DB user), and
   returns a plain-English answer, a chart, and a confidence flag from the
   validation layer.

## Setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # then fill in your real API key + DB credentials
streamlit run app.py
```

Local dev connects to a full local MySQL copy of the Yelp Open Dataset. The deployed
demo instead points at a small, referential-integrity-preserving subset hosted on
Aiven, since Streamlit Community Cloud can't reach `localhost` — see
`scripts/export_subset_to_aiven.sh` and `.streamlit/secrets.toml.example` for how
that's wired up.

## Tech stack

Python · pandas · Streamlit · Anthropic Claude API · MySQL · mysql-connector-python ·
Plotly · Aiven (cloud MySQL hosting) · Streamlit Community Cloud

## Status

Complete and deployed. Built solo over 6 weeks (Aug–Sep 2026) as a self-directed
portfolio project. Full plan, decisions, and glossary: see `Plan.md` and
`Technical Design.md` in the project's Obsidian vault (not committed here — private
working notes).
