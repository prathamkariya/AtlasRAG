# AtlasRAG — Week 22: V8 Controlled Research Execution

## 1. Purpose

Week 21 ended with a deliberate constraint:

```text
do not invent V8
```

The purpose of Week 21 was to inspect the released AtlasRAG evidence, identify the strongest unresolved bottleneck, perform a fresh literature review, compare candidate directions, and freeze exactly one primary V8 research question before implementation.

Week 22 begins only after that specification is actually locked.

The central principle is:

> **V8 is a new controlled research cycle built on the released AtlasRAG system. It must change one clearly defined research variable, preserve the released baseline, and produce evidence that can be independently interpreted.**

The workflow is:

```text
V8 specification
      ↓
baseline verification
      ↓
benchmark/data preparation
      ↓
minimal implementation
      ↓
unit tests
      ↓
smoke test
      ↓
pilot
      ↓
full controlled experiment
      ↓
raw result lock
      ↓
analysis
```

Do not jump from:

```text idea
```

to:

```text final result
```

without the intermediate controls.

---

# 2. Precondition: V8 must already be selected

Before doing substantial work, verify that Week 21 produced:

```text
V8_RESEARCH_QUESTION
V8_HYPOTHESIS
V8_BASELINE
V8_BENCHMARK_PLAN
V8_PRIMARY_METRIC
V8_LEAKAGE_CONTROLS
V8_BUDGET
```

If any of these are missing:

```text stop
```

and finish the specification first.

Do not choose a new research direction while implementing another one.

---

# 3. V8 is a separate research cycle

Keep the released first-cycle AtlasRAG system intact.

Conceptually:

```text
AtlasRAG Release v1
        |
        └────→ V8 research branch / experiment
```

The V8 work may reuse:

```text code
benchmarks
configs
models
infrastructure
```

but the release itself must remain reproducible.

Do not mutate the released state and later call that:

```text original release
```

---

# 4. Define the exact intervention

Write one sentence:

> **The V8 intervention changes ______ while keeping ______ fixed.**

Examples of valid structure:

```text intervention:
new table representation

fixed:
embedding, reranker, answer model, benchmark
```

or:

```text intervention:
new graph edge filtering rule

fixed:
graph nodes, retrieval stack, answer model, benchmark
```

or:

```text intervention:
new calibration method

fixed:
retrieval model, predictor, benchmark, graph
```

The exact intervention depends on the Week 21 selection.

---

# 5. Independent variable discipline

Identify:

```text primary independent variable
```

and:

```text controlled variables
```

Do not let the experiment accidentally vary:

```text retrieval
+
answer model
+
prompt
+
benchmark
+
intervention
```

at once.

If multiple changes are necessary for the intervention to function, document them as:

```text one composite intervention
```

and acknowledge the attribution limitation.

---

# 6. Hypothesis structure

The V8 hypothesis should contain:

```text H1
expected outcome

Mechanism
why the intervention should affect it

Primary metric
what will measure the effect

Counter-hypothesis
why the intervention may not help

Failure condition
what result would count against the idea
```

This prevents a vague goal such as:

```text make AtlasRAG better
```

from becoming the experimental question.

---

# 7. Baseline lock

The V8 baseline should normally be:

```text released AtlasRAG system
```

or a clearly specified validated subset of it.

Record:

```text Git commit/tag
benchmark version
corpus version
configuration
models
prompts
graph version
V3 version
V2 version
```

The baseline must be reproducible before V8 is evaluated.

---

# 8. Baseline reproduction

Before implementing the intervention:

```text run the baseline
```

on a small representative subset.

Verify:

```text outputs match expected structure
result schema is correct
metrics can be reproduced
provider accounting works
```

If the baseline has silently drifted:

```text stop
```

and resolve the discrepancy first.

Do not compare:

```text new V8 system
```

against an unverified baseline.

---

# 9. Benchmark decision

Use the final released benchmark when it adequately tests V8.

Create a new:

```text V8 benchmark
```

