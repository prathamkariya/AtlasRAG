"""Look at label distributions BEFORE training Compass.
  python scripts/label_stats.py --split train --status candidate"""
import argparse, sys
from collections import Counter
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from atlasrag.config import resolve
from atlasrag.bench.schema import load_questions

ap = argparse.ArgumentParser()
ap.add_argument("--file", default="data/bench/questions.jsonl")
ap.add_argument("--split", default="train"); ap.add_argument("--status")
a = ap.parse_args()
qs = load_questions(resolve(a.file), status=a.status, split=a.split)
n = len(qs)
print(f"{n} questions (split={a.split}, status={a.status or 'any'})")
for name, key in [("v1 label", lambda q: q.gold_route), ("v2 label", lambda q: q.gold_route_v2)]:
    c = Counter(key(q) for q in qs)
    print(f"{name:9}", dict(c))
print("retrievable (recall 1.0 reachable):", sum(bool(q.oracle_sufficient) for q in qs), "| insufficient:", sum(q.oracle_sufficient is False for q in qs))
print("by qtype:", dict(Counter(q.qtype for q in qs)))
warn = []
v2 = Counter(q.gold_route_v2 for q in qs if q.gold_route_v2)
if sum(v2.values()) < 150: warn.append(f"only {sum(v2.values())} labelled questions; LoRA on <~150 will memorise")
for lab, k in v2.items():
    if k < 0.10 * max(1, sum(v2.values())): warn.append(f"class {lab} is {k} examples (<10%)")
if sum(q.oracle_sufficient is False for q in qs) > 0.25 * max(1, n): warn.append(">25% insufficient: fix retrieval/benchmark before learning a router from it")
print("\nWARNINGS:" if warn else "\nno warnings", *[f"\n - {w}" for w in warn])
