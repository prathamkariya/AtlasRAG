# Repository health and next plan

## Verified state

- Branch: `generate-v3`, pushed at `f5ae3f9`.
- Tests: `120 passed` (`python -m pytest -q`, 2026-10-17).
- Frozen assets: `UNCHANGED vs snapshot` (`scripts/repo_audit.py`).
- Worktree: only untracked `docs/PHASE_B_PROMPT.md`.
- Git integrity: no corruption; `git fsck` reports only unreachable stash-era trees/commit.

## Phase B output

- Candidate-only benchmark: 30 simple, 30 multi-hop, 3 chain, 8 temporal.
- Chain is insufficient for chain-specific claims. Do not promote or analyze it as a viable type.
- All generated candidates retain separate generator/judge provenance.
- Groq throttling came from 30 RPM / 8K TPM limits. Uncached requests now pace at 2.1 seconds; regression test added.

## Phase B execution record

### B0: benchmark-gates repair

- Removed six speculative Week 17--22 planning documents and renamed `docs/NEXT_PLAN (2).md` to `docs/NEXT_PLAN.md`.
- Applied `D:\tmp\gates_fix.patch` followed by `D:\tmp\token_budget.patch`.
- Test result: `119 passed in 14.16s`.
- Documentation line count after repair: `4471`, below repository guard threshold.
- Pushed commits `a0276b3` and `1b0b4c4` to `benchmark-gates`; human merged B0 into main.

### B1: simple generation

- Target: 30 candidate questions; generator `openai/gpt-oss-20b`; independent judge `openai/gpt-oss-120b`; corpus-v2 index; isolated `v3` cache namespace.
- Initial runs hit bounded 429 stops. Resumes preserved candidates and reached `30/30`.
- No candidate was reviewed, accepted, rejected, or finalized.

### B2: multi-hop generation

- Target: 30 candidate questions; same generator/judge separation and fixed `150000` invocation cap.
- Repeated resumable bounded-429 runs reached `30/30`.
- Deterministic pair gates rejected many pairs without shared specific scientific signals; structural judges rejected unsupported, one-passage, and bad-comparison candidates.

### Rate-limit investigation and mitigation

- Initial local aggregate from `pilot_yield.py` incorrectly looked like a shared 200K daily limit because it aggregates all resumed runs, retries, and both models.
- Groq account screenshots and official documentation showed per-model limits. Official free-plan table lists 30 RPM, 1K RPD, 8K TPM, and 200K TPD for both selected GPT-OSS models.
- Root cause: sequential uncached generation/judge calls arrived quickly enough to hit RPM before bounded retries could recover.
- Added `llm.min_provider_interval_seconds: 2.1` to corpus-v2 configuration. `LLMClient` now sleeps only before a subsequent uncached provider request. Cache hits do not wait.
- Added `test_paces_only_second_uncached_provider_request`; full suite result after change: `120 passed in 12.96s`.
- No provider/model switch occurred. Generator remains 20B; judge remains 120B.
- Commit: `bcf3f5a Pace uncached generation requests below Groq RPM limit`.

### B3: chain generation

- Target: up to 10 best-effort candidates, fixed `80000` invocation cap.
- Result: `3` unique candidates after allowed attempts; duplicate suppression removed repeated survivors.
- Dominant structural rejections: no evidence-bearing second section, no shared scientific signal, abstract/first-passage-only answers, and missing structured evidence.
- Conclusion: retain strict gates; chain is underpowered and excluded from chain-specific claims.

### B4: temporal generation

- Target: 8 candidates, fixed `80000` invocation cap.
- Result: `8/8` candidates after resumable runs.
- Structural rejections included weak temporal sections, no actual update signal, different quantities, unsupported answers, and one-passage answers.

### B5: spot check, artifacts, and push

- Printed three candidate IDs per type for human review. No status mutation occurred.
- Spot-check IDs:
  - simple: `simple-eb13d585`, `simple-e8f0949e`, `simple-ad46c5b1`
  - multi-hop: `multi_hop-81cd3cae`, `multi_hop-ecbf29ba`, `multi_hop-e785e7eb`
  - chain: `chain-89a8604c`, `chain-bd9b43c2`, `chain-424b58d2`
  - temporal: `temporal-68d7fc7d`, `temporal-b7cfd1d5`, `temporal-91a6b5bd`
- Wrote and committed only candidate/run records: `data/bench/questions_v3.jsonl`, `data/bench/questions_v3.runs.jsonl`.
- Commit: `f5ae3f9 Generate benchmark candidates on corpus_v2 (simple, multi_hop, chain, temporal), separate judge model, nothing reviewed`.
- Pushed branch: `generate-v3`.
- Frozen check after push: `frozen assets UNCHANGED vs snapshot`.

### Explicit non-actions

- Did not train Compass.
- Did not modify v1 questions, frozen benchmark files, run1, corpus content, processed chunks, indexes, protected audit files, or default cache.
- Did not run review, stability, finalization, oracle labeling, or experiment scripts.
- Did not promote any v3 candidate to accepted.

## Review findings

1. `scripts/show_questions.py` was run without the corpus-v2 configuration, so several v2 chunk IDs displayed `chunk text not found`. Candidate data itself was not changed. Fix the script/config invocation before human review.
2. `pilot_yield.py` aggregates provider tokens across resumed runs and retry accounting. It is useful for run cost, but its `share_of_one_200k_daily_budget` is not a reliable per-model quota measurement.
3. Chain sourcing is the active quality bottleneck: most pairs fail evidence-section and shared-signal gates. Keep gates strict; do not fabricate chain coverage.
4. Stale local branches with deleted upstreams exist: `anchor-fix`, `benchmark-cleanup`, `cleanup`, `corpus-v2`, `report-cluster`; plus local `backup-main-7ddcf56` diverges from main. They may be deleted only after confirming no unmerged commits are needed.

## Next plan

1. Open and review v3 spot-check candidates using corpus-v2 config; keep all statuses as `candidate` until human review.
2. Fix `show_questions.py` configuration selection, test it against a corpus-v2 chunk, then rerun spot checks.
3. Run independent stability audits only for human-approved candidates. Do not finalize before that.
4. Treat simple and multi-hop as primary analysis strata. Report chain as underpowered; temporal is exploratory until review/stability succeeds.
5. After Phase C/E and merge, prune only confirmed-merged stale branches and unreachable Git objects. Never delete corpus, frozen questions, run1, audited artifacts, indexes, or active caches without an explicit target list.
