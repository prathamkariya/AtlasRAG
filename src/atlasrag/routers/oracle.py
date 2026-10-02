from __future__ import annotations
from .base import Router, RouteDecision


def _norm(q: str) -> str:
    return " ".join(q.lower().split())


class OracleRouter(Router):
    """Experiment E. Looks up the gold route for each benchmark question."""
    name = "oracle"

    def __init__(self, gold: dict[str, str]):
        self.gold = {_norm(k): v for k, v in gold.items()}

    def route(self, query: str) -> RouteDecision:
        try:
            return RouteDecision(self.gold[_norm(query)], 1.0, self.name)
        except KeyError:
            raise KeyError(f"No gold route for query: {query[:80]!r}") from None
