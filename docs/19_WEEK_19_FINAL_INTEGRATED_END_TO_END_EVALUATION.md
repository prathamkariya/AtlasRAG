# AtlasRAG — Week 19: Final Integrated System & End-to-End Evaluation

Week 18 stress-tested the selective graph-escalation system. Week 19 moves from component-level evidence to system-level evidence.

The central question is:

> **When the validated AtlasRAG components are assembled into one frozen pipeline, does the complete system actually produce better scientific answers, grounding, and citations at an acceptable operational cost?**

The final candidate architecture may be:

```text
Question
   ↓
Initial routing
   ↓
Initial / structure-aware retrieval
   ↓
Retrieval-state features
   ↓
V3 failure prediction
   ↓
if needed → graph escalation
   ↓
Final evidence
   ↓
Answer generation
   ↓
V2 verification
   ↓
Claims + citations
```

This architecture is a candidate, not an assumption. Include only components that survived their own controlled experiments.

---

## 1. Why Week 19 is different

Earlier weeks isolated mechanisms:

```text
V3 → retrieval-state failure prediction
V6 → scientific evidence structure
V7 → evidence relationships
Week 17 → selective graph escalation
Week 18 → robustness and transfer
```

Week 19 asks:

```text
Does the complete system improve the real user-facing outcome?
```

The final evaluation therefore prioritizes:

```text
answer correctness
groundedness
citation correctness
citation completeness
unsupported-claim rate
cost
latency
```

Retrieval metrics remain essential because they explain why the end-to-end system succeeds or fails.

---

## 2. Primary research question

> **Does the final integrated AtlasRAG system improve scientific answer quality and evidence grounding over the strongest validated baseline while maintaining an acceptable quality/cost/latency tradeoff?**

Secondary questions:

```text
1. Which validated component contributes the most?
2. Are retrieval gains transferred to answer quality?
3. Does V2 reduce unsupported claims?
4. Does selective graph escalation help difficult cases economically?
5. Are citations more correct and complete?
6. Which question types benefit?
7. Which failure modes remain?
8. Does the system retain gains across domains?
9. Is the evidence strong enough for publication/release claims?
10. What should remain research-only versus demo-ready?
```

These are evaluation questions, not conclusions.

---

## 3. Final component-selection gate

Create a component decision table before final testing:

```text
Component
Version
Primary evidence
Known limitation
Status
```

Possible components:

```text
initial router
retrieval stack
structure-aware retrieval
V3 failure detector
graph retrieval
selective graph policy
V2 verification
answer generator
```

For each choose:

```text
KEEP
KEEP WITH QUALIFIERS
REJECT
DEFER
```

A component that failed its own study must not be included merely because it was implemented.

---

## 4. Frozen historical baseline

Keep the historical Run1 results separate from current final baselines.

Maintain at least:

```text
Run1 historical baseline
current strong retrieval baseline
strongest validated adaptive system
final integrated candidate
```

Do not relabel an old experiment as the final baseline if the benchmark, retrieval stack, or instrumentation later changed.

---

## 5. Final benchmark freeze

Before final test execution, freeze:

```text
benchmark version
question count
question-type distribution
paper count
domain distribution
gold-evidence definition
annotation version
split definition
benchmark hash
```

After final test begins:

```text benchmark = immutable
```

Any repair creates a new benchmark version and requires affected experiments to be rerun.

---

## 6. Final corpus and index freeze

Record:

```text
corpus version
paper count
domains
source provenance
license/access status
text-extraction version
chunking version
structure-extraction version
graph version
```

Verify that the evaluated index corresponds exactly to the frozen corpus manifest.

---

## 7. Final retrieval configuration

Freeze and record:

```text embedding model
dense_k
BM25_k
RRF settings
reranker
final_k
chunk size
overlap
minimum chunk size
structure-aware settings
```

Do not silently upgrade any retrieval component immediately before final evaluation.

---

## 8. Final answer-generation configuration

Freeze:

```text answer model
provider
system prompt
answer prompt
temperature
max output tokens
context assembly
citation format
generation settings
```

The answer model and prompt must be identical across systems in the primary comparison unless the experiment explicitly studies generation.

