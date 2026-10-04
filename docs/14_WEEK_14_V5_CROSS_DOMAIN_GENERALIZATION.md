# AtlasRAG — Week 14: V5 Cross-Domain Generalization & Scientific-Domain Transfer

## 1. Purpose

Week 13 expands the scientific benchmark so that AtlasRAG's conclusions are not dominated by a tiny 27-question evaluation set.

Week 14 takes the next harder step:

> **Does the useful part of AtlasRAG's adaptive retrieval methodology generalize beyond astrophysics/cosmology when the scientific domain, vocabulary, evidence structure, and retrieval distribution change?**

The purpose of V5 is not to make AtlasRAG support every scientific field.

The purpose is to test whether the research contribution is:

```text
specific to one corpus
```

or whether it represents a more general principle:

```text
question-aware / retrieval-state-aware adaptive evidence acquisition
```

The central conceptual transition is:

```text
V1
adaptive retrieval in one scientific domain

        ↓

V4
larger and cleaner scientific benchmark

        ↓

V5
cross-domain generalization
```

A strong V5 result would make the research claim more interesting.

A weak V5 result is also scientifically useful because it can identify:

```text
domain-specific assumptions
feature instability
vocabulary shift
retrieval-model dependence
benchmark-specific behavior
```

Do not assume transfer will work.

The experiment exists to find out.

---

# 2. Where V5 fits in the AtlasRAG roadmap

The long-term progression is:

```text
V1
Adaptive retrieval routing
        ↓
V2
Evidence verification
        ↓
V3
Retrieval-failure prediction
        ↓
V4
Larger / paper-disjoint scientific benchmark
        ↓
V5
Cross-domain generalization
        ↓
V6
Scientific tables / equations / temporal reasoning
```

Each version answers a different question.

### V1

```text
Which retrieval strategy should this question use?
```

### V2

```text
Does the evidence actually support the generated claims?
```

### V3

```text
Can retrieval-state signals predict likely retrieval failure?
```

### V4

```text
Do the earlier observations survive a larger, cleaner benchmark?
```

### V5

```text
Do the observations survive a change in scientific domain?
```

### V6

```text
How should scientific evidence structures be represented more explicitly?
```

Do not merge these claims.

A result for V5 must be reported as a transfer/generalization result, not retroactively treated as proof of V1/V2/V3 assumptions.

---

# 3. V5 research question

Primary research question:

> **Can an adaptive retrieval policy learned or designed on one scientific domain retain useful evidence quality and efficiency on an unseen scientific domain without requiring domain-specific retraining?**

Secondary questions:

```text
1. Which routing signals transfer across domains?

2. Which retrieval-state features remain predictive under domain shift?

3. Does dense/BM25 disagreement behave similarly across domains?

4. Does question-only routing generalize better or worse than retrieval-state-aware escalation?

5. How much adaptation is required before performance becomes stable?

6. Does a shared router outperform separate domain-specific routers when data is limited?

7. Which scientific evidence structures cause the largest transfer failures?

8. Does domain transfer preserve the quality/cost advantage of adaptive retrieval?
```

These are hypotheses, not conclusions.

---

# 4. The main experimental idea

Suppose AtlasRAG is trained or calibrated using:

```text
Domain A = astrophysics / cosmology
```

Then evaluate on:

```text
Domain B = an unseen scientific field
```

without changing the test benchmark after seeing results.

The core transfer setup is:

```text
TRAIN
Astrophysics / cosmology
        ↓
router / failure detector

TEST
Unseen scientific domain
        ↓
zero-shot evaluation
```

The cleanest first question is therefore:

```text
Can the existing decision rule transfer at all?
```

Only after that should adaptation be introduced.

---

# 5. Domain selection principle

Do not select the new domain simply because its papers are easy to download.

The second domain should create a meaningful distribution shift.

Useful selection criteria:

```text
scientific literature is publicly accessible

papers contain substantial technical content

questions require evidence retrieval rather than trivia

papers contain terminology not dominant in astrophysics

there is enough diversity in papers / topics / years

license and redistribution constraints are understood

retrieval can be performed using the same general infrastructure
```

Potential candidate domains include fields such as:

```text
biology / biomedical science

materials science

chemistry

geoscience / climate science

computer science research literature
```

These are candidate categories, not a recommendation to choose all of them.

A single well-designed held-out domain is more useful than several tiny domains that cannot support meaningful analysis.

---

# 6. Domain choice must be justified

Create a domain-selection record before collecting the full corpus.

Recommended fields:

```text
domain_name
domain_reason
public_source
access_method
license_status
estimated_paper_count
estimated_question_count
technical_density
terminology_distance
scientific_structure_notes
known_dataset_limitations
```

The final write-up should explain why the selected domain constitutes genuine distribution shift.

Avoid vague wording such as:

```text
"we selected biology because it is another field."
```

Instead document observable differences such as:

```text
vocabulary
observable types
units
citation patterns
section structures
equation frequency
table usage
entity naming conventions
```

---

# 7. Fresh literature review requirement

Before making any V5 novelty claim, perform a fresh literature search.

This is especially important because:

```text
adaptive RAG
query routing
retrieval routing
selective retrieval
uncertainty estimation
retrieval failure prediction
cross-domain scientific QA
cross-domain RAG
```

are active research areas.

The V5 document should therefore maintain two separate sections:

```text
existing literature
```

and:

```text
AtlasRAG-specific experiment
```

Never claim:

```text
"no one has done this"
```

unless the search genuinely supports such a statement and the scope is precisely defined.

A stronger and safer framing is:

```text
"We evaluate X under Y cross-domain scientific transfer setting."
```

The experimental configuration can be novel even when individual components are not novel.

---

# 8. What exactly should transfer?

Do not define transfer only as:

```text
same accuracy on another dataset
```

There are multiple potentially transferable components.

### Transfer type A — routing semantics

Do the classes still mean roughly the same thing?

```text
SIMPLE
MULTI_HOP
UNCERTAIN
```

### Transfer type B — retrieval signals

Do features such as:

```text
reranker score
dense/BM25 agreement
score gap
scientific-anchor coverage
```

remain useful?

### Transfer type C — decision policy

Does the same threshold or routing policy behave similarly?

### Transfer type D — operational advantage

Does adaptive retrieval still reduce unnecessary work while maintaining evidence quality?

