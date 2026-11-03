# Phase B: decision and agent prompt

Part 1 is for you. Part 2 is the prompt to paste to your coding agent.

---

# Part 1: the decision

## The pilot table you were given is wrong in three places
It was built from the *last run only* of the pilot, which is exactly the flaw `gates_fix.patch` repairs. The correct whole-pilot numbers (3 runs, 8 saved candidates, 48,851 provider tokens):

| Type | Saved | What the agent's table said | Reality |
|---|---|---|---|
| simple | 3 | 3 of 5 attempts (60%) | same, but only 5 attempts: a rough guide, not a rate |
| multi_hop | 3 | 3 of 6 (50%) | same caveat |
| chain | **1** | "2 of 24 = 8.3%, viable" | **1 saved of about 24 unique attempts (about 4%)**. The second "survivor" was a duplicate of the saved one. |
| temporal | 1 | 1 of 24 (4.2%) | same |
| cost | | "about 4,400 tokens per survivor" | **6,106 tokens per saved candidate overall** |

Cost by type, from the per-run totals (rough, 1 sample each for chain and temporal): about **3K tokens per saved simple or multi-hop candidate, 13K to 16K per saved chain or temporal candidate**.

## Why chain and temporal are expensive (and why my earlier remark was wrong)
I told you chain and temporal attempts "mostly die at the free deterministic gate, so more attempts are cheap". The per-run outcomes say otherwise. In run 3, about 12 of the roughly 13 chain attempts that reached the judge failed with `not_all_passages_needed`: the generator writes a question the *abstract alone* can answer. Those attempts spend generation and judge tokens and are then thrown away. More attempts mean more wasted tokens, not free ones.

I also tested the obvious cheap fix, a free filter on how much of the reference answer one passage covers. It shows no signal on your 10 labelled non-simple questions (mean single-passage coverage 0.36 for stable failures, 0.43 for unstable ones), because reference answers are paraphrases. So I did not build it.

## My choice: A-prime (neither A nor B as framed)

- **Scale `simple` and `multi_hop` now.** They are cheap and productive: about 3K tokens per saved candidate, 50% to 60% of attempts in a tiny sample.
- **`chain` and `temporal` are best-effort, under a hard token cap, with no minimum.** If they do not reach about 10 stable, human-accepted questions each, they are out of the claims, and the write-up says so.
- Targets, as **generated candidates** (about 3x the final goal): simple 30, multi_hop 30, chain 10, temporal 8. Final minimums at Phase E: simple 15 and multi_hop 15, chain and temporal "if they get there".
- **The research question survives.** Your H4 ("does routing help only some question types?") becomes *simple vs multi-hop*, which is the core Adaptive-RAG-style question.
- Improving the chain and temporal question-writing prompt so the second passage is genuinely required is a separate, later experiment (about 25K tokens to test). It is not part of this phase.

## Budget (from your Groq limits: 200K tokens/day and 1K requests/day per model)

| Step | Expected total tokens | Cap in the command |
|---|---|---|
| simple, 30 candidates | about 100K (roughly half on each model) | 150K |
| multi_hop, 30 candidates | about 100K | 150K |
| chain, up to 10 | up to 80K | 80K |
| temporal, up to 8 | up to 80K | 80K |

Day 1 is simple and multi_hop (about 100K per model, inside the 200K/day cap). Day 2 is chain and temporal. If a command stops on the daily cap, it resumes the next day. Phase C (the stability reruns) needs roughly another 2 judge calls per saved candidate, so budget a third day.

## Things the agent did that you should know about
- **A new commit on `benchmark-gates` added six more planning docs (about 16,600 lines, Weeks 17-22) and a file named `NEXT_PLAN (2).md`.** `docs/` is now 22,818 lines against the 8,000 cap, so the repo's own guard test fails: **merging this branch as it stands would break `main`'s CI.** Step B0 removes them. The agent should create no more documents; the guard test enforces it.
- Pilot runs wrote 54 new cache files into the tracked `default` namespace. From now on the agent sets a separate cache namespace so cache files stay untracked.

## Decisions that are yours
1. Confirm A-prime, or change the targets.
2. After Phase B, you read the spot-check questions the agent pastes, before Phase C spends more quota.

