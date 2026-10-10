"""Judge-stability audit. Reruns the support audit N times (fresh LLM calls each time) and compares with the
verdicts you already have. Resumable; stops cleanly on a rate limit.

  python scripts\audit_stability.py --reps 2 --wait-on-rate-limit              # non-simple questions only (cheaper)
  python scripts\audit_stability.py --reps 2 --all --wait-on-rate-limit        # also the 17 simple ones

Existing verdicts included in the comparison: data\bench\audit.jsonl and data\bench\v2_review_manifest.json.
Output: data\bench\audit_stability.json (per-question classes). Quota: about 10 judge calls per repetition
(27 with --all), roughly 1.6K tokens each, and a free tier allows only a few per minute: expect minutes, not seconds."""
import argparse, json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from tqdm import tqdm
from atlasrag.config import load_config, resolve
from atlasrag.llm import LLMClient
from atlasrag.bench.schema import load_questions
from atlasrag.bench.audit_stability import run_stability, collect, summarize, write_report

ap = argparse.ArgumentParser()
ap.add_argument("--file", default="data/bench/questions.jsonl")
ap.add_argument("--status", default="accepted"); ap.add_argument("--split", default="test")
ap.add_argument("--reps", type=int, default=2)
ap.add_argument("--all", action="store_true", help="include simple questions (default: non-simple only)")
ap.add_argument("--model"); ap.add_argument("--wait-on-rate-limit", action="store_true")
ap.add_argument("--out-dir", default="data/bench")
ap.add_argument("--baseline", default="data/bench/audit.jsonl")
ap.add_argument("--manifest", default="data/bench/v2_review_manifest.json")
a = ap.parse_args()

cfg = load_config()
text_of = {}
for l in open(resolve(cfg["retrieval"]["index_dir"]) / "chunks.jsonl", encoding="utf-8"):
    c = json.loads(l); text_of[c["chunk_id"]] = c["text"]
qs = [q for q in load_questions(resolve(a.file), status=a.status, split=a.split) if a.all or q.qtype != "simple"]
print(f"{len(qs)} questions x {a.reps} fresh repetitions")


def make_llm(ns):
    c = dict(cfg["llm"]); c["cache_namespace"] = ns
    return LLMClient(c, cache_root=resolve(cfg["llm"]["cache_dir"]))


out_dir = resolve(a.out_dir)
res = run_stability(make_llm, qs, text_of, out_dir, a.reps, a.model, a.wait_on_rate_limit,
                    progress=lambda x: tqdm(x, desc="judge"))
extra = []
bp = resolve(a.baseline)
if bp.exists():
    extra.append({json.loads(l)["id"]: json.loads(l)["ok"] for l in open(bp, encoding="utf-8") if l.strip()})
mp = resolve(a.manifest)
if mp.exists():
    extra.append({r["id"]: r["audit_ok"] for r in json.load(open(mp, encoding="utf-8"))})
verdicts = collect(qs, [out_dir / f"audit_stability_r{k}.jsonl" for k in range(1, a.reps + 1)], extra)
summary = summarize(verdicts, {q.id: q.qtype for q in qs})
write_report(out_dir / "audit_stability.json", summary)

print(f"\nruns compared per question: {summary['runs']}  (new repetitions + audit.jsonl + manifest)")
print(f"questions compared: {summary['questions']} of {len(qs)}   pairwise agreement: {summary['pairwise_agreement']:.0%}")
print("classes:", summary["classes"]); print("by type:", summary["by_type"])
for qid, d in summary["per_question"].items():
    if d["class"] == "unstable":
        q = next(x for x in qs if x.id == qid)
        print(f"\nUNSTABLE {qid} [{d['type']}] verdicts={['PASS' if v else 'FAIL' for v in d['verdicts']]}\n   Q: {q.question[:160]}")
if res["stopped"]:
    print("\nSTOPPED by a rate limit:", res["stopped"], "- rerun the same command to resume; finished work is kept.")
    sys.exit(2)
print(f"\nwrote {out_dir / 'audit_stability.json'}")
