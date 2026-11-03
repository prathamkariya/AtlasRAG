# AtlasRAG

A retrieval-augmented generation (RAG) system over astrophysics papers on the Hubble tension, with a configurable
retrieval pipeline, several query-routing strategies, and an evaluation harness.

**Status (2026-11-03):** the retrieval stack, API and evaluation tooling are built and tested. The routing
*study* is incomplete: the benchmark has known quality problems and some earlier conclusions have been withdrawn.
Read [`reports/FINAL_RESULTS.md`](reports/FINAL_RESULTS.md) before citing any number from this repository.

> [!IMPORTANT]
> **Scope of every result here.** Retrieval only (`retrieval_only=true`): evidence-chunk recall and paper recall
> against gold passages. Answer correctness and citation quality were **not** evaluated. One narrow-topic corpus,
> 64 questions from 30 papers. Results do not generalize to other corpora or to answer quality.

---

## 1. What is built

| Component | State |
|---|---|
| Ingestion: arXiv fetch, PyMuPDF parsing, section-aware chunking | Working |
| Corpus v3: 121 papers, 4,076 chunks, manifest with hashes, paper-level train/test split (89 / 32 papers) | Working; manifest verified in tests |
| Retrieval: BGE-small dense + BM25 + RRF fusion + MiniLM cross-encoder rerank | Working |
| Strategy table (`configs/*.yaml`) shared by every experiment | Working |
| Routers: fixed, heuristic, LLM, oracle, escalating | Implemented |
| Compass (trained router) | **Not built.** Placeholder only |
| LLM client: disk cache, bounded retries, rate-limit handling, token accounting | Working |
| FastAPI service (`/health`, `/routers`, `/ask`) | Working prototype, not production-hardened |
| Benchmark tooling: generation, support audit, stability audit, finalization gates | Working |
| Tests and CI (Python 3.11 / 3.12, ruff `F` rules) | Passing; 165 passed, 1 skipped at commit `2d35713` |
| Frontend | Not started |
| Answer-quality and citation evaluation | Not started |

## 2. What the evidence supports

All figures are recomputed from the committed rows in `results/final_v3/` (retrieval only, n = 64).
Full table, confidence intervals and caveats are in [`reports/FINAL_RESULTS.md`](reports/FINAL_RESULTS.md).

| Strategy | Evidence recall | Paper recall | Logical LLM calls / query |
|---|---|---|---|
| A dense only, k=5 | 0.492 | 0.656 | 0 |
| B hybrid + rerank, k=8 | 0.688 | 0.828 | 0 |
| K hybrid + rerank, k=10 | 0.703 | 0.836 | 0 |
| C LLM router | 0.586 | 0.758 | 1.84 |
| F always decompose, k=10 | 0.695 | 0.828 | 1.00 |
| G always decompose, k=8 | 0.664 | 0.805 | 1.00 |

Supported:

- Hybrid retrieval with reranking beats the dense-only baseline (paired recall difference vs B: −0.195, 95% CI
  [−0.297, −0.094]). This comparison changes three things at once (BM25, reranking, k from 5 to 8); the contribution
  of each is **not measured**.
- Query decomposition showed no measurable gain over static retrieval in this setup (F−B +0.008, G−B −0.023, both CIs
  include zero).
- The LLM router (C) scored below B by 0.102 (95% CI [−0.180, −0.031]). Most of that gap comes from the
  `SIMPLE` strategy, which is the weak dense-only baseline, not from misclassification of multi-hop questions.
  See the report, section 5.
- The static and decomposition controls B, K, F and G each score 0.97 on the simple subset. This saturation does
  **not** apply to every router: C scores 0.80 and H scores 0.73 on those questions.

**Provenance caveat:** the `final_v3` run metadata records `questions_hash=58ebacd6a9e8`, while the current
`questions_final.jsonl` has hash `b0144a062d1e`. The only reported content change between those revisions is
`gold_route` being set to null; question IDs, question text and gold chunk IDs are unchanged. Recomputing all
512 stored recall rows against the current gold IDs reproduces the stored recall values, but this is still a
run-input hash mismatch. The results are not exact-input reproductions from the current HEAD file. The Oracle
run can be rerun only with the separately pinned v1-label sidecar described below; route-accuracy diagnostics still
need explicit sidecar-aware handling. See the report, sections 6 and 9.

## 3. Withdrawn or unverified claims

Earlier versions of this README and the results report made the claims below. They are **withdrawn** and must not
be cited.

