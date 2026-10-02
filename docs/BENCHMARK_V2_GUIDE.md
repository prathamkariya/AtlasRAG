# Benchmark v2: repair workflow (Week 2c)

run1 stays frozen as historical evidence. Everything below writes to NEW files/groups.

## What this patch adds
| Piece | Purpose |
|---|---|
| `validate.py` + `audit_questions.py` | LLM audit: is the reference answer supported by the gold chunks? are all passages needed (multi-hop/chain)? are compared quantities comparable? same quantity for temporal/conflicting? |
| `generate_v2.py` + `gen_questions_v2.py` | the same generator, but every candidate is audited before you ever see it; prints which defect dominates |
| `oracle_v2.py` + `label_oracle_v2.py` | oracle = cheapest strategy achieving the BEST recall on the ladder; stores all ladder recalls; `E2` experiment uses it |
| `diagnostics.py` + `route_diagnostics.py` | recall retained vs F, calls saved vs F, regret vs E, over-routed (wasted) vs under-routed (harmful) |
| `label_stats.py` | class counts / insufficient share / warnings BEFORE any Compass training |

## Order
```bash
python apply_patch.py                      # anchor-checked edits (schema, experiments, run_experiment)
python -m pytest -q                        # expect 36 passed in a fresh scaffold; your count differs if you added tests

# 1. what is wrong with the 27 you already accepted? (read the flagged ones yourself)
python scripts/audit_questions.py --status accepted --split test

# 2. new candidates, audited at generation time. Start with the 3 types the pipeline can actually test.
python scripts/gen_questions_v2.py --split test --per-type 20 --types simple multi_hop chain

# 3. human review with the v2 rubric (point review_questions.py at questions_v2.jsonl)
python scripts/review_questions.py --file data/bench/questions_v2.jsonl --split test --batch 20

# 4. oracle labels, both versions
python scripts/label_oracle.py    --file data/bench/questions_v2.jsonl --split test --status accepted
python scripts/label_oracle_v2.py --file data/bench/questions_v2.jsonl --split test --status accepted

# 5. rerun controls into run2 (add --file data/bench/questions_v2.jsonl to run_experiment/report)
for e in A B K G C F E E2; do python scripts/run_experiment.py --group run2 --exp $e --retrieval-only --file data/bench/questions_v2.jsonl; done
python scripts/report.py --group run2 --paired-ref F --file data/bench/questions_v2.jsonl
python scripts/route_diagnostics.py --group run2 --router C_llm_router --file data/bench/questions_v2.jsonl
```

## Why oracle v2
v1 labelled any question that no strategy fully covered as UNCERTAIN (9 of your 27). That mixes "hard but solvable" with "unsolvable by this retriever", and a router trained on it learns to spend the most on questions that fail anyway. v2 asks only: what is the cheapest way to get the best recall that is achievable? When nothing helps, the cheapest strategy wins. That is a policy choice (spend nothing on hopeless questions); the alternative `v2_sufficient` training scheme drops those questions entirely. Compare both before committing.
For fully-covered questions v1 == v2.

## Caveats
- **The judge is a filter, not ground truth.** Cheap LLM judges are lenient. Read every flagged question and a sample of passed ones. Log the agreement rate between judge and you; it is a result worth reporting.
- **Audit costs one extra call (~600-900 tokens) per candidate.** Yield drops; that is the point. Budget for it.
- **Temporal and conflicting are off by default.** The audit can reject bad pairs but cannot create good ones. Pairs need to be chosen by shared quantity (e.g. both mention H0 / the same survey) before generation. Until then, report simple, multi_hop and chain only.
- `ValidatedGenerator` subclasses your local `Generator`; if you changed its `ix`/`llm`/`model` attributes, adjust `generate_v2.py`.
- `diagnose()` refuses fixed routers (A, B, F, G, K): they have no routing decisions to diagnose.

## Do not train Compass until
`python scripts/label_stats.py --split train --status candidate` shows: >=150 labelled questions, no class under 10%, insufficient share under 25%, and you have decided v2 vs v2_sufficient. If it warns, fix the data, not the model.
