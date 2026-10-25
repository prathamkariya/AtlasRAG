# AtlasRAG

**Adaptive Retrieval Routing for Scientific Literature (Hubble Tension Corpus)**

> **Research Focus:** Investigating whether adaptive, query-dependent retrieval routing improves evidence retrieval accuracy and efficiency over static hybrid retrieval when navigating dense, conflicting scientific literature in astrophysics.
>
> **Core Empirical Finding:** Static hybrid retrieval (**`B_static`**: Dense BGE-small + Lexical BM25 + Cross-Encoder reranking) decisively outperforms adaptive LLM routing (**`C_llm_router`**) by **+10.0% evidence recall** (paired 95% bootstrap CI $[-0.18, -0.03]$ strictly excludes zero), with **0 LLM calls**, **zero token overhead**, and **more than 2x lower latency**. Static hybrid operates within **2%** of the empirical Oracle ceiling (**`E_oracle`**).
>
> **Scope & Status:** Corpus v3 (121 papers, 4,076 chunks) and Benchmark v3 (64 questions, 30 test papers) are frozen, fully audited, and evaluated across 8 baselines. `CompassRouter` is an unbuilt placeholder and is documented as future work.

> [!IMPORTANT]
> **Evaluation Scope: Retrieval-Only Evaluation (`retrieval_only=true`)**
> All queries in this evaluation were evaluated strictly on evidence chunk recall and paper recall against curated gold passages (`answer: null`). Generative answer synthesis correctness was not evaluated, isolating retrieval performance directly.

---

## 1. Key Results Summary

Evaluated on the frozen, leakage-free test split of **Benchmark v3** (`atlasrag-bench-v3`, $n=64$, 30 test papers):

| Experiment | Router / Strategy | Evidence Recall [95% CI] | Paper Recall [95% CI] | Median Latency | Logical Tokens | Logical LLM Calls | Route Acc |
|---|---|---|---|---|---|---|---|
| **A_vanilla** | Dense only ($k=5$) | 0.49 [0.39, 0.60] | 0.66 [0.56, 0.76] | 0.04s | 0 | 0.00 | — |
| **B_static** | **Static Hybrid + Rerank ($k=8$)** | **0.69 [0.59, 0.78]** | **0.83 [0.74, 0.90]** | **2.00s** | **0** | **0.00** | — |
| **K_static_k10** | Static Hybrid + Rerank ($k=10$) | 0.70 [0.61, 0.80] | 0.84 [0.77, 0.91] | 1.83s | 0 | 0.00 | — |
| **C_llm_router** | LLM-based Adaptive Router | 0.59 [0.48, 0.69] | 0.76 [0.67, 0.84] | 4.53s | 458 | 1.84 | 0.19 |
| **H_heuristic** | Rule-based Heuristic (dev only) | 0.53 [0.43, 0.63] | 0.70 [0.61, 0.78] | 0.03s | 32 | 0.12 | 0.36 |
| **F_uncertain** | Always Decomposed Hybrid ($k=10$) | 0.70 [0.60, 0.79] | 0.83 [0.76, 0.89] | 4.35s | 248 | 1.00 | — |
| **G_multihop** | Always Decomposed Multi-Hop ($k=8$) | 0.66 [0.57, 0.76] | 0.80 [0.73, 0.88] | 9.14s | 248 | 1.00 | — |
| **E_oracle** | Oracle Route Upper Bound | 0.71 [0.61, 0.80] | 0.83 [0.76, 0.89] | 3.47s | 156 | 0.62 | 1.00 |

*Paired Difference vs. Static Hybrid (`B_static`):*
- **`A_vanilla` vs `B_static`:** Mean recall diff **-0.20** [95% CI: -0.30, -0.09] — 95% bootstrap CI strictly excludes zero (Hybrid significantly superior).
- **`C_llm_router` vs `B_static`:** Mean recall diff **-0.10** [95% CI: -0.18, -0.03] — 95% bootstrap CI strictly excludes zero (LLM router significantly underperforms).
- **`E_oracle` vs `B_static`:** Mean recall diff **+0.02** [95% CI: -0.02, +0.08] — difference includes zero (Static hybrid operates near the Oracle ceiling).