These should be evaluated separately.

---

# 9. Critical concern: are the V1 route labels domain-general?

The original AtlasRAG route semantics were developed around a scientific corpus.

For example:

```text
SIMPLE
→ one compact evidence requirement

MULTI_HOP
→ evidence requires multiple linked pieces

UNCERTAIN
→ difficult / ambiguous / low-confidence retrieval case
```

These semantics may not map perfectly to another domain.

For example, a biomedical question might involve:

```text
intervention
population
outcome
study design
```

rather than the kinds of entities common in cosmology.

Therefore V5 must explicitly test:

```text
label semantic compatibility
```

before treating cross-domain route accuracy as meaningful.

---

# 10. Do not force incompatible labels

Bad design:

```text
Take the same labels
↓
assign them to every domain
↓
train
↓
claim transfer
```

Better:

```text
define domain-neutral evidence requirements
↓
map domain-specific questions to those requirements
↓
verify mapping with human review
↓
use the shared labels only when semantics remain valid
```

If a class does not transfer cleanly, record:

```text
not_applicable
```

or redesign the label system for the V5 experiment.

Do not manufacture agreement.

---

# 11. Domain-neutral task formulation

A more robust representation is to define the underlying retrieval problem as:

```text
How many distinct evidence units are required?
How strongly are they linked?
How ambiguous is the evidence target?
How likely is one compact retrieval path to suffice?
```

Conceptually:

```text
Question
   ↓
Evidence requirement structure
   ↓
retrieval strategy
```

This can make transfer more meaningful than simply copying class names.

Still, preserve the original V1 labels for historical comparison.

---

# 12. V5 experimental ladder

Use progressively harder experiments.

### Experiment V5-A — zero-shot static retrieval

Run the frozen retrieval system on the new domain.

Purpose:

```text
measure basic retrieval transfer
```

No router training is involved.

### Experiment V5-B — frozen rule-based routing

Apply an existing routing policy without retraining it on the target domain.

Purpose:

```text
test direct transfer of decision logic
```

### Experiment V5-C — zero-shot learned router

Use the router trained on Domain A without target-domain training.

Purpose:

```text
test model transfer
```

### Experiment V5-D — zero-shot failure detector

Apply the V3 predictor to target-domain retrieval states without target labels.

Purpose:

```text
test whether retrieval-state features transfer
```

### Experiment V5-E — few-shot adaptation

Add a small amount of target-domain labelled data.

Purpose:

```text
measure adaptation efficiency
```

### Experiment V5-F — mixed-domain training

Train with multiple source domains and hold one domain out.

Purpose:

```text
measure domain-general training
```

Do not jump directly to V5-F.

First establish whether zero-shot transfer is possible.

---

# 13. Recommended first V5 setup

The first clean setup should be:

```text
SOURCE DOMAIN
Astrophysics / cosmology

TARGET DOMAIN
one unseen scientific field

TRAIN
source-domain data only

VALIDATION
source-domain data only

TEST
target-domain benchmark
```

This gives a strict transfer question.

The target test data must remain isolated from model fitting and threshold tuning.

---

# 14. Domain-disjoint vs paper-disjoint

These are different controls.

### Paper-disjoint

No paper appears in both train and test.

### Domain-disjoint

No target-domain examples appear in training.

V5 should use both:

```text
paper-disjoint
+
domain-disjoint
```

Otherwise the experiment may accidentally measure memorization or vocabulary familiarity rather than transfer.

---

# 15. Proposed data layout

Recommended structure:

```text
data/v5/
    domains.json
    papers/
    questions/
    splits/
    retrieval_states/
    manifests/
    audits/
    results/
```

Each question should retain provenance.

For example:

```json
{
  "question_id":"bio-simple-001",
  "domain":"biology",
  "paper_ids":["paper-042"],
  "split":"test",
  "question_type":"simple",
  "answer":"...",
  "gold_evidence_ids":["chunk-123"]
}
```

The exact schema should follow the current repository conventions instead of creating unnecessary duplication.

---

# 16. Corpus normalization

The new domain should pass through the same conceptual ingestion stages:

```text
raw papers
↓
metadata extraction
↓
text extraction
↓
section handling
↓
chunking
↓
indexing
```

Track domain-specific ingestion problems separately.

Examples:

```text
PDF extraction failure
formula corruption
table loss
reference contamination
section parsing errors
```

If one domain has substantially worse extraction quality, that becomes a confounder.

Do not interpret every cross-domain performance drop as model failure.

---

# 17. Retrieval stack control

For the initial transfer experiment, keep the retrieval stack as fixed as reasonably possible.

Current historical baseline includes:

```text
BAAI/bge-small-en-v1.5

Dense retrieval
BM25 retrieval
RRF fusion
cross-encoder reranking
```

The exact live configuration must be verified from the repository before execution.

Do not silently upgrade:

```text
embedding model
reranker
chunking rules
retrieval k
```

between source and target domains.

Otherwise the experiment confounds:

```text
domain shift
+
retrieval-stack change
```

---

# 18. Important transfer confounder: vocabulary shift

A target scientific domain can contain terminology absent from astrophysics.

For example, the router may see unfamiliar:

```text
acronyms
entity names
parameter names
method names
```

A question-only model might therefore become less confident simply because its vocabulary changes.

This is not necessarily a failure of the routing concept.

It may be a feature-distribution problem.

Measure it.

---

# 19. Embedding-model dependence

A semantic retriever may transfer better than a router because the embedding space already captures broad semantic relationships.

Alternatively, the opposite may happen if the embedding model is weak on technical terminology in the new domain.

Therefore separate:

```text
retrieval transfer
```

from:

```text
router transfer
```

A useful diagnostic matrix is:

```text
                Target retrieval
                good     weak
Router good     ideal    retrieval bottleneck
Router weak     routing  joint failure
```

This prevents blaming the wrong component.

---

# 20. Scientific-anchor transfer

V1/V4 benchmark generation uses scientific signals such as:

```text
acronyms
parameters
model symbols
observables
```

These concepts may transfer, but the actual extractors are likely domain-sensitive.

Example:

```text
cosmology:
H0, Ωm, Neff

biology:
IL-6, TNF-α, CRP
```

The shared abstraction is:

```text
specific scientific identifiers
```

rather than any one vocabulary.

V5 should therefore evaluate both:

```text
raw identifier matching
```

and, where justified,

```text
domain-neutral scientific-signal coverage
```

Do not broaden the signal extractor without an ablation.

---

# 21. Evidence structure shift

Different fields use evidence differently.

Potential differences include:

```text
tables vs prose

equations vs prose

methods vs results

experimental values vs theoretical values

single-study evidence vs meta-analysis
```

A retrieval policy that works on prose-heavy cosmology passages may not work as well on data-heavy biomedical or materials-science papers.

That is a useful V5 finding.

The goal is not to hide it.

---

# 22. Benchmark design for target domain

The target benchmark should contain meaningful question diversity.

Recommended categories:

```text
SIMPLE
MULTI_HOP
CONFLICTING
TEMPORAL
CHAIN
```

Use these only when the category can be defined consistently in the new domain.

A benchmark does not become stronger just by containing more labels.

The questions should represent genuine evidence requirements.

---

# 23. Target-domain SIMPLE questions

A good SIMPLE question should generally be answerable from a compact evidence region.

Examples of structure:

```text
What value of X was reported?

Which method was used?

What was the measured effect?
```

Avoid:

```text
questions whose answer can be guessed from common knowledge
```

or:

```text
questions that require the whole paper
```

---

# 24. Target-domain MULTI_HOP questions

A useful MULTI_HOP question must require distinct evidence pieces.

For example:

```text
passage A
contains baseline measurement

passage B
contains interpretation / comparison

question
requires A + B
```

The current deterministic pair-sourcing infrastructure should be reused where applicable.

Do not reintroduce the historical problem of selecting passages merely because they share a broad topic.

Require concrete shared scientific anchors and complementary evidence.

---

# 25. Target-domain CONFLICTING questions

Conflict must be real.

Potential forms:

```text
study A reports one value
study B reports another

method A finds an effect
method B finds a weaker effect

earlier result conflicts with later evidence
```

The benchmark must preserve enough source context for the conflict to be understood.

Do not create conflict artificially by mixing unrelated quantities.

---

# 26. Target-domain TEMPORAL questions

Temporal questions require:

```text
ordered evidence
+
shared scientific anchor
+
actual change over time
```

Examples of temporal structure:

```text
earlier estimate
vs
later estimate

initial method
vs
updated method

preliminary result
vs
later measurement
```

Do not label two papers as temporal merely because one is newer.

The question should depend on the temporal relationship.

---

# 27. Target-domain CHAIN questions

A CHAIN question should require a sequence such as:

```text
observation
↓
method / intermediate result
↓
scientific conclusion
```

The evidence must contribute distinct steps.

Do not accept a chain question when the final answer is already stated directly in the abstract.

This was a known failure mode in earlier benchmark construction.

---

# 28. Human review remains mandatory

Automatic generation is useful for scale.

It is not the final authority.

Every accepted V5 benchmark item should pass checks for:

```text
question clarity
answer support
gold evidence quality
question-type validity
all-passages-needed validity
quantity compatibility
temporal validity
conflict validity
```

Keep the review process documented.

---

# 29. Gold evidence: exact chunk vs alternative support

The V1 benchmark uses an exact-gold style recall concept.

That remains useful for controlled experiments.

However, V5 must not accidentally treat:

```text
not the annotated gold chunk
```

as equivalent to:

```text
cannot answer
```

A target-domain passage may legitimately provide alternative evidence.

Record both when practical:

```text
exact_gold_recall

alternative_support / evidence_sufficiency
```

The latter requires a stronger annotation protocol.

---

# 30. Oracle-v2 recomputation

Do not transfer the old Oracle-v2 labels directly to the target domain.

After building the target-domain benchmark:

```text
run retrieval ladder
↓
measure recall
↓
compute best attainable recall
↓
select cheapest strategy within epsilon
↓
mark sufficiency
```

This recreates the Oracle semantics under the new domain.

The target-domain oracle is therefore an empirical control, not a copied label set.

---

# 31. Why copied labels would be wrong

Suppose a question was:

```text
MULTI_HOP
```

in astrophysics.

That does not imply:

```text
same retrieval strategy
```

in another domain.

The new domain may have:

```text
different chunk density
different evidence distributions
different terminology
different semantic similarity patterns
```

Oracle-v2 should be rerun because the retrieval landscape changed.

---

# 32. V5 baseline matrix

At minimum, include:

| System | Source-trained? | Target-labelled? | Purpose |
|---|---:|---:|---|
| A | No | No | vanilla retrieval control |
| B | No | No | static retrieval baseline |
| Strong | No | No | strongest retrieval reference |
| V1 frozen router | Yes | No | zero-shot routing transfer |
| V3 frozen detector | Yes | No | zero-shot failure prediction |
| Target few-shot router | Yes | Yes, small | adaptation cost |
| Target few-shot detector | Yes | Yes, small | adaptation cost |
| Oracle-v2 | Test-computed | No training | empirical upper/reference policy |

The exact experiment names should follow the current `experiments.py` conventions.

---

# 33. Primary metrics

The main metrics should remain consistent with previous AtlasRAG work.

### Retrieval quality

```text
gold-evidence recall
retrieval sufficiency
```

### Answer quality

```text
correctness
relevance
groundedness
```

### Citation quality

```text
citation precision
citation completeness
unsupported-claim rate
```

### Operational cost

```text
provider API calls
retry attempts
prompt tokens
completion tokens
latency
```

### Routing / prediction

```text
route agreement
failure-detection precision
failure-detection recall
AUROC
AUPRC
calibration
```

Use only metrics that the experiment actually measures.

---

# 34. The most important V5 comparison

The most informative comparison is not:

```text
router accuracy: 82% vs 78%
```

The key comparison is:

```text
adaptive policy
vs
strong retrieval
vs
static baseline
```

under the target domain.

Ask:

```text
How much evidence quality is retained?
How much unnecessary retrieval is avoided?
What happens to cost and latency?
```

A routing model can have imperfect classification accuracy and still provide useful operational behavior.

Conversely, high route accuracy can be irrelevant if route differences do not change evidence quality.

---

# 35. Cost/quality frontier under transfer

Construct the same kind of operational frontier used in previous experiments.

Conceptually:

```text
x-axis:
cost / provider calls / latency

y-axis:
evidence quality or answer quality
```

Compare:

```text
static
strong retrieval
zero-shot router
zero-shot failure detector
few-shot adapted models
```

The question is whether the adaptive policy remains on or near the useful frontier after domain shift.

---

# 36. Zero-shot transfer is the most important first result

Before adapting to the new domain, freeze everything.

Then measure:

```text
source-domain result
vs
target-domain result
```

The difference gives a first estimate of transfer degradation.

For example:

```text
source evidence recall = 0.82

target evidence recall = 0.71
```

This is not necessarily failure.

The important question becomes:

```text
How much of the degradation is retrieval?
How much is routing?
How much is domain-specific evidence structure?
```

---

# 37. Domain-shift decomposition

When target performance drops, inspect at least four layers.

```text
1. ingestion

2. retrieval

3. routing / failure prediction

4. answer generation
```

A useful decomposition is:

```text
fixed strong retrieval target-domain result
```

versus:

```text
adaptive target-domain result
```

If both are weak, the bottleneck is likely not routing alone.

---

# 38. Failure taxonomy for V5

Add a domain-transfer taxonomy.

Suggested labels:

```text
VOCABULARY_SHIFT

RETRIEVAL_SHIFT

EVIDENCE_STRUCTURE_SHIFT

LABEL_SEMANTIC_MISMATCH

CALIBRATION_SHIFT

ROUTING_SHIFT

INGESTION_FAILURE

ANSWER_GENERATION_FAILURE
```

Keep multiple causes when a failure is genuinely mixed.

Do not force every failure into a single category.

---

# 39. Vocabulary-shift analysis

Measure simple corpus-level indicators such as:

```text
out-of-domain scientific terms
acronym frequency
rare-token proportion
entity-name frequency
```

Where practical, compare feature distributions between:

```text
source benchmark
vs
target benchmark
```

This helps explain why a question-only router may become uncertain.

---

# 40. Feature-distribution shift for V3

For the V3 failure detector, compare source and target distributions of:

```text
top reranker score
score gap
mean top-k score
BM25/dense overlap
unique-paper count
unique-section count
scientific-anchor coverage
redundancy
```

A detector trained on:

```text
source score distribution
```

may become miscalibrated when the target scores shift.

This is a central V5 diagnostic.

---

# 41. Calibration transfer

Suppose the source detector predicts:

```text
P(failure)=0.8
```

The target domain may exhibit a different observed failure rate.

Therefore measure:

```text
source calibration
vs
target calibration
```

using appropriate metrics such as:

```text
Brier score
ECE
reliability plots
```

A detector can preserve ranking ability while losing probability calibration.

Do not conflate the two.

---

# 42. Threshold-transfer experiment

For a fixed policy:

```text
source threshold = t
```

apply:

```text
target threshold = same t
```

Then compare against:

```text
oracle target threshold
```

where the latter is selected only from target validation data, never the final test set.

This answers:

```text
Does the policy transfer?
```

rather than merely:

```text
Can we retune it?
```

---

# 43. Few-shot adaptation ladder

After zero-shot evaluation, introduce a controlled adaptation budget.

For example:

```text
0 target labels
5 target labels
10 target labels
25 target labels
50 target labels
```

The exact sizes depend on the benchmark scale.

The key measurement is:

```text
performance gain per target-domain label
```

Do not use the final test set for adaptation.

---

# 44. Why few-shot adaptation matters

A system that fails completely zero-shot but becomes strong after 10 examples may still be useful.

The scientific result then becomes:

```text
zero-shot transfer is limited
but adaptation is label-efficient
```

That is different from:

```text
fully domain-general
```

The distinction must appear in the final claims.

---

# 45. Shared model vs domain-specific model

A later experiment can compare:

```text
one shared router
```

against:

```text
one router per domain
```

The clean hypothesis is:

```text
shared model may improve sample efficiency
```

while:

```text
domain-specific models may improve peak performance
```

Do not assume either outcome.

---

# 46. Metadata ablation

A tempting approach is to tell the router:

```text
domain = biology
```

This can make adaptation easier.

But it changes the task.

Therefore run:

```text
no domain metadata
```

and optionally:

```text
explicit domain metadata
```

as a separate ablation.

The first test asks whether the system can infer useful behavior from the question/retrieval state itself.

---

# 47. Domain metadata must not leak answers

Allowed:

```text
domain label
corpus identity
```

Potentially dangerous:

```text
metadata encoding outcome
paper-specific answer fields
human annotations
split information
```

Only use information that would plausibly be available at inference time.

---

# 48. Retrieval-only first

Do not begin V5 by evaluating full answers from a complicated new stack.

First establish:

```text
retrieval quality
oracle behavior
routing behavior
failure prediction
```

Then evaluate answer quality.

This keeps the causal interpretation manageable.

---

# 49. Answer model control

The answering LLM should remain frozen for the first V5 experiment.

The current project has used:

```text
openai/gpt-oss-20b
through a Groq-compatible API
```

The actual live model must be verified from the repository before final execution.

Do not change the model simply because target-domain answers look weaker.

A stronger answer model would make the comparison harder to interpret.

---

# 50. Prompt control

Keep the answer prompt frozen.

Record:

```text
prompt version
model name
sampling parameters
retrieval configuration
router configuration
```

If a domain-specific prompt becomes necessary, treat that as an adaptation experiment rather than a silent implementation change.

---

# 51. Fresh literature and current-tool verification

Because the project may make claims about:

```text
state of the art
cross-domain RAG
scientific QA
adaptive retrieval
router transfer
```

perform current web research before finalizing V5 conclusions or paper language.

Verify:

```text
recent papers
recent benchmarks
current model capabilities
current public dataset availability
licenses / access conditions
```

Any external finding should be clearly separated from repository-derived experiment results.

---

# 52. Reproducibility manifest

Create a V5 manifest before the final run.

Recommended fields:

```text
experiment_id
source_domain
source_corpus_hash
target_domain
target_corpus_hash
benchmark_hash
benchmark_version
retrieval_config_hash
router_model_hash
failure_detector_hash
answer_model
answer_prompt_version
seed
git_commit
test_count
```

Also record environment information where practical.

---

# 53. Instrumentation requirement

The project previously identified a gap in generation instrumentation.

V5 should not repeat it.

Persist separately:

```text
logical LLM calls
provider API calls
cache hits
cache misses
retry attempts
RateLimitError count
APIConnectionError count
final error state
prompt tokens
completion tokens
total tokens
```

