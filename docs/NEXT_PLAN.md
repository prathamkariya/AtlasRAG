# AtlasRAG: next plan

Part 1 is for you. Part 2 is the prompt to paste to your coding agent (Phase A only; it stops and waits for you).

---

# Part 1: the plan

## Where you are (verified on GitHub, `main` = `6317774`)
- Clean: **103 tests pass** with CI-only dependencies, 0 PDFs tracked, no stray root files, 4 docs files (6,057 lines), frozen assets unchanged, corpus manifest verifies. *Not verified:* whether the GitHub Actions workflow actually ran. Look at the **Actions** tab and tell me.
- Corpus v2: 119 papers (2022 to 2026), **32 test papers** (2022: 5, 2023: 2, 2024: 7, 2025: 5, 2026: 13). Embeddings exist only on your machine (`data/index_v2/`) and can be rebuilt from `chunks.jsonl`.
- **There is no valid benchmark on corpus v2 yet.** Run 1 (v1 corpus, 27 questions from 9 papers) stays as the historical result: on every audit-clean subset C, E, F and G have equal recall, so routing's measurable value there is **cost only**.
- You do **not** need to adjudicate the 5 unstable questions from the old benchmark. Their instability (75% pairwise agreement over 4 judge runs) is already the evidence for why the new benchmark needs stability gating.

## What was missing, now built (`benchmark_gates.patch`, 111 tests pass on `main`)
1. **Judge ≠ generator.** The generator used one model for both writing and judging a question. `--judge-model` separates them and records both in each question.
2. **Review provenance.** Every accept/reject now records `review:human` or `review:llm_assisted`. The final benchmark requires `review:human`.
3. **Stability for new files.** The old options silently compared *zero* new questions (they were missing from the old runs). `--no-baseline --include-validation` fixes that.
4. **`finalize_benchmark.py`**: the only door into a final benchmark. Gates, each reported by name: reviewed by a human, test-split paper, judge passed in **every** run (at least 3), right evidence structure for the type, no duplicates, provenance present. It writes `questions_final.jsonl` plus a manifest (counts, papers, paper concentration, models, review modes, whether the same model generated and judged).
5. **`pilot_yield.py`**: survival rate per type and provider tokens per surviving question.

## What is still NOT solved (say so in any write-up)
- **No gate exists for "conflicting" questions.** The code only branches for multi-hop and temporal; nothing checks that findings actually disagree. Conflicting stays out of scope: the benchmark will have 0 of them.
- The pair gate is still permissive (37% of cross-paper chunk pairs pass after the anchor fix), so most selection happens in expensive LLM calls.
- Compass does not exist. There are no answer-quality metrics yet (only retrieval recall, cost and latency).
- Your accept/reject labels on the old 94 questions were partly LLM-assisted.

## Phases

| Phase | Who | What | Gate to continue |
|---|---|---|---|
| **A** (about 1 hour) | agent | Apply the patch (PR), list available models, run a small pilot on corpus v2, summarize yield | You read the pilot numbers |
| **B** | agent, unattended | Scale generation: about 3x the final target per type | Survival rate per type (below) |
| **C** | agent | Stability audit on the candidates *before* any human sees them: `audit_stability.py --status candidate --all --no-baseline --include-validation --reps 2` | Only `stable_pass` goes to review |
| **D** | **you** | Interactive review (about 2 min per question; do not use `--apply`) | Enough reviewed questions |
| **E** | agent | `finalize_benchmark.py --strict`, commit the final file and manifest, tag `bench-v2-final` | Minimums met |
| **F** | agent | Only now: oracle labels, baselines A/B/K/F/G/C/E (retrieval-only), paired and paper-cluster CIs, a stability rerun | Then decide on Compass |

**Proposed minimums** (warnings, not claims): simple 15, multi_hop 15, chain 10, temporal 10 = 50 questions from at least 20 distinct test papers, with no paper contributing more than about 20%. You adjust these at Phase E.

