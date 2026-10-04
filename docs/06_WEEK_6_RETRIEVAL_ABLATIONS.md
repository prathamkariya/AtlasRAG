# AtlasRAG — Week 6: Retrieval Ablations & Retrieval-System Analysis

## 1. Purpose

Week 6 isolates the retrieval stack after benchmark/routing work is stable enough to study.

The current architecture is:

```text
Question
   |
   +--> Dense Retrieval
   |
   +--> BM25
          |
          v
      Hybrid / RRF
          |
          v
       Reranker
          |
          v
      Final evidence
```

The baseline uses:

```text
Embedding:
    BAAI/bge-small-en-v1.5

Dense k:
    20

BM25 k:
    20

RRF k:
    60

Reranker:
    cross-encoder/ms-marco-MiniLM-L-6-v2

Chunking:
    max_chars = 1800
    overlap_chars = 200
    min_chars = 200
```

The research question is:

> Which retrieval components and configuration choices materially affect evidence coverage, latency, and robustness, and how do those effects interact with adaptive routing?

The core rule is:

```text
change one controlled variable at a time
```

unless a deliberately designed interaction experiment is being run.

---

## 2. Why this phase exists

Historical Run 1 already showed:

```text
A Vanilla       0.52
B Static        0.63
C LLM Router    0.70
E Oracle        0.76
F Always Strong 0.76
K Static K10    0.65
```

These results show that retrieval configuration matters.

However, changing the retrieval stack during benchmark construction would also change:

```text
gold-evidence reachability
Oracle labels
candidate pairing
question generation
Compass supervision
```

Therefore retrieval changes must now be treated as explicit ablations.

Do not silently replace the baseline.

---

## 3. Frozen artifacts

Preserve:

```text
data/bench/questions.jsonl
data/bench/questions_v1_frozen.jsonl
results/run1/
```

Also preserve the declared benchmark-v2 version used for the experiment.

Never overwrite Run 1.

Never evaluate one retrieval variant with a different benchmark version and silently compare it with another.

---

## 4. Shared-pipeline rule

All retrieval variants should use the same:

```text
corpus
chunk corpus
evaluation implementation
question set
metric implementation
```

and, where the ablation permits:

```text same router
same final-k
same candidate-depth policy
```

The point is to isolate the retrieval variable.

Avoid duplicating retrieval logic into separate scripts when the shared pipeline already supports the variation.

---

## 5. Baseline retrieval

The baseline retrieval stack is conceptually:

```text
question
   |
   +--> dense retrieval
   |
   +--> BM25
          |
          v
      RRF / hybrid fusion
          |
          v
       cross-encoder
          |
          v
       final evidence
```

Dense retrieval captures semantic similarity.

BM25 captures lexical overlap and exact scientific identifiers.

Reranking improves ordering among candidates.

The final-k stage determines how much evidence is actually returned.

---

## 6. Dense-only ablation

Run:

```text
question
→ dense retrieval
→ final evidence
```

This provides a clean comparison against hybrid retrieval.

Purpose:

```text measure the contribution of semantic retrieval alone
```

Use the existing Vanilla/dense implementation where possible rather than creating a second implementation.

---

## 7. BM25-only ablation

Run:

```text
question
→ BM25
→ final evidence
```

Scientific papers contain many exact identifiers:

```text H0
YHe
ΔNeff
DESI
BAO
ΛCDM
Ωm
```

BM25 may recover exact terminology that dense retrieval ranks poorly.

This ablation measures how much of the benchmark depends on lexical matching.

---

## 8. Hybrid ablation

Compare:

```text dense-only
BM25-only
dense + BM25
```

with all other settings fixed.

This answers:

```text Does combining semantic and lexical retrieval improve evidence coverage?
```

Do not tune fusion before establishing whether fusion itself helps.

---

## 9. RRF / fusion

The baseline includes:

```yaml
rrf_k: 60
```

Verify how the actual repository implements RRF before interpreting this as a standard RRF parameter.

Do not assume notation from an external implementation exactly matches the local code.

A later experiment can vary the fusion parameter after the basic hybrid contribution is known.

---

## 10. Reranker ablation

The current reranker is:

```text
cross-encoder/ms-marco-MiniLM-L-6-v2
```

The key controlled comparison is:

```text hybrid without reranker
vs
hybrid + reranker
```

Hold fixed:

```text embedding
dense_k
BM25_k
fusion
final_k
```

