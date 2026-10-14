# AtlasRAG — Week 18: V7 Robustness, Cross-Domain Graph Transfer & Stress Testing

## 1. Purpose

Week 17 connected two previously separate research ideas:

```text
V3
retrieval-state-aware failure prediction

+

V7
evidence graph retrieval
```

and introduced:

```text
selective graph escalation
```

The system can now conceptually decide:

```text
cheap retrieval
      ↓
observe retrieval state
      ↓
predict whether stronger evidence acquisition is needed
      ↓
invoke graph retrieval selectively
```

Week 18 is not another feature-building week.

It is the **robustness and transfer stress test**.

The central question becomes:

> **Does the selective graph-escalation behavior survive changes in papers, domains, retrieval conditions, graph quality, and operating thresholds, or does it only work under one narrow experimental setup?**

The purpose is to distinguish:

```text
real methodological behavior
```

from:

```text
benchmark-specific optimization
configuration-specific luck
graph-version artifacts
threshold overfitting
domain-specific heuristics
```

The progression is:

```text
V1
adaptive retrieval routing

        ↓

V2
evidence verification

        ↓

V3
retrieval-failure prediction

        ↓

V4
benchmark expansion

        ↓

V5
cross-domain transfer

        ↓

V6
scientific-structure-aware evidence

        ↓

V7
evidence graph

        ↓

Week 17
selective graph escalation

        ↓

Week 18
robustness + transfer stress testing
```

Do not add another major model unless the existing evidence shows a genuine need.

Week 18 should primarily answer:

```text What survives when we perturb the environment?
```

---

# 2. Why Week 18 is necessary

A selective policy can look strong on a single benchmark for many accidental reasons.

Possible causes include:

```text threshold tuned too closely to one dataset

graph contains unusually clean relations

V3 features happen to match source-domain vocabulary

question types are unbalanced

test papers resemble training papers

one retrieval configuration dominates the result

graph construction quality is unusually high

provider latency happened to be low

a handful of rescue cases drive the average
```

A robustness week tests whether the main result remains visible after controlled changes.

This is essential before making a final research claim.

---

# 3. Primary research question

Primary:

> **Does selective graph escalation retain its evidence-quality and efficiency advantage across unseen papers, domain shift, retrieval perturbations, and reasonable threshold changes?**

Secondary questions:

```text
1. Does the policy generalize to papers not represented during training?

2. Does it generalize to unseen scientific domains?

3. Does graph quality degradation expose instability?

4. Is the selected threshold robust?

5. Does the policy depend strongly on one retrieval model?

6. Does the benefit survive changes in chunk/retrieval depth?

7. Are rescue cases concentrated in a small subset of papers?

8. Does performance collapse when scientific-anchor features shift?

9. Is the graph itself the bottleneck under transfer?

10. Which results remain stable enough for final publication claims?
```

These are hypotheses.

Do not describe them as conclusions before running the tests.

---

# 4. Week 18 is a stress-test week

The core distinction is:

```text Week 17
"What happens?"

Week 18
"Does it keep happening?"
```

Therefore:

```text no architecture rewrite
no benchmark rewriting after test inspection
no threshold tuning on held-out results
no silent retrieval changes
```

The objective is evidence stability.

---

# 5. Frozen primary system

Before Week 18 begins, freeze the main Week 17 condition.

Record:

```text benchmark version
corpus version
graph version
V3 model version
feature version
threshold
retrieval configuration
embedding model
reranker
answer model
answer prompt
generation settings
Git commit
```

This becomes:

```text W18-FROZEN
```

Every robustness experiment begins from this exact configuration.

---

# 6. Historical artifacts remain frozen

Never overwrite:

```text Run1
V1 benchmark
questions_v1_frozen.jsonl
V4 benchmark snapshot
V5 benchmark snapshot
V6 benchmark
V7 graph experiments
Week 17 results
```

Create:

```text Week 18
```

artifacts separately.

Historical results are not disposable.

---

# 7. Robustness dimensions

Week 18 should test several dimensions.

```text A
paper-disjoint robustness

B
domain-disjoint transfer

C
threshold robustness

D
retrieval perturbation robustness

E
graph-quality robustness

F
feature-distribution robustness

G
question-type robustness

H
cost/latency robustness
```

Do not necessarily run every perturbation at full scale.

Prioritize dimensions most relevant to the Week 17 result.

---

# 8. Paper-disjoint robustness

The first test is:

```text train/validate on source papers
test on completely unseen papers
```

This should already be part of the benchmark design where possible.

Week 18 should verify that:

```text no paper overlap
```

is actually true.

Check:

