"""Create a cleaned benchmark from an existing benchmark and support audit.

The source benchmark is never modified. Failed accepted items are marked
rejected in a distinct output file with the audit reasons recorded in notes.
"""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from atlasrag.bench.cleanup import reject_audit_failures
from atlasrag.bench.schema import load_questions, save_questions
from atlasrag.config import resolve


ap = argparse.ArgumentParser()
ap.add_argument("--in", dest="source", default="data/bench/questions_v2.jsonl")
ap.add_argument("--audit", default="data/bench/audit.jsonl")
ap.add_argument("--out", default="data/bench/questions_v2_clean.jsonl")
a = ap.parse_args()

source, audit, out = map(resolve, (a.source, a.audit, a.out))
if source == out:
    raise SystemExit("--out must be a new benchmark artifact, not the source file")
questions = load_questions(source)
rows = [json.loads(line) for line in open(audit, encoding="utf-8") if line.strip()]
clean, summary = reject_audit_failures(questions, rows)
save_questions(out, clean)
print(f"wrote {out}: rejected {len(summary['rejected'])} accepted questions")
for question_id in summary["rejected"]:
    print("-", question_id)
