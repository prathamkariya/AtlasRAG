"""Candidate generation WITH automatic support audit. Writes a NEW file (benchmark v2), leaving v1 untouched.
  python scripts/gen_questions_v2.py --split test --per-type 20 --types simple multi_hop chain"""
import argparse, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from tqdm import tqdm
from atlasrag.config import load_config, resolve
from atlasrag.llm import LLMClient
from atlasrag.retrieval.index import Index
from atlasrag.bench.generate import load_meta
from atlasrag.bench.generate_v2 import ValidatedGenerator
from atlasrag.bench.schema import QTYPES, load_questions, save_questions

ap = argparse.ArgumentParser()
ap.add_argument("--split", choices=["test", "train"], default="test")
ap.add_argument("--per-type", type=int, default=20)
ap.add_argument("--types", nargs="*", default=["simple", "multi_hop", "chain"])
ap.add_argument("--attempts", type=int, default=6)
ap.add_argument("--model"); ap.add_argument("--seed", type=int, default=1)
ap.add_argument("--out", default="data/bench/questions_v2.jsonl")
a = ap.parse_args()

cfg = load_config(); out = resolve(a.out)
existing = load_questions(out); seen = {q.id for q in existing}
llm = LLMClient(cfg["llm"], cache_root=resolve(cfg["llm"]["cache_dir"]))
gen = ValidatedGenerator(Index.load(resolve(cfg["retrieval"]["index_dir"])), llm,
                         load_meta(resolve(cfg["corpus"]["raw_dir"])), seed=a.seed, model=a.model)
for qt in a.types:
    got = sum(1 for q in existing if q.qtype == qt and q.split == a.split)
    tries = 0
    while got < a.per_type and tries < a.per_type * a.attempts:
        tries += 1
        rate_limits_before = gen.vstats["rate_limited"]
        q = gen.make(qt, a.split)
        if gen.vstats["rate_limited"] > rate_limits_before:
            print(f"{qt}: rate limited; stopping this type. Rerun later to resume from {out}.")
            break
        if q is None or q.id in seen:
            continue
        existing.append(q); seen.add(q.id); got += 1
        save_questions(out, existing)
    print(f"{qt}: {got}/{a.per_type} survived audit after {tries} attempts")
print("audit outcomes:", dict(gen.vstats))
print(f"LLM calls: {llm.stats['calls']}, tokens: {llm.stats['prompt_tokens'] + llm.stats['completion_tokens']}")
print("temporal/conflicting are off by default: fix the pairing first (docs), then add them with --types")
