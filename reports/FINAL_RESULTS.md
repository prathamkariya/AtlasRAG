# AtlasRAG Final Empirical Evaluation Report (Corpus v3 & Benchmark v3)

> **Document:** `reports/FINAL_RESULTS.md`
> **Evaluation Date:** October 24, 2026
> **Repository Commit:** `b921d54` (Branch: `finalization-v3`)
> **Corpus Manifest:** [`corpus/manifests/atlasrag-corpus-v3.json`](corpus/manifests/atlasrag-corpus-v3.json)
> **Benchmark Manifest:** [`data/bench/final/atlasrag-bench-v3/benchmark_manifest.json`](data/bench/final/atlasrag-bench-v3/benchmark_manifest.json)
> **Benchmark File:** [`data/bench/final/atlasrag-bench-v3/questions_final.jsonl`](data/bench/final/atlasrag-bench-v3/questions_final.jsonl)
> **Results Directory:** [`results/final_v3/`](results/final_v3/)

> [!IMPORTANT]
> **Evaluation Scope: Retrieval-Only Evaluation (`retrieval_only=true`)**
> All queries in this evaluation were evaluated strictly on evidence chunk recall and paper recall against curated gold passages (`answer: null`). Generative answer synthesis correctness was not evaluated, isolating retrieval performance directly.

---

## 1. Executive Summary & Research Question

**Primary Research Question:**
*Does adaptive, query-dependent routing (heuristic or LLM-based) improve retrieval accuracy and efficiency over static hybrid retrieval when navigating dense, highly technical scientific literature on the Hubble tension?*

**Core Finding:**
**No.** Static hybrid retrieval (`B_static`: Dense BGE-small + Lexical BM25, cross-encoder reranked to top-8) provides superior retrieval accuracy compared to adaptive routing, while incurring **zero LLM cost**, **zero token overhead**, and **more than 2x lower latency**.

Specifically:
1. **Static Hybrid (`B_static`)** achieves **0.69 evidence recall** [95% bootstrap CI: 0.59, 0.78] and **0.83 paper recall** [0.74, 0.90] (mean 0.828) at a median latency of **2.00s**, with **0 LLM calls** and **0 tokens**. Expanding context to top-10 (`K_static_k10`) yields **0.70 evidence recall** [0.61, 0.80] and **0.84 paper recall** [0.77, 0.91] (mean 0.836) at **1.83s** median latency.
2. **Adaptive LLM Routing (`C_llm_router`)** underperforms static hybrid by **-10.0% evidence recall** (0.59 vs 0.69; paired 95% bootstrap CI $[-0.18, -0.03]$ strictly excludes zero) and achieves **0.76 paper recall** [0.67, 0.84] (mean 0.758). The LLM router suffers from poor routing classification accuracy (**19%**), frequently under-routing multi-hop queries to simple single-passage dense retrieval, while adding 458 logical tokens and more than doubling median query latency to **4.53s**.
3. **Empirical Oracle Upper Bound (`E_oracle`)** achieves **0.71 evidence recall** [0.61, 0.80] and **0.83 paper recall** [0.76, 0.89] (mean 0.828). The paired difference between the Oracle and static hybrid is $+0.02$ [95% bootstrap CI: $-0.02, +0.08$], which includes zero. This demonstrates that a well-tuned static hybrid retrieval pipeline already operates within 2% of the theoretical upper bound of route selection on this corpus.
4. **Heuristic Routing (`H_heuristic_devonly`)** achieves **0.53 evidence recall** [0.43, 0.63] and **0.70 paper recall** [0.61, 0.78] (mean 0.695) with route accuracy of 36%, significantly below static hybrid (paired recall difference $-0.16$ [$-0.25, -0.06$] strictly excludes zero).
5. **Always-Decomposed Routing (`F_always_uncertain`)** achieves **0.70 evidence recall** [0.60, 0.79] and **0.83 paper recall** [0.76, 0.89], matching `K_static_k10` (+0.01 vs B; CI includes zero), but requires 248 logical tokens/query and 4.35s latency.

