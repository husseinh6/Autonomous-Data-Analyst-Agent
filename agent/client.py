"""
Anthropic API client wrapper.

Handles auth (reads ANTHROPIC_API_KEY from env) and model selection —
Sonnet 5 for reasoning-heavy calls (cleaning recommendations, SQL
generation, validation), Haiku 4.5 as a cheaper option if needed later.

Not yet implemented.
"""