```text paper IDs
DOIs
titles
hashes
source filenames
```

when appropriate.

Do not rely only on filenames.

---

# 9. Near-duplicate paper detection

Scientific literature may contain:

```text preprint
conference version
journal version
updated preprint
supplement
```

These can produce accidental leakage.

Potential detection signals:

```text DOI
title normalization
author overlap
publication metadata
text similarity
```

If near duplicates exist:

```text record them
```

and decide whether they belong in:

```text same paper group
```

for split purposes.

Do not retroactively alter results without documenting the change.

---

# 10. Domain-disjoint transfer

If the V5 target domain exists:

```text source-trained policy
↓
target-domain evaluation
```

should remain frozen for the strictest transfer test.

Specifically preserve:

```text source V3 model
source threshold
graph policy
retrieval configuration
```

No target test tuning.

This is:

```text zero-shot transfer
```

and should be reported separately from:

```text few-shot adaptation
```

---

# 11. Zero-shot transfer hierarchy

A useful hierarchy:

```text T0
frozen retrieval only

T1
frozen V3 selective policy

T2
frozen graph

T3
frozen V3 + frozen graph escalation
```

The most important comparison is:

```text target-domain no-graph
vs
target-domain selective graph
```

This reveals whether the combined policy transfers.

---

# 12. Separate transfer failures

A target-domain failure can originate from:

```text retrieval model
V3 predictor
graph construction
graph relation semantics
threshold calibration
answer generation
```

Do not collapse all of this into:

```text model does not generalize
```

Use a staged diagnosis.

---

# 13. Target-domain graph quality audit

Before interpreting transfer results, measure:

```text node coverage
edge coverage
edge precision
relation distribution
graph density
```

source vs target.

If target graph quality is much lower:

```text graph transfer failure
```

may simply be:

```text graph extraction failure
```

This must be reported separately.

---

# 14. Relation-family transfer

Compare source vs target for:

```text structural
evidential
comparative
temporal
```

and any project-specific families.

For each relation family measure:

```text frequency
precision
coverage
retrieval utility
```

This can reveal:

```text generic relations transfer
domain-specific relations do not
```

or the opposite.

---

# 15. Threshold robustness

The Week 17 policy may select:

```text threshold = τ
```

Week 18 asks:

```text how sensitive is performance around τ?
```

Evaluate nearby thresholds:

```text τ-0.10
τ-0.05
τ
τ+0.05
τ+0.10
```

Use this primarily as a stability analysis.

The final reported test threshold remains:

```text frozen τ
```

unless a new experiment explicitly defines a new calibration protocol.

---

# 16. Do not retune on the robustness test

Bad:

```text observe target-domain failure
↓
change threshold
↓
report improved target result
```

That converts the robustness test into tuning.

Instead:

```text zero-shot target result
```

must remain untouched.

Then, if desired:

```text target validation
↓
new calibrated threshold
↓
separate adapted experiment
```

---

# 17. Few-shot threshold adaptation

A controlled adaptation experiment can use:

```text small target-domain validation set
```

to select a new threshold.

Compare:

```text zero-shot threshold
vs
few-shot threshold
```

The adaptation budget must be fixed before evaluation.

Record:

```text number of target validation questions
```

and:

```text what exactly they were used for
```

---

# 18. Threshold stability metric

Useful summaries include:

```text graph invocation rate
evidence recall
answer correctness
```

for nearby thresholds.

A policy is more stable when:

```text small threshold changes
```

produce:

```text small performance changes
```

unless the benchmark is genuinely too small.

---

# 19. Retrieval perturbation principle

The policy should be tested under reasonable retrieval variations.

Potential controlled changes:

```text dense_k
BM25_k
final_k
reranker on/off
```

where these variations are already supported by the retrieval architecture.

The question is:

```text does the gating policy remain useful
when the initial evidence state changes?
```

This is especially important because V3 operates on retrieval-state features.

---

# 20. Retrieval perturbation design

Do not change every variable simultaneously.

Example sequence:

```text P1
change dense_k

P2
change BM25_k

P3
change final_k

P4
disable reranker
```

Each condition should have a clear interpretation.

Keep:

```text benchmark
graph
V3 model
answer system
```

fixed where possible.

---

# 21. What retrieval perturbation can reveal

Possible result:

```text policy robust across k
```

This suggests:

```text state-based gating may generalize across retrieval depth
```

Another:

```text policy collapses when reranker changes
```

This suggests:

```text V3 is strongly coupled to reranker score distributions
```

That is an important limitation.

---

# 22. Score calibration under retrieval changes

The V3 predictor may use:

```text reranker score
top-1/top-2 gap
```

