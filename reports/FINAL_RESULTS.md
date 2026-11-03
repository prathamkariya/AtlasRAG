# AtlasRAG evaluation report (Corpus v3, Benchmark v3), corrected 2026-11-03

This replaces the report dated 2026-10-24. Several conclusions in that report are withdrawn (section 8). Numbers in
this document were **recomputed from the committed result rows** in `results/final_v3/`; the retrieval runs
themselves were not re-executed in this review.

**Evidence labels used below**

- **[RECOMPUTED]** recomputed from committed rows and matches the earlier report.
- **[PARTIAL]** holds only under stated conditions.
- **[WITHDRAWN]** earlier claim, not supported by the data.
- **[NOT MEASURED]** never measured; any earlier statement about it is unsupported.

## 1. Scope

- Retrieval only (`retrieval_only=true`). Metrics are evidence-chunk recall and paper recall against gold chunk and
  paper IDs. Answer correctness and citation quality were not evaluated.
- Corpus v3: 121 papers, 4,076 chunks, one topic (Hubble tension). Benchmark v3: 64 accepted questions drawn from
  30 test-split papers (simple 30, multi_hop 23, temporal 7, chain 4).
- LLM: `openai/gpt-oss-20b` via Groq (free tier) for routing and decomposition. Embeddings `bge-small-en-v1.5`,
  reranker `ms-marco-MiniLM-L-6-v2`.
- No result here says anything about generated-answer quality, other corpora or larger corpora.

## 2. Strategy definitions

All experiments share one pipeline; only the strategy differs (`configs/corpus_v3.yaml`).

| Strategy | Hybrid | Rerank | Decompose (LLM) | Final k |
|---|---|---|---|---|
| VANILLA / SIMPLE (A) | no | no | no | 5 |
| STATIC (B) | yes | yes | no | 8 |
| STATIC_K10 (K) | yes | yes | no | 10 |
| MULTI_HOP (G) | yes | yes | yes | 8 |
| UNCERTAIN (F) | yes | yes | yes | 10 |

`SIMPLE` is identical to `VANILLA`. Any router that selects SIMPLE therefore selects the weakest retriever in the
table. This is a property of the strategy table, not of routing.

## 3. Results [RECOMPUTED]

Mean over 64 questions. "Logical" calls and tokens count what the system requested, independent of cache state.

| Experiment | Evidence recall | Paper recall | Logical LLM calls / query | Logical tokens / query |
|---|---|---|---|---|
| A vanilla (dense, k=5) | 0.492 | 0.656 | 0.00 | 0 |
| B static (k=8) | 0.688 | 0.828 | 0.00 | 0 |
| K static (k=10) | 0.703 | 0.836 | 0.00 | 0 |
| C LLM router | 0.586 | 0.758 | 1.84 | 458 |
| H heuristic (dev only) | 0.531 | 0.695 | 0.12 | 32 |
| F always UNCERTAIN | 0.695 | 0.828 | 1.00 | 248 |
| G always MULTI_HOP | 0.664 | 0.805 | 1.00 | 248 |
| E oracle (label-based, see section 6) | 0.711 | 0.828 | 0.62 | 156 |

By question type (evidence recall):

| Type | n | A | B | K | C | F | G |
|---|---|---|---|---|---|---|---|
| simple | 30 | 0.67 | 0.97 | 0.97 | 0.80 | 0.97 | 0.97 |
| multi_hop | 23 | 0.35 | 0.46 | 0.46 | 0.39 | 0.43 | 0.39 |
| temporal | 7 | 0.21 | 0.43 | 0.43 | 0.43 | 0.43 | 0.43 |
| chain | 4 | 0.50 | 0.38 | 0.62 | 0.38 | 0.62 | 0.38 |

Temporal (n = 7) and chain (n = 4) differences are not interpretable.

### Paired differences against B [RECOMPUTED]

Per-question recall difference (experiment minus B). 95% bootstrap CI resampling questions, and resampling whole
papers (a question is assigned to its first gold paper). Seven comparisons, no multiplicity correction.

