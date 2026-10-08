r"""Read questions next to their gold passages and the judge's verdicts. This is the human step for questions the
audit cannot settle.
  python scripts\show_questions.py --unstable                 # every question the judge runs disagreed on
  python scripts\show_questions.py --ids multi_hop-a55a4306 chain-505459d1
Verdict history comes from data\bench\audit_stability.json (if present) and data\bench\audit.jsonl."""
import argparse, json, sys, textwrap
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from atlasrag.config import load_config, resolve
from atlasrag.bench.schema import load_questions

ap = argparse.ArgumentParser()
ap.add_argument("--file", default="data/bench/questions.jsonl")
ap.add_argument("--ids", nargs="*", default=[])
ap.add_argument("--unstable", action="store_true", help="show the questions classed 'unstable' in audit_stability.json")
ap.add_argument("--max-chars", type=int, default=1400)
a = ap.parse_args()

ids = list(a.ids)
stab = resolve("data/bench/audit_stability.json")
history = json.loads(stab.read_text(encoding="utf-8"))["per_question"] if stab.exists() else {}
if a.unstable:
    ids += [q for q, d in history.items() if d["class"] == "unstable"]
if not ids:
    sys.exit("nothing to show: pass --ids ... or --unstable (needs data\\bench\\audit_stability.json)")

cfg = load_config()
text_of = {}
for p in (resolve(cfg["retrieval"]["index_dir"]) / "chunks.jsonl", resolve(cfg["corpus"]["processed_dir"]) / "chunks.jsonl"):
    if p.exists():
        for l in open(p, encoding="utf-8"):
            c = json.loads(l); text_of[c["chunk_id"]] = (c["title"], c["section"], c["text"])
        break
judge = {}
ap_ = resolve("data/bench/audit.jsonl")
if ap_.exists():
    judge = {r["id"]: r for r in (json.loads(l) for l in open(ap_, encoding="utf-8") if l.strip())}
qs = {q.id: q for q in load_questions(resolve(a.file))}

for qid in dict.fromkeys(ids):
    q = qs.get(qid)
    if q is None:
        print(f"\n{qid}: not in {a.file}"); continue
    print("\n" + "=" * 100)
    h = history.get(qid)
    print(f"{qid}  [{q.qtype}]  status={q.status}  class={h['class'] if h else '-'}  verdicts={['PASS' if v else 'FAIL' for v in h['verdicts']] if h else '-'}")
    print("QUESTION :", q.question)
    print("REFERENCE:", q.reference_answer)
    j = judge.get(qid)
    if j:
        print("JUDGE    :", j.get("reasons"), "|", (j.get("verdict") or {}).get("problems", "")[:200])
    for n, cid in enumerate(q.gold_chunk_ids, 1):
        title, sec, text = text_of.get(cid, ("?", "?", "(chunk text not found)"))
        print(f"\n  --- passage {n}: {cid} | {title[:60]} | {sec}")
        print(textwrap.indent(textwrap.fill(text[:a.max_chars], 98), "      "))
    print("\n  DECIDE: (1) every passage necessary?  (2) is the reference answer fully stated in the passages?  (3) is the question answerable without them?")