---

## 2. Frozen Corpus v3 Inventory & Curation

Corpus v3 was finalized and frozen following the planned additions and explicit single exclusion:

| Metric | Corpus v2 Baseline | Final Corpus v3 | Change |
|---|---|---|---|
| **Unique Papers** | 119 | **121** | +2 net (+3 added, -1 excluded) |
| **PDF Extraction Failures** | 0 | **0** | Clean parse across all 121 PDFs |
| **Total Chunks** | 3,905 | **4,076** | +171 chunks (+4.4%) |
| **Embedding Dimension** | 384 (`bge-small-en-v1.5`) | **384** (`bge-small-en-v1.5`) | Identical model |
| **Train Split Papers** | 87 (73.1%) | **89** (73.6%) | Zero leakage |
| **Test Split Papers** | 32 (26.9%) | **32** (26.4%) | Zero leakage |

### Curated Paper Details
- **Explicit Exclusion:** `2609.13266v1` (*Lemaitre Conference 2024*) was excluded due to relevance and multi-paper conference compilation structure.
- **Verified Additions:**
  1. `2510.23823v1`: *The Local Distance Network: A community consensus report on the measurement of the Hubble constant at 1% precision*.
  2. `2610.14781v1`: *TDCOSMO 2026 strong-lensing and stellar-kinematics constraints on H₀*.
  3. `2604.08530v1`: *Disentangling cosmic distance tensions with early and late dark energy*.
- **Documentation:** Full inventory, arXiv links, and dates are recorded in [`docs/CORPUS_V3_MANIFEST.md`](docs/CORPUS_V3_MANIFEST.md).
- **Integrity Verification:** Tested via [`tests/test_corpus_v3.py`](tests/test_corpus_v3.py).

---

## 3. Benchmark v3 Composition & Verification

The final evaluation benchmark (`atlasrag-bench-v3`) was finalized through strict multi-round quality and stability gates:

### Benchmark Summary Statistics
- **Total Evaluated Questions:** **64**
- **Test Set Paper Isolation:** 100% (all 64 questions drawn strictly from test split papers; 0 train paper leakage).
- **Unique Papers Represented:** 30 papers across the 32 test papers (93.8% coverage).
- **Paper Concentration:** Max paper share is **12.5%** (8/64 questions in any position) and **10.9%** (first position), well below the 20% concentration ceiling.
- **Question Typology Distribution:**
  - `simple` (single-passage factual/parameter): **30** (46.9%)
  - `multi_hop` (cross-paper comparative synthesis): **23** (35.9%)
  - `temporal` (longitudinal analysis across publications): **7** (10.9%)
  - `chain` (within-paper multi-section evidence): **4** (6.3%)
- **Review Provenance:**
  - `review:human`: **1** question (accepted pilot question `multi_hop-c593c727`).
  - `review:llm_assisted`: **63** questions.
  - Zero false human review attributions (Operating Rule 8).
- **Model Independence:**
  - Generator Model: `openai/gpt-oss-20b`
  - Judge Model: `openai/gpt-oss-120b`
  - Stability Judge Model: `openai/gpt-oss-120b`
  - Same-model generated and judged: **0 questions (False)**.
- **Judge Stability Audit:**
  - 3 independent evaluation passes per question (generation-time audit + 2 fresh repetitions).
  - Pairwise judge agreement: **95.0%**.
  - Questions audited: 70 candidate questions $\to$ 64 stable passes accepted into final benchmark (5 unstable rejected by judge, 1 rejected for duplicate gold set).

---

## 4. Empirical Evaluation Matrix

Retrieved chunks were evaluated strictly against gold passage chunk IDs and gold paper IDs.

### 4.1 Stratified Performance by Strategy & Question Type

