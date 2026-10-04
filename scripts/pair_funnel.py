r"""OFFLINE cross-paper pair funnel (multi_hop / temporal / conflicting) using the project's OWN gate
(assess_cross_paper_pair). No LLM, no network, no embeddings.

It enumerates EVERY cross-paper chunk pair inside a split, which is an UPPER BOUND on what the
dense+BM25 candidate pool can ever offer the generator. If the upper bound is small, no amount of
prompting or gate tuning can fix yield: the corpus/split is the limit.

  python scripts\pair_funnel.py --split test --qtype multi_hop
  python scripts\pair_funnel.py --split test --qtype temporal
  python scripts\pair_funnel.py --split all  --qtype multi_hop     # what you'd have WITHOUT the paper-level split
"""
import argparse, collections, json, sys
from itertools import combinations
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import functools
import atlasrag.bench.generate_v2 as gv2
from atlasrag.bench.generate_v2 import assess_cross_paper_pair

# Memoize the text -> signal-set extraction (pure functions; results unchanged, ~100x faster for all-pairs scans).
# Safe because the gate only builds NEW sets from them (&, -, |); it never mutates the returned sets.
gv2.scientific_signals = functools.lru_cache(maxsize=None)(gv2.scientific_signals)
gv2.specific_scientific_signals = functools.lru_cache(maxsize=None)(gv2.specific_scientific_signals)
from atlasrag.bench.schema import paper_split

ap = argparse.ArgumentParser()
ap.add_argument("--split", default="test", choices=["test", "train", "all"])
ap.add_argument("--qtype", default="multi_hop", choices=["multi_hop", "temporal", "conflicting"])
ap.add_argument("--chunks", default=None)
a = ap.parse_args()

path = Path(a.chunks) if a.chunks else next(p for p in (ROOT / "data/index/chunks.jsonl", ROOT / "data/processed/chunks.jsonl") if p.exists())
chunks = [json.loads(l) for l in open(path, encoding="utf-8") if l.strip()]
meta = {}
mp = ROOT / "data/raw/metadata.jsonl"
if mp.exists():
    meta = {r["id"]: r for r in (json.loads(l) for l in open(mp, encoding="utf-8") if l.strip())}
date = lambda pid: str(meta.get(pid, {}).get("published", ""))[:10]

pool = [c for c in chunks if len(c["text"]) >= 500 and c["section"] != "Front matter"
        and (a.split == "all" or paper_split(c["paper_id"]) == a.split)]
papers = sorted({c["paper_id"] for c in pool})
print(f"split={a.split} qtype={a.qtype}: {len(papers)} papers, {len(pool)} long chunks, "
      f"{len(papers) * (len(papers) - 1) // 2} possible paper pairs")

reasons, passing, paper_pairs = collections.Counter(), 0, collections.Counter()
for x, y in combinations(pool, 2):
    if x["paper_id"] == y["paper_id"]:
        continue
    A, B = x, y
    if a.qtype == "temporal":
        if date(A["paper_id"]) > date(B["paper_id"]):
            A, B = B, A
    r = assess_cross_paper_pair(A["text"], B["text"], qtype=a.qtype, dense_similarity=0.0,
                                date_a=date(A["paper_id"]), date_b=date(B["paper_id"]),
                                section_a=A["section"], section_b=B["section"])
    if r.reason:
        reasons[r.reason] += 1
    else:
        passing += 1
        paper_pairs[tuple(sorted((x["paper_id"], y["paper_id"])))] += 1

total = sum(reasons.values()) + passing
print(f"\ncross-paper chunk pairs evaluated: {total}")
for k, n in reasons.most_common():
    print(f"   rejected {n:7}  {k}")
print(f"   PASS     {passing:7}  ({100 * passing / max(1, total):.2f}%)")
print(f"\ndistinct PAPER PAIRS with >=1 passing chunk pair: {len(paper_pairs)} of {len(papers) * (len(papers) - 1) // 2}")
print("papers involved in at least one passing pair:", len({p for pp in paper_pairs for p in pp}), "of", len(papers))
print("top paper pairs by passing chunk pairs:", paper_pairs.most_common(5))
print("\nUPPER BOUND ONLY: the real generator ranks a dense+BM25 pool, a subset of these pairs, and the LLM, structural gates")
print("and support audit remove more. Every accepted question needs 2 papers: this is the hard ceiling on diversity.")
