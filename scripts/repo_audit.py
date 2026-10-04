"""READ-ONLY repo audit for the AtlasRAG handoff. Changes nothing (except with --snapshot, which writes
audit/frozen_hashes.json only). Paste the output to whoever is planning the next change.

  python scripts/repo_audit.py                     # git state, frozen-asset check, instrumentation grep, chain feasibility, pilots
  python scripts/repo_audit.py --run-tests         # also run pytest and show the tail
  python scripts/repo_audit.py --snapshot          # record sha256 of frozen assets (commit audit/frozen_hashes.json afterwards)
"""
import argparse, collections, glob, hashlib, json, os, re, subprocess, sys
from pathlib import Path

for _s in (sys.stdout, sys.stderr):          # Windows consoles/pipes default to cp1252 and crash on e.g. 'ΩΛ'
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
FROZEN = ["data/bench/questions.jsonl", "data/bench/questions_v1_frozen.jsonl",
          "src/atlasrag/bench/oracle_v2.py", "src/atlasrag/bench/experiments.py"]
FROZEN_GLOBS = ["results/run1/*"]


def sh(*cmd):
    try:
        return subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, timeout=300).stdout.strip()
    except Exception as e:
        return f"<failed: {e}>"


def sha(p):
    """Line-ending-normalized, so the SAME file hashes identically on Windows (CRLF checkout) and Linux/CI (LF)."""
    return hashlib.sha256(Path(p).read_bytes().replace(b"\r\n", b"\n")).hexdigest()[:16]


def frozen_files():
    out = [ROOT / f for f in FROZEN]
    for g in FROZEN_GLOBS:                    # report.md is DERIVED (report.py rewrites it), so it is not a frozen input
        out += [Path(p) for p in glob.glob(str(ROOT / g)) if Path(p).is_file() and Path(p).name != "report.md"]
    return out


def head(t):
    print(f"\n{'=' * 78}\n{t}\n{'=' * 78}")


ap = argparse.ArgumentParser()
ap.add_argument("--run-tests", action="store_true")
ap.add_argument("--snapshot", action="store_true")
ap.add_argument("--out", help="also write the report to this file (UTF-8). Prefer this over shell redirection on Windows.")
ap.add_argument("--dump-sections", help="write every section name with counts to this CSV so you can label evidence/non-evidence by hand")
a = ap.parse_args()


class _Tee:
    def __init__(self, *streams): self.streams = streams
    def write(self, x):
        for st in self.streams: st.write(x)
        return len(x)
    def flush(self):
        for st in self.streams: st.flush()


if a.out:
    sys.stdout = _Tee(sys.stdout, open(a.out, "w", encoding="utf-8"))

# ---- 1. git ----
head("1. GIT STATE (verify against github.com/prathamkariya/AtlasRAG)")
print("commit :", sh("git", "rev-parse", "HEAD"))
print("branch :", sh("git", "branch", "--show-current"))
print("remote :", sh("git", "remote", "-v").splitlines()[:1])
print("ahead/behind origin:", sh("git", "rev-list", "--left-right", "--count", "HEAD...@{u}") or "no upstream")
print("recent commits:\n" + sh("git", "log", "--oneline", "-n", "10"))
st = sh("git", "status", "--porcelain")
print("uncommitted changes:", "none" if not st else "\n" + st)
print("\nreported-but-possibly-unpushed files tracked by git?")
for f in ["src/atlasrag/bench/generate_v2.py", "src/atlasrag/bench/generate.py", "tests/test_bench_v2.py",
          "scripts/gen_questions_v2.py", "src/atlasrag/llm.py"]:
    tracked = bool(sh("git", "ls-files", "--error-unmatch", f))
    last = sh("git", "log", "-1", "--format=%h %ad", "--date=short", "--", f)
    print(f"  {'tracked  ' if tracked else 'UNTRACKED'} {f:46} last commit: {last or '-'}")

