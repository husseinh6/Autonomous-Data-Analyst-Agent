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

## 2026-08-19 — Week 2, Day 3 (Wednesday) — data-quality report generation
- Built `data/report.py` (`generate_report(profile, changes)`) — a new
  file, not part of the original day-1 scaffold (that only anticipated
  profiling/cleaning/db/audit/tests, not a dedicated report step).
  Combines `profile[col]` (what was found: dtype, missing %, outlier
  count) with the matching `changes` entry (what was done: action,
  reason, risk, before/after) into one readable line per column, plus a
  dataset-level summary line up top. Built by Hamsa largely independently
  — bugs were minor and self-explanatory once flagged (missing `def`,
  appending raw dicts to a list `"\n".join()` expected to be all
  strings — needed f-strings pulling specific values out instead of the
  whole dict, an unterminated f-string missing its closing quote in two
  places, and a `'Total Columns'`/`'Total columns'` casing mismatch
  against the real profiling.py key).
- Recurring issue mitigated properly this time rather than re-debugged:
  the `JSONDecodeError` (empty reply text) from Sunday/Tuesday happened
  a third time today, despite Monday's `max_tokens` bump — confirming
  the note from Monday that it wasn't fully eliminated. Rather than
  diagnose the same known issue again, added a genuine fix: `get_cleaning_
  recommendations` now retries up to 3 times on a JSON parse failure
  before actually raising an error. Standard practice for flaky LLM
  calls; a pragmatic, minimal mitigation rather than the full validation
  layer (still week 4's job for judging recommendation *quality*, not
  just call *reliability*).
- `stars`/`review_count` got `"drop"` again this run — now a well-
  established, previously documented pattern (Tuesday's notes), not
  reflagged in depth here.
- Week 2 progress: Mon (apply cleaning), Tue (audit logging), Wed
  (report generation) all done, each verified against real output, not
  just "ran without error." Next per Notion/Plan.md: Thu Aug 20 — test
  on Yelp export + a second messy CSV, fix bugs.

## 2026-08-20 — Week 2, Day 4 (Thursday) — test on a second messy CSV, fix bugs
- `top_reviewed_businesses.csv` (used all week) turned out to have 0%
  missing values and 0 duplicates throughout — never actually exercised
  the messy-data paths. Built a genuinely messy second file instead:
  `business_sample_messy.csv`, exported from the real `yelp_db.business`
  table via `(SELECT ... WHERE address IS NULL LIMIT 100) UNION ALL
  (SELECT ... WHERE address IS NOT NULL LIMIT 400)` — 500 rows, 11
  columns, 100 genuinely missing addresses by design, not luck.
- First export attempt failed to even load: `attributes` (nested JSON)
  wasn't properly quote-escaped by MySQL Workbench's CSV export, so
  unescaped internal quotes broke the file's column structure entirely
  (`ParserError: Expected 12 fields, saw 14`). Fixed by re-exporting
  without that column — not needed for what's being tested anyway. A
  different, more realistic kind of messy than anything hit before: a
  structurally broken file, not just messy values inside a valid one.
- Full pipeline (profile → Claude → clean → audit → report) ran
  end-to-end on the new 500-row/11-column file with no crash — real
  evidence the code generalizes beyond the narrow 50-row/5-column file
  it was originally built against.
- Two genuine bugs found by actually reading the output, not just
  checking it ran (same principle as every prior "sanity check" this
  project keeps coming back to):
  1. **Serious — `is_open` (binary 0/1) got silently corrupted.**
     IQR-based outlier clipping is meaningless on a column with two
     values: when one class dominates, Q1 and Q3 both land on the
     majority value, the IQR collapses to 0, and the "valid range"
     becomes a single point — so the entire minority class (closed
     businesses) got flagged as "outliers" and clipped to match the
     majority (silently turned into "open"). Real data corruption, not
     a stylistic issue. Fixed in `data/cleaning.py`: skip clipping
     entirely when `IQR == 0`, with an explicit before/after message
     explaining why, rather than silently doing nothing or corrupting
     data.
  2. **`address` got filled with a fabricated duplicate.** Text-column
     imputation used `.mode()` unconditionally — meaningless for a
     near-unique column (400 unique values across 400 non-null rows),
     so it just grabbed an arbitrary single address and copied it into
     100 different businesses' records. Fixed (Hamsa's own design,
     mirroring the IQR-zero fix's logic): only use the mode value if it
     actually represents at least 30% of non-null values; otherwise
     fall back to a `"Unknown"` placeholder. Verified this also
     correctly caught `postal_code` as a case that looked plausible for
     mode-fill by eye but didn't actually clear the 30% bar either —
     the fix judges the real data, not assumptions about it.
  3. **Documented, not fixed today — aggressive clipping on naturally
     skewed data.** `longitude` (68/500 flagged, spans genuinely
     different states) and `review_count` (64/500, max clipped from
     1119 down to 72) both got heavily clipped by simple 1.5×IQR, which
     doesn't distinguish "erroneous extreme value" from "legitimate but
     rare high value." A real methodological limitation of the outlier
     method chosen in week 1, not a quick bug fix — flagged for the
     write-up's limitations section rather than solved today.
- Both fixed bugs directly demonstrate why the audit trail and report
  exist: neither would have been caught by "did it crash" alone, only
  by actually reading what the agent did.
- Week 2 complete except Friday's wrap-up. Next per Notion/Plan.md:
  Fri Aug 21 — review + notes for the case study.

## 2026-08-21 — Week 2, Day 5 (Friday) — review + wrap-up
- Week 2 in one line: the cleaning agent went from "Claude suggests
  actions" (end of week 1) to a full pipeline that actually applies
  changes, logs them, reports on them, and survives real messy data —
  including finding and fixing two genuine bugs along the way, one of
  which was silently corrupting data (`is_open`).
- Pace held up again — every day landed at or under its estimate, no
  plan adjustments needed. Two build-mode moments worth remembering for
  future weeks: (1) purely mechanical/repetitive fixes (the cleaning.py
  before/after enrichment) got handed to Claude directly rather than
  redone by hand once the pattern was already understood; (2) genuinely
  new territory (file I/O and JSON on Tuesday) got more scaffolding
  than usual, correctly — not every new thing deserves the same "figure
  it out" treatment.
- Recurring theme worth carrying into week 3: several real findings
  this week only surfaced because output got actually read, not just
  checked for crashes (the `stars`/`review_count` action inconsistency,
  the `is_open` corruption, the fake-duplicate address). Worth keeping
  that habit deliberately as SQL and DB work starts — a query that runs
  without error is not the same as a query that's correct.
- Open items carried forward, not forgotten: (1) the naturally-skewed-
  data outlier-clipping limitation (`longitude`/`review_count`) — 
  documented, not fixed, candidate for the write-up's limitations
  section; (2) the recommendation-inconsistency pattern (`stars`/
  `review_count` getting reformat/impute/drop across different runs on
  identical data) — the first concrete test case already in hand for
  week 4's validation layer.
- Week 3 tasks added to Notion (Mon Aug 24 – Fri Aug 28): connect to
  Yelp MySQL DB, build the question-to-SQL agent call, execute SQL
  safely with guardrails, turn results into a chart + plain-English
  answer, then run a fixed test-question set and log failures.

## 2026-08-24 — Week 3, Day 1 (Monday) — connect to Yelp MySQL DB
- Created a dedicated read-only MySQL user (`agent_readonly`) with
  `GRANT SELECT` only on `yelp_db` — no write/delete privileges at the
  DB level, per Technical Design.md's guardrails (belt-and-braces
  alongside the application-level SELECT-only check planned for
  Wednesday). Credentials added to `.env` (`DB_HOST`, `DB_USER`,
  `DB_PASSWORD`, `DB_NAME`), never committed.
