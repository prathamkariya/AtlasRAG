from __future__ import annotations
from dataclasses import dataclass

LABELS = ("SIMPLE", "MULTI_HOP", "UNCERTAIN")


@dataclass
class RouteDecision:
    label: str                 # a key in config `strategies`
    confidence: float = 1.0
    source: str = ""
    escalated: bool = False


class Router:
    name = "base"

    def route(self, query: str) -> RouteDecision:
        raise NotImplementedError
