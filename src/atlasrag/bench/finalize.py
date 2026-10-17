"""The ONLY door into a final benchmark. A question passes only if every gate below holds; the result is a file that
experiments can use unchanged (all rows status='accepted') plus a manifest that pins what it is.

Gates (each failure is recorded by name, so you can see WHY questions were lost):
  not_accepted / not_test_split         reviewed-in and drawn from a test-split paper
  no_human_review                       a person made the final decision (review:human in notes); LLM-applied A/R letters do not count
  no_stability_record / too_few_judge_runs / judge_unstable / judge_stable_fail
                                        the support judge passed in EVERY run, and there were at least `require_runs` runs
  too_few_gold_chunks / needs_two_papers / chain_must_be_single_paper / unknown_qtype
                                        the evidence structure matches the question type
  no_judge_model_recorded               provenance of the audit exists
  duplicate_question / duplicate_gold_set
"""
from __future__ import annotations
import hashlib
import json
import re
import subprocess
import time
from collections import Counter

MIN_GOLD_CHUNKS = {"simple": 1, "multi_hop": 2, "conflicting": 2, "temporal": 2, "chain": 2}
CROSS_PAPER = {"multi_hop", "conflicting", "temporal"}


def norm_q(text: str) -> str:
    return re.sub(r"\W+", " ", text.lower()).strip()


def sha_text_bytes(b: bytes) -> str:
    return hashlib.sha256(b.replace(b"\r\n", b"\n")).hexdigest()


def gate_reasons(q, stability: dict, require_runs: int = 3, require_human: bool = True) -> list[str]:
    from .review_meta import review_mode
    r = []
    if q.status != "accepted":
        r.append("not_accepted")
    if q.split != "test":
        r.append("not_test_split")
    if require_human and review_mode(q) != "human":
        r.append("no_human_review")
    st = stability.get(q.id)
    if st is None:
        r.append("no_stability_record")
    else:
        if len(st["verdicts"]) < require_runs:
            r.append("too_few_judge_runs")
        if st["class"] != "stable_pass":
            r.append("judge_" + ("unstable" if st["class"] == "unstable" else "stable_fail"))
    if q.qtype not in MIN_GOLD_CHUNKS:
        r.append("unknown_qtype")
    else:
        papers = len(set(q.gold_paper_ids))
        if len(q.gold_chunk_ids) < MIN_GOLD_CHUNKS[q.qtype]:
            r.append("too_few_gold_chunks")
        if q.qtype in CROSS_PAPER and papers < 2:
            r.append("needs_two_papers")
        if q.qtype == "chain" and papers != 1:
            r.append("chain_must_be_single_paper")
    try:
        v = json.loads(q.validation) if q.validation else {}
    except json.JSONDecodeError:
        v = {}
    if not v.get("judge_model"):
        r.append("no_judge_model_recorded")
    return r


def finalize(questions, stability: dict, require_runs: int = 3, require_human: bool = True):
    """Returns (final_questions, rejected {id: [reasons]})."""
    final, rejected = [], {}
    seen_q, seen_gold = set(), set()
    for q in questions:
        reasons = gate_reasons(q, stability, require_runs, require_human)
        if not reasons:
            key_q, key_g = norm_q(q.question), (q.qtype, tuple(sorted(q.gold_chunk_ids)))
            if key_q in seen_q:
                reasons.append("duplicate_question")
            elif key_g in seen_gold:
                reasons.append("duplicate_gold_set")
            else:
                seen_q.add(key_q); seen_gold.add(key_g)
        if reasons:
            rejected[q.id] = reasons
        else:
            final.append(q)
    return final, rejected


def parse_minimums(spec: str) -> dict:
    out = {}
    for part in filter(None, (spec or "").split(",")):
        k, v = part.split("=")
        out[k.strip()] = int(v)
    return out


def check_minimums(by_type: dict, minimums: dict) -> list[str]:
    return [f"{t}: {by_type.get(t, 0)} < {n}" for t, n in minimums.items() if by_type.get(t, 0) < n]


def build_manifest(benchmark_id, final, rejected, questions_sha256, corpus_manifest_sha256=None, require_runs=3,
                   source_file="", git_commit="unknown") -> dict:
    from .review_meta import review_mode
    papers = Counter(p for q in final for p in dict.fromkeys(q.gold_paper_ids))
    first = Counter((q.gold_paper_ids[0] if q.gold_paper_ids else "?") for q in final)
    models = {"generator": set(), "judge": set()}
    for q in final:
        try:
            v = json.loads(q.validation)
            models["generator"].add(v.get("generator_model", "?")); models["judge"].add(v.get("judge_model", "?"))
        except Exception:
            pass
    n = len(final)
    return {"benchmark_id": benchmark_id, "created": time.strftime("%Y-%m-%dT%H:%M:%S"), "git_commit": git_commit,
            "source_file": source_file, "corpus_manifest_sha256": corpus_manifest_sha256,
            "questions_sha256": questions_sha256, "require_runs": require_runs,
            "n_questions": n, "by_type": dict(Counter(q.qtype for q in final)),
            "n_distinct_papers": len(papers),
            "max_paper_share": round(max(first.values()) / n, 3) if n else None,       # share of questions whose FIRST gold paper is the most common one
            "review_modes": dict(Counter(review_mode(q) or "none" for q in final)),
            "generator_models": sorted(models["generator"]), "judge_models": sorted(models["judge"]),
            "same_model_generated_and_judged": bool(models["generator"] & models["judge"]),
            "rejected_total": len(rejected),
            "rejected_by_reason": dict(Counter(r for rs in rejected.values() for r in rs))}


def git_commit() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], stderr=subprocess.DEVNULL).decode().strip()
    except Exception:
        return "unknown"