- Built `db/connection.py` — two functions:
  1. `get_connection()` — opens a `mysql-connector-python` connection
     using the four `.env` values, same pattern as `agent/client.py`'s
     API-key loading. First attempt passed the env-var names in
     unquoted (`os.getenv(DB_HOST)`), which Python read as an undefined
     variable reference rather than a string key — fixed by quoting.
  2. `get_schema()` — queries `INFORMATION_SCHEMA.COLUMNS` for every
     table/column/type in `yelp_db`, builds a `{table: [(column, type),
     ...]}` dict. This is what Wednesday's SQL-generation agent will
     read to ground its queries in real column names.
- Two real bugs in the `get_schema()` loop, both self-corrected with
  guidance: (1) an unnecessary inner `for column_name in table_name:`
  — looping over a string iterates its individual characters, not
  useful here, since the outer loop already unpacks one full row per
  iteration; (2) `schema = {table_name: [...]}` inside the loop
  overwrote the entire dict every iteration instead of adding to it —
  fixed with an `if table_name in schema` branch, appending to the
  existing list or creating a new one. A follow-up slip on the fix
  itself: called `.append()` with two arguments instead of one tuple,
  and reassigned `schema[table_name] = schema[table_name].append(...)`
  — `.append()` mutates a list in place and returns `None`, unlike the
  pandas methods used all of week 2 that return new objects and need
  reassignment. Good contrast to have hit directly.
- Verified against the real local `yelp_db`, not just "ran without
  error": `Connected: True`, and `get_schema()` returned real
  structure for **9 tables** (business, business_category,
  business_hours, category, checkin, review, tip, user_elite_year,
  yelp_user) with correct column names and types — e.g. `business` has
  12 columns including `attributes` (json). Technical Design.md Section
  4 says "8 tables" — minor doc/reality mismatch, not investigated
  further today (likely just an old count from before `user_elite_year`
  or `business_category` were split out); worth a one-line fix to the
  design doc at some point, doesn't block anything.
- Day 1 of week 3 complete, roughly on estimate. Next per Notion/
  Plan.md: Tue Aug 25 — build the question-to-SQL agent call.

## 2026-08-25 — Week 3, Day 2 (Tuesday) — question-to-SQL agent call
- Built `generate_sql(question)` in `agent/sql_agent.py`: calls
  yesterday's `get_schema()`, drops the resulting dict straight into an
  f-string (Python auto-stringifies it — no manual formatting needed),
  asks Claude for a single SQL SELECT answering the question, extracts
  the text block same as `cleaning_agent.py`, returns it as a plain
  string. Deliberately simpler than a full tool-calling loop for today
  — schema goes in the prompt directly rather than Claude calling
  `get_schema` as a tool mid-conversation (Technical Design.md Section 4
  explicitly allows this simplification). SQL execution itself is
  tomorrow's task, not today's.
- Conceptual point clarified: no JSON parsing needed here, unlike
  `cleaning_agent.py`. `json.loads()` was only needed there because
  that prompt specifically asked for JSON; today's prompt asks for a
  plain SQL string, so Claude's text reply is already the final answer
  — no conversion step.
- Tested against two real questions on the actual `yelp_db` schema, not
  just one: (1) "Which city has the most businesses?" — produced a
  correct single-table `GROUP BY`/`COUNT`/`ORDER BY`/`LIMIT` query; (2)
  "top 5 businesses by average review star rating, with at least 10
  reviews" — correctly `JOIN`ed `business` and `review` on
  `business_id`, grouped by both `business_id` and `name`, used
  `HAVING` (not `WHERE`) to filter on the aggregate review count.
  Deliberately picked the second question to force multi-table
  reasoning rather than trusting a single easy query as proof it works.
- Real finding, not just a clean run: despite the prompt explicitly
  saying "no markdown code fences," Claude wrapped both replies in
  ` ```sql ... ``` ` anyway — an instruction not followed, consistent
  across both test runs (systematic habit, not a one-off). Same class
  of unreliability as week 2's `JSONDecodeError`s. Left unfixed today,
  deliberately deferred to tomorrow's "execute SQL safely" task, since
  stripping the fences before execution belongs naturally with that
  guardrail work rather than bolted on today.
- Day 2 of week 3 complete. Next per Notion/Plan.md: Wed Aug 26 —
  execute SQL safely (read-only, guardrails), return results — starts
  with stripping the markdown-fence issue found today.

## 2026-08-26 — Week 3, Day 3 (Wednesday) — execute SQL safely, guardrails
- Fixed yesterday's leftover fence issue first: `generate_sql` now
  strips ` ```sql ` / ` ``` ` via `.replace().replace().strip()` before
  returning. First attempt forgot to reassign the result (`sql_query =
  ...`) — same "string/DataFrame methods return new objects, don't
  mutate in place" rule that's recurred all project, this time on a
  plain string rather than a pandas object. Confirmed fixed by rerunning
  both of yesterday's test questions — clean SQL, no fences, both still
  correct.
- Built `run_sql_query(sql, row_limit=1000, timeout_ms=5000)` in
  `db/connection.py`, implementing all three guardrails from Technical
  Design.md Section 5: (1) reject anything not starting with `SELECT`
  (case-insensitive check via `.upper().startswith(...)`); (2) reject
  if a semicolon remains after stripping a single trailing one (blocks
  multi-statement injection); (3) auto-append `LIMIT {row_limit}` if
  the query doesn't already specify one; (4) a MySQL session-level
  `SET SESSION MAX_EXECUTION_TIME` timeout set immediately before
  running the real query. Returns both column names (from
  `cursor.description`) and row data, not just rows — needed for
  Thursday's chart/answer step to know what the columns mean.
  Self-corrected bugs along the way: `=!` instead of `!=` (backwards
  operator), a 5-character slice (`[0:5]`) that could never match the
  6-character word `"SELECT"` even if fixed, and `NOT` (SQL-style
  capitalization) instead of Python's lowercase `not` keyword — the
  last one a direct consequence of writing SQL-as-text and Python
  side by side today for the first time.