only if the selected research question requires evidence the released benchmark cannot provide.

Examples:

```text new evidence structure
new relation family
new domain
new failure class
```

Do not create a new benchmark merely because it may be easier.

---

# 10. Benchmark versioning

If a V8 benchmark is required, record:

```text version
question count
paper count
domain count
question-type distribution
gold evidence definition
annotation version
split
hash
```

Never overwrite the release benchmark.

---

# 11. Benchmark generation

If new questions are needed:

```text candidate generation
↓
automatic filtering
↓
support audit
↓
human review
↓
retrieval sufficiency
↓
final freeze
```

Reuse the benchmark-quality lessons from earlier AtlasRAG work.

Do not lower review standards because V8 has a small time budget.

---

# 12. Benchmark leakage audit

Before finalizing the V8 benchmark, inspect:

```text duplicate questions
near duplicates
paper overlap
answer leakage
gold evidence leakage
training/test contamination
question-specific rules
```

The intervention must never receive:

```text gold evidence
gold path
gold answer
test label
```

unless the research question explicitly requires such information.

---

# 13. Paper-disjoint split

Whenever model training is involved:

```text paper-disjoint split
```

is preferred.

Possible:

```text train papers
validation papers
test papers
```

No paper should accidentally appear in both training and final evaluation through:

```text preprint/journal duplication
```

or another near-duplicate.

---

# 14. Domain-disjoint split

If V8 includes transfer:

```text train domains
validation domains
test domain
```

where feasible.

Keep:

```text zero-shot
few-shot
fine-tuned
```

conditions separate.

Do not call few-shot adaptation:

```text zero-shot generalization
```

---

# 15. Implementation principle

Implement the smallest possible change needed to test the hypothesis.

Before coding:

```text locate reusable existing modules
```

Do not rewrite:

```text retrieval stack
graph store
benchmark loader
answer pipeline
```

if existing abstractions already work.

A good V8 implementation should add:

```text minimal new surface area
```

rather than a second AtlasRAG codebase.

---

# 16. Architecture boundary

Keep the intervention isolated.

Conceptually:

```text released baseline
       ↓
 V8 intervention
       ↓
 final evidence/result
```

The baseline path should remain callable independently.

This enables:

```text direct paired comparison
```

without duplicating the whole application.

---

# 17. Suggested module strategy

Only if the repository lacks equivalent abstractions, create a dedicated namespace such as:

```text
src/atlasrag/v8/
    __init__.py
    config.py
    method.py
    evaluation.py
```

and:

```text
scripts/run_v8.py
scripts/analyze_v8.py
```

Use the actual project architecture where a matching abstraction already exists.

Do not create unnecessary duplicate utilities.

---

# 18. Configuration separation

Use a dedicated V8 configuration file or clearly versioned section.

Record:

```text V8 method parameters
baseline parameters
evaluation parameters
```

Do not mutate:

```text released config
```

just to run V8.

---

# 19. Test-first implementation

Before the full experiment, add tests for:

```text intervention behavior
input/output schema
edge cases
configuration loading
failure handling
determinism
```

Then run:

```powershell
python -m pytest -q
```

Do not proceed on:

```text known failing tests
```

unless they are unrelated and explicitly documented.

---

# 20. Regression-test the released path

V8 must not silently break the baseline.

Run:

```text existing test suite
```

and at least one:

```text baseline smoke test
```

after implementation.

If baseline behavior changes unexpectedly:

```text investigate
```

before V8 evaluation.

---

# 21. Smoke test

Run:

```text 3–10 questions
```

covering the central V8 task.

Check:

```text benchmark ID
baseline result
V8 result
provenance
runtime
tokens
failure status
```

Do not launch a large provider-backed run until the smoke test behaves correctly.

---

# 22. Pilot experiment

A pilot should answer:

```text does the intervention execute correctly?
does the evaluation pipeline score it correctly?
is the result schema complete?
are costs within expectation?
```

Use a small subset.

The pilot is:

```text engineering validation
```

not:

```text evidence for the final research claim
```

unless explicitly defined as part of the study.

---

# 23. Pilot stopping condition

Stop the pilot if:

```text wrong outputs
missing logs
unexpected provider calls
large latency spike
broken provenance
evaluation mismatch
```

Fix the implementation before the full experiment.

---

# 24. Instrumentation

Every V8 experiment should persist:

```text logical calls
provider calls
cache hits
cache misses
retry attempts
RateLimitError count
APIConnectionError count
prompt tokens
completion tokens
latency
final status
```

Add intervention-specific fields according to the chosen research question.

---

# 25. Why instrumentation matters

A method can appear cheaper because:

```text cache hits are ignored
failed calls disappear
retries are not counted
only successful queries are included
```

This is unacceptable.

All systems must use the same accounting definitions.

---

# 26. Runtime status model

Use explicit states such as:

```text COMPLETE
PARTIAL
FAILED
SKIPPED
```

Do not silently convert:

```text provider failure
```

into:

```text model error
```

or:

```text omitted row
```

---

# 27. Bounded retry behavior

Continue the project's bounded retry strategy.

For provider-backed runs:

```text finite retry attempts
finite backoff
explicit terminal state
```

If limits are reached:

```text record failure
```

and continue or stop according to the experiment policy.

Do not retry indefinitely.

---

# 28. Full experiment matrix

At minimum define:

```text V8-A
released baseline

V8-B
primary intervention

V8-C
matched control / ablation

V8-D
combined condition only if justified
```

The exact matrix depends on the selected V8 hypothesis.

---

# 29. Why V8-A baseline must be rerun

Even though the release contains results, rerunning the baseline in the same V8 environment provides:

```text same benchmark
same environment
same accounting
same run schema
```

This makes the comparison cleaner.

Historical release numbers remain:

```text historical reference
```

not necessarily:

```text paired V8 baseline
```

---

# 30. Matched control

A V8 intervention often needs a control that changes the same resource budget.

Examples:

```text graph expansion vs semantic expansion
new parser vs flattened representation
new reranker vs same candidate count
new calibration vs fixed threshold
```

The exact control should match the hypothesis.

The objective is:

```text attribute improvement to the intervention
```

rather than:

```text extra compute
```

---

# 31. Context-budget matching

When evidence retrieval changes, record:

```text candidate count
final evidence count
context tokens
unique papers
```

Use:

```text equal context budget
```

where practical.

If unequal:

```text report the difference
```

and explain why.

---

# 32. Compute-budget matching

For expensive methods, also consider:

```text CPU/GPU time
reranking calls
LLM calls
provider tokens
```

The strongest comparison is often:

```text same quality budget
```

or:

```text same resource budget
```

depending on the research question.

---

# 33. Primary metric

Select exactly one:

```text primary metric
```

Examples could be:

```text evidence recall
answer correctness
unsupported claim rate
citation precision
latency
cost
```

depending on V8.

Other metrics are:

```text secondary
```

or:

```text diagnostic
```

This prevents metric shopping.

---

# 34. Secondary metrics

Use only those that answer the research question.

Potential:

```text evidence completeness
groundedness
citation completeness
graph invocation
latency
token usage
```

Do not report every available metric as though all were equally important.

---

# 35. Predeclare success interpretation

Before final test, write:

```text If primary metric improves:
interpretation = ...

If primary metric is unchanged:
interpretation = ...

If primary metric worsens:
interpretation = ...
```

This reduces post-hoc storytelling.

---

# 36. Negative-result interpretation

If V8 fails:

```text reject the hypothesis
```

or:

```text refine it
```

based on diagnostics.

Do not silently broaden:

```text V8
```

after the result looks weak.

---

# 37. Full-run preparation

Before the full run verify:

```text code commit
benchmark version
configuration
models
prompts
random seed
provider
output directory
```

Then create:

```text experiment manifest
```

before launching.

---

# 38. V8 experiment manifest