**Decision rules after the pilot (Phase A):**
- A type with a survival rate under about 5% per attempt: **do not brute-force it.** Either fix its gate first or drop it from the claims.
- **Quota (from your Groq Limits page, organization base limits).** `openai/gpt-oss-20b`, `openai/gpt-oss-120b` and `qwen/qwen3.8-27b` each show 30 requests/min, **1K requests/day, 8K tokens/min, 200K tokens/day**. Limits are listed per model, and Groq documents them per model, so the generator (20b) and the judge (120b) should have separate daily buckets; the pilot confirms this (if both stop at the same moment, they share one). The **200K/day cap is the real limit**, not the per-minute cap.
  - Illustration only, until the pilot measures real tokens: at about 1.3K tokens per call, the judge model's 200K/day is about 150 judge calls per day. Each saved candidate costs one judge call per judged attempt plus 2 stability repetitions, so if 30% of judged attempts are saved that is about 5 judge calls per saved candidate: **roughly 28 saved candidates per day**. About 125 candidates (for 50 final after stability and review attrition) is then **4 to 5 days of quota**. Plan it as an unattended multi-day run, not an evening.
  - Use `pilot_yield.py` output (`tokens_per_survivor`) to replace this illustration with your real number.
- **Time-box:** if after Phase D the final set has fewer than 30 questions or fewer than 12 papers, stop growing the benchmark. Report the cost-only result on what is valid, and present the *methodology* (judge instability, funnel measurements) as the contribution. That is an honest, defensible outcome.

**Compass comes last, and only if** Phase F shows oracle headroom (E using clearly fewer LLM calls than F at equal recall) and the label distribution passes `label_stats.py`.

## Decisions that are yours
1. Judge model. Recommended: **`openai/gpt-oss-120b`**: a different model from the generator (avoids self-agreement bias), larger, with its own 200K/day bucket per Groq's per-model limits. `qwen/qwen3.8-27b` is another independent family with the same limits, but I know nothing about its behavior; test it on a few known questions before trusting it, and it may reject the `reasoning_effort` parameter the client sends. `allam-2-7b` (6K tokens/min), the prompt-guard models and `gpt-oss-safeguard-20b` (3 requests/min, 2K tokens/min) are not suitable judges.
2. The minimums, and how many review hours you can give.
3. Whether to write a conflicting-question gate (a coding task) or leave it out of scope.

---

# Part 2: Phase A agent prompt (paste everything below this line)

You are working in `D:\Pratham\coding\projects\AtlasRAG` (GitHub `prathamkariya/AtlasRAG`), Windows PowerShell, Python 3.13 venv. This phase is **mechanical**: apply one reviewed patch, list models, run one small generation pilot, and **report raw output**. You make no research decisions. You stop at the end of A4.

The patch is at `D:\tmp\benchmark_gates.patch`. `main` should be at `6317774` or later.

## Rules
1. **Protected, never modify:** `data/bench/questions.jsonl`, `data/bench/questions_v1_frozen.jsonl`, `results/run1/`, `data/bench/audit*.json*`, `data/bench/v2_review_manifest.json`, `data/processed/chunks.jsonl`, `data/raw/metadata.jsonl`, `data/llm_cache/default/`, `data/processed_v2/chunks.jsonl`, `data/raw_v2/metadata.jsonl`, `corpus/`. After each task run `python scripts\repo_audit.py | Select-String "frozen assets"`; it must print `UNCHANGED vs snapshot`.
2. **Never run** `gen_questions.py`, `review_questions.py`, `label_oracle.py`, `label_oracle_v2.py`, `audit_stability.py`, or `finalize_benchmark.py` in this phase. Do not review, accept, reject or finalize any question.
3. **Never `git add -A` or `git add .`.** Exact paths only. Never stage PDFs, `data/index_v2/`, `.env`, `*.npy`, or new files under `data/llm_cache/`. No force-push. No new documents.
4. Do not change code beyond what the patch contains. If `git apply --check` fails, stop and paste the output.
5. **Report only what you ran**, verbatim. If a command fails, stop and paste the full error.
6. The environment variable `ATLAS_CONFIG` selects the corpus: unset for A1 and A2, set to `configs\corpus_v2.yaml` for A3 only, then unset again. Always set `PYTHONUTF8=1`.