- Didn't just trust the happy path — deliberately tested each guardrail
  in isolation before trusting the combined pipeline: `SELECT * FROM
  business` (no `LIMIT` in the query) correctly capped at exactly 1000
  rows; `DELETE FROM business` correctly raised `ValueError` before
  ever reaching the database, nothing deleted.
- Genuine, unplanned finding: wiring `generate_sql` + `run_sql_query`
  together end-to-end, the JOIN query from yesterday (`business` JOIN
  `review`, no `WHERE`, `GROUP BY`/`HAVING`/`ORDER BY` on an aggregate)
  hit the timeout guardrail for real — `MySQLInterfaceError: Query
  execution was interrupted, maximum statement execution time
  exceeded` — at both 5000ms and, retested, still at 15000ms. This
  wasn't a bug in the guardrail code; it's the timeout doing its job on
  a legitimately expensive, unindexed aggregation across the full
  `review` table (6.9M rows). Read as an honest limitation worth
  keeping for the write-up: correct SQL can still get blocked by a
  safety guardrail purely for being slow, which is a real trade-off,
  not something to silently paper over. Not optimized today (would
  need indexing or a narrower question) — deliberately left as
  documented, not fixed, same treatment as week 2's skewed-outlier-
  clipping limitation.
- Full pipeline proven end-to-end for the first time with a query that
  actually completes: "Which city has the most businesses?" → clean
  generated SQL → guardrails pass → real execution → `[('Philadelphia',
  14577)]`, matching the direct `run_sql_query` test from earlier today
  exactly.
- Day 3 of week 3 complete, all three Technical Design.md guardrails
  now genuinely proven (not just written), plus one real limitation
  found and documented rather than silently hit. Next per Notion/
  Plan.md: Thu Aug 27 — results → chart + plain-English answer.

## 2026-08-27 — Week 3, Day 4 (Thursday) — results → chart + plain-English answer
- Built `generate_answer(question, columns, rows)` in `agent/sql_agent.py`
  — a second, separate Claude call (not the same call that generated
  the SQL), same shape as `generate_sql`: builds a prompt embedding the
  question plus the real query results, asks for a short natural-
  language sentence, explicitly instructed not to leak SQL/column/row
  language into the answer. Worked correctly first attempt: "Philadelphia
  has the most businesses, with 14,577 in total."
