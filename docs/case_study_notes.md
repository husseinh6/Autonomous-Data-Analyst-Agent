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