---

## 9. Final V2 verification configuration

If V2 survives, record:

```text claim extraction method
citation mapper
verification model
verification prompt
verification labels
thresholds
repair policy
```

Detection-only verification should remain the clean primary condition unless repair was independently validated.

Do not attribute answer gains to retrieval if a new repair model is doing the substantive work.

---

## 10. Final V3 and graph configuration

If V3 survives:

```text predictor version
feature version
calibration version
threshold
training/validation split
```

If graph survives:

```text graph schema
graph snapshot
edge version
max hops
neighbor cap
candidate-selection policy
context budget
graph invocation policy
```

Everything must be immutable during final test evaluation.

---

## 11. Main final comparison set

At minimum compare:

```text
F0 — strong static retrieval baseline
F1 — strongest validated adaptive system
F2 — strongest selective graph system
F3 — final integrated system
```

Optional references:

```text always-strong retrieval
always-graph retrieval
Oracle/strongest empirical reference
```

Keep historical experiments in appendices rather than overcrowding the headline result table.

---

## 12. Why the baseline must be strong

The final system is not successful merely because it beats a weak baseline.

The relevant comparison is:

```text
final integrated
vs
strongest practical simpler baseline
```

The simpler baseline should contain the best validated retrieval components that do not depend on the adaptive machinery being evaluated.

---

## 13. End-to-end outcome hierarchy

Evaluate in layers:

```text
1. retrieval evidence
2. evidence completeness
3. answer correctness
4. groundedness
5. citation correctness
6. citation completeness
7. cost / latency
```

This prevents a retrieval-only improvement from being reported as an end-to-end improvement when the answer quality does not change.

---

## 14. Answer correctness protocol

Freeze an answer-evaluation rubric covering, where relevant:

```text
factual correctness
completeness
relevance
scientific interpretation
numeric correctness
unit correctness
uncertainty correctness
comparative correctness
temporal correctness
```

Use established project definitions when available.

---

## 15. Groundedness

Groundedness asks:

```text
Are the scientific claims in the answer supported by the available evidence?
```

Keep this separate from factual correctness. An answer may be factually right but poorly grounded or cited.

---

## 16. Citation correctness

For every citation ask:

```text
Does the cited source actually support the attached claim?
```

Common errors include:

```text
same topic, wrong paper
right paper, wrong section
right section, wrong quantity
right quantity, wrong value
right study, wrong temporal context
```

Topic similarity is not citation correctness.

---

## 17. Citation completeness

Measure whether the important externally verifiable claims are actually cited.

Keep:

```text
citation correctness
```

separate from:

```text
citation completeness
```

A response can have correct citations while still leaving major claims unsupported.

---

## 18. Unsupported-claim rate

Track:

```text unsupported scientific claims
/
evaluated scientific claims
```

This is a major final metric for scientific RAG.

If V2 is helpful, a likely mechanism is a reduction in unsupported claims. Whether that happens must be measured.

---

## 19. Numeric answer evaluation

Scientific answers require special attention to:

```text value
unit
sign
uncertainty
interval
upper/lower limit
parameter identity
```

For example:

```text 73.0 ± 1.0
```

is not equivalent to:

```text 73.0
```

when uncertainty is part of the evidence.

---

## 20. Comparative, temporal, and conflict evaluation

For comparative questions verify:

```text both quantities
comparison direction
relevant context
```

For temporal questions verify:

```text chronology
earlier/later claims
direction of change
```

For conflicting evidence verify:

```text source attribution
same scientific target
different result/claim
context
```

Do not collapse distinct scientific findings into an unsupported consensus.

---

## 21. Multi-hop and chain completeness

For MULTI_HOP and CHAIN questions, verify that all required evidence contributions are present.

For a question requiring:

```text A + B + C
```

do not give full credit merely because one paragraph gives a vague summary.

The evaluation must distinguish:

```text direct one-passage answer
```

from:

```text genuine linked evidence
```

---

## 22. Human evaluation

Automatic metrics should be supported by a human-reviewed subset containing:

```text random examples
baseline/final disagreements
graph rescues
graph regressions
high-confidence wrong answers
citation failures
numeric cases
multi-hop cases
temporal/conflict cases
```

Reviewers should see:

```text question
answer
retrieved evidence
citations
```

and original source material when necessary.

---

## 23. Human rubric

A compact rubric can use:

```text
Correct / Partially correct / Incorrect

Grounded / Partially grounded / Ungrounded

Citation correct / Questionable / Incorrect
```

Record detailed reasons for:

```text numeric error
missing evidence
wrong source
unsupported claim
wrong chronology
```

Freeze the rubric before final review.

---

## 24. Automatic judge audit

If an LLM judge is used:

```text
validate it on a human-reviewed subset
```

Record:

```text evaluator model
prompt version
temperature
schema
agreement with human labels
```

Do not tune the judge prompt after seeing the final-system answers.

---

## 25. Avoid evaluator leakage

The evaluator should not receive:

```text gold answer
gold evidence IDs
system identity
experiment condition
```

unless a particular evaluation explicitly requires them.

Blind comparison is preferable where practical.

---

## 26. Context-budget fairness

For every system record:

```text context tokens
evidence-unit count
paper count
```

At least one final comparison should use a matched context budget.

Otherwise an apparent graph advantage may simply be a larger evidence budget.

---

## 27. Latency decomposition

Measure:

```text routing
initial retrieval
reranking
V3 prediction
graph traversal
graph reranking
generation
verification
```

Report:

```text p50
p95
```

when enough samples exist.

This identifies which component actually causes the operational overhead.

---

## 28. Token and provider accounting

Persist separately:

```text logical calls
provider calls
cache hits
cache misses
retry attempts
rate-limit errors
connection errors
prompt tokens
completion tokens
```

Do not infer provider usage from logical call counts.

---

## 29. Cost accounting

Report:

```text offline indexing/build cost
online query cost
tokens/query
provider calls/query
compute/query
```

For graph systems distinguish:

```text one-time graph-build cost
```

from:

```text per-query graph cost
```

If current provider pricing is used, record the price source/date rather than hard-coding a stale number.

---

## 30. Cost amortization

When useful, evaluate:

```text total cost =
offline graph construction
+
N × online query cost
```

for several deployment scales.

This makes it possible to answer:

```text At what workload does the added structure become operationally worthwhile?
```

---

## 31. Final component ablation

Run a compact ablation such as:

```text Base
Base + V3
Base + Graph
Base + V3 + Graph
Final + V2
```

Only include combinations that are scientifically interpretable.

The purpose is to identify marginal contribution, not to reproduce every historical experiment.

---

## 32. V3 attribution

Compare:

```text no graph
always graph
selective graph
```

This isolates the value of selective gating from the value of graph retrieval itself.

---

## 33. Graph attribution

Compare:

```text strong non-graph retrieval
```

against:

```text graph-assisted retrieval
```

under matched or explicitly documented budgets.

A graph improvement must not be attributed to graph structure when the real change is simply a larger context.

---

## 34. V2 attribution

Compare the selected retrieval architecture:

```text without V2
vs
with V2
```

with retrieval, graph, V3, and answer generation held fixed.

This isolates effects on:

```text unsupported claims
groundedness
citation precision
citation completeness
```

---

## 35. Structure-aware attribution

If V6 survives, retain a secondary comparison:

```text prose-oriented retrieval
vs
structure-aware retrieval
```

This helps determine whether the graph layer depends on the structural evidence representation.

---

## 36. Final question-type analysis

Report separately:

```text SIMPLE
MULTI_HOP
TEMPORAL
CONFLICTING
CHAIN
```

A strong final system may improve some categories much more than others. That is useful evidence, not a problem to hide.

---

## 37. Domain analysis

For multi-domain evaluation report:

```text per-domain results
```

and:

```text overall results
```

when appropriate.

Do not let a large source domain dominate the aggregate without showing domain-level behavior.

---

## 38. Paper-level concentration

Measure whether improvements are spread broadly or concentrated in a small number of papers.

Useful diagnostics:

```text papers with rescues
papers with regressions
rescues per paper
```

