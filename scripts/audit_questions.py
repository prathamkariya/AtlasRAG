"""Audit EXISTING questions against their gold evidence (does not modify the question file,
so run1's benchmark stays frozen). Writes data/bench/audit.jsonl.
  python scripts/audit_questions.py --status accepted --split test"""
import argparse, json, sys
from collections import Counter
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from tqdm import tqdm
from atlasrag.config import load_config, resolve
from atlasrag.llm import LLMClient
from atlasrag.bench.schema import load_questions
from atlasrag.bench.validate import judge_support, verdict

ap = argparse.ArgumentParser()
ap.add_argument("--file", default="data/bench/questions.jsonl")
ap.add_argument("--status", default="accepted"); ap.add_argument("--split", default="test")
ap.add_argument("--model"); ap.add_argument("--out", default="data/bench/audit.jsonl")
a = ap.parse_args()

cfg = load_config()
text_of = {}
for l in open(resolve(cfg["retrieval"]["index_dir"]) / "chunks.jsonl", encoding="utf-8"):
    c = json.loads(l); text_of[c["chunk_id"]] = c["text"]
llm = LLMClient(cfg["llm"], cache_root=resolve(cfg["llm"]["cache_dir"]))
qs = load_questions(resolve(a.file), status=a.status, split=a.split)

reasons, bad = Counter(), []
out = resolve(a.out); out.parent.mkdir(parents=True, exist_ok=True)
with open(out, "w", encoding="utf-8") as f:
    for q in tqdm(qs, desc="audit"):
        v = judge_support(llm, q.question, q.reference_answer, [text_of[i] for i in q.gold_chunk_ids], a.model)
        ok, rs = verdict(v, q.qtype)
        f.write(json.dumps({"id": q.id, "qtype": q.qtype, "ok": ok, "reasons": rs, "verdict": v}) + "\n")
        if not ok:
            bad.append((q, rs, v)); reasons.update(rs)
print(f"\n{len(qs) - len(bad)}/{len(qs)} pass the support audit; reasons: {dict(reasons)}\n")
for q, rs, v in bad:
    print(f"- {q.id} [{q.qtype}] {rs}\n    Q: {q.question[:150]}\n    judge: {v.get('problems', '')}")
print(f"\nfull results: {out}   (the judge is a filter; read the flagged ones yourself)")
