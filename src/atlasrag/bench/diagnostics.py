"""Route diagnostics: how does a router compare to the oracle (E) and to the
always-strongest control (F)? Route accuracy is NOT the headline; these are.

A router can disagree with the oracle's label and lose nothing (over-routing that
still covers evidence), or agree on cost and still miss evidence. We separate:
 wasted    = routed more expensively than oracle, recall no better  (pure cost)
 harmful   = routed cheaper than oracle, recall worse               (quality loss)"""
from __future__ import annotations
from collections import Counter, defaultdict

import numpy as np

RANK = {"SIMPLE": 0, "MULTI_HOP": 1, "UNCERTAIN": 2}


def diagnose(router_rows, oracle_rows, strong_rows, questions) -> dict:
    by = lambda rows: {r["id"]: r for r in rows}
    R, O, S, Q = by(router_rows), by(oracle_rows), by(strong_rows), {q.id: q for q in questions}
    ids = [i for i in R if i in O and i in S and i in Q]
    if not ids:
        raise ValueError("no overlapping question ids between router, oracle and strong runs")
    if any(R[i]["route"]["label"] not in RANK for i in ids):
        raise ValueError("diagnostics need an adaptive router whose labels are SIMPLE/MULTI_HOP/UNCERTAIN")
    calls = lambda r: r["metrics"]["llm_calls"]
    wasted = harmful = over = under = exact = 0
    confusion: dict = defaultdict(Counter)
    suff_total = suff_ok = 0
    for i in ids:
        rl, ol = R[i]["route"]["label"], O[i]["route"]["label"]
        confusion[rl][ol] += 1
        exact += rl == ol
        if RANK[rl] > RANK[ol]:
            over += 1
            wasted += R[i]["evidence_recall"] <= O[i]["evidence_recall"] + 1e-9
        elif RANK[rl] < RANK[ol]:
            under += 1
            harmful += R[i]["evidence_recall"] < O[i]["evidence_recall"] - 1e-9
        if Q[i].oracle_sufficient:
            suff_total += 1
            suff_ok += R[i]["evidence_recall"] >= 1.0 - 1e-9
    n = len(ids)
    mean = lambda D, f: float(np.mean([f(D[i]) for i in ids]))
    rec = lambda r: r["evidence_recall"]
    out = {
        "n": n,
        "recall": mean(R, rec), "recall_oracle": mean(O, rec), "recall_strong": mean(S, rec),
        "calls": mean(R, calls), "calls_oracle": mean(O, calls), "calls_strong": mean(S, calls),
        "recall_retention_vs_strong": mean(R, rec) / mean(S, rec) if mean(S, rec) > 0 else float("nan"),
        "calls_saved_vs_strong": mean(S, calls) - mean(R, calls),
        "regret_recall_vs_oracle": mean(O, rec) - mean(R, rec),
        "regret_calls_vs_oracle": mean(R, calls) - mean(O, calls),
        "exact_route_match": exact / n,
        "over_routed": over, "wasted": wasted, "under_routed": under, "harmful": harmful,
        "sufficient_cover_rate": (suff_ok / suff_total) if suff_total else float("nan"),
        "confusion": {k: dict(v) for k, v in confusion.items()},
    }
    return out


def to_markdown(d: dict) -> str:
    f = lambda x: f"{x:.2f}"
    lines = [f"n = {d['n']}",
             f"recall      router {f(d['recall'])} | oracle {f(d['recall_oracle'])} | always-strongest {f(d['recall_strong'])}",
             f"LLM calls   router {f(d['calls'])} | oracle {f(d['calls_oracle'])} | always-strongest {f(d['calls_strong'])}",
             f"recall retained vs strongest: {f(d['recall_retention_vs_strong'])}   calls saved vs strongest: {d['calls_saved_vs_strong']:+.2f}",
             f"regret vs oracle: recall {d['regret_recall_vs_oracle']:+.2f}, calls {d['regret_calls_vs_oracle']:+.2f}",
             f"covered the evidence on {f(d['sufficient_cover_rate'])} of retrievable questions",
             f"over-routed {d['over_routed']} (wasted {d['wasted']}), under-routed {d['under_routed']} (harmful {d['harmful']}), "
             f"exact label match {f(d['exact_route_match'])} (diagnostic only)",
             "confusion (rows = router, cols = oracle): " + str(d["confusion"])]
    return "\n".join(lines)
