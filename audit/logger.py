"""
Audit-trail logger.

Writes one JSON-lines entry per autonomous decision (cleaning or query) to
audit_log.jsonl — timestamp, action, before/after, reason, risk/confidence
flag. See Technical Design.md Section 6 for the format.

Not yet implemented.
"""
