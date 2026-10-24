# AtlasRAG repository audit — 2026-10-24

## Audit basis

Reviewed the pushed main tree at `f4cd074d40234ed6e032a842a65f25b776d1287f`, recent commit diff, CI output, and core source paths for config loading, LLM calls/caching/retries, corpus ingestion, chunk/index construction, retrieval, routing/API, and benchmark generation/validation/finalization. The latest main CI run had **134 passed and 2 failed**; the two failures were repository-hygiene assertions, not the unit-level generation checks.

## Confirmed issues and changes on this branch

1. **CI was red.** The latest push introduced a root-level handoff note plus five one-off patch scripts that violated the repository's root-file guard, and a byte-identical pre-repair copy of `questions_v3.jsonl` that violated the benchmark duplicate guard. The handoff and backup are preserved under `audit/archive/`; the throwaway patch scripts are removed from the root, and cache blobs introduced by that commit are removed from the tracked tree.
2. **Scientific anchors missed equivalent notation.** Greek glyphs, Unicode subscripts, LaTeX parameter names and plain-text aliases did not consistently intersect (e.g. `Ω_m` / `Omega_m` / `\Omega_m`, `σ₈` / `sigma_8`, `fσ8` / `f_sigma_8`, `H₀` / `H0`). Pair acceptance thresholds remain strict; canonicalization and ranking are improved, with alias regression tests.
3. **A blank/truncated completion could crash a generation run.** Empty provider responses now use a dedicated `LLMEmptyCompletion` exception. Expected empty generation/judge completions become counted failed attempts; unexpected programming errors still propagate. Corrupt cache JSON is evicted and regenerated instead of aborting the same prompt.
4. **The unattended runner could confuse CLI errors with rate limits.** Both argparse errors and rate-limit stops can use exit code 2. Cooldown is now attempted only when the child appended a new run record whose stop reason is `rate_limited`. Quota checks use fresh records from the child invocation.
5. **Candidate counts and language were misleading.** The automatic pipeline creates audited `candidate` rows; it does not human-accept benchmark records. Resume targets count candidates only, and status messages/docs now call them audited candidates.
6. **Saved progress could be truncated on interruption.** Question JSONL writes now go through a same-directory temporary file and atomic replace.
7. **Index invariants failed late and opaquely.** Empty indexes, non-2D embeddings, row-count mismatches and zero-dimensional vectors now fail early with actionable `ValueError`s; top-k returns an empty list for empty score arrays or `k <= 0`.
8. **Relative config paths depended on the current directory.** `load_config()` resolves relative paths from the project root and validates that the YAML root and `llm` section have the expected structure. `show_questions.py` accepts `--config` so corpus-v2 question IDs can be resolved against the matching index.
9. **Ingestion accepted `date_from=None` in its type signature but compared a date string directly to `None`.** The fetcher now uses an explicit safe arXiv lower bound when no lower date is passed, with a regression test.
10. **Default model calls were not paced.** The default config now uses the same 2.1-second minimum interval as corpus-v2; pacing timestamp updates before every provider attempt, including failed attempts.
11. **Docs drifted.** Removed an obsolete hard-coded test count, documented the audited-candidate generation/review flow and corpus-config selection, and clarified that Compass is currently a placeholder rather than a functioning baseline.
12. **CI coverage.** A `compileall` step now checks Python syntax across source, scripts and tests before pytest.

## Data/artifact decisions

- `data/bench/questions_v3.jsonl`, run histories, stability reports and frozen question files are kept. The exact duplicate backup is archived unchanged rather than left beside the active benchmark.
- The zero-byte `data/bench/final/atlasrag-v3-2026-10-23/questions_final.jsonl` is intentionally preserved for provenance. Its manifest reports zero questions and the empty-file SHA-256; it is **not** a usable final benchmark.
- Historical candidate rows remain candidates until a person reviews them. An automated support verdict is not ground truth or human acceptance.
- The tracked `data/llm_cache/default/` namespace is described by the repo as retained for Run 1 reproducibility. Newly introduced cache blobs from the latest run are removed; the pre-existing cache remains.

## Remaining quality limitations

- The full pair-funnel script is an upper bound over all cross-paper chunk combinations, not what dense+BM25 actually returns. Improved aliases will not by themselves guarantee a usable neighbor in the retrieved pool.
- Chain yield is still dependent on section labeling and whether later-section material adds evidence beyond the abstract. Do not weaken this gate merely to increase counts.
- LLM-backed end-to-end generation was not run as part of this offline audit; it would consume provider tokens and depend on a live key/quota. A real provider pilot is still needed to measure question yield after the fixes.
- This was a static source/code and test audit through GitHub. It does not certify the remote API key, live Groq availability, downloaded corpus/PDF integrity, or model-quality claims.

## Verification

The branch adds tests for parameter normalization, empty completion handling, corrupted-cache recovery, resume target accounting, invalid-exit classification, index input validation, and `date_from=None`. Use the pull-request check result before merging; this report intentionally does not pre-claim those checks passed.