from __future__ import annotations
import math


def evidence_recall(gold_ids: list[str], retrieved_ids: list[str]) -> float:
    g = set(gold_ids)
    return len(g & set(retrieved_ids)) / len(g) if g else math.nan


def paper_recall(gold_papers: list[str], retrieved_papers: list[str]) -> float:
    g = set(gold_papers)
    return len(g & set(retrieved_papers)) / len(g) if g else math.nan


def percentile(values: list[float], p: float) -> float:
    if not values:
        return math.nan
    v = sorted(values)
    k = (len(v) - 1) * p / 100
    lo, hi = math.floor(k), math.ceil(k)
    return v[lo] if lo == hi else v[lo] + (v[hi] - v[lo]) * (k - lo)