A large average driven by two papers should not be described as broadly general.

---

## 39. Full failure taxonomy

Use a final hierarchy such as:

```text F1 ingestion / extraction
F2 chunking / structure
F3 retrieval
F4 reranking
F5 routing
F6 V3 prediction
F7 graph construction
F8 graph traversal / selection
F9 context pollution
F10 generation
F11 citation mapping
F12 verification
F13 corpus absence
F14 benchmark annotation
F15 provider/runtime
```

Only use categories actually observed.

---

## 40. Root-cause hierarchy

For every incorrect final answer ask:

```text Is the benchmark valid?
        ↓
Is required evidence present?
        ↓
Was it retrieved?
        ↓
Was it selected?
        ↓
Was the answer grounded?
        ↓
Were citations correct?
```

This prevents vague conclusions such as:

```text the model hallucinated
```

when the actual cause was a retrieval miss.

---

## 41. Rescue/regression analysis

For each important comparison report:

```text baseline only correct
final only correct
both correct
both incorrect
```

For graph systems also report:

```text graph rescued
graph unnecessary
graph regressed
graph skipped but would have helped
```

These categories explain system behavior much better than an average alone.

---

## 42. Verification-induced regressions

If verification can modify answers, inspect:

```text correct before verification
wrong after verification
```

The same principle applies to:

```text citation suppression
claim deletion
repair
```

Verification must not quietly create errors while the headline metric improves elsewhere.

---

## 43. Final abstention behavior

Define how the system behaves when evidence is insufficient.

Distinguish:

```text correct abstention
```

from:

```text unnecessary abstention
```

This is especially relevant for:

```text UNCERTAIN
retrieval-insufficient
```

cases.

---

## 44. Selective-risk view

For the final system measure:

```text coverage
failure rate
cost
```

where:

```text coverage =
fraction of questions answered without expensive escalation
```

This shows whether the system is genuinely selective.

---

## 45. Final quality-cost frontier

Produce a primary frontier:

```text X = cost/query
Y = answer correctness
```

and, where useful:

```text X = cost/query
Y = evidence recall
```

Include compatible reference systems such as:

```text strong baseline
selective system
always-strong
always-graph
```

---

## 46. Final latency-quality view

A second frontier can use:

```text X = p95 latency
Y = answer correctness
```

This helps reveal whether difficult cases create an unacceptable latency tail.

---

## 47. Primary final hypothesis

> **The final integrated AtlasRAG system can retain the evidence advantages of stronger retrieval while reducing unnecessary expensive retrieval/graph operations and improving grounding of scientific answers.**

Treat this as a hypothesis until the frozen evaluation is complete.

---

## 48. Final statistical plan

Before inspecting final numbers, define:

```text primary comparisons
primary metrics
confidence-interval method
paired-test method
secondary analyses
```

Potential paired methods include:

```text paired bootstrap
sign test
McNemar-type tests for binary outcomes
```

Use methods appropriate to the actual metric and sample size.

---

## 49. Effect sizes

For every primary comparison report:

```text absolute difference
confidence interval
sample size
```

Do not rely on p-values alone.

A practically meaningful effect may not reach significance on a small benchmark, while a tiny effect may become statistically reliable on a large one.

---

## 50. Multiple comparisons

The final study can contain many ablations.

Define a small number of:

```text primary comparisons
```

and treat the rest as:

```text secondary / exploratory
```

Do not search all possible comparisons and report only the favorable ones.

---

## 51. Final benchmark integrity audit

Before final test verify:

```text duplicate questions
near duplicates
paper overlap
domain overlap
gold evidence availability
answer support
question-type validity
temporal validity
conflict validity
multi-hop necessity
```

Once final testing begins, the benchmark is frozen.

---

## 52. Final environment freeze

Record:

```text Python version
package versions
OS
hardware / CUDA context if relevant
embedding model
reranker
LLM model
provider
configuration
Git commit
```

Remove dependence on hidden local state before release.

---

## 53. Clean-machine reproduction

Where practical:

```text clean environment
↓
documented setup
↓
final benchmark
↓
final evaluation
↓
reproduced result
```

