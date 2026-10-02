"""Generate CANDIDATE questions. Review them before use (review_questions.py).
Example: python scripts/gen_questions.py --split test --per-type 30"""
import argparse, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from tqdm import tqdm
from atlasrag.config import load_config, resolve
from atlasrag.llm import LLMClient
from atlasrag.retrieval.index import Index
from atlasrag.bench.generate import Generator, load_meta
from atlasrag.bench.schema import QTYPES, load_questions, save_questions

ap = argparse.ArgumentParser()
ap.add_argument("--split", choices=["test", "train"], default="test")
ap.add_argument("--per-type", type=int, default=30, help="target candidates per question type")
ap.add_argument("--types", nargs="*", default=list(QTYPES))
ap.add_argument("--attempts", type=int, default=4, help="attempts per target (many pairs yield NONE)")
ap.add_argument("--model", help="override generation model (70B is better but has a small daily quota)")
ap.add_argument("--out", default="data/bench/questions.jsonl")
ap.add_argument("--seed", type=int, default=0)
a = ap.parse_args()

cfg = load_config()
out = resolve(a.out)
existing = load_questions(out)
seen = {q.id for q in existing}
llm = LLMClient(cfg["llm"], cache_root=resolve(cfg["llm"]["cache_dir"]))
gen = Generator(Index.load(resolve(cfg["retrieval"]["index_dir"])), llm,
                load_meta(resolve(cfg["corpus"]["raw_dir"])), seed=a.seed, model=a.model)
for qt in a.types:
    got = sum(1 for q in existing if q.qtype == qt and q.split == a.split)
    tries = 0
    pbar = tqdm(total=a.per_type, initial=min(got, a.per_type), desc=f"{qt}/{a.split}")
    while got < a.per_type and tries < a.per_type * a.attempts:
        tries += 1
        q = gen.make(qt, a.split)
        if q is None or q.id in seen:
            continue
        existing.append(q); seen.add(q.id); got += 1; pbar.update(1)
        save_questions(out, existing)
    pbar.close()
    print(f"{qt}: {got}/{a.per_type} candidates after {tries} attempts")
print(f"LLM calls: {llm.stats['calls']}, tokens: {llm.stats['prompt_tokens'] + llm.stats['completion_tokens']}")
