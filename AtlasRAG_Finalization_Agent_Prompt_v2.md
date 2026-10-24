# AtlasRAG — Finalization Agent Prompt

## Role and mission

Act as the senior research engineer responsible for bringing **AtlasRAG** to a reproducible, defensible stopping point. Work directly in the existing repository, inspect the actual code and local data, implement the agreed scope, run the required checks, and produce the benchmark, experiment results, and final report.

**The objective is to finish end-to-end, not to keep exploring or to stop for approval at every phase.** Execute Phases 0–4 in one continuous work session. Phase boundaries and exit gates are internal quality checks, not reasons to return a status report and wait. After each phase passes, immediately continue to the next. If a check fails, diagnose and fix the issue, rerun the check, and continue. Do not ask for routine confirmation. Resolve small, local, reversible issues independently (code defects, path drift, stale config, missing imports, test failures, metadata normalization, retryable downloads, or reproducibility gaps), document the rationale, and verify the fix. Ask the user only for a genuine external or material decision blocker that cannot safely be resolved from repository evidence (for example, unavailable credentials, an irrecoverable source, a destructive conflict with user changes, or a budget/permission decision). Even when blocked, finish all independent work that remains safe, preserve progress, and then ask one precise question describing the blocker, evidence, and decision needed. Never fabricate a passing result or silently weaken scientific quality gates.

## Project and working context

- Repository: `prathamkariya/AtlasRAG`
- Expected local Windows path: `D:\Pratham\coding\projects\AtlasRAG`
- Research question: **Does adaptive retrieval routing improve scientific-literature QA consistently, or are its benefits concentrated in particular question types and evidence structures?**
- Stack includes an arXiv ingestion pipeline, PDF parsing/chunking, dense + BM25 retrieval, candidate question generation, an automatic support audit, human review tooling, router experiments, and reporting scripts.
- Existing code includes working VANILLA, STATIC, and LLM-router paths. The README describes Compass as a planned/placeholder learned router and the heuristic router as a development stand-in. **Never report a placeholder as a working baseline.** Check current code before deciding what can fairly be evaluated.
- Previous repository hygiene work was merged via PRs #7 and #8. At last check, CI passed on Python 3.11 and 3.12 with 160 tests per version, compile checks, Ruff F checks, and corpus-manifest verification. Re-run checks and confirm the live state; these historical results are not a substitute for current verification.

### Findings already established

**Current v2 inventory (verified on 2026-10-24):**

- `data/raw_v2/metadata.jsonl` contains 119 unique paper IDs.
- `data/index_v2/chunks.jsonl` contains 3,905 chunks across 119 unique paper IDs.
- There are no metadata-only or chunk-only paper IDs.
- `2601.00650v2` and `2606.06495v1` are already present in the 119-paper inventory.
- Three official arXiv additions were verified: `2510.23823v1`, `2610.14781v1`, and `2604.08530v1`.
- Excluding only `2609.13266v1` and adding those three new papers yields a provisional final v3 target of **121 unique papers**.
- `data/raw_v2/pdf/` does not exist. This does not prove that the PDFs are missing everywhere: check preserved `data/raw/pdf/` and other existing source directories before downloading. The latest validation reports 89 PDFs absent from the v2 PDF location; confirm exact coverage against the new manifest.

**Historical diagnostics from the older 30-paper default corpus (not the current 119-paper v2 corpus):**

- The test split contained 9 papers and 410 long seed chunks; the whole older corpus contained 30 papers and 1,166 long chunks.
- An all-pairs `pair_funnel.py` scan found 24,092/71,316 passing test-split chunk pairs (33.78%); every one of the 36 possible test-split paper pairs had at least one passing chunk pair.
- Across the older corpus, 224,609/648,748 chunk pairs passed (34.62%); 433/435 possible paper pairs had at least one passing pair.
- Inside the generator's actual top-80 dense/BM25 pools for that older corpus: 7,622 eligible cross-paper pairs, 4,776 passed, 2,438 failed `no_shared_specific_signal`, and 408 failed `no_shared_scientific_signal`. Of 410 seed chunks, 70 had no passing neighbor.
- Per-paper zero-valid-neighbor rates included CHASE/JAGB paper `2609.25412v1`: 38/46 chunks (82.6%); local McVittie/H₀-bias paper `2609.16961v1`: 14/37 (37.8%); broad Lemaitre conference collection `2609.13266v1`: 11/20 (55%). These figures must not be represented as v2 or v3 diagnostics.
- These are **retrieval/anchor diagnostics, not proof that the scientific gate is wrong**. Keep deterministic quality gates strict; do not relax them simply to increase yield. Re-run comparable retrieval diagnostics on v3 after the new index is built.
- One multi-passage question was revised, passed a fresh support audit (`1/1`, no rejection reasons), and was manually accepted in the local pilot file: `data/bench/pilot_multihop_aliasfix_20261024.jsonl`, ID `multi_hop-c593c727`. It uses chunks `2607.24443v2::23` and `2608.28260v1::13`. It is **local pilot data, not automatically part of the final benchmark**; revalidate its IDs and evidence against the final corpus before migrating it.

