"""Candidate generation WITH automatic support audit. Writes a NEW file (benchmark v2), leaving v1 untouched.
  python scripts/gen_questions_v2.py --split test --per-type 20 --types simple multi_hop chain

Every run appends ONE JSON line to <out>.runs.jsonl (also on abort/rate limit): args, per-type
progress, rejection reasons, per-type attempt/survivor funnel and full LLM counters (provider calls,
cache misses, rate-limit errors, provider tokens). Exit code 2 = stopped by a rate limit; rerun later to resume."""
import argparse, json, subprocess, sys, time
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
ap.add_argument("--summary", help="run-summary JSONL (default: <out>.runs.jsonl)")
a = ap.parse_args()


def git_commit():
    try:
        return subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], stderr=subprocess.DEVNULL).decode().strip()
    except Exception:
        return "unknown"


cfg = load_config(); out = resolve(a.out)
summary_path = Path(a.summary) if a.summary else out.with_suffix(".runs.jsonl")
existing = load_questions(out); seen = {q.id for q in existing}
llm = LLMClient(cfg["llm"], cache_root=resolve(cfg["llm"]["cache_dir"]))
gen = ValidatedGenerator(Index.load(resolve(cfg["retrieval"]["index_dir"])), llm,
                         load_meta(resolve(cfg["corpus"]["raw_dir"])), seed=a.seed, model=a.model)

per_type, stopped, t0, error = {}, None, time.time(), None
try:
    for qt in a.types:
        got = sum(1 for q in existing if q.qtype == qt and q.split == a.split)
        tries = 0
        while got < a.per_type and tries < a.per_type * a.attempts:
            tries += 1
            rate_limits_before = gen.vstats["rate_limited"]
            q = gen.make(qt, a.split)
            if gen.vstats["rate_limited"] > rate_limits_before:
                stopped = {"type": qt, "reason": "rate_limited"}
                print(f"{qt}: rate limited; stopping the run (later types would hit the same limit). "
                      f"Rerun later to resume from {out}.")
                break
            if q is None or q.id in seen:
                continue
            existing.append(q); seen.add(q.id); got += 1
            save_questions(out, existing)
        per_type[qt] = {"got": got, "target": a.per_type, "tries": tries}
        print(f"{qt}: {got}/{a.per_type} survived audit after {tries} attempts")
        if stopped:
            break
except BaseException as e:                     # still record what happened (Ctrl-C, bugs)
    error = f"{type(e).__name__}: {e}"
    raise
finally:
    record = {"finished": time.strftime("%Y-%m-%dT%H:%M:%S"), "elapsed_s": round(time.time() - t0, 1),
              "git_commit": git_commit(), "model": a.model or cfg["llm"]["model"], "args": vars(a),
              "per_type": per_type, "stopped": stopped, "error": error,
              "outcomes": dict(gen.vstats), "llm": dict(llm.stats)}
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    with open(summary_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")

print("audit outcomes:", dict(gen.vstats))
print("LLM:", {k: v for k, v in llm.stats.items() if v})
print(f"run summary appended to {summary_path}")
print("temporal/conflicting are off by default: fix the pairing first (docs), then add them with --types")
if stopped:
    sys.exit(2)