Do not infer provider-call counts from logical call counts.

---

# 54. Provider rate-limit handling

The current project has bounded retry logic.

That behavior should remain bounded during V5.

A V5 run should terminate cleanly after configured retry exhaustion rather than hanging indefinitely.

Persist failure state in the run artifact.

For interrupted runs:

```text
mark incomplete
```

Do not treat partial output as a complete experiment.

---

# 55. Run IDs

Use explicit run identifiers.

Example:

```text
v5_zero_shot_router_001
v5_zero_shot_detector_001
v5_fewshot_10_001
```

Avoid ambiguous files such as:

```text
final.json
latest.json
result2.json
```

The raw artifact should tell you exactly what happened.

---

# 56. Recommended V5 directory outputs

Use something like:

```text
experiments/v5/
    manifests/
    retrieval/
    routing/
    failure_prediction/
    answers/
    metrics/
    failures/
    plots/
```

Keep historical V1/V4 artifacts untouched.

---

# 57. Statistical analysis

Use paired comparisons where the same target questions are evaluated under different policies.

Relevant comparisons include:

```text
static vs strong
router vs static
router vs strong
failure detector vs static
failure detector vs strong
zero-shot vs few-shot
```

For a benchmark with matched questions, preserve question-level outcomes so confidence intervals can be estimated from paired differences.

Do not report only aggregate means.

---

# 58. Domain-wise and question-type analysis

Report results by:

```text
overall
domain
question type
```

For V5 there may be only one target domain in the first pilot.

That is acceptable.

But avoid making a universal claim from one domain.

---

# 59. Failure analysis should be qualitative as well

Inspect representative failures.

A useful table is:

| Question | Domain | System | Failure type | What happened | Fix direction |
|---|---|---|---|---|---|
| ... | ... | ... | ... | ... | ... |

Look for recurring patterns:

```text
wrong section
wrong study
same acronym, different meaning
same topic, wrong quantity
retrieval misses table
retriever overweights abstract
router becomes overconfident
failure detector calibration shifts
```

These observations are often more informative than a single score.

---

# 60. Negative transfer

One of the most important possible outcomes is:

```text
adaptive system performs worse on target domain
```

This can reveal:

```text
source-specific feature assumptions
poor calibration
misaligned route semantics
retrieval-model weaknesses
```

Do not hide negative transfer because the overall project narrative expected generalization.

A well-designed V5 makes negative transfer measurable.

---

# 61. Cross-domain feature ablation

After establishing zero-shot behavior, examine feature families.

For V3-style failure prediction:

```text
semantic only
lexical only
ranking only
agreement/diversity only
scientific signals only
all features
```

Train on source and evaluate on target.

The key question is:

```text
Which features transfer?
```

A feature that performs well in-domain but collapses cross-domain is especially important to identify.

---

# 62. Domain-general vs domain-specific features

Potentially domain-general:

```text
score gap
dense/BM25 disagreement
retrieval diversity
reranker score shape
```

Potentially domain-specific:

```text
exact scientific terminology dictionaries
domain-specific acronym lists
fixed observable names
cosmology-specific symbols
```

This distinction should remain a hypothesis until measured.

---

# 63. Scientific signal abstraction experiment

A later V5 ablation can compare:

```text
raw domain-specific anchors
```

against:

```text
abstract scientific-signal categories
```

For example:

```text
parameter
measurement
method
material / molecule / entity
model
observable
uncertainty
```

The purpose is to test whether abstraction improves transfer.

Do not implement a large ontology before the simple baseline exists.

---

# 64. Cross-domain Oracle regret

One strong way to evaluate adaptive routing is through regret relative to the empirical Oracle-v2 policy.

Define conceptually:

```text
oracle quality/cost
vs
adaptive policy quality/cost
```

A useful quantity is:

```text
quality regret
cost regret
```

This can tell you whether the adaptive policy becomes less aligned under domain shift even when raw recall remains reasonable.

---

# 65. Selective-risk framing

For V3 transfer, the decision is effectively:

```text
trust
vs
escalate
```

Therefore report:

```text
coverage
fallback / escalation rate
failure rate among trusted cases
cost per query
```

A good target-domain policy should ideally:

```text
reduce failures among trusted cases
```

without:

```text
escalating almost every query
```

---

# 66. Transfer efficiency

A useful summary metric is:

```text
performance retained per unit of adaptation cost
```

For few-shot adaptation, record:

```text
target labels used
training time
provider cost if any
performance gain
```

The goal is not only peak target performance.

It is efficient adaptation.

---

# 67. What not to do in V5

Do not simultaneously change:

```text
embedding model
chunking
reranker
router
answer model
benchmark
prompt
```

and then call the result:

```text
cross-domain generalization
```

That would be an uncontrolled redesign.

V5 begins with the frozen stack.

Adaptations are introduced one variable at a time.

---

# 68. What counts as a meaningful V5 result?

A meaningful result is not necessarily:

```text
+10% accuracy
```

A useful result could be:

```text
zero-shot transfer retains most retrieval quality

or

failure prediction degrades less than question-only routing

or

10 target examples recover most of the lost performance

or

specific feature groups consistently survive domain shift
```

The contribution should follow the observed evidence.

---

# 69. Possible outcomes

### Outcome A — strong transfer

```text
zero-shot adaptive policy remains competitive
```

Interpretation:

```text
supports broader domain-general potential
```

Still avoid universal claims.

### Outcome B — moderate transfer

```text
quality declines
but adaptation is cheap
```

Interpretation:

```text
method may be practically transferable with light calibration
```

### Outcome C — weak zero-shot, strong few-shot

Interpretation:

```text
domain adaptation is required but label-efficient
```

### Outcome D — poor transfer even after adaptation

Interpretation:

```text
current approach may rely heavily on domain-specific assumptions
```

### Outcome E — retrieval itself is the bottleneck

Interpretation:

```text
V5 does not invalidate adaptive routing;
non-transfer may originate in retrieval infrastructure
```

---

# 70. V5 decision framework

At the end, classify the result as:

```text
KEEP
```

if the cross-domain experiment provides credible generalization evidence.

```text
KEEP WITH QUALIFIERS
```

if transfer exists only under limited conditions.

```text
REJECT
```

if the result provides no useful evidence of generalization.

