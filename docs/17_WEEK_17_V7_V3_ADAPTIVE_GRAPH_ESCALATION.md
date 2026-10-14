# AtlasRAG — Week 17: V7/V3 Adaptive Graph Escalation & Selective Evidence Expansion

## 1. Purpose

Week 16 isolated the idea of an evidence graph:

```text
scientific evidence units
        ↓
explicit relationships
        ↓
graph-assisted retrieval
        ↓
evidence set
```

Week 17 takes the next controlled step.

The question is no longer only:

```text
Does graph-assisted retrieval help?
```

It becomes:

```text
When should the system pay the extra cost of graph-assisted retrieval?
```

This connects the V7 evidence graph to the V3 retrieval-failure predictor.

The intended architecture is:

```text
Question
   ↓
Initial routing
   ↓
Initial retrieval
   ↓
Retrieval-state observation
   ↓
V3 failure predictor
   ├─ likely sufficient
   │      ↓
   │   normal answer path
   │
   └─ likely insufficient
          ↓
      graph escalation
          ↓
      stronger evidence set
          ↓
         answer
```

The central idea is:

```text
do not use the expensive graph path for every query
```

Instead:

```text
use graph assistance selectively
```

The primary research question is:

> **Can retrieval-state-aware selective graph escalation recover difficult evidence cases while avoiding the cost and latency of graph retrieval on queries that do not need it?**

This is a natural continuation of the original AtlasRAG objective:

```text
better evidence
+
less unnecessary computation
```

Do not assume that selective escalation will outperform always-graph or never-graph policies.

The experiment must measure it.

---

# 2. Where Week 17 fits

The research progression is now:

```text
V1
Adaptive retrieval routing

        ↓

V2
Evidence / citation verification

        ↓

V3
Retrieval-failure prediction

        ↓

V4
Larger and cleaner benchmark

        ↓

V5
Cross-domain generalization

        ↓

V6
Scientific-structure-aware retrieval

        ↓

V7
Evidence graph and provenance

        ↓

Week 17
Selective graph escalation
```

Each stage should remain conceptually separate.

V3 answers:

```text
Is the current retrieval state likely to be insufficient?
```

V7 answers:

```text
Can graph relationships provide better evidence?
```

Week 17 combines them:

```text
Should graph retrieval be invoked for this retrieval state?
```

That is a policy problem.

Do not rewrite the history and call the whole architecture simply:

```text adaptive RAG
```

without identifying which decision each module makes.

---

# 3. Primary research question

Primary:

> **Can a retrieval-state-aware policy selectively invoke graph-assisted retrieval so that evidence quality approaches always-graph retrieval while reducing unnecessary graph computation?**

Secondary questions:

```text
1. Does V3 failure probability predict when graph escalation is useful?

2. Is a simple threshold enough?

3. Does selective escalation retain most of the graph rescue cases?

4. How many graph invocations are unnecessary?

5. Does the selective policy improve the quality/cost frontier?

6. Which retrieval-state features are most useful for graph invocation?

7. Are graph rescues concentrated in MULTI_HOP/TEMPORAL/CONFLICTING/CHAIN cases?

8. Does selective graph escalation create harmful under-escalation?

9. How sensitive is the policy to threshold choice?

10. Does the benefit survive paper-disjoint and domain-shifted evaluation?
```

All are hypotheses until measured.

---

# 4. Core decision problem

The system has two retrieval states.

### State 1 — likely sufficient

```text
initial retrieval
      ↓
strong enough evidence
      ↓
answer
```

### State 2 — likely insufficient

```text
initial retrieval
      ↓
failure predictor
      ↓
graph escalation
      ↓
additional / related evidence
      ↓
answer
```

The policy therefore has to make a binary operational decision:

```text
GRAPH
or
NO_GRAPH
```

A simple initial rule is:

```text
if failure_probability >= threshold:
    use graph
else:
    use baseline
```

Do not immediately use reinforcement learning, a neural policy network, or a complex bandit algorithm.

A fixed threshold is the cleanest first baseline.

---

# 5. What is actually being optimized?

The objective should not be:

```text maximize graph usage
```

and it should not be:

```text minimize graph usage
```

The useful objective is:

```text maximize evidence quality
subject to
reasonable cost / latency
```

Conceptually:

```text utility =
quality_gain
-
λ * additional_cost
```

The exact utility equation should be chosen carefully and not tuned opportunistically after seeing the test results.

The safest reporting strategy is to show the complete tradeoff curve:

```text graph coverage
vs
evidence recall
vs
cost
vs
latency
```

rather than hiding everything inside one score.

---

# 6. Baseline hierarchy

Week 17 needs several controls.

### W17-A — no graph

```text Question
↓
initial route
↓
initial retrieval
↓
answer
```

This is the no-escalation control.

### W17-B — always graph

```text Question
↓
initial route
↓
initial retrieval
↓
graph retrieval
↓
answer
```

This is the quality reference for graph use.

### W17-C — fixed threshold

```text Question
↓
initial route
↓
initial retrieval
↓
simple threshold
↓
graph / no graph
```

This tests whether selective escalation can work without a learned policy.

### W17-D — learned V3 detector

```text Question
↓
initial route
↓
initial retrieval
↓
V3 failure predictor
↓
graph / no graph
```

This is the primary Week 17 system.

### W17-E — oracle graph invocation

Only for analysis:

```text use graph exactly when graph would rescue / improve the result
```

This must never be available to the deployed model.

It is an upper-bound diagnostic for policy potential.

---

# 7. Why the always-graph baseline matters

Suppose the learned selective system achieves:

```text evidence recall = 0.82
```

That number is hard to interpret by itself.

If:

```text no graph = 0.70
always graph = 0.90
```

then the selective system recovers:

```text 12 / 20 percentage points
```

of the possible graph gain.

But if:

```text always graph = 0.81
```

then the selective system has nearly captured the entire graph benefit.

Therefore every Week 17 result should be interpreted relative to:

```text no graph
and
always graph
```

---

# 8. Graph cost must be explicit

Graph escalation may create:

```text traversal cost
candidate expansion
reranking cost
additional context
LLM answer cost
```

Track all relevant components.

At minimum:

```text graph_invoked
graph_latency
graph_candidates
graph_added_evidence
graph_context_tokens
total_query_latency
total_query_tokens
```

If graph construction is an offline cost:

```text graph_build_cost
```

should remain separate.

Do not hide offline and online costs inside one unexplained number.

---

# 9. The V3 predictor input

The predictor should operate on information available immediately after initial retrieval.

Potential feature groups:

```text ranking
semantic
lexical
agreement
diversity
scientific-anchor
retrieval-shape
```

Examples:

```text top reranker score
top-1/top-2 gap
mean top-k score
score variance
dense/BM25 overlap
dense/BM25 disagreement
number of unique papers
number of sections
query/evidence similarity
scientific anchor coverage
evidence redundancy
```

The exact feature set should follow the final V3 implementation.

Do not introduce new features merely because they correlate better on the Week 17 test set.

---

# 10. Graph-benefit prediction vs retrieval-failure prediction

This distinction is critical.

V3 predicts:

```text initial retrieval is likely insufficient
```

Week 17 really needs:

```text graph escalation is likely to improve the evidence state
```

These are not necessarily identical.

Example:

```text initial retrieval insufficient
```

