"""Run one experiment over the accepted benchmark questions.
  python scripts/run_experiment.py --group run1 --exp B
  python scripts/run_experiment.py --group run1 --exp D --escalate 0.7 --retrieval-only
Experiments: A vanilla, B static, C llm-router, D compass, E oracle, H heuristic (dev only)."""
import argparse, sys
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

ap = argparse.ArgumentParser()
ap.add_argument("--group", required=True, help="results/<group>/ ; use a new group (and cache namespace) for reruns")
ap.add_argument("--exp", required=True, choices=sorted(CODES))
ap.add_argument("--file", default="data/bench/questions.jsonl")
ap.add_argument("--split", default="test")
ap.add_argument("--retrieval-only", action="store_true")
ap.add_argument("--escalate", type=float)
ap.add_argument("--limit", type=int)
ap.add_argument("--wandb", action="store_true")
a = ap.parse_args()

cfg = load_config()
qpath = resolve(a.file)
qs = load_questions(qpath, status="accepted", split=a.split)
if a.exp in ("E", "E2"):
    _key = "gold_route" if a.exp == "E" else "gold_route_v2"
    qs = [q for q in qs if getattr(q, _key)]
if a.limit:
    qs = qs[: a.limit]
if not qs:
    sys.exit("no accepted questions (run gen_questions -> review_questions -> label_oracle first)")

pipe, llm = build_pipeline(cfg)
router = make_router(a.exp, cfg, llm, qs, a.escalate)
name = NAMES[a.exp] + (f"_esc{a.escalate}" if a.escalate is not None else "")
run = init_run(cfg, f"{a.group}/{name}") if a.wandb else None
meta = {"group": a.group, "experiment": name, "llm_model": cfg["llm"]["model"],
        "cache_namespace": cfg["llm"]["cache_namespace"], "questions_hash": file_hash(qpath),
        "strategies": cfg["strategies"], "escalation": a.escalate}
print(run_experiment(pipe, router, qs, resolve("results") / a.group / f"{name}.jsonl",
                     a.retrieval_only, meta, run, progress=lambda x: tqdm(x, desc=name)))
print("LLM stats:", llm.stats)
