"""Stratified report. Compare a rerun with --compare to check ranking stability."""
import argparse, json, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from atlasrag.config import resolve
from atlasrag.bench.report import build_rows, to_markdown, compare_groups, paired_vs, paired_markdown
from atlasrag.bench.schema import load_questions

ap = argparse.ArgumentParser()
ap.add_argument("--group", required=True)
ap.add_argument("--compare", help="a second group (rerun) for the stability check")
ap.add_argument("--paired-ref", help="experiment prefix to compare everything against, e.g. B")
ap.add_argument("--file", default="data/bench/questions.jsonl")
a = ap.parse_args()

qs = load_questions(resolve(a.file), status="accepted")
gdir = resolve("results") / a.group
md = to_markdown(build_rows(gdir, qs))
(gdir / "report.md").write_text(md, encoding="utf-8")
print(md)
if a.paired_ref:
    print(f"\nPAIRED vs {a.paired_ref}:\n" + paired_markdown(paired_vs(gdir, a.paired_ref, questions=qs)))
if a.compare:
    print("\nSTABILITY:", json.dumps(compare_groups(gdir, resolve("results") / a.compare), indent=2))