Changing retrieval/reranker configuration can change their distributions.

Therefore inspect:

```text feature distribution
and
prediction calibration
```

under each perturbation.

Do not assume:

```text same score = same confidence
```

across models/configurations.

---

# 23. Feature normalization

If robustness is poor because of score-scale shifts, a later improvement may be:

```text normalized rank features
percentiles
within-query normalization
```

But do not introduce them before diagnosing the failure.

Week 18 should first answer:

```text what broke?
```

before:

```text how do we fix it?
```

---

# 24. Graph-quality perturbation

The graph itself should be stress-tested.

Potential simulated degradation:

```text remove a small fraction of edges
remove low-confidence edges
inject controlled false-positive edges
```

The perturbation must be deterministic and documented.

The purpose is to estimate:

```text tolerance to graph imperfections
```

not to create arbitrary failure.

---

# 25. Edge removal experiment

A clean experiment:

```text graph v1
↓
remove x% of eligible edges
↓
run retrieval
```

with:

```text x ∈ {5%,10%,20%}
```

or another predefined range.

Measure:

```text evidence recall
rescue rate
regression rate
```

This tells you how brittle the graph is to:

```text missing relations
```

---

# 26. False-edge injection experiment

A controlled stress test can add:

```text small number of incorrect relations
```

such as:

```text same-domain wrong entity
wrong temporal direction
same topic wrong quantity
```

Do not use random garbage.

The goal is to simulate realistic extraction errors.

Measure:

```text when does graph noise begin to damage retrieval?
```

---

# 27. Graph precision/recall tradeoff

Graph quality can produce:

```text sparse/high-precision graph
```

or:

```text dense/lower-precision graph
```

Week 18 can study:

```text graph precision
vs
retrieval utility
```

This may reveal a useful operating region.

Do not optimize graph density for aesthetics.

---

# 28. Feature-distribution robustness

V3 depends on retrieval-state features.

For each major feature compare:

```text source train
source validation
source test
target test
perturbed retrieval
```

Examples:

```text top reranker score
score gap
dense/BM25 overlap
paper diversity
anchor coverage
```

Look for large distribution shifts.

---

# 29. Scientific-anchor sensitivity

If the model uses scientific-anchor features, assess:

```text source domain anchor coverage
target domain anchor coverage
```

A large drop may produce:

```text false failure predictions
```

even when retrieval is adequate.

This is evidence of:

```text domain-sensitive feature dependence
```

not necessarily a failure of selective retrieval itself.

---

# 30. Feature ablation under transfer

A useful transfer study:

```text no-anchor model
anchor-enabled model
```

on target data.

If:

```text removing anchors improves target transfer
```

then the anchor features may be:

```text too domain-specific
```

This is a concrete, testable finding.

---

# 31. Paper-count sensitivity

A policy can be affected by:

```text corpus scale
```

For example:

```text small corpus
```

may make:

```text top-k evidence
```

more concentrated.

A useful robustness analysis can compare:

```text subset corpus
vs
full corpus
```

if the evaluation design permits.

Do not change the benchmark answers or labels.

---

# 32. Corpus perturbation

Possible controlled perturbations:

```text remove a paper
remove a near-duplicate
remove citation-connected papers
```

Only use perturbations that preserve a valid answerable benchmark.

The purpose is:

```text test whether the system is overly dependent on specific distractor/evidence papers
```

Do not delete gold evidence and then call the result a system failure.

---

# 33. Answerable vs unanswerable cases

Distinguish:

```text retrieval-insufficient because evidence was missed
```

from:

```text corpus truly lacks sufficient evidence
```

A graph cannot retrieve evidence that is absent.

This distinction should remain central in all robustness analysis.

---

# 34. Benchmark preservation under perturbation

For every perturbation:

```text verify gold evidence availability
```

If a perturbation removes:

```text only valid source evidence
```

then the question becomes:

```text structurally unanswerable
```

It must be excluded or separately reported.

Do not mix:

```text system retrieval failure
```

with:

```text benchmark invalidation
```

---

# 35. Question-order robustness

Question ordering should not affect:

```text deterministic retrieval
graph traversal
policy decisions
```

unless the system intentionally has state.

Test repeated runs or shuffled question orders where practical.

This can catch:

```text cache contamination
mutable state
non-deterministic indexing
```

---

# 36. Seed and determinism checks

Record:

```text random seed
model generation settings
retrieval determinism
graph traversal determinism
```

If the model contains stochastic components:

```text document the variability
```

Do not silently average different settings.

---

# 37. Provider robustness

Provider-side variability can affect:

```text LLM extraction
LLM answers
latency
rate limits
```

