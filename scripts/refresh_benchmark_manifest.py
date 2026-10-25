r"""Refresh benchmark_manifest.json questions_sha256 after oracle labeling.

Preserves the original source_file, candidate_source_sha256, rejection reasons,
model provenance, and paper shares while updating the final questions hash.

Hardened checks:
- Aborts if questions_final.jsonl is missing, empty (0 bytes), or malformed.
- Aborts if question count or typology does not match benchmark_manifest.json.
- Verifies rejection history and preserves/populates candidate_source_sha256.

Usage:
    python scripts/refresh_benchmark_manifest.py --dir data/bench/final/atlasrag-bench-v3
"""
from __future__ import annotations

import argparse
from collections import Counter
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from atlasrag.bench.finalize import git_commit, sha_text_bytes
from atlasrag.config import resolve


def refresh_manifest(bench_dir: Path) -> dict:
    q_path = bench_dir / "questions_final.jsonl"
    m_path = bench_dir / "benchmark_manifest.json"

    if not q_path.exists():
        sys.exit(f"Error: {q_path} does not exist")
    if not m_path.exists():
        sys.exit(f"Error: {m_path} does not exist")

    # Guard 1: Non-empty file
    if q_path.stat().st_size == 0:
        sys.exit(f"ABORT: {q_path} is empty (0 bytes). Refusing to refresh manifest from an empty benchmark.")

    # Guard 2: Well-formed JSONL and required schema fields
    questions = []
    required_keys = {"id", "question", "qtype", "gold_chunk_ids", "gold_paper_ids", "split", "status"}
    for idx, line in enumerate(q_path.read_text(encoding="utf-8").splitlines(), 1):
        line = line.strip()
        if not line:
            continue
        try:
            q = json.loads(line)
        except json.JSONDecodeError as err:
            sys.exit(f"ABORT: Malformed JSON at line {idx} in {q_path}: {err}")
        if not isinstance(q, dict):
            sys.exit(f"ABORT: Line {idx} in {q_path} is not a JSON object")
        missing = required_keys - set(q.keys())
        if missing:
            sys.exit(f"ABORT: Line {idx} ({q.get('id', '?')}) missing required keys: {missing}")
        questions.append(q)

    if not questions:
        sys.exit(f"ABORT: Zero valid questions found in {q_path}")

    manifest = json.loads(m_path.read_text(encoding="utf-8"))

    # Guard 3: Count and typology consistency
    expected_n = manifest.get("n_questions")
    actual_n = len(questions)
    if expected_n is not None and expected_n != actual_n:
        sys.exit(f"ABORT: Count mismatch: {q_path} has {actual_n} questions, but manifest expected {expected_n}")

    actual_types = dict(Counter(q["qtype"] for q in questions))
    expected_types = manifest.get("by_type", {})
    if expected_types and actual_types != expected_types:
        sys.exit(f"ABORT: Type distribution mismatch: questions have {actual_types}, manifest expected {expected_types}")

    # Guard 4: Candidate source provenance and rejection history
    source_rel = manifest.get("source_file", "")
    if source_rel:
        source_path = resolve(source_rel)
        if source_path.exists():
            manifest["candidate_source_sha256"] = sha_text_bytes(source_path.read_bytes())

    if "rejected_total" not in manifest or "rejected_by_reason" not in manifest:
        sys.exit(f"ABORT: Manifest {m_path} missing rejection history (rejected_total / rejected_by_reason)")

    new_hash = sha_text_bytes(q_path.read_bytes())
    old_hash = manifest.get("questions_sha256")

    manifest["questions_sha256"] = new_hash
    manifest["git_commit"] = git_commit()

    m_path.write_text(json.dumps(manifest, indent=1) + "\n", encoding="utf-8")
    print(f"Successfully refreshed {m_path}:")
    print(f"  questions: {actual_n} ({actual_types})")
    print(f"  questions_sha256: {old_hash} -> {new_hash}")
    print(f"  candidate_source_sha256: {manifest.get('candidate_source_sha256')}")
    print(f"  rejections preserved: {manifest.get('rejected_total')} ({manifest.get('rejected_by_reason')})")
    print(f"  git_commit: {manifest['git_commit']}")
    return manifest


def main():
    ap = argparse.ArgumentParser(description="Refresh benchmark manifest hash after oracle labeling")
    ap.add_argument("--dir", default="data/bench/final/atlasrag-bench-v3", help="Directory containing questions_final.jsonl and benchmark_manifest.json")
    args = ap.parse_args()
    refresh_manifest(resolve(args.dir))


if __name__ == "__main__":
    main()
