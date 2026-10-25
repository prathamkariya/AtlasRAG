r"""Refresh benchmark_manifest.json questions_sha256 after oracle labeling.

Preserves the original source_file, candidate_source_sha256, rejection reasons,
model provenance, and paper shares while updating the final questions hash.

Usage:
    python scripts/refresh_benchmark_manifest.py --dir data/bench/final/atlasrag-bench-v3
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from atlasrag.bench.finalize import git_commit, sha_text_bytes
from atlasrag.config import resolve


def main():
    ap = argparse.ArgumentParser(description="Refresh benchmark manifest hash after oracle labeling")
    ap.add_argument("--dir", default="data/bench/final/atlasrag-bench-v3", help="Directory containing questions_final.jsonl and benchmark_manifest.json")
    args = ap.parse_args()

    bench_dir = resolve(args.dir)
    q_path = bench_dir / "questions_final.jsonl"
    m_path = bench_dir / "benchmark_manifest.json"

    if not q_path.exists():
        sys.exit(f"Error: {q_path} does not exist")
    if not m_path.exists():
        sys.exit(f"Error: {m_path} does not exist")

    manifest = json.loads(m_path.read_text(encoding="utf-8"))
    new_hash = sha_text_bytes(q_path.read_bytes())
    old_hash = manifest.get("questions_sha256")

    manifest["questions_sha256"] = new_hash
    manifest["git_commit"] = git_commit()

    m_path.write_text(json.dumps(manifest, indent=1) + "\n", encoding="utf-8")
    print(f"Updated {m_path}:")
    print(f"  questions_sha256: {old_hash} -> {new_hash}")
    print(f"  git_commit: {manifest['git_commit']}")


if __name__ == "__main__":
    main()