- Built `build_chart(columns, rows)` using `plotly.express` (`px`) —
  first exposure to Plotly. Deliberately kept deterministic (plain
  Python, no LLM call) rather than asking Claude to choose a chart
  type — same philosophy as `profile_dataset()` never needing an LLM,
  and one less place for an unreliable instruction-following failure
  (like this week's markdown-fence issue) to creep in. Splits `rows`
  (a list of tuples) into separate `labels`/`values` lists via a plain
  loop with `.append()` (functionally identical to a list
  comprehension, just more explicit — fine), then `px.bar(x=labels,
  y=values, ...)` builds the figure in one line.
- First test used the existing `LIMIT 1` question ("which city has the
  most businesses") — technically worked, but only produced a single
  bar, not a real test of the chart with multiple values. Caught before
  trusting it: switched to "top 5 cities by number of businesses"
  instead, confirmed 5 real bars (Philadelphia, Tucson, Tampa,
  Indianapolis, Nashville), correctly ordered descending.
- Also fixed on the same pass: default `px.bar()` axes were labeled
  generically "x"/"y" rather than the real column names, since raw
  lists carry no column identity. Added a `labels={"x": columns[0],
  "y": columns[1]}` argument mapping the internal axis names to the
  actual query's column names ("city", "business_count") — matters for
  the eventual Streamlit demo looking finished, not just functionally
  correct.
- `.show()` used to preview the chart in a browser tab for now (opens
  in Safari) — real Streamlit rendering (`st.plotly_chart`) is later
  integration work, not today's scope.
- Milestone moment: this is the first day the full, real pipeline ran
  end-to-end exactly as originally scoped in Plan.md's Goal section —
  natural-language question in, generated SQL, guardrailed execution,
  plain-English answer, and a chart out — with zero manual SQL writing
  on the user's side. Genuinely felt like the project's core idea
  working, not just individual pieces passing tests in isolation.
- Day 4 of week 3 complete, on estimate. Next per Notion/Plan.md: Fri
  Aug 28 — run a fixed test-question set against the pipeline, log
  failures (light review day, closes out week 3).

## 2026-08-28 — Week 3, Day 5 (Friday) — fixed test-question set, week 3 wrap
- Built `tests/test_questions.py`: 5 real questions run through the full
  pipeline (`generate_sql` → `run_sql_query` → `generate_answer`),
  chosen to map onto ground-truth patterns already in `Code.md` (the
  manual SQL from the original Yelp project) — single-table aggregate,
  state-level `GROUP BY`, JOIN + `HAVING` threshold, date-based
  `GROUP BY`, and simple `ORDER BY`/`LIMIT`. Deliberately scoped down
  from full automated SQL-equivalence grading (checking whether
  generated SQL is *exactly* equivalent to hand-written SQL is a hard
  problem on its own) to manual review against `Code.md`'s patterns —
  appropriate for a 1h light day.
- One bug, self-corrected: 3 of the 5 question strings in the list were
  missing trailing commas. Python doesn't error on this — adjacent
  string literals with no comma between them get silently concatenated
  into one string. All 4 later questions merged into a single ~200-word
  run-on question, which Claude then tried to answer with a 4-part
  `UNION ALL` query wrapped in parentheses — correctly rejected by
  yesterday's guardrail, since the query started with `(` rather than
  `SELECT`. Good incidental confirmation the guardrail works on
  malformed input too, not just the deliberate `DELETE` test from
  Wednesday. Root cause was the missing commas, not the guardrail.
- All 5 questions passed on the rerun, checked against `Code.md`
  patterns and cross-referenced against real prior findings — no
  failures to log, stated plainly rather than manufactured:
  1. City with most businesses: Philadelphia, 14,577 (consistent all
     week).
  2. State with most businesses: PA, 34,039 — sanity-checks correctly
     against #1 (state total > single city total).
  3. Highest-rated category (≥100 businesses): Reiki, 4.68 — matches
     `Code.md`'s JOIN+HAVING pattern exactly; Claude's version used
     `COUNT(DISTINCT business_id)` rather than plain `COUNT(*)`,
     arguably more correct than the original manual query.
  4. Reviews per year: matches `Code.md`'s year-grouping pattern;
     plain-English answer correctly flagged 2022's low count as likely
     incomplete data rather than a real decline — an appropriate,
     unprompted caveat.
  5. Top 10 businesses by review count: Acme Oyster House, 7,568 — this
     exact number independently matches `review_count`'s documented
     original max from week 2's `top_reviewed_businesses.csv` outlier
     analysis, a real cross-check of internal consistency across
     unrelated parts of the project.
- Week 3 in one line: went from "no DB connection at all" (Monday) to a
  fully working NL-to-SQL pipeline — schema-grounded SQL generation,
  guardrailed execution, plain-English answers, and charts — verified
  against real ground-truth SQL patterns from the original Yelp
  project, with zero failures on the first full test pass.
- Two genuine, unplanned guardrail confirmations this week, neither
  manufactured as a test: Wednesday's timeout firing on a legitimately
  expensive JOIN query, and today's SELECT-only check catching a
  malformed `UNION ALL` query caused by an unrelated Python bug. Real
  evidence the guardrails work under real conditions, not just the
  cases they were written for.
- Week 4 tasks (Mon Aug 31 – Fri Sep 4) added to Notion: sanity checks
  (row counts, table-relevance), seeding deliberate errors to confirm
  the validation harness catches them, confidence scoring/flagging in
  the UI, applying the same validation logic to risky cleaning changes,
  and a check-in against the plan's original success criteria. This is
  the week that turns this week's `stars`/`review_count` recommendation-
  inconsistency (week 2) and Wednesday's timeout-vs-correctness
  trade-off (week 3) from documented findings into an actual working
  validation layer.
- Pacing note: Hamsa is off work this week (holiday), wants to move
  faster than one task/day where the day allows — up to 2 tasks in a
  session some days, one on others, driven by how the day's going
  rather than the calendar. Same execution either way (hands-on build,
  verify real output, log notes, git command, Notion update per task)
  — just decoupled from the strict one-task-per-weekday cadence used
  weeks 1-3.

## 2026-08-31 — Week 4, Day 1 (Monday) — sanity checks: row counts, table relevance
- Built two deterministic (non-LLM) checks in `agent/validation.py`,
  per Technical Design.md Section 4's split between mechanical checks
  and the separate LLM-based "fresh eyes" review (not built yet — later
  this week):
  1. `check_row_count(rows, row_limit=1000)` — flags zero rows back
     (wrong filter, or a genuinely correct empty result — worth
     surfacing either way) and rows count exactly at the row-limit cap
     (results possibly truncated by Wednesday's guardrail, meaning an
     answer could be based on an incomplete picture). The row-limit
     case is a small extension beyond the plan's literal wording
     ("suspiciously huge") — same spirit, adapted to the fact the
     guardrail already caps results at exactly 1000 rather than letting
     genuinely huge results through.
  2. `check_table_relevance(question, sql)` — a blunt keyword-matching
     heuristic: finds which real schema tables the SQL touches, then
     checks whether any word from each table's name (split on `_`, so
     `yelp_user` → `yelp`/`user`) appears in the question. Flags tables
     used that don't obviously relate to anything asked. Explicitly not
     real semantic understanding — good for catching obvious
     table-choice errors, not subtle ones. Tomorrow's "seed deliberate
     errors" task is the real stress test of how well this catches
     genuine problems.
- Both functions tested across all branches, not just the happy path —
  same discipline as every guardrail test this project has done:
  `check_row_count` confirmed on an empty list, a 1000-item list
  (built via a loop, `list(range(1000))` noted as the shorter
  equivalent), and a normal small list. `check_table_relevance`
  confirmed both on a real matching pair (question about businesses,
  SQL touching `business` → `"ok"`) and a deliberately broken pair
  (question about check-ins, SQL touching only `tip` →
  correctly flagged `['tip']` as unrelated) — the mismatch case wasn't
  tested until asked for explicitly, worth remembering as a recurring
  habit: a check that's never seen its own failure case fire isn't
  actually proven yet.
- Day 1 of week 4 complete. Next: Tue — seed deliberate errors, confirm
  the harness (today's two checks, at minimum) actually catches them.

## 2026-08-31 — Week 4, Day 2 (Monday session, same day) — seed deliberate errors
- Ran Monday's two checks against 3 deliberately broken question/SQL
  pairs, each targeting one of Plan.md's own named failure types
  (wrong join, silently-wrong column, doesn't actually answer the
  question) — real, mixed results, not a clean sweep:
  1. **Wrong join** (joined `tip` into a city/star-rating question):
     `check_table_relevance` correctly flagged `tip` — the actual
     intended catch. `check_row_count` fired too, but coincidentally —
     it flagged truncation at 1000 rows, an unplanned finding that the
     real `business` table likely has 1000+ distinct `city` string
     values (probably inconsistent capitalization/whitespace in the
     live production table, not just the messy CSVs from week 2), not
     evidence the join itself was caught.
  2. **Impossible filter → zero rows** (`stars > 10`, impossible since
     stars only go to 5): clean pass, exactly as designed —
     `check_row_count` caught it, `check_table_relevance` correctly
     stayed quiet.
  3. **Wrong metric, doesn't answer the question** (ordered by
     `review_count` instead of `stars`): `check_row_count` correctly
     stayed silent (real, non-empty result — this class of error is a
     genuine, expected gap for a row-count check). But
     `check_table_relevance` incorrectly flagged `review` as a table
     used — a real bug, not a heuristic limitation: the check matched
     the substring `"review"` inside the column name `review_count`,
     even though the `review` table itself was never touched.
- Fixed the substring bug directly (Hamsa's explicit request, invoking
  the established fallback — this was new syntax, not a derivable
  extension of known patterns): switched `check_table_relevance`'s
  table-detection from a plain `in` substring check to a regex
  word-boundary match (`\btable_name\b`, via Python's `re` module,
  first use in this project). `_` counts as a word character in
  regex, so `\breview\b` correctly fails to match inside
  `review_count` (no boundary between `w` and `_`) while still matching
  a real standalone `review` reference. Reran the same 3 seeded tests
  after the fix: test 3's false `review` flag is gone, now correctly
  reports `"ok"`; tests 1 and 2 unchanged as expected.
- Real, honest limitation left undone, deliberately not "fixed" today:
  test 1's `business` false positive (the right table, flagged only
  because the question's wording — "star rating per city" — never
  literally says "business"). This isn't a bug in the same sense as the
  substring issue; it's the ceiling of what keyword-matching alone can
  ever do, and is exactly why Technical Design.md calls for a separate,
  smarter LLM-based "fresh eyes" cross-check rather than trying to
  brute-force natural-language understanding with more string logic.
  Documented as the concrete motivation carried into the rest of this
  week, not a gap to silently work around.
