"""
MySQL connection + schema introspection.

Read-only connection to yelp_db (local for dev, trimmed cloud subset for
the deployed demo — see Technical Design.md Section 1). Dedicated
read-only DB user only; SELECT-only enforced at both the DB grant level
and in application code.

Not yet implemented.
"""