> **Metrics and Accounting Notice:**
> - **Logical LLM Calls** and **Logical Tokens** reflect the query execution accounting in `llm.py`, counting logical inference passes independent of cache status.
> - Runs operated under the `default` cache namespace (`data/llm_cache/default/`).
> - Uncached provider API latency and monetary cost were not isolated per-query in the result logs; latency represents measured local execution latency in the test environment.

| Experiment | Strategy Description | Question Type | n | Evidence Recall [95% CI] | Paper Recall [95% CI] | Logical LLM Calls | Logical Tokens | Median Latency | p95 Latency | Route Accuracy |
|---|---|---|---|---|---|---|---|---|---|---|
| **A_vanilla** | Dense only, k=5 | ALL | 64 | 0.49 [0.39, 0.60] | 0.66 [0.56, 0.76] | 0.00 | 0 | 0.04s | 0.05s | — |
| | | simple | 30 | 0.67 [0.50, 0.83] | 0.80 [0.67, 0.93] | 0.00 | 0 | 0.03s | 0.04s | — |
| | | multi_hop | 23 | 0.35 [0.24, 0.46] | 0.50 [0.39, 0.61] | 0.00 | 0 | 0.04s | 0.05s | — |
| | | temporal | 7 | 0.21 [0.00, 0.50] | 0.36 [0.14, 0.64] | 0.00 | 0 | 0.04s | 0.05s | — |
| | | chain | 4 | 0.50 [0.00, 1.00] | 1.00 [1.00, 1.00] | 0.00 | 0 | 0.04s | 0.11s | — |
| **B_static** | Hybrid (Dense+BM25) + Rerank, k=8 | **ALL** | **64** | **0.69 [0.59, 0.78]** | **0.83 [0.74, 0.90]** | **0.00** | **0** | **2.00s** | **2.46s** | — |
| | | simple | 30 | 0.97 [0.90, 1.00] | 1.00 [1.00, 1.00] | 0.00 | 0 | 1.99s | 2.38s | — |
| | | multi_hop | 23 | 0.46 [0.33, 0.61] | 0.63 [0.52, 0.74] | 0.00 | 0 | 2.10s | 3.64s | — |
| | | temporal | 7 | 0.43 [0.14, 0.71] | 0.64 [0.29, 0.93] | 0.00 | 0 | 1.94s | 1.98s | — |
| | | chain | 4 | 0.38 [0.00, 0.75] | 1.00 [1.00, 1.00] | 0.00 | 0 | 1.90s | 1.94s | — |
| **K_static_k10** | Hybrid (Dense+BM25) + Rerank, k=10 | ALL | 64 | 0.70 [0.61, 0.80] | 0.84 [0.77, 0.91] | 0.00 | 0 | 1.83s | 2.12s | — |
| | | simple | 30 | 0.97 [0.90, 1.00] | 1.00 [1.00, 1.00] | 0.00 | 0 | 1.77s | 2.20s | — |
| | | multi_hop | 23 | 0.46 [0.33, 0.61] | 0.65 [0.52, 0.78] | 0.00 | 0 | 1.85s | 1.95s | — |
| | | temporal | 7 | 0.43 [0.14, 0.71] | 0.64 [0.29, 0.93] | 0.00 | 0 | 1.85s | 1.92s | — |
| | | chain | 4 | 0.62 [0.25, 1.00] | 1.00 [1.00, 1.00] | 0.00 | 0 | 1.84s | 1.90s | — |
| **C_llm_router** | LLM-based Adaptive Routing | ALL | 64 | 0.59 [0.48, 0.69] | 0.76 [0.67, 0.84] | 1.84 | 458 | 4.53s | 6.81s | 0.19 |
| | | simple | 30 | 0.80 [0.63, 0.93] | 0.90 [0.80, 1.00] | 1.67 | 396 | 4.23s | 6.32s | 0.30 |
| | | multi_hop | 23 | 0.39 [0.28, 0.50] | 0.54 [0.41, 0.65] | 2.00 | 522 | 4.92s | 27.17s | 0.04 |
| | | temporal | 7 | 0.43 [0.14, 0.71] | 0.71 [0.43, 0.93] | 2.00 | 495 | 4.50s | 5.65s | 0.29 |
| | | chain | 4 | 0.38 [0.00, 0.75] | 1.00 [1.00, 1.00] | 2.00 | 486 | 5.64s | 6.13s | 0.00 |
| **H_heuristic** | Rule-based Heuristic Routing | ALL | 64 | 0.53 [0.43, 0.63] | 0.70 [0.61, 0.78] | 0.12 | 32 | 0.03s | 2.98s | 0.36 |
| | | simple | 30 | 0.73 [0.57, 0.87] | 0.87 [0.73, 0.97] | 0.17 | 41 | 0.02s | 2.96s | 0.63 |
| | | multi_hop | 23 | 0.37 [0.26, 0.48] | 0.50 [0.39, 0.61] | 0.04 | 14 | 0.03s | 0.04s | 0.04 |
| | | temporal | 7 | 0.21 [0.00, 0.50] | 0.43 [0.21, 0.64] | 0.29 | 65 | 0.03s | 3.85s | 0.14 |
| | | chain | 4 | 0.50 [0.00, 1.00] | 1.00 [1.00, 1.00] | 0.00 | 0 | 0.03s | 0.03s | 0.50 |
| **F_uncertain** | Always Decomposed Hybrid, k=10 | ALL | 64 | 0.70 [0.60, 0.79] | 0.83 [0.76, 0.89] | 1.00 | 248 | 4.35s | 14.25s | — |
| | | simple | 30 | 0.97 [0.90, 1.00] | 1.00 [1.00, 1.00] | 1.00 | 233 | 8.65s | 12.83s | — |
| | | multi_hop | 23 | 0.43 [0.33, 0.54] | 0.61 [0.52, 0.72] | 1.00 | 267 | 4.06s | 21.18s | — |
| | | temporal | 7 | 0.43 [0.14, 0.71] | 0.71 [0.43, 0.93] | 1.00 | 247 | 3.18s | 4.15s | — |
| | | chain | 4 | 0.62 [0.50, 0.88] | 1.00 [1.00, 1.00] | 1.00 | 247 | 4.13s | 4.67s | — |
| **G_multihop** | Always Decomposed Multi-Hop, k=8 | ALL | 64 | 0.66 [0.57, 0.76] | 0.80 [0.73, 0.88] | 1.00 | 248 | 9.14s | 13.81s | — |
| | | simple | 30 | 0.97 [0.90, 1.00] | 1.00 [1.00, 1.00] | 1.00 | 233 | 9.64s | 13.13s | — |
| | | multi_hop | 23 | 0.39 [0.28, 0.50] | 0.54 [0.43, 0.67] | 1.00 | 267 | 4.63s | 13.82s | — |
| | | temporal | 7 | 0.43 [0.14, 0.71] | 0.71 [0.43, 0.93] | 1.00 | 247 | 9.74s | 11.30s | — |
| | | chain | 4 | 0.38 [0.00, 0.75] | 1.00 [1.00, 1.00] | 1.00 | 247 | 11.72s | 13.59s | — |
| **E_oracle** | Oracle Route Upper Bound | ALL | 64 | 0.71 [0.61, 0.80] | 0.83 [0.76, 0.89] | 0.62 | 156 | 3.47s | 13.12s | 1.00 |
| | | simple | 30 | 0.97 [0.90, 1.00] | 1.00 [1.00, 1.00] | 0.33 | 72 | 0.10s | 12.65s | 1.00 |
| | | multi_hop | 23 | 0.43 [0.33, 0.54] | 0.61 [0.52, 0.72] | 0.96 | 254 | 3.94s | 14.79s | 1.00 |
| | | temporal | 7 | 0.50 [0.14, 0.86] | 0.71 [0.43, 0.93] | 0.86 | 213 | 3.44s | 4.26s | 1.00 |
| | | chain | 4 | 0.75 [0.50, 1.00] | 1.00 [1.00, 1.00] | 0.50 | 121 | 1.87s | 4.61s | 1.00 |