- Net result for the day: 1 real catch confirmed clean (impossible
  filter), 1 real catch confirmed but with a coincidental/misleading
  companion signal (wrong join), 1 real implementation bug found and
  fixed (substring-inside-column-name false match), and 1 genuine,
  well-understood limitation documented rather than glossed over. Two
  tasks done in one sitting today, per this week's flexible holiday
  pacing. Next: Wed — confidence scoring / flagging in the UI.

## 2026-09-01 — Week 4, Day 3 (Tuesday) — confidence scoring
- Built `check_answers_question(question, sql)` in `agent/validation.py`
  — the "fresh eyes" LLM check named in Technical Design.md Section 4:
  a separate Claude call (not the one that generated the SQL)
  reviewing whether the query actually answers the question, replying
  yes/no plus a short reason. This is the piece that closes Monday's
  documented gap: tested directly against the "wrong metric" seeded
  error (ordered by `review_count` instead of `stars`), and it
  correctly caught it — "No, the query orders by review_count instead
  of the star rating column" — something neither deterministic check
  could ever see, since it requires actually understanding what the
  question wants, not just which tables/columns are touched.
- Built `validate(question, sql, columns, rows)`, combining all three
  signals (row-count check, table-relevance check, LLM fresh-eyes
  check) into one overall risk level — `"low"`/`"medium"`/`"high"`,
  matching `cleaning_agent.py`'s existing risk vocabulary for
  consistency across the project. LLM "no" leads to `"high"` (most
  serious, the actual answer would be wrong); "yes" but a deterministic
  warning leads to `"medium"`; clean on all three leads to `"low"`.
  Actual Streamlit UI rendering of this is week 5 integration work, not
  today's scope — today built and proved the logic via prints, same
  pattern as every other day.
- One self-corrected bug: `llm_answer = llm_result.strip().split(" ")[0]`
  used `.split(" ")` (splits only on literal space characters), but
  `check_answers_question`'s reply has a newline between "no"/"yes" and
  the reason, not a space — so this would have grabbed `"no\nThe"` as
  one chunk instead of just `"no"`, silently breaking the `"high"` risk
  branch forever. Fixed to `.split()` with no argument, which splits on
  any whitespace including newlines. Also added `.lower()` defensively
  — turned out not to be theoretical: a later real run had Claude reply
  `"No"` (capital N) instead of `"no"`, confirming the normalization
  was genuinely necessary, not just caution for its own sake.
- Also caught and fixed independently: a leftover `validate(question,
  sql, columns, rows)` test call referencing bare `question`/`sql`
  variables that were never assigned outside the seeded-tests loop
  (only `test["question"]`/`test["sql"]` existed) — would have thrown
  `NameError`. Replaced with a proper, explicit test case.
