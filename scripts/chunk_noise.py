r"""How noisy are the parsed chunks? Offline.
  python scripts\chunk_noise.py --chunks data\processed_v2\chunks.jsonl
  python scripts\chunk_noise.py --chunks data\processed_v2\chunks.jsonl --questions data\bench\questions.jsonl   # noise under GOLD passages"""
import argparse, json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from atlasrag.bench.chunk_noise import numeric_fraction

ap = argparse.ArgumentParser()
ap.add_argument("--chunks", required=True)
ap.add_argument("--questions")
ap.add_argument("--threshold", type=float, default=0.25)
a = ap.parse_args()
ch = [json.loads(l) for l in open(a.chunks, encoding="utf-8") if l.strip()]
long_ = [c for c in ch if len(c["text"]) >= 500]
fr = {c["chunk_id"]: numeric_fraction(c["text"]) for c in long_}
bad = [c for c in long_ if fr[c["chunk_id"]] >= a.threshold]
print(f"{len(long_)} long chunks; {len(bad)} ({100 * len(bad) / max(1, len(long_)):.1f}%) have >= {int(a.threshold * 100)}% purely-numeric tokens")
for c in sorted(bad, key=lambda c: -fr[c["chunk_id"]])[:5]:
    print(f"   {fr[c['chunk_id']]:.2f} {c['chunk_id']} [{c['section'][:24]}] {c['text'][:70]!r}")
if a.questions:
    qs = [json.loads(l) for l in open(a.questions, encoding="utf-8") if l.strip()]
    hits = [(q["id"], q["qtype"], round(max(fr.get(g, numeric_fraction(next((c["text"] for c in ch if c["chunk_id"] == g), ""))) for g in q["gold_chunk_ids"]), 2))
            for q in qs if q.get("status") == "accepted"]
    print("accepted questions with a noisy gold passage:", [h for h in hits if h[2] >= a.threshold] or "none")