but:

```text graph has no relevant neighbors
```

Then graph escalation does not help.

Another case:

```text initial retrieval appears strong
```

but:

```text graph reveals a missing second evidence unit
```

Then graph escalation helps.

Therefore the first Week 17 study should measure:

```text failure prediction
```

and:

```text graph benefit conditional on failure
```

separately.

This is one of the most important conceptual points of the week.

---

# 11. Define escalation benefit

A query can be classified experimentally as:

```text graph-beneficial
```

when:

```text graph condition
recovers required evidence
```

while:

```text baseline condition
does not
```

Possible categories:

```text RESCUE
graph succeeds, baseline fails

NO_EFFECT
both succeed or both fail similarly

REGRESSION
baseline succeeds, graph fails

PARTIAL_RESOLVE
graph increases evidence completeness without full success
```

These categories are diagnostic.

Do not use them as labels for training unless the target definition explicitly requires it.

---

# 12. Avoid circular policy labels

Bad:

```text V3 predicts failure
↓
label = graph beneficial
```

That would simply teach the Week 17 model to reproduce itself.

Correct:

```text baseline retrieval
+
graph retrieval
↓
independent evaluation
↓
graph benefit label
```

The target must come from measured retrieval/evidence outcomes.

---

# 13. Two-stage target design

There are two sensible target choices.

### Target A — retrieval failure

```text Was the initial evidence insufficient?
```

This is the existing V3 target.

### Target B — graph utility

```text Did graph escalation improve the result?
```

This is directly relevant to Week 17.

A useful first architecture is:

```text V3 failure predictor
       ↓
estimated failure
       ↓
graph escalation
```

Only later consider:

```text direct graph-benefit predictor
```

if evidence shows that failure prediction is not a good proxy for graph usefulness.

---

# 14. Why V3 may still be a useful proxy

The graph is intended as:

```text stronger evidence acquisition
```

Therefore many cases where initial retrieval fails may also be the cases where graph escalation helps.

That relationship should be measured:

```text P(graph rescue | retrieval failure)
```

and:

```text P(graph rescue | predicted failure)
```

But do not assume:

```text failure = graph benefit
```

---

# 15. Main Week 17 hypothesis

A simple hypothesis can be:

> **Selective graph escalation can retain most of the evidence-quality gain of always-graph retrieval while invoking the graph substantially less often.**

This hypothesis is stronger than:

```text graph is useful
```

because graph usefulness should already have been tested in Week 16.

Week 17 is specifically about:

```text selective invocation
```

---

# 16. Selection threshold

Start with:

```text threshold ∈ {0.1,0.2,...,0.9}
```

or another reasonable grid.

For each threshold measure:

```text graph invocation rate
evidence recall
rescue rate
regression rate
cost
latency
```

The resulting curve may look conceptually like:

```text low threshold
→ many graph calls
→ high quality
→ high cost

high threshold
→ few graph calls
→ low cost
→ more missed rescues
```

Do not choose the best threshold on the test set.

---

# 17. Threshold selection protocol

Use:

```text TRAIN
fit V3

VALIDATION
choose threshold

TEST
evaluate fixed threshold
```

After selecting the threshold:

```text freeze it
```

Then run the final test.

Never:

```text inspect test failures
→ change threshold
→ rerun test
→ report improved number
```

That turns the test set into a tuning set.

---

# 18. Calibration matters

If V3 outputs:

```text 0.8
```

it should ideally behave like:

```text approximately 80% failure probability
```

But raw classifier scores are not automatically calibrated.

Evaluate:

```text reliability curve
ECE
Brier score
```

when sample size permits.

Potential calibration methods:

```text Platt scaling
isotonic regression
```

should be treated as separate experiments.

Do not calibrate directly on the test set.

---

# 19. Fixed-threshold baseline

Before trusting V3:

```text use a simple retrieval statistic
```

such as:

```text top reranker score < threshold
```

or:

```text score gap < threshold
```

to invoke graph retrieval.

This answers:

```text does a learned failure detector add anything?
```

over:

```text a trivial signal?
```

This is an important baseline.

---

# 20. Always-graph upper reference

The system may also include:

```text ALL_GRAPH
```

where every question receives graph escalation.

This is operationally inefficient but scientifically valuable.

It measures:

```text maximum observed value of graph retrieval
```

under the current experiment.

The selective policy should ideally approach:

```text always-graph quality
```

while using:

```text substantially fewer graph calls
```

---

# 21. No-graph lower reference

Likewise:

```text NO_GRAPH
```

establishes the cost floor.

This allows a useful three-point view:

```text NO_GRAPH
↓
SELECTIVE_GRAPH
↓
ALL_GRAPH
```

The research objective is not necessarily to make selective graph equal all-graph.

A successful policy may instead provide:

```text most of the quality
at a fraction of the graph usage
```

---

# 22. Graph escalation budget

Define explicit limits.

For example:

```text max graph invocations per query = 1
max graph hops = 1
neighbor cap = N
final context = fixed
```

The first experiment should have:

```text one escalation only
```

This keeps causal attribution simple.

Do not allow:

```text repeated graph → reretrieve → re-evaluate → graph again
```

in the initial policy.

---

# 23. Prevent escalation loops

A robust implementation should guarantee:

```text baseline
→ graph escalation
→ stop
```

not:

```text baseline
→ graph
→ failure predictor
→ graph
→ graph
→ ...
```

Implement a state flag such as:

```text graph_escalated = true
```

or an equivalent explicit control.

The exact code should follow the existing architecture.

---

# 24. Context budget fairness

Suppose:

```text NO_GRAPH
final context = 10 units

GRAPH
final context = 20 units
```

Then graph may improve answers simply because it supplies more evidence.

Therefore test at least one matched condition:

```text same final context budget
```

where graph candidates compete with baseline candidates.

If graph is allowed a larger context budget, report that explicitly.

---

# 25. Graph rescue under fixed budget

The strongest demonstration would be:

```text baseline:
10-unit context

graph:
same 10-unit context

graph replaces or adds candidates intelligently
```

and still:

```text graph > baseline
```

That would suggest:

```text relationship quality
```

rather than merely:

```text more text
```

is contributing.

---

# 26. Candidate-preservation policy

One risk of graph escalation is:

```text graph candidate crowding
```

For example:

```text baseline seeds:
A B C D E

graph candidates:
F G H I J
```

A global reranker may remove:

```text B
```

even when B is necessary.

A safe first policy is:

```text retain top-M baseline seeds
+
rank graph-added candidates into remaining slots
```

This protects against regressions.

Whether this policy is used should be documented and held fixed during the primary comparison.

---

# 27. Selective graph policy state machine

A clean first implementation is:

```text
START
  ↓
INITIAL_RETRIEVAL
  ↓
FEATURE_EXTRACTION
  ↓
V3_PREDICT
  ↓
 threshold not crossed ─────→ ANSWER
  │
  threshold crossed
  ↓
GRAPH_ESCALATION
  ↓
FINAL_EVIDENCE
  ↓
ANSWER
```

There should be no hidden state transitions.

Log each transition.

---

# 28. Per-question provenance

Each result should indicate:

```json
{
  "question_id":"...",
  "initial_route":"STATIC",
  "graph_invoked":true,
  "failure_probability":0.81,
  "threshold":0.62,
  "initial_evidence_ids":["..."],
  "graph_added_ids":["..."],
  "final_evidence_ids":["..."]
}
```

