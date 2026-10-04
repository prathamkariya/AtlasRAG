r"""OFFLINE chain-pair funnel using the project's OWN gate (assess_chain_pair). No LLM, no network.

For every paper: abstract x every other long chunk of that paper -> deterministic gate -> reason or pass.
Answers: is chain sourcing starved by the corpus, or filtered by the section/overlap gates?

  python scripts\chain_funnel.py                       # current rule
  python scripts\chain_funnel.py --compare-rules       # also show what a blacklist rule WOULD admit (diagnostic only)
  python scripts\chain_funnel.py --section-labels sections_labeled.csv   # use your hand labels (is_evidence y/n/maybe)
"""
import argparse, collections, csv, json, re, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from atlasrag.bench.generate_v2 import assess_chain_pair, scientific_signals
from atlasrag.bench.schema import paper_split

ap = argparse.ArgumentParser()
ap.add_argument("--chunks", default=None)
ap.add_argument("--compare-rules", action="store_true")
ap.add_argument("--section-labels", help="CSV from repo_audit --dump-sections with is_evidence filled (y/n/maybe)")
ap.add_argument("--min-chars", type=int, default=500)
a = ap.parse_args()

path = Path(a.chunks) if a.chunks else next(p for p in (ROOT / "data/index/chunks.jsonl", ROOT / "data/processed/chunks.jsonl") if p.exists())
chunks = [json.loads(l) for l in open(path, encoding="utf-8") if l.strip()]
by_paper = collections.defaultdict(list)
for c in chunks:
    by_paper[c["paper_id"]].append(c)

NON_EVIDENCE = re.compile(r"^(abstract|front matter|introduction|background|outlook|summary|conclusions?|"
                          r"acknowledg|appendix|references|bibliography|related work|motivation)", re.I)
RESTATE = re.compile(r"conclusion|summary|outlook", re.I)


def run(section_override=None):
    reasons, passes = collections.Counter(), []
    for pid, cs in by_paper.items():
        absr = next((c for c in cs if c["section"] == "Abstract"), None)
        if absr is None:
            reasons["no_abstract"] += 1
            continue
        for c in cs:
            if c is absr or len(c["text"]) < a.min_chars:
                continue
            sec = section_override(c["section"]) if section_override else c["section"]
            r = assess_chain_pair(absr["text"], c["text"], same_paper=True, section=sec)
            if r.reason:
                reasons[r.reason] += 1
            else:
                passes.append((pid, c["section"], len(r.shared_signals)))
    return reasons, passes


def show(title, reasons, passes):
    n_eval = sum(reasons.values()) + len(passes)
    print(f"\n=== {title}")
    print(f"pairs evaluated: {n_eval}   PASS: {len(passes)}   papers with >=1 pass: {len({p for p, _, _ in passes})}/{len(by_paper)}")
    for r, n in reasons.most_common():
        print(f"   rejected {n:5}  {r}")
    sec = collections.Counter(s for _, s, _ in passes)
    rs = sum(n for s, n in sec.items() if RESTATE.search(s))
    print(f"   passes from restating sections (conclusion/summary/outlook): {rs} of {len(passes)} ({100 * rs / max(1, len(passes)):.0f}%)")
    print("   top pass sections:", sec.most_common(8))
    per = collections.Counter(p for p, _, _ in passes)
    print("   passes per paper (min/median/max):", min(per.values(), default=0), sorted(per.values())[len(per) // 2] if per else 0, max(per.values(), default=0))
    for split in ("test", "train"):
        n = sum(1 for p, _, _ in passes if paper_split(p) == split)
        print(f"   {split}-split passes: {n} (papers in split: {sum(1 for p in by_paper if paper_split(p) == split)})")


reasons, passes = run()
show("CURRENT gate (EVIDENCE_SECT whitelist)", reasons, passes)

if a.compare_rules:
    PASS, FAIL = "Results", "Introduction"          # strings EVIDENCE_SECT does / does not match
    r2, p2 = run(lambda s: FAIL if RESTATE.search(s) else s)
    show("TIGHTEN only: current whitelist, but reject restating sections (conclusion/summary/outlook)", r2, p2)
    NON_EVID_NO_CONC = re.compile(r"^(abstract|front matter|introduction|background|acknowledg|appendix|references|bibliography|related work|motivation)", re.I)
    r3, p3 = run(lambda s: PASS if (not NON_EVID_NO_CONC.match(s) and not RESTATE.search(s)) else FAIL)
    show("BLACKLIST (diagnostic only): admit anything not obviously non-evidence, still reject conclusions", r3, p3)

if a.section_labels:
    lab = {}
    with open(a.section_labels, encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            v = (row.get("is_evidence (fill y/n/maybe)") or "").strip().lower()
            if v in ("y", "n", "maybe"):
                lab[row["section"]] = v
    r4, p4 = run(lambda s: "Results" if lab.get(s) == "y" else "Introduction")
    show(f"YOUR HAND LABELS (y only; {len(lab)} sections labelled)", r4, p4)
