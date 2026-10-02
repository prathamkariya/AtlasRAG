"""Idempotent, anchor-checked edits to files you may have changed locally.
Run from the project root:  python apply_patch.py
If an anchor is not found it tells you exactly what to add by hand; nothing is overwritten blindly."""
from pathlib import Path

EDITS = [
    ("src/atlasrag/bench/schema.py", "ladder_recalls",
     '    notes: str = ""\n',
     '    notes: str = ""\n    gold_route_v2: str | None = None   # oracle v2 (best-recall, cheapest)\n'
     '    ladder_recalls: dict | None = None\n    validation: str = ""               # support-audit verdict (json)\n'),
    ("src/atlasrag/bench/experiments.py", '"E2": "oracle"',
     '"E": "oracle",', '"E": "oracle", "E2": "oracle",'),
    ("src/atlasrag/bench/experiments.py", '"E2": "E2_oracle_v2"',
     '"E": "E_oracle",', '"E": "E_oracle", "E2": "E2_oracle_v2",'),
    ("src/atlasrag/bench/experiments.py", 'code == "E2"',
     'gold = {q.question: q.gold_route for q in questions if q.gold_route} if code == "E" else None',
     'gold = None\n    if code == "E":\n        gold = {q.question: q.gold_route for q in questions if q.gold_route}\n'
     '    elif code == "E2":\n        gold = {q.question: q.gold_route_v2 for q in questions if q.gold_route_v2}'),
    ("scripts/run_experiment.py", "gold_route_v2",
     '''if a.exp == "E":
    qs = [q for q in qs if q.gold_route]''',
     '''if a.exp in ("E", "E2"):
    _key = "gold_route" if a.exp == "E" else "gold_route_v2"
    qs = [q for q in qs if getattr(q, _key)]'''),
]

for rel, marker, anchor, new in EDITS:
    p = Path(rel)
    s = p.read_text(encoding="utf-8")
    if marker in s:
        print(f"[skip]   {rel}: already applied ({marker})"); continue
    if s.count(anchor) != 1:
        print(f"[MANUAL] {rel}: anchor not found exactly once. Add by hand, replacing:\n{anchor}\nwith:\n{new}\n"); continue
    p.write_text(s.replace(anchor, new), encoding="utf-8")
    print(f"[ok]     {rel}: {marker}")
