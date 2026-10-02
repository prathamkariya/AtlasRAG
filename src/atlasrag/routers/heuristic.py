from __future__ import annotations
import re
from .base import Router, RouteDecision

_MULTI = re.compile(r"\b(compare|contrast|versus|vs\.?|across|differ|disagree|conflict|"
                    r"consistent with|both|relationship between|agree|evolv|over time|"
                    r"which (?:paper|study)|papers|studies)\b", re.I)


class HeuristicRouter(Router):
    """DEVELOPMENT STAND-IN so the pipeline runs end to end before Compass
    exists. It is NOT a baseline for the experiments."""
    name = "heuristic"

    def route(self, query: str) -> RouteDecision:
        hits = len(_MULTI.findall(query))
        if hits >= 2:
            return RouteDecision("MULTI_HOP", 0.8, self.name)
        if hits == 1:
            return RouteDecision("MULTI_HOP", 0.55, self.name)
        return RouteDecision("SIMPLE", 0.7, self.name)
