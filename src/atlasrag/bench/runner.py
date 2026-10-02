from __future__ import annotations
import hashlib
import json
import subprocess
import time
from pathlib import Path

from .metrics import evidence_recall, paper_recall


def _git_commit() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "--short", "HEAD"],
                                       stderr=subprocess.DEVNULL).decode().strip()
    except Exception:
        return "unknown"


def file_hash(path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()[:12] if Path(path).exists() else "missing"


def run_experiment(pipeline, router, questions, out_path, retrieval_only=False,
                   meta: dict | None = None, tracker=None, progress=None) -> dict:
    """Resumable: question ids already in out_path are skipped."""
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    done = set()
    if out_path.exists():
        done = {json.loads(l)["id"] for l in open(out_path, encoding="utf-8") if l.strip()}
    meta = dict(meta or {})
    meta.update({"git_commit": _git_commit(), "started": time.strftime("%Y-%m-%dT%H:%M:%S"),
                 "retrieval_only": retrieval_only, "router": getattr(router, "name", "?"),
                 "n_questions": len(questions)})
    out_path.with_suffix(".meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")

    todo = [q for q in questions if q.id not in done]
    it = progress(todo) if progress else todo
    n = 0
    with open(out_path, "a", encoding="utf-8") as f:
        for q in it:
            res = pipeline.retrieve_only(q.question, router) if retrieval_only else pipeline.answer(q.question, router)
            cites = res["citations"]
            row = {
                "id": q.id, "qtype": q.qtype, "route": res["route"],
                "subqueries": res["subqueries"],
                "answer": res.get("answer"),
                "retrieved_chunk_ids": [c["chunk_id"] for c in cites],
                "evidence_recall": evidence_recall(q.gold_chunk_ids, [c["chunk_id"] for c in cites]),
                "paper_recall": paper_recall(q.gold_paper_ids, [c["paper_id"] for c in cites]),
                "metrics": res["metrics"],
            }
            f.write(json.dumps(row) + "\n")
            f.flush()
            if tracker is not None:
                tracker.log({"evidence_recall": row["evidence_recall"],
                             "llm_calls": row["metrics"]["llm_calls"],
                             "latency_s": row["metrics"]["latency_s"]})
            n += 1
    return {"ran": n, "skipped": len(done), "out": str(out_path)}