This is an example only.

The repository's existing schema should be used where possible.

The key requirement is:

```text decision provenance
```

must be reconstructable.

---

# 29. Graph decision audit

For each escalated query, inspect:

```text Was V3 correct that retrieval looked weak?
Did graph actually add useful evidence?
Was graph invocation necessary?
Did graph improve final evidence?
```

For non-escalated queries:

```text Did baseline succeed?
Was graph actually unnecessary?
Did the policy miss a graph rescue?
```

This identifies:

```text true positive escalation
false positive escalation
true negative
false negative
```

from an operational perspective.

---

# 30. Escalation confusion matrix

Define:

```text P = graph would have helped
N = graph would not have helped

Predicted escalate:
TP = graph used and beneficial
FP = graph used but not beneficial

Predicted no graph:
TN = graph skipped and baseline was sufficient
FN = graph skipped and graph would have helped
```

This is useful because the operational meaning differs from ordinary binary classification.

The most expensive error may be:

```text FP
```

if graph usage is costly.

The most damaging quality error may be:

```text FN
```

if graph would have rescued an important scientific question.

---

# 31. Cost-sensitive thresholding

The threshold should eventually reflect operational cost.

For example:

```text expensive graph
→ require strong evidence of likely benefit
```

versus:

```text cheap graph
→ tolerate more invocations
```

But do not use subjective costs.

Use measured:

```text latency
provider calls
tokens
compute
```

and document any weighting.

---

# 32. Quality-cost frontier

Plot:

```text X = graph invocation rate or cost/query

Y = evidence recall
```

Then identify:

```text NO_GRAPH
SELECTIVE thresholds
ALL_GRAPH
```

This creates a direct frontier.

A strong result would look conceptually like:

```text selective policy
approaches all-graph recall
while remaining much closer to no-graph cost
```

The exact result must come from data.

---

# 33. Answer-quality frontier

Repeat the same analysis for:

```text answer correctness
groundedness
citation quality
```

because retrieval quality and final answer quality can diverge.

A graph policy may achieve:

```text retrieval gain
```

without:

```text answer gain
```

which points to a generation bottleneck.

---

# 34. Primary metrics

Recommended primary metrics:

```text evidence recall
graph invocation rate
cost/query
p50 latency
p95 latency
```

Secondary:

```text answer correctness
groundedness
citation precision
citation completeness
unsupported claim rate
```

Diagnostic:

```text rescue rate
regression rate
V3 classification performance
calibration
feature importance
```

---

# 35. Question-type analysis

Always break down:

```text SIMPLE
MULTI_HOP
TEMPORAL
CONFLICTING
CHAIN
```

The expectation is not:

```text graph should help everything
```

Instead measure where graph escalation matters.

Example interpretation:

```text SIMPLE
graph rarely needed

MULTI_HOP
graph frequently useful

TEMPORAL
moderately useful

CONFLICTING
useful only with high-quality relation extraction
```

These are examples of possible patterns only.

---

# 36. Paper-level analysis

Graph usefulness may also vary by paper.

Inspect:

```text paper with many tables
paper with many equations
paper with extensive citations
paper with dense methods
```

and compare with:

```text prose-dominant papers
```

This may reveal structural conditions under which graph escalation is useful.

Do not turn such observations into broad claims without enough papers.

---

# 37. Scientific-structure analysis

Use V6 evidence labels where available.

Possible comparison:

```text PROSE
TABLE
EQUATION
NUMERIC_RESULT
TEMPORAL
```

Then compute:

```text graph rescue rate by structure type
```

This connects V7 directly to V6.

If graph escalation mainly rescues:

```text TABLE
```

cases, the contribution should say so.

---

# 38. Domain-shift analysis

If V5 created an unseen-domain benchmark, evaluate Week 17 under:

```text source domain
target domain
```

separately.

A policy can appear strong on:

```text astrophysics/cosmology
```

but fail on:

```text unseen domain
```

because:

```text V3 scores are miscalibrated
graph relation coverage differs
```

This is valuable evidence about generalization.

---

# 39. Zero-shot policy transfer

A strict transfer test is:

```text train V3 on source domain

freeze predictor

apply same threshold

use graph escalation on target domain
```

Do not tune:

```text threshold
feature normalization
classifier
```

on target test data.

If target performance drops, report it.

That is the point of the transfer experiment.

---

# 40. Few-shot recalibration

A later experiment can provide a small target-domain validation set:

```text 10–50 examples
```

or another predeclared size.

Use it only for:

```text calibration
threshold selection
```

not:

```text test evaluation
```

Compare:

```text zero-shot
vs
few-shot calibrated
```

This measures:

```text adaptation efficiency
```

rather than hiding domain shift.

---

# 41. Do not mix V3 training with Week 17 test labels

If you retrain V3 using graph-benefit labels:

```text all test queries remain untouched
```

and:

```text training / validation / test
```

must remain clean.

Otherwise Week 17 becomes impossible to interpret.

---

# 42. Potential direct-benefit predictor

Only if V3 proves insufficient, consider:

```text Question
↓
initial retrieval
↓
feature extraction
↓
predict graph usefulness
↓
graph / no graph
```

This is a new model target:

```text graph_beneficial
```

Advantages:

```text directly optimizes the operational decision
```

Risks:

```text harder labels
more experiments
more leakage risk
```

Do not begin with this unless data supports it.

---

# 43. Creating graph-benefit labels

For each question:

```text run baseline
run graph condition
compare independent evidence outcome
```

Possible label:

```text graph_helpful = baseline insufficient AND graph sufficient
```

A richer target can be:

```text improvement = graph_recall - baseline_recall
```

For example:

```text 0
no gain

0.5
partial rescue

1
full rescue
```

This can later support regression or ranking approaches.

---

# 44. Hard negative for escalation

A particularly useful case:

```text V3 says failure
but graph cannot help
```

This is a false-positive escalation.

Examples may include:

```text source corpus genuinely lacks evidence
bad PDF extraction
wrong question
graph relation absent
all available evidence already retrieved
```

These examples prevent the policy from learning:

```text uncertainty → always graph
```

which would destroy cost savings.

---

# 45. Hard negative for non-escalation

The opposite:

```text V3 says sufficient
but graph would rescue
```

This is the most important false negative.

Inspect why V3 missed it.

Potential causes:

```text high semantic similarity
wrong paper
wrong section
single strong distractor
missing second-hop relation
dense/BM25 agreement despite incompleteness
```

These cases can reveal missing retrieval-state features.

---

# 46. Feature ablation in Week 17

Use the final V3 features and test:

```text ranking only

ranking + agreement

ranking + diversity

ranking + scientific anchors

all features
```

Do not keep every possible feature without measurement.

The question is:

```text what signals tell the system that graph escalation is worthwhile?
```

---

# 47. Feature interactions

Potential interactions include:

```text low top score
+
high dense/BM25 disagreement
```

or:

```text high top score
+
low evidence diversity
```

A tree-based model may capture these interactions.

But first compare against:

```text logistic regression
```

so the gain is interpretable.

---

# 48. Model progression

Recommended:

```text M0
single score threshold

M1
logistic regression

M2
small tree / gradient boosting

M3
more complex model only if justified
```