| Earlier claim | Status |
|---|---|
| Static hybrid is within 2% of the oracle, so routing has no headroom | Withdrawn. The oracle's strategy ladder excludes `STATIC` and `STATIC_K10`, so it is not an upper bound |
| The LLM router under-routes multi-hop questions to SIMPLE | Incorrect. It routed 23 of 23 multi-hop questions to MULTI_HOP |
| LLM router route accuracy is 19% | Not meaningful. The target labels mark unretrievable questions as UNCERTAIN, which no router can predict |
| `STATIC_K10` is the best strategy | Not demonstrated (K−B +0.016, CI [0.000, 0.039]). Choose k by latency and context budget |
| Multi-hop retrieval is the main opportunity | Premature. Benchmark gold for multi-hop questions must be repaired first |
| BM25 fixes dense retrieval's failures on exact parameter values | Untested. No ablation separates BM25 from reranking and k |
| ">2x lower latency than the LLM router" | Unsupported. Recorded latencies are dominated by rate-limit pacing and environment noise |
| Ranking stability verified by rerun | Vacuous. Only the deterministic, LLM-free `B_static` was rerun |

## 4. Known limitations of the benchmark

- 63 of 64 questions were reviewed by an LLM only; 1 was reviewed by a human. Generator (`gpt-oss-20b`) and judge
  (`gpt-oss-120b`) are the same model family.
- Many multi-hop gold sets are unreliable. 20 of 23 multi-hop questions cannot be fully covered by any strategy in the
  oracle ladder, and sampled failures include a question that refers to "the first passage" and gold chunks from
  papers unrelated to the question.
- The 34 non-simple questions (multi-hop, temporal and chain) are the only subset with meaningful potential to
  discriminate more complex retrieval behavior. Their gold sets are also the least reliable, and the temporal
  and chain subgroups are tiny (n = 7 and n = 4). Treat their recall comparisons as diagnostic, not as a ranking.
- Corpus v3 is one narrow topic. Nothing here says how the findings transfer.

## 5. Direction

The research framing (can a learned router approximate an oracle?) is being retired. The project is moving to an
application: a hybrid retrieval engine with a lightweight task-aware router, evaluated on **answer and citation
correctness**. Rule: the router becomes part of the default pipeline only if it beats a single universal prompt on
a manually verified question set. Otherwise the universal prompt stays.

Planned order:

1. Correct the record (this document and report), add a hash guard that rejects result/benchmark input mismatches,
   and perform repository cleanup.
2. Hand-verified evaluation set of about 40 questions, with expected answers and supporting passages.
3. Retrieval ablations: dense k=8, hybrid without rerank, and a genuine cheap `SIMPLE` strategy.
4. Router with four intent categories, evaluated against the universal-prompt baseline.
5. API hardening (input limits, timeouts, real readiness), request-level logging, minimal UI, Docker.

Compass training is deferred. The research code and the historical results stay in the repository.

---

## 6. Quickstart

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
cp .env.example .env     # add GROQ_API_KEY
$env:PYTHONPATH = "src"
python scripts/check_env.py --ping
python -m pytest -q
```

PDFs are not tracked. Run `scripts/refetch_pdfs.py` before rebuilding a corpus locally.

## 7. Reproducing the experiments

Run under PowerShell with the venv active.

```powershell
$env:PYTHONPATH = "src"
$env:ATLAS_CONFIG = "configs/corpus_v3.yaml"

# Corpus and index
python scripts/build_curated_corpus_v3.py
python scripts/build_index.py
python scripts/make_corpus_manifest.py --verify corpus/manifests/atlasrag-corpus-v3.json

# Experiments A, B, C, H, F, G, K (retrieval only)
$Q = "data/bench/final/atlasrag-bench-v3/questions_final.jsonl"
foreach ($e in "A","B","C","H","F","G","K") {
  python scripts/run_experiment.py --group final_v3 --exp $e --file $Q --retrieval-only
}

# Report with paired differences against B
python scripts/report.py --group final_v3 --file $Q --paired-ref B
```

**Experiment E (oracle).** Commit `389cef4` removed `gold_route` from all 64 questions. The v1 labels used by the
recorded E run are therefore pinned separately in
`data/bench/final/atlasrag-bench-v3/oracle_v1_labels.json`, restored from commit `3cca0da` without changing the
benchmark hash. Rerun E with:

```powershell
python scripts/run_experiment.py --group final_v3_e_repro --exp E --file $Q --retrieval-only `
  --oracle-labels data/bench/final/atlasrag-bench-v3/oracle_v1_labels.json
```

E remains a label-based diagnostic, not an upper bound (see the report).

## 8. Repository layout

```
configs/        corpus and strategy configuration (default.yaml, corpus_v2.yaml, corpus_v3.yaml)
corpus/         corpus manifests (SHA-256 of PDFs, chunks, metadata)
data/           metadata, processed chunks, benchmark files, LLM cache (PDFs and indexes are not tracked)
docs/           current corpus documentation
reports/        FINAL_RESULTS.md, the corrected evaluation report
results/        per-experiment outputs: run1/ (early), final_v3/, final_v3_rerun/ (B only)
audit/          repository audit notes, frozen hashes, and archived planning material under audit/archive/
scripts/        build, benchmark, experiment and reporting entry points
src/atlasrag/   ingest/, retrieval/, routers/, bench/, api/, pipeline.py, llm.py
tests/          unit and integration tests (fakes only; no real-model test)
```
