from __future__ import annotations
from .base import Router, RouteDecision


class CompassRouter(Router):
    """Experiment D. Placeholder until Week 3.

    Contract: route(query) -> RouteDecision(label in {SIMPLE, MULTI_HOP, UNCERTAIN},
    confidence = softmax probability of the predicted class). Implementation: small
    frozen base model + LoRA adapter + classification head, trained in
    notebooks/ on Kaggle, loaded here from a local path or the HF Hub.
    Compass must never see the answering LLM's context (isolation rule)."""
    name = "compass"

    def route(self, query: str) -> RouteDecision:
        raise NotImplementedError("Compass is trained in Week 3. Use 'heuristic' in the meantime.")