The primary scientific analysis should keep:

```text provider
model
temperature
prompt
```

fixed.

A later robustness check can compare providers only if that question matters.

Do not turn Week 18 into an uncontrolled provider benchmark.

---

# 38. Rate-limit and partial-run protocol

The existing bounded retry behavior remains mandatory.

For each run:

```text bounded retries
explicit failure state
run summary
partial status
```

If 429s occur:

```text stop cleanly after configured attempts
```

and preserve the run.

Never silently convert:

```text provider failure
```

into:

```text model failure
```

---

# 39. Instrumentation required

Each run should persist:

```text logical calls
provider calls
cache hits
cache misses
retry attempts
rate-limit errors
connection errors
prompt tokens
completion tokens
latency
```

For graph-specific work also:

```text graph invocations
graph traversal time
nodes expanded
edges traversed
graph-added evidence
```

This is essential for comparing operating costs under stress.

---

# 40. Cost robustness

A policy may remain accurate but become expensive under a perturbed setting.

For each condition report:

```text evidence recall
graph invocation rate
tokens/query
provider calls/query
p50 latency
p95 latency
```

Do not define robustness only through accuracy.

Operational instability matters.

---

# 41. Latency-tail analysis

Selective policies can create a long latency tail because:

```text rare difficult queries
→ graph expansion
→ more reranking
→ more answer context
```

Therefore compare:

```text p50
p95
```

and, where useful:

```text worst 5%
```

Do not optimize only average latency.

---

# 42. Rescue-case concentration

Count:

```text graph rescues per paper
```

A strong average may come from:

```text 2 papers
```

with unusually many difficult questions.

Inspect:

```text paper-level rescue concentration
```

and report it.

This prevents over-generalization.

---

# 43. Bootstrap by question

Confidence intervals should resample:

```text questions
```

rather than:

```text individual retrieved chunks
```

when the unit of evaluation is the question.

This preserves the paired nature of the experiment.

---

# 44. Bootstrap by paper

When paper clustering is strong, a secondary analysis can resample:

```text papers
```

to understand:

```text how dependent results are on particular sources
```

This can be especially valuable for:

```text cross-domain
```

and:

```text paper-disjoint
```

claims.

---

# 45. Statistical stability

Compare:

```text full benchmark estimate
```

against:

```text bootstrap distribution
```

and report:

```text median
confidence interval
```

if useful.

If the interval is extremely wide:

```text state clearly that the benchmark is still underpowered
```

Do not overinterpret point estimates.

---

# 46. Robustness decision hierarchy

The final Week 18 interpretation should distinguish:

```text ROBUST
```

meaning behavior persists across reasonable perturbations.

```text CONDITIONAL
```

meaning benefit exists only under certain conditions.

```text BRITTLE
```

meaning small changes destroy the result.

```text UNRESOLVED
```

meaning the data is insufficient.

This is more informative than:

```text works / does not work
```

---

# 47. Main robustness matrix

Build a matrix such as:

```text
Condition
Base
Paper-disjoint
Target-domain
Threshold -0.05
Threshold +0.05
Different dense_k
Different final_k
Reranker off
Graph edge removal
Graph noise
```

For each:

```text evidence recall
graph invocation
answer quality
cost
latency
```

Only include perturbations that are actually run.

---

# 48. Primary comparison

The primary Week 18 comparison remains:

```text frozen selective graph
```

versus:

```text frozen no-graph baseline
```

under each stress condition.

Then compare:

```text selective graph
```

with:

```text always graph
```

when useful.

---

# 49. Robustness score caution

It may be tempting to create:

```text one robustness score
```

Do not do this immediately.

A single score can hide:

```text quality collapse
```

in one domain while preserving:

```text low average degradation
```

Prefer a matrix of metrics.

A summary score can be a secondary analysis only if carefully justified.

---

# 50. Domain transfer result table

If V5/V17 target-domain evaluation exists:

```text
System
Source evidence recall
Target evidence recall
Source graph rate
Target graph rate
Source cost
Target cost
```

and:

```text transfer gap =
source metric - target metric
```

The gap is itself informative.

---

# 51. Transfer degradation decomposition

Suppose target evidence recall falls.

Decompose:

```text retrieval degradation
+
graph degradation
+
policy degradation
+
generation degradation
```

Use staged controls.

For example:

```text target no-graph
target always-graph
target selective-graph
```

can identify whether:

```text graph
```

still helps even if:

```text base retrieval
```

is weaker.

---

# 52. Graph transfer without policy transfer

A useful diagnostic:

```text target always graph
```

If this is strong but:

```text target selective graph
```

