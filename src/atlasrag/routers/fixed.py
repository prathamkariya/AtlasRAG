from __future__ import annotations
from .base import Router, RouteDecision


class FixedRouter(Router):
    """Always the same strategy. Experiment A = FixedRouter('VANILLA'),
    Experiment B = FixedRouter('STATIC')."""

    def __init__(self, label: str):
        self.label, self.name = label, f"fixed:{label}"

    def route(self, query: str) -> RouteDecision:
        return RouteDecision(self.label, 1.0, self.name)