Detailed analysis, question-type stratifications, and cluster-robust bootstrap CIs are documented in [`reports/FINAL_RESULTS.md`](reports/FINAL_RESULTS.md).

---

## 2. Completed vs. Future Work

### Completed Deliverables
- **Curated Corpus v3:** 121 unique papers on the Hubble tension, 4,076 chunks, zero PDF parse errors. Verified against manifest [`corpus/manifests/atlasrag-corpus-v3.json`](corpus/manifests/atlasrag-corpus-v3.json) and documented in [`docs/CORPUS_V3_MANIFEST.md`](docs/CORPUS_V3_MANIFEST.md).
- **Benchmark v3 (`atlasrag-bench-v3`):** 64 questions across 30 test-split papers. Fully audited across 3 independent judge passes (95.0% stability agreement). Generator model `openai/gpt-oss-20b`, Judge model `openai/gpt-oss-120b` (strictly separated, zero self-judging). Maximum paper concentration is 12.5% (observed test-split distribution).
- **Full Experiment Matrix:** Baselines A, B, C, H, F, G, K, E executed and analyzed in `results/final_v3/` with a deterministic replication run for `B_static` in `results/final_v3_rerun/` (ranking stable, 0.000 recall drift).
- **Comprehensive Test Suite:** Portable unit and integration tests passing in pytest.

### Planned Future Work
- **Compass Router (Baseline D):** `CompassRouter` remains an unbuilt placeholder stub in `src/atlasrag/routers/compass.py`. Building a trained local classifier (extracting lightweight query embeddings and surface features trained exclusively on the 89-paper train split without test contamination) is deferred to future work. It was intentionally omitted from the evaluation matrix to uphold scientific integrity.

---

## 3. Quickstart

### Prerequisites & Setup
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
cp .env.example .env     # Add GROQ_API_KEY
```

Verify environment and run test suite:
```powershell
$env:PYTHONPATH = "src"
python scripts/check_env.py --ping
python -m pytest -q
```

---

## 4. End-to-End Reproduction Commands

All commands run under PowerShell with the venv active.

### 4.1 Corpus v3 Build & Verification
```powershell
$env:PYTHONPATH = "src"
$env:ATLAS_CONFIG = "configs/corpus_v3.yaml"

# 1. Fetch metadata and PDFs for curated corpus v3 (121 papers)
python scripts/build_curated_corpus_v3.py

# 2. Parse PDFs and build dense and BM25 index
python scripts/build_index.py

# 3. Verify corpus manifest integrity
python scripts/make_corpus_manifest.py --verify corpus/manifests/atlasrag-corpus-v3.json
```

### 4.2 Benchmark v3 Finalization & Oracle Labeling
```powershell
$env:PYTHONPATH = "src"
$env:ATLAS_CONFIG = "configs/corpus_v3.yaml"

# 1. Audit stability (3 passes with independent judge model)
python scripts/audit_stability.py --file data/bench/questions_v3_candidates.jsonl --out-dir data/bench/v3_stability --reps 2 --model openai/gpt-oss-120b --no-baseline --all

# 2. Finalize benchmark assembly (enforcing stability and test isolation)
python scripts/finalize_benchmark.py --file data/bench/questions_v3_candidates.jsonl --stability data/bench/v3_stability/audit_stability.json --benchmark-id atlasrag-bench-v3 --corpus-manifest corpus/manifests/atlasrag-corpus-v3.json --allow-llm-assisted

# 3. Label oracle routes
python scripts/label_oracle_v2.py --file data/bench/final/atlasrag-bench-v3/questions_final.jsonl --split test --status accepted

