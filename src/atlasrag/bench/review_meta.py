"""Who made a review decision? Recorded in Question.notes so the final benchmark can require a HUMAN decision.
  review:human         decided interactively by a person
  review:llm_assisted  decided by applying A/R letters that another model produced (review_questions.py --apply)"""
from __future__ import annotations

MODES = ("human", "llm_assisted")


def mark_review(q, mode: str) -> None:
    if mode not in MODES:
        raise ValueError(mode)
    tags = [t for t in (q.notes or "").split() if not t.startswith("review:")]      # last decision wins
    q.notes = " ".join(tags + [f"review:{mode}"])


def review_mode(q) -> str | None:
    for t in (q.notes or "").split():
        if t.startswith("review:"):
            return t.split(":", 1)[1]
    return None
