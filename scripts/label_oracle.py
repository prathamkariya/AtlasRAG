"""Derive oracle routes (retrieval-only; uses LLM only for MULTI_HOP/UNCERTAIN decomposition).
test split  -> labels for Experiment E.   train split -> Compass training labels (Week 3)."""
import argparse, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from tqdm import tqdm
from atlasrag.config import load_config, resolve
from atlasrag.factory import build_pipeline
from atlasrag.bench.oracle import derive_oracle
from atlasrag.bench.schema import load_questions, save_questions

ap = argparse.ArgumentParser()
ap.add_argument("--file", default="data/bench/questions.jsonl")
ap.add_argument("--split", default="test")
ap.add_argument("--status", default="accepted", help="use 'candidate' for the train split")
ap.add_argument("--min-recall", type=float, default=1.0)
a = ap.parse_args()

cfg = load_config()
pipe, llm = build_pipeline(cfg)
path = resolve(a.file)
allq = load_questions(path)
sel = [q for q in allq if q.split == a.split and q.status == a.status]
print(derive_oracle(pipe, sel, a.min_recall, progress=lambda x: tqdm(x, desc="oracle")))
save_questions(path, allq)