- Tested both ends of the risk scale for real, not just the interesting
  one: the wrong-metric case correctly returned `"high"` (LLM said no,
  reasoning correct both times it was asked, once with lowercase "no"
  and once with capital "No"); a genuinely correct question ("which
  city has the most businesses") correctly returned `"low"`, LLM
  confirming "Yes, the query... directly answers the question."
  `"medium"` not separately exercised through `validate()` itself —
  it's a simple OR of two already-individually-proven signals from
  Monday, reasonable to trust without a dedicated fourth test.
- Day 3 of week 4 complete. Next: Thu — apply this same validation
  logic to risky cleaning changes (week 2's `stars`/`review_count`
  drop-recommendation inconsistency becomes the real test case here).

## 2026-09-01 — Week 4, Day 4 (Tuesday session, same day) — validation on risky cleaning changes
- Built `check_drop_severity(column, profile_col, action)` in
  `agent/validation.py` — a deterministic check flagging `"drop"`
  actions on columns with low missing percentage (< 20%), on the
  reasoning that dropping a mostly-complete column is a poor default
  unless justified by something other than missingness (outliers are a
  reformat problem, not a drop problem). Tested directly against the
  real week 2 case: `stars` at 0% missing, action `"drop"` — correctly
  flagged as suspicious on the first try.
- Built `check_cleaning_decision(column, profile_col, recommendation)`
  — the cleaning-side "fresh eyes" LLM review, same shape as
  yesterday's `check_answers_question`. Self-corrected bugs while
  writing it (asked for help rather than guessing): missing `def`
  keyword (function definition wasn't recognized as one), and leftover
  `{question}`/`{sql}` variable names copy-pasted from yesterday's SQL
  version instead of this function's real parameters (`{column}`/
  `{profile_col}`) — would have thrown `NameError` immediately. Tested
  against the real `stars`/`"drop"` case: correctly said "no," with
  genuinely good reasoning — "outliers should be handled at the row
  level (capping, transformation, removal), not by discarding the
  whole column."
- Built `validate_cleaning(column, profile_col, recommendation)`,
  combining both signals into one risk level — same structure as
  yesterday's `validate()`, written by Hamsa with minimal scaffolding
  this time (a near-direct application of yesterday's proven pattern).
  Tested against the real `stars`/`"drop"` case: correctly returned
  `"high"`, both signals agreeing.
- Significant, unplanned finding testing the "clean" comparison case
  (`stars` with a sensible `"reformat"` action instead of `"drop"`):
  expected `"low"` risk, got `"high"` instead — not a bug, a genuine
  new critique from the LLM review. It flagged that `stars` is a
  bounded rating scale (1-5), so IQR-based outlier *clipping* itself
  may be inappropriate, not just the drop action. This connects
  directly to a real number already on record: week 2 documented
  `stars`'s original min as 2.5, flagged as an "outlier" by the 1.5×IQR
  rule and clipped up to 3.25 — but 2.5 is a completely legitimate
  rating, not a data error; clipping it doesn't fix bad data, it
  artificially inflates a real business's real low rating. Week 2 had
  already flagged this exact failure mode for `longitude`/
  `review_count` ("aggressive clipping on naturally skewed data") but
  never applied it to `stars`, which got reformatted all week without
  question since it looked like the "safe" choice next to the more
  visible drop-recommendation bug. The validation layer just surfaced a
  problem in the option that looked safe, not only the one that looked
  risky — a stronger result for the case study than a clean pass would
  have been. Not fixed today, deliberately — same treatment as the
  original skewed-clipping limitation: documented for the write-up's
  "where the agent got it wrong" section, not chased down mid-task.
- Day 4 of week 4 complete, two tasks done today (Tue Day 3 + Day 4).
  Net result: week 2's real, previously-documented `stars`/
  `review_count` drop bug is now caught automatically by two
  independent signals, and a second, previously-unnoticed methodological
  issue (inappropriate IQR clipping on a bounded rating scale) was
  found as a direct side effect of building the validation layer, not
  something specifically hunted for. Next: Fri — check progress against
  the plan's original success criteria, closing out week 4.

## 2026-09-02 — Week 4, Day 5 (Wednesday) — success-criteria audit, week 4 wrap
- Went through Plan.md's five success criteria one by one against real
  work done, rather than assuming they're all satisfied:
  1. Data-quality report + cleaned dataset, every change logged — met
     (weeks 1-2, tested on real messy data, two genuine bugs found and
     fixed along the way).
  2. Fixed test-question set answered correctly, checked against manual
     SQL — met (week 3 Friday, 5/5 questions passed against `Code.md`
     patterns, cross-verified independently).
  3. Validation layer catches wrong join / silently dropped column /
     doesn't-answer-the-question — the one criterion worth actually
     re-testing rather than assuming: this week's seeded tests covered
     "wrong join" and "wrong metric" on the SQL side, and a "drop"
     decision on the cleaning side, but not the specific case of SQL
     silently dropping a *requested column* from a `SELECT` (a question
     asking for two things, SQL returning only one) — a real, distinct
     failure mode from the cleaning-side column drop already tested
     Tuesday. Constructed a real test for it: "Give me the name and
     star rating of the most-reviewed business" against SQL that only
     selects `name`. Predicted before running (not just checked after):
     `check_row_count` and `check_table_relevance` almost certainly
     wouldn't catch it (real row back, right table used — "business" is
     literally in the question), and `check_answers_question` was the
     real chance, since its prompt explicitly asks it to consider "the
     right columns." Confirmed exactly as predicted: row/table checks
     stayed silent, LLM check correctly caught it — "The query selects
     only 'name' but not the star rating, missing the 'stars' column
     requested in the question." All three of the plan's named failure
     types are now genuinely confirmed caught, not assumed to be.
  4. Public deployment — not done, correctly scheduled for week 6, not
     a gap.
  5. Write-up with explicit limitations — in progress and on track;
     `case_study_notes.md` already holds substantial honest material
     (skewed-outlier clipping, recommendation inconsistency, the
     bounded-rating-scale clipping finding from Tuesday, the wrong-join
     false-positive limitation). Actual Notion write-up is week 6.
- Week 4 in one line: went from zero validation logic (end of week 3)
  to a working two-layer system — deterministic sanity checks plus an
  independent LLM "fresh eyes" review — that catches real, previously
  undetected problems on both the SQL side and the cleaning side,
  including one (the `stars` clipping issue) nobody had thought to
  question until the validation layer surfaced it unprompted.
- Pace note: week 4's five tasks were completed across 3 sessions
  (Mon: 2 tasks, Tue: 2 tasks, Wed: 1 task) rather than one per weekday,
  per this week's flexible holiday pacing — same rigor and verification
  discipline throughout regardless of how many tasks landed in a
  session.
- Week 5 tasks (Mon Sep 7 – Fri Sep 11, Integration + polish) added to
  Notion: full end-to-end test on a fresh CSV, fixing what breaks,
  more fixing/edge cases, UI polish, and a buffer day. This is the
  week everything built so far (cleaning pipeline, NL-to-SQL pipeline,
  validation layer) actually gets wired into `app.py`'s Streamlit UI
  for the first time — until now, every piece has been tested via
  prints and `.show()`, not the real interface end users would see.
- Pacing change: Hamsa wants to compress week 5 into this week given
  the pace held all through week 4 — Notion due dates moved from the
  original Mon-Fri spread to today/tomorrow/Friday (2/2/1 tasks). Same
  execution discipline regardless of compression.

## 2026-09-02 — Week 5, Day 1 (Wednesday) — full end-to-end test, fresh CSV
- First real wiring of `app.py` to the actual pipeline — until today it
  was still the Day 2 (week 1) skeleton, just title/caption/uploader
  with a status message. Chained the five already-built functions
  behind the file uploader for the first time: `profile_dataset` →
  `get_cleaning_recommendations` → `apply_cleaning` → `write_audit_log`
  → `generate_report`, displayed via two new Streamlit calls
  (`st.text` for the report, `st.dataframe` for the cleaned data —
  free sorting/downloading included, no extra code).
- Test data deliberately chosen to be genuinely fresh: `yelp_user`
  (200 rows via `SELECT * FROM yelp_user LIMIT 200`), a table never
  exercised through the cleaning pipeline before — different column
  types entirely (datetime, several integer counters, a decimal
  average). Checked for real missingness first (`WHERE name = '' OR
  name IS NULL` → 0) rather than assuming; proceeded anyway since
  today's actual goal was schema generalization and UI wiring, not
  re-proving missing-value handling (already covered week 2).
- Two real bugs on the way to a working run, neither Hamsa's fault in
  the interesting sense — both genuine gaps in translating known
  patterns to a new context:
  1. First `app.py` attempt chained `dataset_test` into every function
     call instead of each function's actual expected input (e.g.
     passing the raw dataframe to `get_cleaning_recommendations`,
     which needs the profile dict) — pointed back to `data/report.py`'s
     own `__main__` block as the reference for the correct chain,
     which Hamsa then reproduced correctly.
  2. `TabError: inconsistent use of tabs and spaces` — the original
     Day 2 `else` block used a tab character, the newly pasted lines
     used spaces; Python 3 refuses to guess how to reconcile mixed
     indentation within one block. Fixed directly (pure whitespace
     mismatch, not a logic bug). Side finding: Safari showed a blank
     white page rather than Streamlit's usual in-browser error display
     for this same error, while Chrome rendered the real traceback
     correctly — Chrome confirmed as the more reliable browser for this
     project going forward.
