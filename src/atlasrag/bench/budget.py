"""A hard stop for unattended generation: stop when this invocation has spent N provider tokens.
Counts only tokens actually sent to the provider (cache hits are free), so a resume does not 'pay' for replays."""
from __future__ import annotations


def tokens_used(stats: dict) -> int:
    return int(stats.get("provider_prompt_tokens", 0)) + int(stats.get("provider_completion_tokens", 0))


def over_budget(stats: dict, limit: int) -> bool:
    """limit <= 0 means 'no budget'."""
    return limit > 0 and tokens_used(stats) >= limit
