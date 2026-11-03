"""Run one experiment over the accepted benchmark questions.
  python scripts/run_experiment.py --group run1 --exp B
  python scripts/run_experiment.py --group run1 --exp D --escalate 0.7 --retrieval-only
Experiments: A vanilla, B static, C llm-router, D compass, E oracle, H heuristic (dev only)."""
import argparse
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from tqdm import tqdm
from atlasrag.config import load_config, resolve
from atlasrag.factory import build_pipeline
from atlasrag.tracking import init_run
from atlasrag.bench.experiments import CODES, NAMES, make_router
from atlasrag.bench.runner import run_experiment, file_hash
from atlasrag.bench.schema import load_questions
from atlasrag.bench.provenance import (
    BenchmarkHashMismatch,
    BenchmarkManifestMissing,
    BenchmarkProvenanceError,
    load_oracle_labels,
    questions_sha256,
    verify_benchmark,
)

ap = argparse.ArgumentParser()
ap.add_argument("--group", required=True, help="results/<group>/ ; use a new group (and cache namespace) for reruns")
ap.add_argument("--exp", required=True, choices=sorted(CODES))
ap.add_argument("--file", default="data/bench/final/atlasrag-bench-v3/questions_final.jsonl")
ap.add_argument("--split", default="test")
ap.add_argument("--retrieval-only", action="store_true")
ap.add_argument("--escalate", type=float)
ap.add_argument("--limit", type=int)
ap.add_argument("--wandb", action="store_true")
ap.add_argument("--oracle-labels", help="JSON sidecar {labels: {question_id: label}} for --exp E only")
ap.add_argument("--allow-unmanifested", action="store_true", help="development only: permit an absent manifest")
ap.add_argument("--allow-hash-mismatch", action="store_true", help="development only: permit a valid manifest hash mismatch")
a = ap.parse_args()

qpath = resolve(a.file)
# Guard before config, index, LLM, or pipeline loading. Only the two named,
# narrow development overrides are permitted; malformed inputs still fail closed.
hash_check, bench_id = "ok", None
try:
    provenance = verify_benchmark(qpath)
    bench_id, q_sha = provenance["benchmark_id"], provenance["questions_sha256"]
except BenchmarkManifestMissing as exc:
    if not a.allow_unmanifested:
        sys.exit(f"ABORT: {exc}. Pass --allow-unmanifested for development files only.")
    hash_check, q_sha = "unmanifested", questions_sha256(qpath)
except BenchmarkHashMismatch as exc:
    if not a.allow_hash_mismatch:
        sys.exit(f"ABORT: {exc}")
    hash_check, q_sha = "mismatch_overridden", questions_sha256(qpath)
except BenchmarkProvenanceError as exc:
    sys.exit(f"ABORT: {exc}")

all_questions = load_questions(qpath)
qs = [q for q in all_questions if q.status == "accepted" and q.split == a.split]
if a.oracle_labels and a.exp != "E":
    sys.exit("ABORT: --oracle-labels is valid only with --exp E")
oracle_labels = None
if a.oracle_labels:
    try:
        oracle_labels = load_oracle_labels(resolve(a.oracle_labels), [q.id for q in all_questions])
    except BenchmarkProvenanceError as exc:
        sys.exit(f"ABORT: {exc}")
if a.exp == "E" and oracle_labels is None:
    qs = [q for q in qs if q.gold_route]
elif a.exp == "E2":
    qs = [q for q in qs if q.gold_route_v2]
if a.limit:
    qs = qs[: a.limit]
if not qs:
    sys.exit("no accepted questions (run gen_questions -> review_questions -> label_oracle first)")

cfg = load_config()
pipe, llm = build_pipeline(cfg)
router = make_router(a.exp, cfg, llm, qs, a.escalate, oracle_labels)
name = NAMES[a.exp] + (f"_esc{a.escalate}" if a.escalate is not None else "")
run = init_run(cfg, f"{a.group}/{name}") if a.wandb else None
meta = {"group": a.group, "experiment": name, "llm_model": cfg["llm"]["model"],
        "cache_namespace": cfg["llm"]["cache_namespace"], "questions_hash": file_hash(qpath),
        "strategies": cfg["strategies"], "escalation": a.escalate,
        "questions_sha256": q_sha, "benchmark_id": bench_id, "hash_check": hash_check,
        "oracle_labels": a.oracle_labels}
print(run_experiment(pipe, router, qs, resolve("results") / a.group / f"{name}.jsonl",
                     a.retrieval_only, meta, run, progress=lambda x: tqdm(x, desc=name)))
print("LLM stats:", llm.stats)