Compare the reproduction to the released result and document any provider/model drift.

---

## 54. Secret and path audit

Before publication/release check for:

```text API keys
tokens
private URLs
absolute local paths
personal filesystem references
untracked credentials
```

Document required environment-variable names without publishing their values.

---

## 55. Final result registry

Create one registry containing:

```text experiment_id
purpose
system
benchmark
configuration
result path
status
Git commit
```

This becomes the authoritative map of what was actually measured.

---

## 56. Final claim-to-result map

Create a table:

```text Claim
Supporting experiment
Metric
Effect
Confidence
Limitation
```

Every major sentence in the abstract should be traceable to this table.

---

## 57. Claim discipline

Do not write:

```text improved by 30%
```

when the result is an absolute change that should be described as:

```text +X percentage points
```

Always state the baseline and metric clearly.

Do not select whichever metric produces the largest-looking improvement.

---

## 58. What the final study cannot claim

Unless directly supported, do not claim:

```text universal scientific-domain generalization
universal scientific reasoning
hallucination elimination
guaranteed citation correctness
state-of-the-art scientific QA
```

Scope claims to:

```text benchmark
corpus
domains
retrieval configuration
graph version
model versions
evaluation protocol
```

---

## 59. Publication structure

A clean final paper/report structure is:

```text
1. Problem
2. AtlasRAG architecture
3. Benchmark
4. Retrieval and adaptive policy
5. Scientific evidence / graph layer
6. Evaluation protocol
7. Main results
8. Ablations
9. Robustness and transfer
10. Failure analysis
11. Limitations
12. Conclusion
```

Do not force every historical experiment into the main body.

---

## 60. Final contribution framing

Depending on the evidence, the strongest contribution may be:

```text
adaptive retrieval methodology
selective graph-assisted evidence acquisition
scientific evidence representation
provenance-aware RAG evaluation
empirical benchmark/evaluation study
```

The final contribution should follow the measured result, not the amount of code written.

---

## 61. Negative-result framing

A negative result is still publishable research when it is controlled.

For example:

```text
complex graph expansion did not improve end-to-end quality after context-budget control
```

can be useful if the benchmark, baseline, and analysis are rigorous.

Do not hide negative results to make the project appear more novel.

---

## 62. Final deployment status

Choose:

```text DEPLOY
DEMO ONLY
RESEARCH PROTOTYPE
```

based on:

```text reliability
latency
cost
failure behavior
reproducibility
```

A strong research prototype does not need to claim production readiness.

---

## 63. Demo rules

A public demo must use the evaluated or explicitly labeled release version.

Do not demonstrate:

```text unreleased experimental features
hard-coded answers
hidden gold evidence
manually selected context unavailable to the system
```

The demo should reflect the measured architecture.

---

## 64. Demo question selection

Prefer representative questions:

```text one simple
one multi-hop
one graph-rescue case
one temporal/conflict case
one insufficient-evidence case
```

where the frozen corpus supports them.

Do not show only easy successes.

---

## 65. Portfolio framing

A strong final project description emphasizes:

```text research problem
architecture
controlled evaluation
measured outcome
```

For example:

```text
Built and evaluated an adaptive scientific RAG system combining retrieval-state prediction, structure-aware evidence retrieval, selective graph expansion, and citation verification under controlled paper-disjoint benchmarks.
```

Use only the components actually implemented and validated.

---

## 66. Resume discipline

Every resume number must map to a result artifact.

Every architecture claim must map to actual code.

Do not list:

```text planned
experimental but unvalidated
deferred
```

components as completed achievements.

---

## 67. GitHub README alignment

The README should communicate:

```text problem
architecture
key technologies
evaluation
main results
limitations
reproduction
```

Keep deep experiment chronology in dedicated documentation instead of making the README enormous.

---

## 68. Archive vs repository

The Git repository should contain:

```text code
configs
scripts
manifests
small reproducibility artifacts
```

Large or restricted data can live in release archives or external storage when licensing requires it.

Do not redistribute copyrighted source material without permission.

---

## 69. Final release package

Recommended release contents:

```text final benchmark manifest
corpus manifest
experiment manifests
configuration
analysis scripts
figure-generation scripts
environment specification
result schemas
final decision
```

Where licensing permits, preserve per-question outputs or an equivalent auditable artifact.

---

## 70. Figure reproducibility

Generate final figures from machine-readable result files.

Record:

```text source result file
analysis script
script version
Git commit
```

Avoid hand-editing final values into figures.

---

## 71. Final analysis pipeline

Prefer one analysis entry point that regenerates:

```text primary metrics
confidence intervals
paired comparisons
cost tables
question-type results
domain results
robustness summaries
```

This prevents multiple inconsistent analysis implementations.

---

## 72. Reproduction discrepancy policy

If clean-machine results differ:

```text identify whether the cause is
provider/model drift
randomness
environment
code mismatch
data mismatch
```

Do not simply retain whichever run produces the better result.

---

## 73. Final stopping rule

Stop expanding the architecture when:

```text final benchmark locked
+
main baselines compared
+
primary system evaluated
+
answer/citation quality measured
+
cost/latency measured
+
major failures understood
+
robustness checked
+
reproducibility verified
```

At that point, new features belong in future research rather than the current claim set.

---

## 74. What comes after Week 19

Do not automatically create a V8.

Let the final evidence decide.

Possible next directions:

```text larger benchmark
better equation/table representation
multimodal scientific retrieval
stronger graph verification
uncertainty calibration
human-in-the-loop retrieval
new scientific domains
```

These are future possibilities, not commitments.

---

## 75. Recommended Week 19 deliverables

Create:

```text
01_FINAL_SYSTEM_SPEC.md
02_FINAL_EVALUATION_PROTOCOL.md
03_FINAL_RESULTS.md
04_FINAL_ABLATIONS.md
05_FINAL_FAILURE_ANALYSIS.md
06_FINAL_COST_LATENCY_ANALYSIS.md
07_FINAL_REPRODUCIBILITY.md
08_FINAL_DECISION.md
09_FINAL_RELEASE_MANIFEST.json
```

Raw:

```text
data/final/
experiments/final/
figures/final/
```

Use existing repository conventions when they already exist.

---

## 76. Exact execution order

Follow:

```text
1. inspect Week 18 decision
2. select only validated components
3. create final system manifest
4. freeze benchmark
5. freeze corpus
6. freeze retrieval
7. freeze graph
8. freeze V3
9. freeze V2
10. freeze answer model
11. create clean Git checkpoint
12. run tests
13. smoke test
14. lock final configuration
15. run strong baseline
16. run final integrated system
17. run strongest reference
18. run component ablations
19. lock raw outputs
20. evaluate answers
21. evaluate grounding/citations
22. human audit
23. compute statistics
24. generate final tables/figures
25. analyze failures
26. perform reproduction test
27. create final decision
28. create release manifest
29. commit final research state
```

After step 19, any evaluation-relevant change must become a new version.

---

## 77. PowerShell starting point

Use the actual repository paths and scripts:

```powershell
cd <AtlasRAG-repo>

$env:PYTHONPATH="src"

python -m pytest -q

git status --short
git diff
git log --oneline --decorate -10

Get-ChildItem configs
Get-ChildItem data
Get-ChildItem scripts
Get-ChildItem src/atlasrag
```

Then verify actual final-run script names before execution.

Run major conditions separately rather than in one giant chained command.

---

## 78. Smoke-test protocol

Before the full run, process a small representative sample:

```text
3–10 questions
```

Verify:

```text correct benchmark version
correct retrieval
correct V3 decision
correct graph invocation
correct final evidence
correct answer
correct citations
correct logging
```

Only then launch the full evaluation.

---

## 79. Partial-run handling

If a final run stops because of:

```text 429
connection failure
crash
manual interruption
```

mark it:

```text PARTIAL
```

and preserve the partial artifacts.

Do not treat missing queries as successes or failures until reconciliation is complete.

---

## 80. Final reconciliation

For each condition verify:

```text expected questions
=
completed + failed + skipped
```

and:

```text one result per question
no duplicate IDs
no missing IDs
no version mismatch
```

Only after this check should final statistics be generated.

---