```text
DEFER
```

if benchmark quality, sample size, or infrastructure is insufficient for a defensible conclusion.

Do not force a KEEP result.

---

# 71. Relationship to publication claims

A V5 result can strengthen a paper/report claim from:

```text
"works on an astrophysics corpus"
```

toward:

```text
"shows evidence of transfer across scientific domains"
```

only when the experiment supports that wording.

It should not automatically become:

```text
"domain-general scientific RAG"
```

unless multiple domains and rigorous controls justify the stronger claim.

---

# 72. Resume / portfolio interpretation

A successful V5 experiment can become a stronger engineering/research story:

```text
Designed and evaluated adaptive retrieval under cross-domain scientific distribution shift, measuring evidence quality, escalation cost, and transfer efficiency.
```

Do not put a numeric improvement into the resume until it is measured on the final frozen V5 artifact.

---

# 73. Suggested research artifact outputs

At completion, aim to have:

```text
V5 benchmark

V5 source/target manifests

zero-shot results

few-shot results

retrieval-state feature analysis

cross-domain calibration plots

cost/quality curves

failure taxonomy

raw per-question predictions

final summary table
```

The raw data is more important than polished screenshots.

---

# 74. Exact execution order

Do not start with model training.

Follow this order:

```text
STEP 1
Read repository state

STEP 2
Verify Week 13 benchmark is complete enough

STEP 3
Perform fresh literature review

STEP 4
Choose one target domain

STEP 5
Document source/license/access constraints

STEP 6
Acquire and normalize target corpus

STEP 7
Run ingestion validation

STEP 8
Build target retrieval index

STEP 9
Construct target benchmark

STEP 10
Human-review benchmark

STEP 11
Recompute Oracle-v2

STEP 12
Run frozen retrieval baselines

STEP 13
Run zero-shot router transfer

STEP 14
Run zero-shot V3 failure detector transfer if V3 is complete

STEP 15
Analyze domain shift

STEP 16
Run few-shot adaptation

STEP 17
Run feature ablations

STEP 18
Evaluate end-to-end answers

STEP 19
Run paired statistical analysis

STEP 20
Perform failure inspection

STEP 21
Lock manifests

STEP 22
Decide KEEP / KEEP WITH QUALIFIERS / REJECT / DEFER
```

---

# 75. Repository inspection commands

Start from the current repository state.

```powershell
cd <AtlasRAG-repo>

git status --short

git log --oneline --decorate -10

$env:PYTHONPATH="src"
python -m pytest -q
```

Then inspect the current benchmark and experiment definitions:

```powershell
Get-ChildItem data/bench
Get-ChildItem src/atlasrag/bench
Get-ChildItem scripts
```

Search for current route names and experiment mappings:

```powershell
Select-String -Path src/atlasrag/**/*.py,scripts/*.py -Pattern "SIMPLE|MULTI_HOP|UNCERTAIN|gold_route_v2|oracle_sufficient"
```

Use the repository implementation as the authority for exact current names.

---

# 76. Verify Week 13 completion before V5

Before creating the target domain, confirm the expanded benchmark has:

```text
accepted questions
clean split
human-review status
recomputed Oracle-v2
benchmark hash
```

If Week 13 is unfinished, V5 may remain a planning phase.

Do not build elaborate transfer experiments on a moving benchmark.

---

# 77. Target-domain corpus validation checklist

For the new corpus check:

```text
paper count
successful parsing count
failed parsing count
section count
chunk count
average chunk size
metadata completeness
PDF/text extraction anomalies
```

Persist a machine-readable summary.

Example:

```json
{
  "domain":"target",
  "papers":100,
  "parsed":98,
  "failed":2,
  "chunks":4200
}
```

The exact values must come from the run.

---

# 78. V5 benchmark generation discipline

Reuse the deterministic pair-sourcing logic where it applies.

Keep:

```text
dense + BM25 candidate pools
scientific signal extraction
anchor matching
duplicate penalties
temporal gates
chain ranking
structural evidence checks
```

Do not weaken gates merely to increase benchmark size.

If the target domain does not fit the extractor assumptions, improve the extractor deliberately and record that as its own change.

---

# 79. Generation instrumentation requirement

Every V5 benchmark-generation run should persist:

```text
logical calls
provider calls
cache hits
cache misses
retry attempts
429 count
connection-error count
input tokens
output tokens
rejected candidates
accepted candidates
rejection taxonomy
runtime
```

This closes the instrumentation weakness identified in earlier pair-sourcing work.

---

# 80. Suggested benchmark manifest

Use a manifest such as:

```json
{
  "benchmark":"V5-target",
  "version":"1.0",
  "domain":"target-domain",
  "question_count":0,
  "types":{},
  "paper_count":0,
  "split":"paper-disjoint",
  "generator_version":"...",
  "review_protocol":"...",
  "oracle_version":"v2",
  "sha256":"..."
}
```

Populate actual values only after generation.

---

# 81. Suggested source-domain control

Do not throw away the original domain.

Run a source-domain control using the same code path.

For example:

```text
source validation benchmark
source test benchmark
```

Then compare:

```text
source performance
vs
target performance
```

under identical implementation versions.

This is necessary to distinguish:

```text
normal variance
```

from:

```text
domain-shift degradation
```

---

# 82. Domain balance

If V5 later expands to multiple target domains, avoid allowing one domain to dominate the aggregate result.

Report:

```text
per-domain metrics
macro average
micro average
```

The macro average is useful because each domain gets equal weight.

The micro average reflects aggregate question volume.

Report both when the sample is large enough.

---

# 83. Cross-domain training later

After source→target transfer, a stronger setup is:

```text
Domain A + Domain B + Domain C
             ↓
          training
             ↓
          Domain D
```

This is a leave-one-domain-out experiment.

It tests whether the system can learn domain-general retrieval behavior rather than memorizing one source field.

Do this only after the single-source transfer experiment is understood.

---

# 84. Leave-one-domain-out design

For domains:

```text
A B C D
```

possible runs are:

```text
train A+B+C → test D
train A+B+D → test C
train A+C+D → test B
train B+C+D → test A
```

This is much stronger evidence than a single source→target result.

But it also requires substantially more data and engineering.

Treat it as V5 expansion, not mandatory first-pass work.

---

# 85. Cross-domain adaptation budget

For few-shot experiments keep an explicit budget.