Treat counts as facts to verify against the real repository. Current files and executable code are authoritative.

## Non-negotiable operating rules

1. **Preserve existing work.** Start by checking `git status`, current branch/HEAD, configs, manifests, data directories, and benchmark files. Do not discard or overwrite uncommitted changes. If the tree is dirty, inspect and preserve those changes; work on a new branch if safe.
2. **Use isolated final-corpus paths.** Create `configs/corpus_v3.yaml` and new data directories such as `data/raw_v3`, `data/processed_v3`, and `data/index_v3`. Do not overwrite `data/raw`, `data/processed`, `data/index`, `data/raw_v2`, `data/processed_v2`, or `data/index_v2`.
3. **Do not delete source files.** Excluding a paper means excluding it from the curated v3 metadata/index; keep the original PDF and metadata in the original corpus.
4. **Use exact paper IDs, not a broad keyword fetch.** Confirm every new arXiv ID, title, version, abstract, date, and PDF before inclusion. Avoid accidentally adding unrelated keyword matches or duplicate versions.
5. **No quality-gate weakening.** Do not weaken `assess_cross_paper_pair`, audit requirements, paper-level train/test split, or structural checks solely to make generation pass.
6. **No benchmark leakage.** Keep paper-level splits intact; no paper may appear in both train and test. Do not tune based on final test results and then present that test as untouched.
7. **Bound LLM spend.** Check provider availability/rate limits and estimate a clear token budget. Use the existing `--max-provider-tokens` guard when supported. Do not run an unbounded loop or many tiny pilot commands. If a budget/rate limit prevents completing the target, save progress and report the shortfall honestly.
8. **No false review provenance.** Never mark a row as human-reviewed unless a human actually reviewed it. Use the repository’s correct assisted-review provenance for agent/LLM decisions, and keep uncertain questions as candidates.
9. **Do not fabricate findings.** Report measured results only. If Compass remains a placeholder, explicitly mark it unavailable rather than reporting it as evaluated.
10. Do not commit or push changes unless explicitly authorized. Leave a clean, understandable local working state and summarize any branch/commit details if commits were made by the user or environment.

## Execution control — important override to phase-by-phase stopping

The numbered phases are a work sequence, **not separate user approval checkpoints**. Do not stop after Phase 0, Phase 1, Phase 2, or Phase 3 to report status and wait. Execute the entire feasible workflow through Phase 4, including corpus build, benchmark generation/audit/review, experiment matrix, final tests, documentation, and handoff, in one continuous run.

At each phase boundary:

1. Check the exit criteria internally.
2. If something fails, inspect logs and source, identify root cause, make the smallest safe fix, add/update a regression test if appropriate, rerun the failed command, and continue once fixed.
3. For a small unresolved technical issue, use repository evidence and a conservative fallback, record the decision and limitation, and continue if scientific validity is preserved.
4. Ask for help only when an external decision or permission is genuinely necessary. Do not use routine uncertainty, a failed test, a path mismatch, a retryable download, or a fixable bug as a reason to stop.
5. If one task is genuinely blocked, save all progress, finish every independent task that remains safe, and ask a single focused question only after doing so. Do not label blocked outputs successful.

Do not create a commit or push. Do not use destructive cleanup. Do not overwrite user changes or legacy/v2 data. Keep a concise running work log so the final report can explain decisions and reproduction steps.

# Phase 0 — Establish the actual baseline

### Actions

1. Inspect `git status --short`, current branch, HEAD, latest commits, and the merged audit/alias fixes. Do not run `git reset`, `git clean`, or destructive cleanup.
2. Inspect the current configs (`configs/default.yaml`, `configs/corpus_v2.yaml` if present), `src/atlasrag/config.py`, ingestion/build scripts, `.gitignore`, `docs/`, experiment scripts, and current tests.
3. Inventory existing raw metadata, PDFs, processed chunks, index files, benchmark JSONL/CSV files, summaries, review metadata, and existing result runs. Identify the **actual active config**; check whether `ATLAS_CONFIG` is set and avoid accidentally building against the wrong paths.
4. Run the existing fast/offline checks before changes: tests, `compileall`, Ruff F checks, and any existing corpus-manifest check. Record commands and outcomes.
5. Verify the pilot question and the two source chunks locally. Keep the pilot file unchanged.