---

# Part 2: agent prompt (paste everything below this line)

You are working in `D:\Pratham\coding\projects\AtlasRAG` (GitHub `prathamkariya/AtlasRAG`), Windows PowerShell, Python 3.13 venv. Do exactly the steps below and **report raw output**. You make no research decisions and you create **no documents of any kind**.

Patch files are in `D:\tmp\`: `gates_fix.patch`, then `token_budget.patch` (apply in that order).

## Rules
1. **Protected, never modify:** `data/bench/questions.jsonl`, `data/bench/questions_v1_frozen.jsonl`, `results/run1/`, `data/bench/audit*.json*`, `data/bench/v2_review_manifest.json`, `data/processed/chunks.jsonl`, `data/raw/metadata.jsonl`, `data/llm_cache/default/`, `data/processed_v2/chunks.jsonl`, `data/raw_v2/metadata.jsonl`, `corpus/`. After each task run `python scripts\repo_audit.py | Select-String "frozen assets"`; it must print `UNCHANGED vs snapshot`.
2. **Never create or edit anything under `docs/`.** The repo has a test that fails above 8,000 lines in `docs/`; a planning document will break CI.
3. **Never `git add -A` or `git add .`.** Exact paths only. Never stage PDFs, `data/index_v2/`, `.env`, `*.npy`, or any file under `data/llm_cache/`. No force-push except where B0 says so.
4. Never run `review_questions.py`, `audit_stability.py`, `finalize_benchmark.py`, `label_oracle*.py`, `run_experiment.py`. Do not review, accept, reject or finalize any question. Do not raise any `--per-type`, `--attempts` or `--max-provider-tokens` value.
5. **Report only what you ran**, verbatim. If a command fails, stop and paste the full error.
6. Cache namespace: for every generation command set `$env:ATLAS_CACHE_NAMESPACE = "v3"` so cache files go to an ignored folder.

Start every session:
```powershell
cd D:\Pratham\coding\projects\AtlasRAG
.venv\Scripts\Activate.ps1
$env:PYTHONUTF8 = "1"; $env:PYTHONPATH = "src"
Remove-Item Env:ATLAS_CONFIG -ErrorAction SilentlyContinue
git fetch --all --prune
```

### B0: repair `benchmark-gates` so CI passes, then stop for the human to merge
```powershell
git switch benchmark-gates
git pull
git status --short                       # must be clean
# remove the six planning docs added by the latest commit (exact paths)
git rm docs/17_WEEK_17_V7_V3_ADAPTIVE_GRAPH_ESCALATION.md docs/18_WEEK_18_V7_ROBUSTNESS_CROSS_DOMAIN_GRAPH_TRANSFER.md docs/19_WEEK_19_FINAL_INTEGRATED_END_TO_END_EVALUATION.md docs/20_WEEK_20_FINAL_RESEARCH_SYNTHESIS_PAPER_RELEASE.md docs/21_WEEK_21_POST_RELEASE_V8_RESEARCH_SELECTION.md docs/22_WEEK_22_V8_CONTROLLED_RESEARCH_EXECUTION.md
git mv "docs/NEXT_PLAN (2).md" docs/NEXT_PLAN.md            # a file name with a space and parentheses; if docs/NEXT_PLAN.md already exists, STOP and report
git commit -m "Remove speculative planning docs added after cleanup; rename NEXT_PLAN copy"
git apply --check D:\tmp\gates_fix.patch
git apply D:\tmp\gates_fix.patch
git apply --check D:\tmp\token_budget.patch
git apply D:\tmp\token_budget.patch
python -m pytest -q                      # report the exact line; the reviewer measured 119 passed, with docs under the cap
git add scripts/gen_questions_v2.py scripts/pilot_yield.py src/atlasrag/bench/generate_v2.py src/atlasrag/bench/pilot_yield.py src/atlasrag/bench/budget.py tests/test_benchmark_gates.py tests/test_gen_script.py
git status --short                       # exactly those 7 paths staged
git commit -m "Fix: record judge/generator provenance for all question types, correct multi-run pilot summary, new seed per resume, token budget"
git push
python scripts\repo_audit.py | Select-String "frozen assets"
(Get-Content docs\*.md | Measure-Object -Line).Lines          # report; must be under 8000
```
Then **stop**. Report the pytest line and the docs line count, and tell the human the PR is ready: the human checks that the **CI check is green** and merges `benchmark-gates` into `main`. Do not continue until the human says `B0 MERGED`.

### B1-B4: generation (only after `B0 MERGED`)
```powershell
git switch main
git pull
python -m pytest -q                       # report; must pass
git switch -c generate-v3
$env:ATLAS_CONFIG = "configs\corpus_v2.yaml"
$env:ATLAS_CACHE_NAMESPACE = "v3"
Test-Path data\index_v2\emb.npy; Test-Path data\index_v2\chunks.jsonl           # both True; else run python scripts\rebuild_index_from_chunks.py and report
```
Run these **in order**, one at a time. Every command appends to the same output file and is resumable:
```powershell
# B1
python scripts\gen_questions_v2.py --split test --types simple    --per-type 30 --attempts 3  --max-provider-tokens 150000 --model openai/gpt-oss-20b --judge-model openai/gpt-oss-120b --out data\bench\questions_v3.jsonl
# B2
python scripts\gen_questions_v2.py --split test --types multi_hop --per-type 30 --attempts 5  --max-provider-tokens 150000 --model openai/gpt-oss-20b --judge-model openai/gpt-oss-120b --out data\bench\questions_v3.jsonl
# B3 (best effort, hard cap)
python scripts\gen_questions_v2.py --split test --types chain     --per-type 10 --attempts 12 --max-provider-tokens 80000  --model openai/gpt-oss-20b --judge-model openai/gpt-oss-120b --out data\bench\questions_v3.jsonl
# B4 (best effort, hard cap)
python scripts\gen_questions_v2.py --split test --types temporal  --per-type 8  --attempts 12 --max-provider-tokens 80000  --model openai/gpt-oss-20b --judge-model openai/gpt-oss-120b --out data\bench\questions_v3.jsonl
```
**Exit codes and what to do:**
- `0`: finished (target reached or attempts used up). Go to the next command.
- `2`: stopped by a rate limit. Wait 2 minutes and rerun the **same** command. If it exits `2` again within 5 minutes, assume the **daily** cap: stop for the day and report. Do not rerun the same command more than 3 times in one session.
- `4`: the token budget for this invocation was reached. **Stop that command and move on.** Do not raise the budget.

After **each** command run, print the whole-pilot summary:
```powershell
python scripts\pilot_yield.py data\bench\questions_v3.runs.jsonl --questions data\bench\questions_v3.jsonl
```
Required check after each: `"saved_without_judge_model"` must be `0`. If it is not, stop and paste the output.

### B5: spot check, then commit
Print three random saved questions per type for the human to read (do **not** judge them yourself):
```powershell
python scripts\show_questions.py --file data\bench\questions_v3.jsonl --ids <3 ids per type taken from the file>
```
Then:
```powershell
Remove-Item Env:ATLAS_CONFIG; Remove-Item Env:ATLAS_CACHE_NAMESPACE
git add data/bench/questions_v3.jsonl data/bench/questions_v3.runs.jsonl
git status --short                        # exactly those 2 paths; no cache files, no PDFs
git commit -m "Generate benchmark candidates on corpus_v2 (simple, multi_hop, chain, temporal), separate judge model, nothing reviewed"
git push -u origin generate-v3
python scripts\repo_audit.py | Select-String "frozen assets"
```

## Final report (one message)
```
B0: pytest line | docs line count | CI status as you can see it | PR link
B1-B4 per command: exit code(s) and how many times you reran | the pilot_yield "saved_per_type", "tokens_per_saved_candidate", "runs_stopped_by_rate_limit", "saved_without_judge_model"
SPOT CHECK: the printed questions, verbatim
COMMITS: (branch, short sha, one-line message)
FROZEN CHECK: repo_audit line after B0 and after B5
NOT RUN / DEVIATIONS: ...
```
**Stop here.** Do not start the stability audit, review questions, or finalize. The human decides.