is weak,

then:

```text graph transfers
but
V3 gating does not
```

This is a valuable decomposition.

---

# 53. Policy transfer without graph transfer

Conversely:

```text target selective policy
```

may behave reasonably while:

```text target graph itself
```

is weak.

Then:

```text gating transfers
but
graph representation does not
```

Again, this is much more informative than:

```text target score decreased
```

---

# 54. Retrieval perturbation diagnosis

If a retrieval change causes failure:

```text compare always-graph
```

and:

```text no-graph
```

If both collapse:

```text retrieval bottleneck
```

If only selective graph collapses:

```text gating sensitivity
```

If graph remains strong but selective becomes weak:

```text policy calibration issue
```

This diagnostic tree should guide any follow-up work.

---

# 55. Graph perturbation diagnosis

If edge removal causes a drop:

```text missing-edge sensitivity
```

If false-edge injection causes a drop:

```text graph precision sensitivity
```

If both have little effect:

```text graph may not be contributing strongly
```

These are hypotheses to inspect.

---

# 56. Robustness to context budget

Repeat at least one important comparison under:

```text small context
medium context
```

if the implementation supports it.

The question is:

```text does graph still help when evidence budget is constrained?
```

A graph that only helps at extremely large context budgets may have limited practical value.

---

# 57. Robustness to final-k

If:

```text final_k = 5
```

versus:

```text final_k = 10
```

changes the graph effect substantially, that should be reported.

Graph retrieval may be especially sensitive to:

```text candidate competition
```

and:

```text evidence completeness
```

under small budgets.

---

# 58. Robustness to graph expansion depth

If Week 17 used:

```text one hop
```

test whether:

```text one hop
```

is already sufficient.

Only evaluate:

```text two hop
```

as a secondary experiment.

Do not make deep traversal the default merely because it raises recall.

---

# 59. Efficiency-normalized robustness

For each stress condition, ask:

```text Does selective graph still improve recall per unit cost?
```

A policy that retains:

```text +quality
```

but incurs:

```text 3× cost
```

may not be preferable.

Use measured cost.

---

# 60. Failure analysis sample

For every major robustness failure, capture:

```text question
condition
initial retrieval
V3 probability
graph decision
graph path
final evidence
answer
root cause
```

This is essential for final discussion.

---

# 61. Robustness failure taxonomy

Suggested categories:

```text R1 threshold instability
R2 feature distribution shift
R3 retrieval configuration dependence
R4 graph quality dependence
R5 domain vocabulary shift
R6 relation-schema mismatch
R7 benchmark concentration
R8 provider variability
R9 context-budget sensitivity
R10 generation bottleneck
```

Use only categories actually observed.

Do not invent explanations before inspection.

---

# 62. Outlier analysis

Inspect:

```text largest graph gains
largest graph regressions
largest latency increases
highest-cost queries
```

These often reveal mechanisms hidden by averages.

Do not remove outliers merely because they make the graph look worse.

An outlier is a potential explanation.

---

# 63. Robustness and answer evaluation

Once retrieval robustness is established, rerun a smaller answer-evaluation subset if full evaluation is expensive.

Prioritize:

```text major rescue cases
major regression cases
domain-shift failures
```

Do not silently change the answer evaluator.

---

# 64. Human review of robustness failures

Human review should focus on:

```text graph-beneficial cases
graph-harmful cases
borderline threshold cases
cross-domain failures
```

The objective is to determine:

```text actual scientific evidence failure
```

rather than:

```text metric artifact
```

---

# 65. Benchmark contamination audit

Before finalizing Week 18, check for:

```text duplicate questions
near-duplicate questions
paper overlap
answer text leakage
gold evidence leakage
benchmark-generation contamination
```

If contamination is found:

```text document it
repair if justified
rerun affected experiments
```

Do not silently delete inconvenient examples.

---

# 66. Target-domain benchmark contamination

For zero-shot target transfer:

```text target test questions
```

must not have influenced:

```text graph extraction prompts
V3 training
threshold selection
answer prompt tuning
```

The target corpus itself may be needed to build a deployed retrieval index.

That is different from:

```text using target labels to tune the policy
```

Maintain this distinction.

---

# 67. Graph construction timing

A target-domain graph can be built before evaluation because:

```text graph is part of the retrieval system
```

provided:

```text no target benchmark annotations
```

are used.

Record:

```text corpus-only graph construction
```

to make this explicit.

---

# 68. Robustness to graph version

If multiple graph schema versions exist:

```text evaluate only one frozen version
```

for the primary result.

Other versions should be:

```text secondary ablations
```

Do not switch graph versions question-by-question.