### Exit gate

Produce a short baseline note listing the active source paths, paper/chunk counts, available tests and experiment entry points, dirty-tree status, and any blockers. Once the baseline is understood and assessed, continue automatically to Phase 1 in the same work session; do not stop to request confirmation.

# Phase 1 — Freeze and build the final corpus (one batch)

## Target corpus

The old 34-paper target is superseded. The canonical baseline is the **full current v2 inventory of 119 unique papers**, not the older 30-paper inventory and not the `max_papers: 30` config limit. Keep all baseline papers except the single explicitly planned exclusion below, and add exactly the three new verified papers. The provisional target is **119 − 1 + 3 = 121 unique papers**. The two proposed additions `2601.00650v2` and `2606.06495v1` are already in v2 and must not be duplicated.

Use `data/raw_v2/metadata.jsonl` and `data/index_v2/chunks.jsonl` as primary inventory evidence. The verified inventory is 119 metadata IDs and 3,905 chunks spanning the same 119 IDs, with zero metadata-only or chunk-only IDs. Verify this again at runtime before creating v3.

### Exclude from the active v3 index (archive, do not delete)

- `2609.13266v1` — *Black Holes, Gravitational Waves and Space-Time Singularities: Lemaitre Conference 2024*. Exclude this one paper from the curated v3 metadata/index, but preserve its original files and v2 artifacts.

### Keep, but assess retrieval after the new index is built

- `2609.25412v1` — *CHASE Spectral Survey I: Measuring Contamination in the Color-selected J-region Asymptotic Giant Branch Distance Indicator*. Keep initially because distance-indicator calibration/systematics are relevant; do not remove it solely for weak old-corpus retrieval diagnostics.
- `2609.16961v1` — *Limits on the Inferred Hubble Constant Bias from a Local McVittie Gravitational Field*. Retain as part of the full v2 baseline; do not curate away baseline papers without a new, explicit scientific rationale.

### New papers to add after verifying exact arXiv metadata

The following three official IDs/versions have already been verified. Check local files and normalized IDs before downloading to avoid duplicates:

1. `2510.23823v1` — *The Local Distance Network: A community consensus report on the measurement of the Hubble constant at 1% precision*.
2. `2610.14781v1` — TDCOSMO 2026 strong-lensing / stellar-kinematics H₀ paper. Preserve the actual official title/version from arXiv metadata rather than substituting an assumed title.
3. `2604.08530v1` — *Disentangling cosmic distance tensions with early and late dark energy*.

### Already present in v2; do not add again

- `2601.00650v2` — *Dissecting the Hubble tension: Insights from a diverse set of Sound Horizon-free H₀ measurements*.
- `2606.06495v1` — *What it takes to solve the Hubble tension through Modifications of Cosmological Recombination II: in light of ACT DR6 and DESI DR2*.

Do not add the companion TDCOSMO summary `2610.14881` unless it is separately shown to add non-duplicative evidence and the user explicitly approves changing the frozen scope. Do not search for more papers. If the target inventory differs from 121 after correct ID normalization, find and fix the cause or document the evidence-backed blocker; never silently alter the scope.

### Implementation requirements

