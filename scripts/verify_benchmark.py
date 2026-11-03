"""Exit 0 only when a final benchmark matches its pinned manifest.

Usage: python scripts/verify_benchmark.py [--dir data/bench/final/atlasrag-bench-v3]
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from atlasrag.bench.provenance import BenchmarkProvenanceError, verify_benchmark  # noqa: E402


parser = argparse.ArgumentParser()
parser.add_argument("--dir", default="data/bench/final/atlasrag-bench-v3")
args = parser.parse_args()
directory = Path(args.dir)
directory = directory if directory.is_absolute() else ROOT / directory
try:
    info = verify_benchmark(directory / "questions_final.jsonl")
except BenchmarkProvenanceError as exc:
    sys.exit(f"FAIL: {exc}")
print(f"OK: {info['benchmark_id']} sha256={info['questions_sha256'][:12]}")