# ---- 2. frozen assets ----
head("2. FROZEN ASSETS")
snap = ROOT / "audit" / "frozen_hashes.json"
cur = {p.relative_to(ROOT).as_posix(): sha(p) for p in frozen_files() if p.exists()}   # POSIX keys: same on Windows/Linux
missing = [f for f in FROZEN if not (ROOT / f).exists()]
empty = [str(p.relative_to(ROOT)) for p in frozen_files() if p.exists() and p.stat().st_size == 0]
if empty:
    print("ZERO-BYTE result files (aborted runs? they pollute report/compare loaders):", empty)
if missing:
    print("MISSING:", missing)
if a.snapshot:
    snap.parent.mkdir(exist_ok=True)
    snap.write_text(json.dumps(cur, indent=2, sort_keys=True))
    print(f"wrote {snap.relative_to(ROOT)} ({len(cur)} files). Commit it; later runs will verify against it.")
elif snap.exists():
    ref = {k.replace("\\", "/"): v for k, v in json.loads(snap.read_text()).items()}   # accept snapshots written on Windows
    bad = [k for k in ref if cur.get(k) != ref[k]]
    new = [k for k in cur if k not in ref]
    print("frozen assets UNCHANGED vs snapshot" if not bad else f"CHANGED/MISSING vs snapshot: {bad}")
    if new: print("not in snapshot:", new)
else:
    print("no snapshot yet; current hashes:")
    for k, v in sorted(cur.items()): print(f"  {v}  {k}")
    print("run with --snapshot to record them")
for p in ["data/bench/questions.jsonl", "results/run1/E_oracle.jsonl"]:
    ign = sh("git", "check-ignore", "-v", p)
    print(f"  git-ignored? {p}: {ign or 'no (tracked or untracked-visible)'}")

# ---- 3. instrumentation (STATIC grep; presence != correctness) ----
head("3. LLM INSTRUMENTATION (static keyword scan; not proof it works)")
llm = (ROOT / "src/atlasrag/llm.py").read_text(encoding="utf-8") if (ROOT / "src/atlasrag/llm.py").exists() else ""
gen = (ROOT / "scripts/gen_questions_v2.py").read_text(encoding="utf-8") if (ROOT / "scripts/gen_questions_v2.py").exists() else ""
checks = {
    "provider/API call counter":   r"provider_calls|api_calls|network_calls",
    "cache hit counter":           r"cache_hits",
    "cache miss counter":          r"cache_miss",
    "RateLimitError counter":      r"rate_?limit_?(errors|count|hits)",
    "APIConnectionError counter":  r"connection_?(errors|count)",
    "retry counter":               r"retr(y|ies)_?(attempts|count)|\bretries\b\s*[\+=]",
    "final rate-limit exception":  r"LLMRateLimitExceeded",
    "token counters":              r"prompt_tokens.*completion_tokens|completion_tokens.*prompt_tokens",
}
for name, rx in checks.items():
    print(f"  {'yes' if re.search(rx, llm) else 'NO ':3} {name}")
print("  generation script prints an LLM summary:", "yes" if re.search(r"stats|summary|tokens", gen) else "NO")
print("  generation script catches the rate-limit stop:", "yes" if "LLMRateLimitExceeded" in gen else "NO")
print("  generation script persists a summary file:", "yes" if re.search(r"json\.dump|write_text", gen) else "NO (stdout only)")

# ---- 4. chain feasibility from the real index ----
head("4. CHAIN SOURCING: is the bottleneck sourcing or the section gate?")
idx = ROOT / "data/index/chunks.jsonl"
if not idx.exists():
    print("data/index/chunks.jsonl not found; skipped")