Start every session:
```powershell
cd D:\Pratham\coding\projects\AtlasRAG
.venv\Scripts\Activate.ps1
$env:PYTHONUTF8 = "1"; $env:PYTHONPATH = "src"
Remove-Item Env:ATLAS_CONFIG -ErrorAction SilentlyContinue
git fetch --all --prune
```

### A1: apply the patch on a branch (do not merge)
```powershell
git switch main
git pull
git switch -c benchmark-gates
git apply --check D:\tmp\benchmark_gates.patch
git apply D:\tmp\benchmark_gates.patch
python -m pytest -q                       # report the exact line; the reviewer measured 111 passed
git add scripts/audit_stability.py scripts/finalize_benchmark.py scripts/gen_questions_v2.py scripts/pilot_yield.py scripts/review_questions.py scripts/show_questions.py src/atlasrag/bench/audit_stability.py src/atlasrag/bench/finalize.py src/atlasrag/bench/generate_v2.py src/atlasrag/bench/pilot_yield.py src/atlasrag/bench/review_meta.py tests/test_benchmark_gates.py
git status --short                        # exactly those 12 paths staged
git commit -m "Benchmark gates: separate judge model, review provenance, stability for new files, finalize gate and manifest, pilot yield summary"
git push -u origin benchmark-gates
python scripts\repo_audit.py | Select-String "frozen assets"
```
Open a pull request `benchmark-gates` into `main`. Do not merge it.

### A2: list the models this key can call
```powershell
python scripts\list_models.py
```
Paste the full list. **Stop here and wait** for the human to reply with `JUDGE_MODEL=<id>`. Do not pick one. (The human has seen the Groq limits table; the recommended judge is `openai/gpt-oss-120b` if it appears in your list.)

### A3: the pilot (only after the human gives `JUDGE_MODEL`)
```powershell
git switch -c pilot-v3
$env:ATLAS_CONFIG = "configs\corpus_v2.yaml"
Test-Path data\index_v2\emb.npy; Test-Path data\index_v2\chunks.jsonl         # both must print True
```
If either is `False`, run `python scripts\rebuild_index_from_chunks.py` (about 5-10 minutes), report that you did, then continue.
```powershell
python scripts\gen_questions_v2.py --split test --per-type 2 --types simple multi_hop chain temporal --attempts 6 --model openai/gpt-oss-20b --judge-model <JUDGE_MODEL> --out data\bench\questions_v3_p1.jsonl
```
Budget: at most 12 attempts per type, 48 in total, so at most about 70K tokens on the generator model (its daily cap is 200K). Do **not** raise `--per-type` or `--attempts` in this phase.

Exit code 2 means "stopped by a rate limit". Wait two minutes and rerun the **same** command (it resumes; finished work is kept). If it stops again almost immediately, it is probably a **daily** cap: do not keep retrying; report it and ask the human to read the Usage page at console.groq.com. Then:
```powershell
python scripts\pilot_yield.py data\bench\questions_v3_p1.runs.jsonl
Remove-Item Env:ATLAS_CONFIG
git add data/bench/questions_v3_p1.jsonl data/bench/questions_v3_p1.runs.jsonl
git status --short                        # exactly those 2 paths
git commit -m "Pilot generation on corpus_v2: 3 per type, separate judge model (candidates only, nothing reviewed)"
git push -u origin pilot-v3
python scripts\repo_audit.py | Select-String "frozen assets"
```

### A4: report, then stop
One message:
```
TASKS: A1 done/failed | A2 done | A3 done/failed
BRANCHES + COMMITS: (branch, short sha, one-line message)
TESTS: exact pytest summary line after A1
OBSERVED (verbatim): model list (A2); the generation script's final printed lines; the full pilot_yield.py output; whether any run stopped with exit code 2 and how long after starting
HUMAN TO ADD: tokens used today per model from console.groq.com Usage (20b and the judge model), to check the buckets are separate
NOT RUN / DEVIATIONS: ...
FROZEN CHECK: repo_audit line after A1 and after A3
```
Do **not** start Phase B, review any question, run the stability audit, or finalize. Do not recommend a judge model or a scale.