---

# 69. Robustness to feature version

Similarly:

```text feature extractor v1
```

must remain fixed during a particular experiment.

If feature bugs are fixed:

```text feature extractor v2
```

becomes a new experiment version.

Preserve:

```text v1 results
```

for chronology.

---

# 70. Robustness to benchmark versions

The same rule applies to:

```text V4 benchmark
V5 benchmark
V6 benchmark
V7 benchmark
```

Maintain separate manifests.

Do not mix question files simply because:

```text IDs overlap
```

or:

```text filenames look similar
```

---

# 71. Reproducibility manifest

A Week 18 manifest should record:

```text experiment_id
base_experiment
perturbation
benchmark_version
corpus_version
graph_version
V3_model_version
feature_version
threshold
retrieval_config
answer_model
prompt_version
git_commit
```

and runtime:

```text provider
calls
tokens
latency
errors
```

---

# 72. Exact run naming

Suggested:

```text
W18-A-PAPER_DISJOINT
W18-B-TARGET_ZERO_SHOT
W18-C-THRESHOLD_ROBUSTNESS
W18-D-RETRIEVAL_K
W18-E-RERANKER_OFF
W18-F-GRAPH_EDGE_DROP
W18-G-GRAPH_FALSE_EDGES
W18-H-CONTEXT_BUDGET
```

Use actual run names consistently.

---

# 73. Do not run all perturbations blindly

A good prioritization is:

```text 1
paper/domain transfer

2
threshold robustness

3
retrieval perturbation

4
graph quality perturbation

5
context-budget robustness
```

Stop when evidence is already sufficient to answer the robustness question.

Do not create dozens of low-value experiments.

---

# 74. Robustness stopping rule

A reasonable stopping condition:

```text primary result stable
+
major expected perturbations tested
+
failure mechanisms understood
```

Do not continue searching for:

```text one magical setting
```

that produces a better headline number.

The goal is confidence, not optimization.

---

# 75. No post-hoc rescue

If a robustness experiment fails:

```text record failure
```

before changing anything.

A later repair can be:

```text new experiment
```

with:

```text new version
```

It cannot overwrite:

```text original robustness result
```

---

# 76. Robustness vs optimization

The distinction should stay explicit.

Optimization asks:

```text What configuration is best?
```

Robustness asks:

```text Does our conclusion survive reasonable configuration changes?
```

Week 18 is primarily the second.

---

# 77. Final claim stability

At the end, classify each planned claim:

```text SUPPORTED
PARTIALLY_SUPPORTED
NOT_SUPPORTED
UNTESTED
```

Examples:

```text selective graph improves evidence recall
graph benefit transfers to unseen domain
V3 gating remains calibrated under shift
graph relations are robust to extraction noise
```

Only:

```text measured claims
```

should enter the final paper.

---

# 78. Evidence hierarchy for final claims

Strongest evidence:

```text preregistered / predefined primary comparison
+
paper-disjoint test
+
independent benchmark
+
paired statistics
+
raw per-question outputs
```

Weaker:

```text exploratory ablation
```

Weakest:

```text anecdotal rescue example
```

Use the strongest available evidence for the main claims.

---

# 79. Final Week 18 result table

A strong final table could contain:

```text
Condition
Evidence Recall
Graph Invocation
Rescue Rate
Regression Rate
Answer Correctness
Citation Quality
Cost / Query
p50
p95
```

and a separate robustness table:

```text
Perturbation
Δ Evidence Recall
Δ Graph Rate
Δ Cost
Δ Latency
Interpretation
```

---

# 80. Robustness plot set

Keep the figure set focused.

Recommended:

```text Figure 1
quality-cost frontier across thresholds

Figure 2
source vs target-domain performance

Figure 3
robustness under retrieval/graph perturbations
```

A fourth figure can show:

```text rescue/regression by question type
```

if useful.

Do not create plots merely because the data can be plotted.

---

# 81. Statistical interpretation

For every important robustness comparison report:

```text absolute difference
confidence interval
sample size
```

Where appropriate:

```text paired test
```

Do not compare intervals visually and call that a significance test.

---

# 82. Multiple comparison discipline

There may be many stress conditions.

Define:

```text primary robustness dimensions
```

before final analysis.

For example:

```text target-domain
threshold neighborhood
retrieval depth
graph edge quality
```

Other experiments can remain:

```text exploratory
```

This avoids cherry-picking favorable perturbations.

---

# 83. Negative transfer

If target performance is worse:

```text do not hide it
```

Report:

```text source result
target result
absolute gap
relative gap
root cause hypothesis
```

Then determine whether:

```text zero-shot transfer
```