The final model should be the smallest one that gives measurable operational improvement.

A complicated predictor is not automatically better research.

---

# 49. Why a simple model may win

The available retrieval-state dataset may be modest.

A small model can:

```text train quickly
avoid overfitting
remain interpretable
calibrate more easily
```

If it performs as well as a larger model, that is a positive result.

Do not optimize model sophistication for its own sake.

---

# 50. Data requirements

A good Week 17 dataset should contain:

```text question
initial route
retrieval features
initial evidence
graph-expanded evidence
ground-truth evidence result
graph benefit
```

and provenance:

```text corpus version
retrieval configuration
graph version
V3 model version
threshold
```

This creates an auditable policy dataset.

---

# 51. Small-data warning

If the current benchmark is still small:

```text do not train a graph-benefit predictor immediately
```

A pilot can instead measure:

```text V3 prediction
+
graph rescue relationship
```

and determine whether:

```text graph benefit
```

is predictable enough to justify a dedicated model.

This avoids another underpowered learned component.

---

# 52. Synthetic negatives warning

Do not inflate the Week 17 dataset with obviously bad synthetic retrieval.

Bad example:

```text random unrelated graph nodes
```

This makes escalation prediction unrealistically easy.

Better hard negatives:

```text semantically similar node
wrong relation

correct paper
wrong section

correct entity
wrong quantity

correct quantity
wrong time

correct relation
but no useful answer evidence
```

Track synthetic and natural examples separately.

---

# 53. Evaluation independence

The clean evaluation stack is:

```text model training
↓
validation threshold selection
↓
frozen test policy
↓
independent evidence evaluation
```

Do not allow:

```text graph rescue result
```

to influence:

```text test threshold
```

after test evaluation begins.

---

# 54. Oracle invocation analysis

An Oracle graph policy is useful for answering:

```text What is the maximum attainable selective benefit?
```

Conceptually:

```text if graph improves recall:
    invoke
else:
    skip
```

This requires knowledge of the outcome and therefore:

```text test-time invalid
```

It exists only for analysis.

A useful diagnostic is:

```text learned policy graph invocation
vs
oracle-required graph invocation
```

The gap is:

```text policy regret
```

---

# 55. Regret-style metric

Define:

```text oracle quality
-
policy quality
```

and:

```text unnecessary graph calls
+
missed graph rescues
```

The exact formal regret metric can be simple.

The key question:

```text How far is the learned policy from the best decision that could have been made with hindsight?
```

Do not describe this as true decision-theoretic regret unless the formal setup supports that claim.

---

# 56. Policy regret decomposition

A useful breakdown:

```text missed beneficial escalation
```

versus:

```text unnecessary escalation
```

This distinguishes:

```text quality regret
```

from:

```text efficiency regret
```

A policy can have:

```text high recall
```

but poor efficiency because it invokes graph too often.

---

# 57. Graph invocation rate

One of the key Week 17 outputs:

```text % of queries sent to graph
```

This should always be reported alongside:

```text evidence recall
```

For example:

```text 100% graph → 0.90 recall
 60% graph → 0.88 recall
 25% graph → 0.84 recall
  0% graph → 0.70 recall
```

Numbers are illustrative only.

The real experiment supplies the values.

---

# 58. Selective risk view

Another useful framing is:

```text coverage
vs
error / failure
```

where:

```text coverage = fraction handled without escalation
```

and:

```text selective failure = failure rate among non-escalated queries
```

A strong policy should produce:

```text high non-escalated coverage
+
low failure among non-escalated queries
```

This connects Week 17 to selective prediction.

---

# 59. Risk-coverage curve

Plot:

```text non-escalated coverage
vs
evidence failure rate
```

Potentially also:

```text answer failure rate
```

This may reveal whether confidence-based gating is useful even before considering graph cost.

Do not claim formal selective classification guarantees unless the evaluation supports them.

---

# 60. Escalation precision

Useful operational metric:

```text precision of graph invocation
=
beneficial graph calls
/
all graph calls
```

High precision means:

```text when the policy asks for graph,
it is often useful
```

This is especially important when graph retrieval is expensive.

---

# 61. Escalation recall

Another operational metric:

```text graph rescue recall
=
beneficial graph cases detected
/
all graph-beneficial cases
```

This measures:

```text how many opportunities the policy captures
```

A policy can have:

```text high precision
low recall
```

or:

```text low precision
high recall
```

The tradeoff is the core Week 17 problem.

---

# 62. Cost per rescued query

A particularly understandable metric:

```text additional graph cost
/
number of rescued queries
```

For example conceptually:

```text graph provider cost
÷
successful graph rescues
```

Use actual measured cost.

For offline-only graph traversal, use:

```text added compute time
```

instead of provider dollars.

---

# 63. Latency per rescue

Similarly:

```text added latency
/
graph-rescued queries
```

This shows whether:

```text graph escalation
```

is operationally expensive.

Again, report actual values.

---

# 64. Answer-level graph rescue

Retrieval rescue is not enough.

Track:

```text baseline answer incorrect
graph answer correct
```

This is a true end-to-end rescue.

Also:

```text baseline retrieval improved
but answer remained incorrect
```

which suggests:

```text generation bottleneck
```

This distinction should appear in the final analysis.

---

# 65. Citation-level graph rescue

A graph may recover:

```text exact supporting source
```

even when the baseline generated a weak citation.

Measure:

```text citation precision improvement
citation completeness improvement
unsupported claim reduction
```

This can create value even when answer wording remains similar.

---

# 66. V2 integration point

The clean order is:

```text initial retrieval
↓
V3 prediction
↓
graph escalation if selected
↓
final evidence
↓
answer
↓
V2 verification
```

This lets V2 determine whether:

```text graph-added evidence
```

actually improved:

```text support for claims
```

Do not have V2 determine whether to invoke graph during the first Week 17 experiment.

That would introduce another feedback loop.

---

# 67. Full mature architecture

The eventual system can become:

```text
                         Question
                            |
                            v
                     Pre-retrieval route
                            |
                            v
                    Initial retrieval
                            |
                            v
                  Retrieval-state features
                            |
                            v
                     V3 failure model
                       /          \
                 sufficient        likely failure
                     |                   |
                     |                   v
                     |             Graph retrieval
                     |                   |
                     └──────────┬────────┘
                                v
                          Final evidence
                                |
                                v
                              Answer
                                |
                                v
                         V2 verification
                                |
                                v
                        claims + citations
```

This is a future target.

Week 17's actual experiment should remain simpler.

---

# 68. Do not let V2 influence the primary gate

A tempting architecture is:

```text generate answer
↓
verify
↓
if unsupported
    graph
```

That is a valid future system but not the clean first Week 17 experiment.

Why?

Because then graph invocation depends on:

```text answer generation quality
+
verifier quality
```

rather than:

```text retrieval-state quality
```

Keep the first causal question narrow.

---

# 69. Graph escalation trigger alternatives

Possible triggers:

```text V3 failure probability

top reranker score

confidence gap

dense/BM25 disagreement

fixed route type

question type
```

The hierarchy should be:

```text simple rule
→ V3 learned predictor
→ more complex policy only if justified
```

This prevents needless model stacking.

---

# 70. Route-type interaction

Graph usefulness may depend on initial route.

For example:

```text SIMPLE
→ rarely graph

MULTI_HOP
→ graph frequently useful
```

A stratified analysis can reveal:

```text graph usage conditional on route
```

But do not use route type as the only graph gate unless validated.

---

# 71. Compass confidence interaction

If Compass exists in the final implementation, compare:

```text Compass confidence
+
retrieval-state features
```

against:

```text retrieval-state features only
```

This can test whether:

```text question-only uncertainty
```

adds value after evidence is observed.

It must remain an ablation, not a hidden change to the main predictor.

---

# 72. Domain-general features

For V5 transfer, favor features likely to generalize:

```text score shape
rank gaps
retrieval agreement
diversity
semantic similarity
```

Be cautious with:

```text domain-specific keyword rules
```

such as:

```text H0
Neff
Ωm
```

These may make the policy look stronger in astrophysics while hurting transfer.

---

# 73. Scientific-anchor coverage

If V3 uses scientific-anchor features, evaluate:

```text source-domain performance
target-domain performance
```

and inspect whether feature distributions shift.

For example:

```text anchor coverage mean
source = high
target = low
```

The model may interpret low coverage as:

```text retrieval failure
```

when it really indicates:

```text vocabulary mismatch
```

This is a classic domain-shift failure.

---

# 74. Feature distribution shift

Compute simple statistics such as:

```text mean
median
standard deviation
quantiles
```

for V3 features in:

```text source
target
```

where available.

Potentially measure distribution divergence.

The exact statistic can be chosen later.

The important purpose is:

```text understand why a frozen predictor transfers or fails
```

---

# 75. Policy calibration under shift

A source-domain predictor may produce:

```text 0.8 failure probability
```

but target-domain actual failure frequency may be:

```text 0.5
```

This is miscalibration.

Measure calibration separately by domain.

A policy can have:

```text good ranking
```

but:

```text poor calibration
```

and still require threshold adaptation.

These are different properties.

---

# 76. Few-shot threshold calibration

A useful low-cost transfer experiment is:

```text frozen V3 model
+
small target validation set
+
new threshold
```

This does not retrain the classifier.

It asks:

```text can decision calibration transfer with very little target-domain supervision?
```

That can be a stronger practical story than:

```text retrain everything on target data
```

---

# 77. Cross-domain graph relation compatibility

The graph itself may behave differently across domains.

Inspect:

```text edge precision
edge density
relation distribution
```

source vs target.

If:

```text graph precision drops sharply
```

then poor selective performance may be caused by:

```text graph construction
```

not:

```text V3 policy
```

Keep these failure modes separate.

---

# 78. Graph quality gating

A later policy could include:

```text graph quality estimate
```

but do not add this immediately.

First establish:

```text graph is sufficiently reliable
```

for the chosen domains.

Otherwise the policy is trying to predict whether to invoke an unreliable mechanism.

---

# 79. Benchmark size

Week 17 should ideally use the expanded benchmark from V4/V5.

If the graph-specific subset is small:

```text report it as a targeted subset analysis
```

and do not generalize to all AtlasRAG questions.

Small samples are particularly dangerous for:

```text graph rescue rate
```

because one or two queries can move the percentage substantially.

---

# 80. Statistical comparison

Primary paired comparisons:

```text NO_GRAPH vs SELECTIVE_GRAPH

NO_GRAPH vs ALL_GRAPH

SELECTIVE_GRAPH vs ALL_GRAPH
```

For each:

```text evidence recall
answer correctness
```

and, where useful:

```text citation metrics
```

Use:

```text paired bootstrap
or
appropriate paired tests
```

for the metric type and sample size.

Report uncertainty.

Do not rely on:

```text one decimal percentage difference
```

alone.

---

# 81. Threshold sweep statistics

Threshold sweeps contain multiple correlated operating points.

Do not treat every point as an independent hypothesis test.

Use the sweep primarily to build:

```text quality-cost frontier
```

Then designate:

```text one primary threshold
```

from validation.

The test evaluation should use the frozen threshold.

---

# 82. Cost confidence intervals

Cost is often deterministic enough at a fixed configuration, but actual provider usage can vary.

Persist:

```text tokens
provider calls
latency
```

per query.

Then summarize:

```text mean
median
p95
```

and confidence intervals where useful.

Do not infer exact provider cost from logical call counts.

---

# 83. Provider instrumentation requirement

Week 17 should preserve the instrumentation improvement planned earlier.

Every run should distinguish:

```text logical requests
provider calls
cache hits
cache misses
retry attempts
rate-limit errors
connection errors
prompt tokens
completion tokens
```

This is particularly important because graph escalation adds conditional calls.

You need to know:

```text did graph actually increase external LLM usage?
```

rather than assuming it did.

---

# 84. Caching considerations

Graph retrieval itself can be deterministic and cheap.

If graph extraction used cached LLM outputs:

```text construction cost
```

should not be charged repeatedly at query time.

If query-time graph reasoning uses an LLM:

```text cache behavior
```

must be recorded.

Do not mix:

```text offline extraction tokens
```

with:

```text online answering tokens
```

without labeling them.

---

# 85. Reproducibility manifest

Each Week 17 experiment should save:

```text experiment_id
git_commit
benchmark_version
corpus_version
graph_schema_version
graph_index_version
V3_model_version
threshold
retrieval_config
answer_model
answer_prompt_version
timestamp
```

and:

```text provider metrics
```

This makes selective-policy results reproducible.

---

# 86. Suggested result artifact

A machine-readable record can contain:

```json
{
  "experiment":"W17-D",
  "threshold":0.62,
  "graph_invocation_rate":0.31,
  "evidence_recall":0.86,
  "baseline_recall":0.72,
  "always_graph_recall":0.89,
  "mean_latency_seconds":2.1,
  "mean_graph_latency_seconds":0.4
}
```

Values are illustrative.

Do not create fake result files with example values.

The actual experiment should populate them.

---

# 87. Rescue examples for qualitative analysis

Select examples where:

```text baseline failed
graph succeeded
```

and show:

```text question
baseline evidence
graph seed
graph path
graph-added evidence
final evidence
answer
citations
```

This is one of the strongest ways to explain what the graph actually contributes.

---

# 88. Regression examples

Also show:

```text baseline succeeded
graph-selected path caused failure
```

Investigate:

```text graph distractor
reranking error
candidate crowding
wrong edge
```

A serious research analysis must include these.

---

# 89. False-positive escalation examples

Example:

```text V3 confidence = high failure
graph invoked
graph adds nothing useful
```

Inspect why.

Possible reason:

```text source corpus lacks the required evidence
```

This indicates:

```text graph cannot solve corpus absence
```

and helps define the limits of escalation.

---

# 90. False-negative escalation examples

The most valuable failures may be:

```text V3 confidence = low failure
graph skipped
graph would have rescued the case
```

Inspect:

```text what feature pattern caused the miss?
```

Possible lesson:

```text top score was misleadingly high
```

or:

```text evidence diversity looked sufficient
```

These can motivate the next V3 feature experiment.

---

# 91. Graph usefulness by initial retrieval quality

Stratify queries by:

```text top score band
```

or:

```text baseline recall band
```

Then measure:

```text graph rescue
```

This can answer:

```text Does graph help only when retrieval is obviously weak?
```

or:

```text Does graph rescue subtle retrieval failures too?
```