Measure:

```text evidence recall
latency
reranking cost
```

This establishes whether the reranker is actually worth its compute cost on the scientific corpus.

---

## 11. Candidate depth

Current baseline:

```text dense_k = 20
BM25_k = 20
```

Candidate depth controls how much material reaches fusion/reranking.

A gold chunk that never enters the candidate pool cannot be recovered by the reranker.

Potential development sweep:

```text 5
10
20
40
80
```

The exact grid can be changed based on corpus size and runtime.

Do not maximize k automatically.

The goal is:

```text evidence recall
vs
candidate-processing cost
```

---

## 12. Dense-k sensitivity

Vary only:

```text dense_k
```

Keep:

```text BM25_k
fusion
reranker
final_k
```

fixed.

For each value report:

```text evidence recall
paper recall
p50 latency
p95 latency
```

This diagnoses whether failures are caused by an insufficient semantic candidate pool.

---

## 13. BM25-k sensitivity

Vary only:

```text BM25_k
```

and preserve the rest.

This is especially useful for questions involving:

```text parameter names
survey names
equations
acronyms
numeric identifiers
```

Do not infer from generic language-only questions that BM25 contributes little.

---

## 14. Final-k sensitivity

Candidate depth and final-k are different.

```text candidate_k:
    how many chunks enter downstream processing

final_k:
    how many chunks are ultimately returned
```

Potential final-k development sweep:

```text 3
5
8
10
15
```

Measure:

```text evidence recall
latency
```

A larger final-k may improve recall but also increases downstream context size and possible distraction.

---

## 15. Why final-k matters

A gold chunk may:

```text enter the candidate pool
→ survive fusion
→ survive reranking
→ still be removed by final-k
```

That is a different failure from:

```text gold chunk never retrieved at all
```

Stage-by-stage analysis should distinguish these.

---

## 16. Embedding-model ablation

Current baseline:

```text BAAI/bge-small-en-v1.5
```

The embedding model should be changed only as a controlled ablation.

Use:

```text same corpus
same chunks
same retrieval configuration
same benchmark
same metric
```

and replace only the embedding model.

The exact alternative must be selected deliberately and recorded with:

```text model name
revision
embedding dimension
license
memory requirements
local inference behavior
```

---

## 17. Rebuild the index for every embedding model

Never reuse:

```text BGE-small vectors
```

as though they belong to another model.

Each embedding model needs a distinct index artifact.

Conceptually:

```text data/index_bge_small
data/index_embedding_variant_1
data/index_embedding_variant_2
```

The exact paths can follow the repository.

---

## 18. Why embeddings have unusually large downstream impact

Embeddings affect:

```text dense retrieval
benchmark recall
multi-hop pair sourcing
temporal pair sourcing
Oracle outcomes
question sufficiency
```

If a retrieval model changes materially, old Oracle labels may no longer describe the new retrieval stack.

This must be acknowledged in later routing experiments.

---

## 19. Chunking is also a retrieval variable

Current chunking:

```text max_chars = 1800
overlap_chars = 200
min_chars = 200
```

Chunking affects:

```text semantic coherence
retrieval granularity
BM25 matching
reranker behavior
gold-evidence reachability
```

Therefore chunk size and overlap should be separate ablations.

---

## 20. Historical chunking bug

A real bug involving an undersized final chunk was fixed using:

```python
if len(chunks)>1 and len(chunks[-1])<min_chars:
    last=chunks.pop()
    chunks[-1]+="\n\n"+last
```

The successful build afterward was:

```text
30 papers -> 1239 chunks (0 failed)
```

Do not regress this implementation during chunking studies.

Every new chunking setting must still pass the existing chunking tests.

---

## 21. Chunk-size sweep

Vary only:

```text max_chars
```

Possible development values:

```text 1200
1800
2400
3000
```

The exact grid is not mandatory.

The questions are:

```text Are chunks too small to preserve context?
Are chunks too large to retrieve precisely?
```

Use the actual corpus to interpret the result.

---

## 22. Overlap sweep

The baseline overlap is:

```text 200 characters
```

Potential development values:

```text 0
100
200
300
```

Hold max_chars fixed.

Measure:

```text evidence recall
paper recall
index/chunk count
latency
```

More overlap can preserve context while also increasing redundancy and corpus size.

---

## 23. Do not change chunk size and overlap together initially

Start with:

```text fixed overlap
→ vary max_chars
```

then:

```text fixed max_chars
→ vary overlap
```

A joint chunk-size/overlap study can come later if the main effects justify it.

---

## 24. Scientific chunk-quality inspection

Numeric retrieval scores are not enough.

Inspect sample chunks for:

```text equations preserved
tables coherent
units retained
qualifiers retained
result + uncertainty kept together
definitions not separated from their quantities
```

Scientific evidence may be unusually sensitive to chunk boundaries.

---

## 25. Table-heavy and equation-heavy cases

Where the benchmark contains them, create diagnostic subsets for:

```text table evidence
equation evidence
parameter-symbol evidence
numerical constraints
```

Then compare ablations on those subsets.

This can reveal whether a model improvement is broad or only helps a particular evidence form.

---

## 26. Primary retrieval metric

Keep the project's existing:

```text evidence recall
```

implementation.

Conceptually:

```text retrieved gold chunks
-------------------------
gold chunks
```

Do not create a second incompatible definition of evidence recall.

---

## 27. Paper recall

Also preserve:

```text paper recall
```

when available.

Paper recall answers:

```text Did we retrieve the correct source paper?
```

Evidence recall answers the stricter question:

```text Did we retrieve the required evidence chunk(s)?
```

A system can have:

```text paper recall = success
evidence recall = failure
```

which is diagnostically useful.

---

## 28. Stage-by-stage retrieval diagnosis

For each gold chunk, ideally inspect:

```text dense rank
BM25 rank
hybrid rank
reranker rank
final inclusion
```

This produces:

```text gold evidence
      ↓
candidate entry
      ↓
fusion
      ↓
reranking
      ↓
final evidence
```

The first stage where the gold chunk disappears identifies a likely bottleneck.

---

## 29. Retrieval failure taxonomy

Classify failures into:

```text 1. source paper not retrieved
2. source paper retrieved, wrong section
3. gold chunk absent from candidate pool
4. gold chunk enters candidate pool but is removed during fusion
5. gold chunk survives to reranking but is ranked too low
6. final-k truncates the gold chunk
7. query representation fails
8. chunk boundary destroys the evidence relationship
9. benchmark/gold-evidence problem
```

This is more useful than a single “retrieval failed” category.

---

## 30. Multi-hop retrieval diagnosis

For multi-hop questions inspect each subquery separately:

```text subquery 1
→ relevant gold chunk
→ rank

subquery 2
→ relevant gold chunk
→ rank
```

If one subquery consistently misses evidence, the problem may be:

```text query decomposition
```

rather than:

```text embedding quality
```

Do not attribute every multi-hop failure to the retriever.

---

## 31. Temporal retrieval caveat

The historical temporal subset had:

```text 2 questions
0.00 recall across tested strategies
```

This is not enough to establish a general temporal-retrieval limitation.

The temporal benchmark itself required repair:

```text earlier date
+
later date
+
same quantity/claim
+
evidence-bearing sections
+
specific shared anchors
+
actual update/refinement/change
```

Only validated temporal examples should be used for strong conclusions.

---

## 32. Chain retrieval diagnosis

Chain questions connect:

```text abstract
→ later evidence-bearing section
```

A retrieval failure can occur because the abstract is broad while the later evidence contains:

```text specific measurement
method
result
constraint
```

Chunking and query representation may therefore matter more than a simple semantic similarity score suggests.

---

## 33. Retrieval-only evaluation

The primary ablations should use:

```powershell
--retrieval-only
```

where supported.

This isolates:

```text retrieval quality
routing
latency
compute
```

from:

```text final answer wording
hallucination
citation formatting
```

Answer-generation evaluation belongs to a later phase.

---

## 34. First ablation stage: component contribution

Start with:

```text R0 baseline
R1 dense-only
R2 BM25-only
R3 hybrid without reranker
R4 hybrid + reranker
```

This answers:

```text What does each major retrieval component contribute?
```

Do not begin with an enormous parameter grid.

---

## 35. Second stage: parameter sensitivity

Once component contributions are clear, test:

```text dense_k
BM25_k
final_k
RRF/fusion parameters
rerank candidate depth
```

Keep architecture fixed.

The purpose is to identify:

```text diminishing returns
latency cliffs
recall plateaus
```

---

## 36. Third stage: embedding representation

Then test:

```text baseline embedding
vs
one carefully selected alternative
```

