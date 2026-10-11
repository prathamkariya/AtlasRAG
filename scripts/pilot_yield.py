r"""Summarize a generation pilot: survival per type, provider tokens per surviving question, top rejection reasons.
  python scripts\pilot_yield.py data\bench\questions_v3_p1.runs.jsonl"""
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from atlasrag.bench.pilot_yield import load_last_run, summarize_run

if len(sys.argv) != 2:
    sys.exit("usage: python scripts\\pilot_yield.py <runs.jsonl>")
s = summarize_run(load_last_run(sys.argv[1]))
print(json.dumps(s, indent=1))
print("\nper type:  " + "  |  ".join(f"{t}: {v['survived']}/{v['attempts']} survived" for t, v in s["per_type"].items()))
print(f"tokens per surviving question: {s['tokens_per_survivor']}   (a free-tier cap of 8,000 tokens/minute turns this into minutes per question)")
