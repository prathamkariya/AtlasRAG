from .base import Router, RouteDecision, LABELS
from .fixed import FixedRouter
from .heuristic import HeuristicRouter
from .llm_router import LLMRouter
from .oracle import OracleRouter
from .compass import CompassRouter
from .escalating import EscalatingRouter


def build_router(name: str, cfg: dict, llm=None, gold=None):
    name = name.lower()
    if name == "vanilla":
        return FixedRouter("VANILLA")
    if name == "static":
        return FixedRouter("STATIC")
    if name == "strongest":            # control F: always the top strategy
        return FixedRouter("UNCERTAIN")
    if name == "multihop":             # control G: always decompose
        return FixedRouter("MULTI_HOP")
    if name == "static_k10":           # control K: static, k matched to UNCERTAIN
        return FixedRouter("STATIC_K10")
    if name == "heuristic":
        return HeuristicRouter()
    if name == "llm":
        if llm is None:
            raise ValueError("llm router needs an LLM client")
        return LLMRouter(llm)
    if name == "oracle":
        if gold is None:
            raise ValueError("oracle router needs gold labels")
        return OracleRouter(gold)
    if name == "compass":
        return CompassRouter()
    raise ValueError(f"unknown router: {name}")


AVAILABLE_NOW = ["vanilla", "static", "heuristic", "llm"]
