"""Oracle v2 labels (cheapest strategy achieving the best recall). Stores all ladder recalls.
  python scripts/label_oracle_v2.py --split test --status accepted
  python scripts/label_oracle_v2.py --file data/bench/questions.jsonl --split train --status candidate"""
import argparse, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from tqdm import tqdm
from atlasrag.config import load_config, resolve
from atlasrag.factory import build_pipeline
from atlasrag.bench.oracle_v2 import derive_oracle_v2
from atlasrag.bench.schema import load_questions, save_questions

ap = argparse.ArgumentParser()
ap.add_argument("--file", default="data/bench/questions.jsonl")
ap.add_argument("--split", default="test"); ap.add_argument("--status", default="accepted")
a = ap.parse_args()
cfg = load_config(); pipe, _ = build_pipeline(cfg)
path = resolve(a.file); allq = load_questions(path)
sel = [q for q in allq if q.split == a.split and q.status == a.status]
print(derive_oracle_v2(pipe, sel, progress=lambda x: tqdm(x, desc="oracle v2")))
save_questions(path, allq)