- First full run through the real UI succeeded, and reading the actual
  report (not just confirming it ran) surfaced three genuine findings:
  1. **Serious — `user_id` corrupted by the generic text-reformat
     step.** `.str.lower()` in `cleaning.py`'s text-reformat branch
     applies uniformly to every text column; sensible for `city`/
     `state`, actively harmful for `user_id`, an opaque unique
     identifier — `___6aix-XvFcQz3GauAPpw` became
     `___6aix-xvfcqz3gauappw`. If this ID is ever matched back against
     the real `yelp_db.yelp_user.user_id` (a join, a lookup), the
     lowercased version silently no longer matches. More serious than
     prior findings: this actively breaks referential integrity, not
     just cosmetic accuracy.
  2. **`review_count` clipped extremely aggressively** — max dropped
     from 1247 to 45.125 (27 outliers, >27x reduction). Same documented
     skewed-clipping limitation as week 2's `longitude`/`review_count`
     and Tuesday's `stars` finding, but the starkest real example yet.
  3. **`yelping_since` recommended for datetime conversion, never
     actually converted.** Before/after sample identical
     (`'2011-09-26 18:10:05'` both times) — the text-reformat branch
     only ever does `.str.strip().str.lower()` regardless of what the
     recommendation's stated reason says is needed. Confirms and
     sharpens week 2's "reformat is a vague bucket" finding with a
     concrete case where the code silently doesn't do what the
     reasoning claims.
  4. Also observed, not a bug: several `compliment_*` columns'
     recommendation reasons said "consider capping extreme values"
     even though the `IQR == 0` guard correctly skipped clipping for
     all of them (all binary/near-constant) — a reminder that Claude's
     stated reasoning and the deterministic code executing it aren't
     always in sync, which is exactly why the guard exists as a safety
     net rather than trusting the reasoning text to self-police.
  5. Genuinely good: the one real missing value in `name` (1/200,
     0.5%) correctly fell through to the `"Unknown"` placeholder path
     from week 2's 30%-threshold fix, rather than fabricating a
     duplicate — first real (not seeded) exercise of that fix on live
     data.
- None of the three findings fixed today, deliberately — per the
  plan's own week 5 split, today's job was finding what breaks;
  tomorrow's is fixing it. All three carried forward as concrete,
  numbered items for tomorrow's task, not vague reminders.
- Day 1 of week 5 complete. Next: fix the `user_id` corruption, the
  review_count over-clipping, and the yelping_since non-conversion —
  today's three real findings.

## 2026-09-02/03 — Week 5, Day 2 — fix what breaks
- Pacing change: Hamsa is compressing week 5 into this week given the
  pace held all through weeks 3-4 — Notion due dates for the remaining
  4 week-5 tasks moved to today/tomorrow/Friday (2/2/1) rather than
  spread Mon-Fri.
- **`review_count` over-clipping** — discussed as a real design
  decision before touching code, not assumed: this is the third
  recurrence of the same skewed-distribution-clipping problem (week 2's
  `longitude`/`review_count`, Tuesday's `stars`, now `yelp_user`'s
  `review_count` at 27x reduction), so worth actually mitigating this
  week rather than documenting a fourth time. Clarified an important
  distinction Hamsa's mental model had blurred: this is NOT the same
  failure mode as `is_open` (a binary/near-constant column where
  IQR = 0, already fixed by a guard) — `review_count`'s IQR is
  genuinely non-zero, the real problem is a long-tailed/skewed
  distribution where the "normal range" computed from typical users is
  too narrow to fairly represent legitimate high-end values. Fix:
  widened the outlier multiplier from 1.5×IQR to 3×IQR in **both**
  `data/profiling.py` (outlier counting) and `data/cleaning.py`
  (actual clip bounds) — both had to change together, or the reported
  outlier count and the real clipping behavior would fall out of sync.
  Verified against real data: outliers flagged dropped 27→14, clip cap
  rose 45.125→71. Explicitly documented as a mitigation, not a full
  fix — even at 3×IQR, genuinely high real values (100, 1247) still
  get clipped; a truly long-tailed distribution needs a fundamentally
  different method (percentile capping, log-transform) to fully solve,
  which is deliberately out of scope for this week.
- **`user_id` corruption** — root cause: `cleaning.py`'s text-reformat
  branch applied `.str.strip().str.lower()` uniformly to every text
  column, appropriate for genuine free text (`city`) but actively
  harmful for an opaque unique identifier, where the exact
  characters/casing *are* the value itself, not incidental formatting.
  Fix: added a check for near-100% column uniqueness
  (`nunique() == len(column)`) — if every row has a different value,
  treat it as an identifier and skip the transformation entirely,
  logging why, same pattern as the existing `IQR == 0` guard.
- **`yelping_since` non-conversion** — root cause: the same
  text-reformat branch never attempted real type conversion, only
  string cleaning, regardless of what the recommendation's reasoning
  claimed was needed. Fix: try `pd.to_datetime(col, errors="coerce")`
  first; if ≥90% of values parse successfully as real dates, convert
  the column for real rather than just tidying the text.
  Deliberately ordered this check *before* the uniqueness check above
  — `yelping_since` is also 100% unique (every signup timestamp
  differs to the second), so checking uniqueness first would have
  wrongly caught it as "an identifier, skip" before ever getting a
  real chance at datetime conversion. Order of checks mattered for
  correctness, not just style.
- Genuine debugging saga getting these verified, worth documenting for
  the write-up as a real Python/Streamlit gotcha, not just "it worked
  eventually": two reruns after the code fix showed *zero* change in
  behavior, exactly matching the old broken output. Diagnosed in
  stages: (1) ruled out browser-level staleness — cleared cache,
  refreshed, reuploaded, no change; (2) suspected the running Python
  process still held the old version of `cleaning.py` in memory (a
  module already imported doesn't reload just because the file on disk
  changed) — did a full `Ctrl+C` + restart of the Streamlit process,
  confirmed via a fresh startup timestamp — still no change; (3) real
  root cause: stale compiled bytecode in `__pycache__` folders. Deleted
  every `__pycache__` directory in the project
  (`find . -name "__pycache__" -type d -exec rm -rf {} +`) before the
  next restart — fixed it immediately, both `user_id` and
  `yelping_since` came out correct on the very next run. Confirmed the
  fix was never actually broken; three separate layers of caching
  (browser, in-memory module, compiled bytecode) all needed to be
  independently ruled out before the real cause was found.
- Day 2 of week 5 complete — all three findings from Day 1 fixed and
  verified with real output, not assumed. Next: more fixing/edge
  cases, or UI polish, depending on pace.

## 2026-09-03 — Week 5, Day 3 — more fixing / edge cases
- Deliberately tested an edge case no prior file had exercised: a
  column with zero real values at all (100% missing), via a small
  hand-built `edge_case_empty_column.csv` (8 rows, `notes` column
  entirely blank) — a plausible real scenario, not just theoretical.
- First test (through the real recommendation pipeline, LLM in the
  loop): no crash, because Claude itself recommended `"drop"` for the
  fully-empty column — a sound call, but one that meant the actually
  fragile code path (`"impute"` on a 100%-missing column) was never
  exercised. Correctly treated as inconclusive, not "proven safe" —
  same "did it run" vs "is it correct" lesson one layer deeper: relying
  on the LLM to happen to avoid a dangerous path isn't the same as the
  code being safe, especially given documented evidence elsewhere in
  this project that identical data can get different LLM
  recommendations across runs.