| Experiment | Mean diff | CI (questions) | CI (papers) | Wins / ties / losses |
|---|---|---|---|---|
| A vanilla | −0.195 | [−0.297, −0.094] | [−0.266, −0.118] | 3 / 44 / 17 |
| H heuristic | −0.156 | [−0.250, −0.062] | [−0.233, −0.073] | 4 / 45 / 15 |
| C LLM router | −0.102 | [−0.180, −0.031] | [−0.158, −0.038] | 3 / 50 / 11 |
| G always MULTI_HOP | −0.023 | [−0.062, +0.023] | [−0.070, +0.022] | 3 / 55 / 6 |
| F always UNCERTAIN | +0.008 | [−0.039, +0.055] | [−0.030, +0.053] | 5 / 55 / 4 |
| K static k=10 | +0.016 | [0.000, +0.039] | [0.000, +0.042] | 2 / 62 / 0 |
| E oracle (label-based) | +0.023 | [−0.023, +0.078] | [−0.020, +0.073] | 7 / 53 / 4 |

## 4. What these results support

1. **[PARTIAL] Hybrid + rerank beats dense-only.** B exceeds A by 0.195 (CI excludes zero under both bootstraps).
   A to B changes BM25, reranking and k (5 to 8) together. There is no dense-k=8, dense+rerank or hybrid-without-rerank
   control, so the contribution of each component is **[NOT MEASURED]**.