If the alternative is meaningfully different, run another controlled comparison.

Do not test many embeddings simultaneously unless the evaluation infrastructure can support a fair comparison without consuming excessive time.

---

## 37. Fourth stage: chunking

Then evaluate:

```text chunk-size variants
overlap variants
```

using the chosen retrieval architecture.

This establishes whether document segmentation is a hidden bottleneck.

---

## 38. Fifth stage: interactions

Only later consider interactions such as:

```text embedding × chunk size
candidate depth × reranker
embedding × candidate depth
```

Interaction studies are justified only when a main effect provides a reason to investigate them.

---

## 39. Do not run a huge Cartesian grid

Avoid immediately testing:

```text many embeddings
× many k values
× many final-k values
× many chunk sizes
× many overlaps
```

This produces a huge number of runs and creates severe multiple-comparison / tuning problems.

Use staged ablations.

---

## 40. Development vs final test

Retrieval hyperparameters should ideally be selected on:

```text development / validation data
```

Then:

```text freeze configuration
→ evaluate final test
```

The final test should not be repeatedly used as a tuning surface.

This is especially important because retrieval has many tunable parameters.

---

## 41. If there is no clean dev set

If the repository does not yet contain a suitable development benchmark:

```text document that limitation
```

and consider creating a separate development split from validated questions.

Do not repeatedly tune dozens of parameters on the same 27-question test set and then describe the best observed score as an unbiased final result.

---

## 42. Retrieval and Oracle-v2 interaction

Changing the retrieval stack can change:

```text ladder recalls
```

and therefore:

```text gold_route_v2
oracle_sufficient
```

So after a major retrieval change:

```text recompute Oracle-v2 for the new stack
```

when Oracle comparisons are needed.

Do not apply old Oracle labels to a fundamentally different retrieval system without qualification.

---

## 43. Retrieval changes and Compass

If the retrieval system changes enough to alter Oracle-v2 labels:

```text old Compass
```

may no longer match:

```text new retrieval policy
```

The proper sequence is:

```text new retrieval stack
        ↓
new Oracle-v2
        ↓
inspect target changes
        ↓
retrain / adapt Compass if needed
```

Do not call this automatically a Compass failure.

---

## 44. Routing should be held fixed during pure retrieval ablations

For the first retrieval studies:

```text router fixed
retrieval changes
```

This isolates retrieval contribution.

Only later run:

```text new retrieval
+
new Oracle
+
new Compass
```

as a co-adaptation experiment.

---

## 45. Latency measurement

Measure consistently:

```text index load
query encoding
dense retrieval
BM25 retrieval
fusion
reranking
finalization
```

At minimum preserve:

```text p50
p95
```

where the existing runner supports them.

For steady-state comparison, use warm models/indexes and report initialization separately.

---

## 46. Index-build cost

For embedding ablations also record:

```text embedding generation time
index build time
index size
embedding dimension
model loading time
```

A model that improves recall but greatly increases resource requirements should be represented honestly.

---

## 47. Reranker cost

Reranker work depends on candidate depth.

More candidates can mean:

```text more cross-encoder evaluations
higher latency
```

When possible, split:

```text retrieval latency
```

from:

```text reranking latency
```

This makes parameter sensitivity interpretable.

---

## 48. Hardware consistency

Run variants on the same:

```text machine
device
Python environment
library versions
threading setup
```

when possible.

Record:

```text CPU/GPU
RAM
device mode
software versions
```

Do not compare warm GPU runs with cold CPU runs.

---

## 49. Cache discipline

Know whether caches are:

```text model-specific
query-specific
shared
```

Do not accidentally reuse vectors produced by another embedding model.

Also record whether measured latency includes:

```text query embedding generation
```

or uses cached query vectors.

---

## 50. Reproducibility manifest

Every retrieval-ablation run should record:

```text run_id
commit
benchmark_version
question_count
embedding_model
embedding_revision
embedding_dimension
index_path
dense_k
bm25_k
rrf_k
reranker
rerank_candidate_count
final_k
chunk_max_chars
chunk_overlap
device
software versions
seed where applicable
```

Results should include:

```text evidence_recall
paper_recall
p50_latency
p95_latency
index_build_time
index_size
```

---

## 51. Per-question result schema

Preserve:

```text question_id
question_type
strategy
gold_chunk_ids
retrieved_chunk_ids
evidence_recall
paper_recall
latency
```

