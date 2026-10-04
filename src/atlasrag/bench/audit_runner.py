"""Resumable support audit. Appends one JSON line per judged question, skips ids already
in the output file, and stops cleanly (no traceback) on a rate limit."""
from __future__ import annotations
import json
import time
from collections import Counter
from pathlib import Path

from ..ratelimit import call_with_quota_wait, is_quota_error, suggested_wait
from .validate import judge_support, verdict


def load_done(out_path) -> dict:
    p = Path(out_path)
    if not p.exists():
        return {}
    return {r["id"]: r for r in (json.loads(l) for l in open(p, encoding="utf-8") if l.strip())}


def run_audit(llm, questions, text_of: dict, out_path, model=None, wait_on_rate_limit=False,
              sleep=time.sleep, log=print, progress=None, max_resumes: int = 6) -> dict:
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    done = load_done(out_path)
    todo = [q for q in questions if q.id not in done]
    it = progress(todo) if progress else todo
    stopped, n_new = None, 0
    with open(out_path, "a", encoding="utf-8") as f:
        for q in it:
            passages = [text_of[i] for i in q.gold_chunk_ids]
            call = lambda: judge_support(llm, q.question, q.reference_answer, passages, model)
            try:
                v = call_with_quota_wait(call, max_resumes=max_resumes, sleep=sleep, log=log) \
                    if wait_on_rate_limit else call()
            except Exception as e:
                if not is_quota_error(e):
                    raise
                stopped = {"reason": "rate_limited", "before_id": q.id, "suggested_wait_s": suggested_wait(e)}
                break
            ok, reasons = verdict(v, q.qtype)
            f.write(json.dumps({"id": q.id, "qtype": q.qtype, "ok": ok, "reasons": reasons, "verdict": v}) + "\n")
            f.flush()
            n_new += 1
    return {"already_done": len(done), "new": n_new, "total": len(questions), "stopped": stopped}


def summarize(out_path, questions) -> dict:
    rows = load_done(out_path)
    mine = [rows[q.id] for q in questions if q.id in rows]
    reasons = Counter(r for row in mine if not row["ok"] for r in row["reasons"])
    return {"judged": len(mine), "passed": sum(r["ok"] for r in mine),
            "reasons": dict(reasons), "flagged": [r for r in mine if not r["ok"]]}
