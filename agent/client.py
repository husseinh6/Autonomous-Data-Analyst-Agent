"""
Anthropic API client wrapper.

Handles auth (reads ANTHROPIC_API_KEY from env) and model selection —
Sonnet 5 for reasoning-heavy calls (cleaning recommendations, SQL
generation, validation), Haiku 4.5 as a cheaper option if needed later.

Not yet implemented.
"""

import os
from dotenv import load_dotenv
from anthropic import Anthropic

def get_client():
    load_dotenv()
    api_key = os.getenv("sk-ant-api03-rg0...6QAA")
    return Anthropic(api_key=api_key)
    
    
if __name__ == "__main__":
    client = get_client()
    response = client.messages.create(
        model="claude-sonnet-5",
        max_tokens=100,
        messages=[{"role": "user", "content": "Say hello in one sentence."}]
    )
    print(response.content[0].text)