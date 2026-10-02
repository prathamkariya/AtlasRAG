from __future__ import annotations
import json
import re
from .base import Router, RouteDecision, LABELS

PROMPT = """You route questions about scientific papers to a retrieval strategy.
Labels:
- SIMPLE: answerable from one passage of one paper (a single fact or finding).
- MULTI_HOP: needs evidence combined from several passages or papers (comparison, conflict, change over time, chains of reasoning).
- UNCERTAIN: you cannot tell.
Reply with JSON only: {"label": "<LABEL>", "confidence": <0.0-1.0>}"""


class LLMRouter(Router):
    """Experiment C. Verbalized confidence from the LLM."""
    name = "llm"

    def __init__(self, llm):
        self.llm = llm

    def route(self, query: str) -> RouteDecision:
        out = self.llm.chat([{"role": "system", "content": PROMPT},
                             {"role": "user", "content": query}],
                            temperature=0.0, max_tokens=40)
        m = re.search(r"\{.*\}", out, re.S)
        try:
            d = json.loads(m.group(0)) if m else {}
            label = str(d.get("label", "")).upper()
            conf = float(d.get("confidence", 0.0))
            if label not in LABELS:
                raise ValueError(label)
            return RouteDecision(label, max(0.0, min(1.0, conf)), self.name)
        except (ValueError, TypeError):
            return RouteDecision("UNCERTAIN", 0.0, f"{self.name}:parse_fail")
