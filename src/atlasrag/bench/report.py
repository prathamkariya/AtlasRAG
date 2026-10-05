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


def cluster_bootstrap_ci(values, clusters, n=2000, seed=0, min_clusters=5):
    """Bootstrap that resamples whole CLUSTERS (papers), not questions.

    Questions drawn from the same paper are not independent (here 10 of 27 come from ONE paper), so the
    question-level CI is too narrow. Returns (mean, lo, hi, n_clusters). With fewer than `min_clusters`
    clusters the interval is undefined (NaN) rather than falsely tight."""
    pairs = [(v, c) for v, c in zip(values, clusters) if not (isinstance(v, float) and math.isnan(v))]
    if not pairs:
        return (math.nan, math.nan, math.nan, 0)
    groups: dict = {}
    for v, c in pairs:
        groups.setdefault(c, []).append(v)
    sums = np.array([sum(g) for g in groups.values()], dtype=float)
    cnts = np.array([len(g) for g in groups.values()], dtype=float)
    mean = float(sums.sum() / cnts.sum())
    if len(groups) < min_clusters:
        return (mean, math.nan, math.nan, len(groups))
    rng = np.random.RandomState(seed)
    idx = rng.randint(0, len(groups), size=(n, len(groups)))
    reps = sums[idx].sum(axis=1) / cnts[idx].sum(axis=1)
    return (mean, float(np.percentile(reps, 2.5)), float(np.percentile(reps, 97.5)), len(groups))


def cluster_map(questions) -> dict:
    """question id -> cluster id (its first gold paper; multi-paper questions are assigned to their first paper)."""
    return {q.id: (q.gold_paper_ids[0] if q.gold_paper_ids else q.id) for q in questions}


def _exp_files(group_dir) -> dict[str, Path]:
    # zero-byte files are aborted runs (e.g. D_compass before Compass existed); loading them yields NaN rows/rankings
    return {p.stem: p for p in sorted(Path(group_dir).glob("*.jsonl")) if p.stat().st_size > 0}


def build_rows(group_dir, questions) -> list[dict]:
    gold_route = {q.id: q.gold_route for q in questions}
    clusters = cluster_map(questions)
    allowed_ids = set(gold_route)
    rows = []
    for exp, path in _exp_files(group_dir).items():
        # A cleaned benchmark is a distinct population from the historical run.
        # Do not let its report include rows for rejected questions.
        res = [r for r in load_jsonl(path) if r.get("id") in allowed_ids]
        for qt in ("ALL",) + QTYPES:
            sub = [r for r in res if qt == "ALL" or r["qtype"] == qt]
            if not sub:
                continue
            rec = bootstrap_ci([r["evidence_recall"] for r in sub])
            crec = cluster_bootstrap_ci([r["evidence_recall"] for r in sub], [clusters.get(r["id"], r["id"]) for r in sub])
            lat = [r["metrics"]["latency_s"] for r in sub]
            labelled = [r for r in sub if r["route"]["label"] in ("SIMPLE", "MULTI_HOP", "UNCERTAIN")
                        and not str(r["route"].get("source", "")).startswith("fixed:")
                        and gold_route.get(r["id"])]
            rows.append({
                "experiment": exp, "qtype": qt, "n": len(sub),
                "recall": rec[0], "recall_lo": rec[1], "recall_hi": rec[2],
                "n_papers": crec[3], "recall_clo": crec[1], "recall_chi": crec[2],
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
    ci = lambda lo, hi: "n/a" if (math.isnan(lo) or math.isnan(hi)) else f"[{lo:.2f}, {hi:.2f}]"
    out = ["| experiment | type | n | papers | evidence recall [95% CI, by question] | [95% CI, by paper] | LLM calls | tokens | p50 s | p95 s | escalated | route acc |",
           "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        out.append(f"| {r['experiment']} | {r['qtype']} | {r['n']} | {r.get('n_papers', '-')} | {f(r['recall'])} [{f(r['recall_lo'])}, {f(r['recall_hi'])}] "
                   f"| {ci(r.get('recall_clo', math.nan), r.get('recall_chi', math.nan))} "
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


def paired_vs(group_dir, ref: str, n: int = 2000, seed: int = 0, questions=None) -> list[dict]:
    """Per-question recall difference vs a reference experiment (prefix match, e.g. 'B').
    Paired CIs are much tighter than comparing two overlapping marginal CIs.
    Pass `questions` to ALSO get a cluster-by-paper CI (clo/chi/n_papers), which is the honest one when
    several questions come from the same paper."""
    files = _exp_files(group_dir)
    ref_key = next(k for k in files if k.startswith(ref))
    allowed_ids = {q.id for q in questions} if questions is not None else None
    ref_by = {
        r["id"]: r["evidence_recall"]
        for r in load_jsonl(files[ref_key])
        if allowed_ids is None or r.get("id") in allowed_ids
    }
    clusters = cluster_map(questions) if questions is not None else None
    rows = []
    for k, p in files.items():
        if k == ref_key:
            continue
        got = [r for r in load_jsonl(p) if r["id"] in ref_by]
        d = [r["evidence_recall"] - ref_by[r["id"]] for r in got]
        m, lo, hi = bootstrap_ci(d, n, seed)
        row = {"experiment": k, "vs": ref_key, "n": len(d), "mean_diff": m, "lo": lo, "hi": hi,
               "wins": sum(x > 0 for x in d), "ties": sum(x == 0 for x in d),
               "losses": sum(x < 0 for x in d)}
        if clusters is not None:
            _, clo, chi, npap = cluster_bootstrap_ci(d, [clusters.get(r["id"], r["id"]) for r in got], n, seed)
            row.update({"clo": clo, "chi": chi, "n_papers": npap})
        rows.append(row)
    return rows


def paired_markdown(rows) -> str:
    f = lambda x: "-" if (isinstance(x, float) and math.isnan(x)) else f"{x:+.2f}"
    cl = bool(rows) and "clo" in rows[0]
    head = "| experiment | vs | n | mean recall diff [95% CI, by question] | wins/ties/losses | CI excludes 0? |"
    out = [head + (" papers | [95% CI, by paper] | excludes 0 by paper? |" if cl else ""), "|---|---|---|---|---|---|" + ("---|---|---|" if cl else "")]
    for r in rows:
        sig = "yes" if (r["lo"] > 0 or r["hi"] < 0) else "no"
        line = (f"| {r['experiment']} | {r['vs']} | {r['n']} | {f(r['mean_diff'])} [{f(r['lo'])}, {f(r['hi'])}] "
                f"| {r['wins']}/{r['ties']}/{r['losses']} | {sig} |")
        if cl:
            undefined = math.isnan(r["clo"]) or math.isnan(r["chi"])
            csig = "n/a" if undefined else ("yes" if (r["clo"] > 0 or r["chi"] < 0) else "no")
            line += f" {r['n_papers']} | {'n/a' if undefined else '[' + f(r['clo']) + ', ' + f(r['chi']) + ']'} | {csig} |"
        out.append(line)
    return "\n".join(out)
