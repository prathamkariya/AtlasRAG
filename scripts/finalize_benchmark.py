r"""Turn reviewed candidates into the FINAL benchmark (the only file experiments should use).
  python scripts\finalize_benchmark.py --file data\bench\questions_v3.jsonl --stability data\bench\v3\audit_stability.json `
      --benchmark-id atlas-bench-v2 --min-per-type "simple=15,multi_hop=15,temporal=10,chain=10" --strict
Writes data\bench\final\<benchmark-id>\questions_final.jsonl and benchmark_manifest.json.
Exit code 3 with --strict if any type is below its minimum (the files are still written so you can inspect them)."""
import argparse, json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from atlasrag.config import resolve
from atlasrag.bench.schema import load_questions, save_questions
from atlasrag.bench.finalize import (finalize, build_manifest, parse_minimums, check_minimums, sha_text_bytes, git_commit)

ap = argparse.ArgumentParser()
ap.add_argument("--file", required=True); ap.add_argument("--stability", required=True)
ap.add_argument("--benchmark-id", required=True)
ap.add_argument("--require-runs", type=int, default=3, help="judge runs per question (e.g. generation-time audit + 2 fresh repetitions)")
ap.add_argument("--allow-llm-assisted", action="store_true", help="NOT recommended: accept review:llm_assisted decisions")
ap.add_argument("--min-per-type", default="", help='e.g. "simple=15,multi_hop=15"')
ap.add_argument("--strict", action="store_true")
ap.add_argument("--corpus-manifest", default="corpus/manifests/atlasrag-corpus-v2.json")
ap.add_argument("--out-dir", default="data/bench/final")
a = ap.parse_args()

qs = load_questions(resolve(a.file))
stab = json.loads(resolve(a.stability).read_text(encoding="utf-8"))["per_question"]
final, rejected = finalize(qs, stab, a.require_runs, not a.allow_llm_assisted)
out = resolve(a.out_dir) / a.benchmark_id
out.mkdir(parents=True, exist_ok=True)
save_questions(out / "questions_final.jsonl", final)
cm = resolve(a.corpus_manifest)
man = build_manifest(a.benchmark_id, final, rejected, sha_text_bytes((out / "questions_final.jsonl").read_bytes()),
                     sha_text_bytes(cm.read_bytes()) if cm.exists() else None, a.require_runs, a.file, git_commit())
(out / "benchmark_manifest.json").write_text(json.dumps(man, indent=1), encoding="utf-8")

print(f"{len(qs)} questions in -> {man['n_questions']} FINAL, {man['rejected_total']} rejected")
print("rejected by reason:", man["rejected_by_reason"])
print("final by type:", man["by_type"], "| papers:", man["n_distinct_papers"], "| max paper share:", man["max_paper_share"])
print("review modes:", man["review_modes"], "| generator:", man["generator_models"], "| judge:", man["judge_models"])
if man["same_model_generated_and_judged"]:
    print("WARNING: the same model generated and judged some final questions (self-agreement bias)")
bad = check_minimums(man["by_type"], parse_minimums(a.min_per_type))
print("below minimum:", bad or "none")
print("wrote", out / "questions_final.jsonl", "and benchmark_manifest.json")
sys.exit(3 if (bad and a.strict) else 0)