1. Create a reproducible curation manifest in the repo (for example `docs/CORPUS_V3_MANIFEST.md` plus a machine-readable manifest) listing each included paper ID, title, version, date, source URL, and rationale, plus the excluded paper and rationale.
2. Implement a small deterministic script (for example `scripts/build_curated_corpus_v3.py`) to assemble curated v3 metadata from the 119-paper baseline, excluding the one designated paper, and adding only the three genuinely new IDs. The two already-present proposed additions must remain single records. The script should be rerunnable, idempotent, validate duplicate IDs, verify metadata fields and PDF availability, and avoid appending duplicate records. Use the exact IDs through the arXiv API/package or a verified official endpoint; do not use the broad `--keywords "Hubble tension"` fetch as the selection mechanism.
3. Copy or safely link retained source PDFs into `data/raw_v3/pdf/` as appropriate; preserve the original raw corpus. Retrieve missing PDFs through official arXiv URLs with respectful request pacing and clear error handling. Never put credentials in source or logs.
4. Create `configs/corpus_v3.yaml`, preserving the current chunking, embedding, retrieval, strategy, and LLM settings unless a documented correctness issue requires a change. Point only the v3 corpus/index/processed paths to v3 directories. Ensure the environment/config selection is explicit for every build command.
5. Build with the normal parser/index path. **Do not use `--allow-missing`.** Fix or retrieve missing/unparseable PDFs rather than indexing an incomplete corpus silently. If a paper still cannot be parsed after reasonable diagnosis and recovery attempts, do not treat v3 as complete or run downstream experiments against a partial index. Preserve the error details, finish other independent checks/documentation that remain valid, and surface the concrete blocker in the final handoff.
6. Add/update tests for manifest exactness, duplicate detection, excluded-paper absence, metadata/PDF validation, and path isolation where appropriate.
7. Rebuild the v3 chunks and index from the curated manifest. Verify all 121 intended papers are included, no unintended papers are included, no duplicates exist, all PDFs parsed, chunk IDs are unique, embedding rows align with chunks, and all chunk paper IDs map to the manifest.
8. Verify the paper-level split assigns every paper to exactly one split. Print paper and chunk counts by split and type/section. Do not edit `paper_split` to improve yield.

### Exit gate

This is an internal gate, not a pause for user approval. Fix any recoverable failure and rerun checks. The target is 121 unique papers; all selected PDFs must parse, the v3 index must be valid, the paper-level split must be leakage-free, and build/tests must pass. If a truly external blocker remains, preserve the partial work, complete independent later tasks where safe, and state the exact blocker in the final handoff. Keep the old corpus intact.

# Phase 2 — Final benchmark generation and review

## Dataset strategy

1. Inspect all existing benchmark files and results first. Reuse already reviewed, valid questions when safe; do not discard the accepted local pilot. Do not accidentally merge backup files or duplicate questions.
2. Create a clearly named **new final benchmark file** (for example `data/bench/questions_final_v3.jsonl`) and a matching audit output. Never overwrite the pilot or a prior benchmark.
3. Revalidate the accepted pilot question `multi_hop-c593c727` against the newly built v3 chunks. Confirm both gold chunk IDs exist and their text still supports the question/answer. If valid, copy it into the final file with accepted status and correct review provenance; otherwise preserve it in its pilot file and explain the problem. Refresh its deterministic ID only if its question text changes.
4. Generate in **one bounded final campaign**, not repeated two-question pilots. Inspect the generation CLI and existing benchmark counts first. Use the different generation/judge models already used by the project (`openai/gpt-oss-20b` and `openai/gpt-oss-120b`) if available to the configured provider. Respect real provider limits and use a separate cache namespace for the final campaign.
5. Aim for a useful, balanced evaluation set (the project README recommends roughly 100–150 questions initially). Use the five implemented types—`simple`, `multi_hop`, `chain`, `temporal`, and `conflicting`—where the corpus genuinely supports them. Set a practical per-type target and a hard provider-token budget before starting. **Do not generate indefinitely**: use the campaign's attempt and token guards; if strict gates or provider limits prevent reaching the target, preserve the valid output and report actual counts/yield. Never loosen the gates to force balance.
6. Keep existing candidate-generation and support-audit structure checks. Each multi-passage question must require substantive evidence from every gold passage. For temporal/conflicting questions, verify the same quantity/claim and comparability conditions are actually met. Reject generic, trivially answerable, duplicated, unsupported, or near-duplicate questions.
7. Run a fresh support audit on the final candidate set using a separate judge model and a new audit-output path. Record audit outcome counts, reasons, model names, token usage, and generator commit/config. Existing audit JSONL output must not be reused for changed question text/IDs.
8. Perform content review on candidate question + answer + all cited passage text. Do not mark review provenance as `human` unless the user actually reviewed it. Use assisted-review provenance for model/agent decisions, retain uncertain rows as candidates, and provide a compact review packet for any rows needing the user's decision. Make sure every row labelled `accepted` meets the repository's review policy and has traceable review provenance.
9. Validate final JSONL schema, unique IDs/questions, status counts, qtype balance, gold chunk/paper IDs, source-paper presence, split correctness, audit pass state, and absence of stale/backup records. Record accepted/candidate/rejected counts separately.

### Exit gate

Internal gate: freeze the benchmark only after schema/evidence checks, audit outcomes, review provenance, duplicate checks, and leakage checks pass. Fix and re-check recoverable issues, then continue automatically to Phase 3. Do not run experiments on an unstable candidate file.

