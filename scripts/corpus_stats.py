r"""Is the corpus big and varied enough for the benchmark you want? Offline, no LLM.
  python scripts\corpus_stats.py                         # uses the active config (set ATLAS_CONFIG for corpus_v2)
Checks: how many papers, over what time span, how many land in the TEST split (the benchmark can only draw
questions from test papers), and chunk counts."""
import collections, json, sys
from datetime import date
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from atlasrag.config import load_config, resolve
from atlasrag.bench.schema import paper_split

cfg = load_config()
raw = resolve(cfg["corpus"]["raw_dir"]) / "metadata.jsonl"
if not raw.exists():
    sys.exit(f"no metadata at {raw}: run fetch first")
meta = [json.loads(l) for l in open(raw, encoding="utf-8") if l.strip()]
d = lambda r: date.fromisoformat(str(r["published"])[:10])
dates = sorted(d(r) for r in meta)
span = (dates[-1] - dates[0]).days
print(f"config corpus: {cfg['corpus']['raw_dir']}")
print(f"papers: {len(meta)}   published {dates[0]} -> {dates[-1]}  (span {span} days = {span / 30.4:.1f} months)")
by_year = collections.Counter(x.year for x in dates)
print("by year:", dict(sorted(by_year.items())))
split = collections.Counter(paper_split(r["id"]) for r in meta)
print(f"paper-level split: test {split['test']}  train {split['train']}   <- questions for the benchmark can ONLY come from the test papers")
test_years = collections.Counter(d(r).year for r in meta if paper_split(r["id"]) == "test")
print("test papers by year:", dict(sorted(test_years.items())))

ch = resolve(cfg["corpus"]["processed_dir"]) / "chunks.jsonl"
if ch.exists():
    chunks = [json.loads(l) for l in open(ch, encoding="utf-8") if l.strip()]
    long_ = [c for c in chunks if len(c["text"]) >= 500]
    print(f"chunks: {len(chunks)} total, {len(long_)} long (>=500 chars); long chunks in test split: "
          f"{sum(1 for c in long_ if paper_split(c['paper_id']) == 'test')}")
    secs = collections.Counter(c["section"] for c in long_)
    print("top sections:", secs.most_common(6))
else:
    print("chunks: not built yet (run build_index)")

warn = []
if split["test"] < 25: warn.append(f"only {split['test']} test papers (want >= 25: question diversity and paper-level CIs depend on it)")
if span < 365: warn.append(f"time span {span} days: 'temporal' questions need an earlier and a later study, so span a few years")
if by_year and max(by_year.values()) > 0.6 * len(meta): warn.append("more than 60% of papers are from one year")
print("\nWARNINGS:" if warn else "\nno warnings", *[f"\n - {w}" for w in warn])