*(Note: Compass `D` is documented as an unbuilt placeholder and was intentionally not run to preserve scientific honesty, per Rule 9).*

---

### 4.2 Paired Differences vs. Reference Static Hybrid (`B_static`)

To account for inter-paper correlation and test question difficulty, paired differences ($Exp - B$) were computed with both unclustered bootstrap CIs (resampling questions) and cluster-robust bootstrap CIs (resampling whole papers):

| Experiment | Comparison | n | Mean Recall Diff | 95% CI (Question) | 95% CI (Paper Cluster) | Wins / Ties / Losses | Statistically Significant vs B? |
|---|---|---|---|---|---|---|---|
| **A_vanilla** | A vs B | 64 | **-0.20** | [-0.30, -0.09] | [-0.27, -0.12] | 3 / 44 / 17 | **Yes (CI strictly excludes zero; B superior)** |
| **C_llm_router** | C vs B | 64 | **-0.10** | [-0.18, -0.03] | [-0.16, -0.04] | 3 / 50 / 11 | **Yes (CI strictly excludes zero; B superior)** |
| **H_heuristic** | H vs B | 64 | **-0.16** | [-0.25, -0.06] | [-0.23, -0.07] | 4 / 45 / 15 | **Yes (CI strictly excludes zero; B superior)** |
| **G_multihop** | G vs B | 64 | **-0.02** | [-0.06, +0.02] | [-0.07, +0.02] | 3 / 55 / 6 | No (CI includes zero) |
| **F_uncertain** | F vs B | 64 | **+0.01** | [-0.04, +0.05] | [-0.03, +0.05] | 5 / 55 / 4 | No (CI includes zero) |
| **K_static_k10**| K vs B | 64 | **+0.02** | [+0.00, +0.04] | [+0.00, +0.04] | 2 / 62 / 0 | Marginal (+2 wins on chain/temporal) |
| **E_oracle** | E vs B | 64 | **+0.02** | [-0.02, +0.08] | [-0.02, +0.07] | 7 / 53 / 4 | No (CI includes zero) |