should remain a claim.

---

# 84. What a strong negative result can mean

Suppose:

```text source:
selective graph works

target:
selective graph fails

target always-graph:
works
```

Then the useful conclusion may be:

```text graph mechanism transfers better than gating calibration
```

This can motivate:

```text cross-domain threshold adaptation
```

without claiming:

```text universal transfer
```

---

# 85. Another negative pattern

Suppose:

```text target no-graph:
weak

target always-graph:
weak

target selective-graph:
weak
```

Then:

```text retrieval / corpus / graph construction
```

is likely the bottleneck.

The policy itself cannot compensate.

This prevents wasting time on threshold tuning.

---

# 86. Graph-noise robustness interpretation

If:

```text 10% false edges
```

barely affects results, that suggests:

```text retrieval may be tolerant to moderate graph noise
```

If a tiny amount of noise causes collapse:

```text graph precision is a critical engineering requirement
```

Both are valuable findings.

Do not extrapolate beyond tested noise levels.

---

# 87. Missing-edge robustness interpretation

If removing edges causes:

```text graceful degradation
```

the graph may have redundancy.

If removing a small number causes:

```text severe collapse
```

the graph may contain critical single points of failure.

Inspect:

```text which relations matter
```

before concluding.

---

# 88. Threshold robustness interpretation

If nearby thresholds have similar:

```text recall
cost
```

the policy is operationally stable.

If tiny changes create large swings:

```text policy may be poorly calibrated
```

or:

```text benchmark may be too small
```

Distinguish these possibilities.

---

# 89. Feature shift interpretation

If feature distributions shift but performance remains stable:

```text robust decision function
```

If they shift and performance collapses:

```text distribution-sensitive policy
```

This is a stronger analysis than simply reporting target accuracy.

---

# 90. Retrieval-model coupling

If changing reranker causes major policy degradation:

```text V3 may be calibrated to one score distribution
```

Possible future improvement:

```text rank-normalized features
```

but defer implementation until after Week 18 diagnosis.

---

# 91. Domain-generalization interpretation

A strong V5/V18 story would look like:

```text source domain
good selective performance

unseen target domain
similar quality/cost behavior

retrieval-state features remain useful

graph relations remain sufficiently reliable
```

A weaker but still valuable result is:

```text zero-shot weak
few-shot recalibration restores performance
```

This supports:

```text limited adaptation requirement
```

rather than:

```text zero-shot universality
```

---

# 92. Final decision categories

At the end of Week 18 classify the entire V7 selective policy as:

```text ROBUST

CONDITIONALLY ROBUST

BRITTLE

UNRESOLVED
```

Then choose the broader roadmap status:

```text KEEP
KEEP WITH QUALIFIERS
REVISE
DEFER
REJECT
```

Use evidence, not intuition.

---

# 93. Recommended follow-up from each outcome

### ROBUST

Proceed to:

```text final end-to-end evaluation
```

### CONDITIONALLY ROBUST

Proceed while explicitly limiting claims.

### BRITTLE

Investigate the dominant failure source:

```text retrieval
graph
features
threshold
domain transfer
```

### UNRESOLVED

Expand:

```text benchmark
paper coverage
audit sample
```

before claiming anything.

---

# 94. Week 18 deliverables

Recommended documents:

```text
01_W18_ROBUSTNESS_SPEC.md
02_W18_TRANSFER_AUDIT.md
03_W18_PERTURBATION_MATRIX.md
04_W18_RESULTS.md
05_W18_FAILURE_ANALYSIS.md
06_W18_STATISTICAL_ANALYSIS.md
07_W18_ROBUSTNESS_DECISION.md
```

Raw artifacts:

```text
data/w18/
experiments/w18/
```

Figures:

```text figures/w18/
```

Use current naming conventions where applicable.

---

# 95. Recommended execution sequence

```text 1. inspect final Week 17 result

2. freeze Week 17 primary system

3. verify benchmark/split integrity

4. verify graph provenance

5. verify V3 model/version

6. run paper-disjoint audit

7. run zero-shot target-domain evaluation

8. run threshold robustness on validation

9. lock threshold

10. evaluate frozen threshold

11. run retrieval perturbations

12. run graph-quality perturbations

13. run context-budget perturbation

14. measure provider/cost/latency behavior

15. inspect rescue/regression cases

16. perform human audit

17. compute paired statistics

18. classify robustness

19. lock raw artifacts

20. write final decision
```

Do not change the base policy halfway through the sequence.

---

# 96. PowerShell starting point

Use:

```powershell
cd <AtlasRAG-repo>

$env:PYTHONPATH="src"

python -m pytest -q

git status --short
git log --oneline --decorate -10
```

