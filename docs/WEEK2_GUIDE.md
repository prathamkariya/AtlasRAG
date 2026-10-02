# Week 2 — Benchmark construction

**Goal:** a human-reviewed benchmark with gold evidence, oracle routes, and a runner that produces stratified, CI-backed results for Experiments A–E. Everything here is built and tested offline; you run it once Week 1's index exists.

## Order of operations

```bash
# 0. prerequisite: make fetch && make index, and you have read the chunks
# 1. candidate TEST questions (this benchmark; paper-level split keeps it clean)
python scripts/gen_questions.py --split test --per-type 30
# 2. YOU review them (this is the step that makes it a benchmark)
python scripts/review_questions.py --split test
# 3. oracle routes for accepted test questions (Experiment E)
python scripts/label_oracle.py --split test --status accepted
# 4. baselines first
python scripts/run_experiment.py --group run1 --exp A --retrieval-only
python scripts/run_experiment.py --group run1 --exp B --retrieval-only
python scripts/run_experiment.py --group run1 --exp E --retrieval-only
python scripts/report.py --group run1
```
`--retrieval-only` skips answer generation: far cheaper in tokens, and it is all you need for the retrieval-side half of H1. Answer-quality metrics (LLM judge / Ragas) are deliberately deferred to Week 5; they are the expensive part on a free tier.

Train-split questions (for Compass, Week 3) come later:
`gen_questions.py --split train --per-type 80`, then `label_oracle.py --split train --status candidate`. They need no human review, but they are never used for evaluation.

## Targets and budget
| Item | Target | Why |
|---|---|---|
| Test candidates | 30 per type (150) | expect to reject 20-40%; aim to keep ~20-25 per type |
| Accepted test set | ~100-125 | below ~20 per type the CIs are too wide to say anything about H4 |
| Train pool | 300-400 | Compass training data |
| Tokens | ~1-2K per candidate question | multi-paper types often return NONE, hence `--attempts` |

Quality matters more than count. Use `--model` for a stronger generator on a small run if you can afford its daily quota.

## Review guidelines (accept only what you'd defend in an interview)
Reject if any of these hold:
- **Echo:** the question reuses distinctive phrases from the evidence (inflates lexical retrieval).
- **Answerable without the papers** (general knowledge), or **ambiguous** (several defensible answers).
- **simple:** needs more than one passage. **multi_hop:** one passage alone suffices.
- **conflicting:** the two passages don't actually disagree (different quantity, different method, different units). Real tension only.
- **temporal:** the two studies don't address the same quantity, or "later" doesn't supersede "earlier".
- **chain:** the abstract claim isn't actually supported by the paired section.
Edit instead of rejecting when a small rewrite fixes it.

## What the oracle is (state this in the report)
For each question: the cheapest strategy on the ladder SIMPLE < MULTI_HOP < UNCERTAIN whose retrieved chunks cover all gold chunks (`--min-recall`, default 1.0). If none does, the label is UNCERTAIN with `oracle_sufficient=False` — these are retrieval-failure cases and the seed for V3.
- Experiment E is therefore an upper bound **for routing among these strategies on this metric, by construction**. It tells you how much headroom routing has; it is not a competing system.
- If E ≈ B on retrieval recall, routing has little to offer on this workload. That is a valid result.

## Known limitations (put these in the write-up)
- **Gold evidence is the source chunks only.** Other chunks may also answer the question, so recall is conservative and chunk-level.
- **Generated questions are LLM-written**, then human-reviewed; some residual lexical leakage is likely.
- **Paper-level split:** train and test never share papers, but they share a topic and a generator.
- **Retrieval metrics are not answer quality.** Don't claim answer-level gains from Week 2 numbers.
- **n is small.** The report prints 95% bootstrap CIs; claim a question-type effect (H4) only when intervals separate.

## Week 2 exit criteria
- [ ] >= ~100 accepted test questions, roughly balanced across the 5 types
- [ ] Oracle labels on all of them; you've looked at the distribution (a label that's 95% one class means your strategies or questions need work)
- [ ] A, B, E run with `--retrieval-only`; report generated
- [ ] A **second** run of A and B in a new `--group` (and `ATLAS_CACHE_NAMESPACE=run2`), then `report.py --group run1 --compare run2`: ranking stable?
- [ ] Results and `meta.json` files committed (or logged to W&B)

## Next (Week 3)
Train Compass on the train split with oracle labels: a Kaggle notebook (LoRA on a small frozen encoder + classification head), evaluated for routing accuracy in isolation before it goes anywhere near the pipeline.