---

## 5. Ranking Stability & Reproducibility Check

A replication run of `B_static` was executed in a distinct results namespace (`results/final_v3_rerun/`):
- **Scope:** Ranking replication was evaluated specifically for `B_static` (not a full rerun of all 8 baselines).
- **Absolute Mean Recall Difference:** **0.000** (identical metric reproduction).
- **Ranking Stability:** `ranking_stable: True`.
- **System Stability:** Verified deterministic retrieval pipeline across runs.

---

## 6. Key Scientific & Engineering Conclusions

1. **Static Hybrid is the Optimal Production Strategy:**
   Dense retrieval alone (`A_vanilla`) fails on exact numerical cosmological parameters ($H_0$, $N_{eff}$, $\sigma_8$, $S_8$), achieving only 49% evidence recall. Adding BM25 lexical retrieval and a cross-encoder reranker (`B_static`) boosts evidence recall by **+20 points** (0.69) without requiring any generative LLM inference.
2. **Adaptive LLM Routing Fails Under Realistic Distribution:**
   Classifying query complexity from question text alone is an ill-posed task for current LLMs in specialized astrophysics:
   - On `multi_hop` questions requiring synthesis across two papers, the LLM router only selected `MULTI_HOP` or `UNCERTAIN` routes 4% of the time, defaulting to `SIMPLE` and causing recall to drop from 0.46 to 0.39.
   - On `simple` questions, it frequently over-routed to multi-hop decomposition, degrading recall from 0.97 to 0.80 and adding 4.2s of needless latency.
3. **The Ceiling of Route Optimization is Narrow:**
   The Oracle router (`E_oracle`) with perfect hindsight knowledge of which pipeline tier succeeds achieves 0.71 evidence recall—only 0.02 higher than `B_static`. Because `B_static` already retrieves 8 passages with cross-encoder precision, dynamic routing offers negligible margin for improvement while introducing substantial fragility, cost, and latency.

