# Case study notes — running log

Notes captured as the project progresses, to feed the eventual Notion
write-up (week 6). Not the write-up itself — just raw material: what
worked, what broke, what the agent got wrong.

## 2026-08-10 — Week 1, Day 1
- Repo scaffolded, technical design signed off.
- Open decision resolved: full yelp_db stays local for dev; a trimmed
  subset gets deployed to a free-tier cloud MySQL for the public demo.
- Packages installed locally (venv), repo pushed to GitHub
  (husseinh6/Autonomous-Data-Analyst-Agent).
- Anthropic API key created, rotated once after being visible in a
  screenshot (safe practice, no actual exposure risk since caught
  immediately), saved to local .env. Monthly spend limit set (Anthropic
  doesn't offer a lifetime cap — monthly is the available mechanism).
- Day 1 (repo/packages/API key/spend cap) complete. Aiven cloud DB setup
  deliberately deferred to closer to deployment (week 6) — not needed yet.
- Next: Tue Aug 11 — Streamlit skeleton (page loads, upload button, blank
  results area), per Plan.md Week 1.

## 2026-08-11 — Week 1, Day 2 (Tuesday)
- Streamlit skeleton built — title, caption, CSV-only file uploader,
  results area that shows "NO FILE UPLOADED" or "<filename> UPLOADED
  SUCCESSFULLY" depending on upload state. Verified working in browser.
- Build mode decision: Hamsa writes the code by hand, Claude explains
  concepts/reviews/debugs rather than writing it directly — first time
  using Streamlit. Fallback: if a task is taking too long, Claude can
  finish the remainder to keep pace with the plan.
- First-pass bugs (all self-corrected with guidance, good sign): using
  `input()`/`print()` out of habit from plain Python scripts instead of
  Streamlit's `st.*` calls; case-sensitivity slips (`St`/`If`/`Else`,
  `X` vs `x`); `=` vs `==`; `NONE` vs `None`; passing `str` (the type)
  instead of a label string; `<var>` instead of an f-string `{var}` for
  interpolation — all standard first-exposure mistakes, not concerning.
- Day 2 complete. Next per Plan.md: Thu Aug 13 — core profiling code
  (pandas: missing %, dtypes, duplicates, outliers). Wed Aug 12 has no
  scheduled task.

## 2026-08-12 — Week 1, Day 3 (Wednesday — Thursday's task pulled forward)
- Wed had no scheduled task per the plan; pulled Thursday's core profiling
  code forward instead of taking the day off, since the energy was there.
- Built `profile_dataset(df)` in `data/profiling.py`: row/column counts,
  duplicate count, per-column dtype/missing-count/missing-%/unique-count,
  and per-column outlier count via the 1.5×IQR rule (numeric columns
  only, `None` for non-numeric). Tested against `top_reviewed_businesses.csv`
  — correct output (50 rows, 5 cols, 0 duplicates, outliers flagged
  correctly on `stars`/`review_count`, `None` on text columns).
- Bugs found and self-corrected: column-name vs column-data confusion
  (`df[i]` vs bare `i`), `I`/`i` case slips (recurring pattern — worth
  double-checking capitalization as a habit going forward), dict key set
  to the literal string `"i"` instead of the variable's value, `df.rows`
  doesn't exist (switched to vectorized boolean-mask + `.sum()` instead
  of a manual loop — good instinct once shown the pattern), stale/unset
  variable across loop iterations (`num_out` needed a default before the
  numeric check), `NONE` vs `None`.
- One structural bug was Claude's fault, not Hamsa's: the original file
  stub's docstring was never closed, so all of Hamsa's code silently
  landed inside a string literal and never executed (no output, no
  error). Claude fixed the file structure directly rather than having
  Hamsa debug something that wasn't his mistake.
- Day 3 complete, ahead of schedule (Thursday's task done Wednesday).
  Next per Plan.md: Fri Aug 14 — first real agent call (profile → Claude
  → structured cleaning recommendations), the highest-risk task of week 1.

## 2026-08-14 — Week 1, Day 4 (Friday) — first real agent call
- Built `agent/client.py` (`get_client()` — loads the API key via
  `python-dotenv`, returns an authenticated Anthropic client) and tested
  it standalone first with a trivial "say hello" call before touching
  anything more complex — isolated "is the connection working" from "is
  the prompt working." Worked on the first attempt.
- Built `agent/cleaning_agent.py` (`get_cleaning_recommendations(profile)`
  — takes a profile dict, prompts Claude for a structured JSON
  recommendation per column with action/reason/risk level, parses the
  reply with `json.loads`). Tested against a small hand-written fake
  profile (not yet wired to Wednesday's real `profile_dataset` output —
  that integration is future work, not today's scope).
- Result: worked correctly on the first real attempt — valid JSON,
  sensible reasoning (e.g. correctly distinguished a numeric column
  needing imputation from a text column needing reformatting). No bugs
  to debug this session — the flagged highest-risk task of week 1 landed
  cleanly.
- Model used: `claude-sonnet-5`. Prompt explicitly demands JSON-only
  output (no markdown fences, no explanation) — this instruction is
  doing real work, not just politeness, since `json.loads` fails on any
  stray text around the JSON.
- Week 1's deep-work tasks (Mon-Fri) are now all complete, with Thursday
  finished a day early. Sun Aug 16 remains: review, tidy, plan week 2 —
  also the checkpoint Plan.md flagged for revisiting pace/scope.