Include:

```text experiment_id
hypothesis
baseline_id
intervention_id
benchmark
corpus
model versions
configuration
Git commit
random seed
timestamp
budget
status
```

This should be generated automatically where practical.

---

# 39. Exact question population

Before execution verify:

```text expected question count
question IDs
type distribution
domain distribution
split
```

Do not accidentally run:

```text candidate questions
```

instead of:

```text accepted benchmark
```

---

# 40. Full-run execution order

Recommended:

```text 1. baseline
2. intervention
3. matched control
4. secondary ablations
```

Keep conditions separate.

Do not run a large chain of commands that makes it difficult to identify where a failure occurred.

---

# 41. Per-condition output

Every experiment should produce:

```text metadata
per-question results
run summary
error summary
aggregate metrics
```

Do not rely only on:

```text terminal output
```

as the experiment record.

---

# 42. Per-question result schema

At minimum:

```json
{
  "question_id":"...",
  "experiment_id":"...",
  "status":"COMPLETE",
  "primary_metric":0.0
}
```

Add intervention-specific fields.

The exact schema should follow current repository conventions.

---

# 43. Lock raw outputs

After the full run:

```text copy / version raw outputs
```

and record:

```text file hashes
```

Do not overwrite them while debugging analysis.

---

# 44. Output reconciliation

Verify:

```text expected questions
=
completed + failed + skipped
```

and:

```text no duplicate question IDs
```

Then inspect:

```text missing fields
invalid JSON
unexpected nulls
version mismatches
```

Only after reconciliation should aggregate metrics be computed.

---

# 45. Re-run policy

A rerun due to:

```text provider outage
```

should have:

```text same configuration
```

where possible.

A rerun due to:

```text method change
```

is:

```text new experiment version
```

Do not merge both into one result.

---

# 46. Analysis stages

Use:

```text Stage 1
data validation

Stage 2
primary metric

Stage 3
secondary metrics

Stage 4
paired analysis

Stage 5
failure analysis

Stage 6
cost/latency

Stage 7
robustness
```

This keeps the causal story manageable.

---

# 47. Paired comparison

Use the same:

```text question IDs
```

across:

```text baseline
intervention
control
```

Then calculate per-question deltas:

```text intervention - baseline
```

where the metric permits it.

This is stronger than comparing unrelated averages.

---

# 48. Confidence intervals

For primary metrics report:

```text point estimate
confidence interval
sample size
```

where appropriate.

Possible methods:

```text paired bootstrap
bootstrap confidence interval
appropriate paired test
```

Choose one method before final analysis.

---

# 49. Multiple comparisons

If many ablations exist:

```text primary comparison
```

must remain clearly identified.

Do not claim significance because:

```text one of 20 comparisons happened to look favorable
```

---

# 50. Effect-size interpretation

State:

```text absolute improvement
```

and, when useful:

```text relative change
```

Do not inflate small absolute differences into dramatic percentage language.

---

# 51. Question-type breakdown

Analyze:

```text SIMPLE
MULTI_HOP
TEMPORAL
CONFLICTING
CHAIN
```

where supported.

This can reveal:

```text intervention-specific benefit
```

and:

```text intervention-specific regressions
```

---

# 52. Paper-level breakdown

Measure whether improvements are:

```text broadly distributed
```

or:

```text concentrated in a few papers
```

Inspect:

```text wins per paper
losses per paper
```

when useful.

---

# 53. Domain-level breakdown

For cross-domain V8:

```text source
target
```

must be separate.

For multi-domain V8:

```text each domain
```

should be visible in the analysis.

Do not hide a failing domain inside:

```text aggregate average
```

---

# 54. Difficulty breakdown

If V8 has a predeclared difficulty representation:

```text evidence units
path length
question category
```

analyze:

```text intervention gain by difficulty
```

Do not define difficulty using final model performance.

---

# 55. Rescue analysis

For the primary intervention:

```text baseline failed
intervention succeeded
```

is:

```text rescue
```