The latter would strongly motivate learned selective escalation.

---

# 92. Graph usefulness by disagreement

Similarly stratify by:

```text dense/BM25 agreement
```

and measure:

```text graph benefit
```

This tests a concrete V3 hypothesis.

Do not assume disagreement is valuable just because it sounds intuitive.

---

# 93. Graph usefulness by evidence density

Use V6 structure labels:

```text number of table/equation/numeric units
```

where available.

Then inspect:

```text graph benefit
```

A strong pattern here could connect:

```text V6 structure-aware retrieval
```

to:

```text V7 graph escalation
```

in a principled way.

---

# 94. Query-level explanation

Every final result should be explainable as:

```text Why did graph run?
Why did graph not run?
What evidence did graph add?
Did the added evidence matter?
```

If the system cannot answer these questions from logs, the experiment is not ready for final interpretation.

---

# 95. Implementation architecture

The ideal separation is:

```text initial retriever
      ↓
state feature extractor
      ↓
failure predictor
      ↓
escalation policy
      ↓
graph retriever
```

Possible conceptual modules:

```text retrieval_state.py
failure_predictor.py
escalation_policy.py
graph/query.py
```

Use actual project architecture when available.

Do not duplicate existing functions.

---

# 96. Escalation policy API

Conceptually:

```python
decision=policy.decide(features)
```

returning something like:

```text
NO_GRAPH
GRAPH
```

The policy should not itself:

```text retrieve
generate answers
inspect gold evidence
```

Keep responsibilities separate.

---

# 97. Graph retriever API

Conceptually:

```python
result=graph_retriever.expand(
   seed_ids=seed_ids,
   max_hops=1,
   neighbor_cap=8
)
```

Again, use repository conventions.

The API should expose enough metadata to log:

```text seeds
edges
neighbors
timing
```

---

# 98. Testing escalation policy

Unit tests should include:

```text high failure probability
→ graph

low failure probability
→ no graph
```

and:

```text threshold boundary
```

For example:

```text p == threshold
```

must have explicitly defined behavior.

Do not leave boundary semantics ambiguous.

---

# 99. Escalation idempotence

Running the policy twice with the same:

```text features
threshold
model
```

should produce the same decision.

This matters for:

```text reproducibility
debugging
```

unless stochastic inference is explicitly enabled.

---

# 100. Graph invocation logging

At minimum log:

```text question_id
decision
probability
threshold
graph_invoked
```

Better:

```text decision_reason
feature snapshot
```

This allows post-hoc analysis without rerunning the model.

---

# 101. No hidden post-processing

Do not write code such as:

```python
if question_type=="MULTI_HOP":
    use_graph=True
```

inside the implementation while claiming:

```text V3 selective graph policy
```

Any rule that affects invocation must be:

```text explicit
versioned
evaluated
```

---

# 102. Training/test leakage through graph state

A subtle leakage risk exists when:

```text graph built from all papers
```

but:

```text benchmark split is supposed to be paper-disjoint
```

Graph construction can use source corpus structure from all papers, but if the graph contains:

```text benchmark-specific labels
gold claims
test annotations
```

then leakage occurs.

The graph should contain only:

```text corpus-derived evidence
```

unless a separate experiment explicitly studies annotation-aware methods.

---

# 103. Cross-paper graph leakage

Be especially cautious with:

```text benchmark question
→ known gold evidence
→ graph edge
```

This must never be encoded.

The graph should be generated:

```text independently of test questions
```

where practical.

This is one of the strongest reproducibility safeguards.

---

# 104. Relation extraction from citations

A citation graph can be built offline from paper metadata.

But a benchmark question should not receive special citation edges because:

```text its gold answer mentions that paper
```

Again:

```text corpus construction
```

must remain separate from:

```text benchmark annotations
```

---

# 105. Evaluation under frozen graph

After the graph version is frozen:

```text no edge edits
```

should occur during test evaluation.

If a graph bug is discovered:

```text create graph v2
```

and rerun the experiment as a new version.

Do not patch the graph silently midway.

---

# 106. Re-running after a bug

If:

```text V7 graph bug
```

is discovered after test execution:

```text preserve original run
↓
document bug
↓
fix graph
↓
version graph
↓
rerun affected experiments
```

Do not overwrite:

```text original results
```

This preserves scientific chronology.

---

# 107. Primary experiment order

Recommended Week 17 order:

```text W17-A
NO_GRAPH

W17-B
ALL_GRAPH

W17-C
fixed-threshold graph

W17-D
V3-selective graph

W17-E
threshold sweep

W17-F
rescue/regression analysis

W17-G
answer + citation evaluation

W17-H
domain-transfer check if available
```

The exact naming can differ.

---

# 108. What to compare first

The central comparison should be:

```text NO_GRAPH
vs
V3_SELECTIVE_GRAPH
```

Then ask:

```text how close is selective graph
to ALL_GRAPH?
```

That directly evaluates the research question.

---

# 109. Primary success condition

A reasonable success pattern is:

```text SELECTIVE_GRAPH
>
NO_GRAPH
```

for evidence quality,

while:

```text SELECTIVE_GRAPH
<<
ALL_GRAPH
```

in graph invocation rate.

The actual magnitude should be determined before the final interpretation.

Do not invent an arbitrary threshold such as:

```text must reduce graph usage by 50%
```

unless the research plan establishes that criterion beforehand.

---

# 110. Stronger success condition

The most compelling result would be:

```text selective graph
≈ always graph
```

in evidence quality,

while:

```text selective graph
<< always graph
```

in:

```text graph invocation
cost
latency
```

This would provide strong evidence that:

```text retrieval-state-aware gating
```

has operational value.

---

# 111. Weak success condition

If selective graph improves:

```text evidence quality
```

but invokes graph on:

```text 90%+ of queries
```

then the policy may have limited value over:

```text always graph
```

The result can still be useful.

It would suggest:

```text current failure detection is not selective enough
```

or:

```text graph is broadly necessary
```

The data should determine which interpretation is supported.

---

# 112. Failure condition

If:

```text selective graph
≈ no graph
```

and:

```text graph rescues exist
```

but are frequently missed, the policy may need better prediction.

Then the next direction could be:

```text direct graph-benefit prediction
```

or:

```text richer retrieval-state features
```

rather than a larger graph.

---

# 113. Cost-dominant failure

If:

```text selective graph
improves recall
```

but:

```text graph cost is too large
```

then the next research question could become:

```text cheaper graph approximation
```

or:

```text lightweight relation filters
```

Do not respond by automatically optimizing the model.

First identify whether:

```text retrieval quality
or
graph computation
```

is the actual bottleneck.

---

# 114. V2 downstream failure

Suppose:

```text graph retrieval
↑ evidence recall

but

unsupported claims unchanged
```

Then:

```text graph solves retrieval
```

but:

```text verification/generation remains limiting
```

This is a valid finding.

It suggests future work should focus on:

```text V2 verifier
or
answer grounding
```

rather than further graph retrieval.

---

# 115. Benchmark limitations

Explicitly record:

```text number of V7 questions
domain coverage
paper count
question types
graph relation coverage
human audit size
```

Do not claim:

```text universal scientific evidence reasoning
```

from one corpus.

---

# 116. Publication framing

A defensible V7/Week 17 framing is:

> We evaluate whether retrieval-state-aware selective graph expansion can recover relationship-dependent scientific evidence while avoiding unnecessary graph computation.

That statement describes:

```text mechanism
evaluation
```

without assuming the result.

A stronger claim can only be made after measurement.

---

# 117. Novelty review

Before publication, run a fresh literature review covering:

```text adaptive RAG
retrieval routing
selective retrieval
graph RAG
knowledge graph RAG
retrieval uncertainty
retrieval failure detection
selective graph expansion
cost-aware retrieval
scientific RAG
```

Clearly separate:

```text existing methods
```

from:

```text AtlasRAG's specific experimental combination
```

Do not claim:

```text first
new
novel
```

without a current literature basis.

---

# 118. Documentation artifacts

Recommended outputs:

```text
01_W17_POLICY_SPEC.md
02_W17_ESCALATION_DATASET.md
03_W17_EXPERIMENT_MATRIX.md
04_W17_RESULTS.md
05_W17_RESCUE_REGRESSION_ANALYSIS.md
06_W17_COST_QUALITY_FRONTIER.md
07_W17_TRANSFER_ANALYSIS.md
08_W17_DECISION.md
```

Raw:

```text
data/v7_escalation/
experiments/w17/
```

Use current repository conventions when they differ.

---

# 119. Experiment manifest

Each experiment should identify:

```text
experiment_id
baseline_version
graph_version
V3_model_version
threshold
feature_version
benchmark_version
corpus_version
answer_model
prompt_version
git_commit
```

Also record:

```text date
run status
provider metrics
```

---

# 120. Recommended command sequence

First:

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

Then verify:

```text V6 result
graph implementation
V3 implementation
benchmark version
```

Do not assume all corresponding files exist.

---

# 121. Before modifying code

Create a clean checkpoint:

```powershell
git status --short
git diff
```

If there are unrelated changes:

```text do not overwrite them
```

Understand what belongs to:

```text prior work
```

and:

```text Week 17
```

before editing.

---

# 122. Recommended commits

Logical commits might be:

```text W17 escalation policy infrastructure

W17 V3 graph gating integration

W17 threshold sweep experiments

W17 analysis tooling

W17 final evaluation
```

Do not bundle:

```text code
benchmark edits
result changes
```

into one opaque commit.

---

# 123. Tests before experiments

At minimum:

```text policy threshold tests
feature schema tests
graph invocation once-only test
logging/provenance tests
benchmark split tests
```

Then run:

```powershell
python -m pytest -q
```

Record:

```text test count
pass/fail
commit
```

---

# 124. Pilot before full run

Start with:

```text 5–10 questions
```

and verify:

```text decision
→ graph invocation
→ graph result
→ final evidence
```

manually.

Do not spend the full provider budget before confirming the policy behaves correctly.

---

# 125. Pilot checklist

For each pilot:

```text Did V3 produce a probability?

Did threshold logic behave correctly?

Was graph invoked exactly when expected?

Were baseline seeds preserved?

Was graph provenance logged?

Was final context bounded?

Were provider calls counted?

Was answer output persisted?
```

Only after these pass should the full run begin.

---

# 126. Full-run execution

Run each condition separately.

Do not use one giant shell command such as:

```powershell
runA;runB;runC;runD
```

while experimenting.

Separate runs make:

```text provider failures
partial output
timing
debugging
```

much easier.

---

# 127. Rate-limit handling

The current LLM layer has bounded retry behavior.

Week 17 must preserve:

```text finite retries
explicit final failure
persisted instrumentation
```

If a run hits the provider limit:

```text stop cleanly
```

and record:

```text partial
```

rather than pretending the experiment completed.

Do not silently drop failed queries.

---

# 128. Partial-run handling

A partially completed experiment should have:

```text status = PARTIAL
```

or an equivalent explicit status.

Record:

```text completed queries
failed queries
skipped queries
```

A partial run is not a full evaluation.

Do not calculate final benchmark statistics as though missing queries were successes.

---

# 129. Reproducible threshold sweep

The threshold sweep should use:

```text same model
same feature vectors
same graph
same benchmark
```

for every threshold.

Only:

```text threshold
```

changes.

This isolates the policy effect.

Do not rerun the entire graph construction for every threshold unless technically necessary.

---

# 130. Threshold sweep efficiency

A well-designed implementation should ideally:

```text compute retrieval state once
↓
save feature vectors
↓
evaluate many thresholds offline
```

This avoids repeated provider calls.

The sweep is a decision-layer experiment.

Do not accidentally turn it into:

```text multiple new retrieval experiments
```

---

# 131. Policy artifact

Save the selected policy as a versioned artifact containing:

```text model ID
feature version
threshold
calibration version
graph version
```

For example conceptually:

```text w17_policy_v1.json
```

The actual filename should follow project conventions.

---

# 132. Frozen final policy

Once validation selects:

```text threshold
```

freeze:

```text threshold
model
features
graph config
```

before test execution.

A test result must correspond to exactly one frozen policy.

---

# 133. Per-question decision ledger

Create a table with fields such as:

```text question_id
baseline_recall
graph_recall
failure_probability
threshold
graph_invoked
graph_beneficial
answer_baseline
answer_graph
citation_baseline
citation_graph
latency_baseline
latency_graph
```

This becomes one of the most valuable analysis artifacts.

---

# 134. Graph benefit conditional table

A useful summary table:

```text
Condition
Graph calls
Beneficial calls
Unnecessary calls
Missed rescues
Evidence recall
Cost/query
Latency/query
```

This makes the selective decision directly interpretable.

---

# 135. Primary failure taxonomy

Suggested categories:

```text F1 V3 false negative
F2 V3 false positive
F3 graph extraction error
F4 graph linking error
F5 graph traversal miss
F6 candidate crowding
F7 graph distractor
F8 reranking error
F9 corpus absence
F10 answer-generation failure
F11 citation failure
```

Do not force a single root cause when multiple failures occur.

Record:

```text primary
secondary
```

if necessary.

---

# 136. The most important Week 17 analysis

Compare:

```text cases V3 said NO_GRAPH
```

against:

```text cases graph would have rescued
```

This reveals:

```text under-escalation
```

Then compare:

```text cases V3 said GRAPH
```

against:

```text cases graph helped
```

This reveals:

```text escalation precision
```

These two analyses explain the policy's behavior much better than average accuracy alone.

---

# 137. Policy error decomposition

Conceptually:

```text Total graph-benefit opportunities
│
├── captured
│     └── successful escalation
│
└── missed
      └── false negative

Total graph invocations
│
├── useful
│
└── unnecessary
```

This provides an operational interpretation of:

```text recall
precision
```

for graph invocation.

---

# 138. Selective quality-cost frontier

Produce at least one figure:

```text x-axis = graph invocation rate

y-axis = evidence recall
```

with points for:

```text NO_GRAPH
threshold values
ALL_GRAPH
```

A second figure can show:

```text x-axis = mean additional cost/query

y-axis = answer correctness
```

Do not overproduce figures.

Two strong plots are better than ten decorative ones.

---

# 139. Statistical reporting rule

For every primary comparison report:

```text absolute difference
confidence interval
paired test result where appropriate
```

Example structure:

```text SELECTIVE_GRAPH vs NO_GRAPH
Δ evidence recall = ...
95% CI = [...]
paired test = ...
```

Do not report:

```text p-value
```

without:

```text effect size
```

and context.

---

# 140. Model interpretation

If V3 is logistic regression, report:

```text feature coefficient direction
```

and preferably:

```text standardized importance
```

where appropriate.

For tree-based models, use:

```text permutation importance
```

or another interpretable diagnostic.

Avoid treating model importance as causal proof.

---

# 141. Counterfactual policy analysis

A useful offline diagnostic:

```text What would happen if the threshold moved?
```

Because the feature vectors and graph outcomes are already stored, this can be analyzed without new provider calls.

This allows:

```text policy frontier
```

construction cheaply.

Do not use test labels to tune a final policy after the fact.

---

# 142. Threshold robustness

A strong policy should not collapse from:

```text threshold = 0.61
```

to:

```text threshold = 0.62
```

unless the dataset is tiny.

Inspect:

```text neighborhood around selected threshold
```

on validation.

The final test should still use only the preselected threshold.

---

# 143. Small benchmark uncertainty

If the benchmark is small, threshold estimates may be unstable.

Use:

```text bootstrap sensitivity
```

or:

```text validation resampling
```

where useful.

If uncertainty is large:

```text report it
```

instead of pretending the exact threshold is scientifically meaningful.

---

# 144. Domain transfer policy calibration

If V5 target-domain results exist:

```text freeze source-trained V3
↓
apply threshold
↓
evaluate target
```

Then optionally:

```text small target validation
↓
recalibrate threshold
↓
test target
```

This produces:

```text zero-shot transfer
vs
minimal adaptation
```

and is a strong practical comparison.

---

# 145. Graph transfer policy

Likewise compare:

```text source graph schema
→ target domain
```

and:

```text adapted graph schema
→ target domain
```

Only if target-domain graph construction is reliable.

Do not blame the policy for:

```text broken target graph
```

---

# 146. What not to do

Do not:

```text invoke graph for every query and call it selective

choose threshold from test results

use graph-benefit labels generated from V3 predictions

retrain V3 on the final test set

allow unlimited graph hops

increase context budget without a matched control

silently change graph schema during evaluation

hide graph construction cost

hide failed provider calls

use benchmark gold paths at inference

add question-type hard rules without documenting them

stack V2 verification into the main gate before retrieval-only analysis

report only aggregate recall
```

---

# 147. Expected research outcomes

### Outcome A — strong selective gain

```text selective graph ≈ all-graph quality
+
much lower graph usage
```

This is the strongest result.

### Outcome B — moderate selective gain

```text selective graph > no graph
but
selective graph < all graph
```

Still useful.

### Outcome C — high graph usage

```text selective graph ≈ all graph
but graph invoked almost always
```

The graph may be useful, but the policy is weak.

### Outcome D — poor graph prediction

```text selective graph ≈ no graph
```

Investigate:

```text V3 signal mismatch
graph-benefit not correlated with failure
```

### Outcome E — graph itself weak

```text all graph ≈ no graph
```

Then:

```text policy optimization is premature
```

and the next effort should improve graph quality or return to another bottleneck.

---

# 148. Final V17 decision categories

Use:

```text KEEP
```

when selective graph escalation produces meaningful quality/cost improvement.

```text KEEP WITH QUALIFIERS
```

when the benefit is limited to certain question or evidence types.

```text REJECT
```

when graph escalation adds complexity without enough benefit.

```text DEFER
```

when the dataset, graph quality, or V3 signal quality is insufficient for a reliable conclusion.

---

# 149. Recommended Week 17 deliverables

Target documents:

```text 01_W17_ESCALATION_POLICY_SPEC.md
02_W17_FEATURE_AND_LABEL_SPEC.md
03_W17_EXPERIMENT_MATRIX.md
04_W17_RESULTS.md
05_W17_RESCUE_REGRESSION_ANALYSIS.md
06_W17_COST_QUALITY_FRONTIER.md
07_W17_DOMAIN_TRANSFER.md
08_W17_DECISION.md
```

Raw artifacts:

```text data/v7_escalation/
experiments/w17/
```

Optional figures:

```text figures/w17/
```

Use existing naming conventions if already established.

---

# 150. Minimal Week 17 pilot

If the project is not ready for a large run, the minimum scientifically useful pilot is:

```text frozen V3 model
+
frozen V7 graph
+
small audited question subset
+
NO_GRAPH
+
ALL_GRAPH
+
fixed threshold
```

Measure:

```text evidence rescue
graph invocation
latency
manual failures
```

If the relationship is weak:

```text stop
```

and investigate before building a dedicated graph-benefit model.

---

# 151. Exact Week 17 execution order

Follow this order:

```text 1. inspect final V6 decision

2. freeze V6 artifacts

3. inspect current V3 implementation

4. inspect current V7 graph implementation

5. verify benchmark and split

6. define graph-benefit analysis

7. build per-query retrieval-state dataset

8. run NO_GRAPH baseline

9. run ALL_GRAPH reference

10. compute graph rescue/regression labels offline

11. evaluate simple fixed threshold

12. train / load V3 failure predictor

13. validate calibration if applicable

14. sweep thresholds on validation

15. freeze one policy threshold

16. run SELECTIVE_GRAPH on test

17. lock raw per-question outputs

18. analyze escalation precision/recall

19. analyze rescue/regression cases

20. evaluate answer/citation effect

21. evaluate cost/latency

22. perform target-domain transfer if justified

23. compute paired statistics

24. write failure taxonomy

25. lock results

26. write W17 decision

27. commit code + manifests + analysis
```

Do not reorder the evaluation stages merely because another ordering produces prettier results.

---

# 152. Final mental model

The key evolution is:

```text
V1
Question
  ↓
Which retriever?

V3
Retrieval state
  ↓
Did retrieval probably fail?

V6
Scientific evidence
  ↓
What form does the evidence take?

V7
Evidence graph
  ↓
How are evidence units related?

Week 17
Retrieval state
  +
graph availability
  ↓
Should we pay for graph expansion?
```

This is the core idea:

```text
cheap path by default
        ↓
observe evidence state
        ↓
pay for stronger structure only when justified
```

The objective is not:

```text maximum model complexity
```

It is:

```text maximum useful evidence
per unit of computational cost
```

---

# 153. Final rule for the next AI agent

Start by inspecting the actual V6 decision, V3 implementation, V7 graph implementation, benchmark state, and repository history.

Do not assume graph escalation is justified.

Do not assume V3 failure probability equals graph usefulness.

Do not use test outcomes to select the threshold.

Do not train graph-benefit labels from the predictor's own outputs.

Do not allow unlimited escalation.

Do not give graph retrieval a larger context budget without a matched comparison.

Do not hide graph construction or query-time cost.

Do not silently alter the graph schema or retrieval baseline.

Do not merge V2 verification into the primary gate before the retrieval-only experiment is understood.

Do not report only overall recall.

The correct workflow is:

```text
inspect
↓
freeze
↓
measure no-graph
↓
measure always-graph
↓
define independent graph-benefit outcomes
↓
test simple threshold
↓
evaluate V3 gating
↓
calibrate on validation
↓
freeze policy
↓
test once
↓
analyze rescues/regressions
↓
measure answer/citation impact
↓
measure cost/latency
↓
test transfer
↓
lock evidence
↓
decide honestly
```

That is Week 17.
