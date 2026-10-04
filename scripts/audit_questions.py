"""Audit EXISTING questions against their gold evidence. Does not modify the question file.
Resumable: rerun the same command and it continues where it stopped.
  python scripts\audit_questions.py --status accepted --split test
  python scripts\audit_questions.py --status accepted --split test --wait-on-rate-limit
Free-tier note: the binding limit is usually tokens-per-MINUTE, so a full pass takes several minutes."""
import argparse, json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from tqdm import tqdm
from atlasrag.config import load_config, resolve
from atlasrag.llm import LLMClient
from atlasrag.bench.schema import load_questions
from atlasrag.bench.audit_runner import run_audit, summarize

ap = argparse.ArgumentParser()
ap.add_argument("--file", default="data/bench/questions.jsonl")
ap.add_argument("--status", default="accepted"); ap.add_argument("--split", default="test")
ap.add_argument("--model", help="judge model; a DIFFERENT model than the generator reduces self-agreement bias")
ap.add_argument("--out", default="data/bench/audit.jsonl")
ap.add_argument("--wait-on-rate-limit", action="store_true",
                help="sleep the provider-suggested time (bounded: <=6 waits/call, <=30s each) instead of stopping")
a = ap.parse_args()

cfg = load_config()
text_of = {}
for l in open(resolve(cfg["retrieval"]["index_dir"]) / "chunks.jsonl", encoding="utf-8"):
    c = json.loads(l); text_of[c["chunk_id"]] = c["text"]
llm = LLMClient(cfg["llm"], cache_root=resolve(cfg["llm"]["cache_dir"]))
qs = load_questions(resolve(a.file), status=a.status, split=a.split)
out = resolve(a.out)

res = run_audit(llm, qs, text_of, out, model=a.model, wait_on_rate_limit=a.wait_on_rate_limit,
                progress=lambda x: tqdm(x, desc="audit"))
s = summarize(out, qs)
print(f"\njudged {s['judged']}/{len(qs)} ({res['already_done']} from earlier runs, {res['new']} new)")
print(f"passed {s['passed']}/{s['judged']}; reasons: {s['reasons']}")
byid = {q.id: q for q in qs}
for r in s["flagged"]:
    q = byid[r["id"]]
    print(f"- {q.id} [{q.qtype}] {r['reasons']}\n    Q: {q.question[:150]}\n    judge: {r['verdict'].get('problems', '')}")
print("LLM stats:", llm.stats)
if res["stopped"]:
    w = res["stopped"]["suggested_wait_s"]
    print(f"\nSTOPPED by a rate limit before {res['stopped']['before_id']} "
          f"(provider suggested ~{w:.0f}s). Partial results are saved in {out}.\n"
          "Wait about a minute and rerun the SAME command to resume, or add --wait-on-rate-limit." if w is not None else
          f"\nSTOPPED by a rate limit before {res['stopped']['before_id']}. Partial results saved; rerun later.")
    sys.exit(2)
