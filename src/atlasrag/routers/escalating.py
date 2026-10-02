from __future__ import annotations
from .base import Router, RouteDecision


class EscalatingRouter(Router):
    """If the primary router's confidence is below threshold, ask the fallback
    (an LLM router). This is the mechanism H3 tests; sweep the threshold."""

    def __init__(self, primary: Router, fallback: Router, threshold: float):
        self.primary, self.fallback, self.threshold = primary, fallback, threshold
        self.name = f"{primary.name}+escalate@{threshold}"

    def route(self, query: str) -> RouteDecision:
        d = self.primary.route(query)
        if d.confidence >= self.threshold:
            return d
        f = self.fallback.route(query)
        f.escalated = True
        f.source = f"{self.fallback.name} (escalated from {self.primary.name})"
        return f
