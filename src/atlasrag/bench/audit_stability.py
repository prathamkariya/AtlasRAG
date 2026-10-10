"""How much should we trust the LLM support audit? Run the SAME judge several times on the SAME questions
(each repetition under its own cache namespace, so every repetition is a fresh provider call) and compare.

Measured on this project: two audits of the same 27 questions disagreed on 4 (23/27 = 85% raw agreement, 6/10 on
the non-simple questions). A reasoning model at temperature 0 is not deterministic. So a single run must not be the
rule for rejecting or keeping a benchmark question. Classes:
    stable_pass   every run passed        -> keep
    stable_fail   every run failed        -> reject
    unstable      the runs disagree       -> a HUMAN decides (read the question and its passages)
"""
from __future__ import annotations
import json
from collections import Counter, defaultdict
from pathlib import Path

from .audit_runner import load_done, run_audit

STABLE_PASS, STABLE_FAIL, UNSTABLE = "stable_pass", "stable_fail", "unstable"


def classify(verdicts: dict) -> dict:
    """verdicts: question id -> list of booleans (one per judge run). Returns id -> class."""
    out = {}
    for qid, vs in verdicts.items():
        if not vs:
            continue
        out[qid] = STABLE_PASS if all(vs) else STABLE_FAIL if not any(vs) else UNSTABLE
    return out


def summarize(verdicts: dict, qtypes: dict) -> dict:
    cls = classify(verdicts)
    by_type = defaultdict(Counter)
    for qid, c in cls.items():
        by_type[qtypes.get(qid, "?")][c] += 1
    runs = max((len(v) for v in verdicts.values()), default=0)
    pair_agree = pair_total = 0
    for vs in verdicts.values():
        for i in range(len(vs)):
            for j in range(i + 1, len(vs)):
                pair_total += 1
                pair_agree += vs[i] == vs[j]
    return {"runs": runs, "questions": len(cls), "classes": dict(Counter(cls.values())),
            "by_type": {t: dict(c) for t, c in sorted(by_type.items())},
            "pairwise_agreement": (pair_agree / pair_total) if pair_total else float("nan"),
            "per_question": {q: {"verdicts": verdicts[q], "class": c, "type": qtypes.get(q, "?")} for q, c in cls.items()}}


def run_stability(make_llm, questions, text_of: dict, out_dir, reps: int = 2, model=None,
                  wait_on_rate_limit=False, sleep=None, log=print, progress=None) -> dict:
    """make_llm(namespace) -> LLM client. Resumable per repetition (each writes out_dir/audit_stability_r<k>.jsonl)."""
    import time
    out_dir = Path(out_dir)
    stops = []
    for k in range(1, reps + 1):
        res = run_audit(make_llm(f"audit_stability_r{k}"), questions, text_of, out_dir / f"audit_stability_r{k}.jsonl",
                        model=model, wait_on_rate_limit=wait_on_rate_limit, sleep=sleep or time.sleep, log=log,
                        progress=progress)
        if res["stopped"]:
            stops.append({"rep": k, **res["stopped"]})
            break                                    # a rate limit would hit the next repetition too
    return {"stopped": stops}


def collect(questions, rep_files, extra_runs=()) -> dict:
    """Verdict lists per question from repetition files plus any already-existing runs ({id: bool} dicts).
    Only questions judged in EVERY run are compared, so a half-finished repetition cannot bias the result."""
    runs = [{qid: r["ok"] for qid, r in load_done(f).items()} for f in rep_files] + list(extra_runs)
    ids = [q.id for q in questions if all(q.id in r for r in runs)]
    return {i: [r[i] for r in runs] for i in ids}


def write_report(path, summary: dict) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(summary, indent=1), encoding="utf-8")