For deeper diagnostics also preserve:

```text dense ranks
BM25 ranks
hybrid rank
reranker rank
final inclusion
```

when the current runner can provide them.

---

## 52. Question-type analysis

For every major ablation, where sample size permits, report:

```text SIMPLE
MULTI_HOP
TEMPORAL
CHAIN
```

This can reveal effects hidden by the overall average.

For example, a retrieval change might improve:

```text simple retrieval
```

without improving:

```text multi-hop evidence coverage
```

Do not infer such patterns without per-type evidence.

---

## 53. Scientific-symbol analysis

A useful diagnostic subset is questions involving exact scientific identifiers such as:

```text H0
Ωm
YHe
ΔNeff
DESI
BAO
```

The purpose is to determine whether lexical retrieval is helping because of exact scientific notation rather than generic word overlap.

---

## 54. Robustness to wording

Where a development set permits it, test paraphrased questions against unchanged gold evidence.

This can measure whether a retrieval variant depends too heavily on:

```text exact wording
```

Do not use paraphrased test examples as hidden training data.

---

## 55. Retrieval quality vs compute

Every ablation should ideally answer two questions:

```text Did evidence recall change?
What did that change cost?
```

Cost can include:

```text latency
index size
memory
candidate count
reranker evaluations
embedding computation
```

A retrieval gain without resource accounting is incomplete.

---

## 56. Example clean result table

| Variant | Evidence Recall | Paper Recall | p50 Retrieval | p95 Retrieval | Index Size |
|---|---:|---:|---:|---:|---:|
| Baseline | | | | | |
| Dense only | | | | | |
| BM25 only | | | | | |
| Hybrid | | | | | |
| Hybrid + reranker | | | | | |
| Embedding variant | | | | | |

Do not fill values in advance.

---

## 57. Example k-sweep table

| dense_k | Evidence Recall | p50 Latency | p95 Latency |
|---:|---:|---:|---:|
| 5 | | | |
| 10 | | | |
| 20 | | | |
| 40 | | | |
| 80 | | | |

Equivalent tables can be produced for:

```text BM25_k
final_k
chunk size
overlap
```

---

## 58. Diminishing-return analysis

Look for the point where:

```text additional candidate depth
```

stops producing meaningful:

```text evidence-recall improvement
```

while continuing to increase:

```text latency
```

Do not assume the turning point is at 20, 40, or 80.

Measure it.

---

## 59. Retrieval failure location is often more important than the model name

Example:

```text gold chunks absent from candidate pool
```

suggests looking at:

```text embeddings
BM25
candidate depth
query representation
```

while:

```text gold chunks enter candidate pool but disappear after reranking
```

suggests:

```text reranker
candidate depth
final-k
```

This is the preferred debugging approach.

---

## 60. Potential retrieval conclusions

Possible measured outcomes include:

```text hybrid improves recall
```

or:

```text BM25 adds little on the current benchmark
```

or:

```text reranking helps recall but costs substantial latency
```

or:

```text larger embeddings change recall very little
```

or:

```text chunk size dominates embedding choice
```

These are examples of possible findings, not current results.

---

## 61. Null results are useful

A controlled null result such as:

```text alternative embedding ≈ baseline recall
but much larger index and slower inference
```

is valuable.

It prevents future work from replacing a simple baseline without evidence.

---

## 62. Retrieval and routing interaction

After a retrieval variant is understood in isolation, ask:

```text Does the routing gap change?
```

For example:

```text stronger retrieval
→ smaller benefit from adaptive routing
```

or:

```text stronger retrieval
→ more useful strategy specialization
```

Both are possible.

The answer must come from experiment results.

---

## 63. Re-evaluate Oracle after major retrieval changes

For a materially different retrieval stack:

```text recompute Oracle-v2
```

and record the new:

```text ladder recalls
gold_route_v2
oracle_sufficient
```

Keep these separate from the baseline Oracle artifacts.

---

## 64. Re-evaluate Compass after Oracle changes

If new Oracle labels differ materially:

```text compare old Compass predictions
vs
new Oracle-v2
```

Only retrain when justified.

This separates:

```text retrieval effect
```

from:

```text learned-router adaptation
```

---

## 65. Exact starting commands

Set imports:

```powershell
$env:PYTHONPATH="src"
```

Check repository state:

```powershell
git status
git log --oneline --decorate -10
```

Run tests:

```powershell
python -m pytest -q
```

Build index when needed:

```powershell
python scripts/build_index.py
```

Run the existing static retrieval baseline:

```powershell
python scripts/run_experiment.py --group run6 --exp B --retrieval-only
```

Use the actual current experiment mapping before running these commands.

---

## 66. Recommended coding workflow

```text 1. verify current repository
2. verify current config
3. verify benchmark version
4. verify baseline B
5. implement one ablation
6. add/update tests
7. run tests
8. run tiny smoke check
9. run full ablation
10. save per-question output
11. inspect failures
12. move to next variable
```

Do not edit several retrieval components at once during the first stage.

---

## 67. Tests before retrieval runs

At minimum verify:

```text chunking
index loading
dense retrieval
BM25 retrieval
hybrid fusion
reranker
metrics
experiment runner
```

Run:

```powershell
python -m pytest -q
```

before expensive sweeps.

---

## 68. Avoid stale-result confusion

Every saved result must identify:

```text code commit
config
benchmark version
retrieval settings
model version
```

Do not compare old results with new ones unless those metadata are known.

This is particularly important because AtlasRAG's benchmark and routing code changed during Week 2.

---

## 69. Research-quality rule for tuning

Do not do:

```text test 50 configurations
→ pick highest test recall
→ report it as final
```

Prefer:

```text validation benchmark
→ tune
→ freeze
→ final test
```

If the current benchmark infrastructure does not yet provide a clean validation set, document the limitation.

---

## 70. Suggested retrieval-ablation order

```text R0  baseline
 ↓
R1  dense-only
 ↓
R2  BM25-only
 ↓
R3  hybrid without reranker
 ↓
R4  hybrid + reranker
 ↓
R5  candidate-depth sweeps
 ↓
R6  final-k sweep
 ↓
R7  embedding alternative
 ↓
R8  chunk-size sweep
 ↓
R9  overlap sweep
 ↓
R10 selected interaction experiments
```

The sequence can change if the actual failure analysis gives a stronger reason.

---

## 71. Week 6 outputs

The final phase should produce:

```text retrieval-ablation summary
per-question result files
component contribution table
parameter-sensitivity tables
embedding comparison
chunking comparison
latency/resource measurements
failure taxonomy
Oracle implications
routing implications
```

Do not keep only the final aggregate score.

---

## 72. What the final report should answer

By the end of Week 6:

```text 1. Does hybrid retrieval actually help?

2. How much does BM25 contribute?

3. How much does reranking contribute?

4. Where does the gold evidence disappear?

5. How sensitive is retrieval to candidate depth?

6. How sensitive is retrieval to final-k?

7. Does another embedding materially change evidence recall?

8. Does chunk size or overlap materially affect retrieval?

9. What do the gains cost in latency/resources?

10. Do retrieval changes alter Oracle-v2 strategy labels?

11. Do retrieval changes alter the learned routing conclusions?
```

---

## 73. Week 6 completion checklist

```text [ ] baseline verified
[ ] dense-only measured
[ ] BM25-only measured
[ ] hybrid measured
[ ] reranker ON/OFF measured
[ ] dense-k sensitivity measured
[ ] BM25-k sensitivity measured
[ ] final-k sensitivity measured
[ ] embedding variant measured
[ ] chunk-size measured
[ ] overlap measured
[ ] per-question outputs preserved
[ ] stage-by-stage failures inspected
[ ] latency measured
[ ] index/resource cost measured
[ ] dev/test separation respected
[ ] benchmark version recorded
[ ] Run 1 untouched
[ ] Oracle implications documented
[ ] routing implications documented
[ ] all tests passing
```

---

## 74. Final Week 6 principle

> **Do not ask which retrieval model is best until you know where the current system loses the evidence.**

AtlasRAG has several distinct stages:

```text dense
BM25
fusion
reranking
final-k
chunking
```

The correct analysis is:

```text Where was the gold evidence lost?
        ↓
Which component controls that stage?
        ↓
What change fixes it?
        ↓
What recall improvement results?
        ↓
What latency/resource cost does it add?
        ↓
Does the routing result change?
```

The purpose of Week 6 is therefore not to build a generic retrieval leaderboard.

It is to make the retrieval stack:

```text measured
controlled
reproducible
interpretable
```

so the final AtlasRAG system can cleanly separate:

```text retrieval contribution
from
routing contribution
from
answer-generation contribution.
```