2. **[RECOMPUTED] Decomposition showed no measurable gain.** F (decompose, k=10) scores 0.695, close to K
   (static, k=10) at 0.703. G is below B. The reported paired CIs for F, G and K against B include zero
   (K's lower bound is 0.000); this does not establish an improvement from decomposition. On multi_hop,
   decomposition is at or below static (F 0.43, G 0.39, B 0.46).
3. **[RECOMPUTED] The simple subset is saturated for the stronger static/decomposition controls.** B, K, F and G
   each score 0.97 on the 30 simple questions; C scores 0.80 and H scores 0.73. Question tokens overlap the gold
   chunk heavily (68% on average), so these questions provide limited signal for distinguishing the stronger
   retrieval strategies, but not for every router.
4. **[RECOMPUTED] No measured gain over B is established for K, F or G.** Each reported paired CI against B
   includes zero; K versus B is +0.016 with a lower CI bound of 0.000. This is not a formal equivalence test and
   does not prove the strategies are interchangeable. Choose k using measured latency and context budget once
   latency is measured under controlled conditions.

## 5. Why the LLM router (C) scored below B [RECOMPUTED]

Routes chosen by C:

| True type | Routed MULTI_HOP | Routed SIMPLE | Routed UNCERTAIN |
|---|---|---|---|
| simple (30) | 20 | 10 | 0 |
| multi_hop (23) | 23 | 0 | 0 |
| temporal (7) | 7 | 0 | 0 |
| chain (4) | 4 | 0 | 0 |

Decomposition of the 0.102 gap to B:

- **10 questions routed to SIMPLE** (all simple-type): C scores 0.50 on them, B scores 1.00. Contribution −0.078.
- **54 questions routed to MULTI_HOP:** C's results are identical to G's on every one. C scores 0.602, B 0.630 on
  these. Contribution −0.024.

So about three quarters of C's deficit comes from sending ten easy questions to the dense-only, no-rerank baseline.
That reflects how `SIMPLE` is defined (section 2). It does not show that routing by question text is impossible.
C also never emitted UNCERTAIN, and routed every multi-hop, temporal and chain question to a decomposing strategy.
The earlier statements that C "under-routes multi-hop questions to SIMPLE" and "selected MULTI_HOP or UNCERTAIN
only 4% of the time" are contradicted by these routes **[WITHDRAWN]**.

H (heuristic) routed 56 questions SIMPLE and 8 MULTI_HOP. It is a development stand-in, not a baseline.

## 6. Oracle (E): what it is and is not

**Definition used for the recorded run.** For each question, the cheapest strategy on the ladder
SIMPLE, MULTI_HOP, UNCERTAIN whose retrieval reaches recall 1.0; if none does, UNCERTAIN (27 of 64 questions).
Label counts: UNCERTAIN 28, SIMPLE 24, MULTI_HOP 12.

`UNCERTAIN` is overloaded: 27 questions receive it because no ladder strategy reaches recall 1.0; one further
question receives it because only the `UNCERTAIN` strategy reaches recall 1.0. The label therefore conflates
"requires the most expensive available strategy" with "no tested strategy fully retrieves the gold evidence."

Problems:

- **[WITHDRAWN] "Upper bound" / "B is within 2% of the oracle".** The ladder does not contain STATIC or
  STATIC_K10, so E is not an upper bound over the strategies that were run. On 4 questions B beats every ladder
  strategy. Taking the per-question best over the strategies that were run, mean recall is 0.734 (B, K, F, G) to
  0.750 (all seven non-oracle runs), a hindsight headroom of roughly 0.05 to 0.06 over B. That figure is selected on
  the test set, so it is optimistic as a router target, but it is not 0.02. The CI on E minus B reaches +0.078.
- **[PARTIAL] Reproducibility.** The E routes in `E_oracle.jsonl` match the `gold_route` labels at commit `3cca0da`
  on 64 of 64 questions. Commit `389cef4` removed `gold_route` from every question, so `run_experiment.py --exp E`
  selects zero questions at HEAD. See section 9.
- **Route accuracy.** The 19% figure for C (and 36% for H) is accuracy against those labels, 28 of which are
  UNCERTAIN, and 27 of those 28 are there only because retrieval fails for every ladder strategy. No router can
  predict that from question text.
  **[WITHDRAWN]** as a measure of routing quality. A valid definition needs labels that mean something a router can
  act on (for example, cheapest strategy within epsilon of best, over the full strategy set).

## 7. Benchmark quality problems

These affect every statement about multi_hop, temporal and chain questions.

1. **Review provenance.** 63 of 64 questions: `review:llm_assisted`; 1: `review:human`. Generator `gpt-oss-20b`,
   judge `gpt-oss-120b`, same model family. Three judge passes agree 95% of the time, which measures judge
   consistency, not correctness.
2. **Unreachable gold.** Under the oracle ladder, 27 of 64 questions are "insufficient": no strategy reaches full
   recall (multi_hop 20 of 23, temporal 4 of 7, chain 2 of 4, simple 1 of 30). This is distinct from the 28
   `UNCERTAIN` labels: one question is labeled `UNCERTAIN` because only that strategy reaches full recall.
   Seven questions have zero recall under every run strategy. B has zero recall on 12 questions (6 of them multi_hop).
3. **Sampled defects** (reviewer judgment, not adjudicated):
   - `multi_hop-81cd3cae` asks about "the first passage" and "the second passage", which a retrieval system cannot
     resolve.
   - `multi_hop-50549cd8` asks about cosmographic expansions and the transition redshift; one of its two gold chunks
     (`2608.28260v1::4`) is the introduction of an unrelated paper about no-go arguments for late-time solutions.
   - `multi_hop-c593c727` (the only human-reviewed question): B retrieved `2607.24443v2::20`, which describes the
     repeated high-redshift calculation directly; the gold chunk is `::23`. Recall counts this as a miss.
4. **Exact chunk-ID recall** penalizes valid alternative evidence and chunks that overlap the gold chunk.
5. **Size.** Roughly 34 questions can discriminate between strategies; subgroups have n = 7 and n = 4.

Consequence: low multi_hop recall (about 0.4 to 0.5 for every strategy) cannot be read as a retrieval or routing
failure until the gold sets are repaired. The earlier suggestion that multi-hop retrieval is the main opportunity
is **[WITHDRAWN]** pending that repair.

## 8. Latency, ranking stability and attribution

**Latency [WITHDRAWN as a comparison].** Recorded `latency_s` includes the client's own 2.1 s pacing sleeps between
provider requests, free-tier throttling and cache state, and was not isolated.
Evidence: F and G used identical decompositions on 64 of 64 questions (cache reuse) yet have median latencies of
4.35 s and 9.14 s; within F, simple questions have a median of 8.65 s and multi_hop 4.06 s; maximum single-query
latencies are 2,024.5 s (C), 450.5 s (F) and 320.0 s (G). Logical LLM calls and tokens (section 3) are reliable;
latency is not. The ">2x lower latency" claim is unsupported. A valid measurement needs a controlled cache policy, pacing excluded from the timed interval, and provider/LLM time reported separately
from local retrieval compute **[NOT MEASURED]**.

**Ranking stability [WITHDRAWN].** `results/final_v3_rerun/` contains only `B_static`, which is deterministic and
makes no LLM calls. Zero drift there shows retrieval is deterministic. It says nothing about the stability of
LLM-dependent runs (C, F, G, E), and a "ranking" over one experiment is vacuous. A real check reruns C, F and G under
a fresh `cache_namespace`.

**Attribution [NOT MEASURED].** "Dense retrieval fails on exact cosmological parameters and BM25 fixes it" has no
ablation behind it. The BM25 tokenizer is `\w+`, which splits "73.04" into "73" and "04".

## 9. Provenance and reproducibility

| Item | Finding |
|---|---|
| Run metadata `questions_hash` | `58ebacd6a9e8` for all `final_v3` runs |
| `questions_final.jsonl` at commits `b921d54`, `3cca0da` | hash `58ebacd6a9e8` (matches the runs) |
| `questions_final.jsonl` at commit `8ec0184` | empty file |
| `questions_final.jsonl` at HEAD (`389cef4` onward) | hash `b0144a062d1e` (matches current manifest) |
| Difference between `3cca0da` and HEAD | only the `gold_route` field, set to `null` on all 64 questions; IDs, questions, gold chunk IDs and `gold_route_v2` are identical |
| Stored recall vs recomputation | identical for all 512 result rows (8 experiments × 64) against current gold IDs |

This is a real provenance mismatch: the result metadata hash does not equal the current benchmark file hash.
The retrieval result rows nevertheless recompute identically against the current gold IDs because the reported
file change is confined to `gold_route`; question IDs, question text and gold chunk IDs are unchanged. Therefore
the retrieval metrics can be described as recomputed against the current gold IDs, but the original runs are
not exact-input reproductions from HEAD. The Oracle result and route-accuracy diagnostics depend on the removed
label field. To rerun E or reproduce those labels, extract the file at `3cca0da` (command in the README).
The benchmark manifest was regenerated on 2026-10-26 and reflects the HEAD file, so the "frozen" description
applies to questions and gold IDs, not to the removed `gold_route` field.

Other verified properties: corpus manifest hashes verified in tests; test suite 165 passed, 1 skipped at `2d35713`
(CI matrix Python 3.11 and 3.12); tests use fakes and do not load real models.

## 10. Corrections to earlier statements

| Earlier statement | Correction |
|---|---|
| Oracle is only 0.02 above static, routing headroom is negligible | Invalid. The oracle ladder excludes STATIC and STATIC_K10; hindsight headroom over B is roughly 0.05 to 0.06 and is selected on the test set |
| LLM router under-routes multi-hop questions to SIMPLE | Incorrect. 23 of 23 multi-hop questions went to MULTI_HOP |
| Router accuracy is 19% | Not meaningful against labels that tag unretrievable questions UNCERTAIN |
| `STATIC_K10` is best | Not demonstrated (+0.016, CI [0.000, 0.039]). Choose k by latency and context budget |
| Multi-hop is the biggest opportunity | Premature until gold quality is repaired |
| 159 tests pass | 165 passed, 1 skipped at `2d35713` |
| Static hybrid is a "decisive" winner over adaptive routing | Not shown. The strategy table has no complementary strategies and the benchmark is noisy |
| ">2x lower latency" | Unsupported (section 8) |
| Ranking stable across reruns | Vacuous (section 8) |
| Benchmark is "frozen, fully audited, high quality" | Questions and gold IDs are fixed; quality is LLM-assessed only (section 7) |

## 11. Open items before any result is cited as established

1. Add a hash guard that fails closed when a result's recorded question hash differs from the benchmark input;
   preserve the historical artifacts, and define a strategy table with a real cheap `SIMPLE` option before rerunning.
2. Add ablations: dense k=8, dense + rerank, hybrid without rerank.
3. Repair or re-review the non-simple gold sets by hand; report recall on the repaired subset.
4. Define routing labels over the full strategy set with an explicit cost tolerance; recompute route accuracy.
5. Rerun C, F and G under a fresh `cache_namespace`; report cache state explicitly, exclude pacing from timed
   intervals, and separate provider/LLM latency from local retrieval compute.
6. Evaluate generated answers and citations on a hand-verified question set.