For example:

```text
0%
1%
5%
10%
```

or:

```text
5 / 10 / 25 / 50 labeled target questions
```

Choose whichever is practical and state the budget clearly.

Do not allow arbitrary tuning until the target result looks good.

---

# 86. Hyperparameter tuning discipline

Any target-domain tuning must use:

```text
target validation
```

not:

```text
target test
```

The final target test set should be touched only for final evaluation.

This includes:

```text
thresholds
model depth
learning rate
number of adaptation examples
feature selection
```

---

# 87. No test-set feedback loop

Bad cycle:

```text
run test
↓
see poor result
↓
change threshold
↓
run test
↓
change features
↓
run test
```

This turns the test set into training data.

Correct:

```text
train
↓
validation tuning
↓
lock
↓
test once for final result
```

---

# 88. V5 raw prediction artifact

Store per-question data.

At minimum:

```json
{
  "question_id":"...",
  "domain":"...",
  "system":"v5_zero_shot_router",
  "route":"SIMPLE",
  "confidence":0.83,
  "retrieval_sufficient":true,
  "provider_calls":1,
  "tokens":123,
  "latency_s":1.42
}
```

The exact schema should follow the repository's experiment serialization patterns.

---

# 89. Why provenance matters more in V5

Cross-domain experiments add another dimension:

```text
domain
```

Every number should therefore be traceable to:

```text
question
paper
split
domain
system
run
commit
```

This makes later analysis dramatically easier.

---

# 90. Expected implementation strategy

Keep V5 modular.

Prefer adding components such as:

```text
src/atlasrag/bench/v5_domains.py
src/atlasrag/bench/v5_transfer.py
src/atlasrag/bench/v5_metrics.py
src/atlasrag/bench/v5_manifest.py
```

only if the existing repository structure warrants them.

Do not create duplicate retrieval implementations.

Reuse the current retrieval and experiment APIs.

---

# 91. Tests to add before running expensive experiments

Unit tests should cover:

```text
domain manifest parsing
paper-disjoint split validation
benchmark domain labeling
Oracle-v2 recomputation
transfer configuration loading
feature serialization
missing-feature handling
threshold transfer
run-manifest generation
instrumentation fields
```

Prefer cheap deterministic tests before expensive API calls.

---

# 92. Target-domain ingestion tests

Add at least:

```text
one normal paper
one long paper
one table-heavy paper if available
one paper with equations
one paper with unusual metadata
```

Inspect extraction failures manually.

The test set should not contain corrupt documents merely because they expose interesting edge cases.

---

# 93. Retrieval-state feature portability

For V3 transfer, define a portability matrix:

| Feature | Source available | Target available | Domain-neutral? | Gold leakage? |
|---|---:|---:|---:|---:|
| Top reranker score | yes | yes | likely | no |
| Score gap | yes | yes | likely | no |
| Dense/BM25 overlap | yes | yes | yes | no |
| Unique-paper count | yes | yes | yes | no |
| Raw scientific anchors | yes | domain-dependent | uncertain | no if query/retrieval only |
| Gold-chunk overlap | yes | yes | no | **invalid** |

Treat the table as a review tool, not as established evidence about transfer.

---

# 94. Cross-domain anchor failure analysis

A particularly interesting failure mode is:

```text
same surface token
≠
same scientific meaning
```

Examples can include reused abbreviations or overloaded terms.

The benchmark should contain difficult cases when naturally available, but not fabricate them.

Such cases are useful because they reveal limitations of naive lexical features.

---

# 95. Domain-specific retrievers

Do not introduce a domain-specific embedding model in the first run unless the frozen baseline fails at a fundamental level.

If later evaluated, make it a separate ablation:

```text
frozen general retriever
vs
adapted/domain-specific retriever
```

Otherwise the transfer question becomes impossible to interpret.

---

# 96. V5 and V2 evidence verification

If V2 evidence verification is implemented and stable, a later target-domain experiment can ask:

```text
Does the verifier transfer across domains?
```

But do not mix this into the first V5 transfer experiment.

First establish retrieval/routing transfer.

Then optionally test:

```text
answer
↓
claim extraction
↓
evidence verification
```

The verifier may itself have domain-specific weaknesses.

---

# 97. V5 and V3 interaction

If V3 is complete, the most interesting system may be:

```text
question-only router
        ↓
initial retrieval
        ↓
retrieval-state failure detector
        ↓
escalation
```

under domain shift.

The question becomes:

```text
Does the post-retrieval detector transfer better than the pre-retrieval router?
```

This directly tests the intuition that retrieval-state information may be more stable than pure question-only uncertainty.

Again, this must be measured rather than assumed.

---

# 98. V5 and answer-generation failures

A target-domain answer can fail even if retrieval is correct.

Therefore preserve the decomposition:

```text
retrieval failure
routing failure
answer-generation failure
citation failure
```

Do not score the whole system only by final answer exact match.

---

# 99. V5 presentation figures

Useful figures include:

```text
Figure 1
Source→target experimental setup

Figure 2
Source vs target retrieval quality

Figure 3
Source vs target routing performance

Figure 4
Feature distribution shift

Figure 5
Calibration transfer

Figure 6
Few-shot adaptation curve

Figure 7
Cost/quality frontier

Figure 8
Failure taxonomy
```

Every figure should be generated from saved machine-readable results.

Do not manually edit values in plots.

---

# 100. Recommended final V5 table

A compact final table can look like:

| System | Target evidence recall | Target answer quality | Failure rate | Escalation | Calls/query | p50 latency | p95 latency |
|---|---:|---:|---:|---:|---:|---:|---:|
| Static | ... | ... | ... | ... | ... | ... | ... |
| Strong | ... | ... | ... | ... | ... | ... | ... |
| Zero-shot router | ... | ... | ... | ... | ... | ... | ... |
| Zero-shot V3 | ... | ... | ... | ... | ... | ... | ... |
| Few-shot router | ... | ... | ... | ... | ... | ... | ... |
| Few-shot V3 | ... | ... | ... | ... | ... | ... | ... |

Only populate from final measured artifacts.

---

# 101. Interpretation rules

Use these rules throughout the analysis:

```text
No measured result → no claim.

No held-out test → no generalization claim.

No independent evidence definition → no valid failure label.

No provenance → result is not final.

Different retrieval stack → not a clean transfer comparison.

Target-test tuning → invalidates the clean final test claim.
```