# 4. Refresh benchmark manifest hash
python scripts/refresh_benchmark_manifest.py --dir data/bench/final/atlasrag-bench-v3
```

### 4.3 Experiment Matrix Execution & Reporting
```powershell
$env:PYTHONPATH = "src"
$env:ATLAS_CONFIG = "configs/corpus_v3.yaml"

# Run all baselines (retrieval-only evaluation)
python scripts/run_experiment.py --group final_v3 --exp A --file data/bench/final/atlasrag-bench-v3/questions_final.jsonl --retrieval-only
python scripts/run_experiment.py --group final_v3 --exp B --file data/bench/final/atlasrag-bench-v3/questions_final.jsonl --retrieval-only
python scripts/run_experiment.py --group final_v3 --exp C --file data/bench/final/atlasrag-bench-v3/questions_final.jsonl --retrieval-only
python scripts/run_experiment.py --group final_v3 --exp H --file data/bench/final/atlasrag-bench-v3/questions_final.jsonl --retrieval-only
python scripts/run_experiment.py --group final_v3 --exp F --file data/bench/final/atlasrag-bench-v3/questions_final.jsonl --retrieval-only
python scripts/run_experiment.py --group final_v3 --exp G --file data/bench/final/atlasrag-bench-v3/questions_final.jsonl --retrieval-only
python scripts/run_experiment.py --group final_v3 --exp K --file data/bench/final/atlasrag-bench-v3/questions_final.jsonl --retrieval-only
python scripts/run_experiment.py --group final_v3 --exp E --file data/bench/final/atlasrag-bench-v3/questions_final.jsonl --retrieval-only

# Generate paired comparative report
python scripts/report.py --group final_v3 --file data/bench/final/atlasrag-bench-v3/questions_final.jsonl --paired-ref B
```

---

## 5. Repository Layout

```
configs/
  corpus_v3.yaml             # Frozen configuration for Corpus v3 paths & parameters
  default.yaml               # Default baseline configuration
corpus/manifests/
  atlasrag-corpus-v3.json    # Machine-readable corpus manifest (SHA256, paper metadata)
data/
  bench/final/atlasrag-bench-v3/
    questions_final.jsonl    # Frozen final benchmark (64 questions)
    benchmark_manifest.json  # Benchmark metadata, concentration metrics, audit summary
  index_v3/                  # Frozen BGE-small dense embeddings & chunk index
  processed_v3/              # Parsed chunks (4,076 chunks)
  raw_v3/                    # Curated metadata (121 papers) and PDFs
docs/
  CORPUS_V3_MANIFEST.md      # Human-readable Corpus v3 inventory and exclusion audit
reports/
  FINAL_RESULTS.md           # Full empirical evaluation report with stratified statistics
results/
  final_v3/                  # Run outputs for baselines A, B, C, H, F, G, K, E
  final_v3_rerun/            # Stability rerun outputs
scripts/                     # Build, benchmark, execution, and evaluation utilities
src/atlasrag/
  bench/                     # Benchmark schema, audit, generation, and reporting
  ingest/                    # arXiv fetching, PDF parsing, text chunking
  retrieval/                 # Dense embedder, BM25 index, cross-encoder reranker
  routers/                   # Fixed, heuristic, LLM, and oracle router implementations
  pipeline.py                # Unified execution pipeline for all strategies
tests/                       # Unit and integration tests
```

---

## 6. Operating Rules & Research Integrity

1. **Identical Pipelines:** All routers are evaluated using the identical retrieval and scoring pipeline (`pipeline.py`).
2. **Strict Paper-Level Split:** Zero questions in Benchmark v3 cite papers from the training split.
3. **Model Independence:** Benchmark generation and judge evaluation are executed on distinct models (`openai/gpt-oss-20b` vs `openai/gpt-oss-120b`).
4. **Honest Provenance:** Only human-reviewed questions carry `review:human`; all model-assisted items are marked `review:llm_assisted`.
5. **No Fabricated Baselines:** Unimplemented models (Compass) are documented as placeholders and excluded from empirical rankings.