## 81. Final per-question ledger

A valuable final table contains:

```text question_id
system
route
retrieval evidence
graph invoked
V3 probability
final evidence
answer status
citation status
latency
tokens
provider calls
```

This becomes the main provenance backbone for final analysis.

---

## 82. Final high-confidence error audit

Inspect:

```text high-confidence wrong answers
low-confidence correct answers
graph-invoked but unnecessary cases
graph-skipped but graph-beneficial cases
verification-induced regressions
```

These examples often reveal weaknesses hidden by averages.

---

## 83. Final scientific-integrity check

For public claims ask:

```text Does the source support the statement?
Did we compare the right quantity?
Are units preserved?
Is uncertainty preserved?
Is chronology correct?
Is disagreement represented honestly?
Did we allow valid alternative evidence?
Did we separate retrieval from generation?
```

This is mandatory before paper/demo/release writing.

---

## 84. Final cost-integrity check

Ask:

```text Are offline graph costs shown?
Are retries counted?
Are cache hits distinguished?
Are provider calls separated from logical calls?
Are latency stages comparable?
Are context budgets comparable?
Are failed calls represented correctly?
```

Do not publish a cost advantage until these checks pass.

---

## 85. Final publication-integrity check

Ask:

```text Does every abstract claim map to a result?
Does every numeric claim map to raw data?
Are limitations visible?
Are negative findings included?
Are exploratory analyses labeled?
Are future ideas clearly separated from measured work?
```

---

## 86. Final headline result table

A paper-facing table can use:

```text
System
Evidence Recall
Answer Correctness
Groundedness
Citation Precision
Citation Completeness
Unsupported Claim Rate
Graph Invocation Rate
Verification Rate
Cost / Query
p50 Latency
p95 Latency
```

The complete machine-readable table should exist in the release artifacts even if the paper shows a reduced version.

---

## 87. Final ablation table

Use a compact table such as:

```text
System
Base Retrieval
V3
Graph
V2
Evidence Recall
Answer Correctness
Citation Quality
Cost
```

The purpose is attribution, not exhaustive history.

---

## 88. Final robustness table

Reuse the strongest Week 18 stress tests:

```text
Condition
Evidence Recall
Answer Quality
Graph Rate
Cost
Latency
Interpretation
```

This provides evidence that the final claim is not a single-configuration artifact.

---

## 89. Final decision categories

Choose one primary status:

```text
STRONG KEEP
KEEP WITH QUALIFIERS
RESEARCH PROTOTYPE
REVISE
STOP / PACKAGE
```

The decision should summarize:

```text strongest positive result
strongest limitation
main failure mode
operational tradeoff
next action
```

---

## 90. Final mental model

The completed research arc is:

```text
basic scientific RAG
        ↓
benchmark + Oracle
        ↓
adaptive retrieval routing
        ↓
retrieval-failure prediction
        ↓
scientific evidence structures
        ↓
evidence graph
        ↓
selective graph escalation
        ↓
robustness / domain transfer
        ↓
final end-to-end answers + citations
```

The final question is not:

```text
Which model is best?
```

It is:

> **Can AtlasRAG acquire, select, and verify scientific evidence efficiently enough to improve real answers under controlled evaluation?**

---

## 91. Final rule for the next AI agent

Start by reading the final Week 18 decision and the actual repository state.

Do not assume every historical component belongs in the final system.

Do not modify the benchmark after final test inspection.

Do not tune thresholds on the final test set.

Do not change the answer model during the primary retrieval comparison.

Do not claim retrieval improvement without checking answer and citation impact.

Do not claim answer improvement without checking grounding.

Do not claim citation improvement without checking the source.

Do not hide graph or verification cost.

Do not remove difficult examples because they hurt the result.

Do not silently repair final outputs.

Do not overwrite historical experiments.

Do not create another research version merely to avoid packaging the current work.

The correct workflow is:

```text
inspect
↓
select
↓
freeze
↓
test
↓
lock raw evidence
↓
evaluate answers
↓
audit citations
↓
analyze failures
↓
verify reproducibility
↓
lock claims
↓
release
```

That is Week 19.