---

## 7. Known Limitations

1. **Compass Baseline (D):** Compass was conceived in earlier design documents as a lightweight local classifier. Because an honest, leak-free, trained classifier does not exist in the codebase today, it is properly documented as an unbuilt placeholder and was omitted from empirical tables to prevent fabrication.
2. **Benchmark Scale:** The final benchmark contains 64 high-quality, 3-run stability-audited questions across 30 test-split papers. While sufficient for statistical separation of primary baselines (where 95% bootstrap CIs strictly exclude zero), sub-group statistical power for smaller topologies (`chain`: $n=4$, `temporal`: $n=7$) has wider confidence intervals.
3. **Retrieval-Only Scope:** The evaluation evaluates evidence and paper recall against gold passages. Generative answer correctness was not evaluated.
4. **Decomposition Cache Sensitivity:** Decompositions require strict prompt adherence; unparseable JSON from small models can degrade fallback subqueries.

---

## 8. Exact Reproduction Commands

All commands below have been audited against the actual argparse implementations in `scripts/`:

```powershell
# Set environment
$env:PYTHONPATH = "src"
$env:ATLAS_CONFIG = "configs/corpus_v3.yaml"

# 1. Corpus build & index
python scripts/build_curated_corpus_v3.py
python scripts/build_index.py
python scripts/make_corpus_manifest.py --verify corpus/manifests/atlasrag-corpus-v3.json

# 2. Stability audit (3 judge runs)
python scripts/audit_stability.py --file data/bench/questions_v3_candidates.jsonl --out-dir data/bench/v3_stability --reps 2 --model openai/gpt-oss-120b --no-baseline --include-validation --all

# 3. Finalize benchmark
python scripts/finalize_benchmark.py --file data/bench/questions_v3_candidates.jsonl --stability data/bench/v3_stability/audit_stability.json --benchmark-id atlasrag-bench-v3 --corpus-manifest corpus/manifests/atlasrag-corpus-v3.json --allow-llm-assisted

# 4. Label oracle routes
python scripts/label_oracle_v2.py --file data/bench/final/atlasrag-bench-v3/questions_final.jsonl --split test --status accepted

# 5. Refresh benchmark manifest hash
python scripts/refresh_benchmark_manifest.py --dir data/bench/final/atlasrag-bench-v3

# 6. Run experiment matrix (retrieval-only)
python scripts/run_experiment.py --group final_v3 --exp A --file data/bench/final/atlasrag-bench-v3/questions_final.jsonl --retrieval-only
python scripts/run_experiment.py --group final_v3 --exp B --file data/bench/final/atlasrag-bench-v3/questions_final.jsonl --retrieval-only
python scripts/run_experiment.py --group final_v3 --exp C --file data/bench/final/atlasrag-bench-v3/questions_final.jsonl --retrieval-only
python scripts/run_experiment.py --group final_v3 --exp H --file data/bench/final/atlasrag-bench-v3/questions_final.jsonl --retrieval-only
python scripts/run_experiment.py --group final_v3 --exp F --file data/bench/final/atlasrag-bench-v3/questions_final.jsonl --retrieval-only
python scripts/run_experiment.py --group final_v3 --exp G --file data/bench/final/atlasrag-bench-v3/questions_final.jsonl --retrieval-only
python scripts/run_experiment.py --group final_v3 --exp K --file data/bench/final/atlasrag-bench-v3/questions_final.jsonl --retrieval-only
python scripts/run_experiment.py --group final_v3 --exp E --file data/bench/final/atlasrag-bench-v3/questions_final.jsonl --retrieval-only

# 7. Generate paired comparative report
python scripts/report.py --group final_v3 --file data/bench/final/atlasrag-bench-v3/questions_final.jsonl --paired-ref B
```