- Second test: bypassed the LLM entirely, directly calling
  `apply_cleaning` with a hand-built recommendations dict forcing
  `"impute"` on `notes` — genuinely testing the code path itself, same
  approach as validation.py's fake-recommendation tests.
- Result was a real bug, but not the one predicted — worth being
  honest about the wrong guess and why: expected an `IndexError` from
  `.mode()[0]` on a fully-empty *text* column, but pandas actually
  infers an entirely-blank CSV column as `float64` (since `NaN` itself
  is a float), not text — so it hit the *numeric* branch instead.
  `.median()` on zero real values doesn't crash, it returns `NaN`, so
  `fillna(NaN)` is a silent no-op. The real bug: the report then
  claimed `"filled with median nan"` — text that reads like a
  successful fix, when in fact nothing changed and the column is still
  100% empty. Arguably worse than a crash: a crash is loud and gets
  noticed immediately; a silently-false "success" message undermines
  the actual point of the audit trail — "auditable, not a black box"
  only holds if what gets logged is genuinely true.
- Fixed in `data/cleaning.py`'s `"impute"` branch: added a
  `not_null_count == 0` check as the first condition, before the
  existing numeric/text split — skips honestly with an explicit
  message rather than attempting (and silently failing at) a fill.
  Also removed a duplicate `not_null_count` calculation that had
  previously only existed inside the text branch, now computed once
  and reused. Verified fixed: rerunning the forced-impute test now
  correctly reports "skipped — column is entirely empty, no real
  values exist to compute a fill value from."
- Recurring `JSONDecodeError` (empty Claude reply) hit again mid-task,
  this time exhausting all 3 of week 2's retry attempts rather than
  failing once and recovering — a slightly worse instance of an
  already-known, already-partially-mitigated limitation. Not
  investigated further today (same call succeeded on a plain rerun) —
  worth flagging as still not fully eliminated for the write-up's
  limitations section, consistent with Monday week 2's original note.
- All three of week 5's compressed Wed-due tasks (full end-to-end test,
  fix what breaks, more fixing/edge cases) now complete in one
  extended session. Remaining: UI polish and buffer, both due Friday.

## 2026-09-04 — Week 5, Day 4/5 — UI polish + buffer, week 5 wrap
- Scope decision made explicitly rather than assumed: Plan.md's literal
  "UI polish" task only covers the existing cleaning UI, but the
  NL-to-SQL half of the project (built since week 3) had never been
  wired into `app.py` at all — only tested via terminal prints and
  `.show()` browser tabs. Raised as a real choice (narrow polish only,
  vs. polish + full SQL-agent integration using today's buffer slack)
  rather than deciding unilaterally; Hamsa chose the larger scope,
  wanting the demo to actually show both capabilities named in Plan.md's
  Goal section before calling the app "finished."
- **Cleaning-UI readability fix** (Hamsa's own observation, raised
  proactively): the report was a single wall of text via `st.text`,
  hard to read. Fixed by leveraging structured data already available —
  `changes` (a list of per-column dicts) converted directly to
  `pd.DataFrame(changes)` and shown via `st.dataframe`, a real
  sortable table instead of a text blob. The original full text report
  wasn't discarded, just tucked into a collapsible `st.expander` for
  anyone who wants the narrative version. Also updated the stale Day 2
  title/caption/docstring, which still described "proving the plumbing
  works" long after that was true.
- **SQL-agent wired into the app for the first time.** New "2. Ask a
  question" section: `st.text_input` for the question, `st.button` to
  gate execution (important new concept — Streamlit reruns the entire
  script on every interaction, so without gating behind a button click,
  every keystroke would fire off live Claude/DB calls), running the
  full pipeline (`generate_sql` → `run_sql_query` → `generate_answer` →
  `build_chart`) and displaying results with `st.plotly_chart` (the
  real in-page renderer, vs. `.show()`'s separate browser tab used for
  all testing until now) and `st.code(sql, language="sql")` for the
  generated query.
- **Closed a task explicitly deferred since Tuesday**: Technical
  Design.md's "confidence scoring / flagging in the UI" was built
  (Tuesday) but its actual Streamlit rendering was deliberately left
  for week 5 integration. Wired `validate()`'s risk level into the new
  section — `st.error` (red) for high risk, `st.warning` (yellow) for
  medium — genuinely closing a loop left open for two days rather than
  a new feature invented today.
- Real bugs along the way, self-written then reviewed together:
  1. A broken import split across two lines (`from agent.sql_agent
     import generate_sql` then a bare `generate_answer, build_chart`
     on the next line with no `import` keyword) — would have thrown
     `NameError` immediately. Self-corrected before running.
  2. More structural: the entire new "Ask a question" section was
     nested inside the CSV-upload `else` block (matching indentation),
     meaning it would only appear *after* uploading a file — defeating
     the point of two independent, parallel capabilities. Also mixed
     tabs/spaces again (same class of bug as Wednesday's `TabError`).
     Fixed by rewriting the file cleanly (a targeted edit failed on a
     whitespace mismatch) with section 2 as a sibling after the
     `if/else` block, not nested inside it.
- Real-world verification, not just "it ran": tested the full loop live
  in the browser twice. First: "which city has the most businesses?" —
  correct answer, correct inline chart, no false warning (correctly
  silent on a genuinely good answer). Second: "which business has the
  highest star rating?" — triggered a real, substantively different
  critique from the LLM fresh-eyes check than any seen before: not the
  old "wrong metric" bug, but a legitimate concern about unhandled ties
  (multiple businesses could share the top rating; `LIMIT 1`
  arbitrarily picks one and silently hides the rest) — genuine evidence
  the validation layer reasons per-query, not from a canned response.
  Also caught a cosmetic bug from this same test: the error message
  read "Low confidence in this answer: no The query ignores ties..." —
  `llm_check`'s raw `"no\n<reason>"` format bleeding into the display
  text. Fixed with `.split("\n", 1)[1]` to show just the reason.
  Rerunning the same question afterward triggered no warning at all —
  not a failure, a real, expected demonstration of LLM
  non-determinism showing up in the validation layer itself, not just
  SQL generation (same well-documented theme from all project, new
  context).
- **Week 5 complete** — full end-to-end testing, three real bugs found
  and fixed on fresh data, and both capabilities now genuinely
  integrated into one working, polished app — completed well ahead of
  the original Mon Sep 7–Fri Sep 11 schedule, compressed into a handful
  of extended sessions across three days per Hamsa's own pacing choice
  this week.