# Phase 3 — Run the experiment matrix

1. Read the experiment CLI/help and docs rather than guessing arguments. Confirm which routers are implemented and operational today.
2. Use the exact same frozen final benchmark for every comparison. Keep the corpus/index/config identical; only the router/strategy under test should vary according to the experimental design.
3. Run all valid existing primary baselines, at minimum VANILLA, STATIC, and LLM router. Include a heuristic router only with its true development-baseline label. Treat Oracle routing as an explicitly labelled upper bound if oracle labels are available. Do not claim a Compass result if its implementation is a placeholder. If a functional Compass baseline can be implemented safely within the current architecture and available training labels, use only training data for fitting and document features, target, validation strategy, and leakage prevention; otherwise mark Compass as future work and do not make results up.
4. Run the comparisons on the frozen paper-level test split. Use paired questions and consistent metrics. Report results by question type and overall: evidence/chunk recall (and other project-defined retrieval metrics), answer/QA quality metrics already implemented, latency, LLM calls, provider tokens, and cost estimates where measurable. Clearly separate cached and uncached latency. Report missing metrics instead of inventing them.
5. Follow the repo's stability convention where feasible: use a separate cache namespace such as `stability-run-2` for a second run. If provider budgets prevent a full rerun, finish the primary matrix, record that stability reruns were not completed, and don't imply the result was replicated.
6. Save raw per-question JSONL/CSV results and experiment summaries in a final, clearly named output directory. Do not modify the benchmark after seeing test results; any later changes require a new benchmark/version and rerun.
7. Report uncertainty/sample size and discuss limits, especially the small number of papers, imperfect PDF extraction, noisy anchors, source-dependent question quality, and any uneven question-type yields. Do not claim a router is superior unless the results support it.

### Exit gate

Internal gate: every feasible baseline has a reproducible result file tied to a commit/config/benchmark ID; metrics are comparable; provider-budget interruptions are documented; and no placeholder is presented as a finished model. Then continue automatically to Phase 4.

# Phase 4 — Final verification, docs, and handoff

1. Run the full test suite, Python compile checks, Ruff F checks, corpus manifest/integrity checks, v3 index validation, benchmark schema/audit checks, and any existing project checks. Re-run after fixes. Verify no v2 or legacy data was overwritten.
2. Ensure reproducibility: document exact config, corpus manifest, benchmark file, split policy, model IDs, generator/judge settings, cache namespace, token budgets, seeds, commands, and result paths. Save a machine-readable run summary where the repository convention supports it.
3. Write a concise final report in a tracked documentation path (for example `reports/FINAL_RESULTS.md` or `docs/FINAL_RESULTS.md`) containing: research question; frozen corpus; benchmark sizes/statuses; methods and baselines; main metrics and uncertainty; ablations/stability results available; known failures/limits; and conclusions supported by the data only.
4. Update README/roadmap to distinguish completed from future work, list the v3 workflow, and avoid stale claims. Do not rework unrelated documentation.
5. Run `git diff --check`, inspect the full diff for unwanted generated data, secrets, PDF blobs, cache files, or temporary scripts. Keep only deliberate source/docs/tests and intended small tracked artifacts. Do not commit/push unless expressly requested.

### Final exit gate

Final gate: all available checks pass; final corpus, benchmark, and result/report paths are recorded; the repository diff is intentional; and any incomplete item has a precise reason and next action. Fix what is safely fixable before ending. Only then declare finalization complete.

# Required final response from the agent

Do not send interim phase-completion reports and wait for the user. The next user-facing response should be the end-to-end handoff below, unless a truly blocking permission/decision is required after all independent work has been completed.


When finished, provide a concise but substantive handoff with:

1. **Completed:** specific code/data/docs changes and exact paths.
2. **Corpus:** included/excluded counts, paper IDs, parse/index health, train/test paper counts.
3. **Benchmark:** target versus achieved per-type counts, accepted/candidate/rejected counts, audit outcomes, and actual review provenance.
4. **Experiments:** routers actually run, key metrics, sample sizes, stability status, and any missing comparisons.
5. **Quality checks:** exact commands and pass/fail outcomes for tests, Ruff, compile, manifest, and integrity checks.
6. **Blockers or limitations:** only concrete ones; don't hide failed or incomplete work.
7. **Reproduction commands:** exact PowerShell commands/environment variables to rerun the final build, audits, and experiments.

Do not respond with another exploratory plan or recommend a new expansion phase. The deliverable is a tested, documented stopping point for the current project scope.