Inspect these cases.

Ask:

```text What did the intervention recover?
Why did baseline miss it?
Was the mechanism actually responsible?
```

---

# 56. Regression analysis

Also inspect:

```text baseline succeeded
intervention failed
```

These are equally important.

Potential causes:

```text extra context noise
wrong edge
parser error
over-aggressive filtering
new ranking error
```

Record actual observed causes.

---

# 57. Counterfactual cases

If possible, identify:

```text intervention changed result
```

but:

```text changed resource budget too
```

These cases help separate:

```text mechanism effect
```

from:

```text additional computation
```

---

# 58. Mechanism validation

For every improvement ask:

```text Did the intended mechanism activate?

Did the intended information reach the final context?

Did the answer depend on that information?
```

If not:

```text the intervention may not have caused the observed improvement
```

This is especially important for:

```text graph
structure
verification
routing
```

experiments.

---

# 59. Ablation of the mechanism

Where feasible remove the central mechanism while preserving:

```text compute budget
```

and compare.

Example concept:

```text new structure representation
vs
flattened version
```

or:

```text real graph edges
vs
matched semantic candidates
```

The exact control depends on V8.

---

# 60. Human audit subset

Select cases covering:

```text intervention rescue
intervention regression
high-confidence mistakes
ambiguous cases
primary question type
```

Human review should inspect:

```text evidence
answer
citation
mechanism
```

where relevant.

---

# 61. Human-reference independence

Do not use:

```text intervention output
```

to define its own human gold label.

The evaluator should compare the system against:

```text independent evidence
```

or:

```text frozen benchmark annotation
```

---

# 62. Automatic evaluator validation

If using an LLM judge:

```text validate judge behavior
```

on a human-reviewed subset.

Measure:

```text agreement
disagreement patterns
```

Do not silently tune the evaluator to favor V8.

---

# 63. Provider accounting

For every condition compare:

```text provider calls/query
tokens/query
cache hit rate
retry rate
failure rate
```

The V8 intervention should not receive an accounting advantage because its extra work occurs in a different stage.

---

# 64. Cost categories

Separate:

```text offline construction
query-time computation
answer-generation cost
verification cost
```

For one-time preprocessing:

```text amortize only in a clearly labeled analysis
```

---

# 65. Latency categories

Report where useful:

```text preprocessing/indexing
retrieval
intervention
generation
verification
total
```

Use:

```text p50
p95
```

for query latency when sample size is sufficient.

---

# 66. Failure accounting

Record:

```text benchmark failure
runtime failure
provider failure
method failure
evaluation failure
```

Do not combine these into one:

```text error count
```

without classification.

---

# 67. Partial provider runs

If a provider outage interrupts the experiment:

```text preserve partial output
```

and label:

```text PARTIAL
```

A completed subset may be used for debugging, but not silently presented as the full final evaluation.

---

# 68. Reproducibility checkpoint

After primary analysis, run:

```text same code
same config
same benchmark
```

again on a small subset.

Confirm:

```text result schema
decision behavior
determinism
```

This catches hidden state before paper writing.

---

# 69. Robustness after primary result

Only after the primary comparison is understood, test relevant perturbations:

```text threshold
data size
paper split
domain
retrieval budget
context budget
reasonable noise
```

Do not run every possible stress test if they do not inform the V8 hypothesis.

---

# 70. V8 stopping rule

Stop the experiment when:

```text primary question answered
+
mechanism inspected
+
main failures understood
+
cost measured
+
robustness sufficient for claim
```

Do not continue searching for:

```text a better configuration
```

after the question has already been answered.

---

# 71. No post-hoc benchmark repair

If the intervention performs poorly because a question is invalid:

```text document invalidity
```

If a benchmark repair is scientifically justified:

```text create V8 benchmark v2
```

and rerun the affected experiment.

Do not edit:

```text in place
```

and keep the same experiment ID.

---

# 72. No post-hoc baseline weakening

If V8 does not beat the released baseline:

```text strengthen V8
```

or:

```text accept the negative result
```

Do not weaken the baseline.

A negative result against a strong baseline is often more informative.

---

# 73. No post-hoc metric switching

If:

```text primary metric does not improve
```

but:

```text secondary metric does
```

report:

```text primary result
+
secondary result
```

Do not quietly rename the secondary metric as:

```text main result
```

---

# 74. V8 result interpretation matrix

Use:

```text Primary metric ↑
Secondary metric ↑
Cost acceptable
→ strong evidence

Primary metric ↑
Cost high
→ conditional benefit

Primary metric unchanged
Secondary metric improves
→ narrow benefit

Primary metric ↓
Secondary metric ↑
→ tradeoff / likely reject

Primary metric ↓
Cost ↑
→ weak result
```

The exact conclusion depends on the actual evidence.

---

# 75. Main failure taxonomy

Use broad categories:

```text data/benchmark
retrieval
ranking
intervention
generation
verification
runtime
```

Then add:

```text V8-specific mechanism failure
```

only where needed.

---

# 76. Result-to-mechanism audit

For every major positive result:

```text claim
↓
metric
↓
question IDs
↓
intervention output
↓
source evidence
```

This creates an auditable chain.

---

# 77. V8 decision

At the end choose:

```text KEEP
KEEP WITH QUALIFIERS
REVISE
DEFER
REJECT
```

The decision record should state:

```text primary question
main result
confidence
strongest rescue
strongest regression
main limitation
cost
recommended next step
```

---

# 78. Recommended artifacts

Create:

```text 01_V8_EXECUTION_LOG.md
02_V8_EXPERIMENT_MANIFESTS/
03_V8_RESULTS.md
04_V8_ANALYSIS.md
05_V8_FAILURE_ANALYSIS.md
06_V8_ROBUSTNESS.md
07_V8_DECISION.md
```

Raw:

```text data/v8/
experiments/v8/
figures/v8/
```

Use project conventions where they already exist.

---

# 79. Suggested experiment names

Use stable identifiers:

```text V8-A-BASELINE
V8-B-INTERVENTION
V8-C-CONTROL
V8-D-ABLATION
V8-E-ROBUSTNESS
```

The exact names depend on the selected intervention.

Never reuse an old experiment ID for a different configuration.

---

# 80. Git discipline

Start:

```powershell
git status --short
git diff
git log --oneline --decorate -20
```

Suggested logical commits:

```text V8 specification lock

V8 infrastructure

V8 intervention

V8 benchmark

V8 evaluation

V8 analysis
```

Keep the released tag untouched.

---

# 81. PowerShell test sequence

Use:

```powershell
cd <AtlasRAG-repo>

$env:PYTHONPATH="src"

python -m pytest -q

git status --short
git log --oneline --decorate -20

Get-ChildItem data
Get-ChildItem scripts
Get-ChildItem src/atlasrag
```

Then inspect actual V8 script names before executing them.

---

# 82. Large-run sequence

Run:

```text baseline smoke
↓
intervention smoke
↓
baseline pilot
↓
intervention pilot
↓
full baseline
↓
full intervention
↓
control
↓
analysis
```

This staged sequence minimizes wasted compute/provider budget.

---

# 83. Full-run budget check

Before launch estimate:

```text number of questions
logical calls
expected provider calls
expected tokens
expected graph/intervention operations
expected latency
```

Compare with:

```text available budget
```

Stop before the full run if the estimate is unexpectedly high.

---

# 84. Data integrity after execution

Check:

```text output files
question counts
IDs
schemas
timestamps
experiment IDs
```

Then hash:

```text raw result files
```

for archival reproducibility.

---

# 85. Analysis reproducibility

The final metrics should be regenerated with:

```text one analysis script
```

from:

```text frozen raw output
```

If manual changes are necessary:

```text document them
```

and prefer converting them into code.

---

# 86. Figure reproducibility

Generate:

```text tables
figures
```

directly from:

```text raw result files
```

where possible.

Record the script commit.

---

# 87. Paper-ready result extraction

Do not write paper claims directly from:

```text terminal output
```

Use:

```text result JSON/CSV
↓
analysis
↓
final table
```

This reduces transcription errors.

---

# 88. V8 paper/report section

After the experiment, write:

```text Research question
Motivation
Method
Baseline
Intervention
Benchmark
Evaluation
Results
Ablations
Robustness
Failures
Limitations
Conclusion
```

Do not start with:

```text We solved...
```

Start with:

```text We evaluated...
```

until the result is established.

---

# 89. Related-work update

Update the literature review if V8 revealed:

```text competing methods
new benchmark
new model
new evaluation
```

The final V8 report should reflect current literature at the time it is written.

---

# 90. Novelty claim discipline

Separate:

```text novelty of component
```

from:

```text novelty of evaluation
```

A V8 experiment can be valuable even when the component itself is established.

Possible contribution:

```text controlled evidence about behavior under a specific scientific setting
```

Do not claim more.

---

# 91. Final V8 claim template

Use:

> **Under [benchmark/domain/configuration], [intervention] changed [primary metric] relative to [baseline], with [cost/latency effect].**

Then add:

```text main limitation
```

This is precise and reproducible.

---

# 92. Portfolio update

Only after the V8 decision is locked should the project description be updated.

Use:

```text implemented
evaluated
measured
```

for completed work.

Keep:

```text future work
```

separate.

---

# 93. Resume update

Every V8 resume bullet should contain:

```text actual action
actual technology
measured result
evaluation setting
```

Do not claim:

```text state-of-the-art
first
universal
production-ready
```

without direct supporting evidence.

---

# 94. V8 decision archive

The final V8 archive should include:

```text question
hypothesis
baseline
intervention
benchmark
results
failure analysis
robustness
decision
```

This allows the next research cycle to start from evidence rather than memory.

---

# 95. When V8 becomes V9

Only if:

```text V8 identifies a meaningful unresolved limitation
```

and:

```text a new controlled question follows from it
```

Otherwise:

```text package V8
```

and stop.

---

# 96. Exact execution order

Use:

```text 1. verify Week 21 V8 specification

2. verify released baseline

3. reproduce baseline smoke

4. freeze V8 benchmark

5. implement minimum intervention

6. run tests

7. run baseline smoke

8. run intervention smoke

9. run small pilot

10. validate instrumentation

11. lock experiment manifest

12. run full baseline

13. run full intervention

14. run matched control

15. lock raw results

16. reconcile outputs

17. compute primary metric

18. compute secondary metrics

19. paired statistical analysis

20. rescue/regression analysis

21. mechanism audit

22. human review

23. cost/latency analysis

24. robustness tests

25. write decision

26. archive evidence

27. commit V8 state
```

Do not skip from implementation directly to publication.

---

# 97. Final rule for the next AI agent

Start by reading the actual Week 21 V8 selection artifacts and the released AtlasRAG state.

Do not invent the V8 intervention.

Do not change the released baseline.

Do not create a benchmark simply to favor V8.

Do not tune on the final test set.

Do not let the intervention see gold evidence.

Do not treat pilot results as final evidence.

Do not hide provider failures.

Do not count logical calls as provider calls.

Do not change metrics after seeing results.

Do not weaken the baseline.

Do not remove difficult examples because they hurt the intervention.

Do not rewrite the result after an unsuccessful run.

Do not stack several major interventions into the primary experiment.

Do not create V9 until V8 produces evidence that actually justifies another research question.

The correct workflow is:

```text
V8 specification
↓
verify released baseline
↓
freeze benchmark
↓
implement one intervention
↓
test
↓
smoke test
↓
pilot
↓
freeze manifest
↓
full baseline
↓
full intervention
↓
matched control
↓
lock raw outputs
↓
analyze
↓
audit mechanism
↓
stress-test
↓
decide
↓
archive
```

That is Week 22.
