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

## 2026-08-16 — Week 1, Day 5 (Sunday) — checkpoint + tidy
- Pace check-in: every task this week finished under estimate (~1h-1.5h
  actual vs ~2-2.5h estimated). Read as week 1 covering well-trodden,
  forgiving territory (Streamlit basics, pandas, a single API call)
  rather than the plan being miscalibrated — harder weeks ahead (SQL
  agent, validation layer) likely to eat into that margin more. No
  changes made to weeks 2-6 — decided to keep re-assessing weekly rather
  than adjusting pre-emptively off one easy week.
- Concept review: walked back through Friday's `client.py`/
  `cleaning_agent.py` and Wednesday's `profile_dataset` in plain terms
  (Hamsa was unwell Friday and flagged gaps in understanding on his own
  initiative — good habit, kept up).
- Closed the real gap from Friday: wired `profile_dataset`'s actual
  output into `get_cleaning_recommendations` for the first time (Friday
  only tested against a hand-written fake profile). Required switching
  `cleaning_agent.py`'s import style from same-folder (`from client
  import ...`) to package-style (`from agent.client import ...`, `from
  data.profiling import ...`) and running via `python3 -m
  agent.cleaning_agent` from the project root instead of running the
  file path directly — needed once imports had to reach across sibling
  folders (`agent/` and `data/`) rather than staying within one.
- Two real bugs surfaced testing against the real profile (neither
  Hamsa's fault — both API/response-handling edge cases):
  1. `profiling.py`'s leftover test `print(...)` was never guarded by
     `if __name__ == "__main__":`, so importing it elsewhere (as
     `cleaning_agent.py` now does) fired it as a side effect. Fixed.
  2. `response.content[0].text` assumed position 0 is always the text
     block; this run, Claude returned a `ThinkingBlock` first. Fixed by
     searching `response.content` for whichever block has
     `type == "text"` instead of assuming a fixed position. A first
     retry after that fix hit a `JSONDecodeError` (empty reply text) —
     resolved itself on the next attempt; added a temporary debug print
     to inspect `stop_reason`/content blocks directly rather than guess,
     confirmed a clean `end_turn` with valid JSON, then removed the
     debug lines. Root cause of that one transient failure unconfirmed —
     flagged as a "LLM calls aren't fully deterministic" reminder for
     the validation layer (week 4) rather than chased further today.
- Real result on the actual Yelp export: Claude recommended "reformat"
  across all 5 columns (text standardization for `name`/`city`/`state`,
  outlier handling for `stars`/`review_count`) — sensible given the real
  profile has 0% missing everywhere, so "impute" correctly never came up
  (unlike Friday's fake profile, which did have a missing column).
- Week 1 fully closed: all deep-work tasks done, pipeline genuinely
  connected end-to-end for the first time (CSV → profile → Claude →
  structured recommendations), checkpoint passed with no plan changes.
  Week 2 tasks being added to Notion next.

## 2026-08-17 — Week 2, Day 1 (Monday) — apply cleaning recommendations
- Built `apply_cleaning(df, recommendations)` in `data/cleaning.py`:
  drops exact duplicate rows automatically (not gated on a Claude
  recommendation — duplicates were never part of the recommendation
  schema to begin with, see design note below), then per column applies
  impute (median for numeric, mode for text), drop (remove the column),
  or reformat (numeric: clip to the same 1.5×IQR bounds used for outlier
  detection in profiling; text: strip whitespace + lowercase). Returns
  the cleaned dataframe plus a plain `changes` list (one entry per
  column) — full audit-trail file format is tomorrow's task.
- Design note worth remembering: `get_cleaning_recommendations`'s prompt
  only ever asks Claude for a per-column action (impute/drop/reformat)
  — duplicate rows were never part of that schema, and "reformat" itself
  is a deliberately vague bucket covering different real fixes per
  column (text standardization vs outlier handling in practice so far).
  The code has to pick a concrete rule for what vague labels mean;
  documented as a heuristic, not a perfect interpretation of Claude's
  reasoning text.
- Bugs found and self-corrected, most stemming from one core pandas rule
  (most methods return a new object rather than mutating in place —
  `.drop_duplicates()`, `.clip()`, `.str.strip()`, `.drop(columns=...)`
  all needed explicit reassignment): backwards `fillna(value) = ...`
  syntax (fixed to `col = col.fillna(value)`), `np.issubdtype` called on
  a whole Series instead of its `.dtype` (switched to
  `pd.api.types.is_numeric_dtype` instead — simpler, already known),
  `import pandas` without the `pd` alias while calling `pd.api...`,
  clipping directly to Q1/Q3 instead of the actual IQR bounds (would
  have flattened ~50% of values, not just outliers), a leftover `[...]`
  placeholder in a `.drop(columns=...)` call, and assigning a
  column-drop's result into a single-column slot instead of the whole
  dataframe.
- Verified end-to-end against the real Yelp export via `python3 -m
  data.cleaning`: real profile → real Claude call → real pandas changes
  → shape stayed (50, 5) as expected (0 duplicates, nothing dropped),
  all 5 columns landed on "reformat" again (consistent with Sunday,
  0% missing throughout the dataset).
- One process note: this session's first run failed with
  `ModuleNotFoundError: No module named 'dotenv'` — venv wasn't
  activated in the fresh terminal session (prompt read `(base)` not
  `(venv) (base)`). Reminder to check for `(venv)` before running
  anything, especially at the start of a new day/terminal session.
- Next per Notion/Plan.md: Tue Aug 18 — audit-trail logging (formalize
  today's `changes` list into the real `audit_log.jsonl` file format).
- Sanity-checked the actual cleaning output before trusting it (in the
  spirit of the project's own thesis — don't trust agent output just
  because it ran without error): compared `stars`/`review_count`
  before/after with `.describe()`. Confirmed exactly, not just
  approximately — `stars`'s IQR lower bound works out to 3.25, original
  min was 2.5 (an outlier), cleaned min is precisely 3.25;
  `review_count`'s IQR upper bound works out to 5947.125, original max
  was 7568 (an outlier), cleaned max is precisely 5947.125. Real
  confirmation the clipping logic is exactly correct, not just plausible.
- The `JSONDecodeError` bug from Sunday recurred once more today, same
  signature (empty text reply). Diagnosed properly this time with a
  temporary debug print on `response.usage`: Claude's "thinking" tokens
  count against the same `max_tokens` budget as the actual answer — on
  the successful debug run, thinking used 423 of 720 output tokens,
  leaving comfortable room under the `max_tokens=1024` cap; the theory
  (unconfirmed for the two failed runs specifically, since debug wasn't
  in yet then, but consistent with the evidence) is that thinking
  occasionally used up the entire budget, leaving zero tokens for the
  real answer. Fix: bumped `max_tokens` from 1024 to 2048 in
  `agent/cleaning_agent.py` for real headroom. Debug lines removed after
  diagnosis. Worth remembering as a real reliability gap the validation
  layer (week 4) should account for, not fully eliminated just because
  it hasn't failed since.

## 2026-08-18 — Week 2, Day 2 (Tuesday) — audit-trail logging
- Enriched `apply_cleaning`'s `changes` list (previously just
  column/action/reason) with `risk` (was already returned by Claude,
  never captured) and structured `before_sample`/`after_sample` per
  action type: impute -> missing count / fill value used; drop -> column
  present / removed; reformat-numeric -> min/max and outlier count
  before vs. min/max after (directly shows the clipping effect);
  reformat-text -> one example value before vs. after. Collapsed what
  had briefly been two parallel lists into one list of complete
  per-column dicts — needed as one structured record per change for the
  JSON logger next, and safer than keeping two lists in sync by hand.
- This edit was made by Claude directly (Hamsa asked for it explicitly,
  invoking the established fallback) rather than hands-on — bugs fixed:
  missing-value count captured *after* `fillna` already ran (always
  read 0), `.min`/`.max` called without parentheses (returns the method
  object, not a value), and `clean_df[col[0]]` indexing into the column
  *name* string's first character instead of the dataframe's first row
  (needed `clean_df[col].iloc[0]`).
- Built `audit/logger.py` (`write_audit_log`) — genuinely new territory
  for Hamsa (first exposure to file I/O and JSON in this project), given
  more scaffolding than usual for that reason. Writes one JSON object
  per line to `audit_log.jsonl` in append mode, each entry combining
  `type`/`timestamp` with the change's own fields via dict-unpacking
  (`**change`). Written by Hamsa from a fuller worked example, correct
  on the first attempt — real, valid JSONL output confirmed by reading
  the file directly.
- Significant finding, found by actually running the pipeline rather
  than assuming it worked: on one run, Claude recommended `"drop"` for
  *both* `stars` and `review_count` — core columns with 0% missing,
  whose only issue was 3 outliers each. Dropping them outright is a
  poor call a competent human analyst wouldn't make, and it's the exact
  failure mode named in the plan's own success criteria ("validation
  layer catches... a silently dropped column") — except this happened
  for real, unprompted, not seeded. Across today's several runs alone,
  Claude gave `stars`/`review_count` four different actions on identical
  data (reformat, impute, drop, impute) — real, repeated evidence of
  recommendation inconsistency, not a one-off.
- Hamsa raised a genuinely good design question in response: should the
  app ask for user confirmation before executing risky actions like a
  column drop? Discussed and deliberately declined for now — the plan
  already made this call explicitly ("autonomous by default... validation
  layer double-checks higher-risk changes rather than every single
  decision"), a step-by-step approval loop cuts against the project's
  actual differentiator (an agent that acts, not a copilot that waits),
  and doesn't scale to bigger/messier datasets (Thursday's task).
  Decision: keep full autonomy as planned; this exact `stars`/
  `review_count` drop becomes the first concrete test case for week 4's
  validation layer rather than a hypothetical to design against later.
- Made the test script robust to whatever Claude decides (a list
  comprehension filtering to only columns that still exist before
  comparing before/after stats) rather than assuming any particular
  column survives — confirmed working on a run where the columns
  happened to still exist, so also worth a follow-up real test on a run
  where they don't survive, to be certain.
- Next per Notion/Plan.md: Wed Aug 19 — data-quality report generation.