else:
    chunks = [json.loads(l) for l in open(idx, encoding="utf-8") if l.strip()]
    rx = None
    for mod in ("atlasrag.bench.generate_v2", "atlasrag.bench.generate"):
        try:
            m = __import__(mod, fromlist=["x"])
            for attr in ("EVIDENCE_SECT", "EVIDENCE_SECTIONS", "EVIDENCE_RE"):
                if hasattr(m, attr):
                    rx, src = getattr(m, attr), f"{mod}.{attr}"; break
        except Exception:
            pass
        if rx: break
    if rx is None:
        rx, src = re.compile(r"result|method|data|observ|analys|discussion|measure", re.I), "FALLBACK (original scaffold regex)"
    match = (lambda s: bool(rx.search(s))) if hasattr(rx, "search") else (lambda s: any(k in s.lower() for k in rx))
    print("evidence-section rule in use:", src)
    long_ = [c for c in chunks if len(c["text"]) >= 500]
    papers = sorted({c["paper_id"] for c in chunks})
    has_abs = {c["paper_id"] for c in chunks if c["section"] == "Abstract"}
    ev = [c for c in long_ if match(c["section"]) and c["section"] not in ("Abstract", "Front matter")]
    ev_papers = {c["paper_id"] for c in ev}
    print(f"papers {len(papers)} | with Abstract chunk {len(has_abs)} | with >=1 evidence chunk {len(ev_papers)} | "
          f"papers with BOTH {len(has_abs & ev_papers)} | evidence chunks {len(ev)} of {len(long_)} long chunks")
    sec = collections.Counter(c["section"] for c in long_)
    print("\nlong-chunk sections NOT matched by the rule (top 30)  <- candidates for false negatives:")
    for s, n in [(s, n) for s, n in sec.most_common() if not match(s)][:30]:
        print(f"  {n:4}  {s[:70]}")
    restate = [c for c in ev if re.search(r"conclusion|summary|outlook", c["section"], re.I)]
    print(f"\nmatched 'evidence' chunks that look like RESTATEMENTS of the abstract (conclusion/summary/outlook): "
          f"{len(restate)} of {len(ev)} ({100 * len(restate) / max(1, len(ev)):.0f}%)")
    if a.dump_sections:
        import csv
        every = collections.Counter(c["section"] for c in chunks)
        example = {}
        for c in chunks:
            example.setdefault(c["section"], c["text"][:90].replace("\n", " "))
        with open(a.dump_sections, "w", newline="", encoding="utf-8-sig") as fh:
            w = csv.writer(fh)
            w.writerow(["section", "chunks", "long_chunks", "rule_matched", "is_evidence (fill y/n/maybe)", "example_text"])
            for sname, n in every.most_common():
                w.writerow([sname, n, sec.get(sname, 0), int(match(sname)), "", example[sname]])
        print(f"wrote {a.dump_sections}: open in Excel, fill the is_evidence column")
    print("\nmatched sections (top 10):", [(s, n) for s, n in sec.most_common() if match(s)][:10])
    print("\nREAD the unmatched list: real evidence headings there (e.g. 'Cepheid calibration', 'Constraints') mean the "
          "gate is a vocabulary problem, not a corpus problem. Junk fragments mean the PDF parser is the problem.")

# ---- 5. pilots ----
head("5. PILOT ARTIFACTS")
for p in sorted(glob.glob(str(ROOT / "data/bench/*pilot*.jsonl"))):
    rows = [json.loads(l) for l in open(p, encoding="utf-8") if l.strip()]
    print(f"{Path(p).name}: {len(rows)} rows | by type {dict(collections.Counter(r.get('qtype') for r in rows))} "
          f"| by status {dict(collections.Counter(r.get('status') for r in rows))}")
if not glob.glob(str(ROOT / "data/bench/*pilot*.jsonl")):
    print("none found")

# ---- 6. tests ----
if a.run_tests:
    head("6. TESTS")
    env = dict(os.environ, PYTHONPATH=str(ROOT / "src"))
    r = subprocess.run([sys.executable, "-m", "pytest", "-q"], cwd=ROOT, capture_output=True, text=True, env=env)
    print("\n".join((r.stdout + r.stderr).strip().splitlines()[-8:]))
