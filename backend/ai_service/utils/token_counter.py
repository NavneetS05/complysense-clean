# Use: Helper utility for calculating and gating token usage.

def approximate_token_count(text: str) -> int:
    return max(1, len(text.split()))
