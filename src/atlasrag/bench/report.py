"""Stratified results with bootstrap CIs. With ~25 questions per type, CIs are
wide: only claim a question-type effect (H4) when intervals actually separate."""
from __future__ import annotations
import json
import math
from pathlib import Path

import numpy as np

from .metrics import percentile
from .schema import QTYPES


def load_jsonl(path) -> list[dict]:
    return [json.loads(l) for l in open(path, encoding="utf-8") if l.strip()]


def bootstrap_ci(values, n=1000, seed=0):
    v = np.array([x for x in values if not (isinstance(x, float) and math.isnan(x))], dtype=float)
    if len(v) == 0:
        return (math.nan, math.nan, math.nan)
    if len(v) == 1:
        return (float(v[0]),) * 3
    rng = np.random.RandomState(seed)
    means = np.array([rng.choice(v, len(v)).mean() for _ in range(n)])
    return (float(v.mean()), float(np.percentile(means, 2.5)), float(np.percentile(means, 97.5)))


def _exp_files(group_dir) -> dict[str, Path]:
    return {p.stem: p for p in sorted(Path(group_dir).glob("*.jsonl"))}


def build_rows(group_dir, questions) -> list[dict]:
    gold_route = {q.id: q.gold_route for q in questions}
    rows = []
    for exp, path in _exp_files(group_dir).items():
        res = load_jsonl(path)
        for qt in ("ALL",) + QTYPES:
            sub = [r for r in res if qt == "ALL" or r["qtype"] == qt]
            if not sub:
                continue
            rec = bootstrap_ci([r["evidence_recall"] for r in sub])
            lat = [r["metrics"]["latency_s"] for r in sub]
            labelled = [r for r in sub if r["route"]["label"] in ("SIMPLE", "MULTI_HOP", "UNCERTAIN")
                        and not str(r["route"].get("source", "")).startswith("fixed:")
                        and gold_route.get(r["id"])]
            rows.append({
                "experiment": exp, "qtype": qt, "n": len(sub),
                "recall": rec[0], "recall_lo": rec[1], "recall_hi": rec[2],
                "llm_calls": float(np.mean([r["metrics"]["llm_calls"] for r in sub])),
                "tokens": float(np.mean([r["metrics"]["prompt_tokens"] + r["metrics"]["completion_tokens"] for r in sub])),
                "lat_p50": percentile(lat, 50), "lat_p95": percentile(lat, 95),
                "escalated": float(np.mean([bool(r["route"].get("escalated")) for r in sub])),
                "route_acc": (float(np.mean([r["route"]["label"] == gold_route[r["id"]] for r in labelled]))
                              if labelled else math.nan),
            })
    return rows


def to_markdown(rows) -> str:
    f = lambda x, d=2: "-" if (isinstance(x, float) and math.isnan(x)) else f"{x:.{d}f}"
    out = ["| experiment | type | n | evidence recall [95% CI] | LLM calls | tokens | p50 s | p95 s | escalated | route acc |",
           "|---|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        out.append(f"| {r['experiment']} | {r['qtype']} | {r['n']} | {f(r['recall'])} [{f(r['recall_lo'])}, {f(r['recall_hi'])}] "
                   f"| {f(r['llm_calls'])} | {f(r['tokens'], 0)} | {f(r['lat_p50'])} | {f(r['lat_p95'])} | {f(r['escalated'])} | {f(r['route_acc'])} |")
    return "\n".join(out)


def compare_groups(dir_a, dir_b, metric="evidence_recall") -> dict:
    """Benchmark-honesty check: does the ranking of experiments survive a rerun?"""
    def means(d):
        return {e: float(np.nanmean([r[metric] for r in load_jsonl(p)])) for e, p in _exp_files(d).items()}
    a, b = means(dir_a), means(dir_b)
    common = sorted(set(a) & set(b))
    rank = lambda m: [e for e in sorted(common, key=lambda e: -m[e])]
    ra, rb = rank(a), rank(b)
    return {"ranking_run1": ra, "ranking_run2": rb, "ranking_stable": ra == rb,
            "abs_diff": {e: abs(a[e] - b[e]) for e in common}}


def paired_vs(group_dir, ref: str, n: int = 2000, seed: int = 0) -> list[dict]:
    """Per-question recall difference vs a reference experiment (prefix match, e.g. 'B').
    Paired CIs are much tighter than comparing two overlapping marginal CIs."""
    files = _exp_files(group_dir)
    ref_key = next(k for k in files if k.startswith(ref))
    ref_by = {r["id"]: r["evidence_recall"] for r in load_jsonl(files[ref_key])}
    rows = []
    for k, p in files.items():
        if k == ref_key:
            continue
        d = [r["evidence_recall"] - ref_by[r["id"]] for r in load_jsonl(p) if r["id"] in ref_by]
        m, lo, hi = bootstrap_ci(d, n, seed)
        rows.append({"experiment": k, "vs": ref_key, "n": len(d), "mean_diff": m, "lo": lo, "hi": hi,
                     "wins": sum(x > 0 for x in d), "ties": sum(x == 0 for x in d),
                     "losses": sum(x < 0 for x in d)})
    return rows


def paired_markdown(rows) -> str:
    f = lambda x: "-" if (isinstance(x, float) and math.isnan(x)) else f"{x:+.2f}"
    out = ["| experiment | vs | n | mean recall diff [95% CI] | wins/ties/losses | CI excludes 0? |", "|---|---|---|---|---|---|"]
    for r in rows:
        sig = "yes" if (r["lo"] > 0 or r["hi"] < 0) else "no"
        out.append(f"| {r['experiment']} | {r['vs']} | {r['n']} | {f(r['mean_diff'])} [{f(r['lo'])}, {f(r['hi'])}] "
                   f"| {r['wins']}/{r['ties']}/{r['losses']} | {sig} |")
    return "\n".join(out)