Then inspect:

```powershell
Get-ChildItem data
Get-ChildItem scripts
Get-ChildItem src/atlasrag
```

Verify actual paths before running anything.

---

# 97. Git workflow

Before experiments:

```powershell
git status --short
git diff
```

During work:

```text logical commit
↓
experiment
↓
analysis artifact
```

Suggested commits:

```text W18 robustness infrastructure

W18 transfer audit

W18 perturbation experiments

W18 analysis tooling

W18 final robustness results
```

Do not hide the development history.

---

# 98. Tests before full runs

At minimum test:

```text threshold boundary

paper split integrity

domain split integrity

graph version consistency

feature version consistency

experiment manifest generation

partial-run status

provider failure accounting
```

Then:

```powershell
python -m pytest -q
```

Record the result.

---

# 99. Pilot-first execution

Before full experiments run:

```text 5–10 representative questions
```

through the primary robustness condition.

Check:

```text correct benchmark version
correct graph
correct V3 model
correct threshold
correct decision
correct logging
```

Only then launch the full run.

---

# 100. Partial-run handling

If a run stops because of:

```text provider 429
connection failure
crash
manual interruption
```

mark:

```text PARTIAL
```

and preserve partial output.

Do not treat missing queries as:

```text failure
```

or:

```text success
```

until the run has been correctly reconciled.

---

# 101. Output reconciliation

Before computing final results verify:

```text expected questions
=
completed + failed + skipped
```

and:

```text no duplicate question IDs
```

Also verify:

```text every reported metric references the intended benchmark version
```

This catches many experiment bookkeeping errors.

---

# 102. No test contamination through robustness selection

Do not choose which perturbations to highlight only after seeing which are favorable.

The final report should explain:

```text planned perturbations
```

and distinguish:

```text planned
exploratory
```

experiments.

This increases credibility.

---

# 103. Robustness analysis as final evidence

The purpose of Week 18 is to make the final claim more conservative.

The final statement should become something like:

```text Under the evaluated paper-disjoint and domain-shift settings, the selective graph policy remained useful across the tested perturbations, with degradation concentrated in ...
```

or:

```text The selective graph policy was beneficial on the primary benchmark but showed substantial sensitivity to ...
```

These are evidence-aligned statements.

---

# 104. What not to do

Do not:

```text tune threshold on the robustness test

modify the graph after seeing failures

remove difficult target-domain questions

drop outlier papers

change reranker and graph simultaneously

change answer model mid-study

pretend partial provider runs are complete

collapse transfer and within-domain results

report only the best perturbation

hide negative transfer

claim robustness from one extra run

call a policy universal
```

---

# 105. Final Week 18 mental model

Think of the full system as:

```text
                 QUESTION
                    |
                    v
              INITIAL ROUTE
                    |
                    v
             INITIAL RETRIEVAL
                    |
                    v
          RETRIEVAL-STATE FEATURES
                    |
                    v
             V3 FAILURE MODEL
                    |
             ┌──────┴──────┐
             |             |
       sufficient       uncertain/failure
             |             |
             v             v
          baseline       graph
                         expansion
             |             |
             └──────┬──────┘
                    v
              FINAL EVIDENCE
                    |
                    v
                  ANSWER
                    |
                    v
             V2 VERIFICATION
```

Week 18 wraps around this system:

```text source papers
target papers
retrieval perturbations
graph perturbations
threshold changes
domain shift
```

and asks:

```text does the behavior survive?
```

---

# 106. Final rule for the next AI agent

Start by inspecting the actual Week 17 results.

Do not assume the selective graph policy deserves further optimization.

Do not tune on the robustness test.

Do not silently repair failures.

Do not change the benchmark because a perturbation makes questions unanswerable.

Do not confuse retrieval failure with graph failure.

Do not confuse graph failure with V3 failure.

Do not confuse domain shift with answer-generation failure.

Do not remove outliers because they are inconvenient.

Do not claim robustness from a single additional configuration.

Do not call zero-shot and few-shot transfer the same result.

Do not hide provider failures or partial runs.

Do not overwrite Week 17 artifacts.

The correct workflow is:

```text
inspect
↓
freeze
↓
audit splits
↓
test zero-shot transfer
↓
test threshold neighborhood
↓
test retrieval perturbations
↓
test graph-quality perturbations
↓
test context-budget sensitivity
↓
measure quality + cost + latency
↓
inspect rescues/regressions
↓
audit representative failures
↓
compute paired statistics
↓
classify robustness
↓
lock evidence
↓
decide what claims survive
```

That is Week 18.
