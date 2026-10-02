"""Why did an experiment miss gold evidence? Shows gold chunks vs what was retrieved.
  python scripts/inspect_failures.py --group run1 --exp E_oracle
  python scripts/inspect_failures.py --group run1 --exp C_llm_router --qtype multi_hop"""
import argparse, json, sys, textwrap
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from atlasrag.config import load_config, resolve
from atlasrag.bench.schema import load_questions
from atlasrag.bench.report import load_jsonl

ap = argparse.ArgumentParser()
ap.add_argument("--group", required=True); ap.add_argument("--exp", required=True)
ap.add_argument("--qtype"); ap.add_argument("--file", default="data/bench/questions.jsonl")
a = ap.parse_args()
cfg = load_config()
chunks = {}
for l in open(resolve(cfg["retrieval"]["index_dir"]) / "chunks.jsonl", encoding="utf-8"):
    c = json.loads(l); chunks[c["chunk_id"]] = c
qs = {q.id: q for q in load_questions(resolve(a.file), status="accepted")}
res = load_jsonl(resolve("results") / a.group / f"{a.exp}.jsonl")
for r in res:
    q = qs.get(r["id"])
    if not q or r["evidence_recall"] >= 1.0 or (a.qtype and r["qtype"] != a.qtype):
        continue
    print("=" * 90)
    print(f"{r['id']}  recall={r['evidence_recall']:.2f}  route={r['route']['label']}  subqueries={r['subqueries']}")
    print("Q:", q.question)
    got = set(r["retrieved_chunk_ids"])
    for cid in q.gold_chunk_ids:
        c = chunks[cid]
        print(f"\n  GOLD [{'HIT ' if cid in got else 'MISS'}] {cid} | {c['title'][:55]} | {c['section']}")
        print(textwrap.indent(textwrap.fill(c["text"][:450], 96), "     "))
    print("\n  RETRIEVED:", [(cid.split('::')[0][-8:], chunks[cid]["section"][:12]) for cid in r["retrieved_chunk_ids"]])
