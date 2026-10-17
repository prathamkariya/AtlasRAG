r"""Summarize a generation pilot: survival per type, provider tokens per surviving question, top rejection reasons.
  python scripts\pilot_yield.py data\bench\questions_v3_p1.runs.jsonl"""
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import json as _json
from atlasrag.bench.pilot_yield import load_last_run, summarize_run, summarize_pilot

import argparse
ap = argparse.ArgumentParser()
ap.add_argument("runs", help="the <out>.runs.jsonl written by gen_questions_v2.py")
ap.add_argument("--questions", help="the candidates file (default: the runs path without .runs)")
a = ap.parse_args()
runs_path = Path(a.runs)
qpath = Path(a.questions) if a.questions else runs_path.with_name(runs_path.name.replace(".runs.jsonl", ".jsonl"))
runs = [_json.loads(l) for l in open(runs_path, encoding="utf-8") if l.strip()]
questions = [_json.loads(l) for l in open(qpath, encoding="utf-8") if l.strip()] if qpath.exists() else []
whole = summarize_pilot(runs, questions)
print("WHOLE PILOT (all runs; the numbers to use)")
print(json.dumps(whole, indent=1))
print(f"\nsaved per type: {whole['saved_per_type']}   tokens per saved candidate: {whole['tokens_per_saved_candidate']}   "
      f"runs: {whole['runs']} (stopped by rate limit: {whole['runs_stopped_by_rate_limit']})")
if whole["saved_without_judge_model"]:
    print(f"WARNING: {whole['saved_without_judge_model']} saved candidate(s) have no judge_model in their provenance "
          "(generated before the provenance fix); finalize_benchmark would reject them.")
if whole["runs"] > 1:
    print("NOTE: per-run attempt counts below include cached replays after a resume; do not read them as survival rates.")
print("\nLAST RUN ONLY")
s_last = summarize_run(load_last_run(runs_path))
print(json.dumps(s_last, indent=1))