These rules protect the project from overclaiming.

---

# 102. V5 stopping condition

The experiment is complete when:

```text
benchmark is frozen

corpus is frozen

retrieval configuration is frozen

source/target splits are frozen

Oracle-v2 is recomputed

zero-shot transfer is measured

adaptation experiment is measured when justified

raw outputs are saved

statistical comparisons are complete

failure analysis is complete

reproducibility manifest is saved

final V5 decision is written
```

Do not continue optimizing simply because the target number is not attractive.

At that point the research question has been answered as far as the evidence allows.

---

# 103. V5 decision record

Create a small machine-readable or Markdown decision record:

```text
V5 STATUS: KEEP / KEEP WITH QUALIFIERS / REJECT / DEFER

Question:
Can the adaptive policy generalize across scientific domains?

Evidence:
...

Strongest positive result:
...

Strongest limitation:
...

Main failure mode:
...

Required next step:
...
```

This makes the transition to V6 evidence-driven.

---

# 104. Transition to V6

Only after V5 should the next major scientific-representation problem be chosen.

If V5 reveals that failures concentrate around:

```text
tables

equations

units

structured experiments

temporal evidence
```

then V6 can focus on retrieval representations for scientific structure.

For example:

```text
prose retrieval
+
table retrieval
+
equation-aware retrieval
+
temporal evidence handling
```

But V6 should be selected from V5 evidence rather than following a fixed feature wish-list.

---

# 105. Recommended Week 14 deliverables

By the end of the week, aim for:

```text
01_DOMAIN_SELECTION.md
02_V5_BENCHMARK_SPEC.md
03_V5_EXPERIMENT_MATRIX.md
04_V5_RESULTS.md
05_V5_FAILURE_ANALYSIS.md
06_V5_TRANSFER_DECISION.md
```

And corresponding raw artifacts:

```text
data/v5/
experiments/v5/
```

The exact names may follow the project's existing naming conventions.

---

# 106. Minimal first-pass implementation

If the full plan is too large, the scientifically clean minimum is:

```text
one target domain

one target benchmark

paper-disjoint / domain-disjoint split

frozen retrieval

frozen source-trained router

zero-shot evaluation

Oracle-v2 target baseline

paired metrics

manual failure inspection
```

Only after this succeeds should you add:

```text
few-shot adaptation
V3 detector transfer
feature ablations
multi-domain training
```

---

# 107. PowerShell execution skeleton

Use the real repository paths and current script names after inspection.

```powershell
cd <AtlasRAG-repo>

$env:PYTHONPATH="src"

python -m pytest -q

# inspect current repo state
git status --short
git log --oneline --decorate -10

# inspect benchmark artifacts
Get-ChildItem data/bench

# inspect V5-specific code after implementation
Get-ChildItem scripts
Get-ChildItem src/atlasrag/bench
```

Then execute each V5 stage separately and save its output.

Do not run a giant chained command that makes failure diagnosis difficult.

---

# 108. Suggested experiment naming

Use stable IDs such as:

```text
V5-A
V5-B
V5-C
V5-D
V5-E
V5-F
```

and descriptive manifest names such as:

```text
v5-a_target_static.json
v5-b_target_strong.json
v5-c_zero_shot_router.json
v5-d_zero_shot_detector.json
v5-e_fewshot_router.json
v5-f_fewshot_detector.json
```

Do not overwrite old runs.

---

# 109. Git discipline

Before making V5 changes:

```powershell
git status --short
git log --oneline --decorate -10
```

Commit logical changes separately.

For example:

```text
V5 benchmark infrastructure
V5 target corpus support
V5 zero-shot transfer experiments
V5 adaptation experiments
V5 analysis artifacts
```

Do not squash away useful experimental history merely to make the repository look cleaner.

---

# 110. Preserve frozen historical work

Never overwrite:

```text
Run1
V1 benchmark
questions_v1_frozen.jsonl
V4 benchmark snapshots
old experiment results
```

New V5 files must be versioned separately.

The historical record is part of the scientific contribution.

---

# 111. Final V5 mental model

Think of V5 as a stress test.

```text
              SOURCE DOMAIN
                   |
                   v
            learned policy
                   |
                   |
             DOMAIN SHIFT
                   |
                   v
              TARGET DOMAIN
                   |
            ┌──────┴──────┐
            v             v
         retrieval      routing
            |             |
            └──────┬──────┘
                   v
              evidence
                   |
                   v
                 answer
```

The scientific question is not:

```text
Can we make the target result look good?
```

It is:

```text
What survives the shift?
```

That is the purpose of Week 14.

---

# 112. Final execution checklist

Before V5:

```text
[ ] Week 13 benchmark status verified
[ ] target domain selected and justified
[ ] fresh literature review completed
[ ] access/license constraints documented
[ ] target corpus versioned
[ ] ingestion validated
[ ] target benchmark generated
[ ] benchmark human-reviewed
[ ] paper-disjoint split validated
[ ] domain-disjoint split validated
[ ] Oracle-v2 recomputed
[ ] frozen retrieval baseline measured
[ ] frozen router transfer measured
[ ] V3 transfer measured if available
[ ] zero-shot results locked
[ ] few-shot adaptation separated from zero-shot
[ ] feature ablations separated from primary result
[ ] end-to-end answer evaluation completed when justified
[ ] provider instrumentation persisted
[ ] raw per-question outputs saved
[ ] paired statistics completed
[ ] failure taxonomy completed
[ ] transfer decision written
[ ] Git commit recorded
```

---

# 113. Final rule for the next AI agent

Start by inspecting the actual repository and Week 13 status.

Do not assume V5 infrastructure exists.

Do not assume the target domain.

Do not train a router before checking benchmark quality.

Do not tune on the target test set.

Do not silently change retrieval or answer generation.

Do not copy Oracle labels from astrophysics into another domain.

Do not make novelty claims without a fresh literature search.

Do not hide negative transfer.

Do not present a single target-domain result as proof of universal scientific-domain generalization.

The correct workflow is:

```text
verify
↓
choose
↓
freeze
↓
build
↓
audit
↓
measure zero-shot
↓
analyze shift
↓
adapt carefully
↓
measure again
↓
inspect failures
↓
lock evidence
↓
decide honestly
```

That is Week 14.
