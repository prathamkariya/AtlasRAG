# Benchmark data layout

The canonical benchmark used by experiments is `final/atlasrag-bench-v3/`:

- `questions_final.jsonl` — the 64-question benchmark. Its SHA-256 is pinned in `benchmark_manifest.json`.
- `benchmark_manifest.json` — provenance and the CRLF-normalised SHA-256 for `questions_final.jsonl`.
- `oracle_v1_labels.json` — the v1 Oracle route labels restored from commit `3cca0da`. This sidecar is separate from the benchmark questions so the frozen question file and its hash remain unchanged.

Every other file and directory under `data/bench/` is historical provenance showing how the benchmark was produced (candidates, audits, stability runs, repairs and backups). These files are not used by the final experiments.

`final/atlasrag-v3-2026-10-23/questions_final.jsonl` is a zero-byte file retained for historical provenance. It is not a usable benchmark.
