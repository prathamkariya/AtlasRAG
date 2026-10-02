from __future__ import annotations
from ..routers import build_router, EscalatingRouter

CODES = {"A": "vanilla", "B": "static", "C": "llm", "D": "compass", "E": "oracle", "E2": "oracle",
         "F": "strongest", "G": "multihop", "K": "static_k10", "H": "heuristic"}
NAMES = {"A": "A_vanilla", "B": "B_static", "C": "C_llm_router", "D": "D_compass",
         "E": "E_oracle", "E2": "E2_oracle_v2",
         "F": "F_always_uncertain", "G": "G_always_multi_hop", "K": "K_static_k10",
         "H": "H_heuristic_devonly"}


def make_router(code: str, cfg: dict, llm, questions, escalate: float | None = None):
    gold = None
    if code == "E":
        gold = {q.question: q.gold_route for q in questions if q.gold_route}
    elif code == "E2":
        gold = {q.question: q.gold_route_v2 for q in questions if q.gold_route_v2}
    r = build_router(CODES[code], cfg, llm=llm, gold=gold)
    if escalate is not None and code in ("D", "H"):
        r = EscalatingRouter(r, build_router("llm", cfg, llm=llm), escalate)
    return r
