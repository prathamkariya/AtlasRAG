"""Compare an adaptive router run with the oracle (E) and always-strongest (F) on the same questions.
  python scripts/route_diagnostics.py --group run1 --router C_llm_router"""
import argparse, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from atlasrag.config import resolve
from atlasrag.bench.schema import load_questions
from atlasrag.bench.report import load_jsonl
from atlasrag.bench.diagnostics import diagnose, to_markdown

ap = argparse.ArgumentParser()
ap.add_argument("--group", required=True); ap.add_argument("--router", required=True)
ap.add_argument("--oracle", default="E_oracle"); ap.add_argument("--strong", default="F_always_uncertain")
ap.add_argument("--file", default="data/bench/questions.jsonl")
a = ap.parse_args()
g = resolve("results") / a.group
rows = lambda name: load_jsonl(g / f"{name}.jsonl")
print(to_markdown(diagnose(rows(a.router), rows(a.oracle), rows(a.strong),
                           load_questions(resolve(a.file), status="accepted"))))
