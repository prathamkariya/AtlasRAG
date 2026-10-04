# AtlasRAG — Week 12: V3 Retrieval-Failure Prediction & Retrieval-State-Aware Escalation

## 1. Purpose

Week 10 defined retrieval-failure prediction as the next major research direction.

Week 11 focused on evidence verification.

Week 12 defines the next controlled experiment:

> **Can a lightweight model predict when the current retrieval result is likely insufficient, and can that prediction support selective escalation more effectively than question-only routing?**

This extends AtlasRAG from:

```text
Question
   ↓
Route
   ↓
Retrieve
   ↓
Answer
```

toward:

```text
Question
   ↓
Initial Route
   ↓
Retrieve
   ↓
Observe Retrieval State
   ↓
Predict Failure
   ├─ likely sufficient → answer
   └─ likely failure → escalate
                          ↓
                    stronger retrieval
                          ↓
                       answer
```

The important idea is:

```text
pre-retrieval prediction
+
post-retrieval observation
```

rather than asking one router to solve every uncertainty before evidence is available.

---

# 2. Why V3 follows V1/V2

The earlier AtlasRAG work established several distinctions.

V1 routing asks:

```text
Which retrieval strategy should this question use?
```

V2 evidence verification asks:

```text
Does the retrieved/cited evidence support the final claims?
```

V3 asks:

```text
Did the chosen retrieval path probably fail before we trust the answer?
```

These are different decisions.

The intended chain becomes:

```text
Question
   ↓
Pre-retrieval routing
   ↓
Initial retrieval
   ↓
Retrieval-state assessment
   ↓
Failure prediction
   ↓
Optional escalation
   ↓
Final evidence
   ↓
Answer
   ↓
Optional evidence/citation verification
```

Do not collapse these stages into one opaque model.

---

# 3. V3 research question

Primary question:

> **Can retrieval-state-aware failure prediction recover cases missed by question-only routing while adding less cost than always using the strongest retrieval strategy?**

Secondary questions:

```text
1. Which observable retrieval signals predict failure?

2. Are dense/BM25 disagreement signals useful?

3. Do reranker score distributions reveal evidence insufficiency?

4. Can a simple classifier outperform a fixed confidence threshold?

5. Does selective escalation improve the quality/cost frontier?

6. Does the benefit concentrate in difficult scientific evidence structures?
```

These are hypotheses.

Do not present them as established facts.

---

# 4. Critical distinction: router vs failure detector

Current router:

```text
Input:
    question
```

Decision:

```text
strategy
```

V3 failure detector:

```text
Input:
    question
    +
retrieval-state features
```

Decision:

```text
retrieval likely sufficient?
```

Potential architecture:

```text
              Question
                  |
                  v
           Compass / router
                  |
                  v
          Initial retrieval
                  |
                  v
       Retrieval-state features
                  |
                  v
         Failure-prediction model
             /                       /                    sufficient       failure
          |                |
          v                v
        answer          escalate
                             |
                             v
                       strong retrieval
                             |
                             v
                          answer
```

The two models should be evaluated independently.

---

# 5. V3 baseline hierarchy

The experiment should include progressively stronger controls.

### Baseline A — always strong

```text
Question
  ↓
strong retrieval
  ↓
answer
```

This is the quality reference.

### Baseline B — question-only router

```text
Question
  ↓
Compass / fixed router
  ↓
selected retrieval
  ↓
answer
```

### Baseline C — fixed post-retrieval threshold

```text
Question
  ↓
initial retrieval
  ↓
simple score threshold
  ↓
answer or escalation
```

### V3 — learned failure detector

```text
Question
  ↓
initial route
  ↓
retrieval
  ↓
learned failure detector
  ↓
answer or escalation
```

This allows the project to ask whether learned failure prediction adds value beyond a simple threshold.

---

# 6. Independent variable

The clean independent variable is:

```text failure-detection policy
```

Everything else should remain frozen where possible:

```text benchmark
corpus
retrieval stack
initial routing
answer model
answer prompt
generation settings
```

The key comparison is:

```text no post-retrieval escalation
vs
fixed-threshold escalation
vs
learned failure-prediction escalation
```

---

# 7. Ground-truth label

The target must be independent of model confidence.

Possible label:

```text retrieval_sufficient
retrieval_insufficient
```

Ground truth should be based on the evaluation definition used by the project.

For the existing benchmark, one candidate definition is:

```text sufficient
=
retrieved evidence contains all required gold evidence
```

But remember:

```text exact gold-chunk recall
```

is conservative.

A more mature target may distinguish:

```text exact gold recovery
```

from:

```text evidence sufficiency / answerability
```

Do not change the target definition silently.

---

# 8. No circular labels

Bad:

```text model confidence = 0.2
      ↓
label = failure
```

Correct:

```text observed retrieval
      ↓
independent evaluation
      ↓
retrieval_sufficient / retrieval_insufficient
```

The model predicts the label.

It does not create the label.

---

# 9. Potential input features

Candidate retrieval-state features:

```text top reranker score
top-1 / top-2 score gap
mean top-k reranker score
score variance
score range
dense rank of best candidate
BM25 rank of best candidate
dense/BM25 overlap
dense/BM25 disagreement
number of unique papers
number of unique sections
evidence redundancy
query/evidence similarity
top-k lexical overlap
scientific-anchor overlap
```

Do not include all features immediately.

Start with a small interpretable set.

---

# 10. Feature availability rule

Every feature must satisfy:

```text available at inference time
```

It must not depend on:

```text gold chunk
gold answer
Oracle label
human evaluation
test-set outcome
```

A feature that requires knowing:

```text whether the retrieved chunk is gold
```

is invalid for deployment-time failure prediction.

---

# 11. Dense/BM25 agreement

One potentially useful feature is retrieval agreement.

Example:

```text dense:
paper A, paper B, paper C

BM25:
paper A, paper D, paper E
```

There is partial agreement.

Another:

```text dense:
paper A, paper B

BM25:
paper X, paper Y
```

There is strong disagreement.

This may signal:

```text lexical/semantic mismatch
ambiguous terminology
multiple candidate evidence regions
```

But this is only a hypothesis.

Measure the relationship with actual failure labels.

---

# 12. Score-gap feature

A simple confidence signal:

```text top1_score - top2_score
```

Potential interpretation:

```text large gap
    →
one clearly dominant candidate

small gap
    →
retrieval uncertainty
```

This can be tested before using a learned model.

Do not assume a larger score gap always means better evidence.

---

# 13. Score-distribution features

Instead of only top-1:

```text [0.92, 0.91, 0.89, 0.42, 0.40]
```

versus:

```text [0.92, 0.70, 0.43, 0.20, 0.10]
```

These rankings have different shapes.

Potential features:

```text mean
variance
top-k mean
top-k range
entropy-like concentration
```

Use only features with a clear interpretation and stable implementation.

---

# 14. Number of unique papers

Potential signal:

```text number of unique papers among top-k
```

For some questions:

```text one paper
```

may be appropriate.

For a genuine multi-hop question:

```text multiple papers
```

may be expected.

But:

```text more papers
```

does not automatically mean:

```text better evidence.
```

Use this as a feature, not as a rule.

---

# 15. Evidence redundancy

If the top retrieved chunks all say roughly the same thing:

```text chunk A → same claim
chunk B → same claim
chunk C → same claim
```

then retrieval may lack breadth.

For a multi-source question this can be a warning sign.

Potential measure:

```text semantic similarity among top chunks
```

Again:

```text redundancy ≠ failure
```

because redundancy can also increase confidence.

Measure first.

---

# 16. Scientific-anchor overlap

The benchmark generation work already uses scientific signals such as:

```text acronym
parameter
model symbol
observable identifier
```

These can potentially become inference-time features.

For example:

```text query:
Neff constraint from CMB

retrieved evidence:
contains Neff
contains CMB
```

versus:

```text retrieved evidence:
contains only generic cosmology terminology
```

The feature can estimate:

```text query/evidence anchor coverage
```

without exposing gold evidence.

---

# 17. Query/evidence similarity

Potential features:

```text top dense similarity
mean dense similarity
reranker score
```

These are cheap to calculate.

However:

```text high similarity
```

does not guarantee:

```text answerability
```

Scientific terminology can be similar while the exact requested quantity is missing.

This should be explicitly tested.

---

# 18. Retrieval-state feature groups

Organize features into:

```text semantic
    dense similarities

lexical
    BM25 features

ranking
    reranker scores/gaps

diversity
    paper/section counts

agreement
    dense vs BM25 overlap

scientific
    anchor coverage
```

This makes feature ablations easier.

---

# 19. Feature ablation plan

Do not train one large model and stop.

Use:

```text F0
score threshold only

F1
semantic features

F2
lexical features

F3
ranking features

F4
agreement/diversity features

F5
all features
```

The exact grouping can change based on the repository.

The objective is to identify:

```text which information actually matters
```

---

# 20. Model progression

Start with:

```text logistic regression
```

Then:

```text decision tree
```

Then:

```text small gradient-boosted model
```

Only later consider:

```text MLP
transformer
```

The preferred model is the smallest model that produces useful operational improvement.

---

# 21. Why logistic regression is a good first baseline

Advantages:

```text simple
fast
interpretable
well suited to small datasets
easy to calibrate
```

It also gives:

```text feature coefficients
```

which can reveal whether signals behave as expected.

For a student research project, interpretability is valuable.

---

# 22. Tree-based model

A small tree model can capture interactions such as:

```text low top score
+
high dense/BM25 disagreement
```

or:

```text low score gap
+
high redundancy
```

without requiring a neural architecture.

This is a useful second baseline.

---

# 23. Data split

Do not randomly split claims from the same paper if that creates leakage.

Prefer:

```text paper-disjoint split
```

when enough data exists.

Potential split:

```text train papers
validation papers
test papers
```

This forces the failure detector to generalize across unseen documents.

---

# 24. Small-data warning

The existing V1 benchmark is:

```text 27 accepted questions
```

and:

```text 9 retrieval-insufficient
```

This is too small for ambitious feature-heavy models.

Therefore V3 may initially be:

```text exploratory
```

unless the benchmark has been expanded or additional independently generated examples are available.

Do not train a complex predictor on 27 examples merely because the code runs.

---

# 25. If the benchmark is too small

There are three choices:

```text OPTION A
run a pilot only

OPTION B
construct a separate larger retrieval-state dataset

OPTION C
defer model training and analyze feature/label relationships
```

Do not inflate the benchmark by lowering quality standards.

---

# 26. Retrieval-state dataset

A future dataset can be generated from many question/retrieval pairs.

A record might contain:

```text question_id
question
route
retrieval_config
retrieved_chunk_ids
feature_vector
ground_truth_sufficiency
```

The critical distinction is:

```text features
```

are computed from actual retrieval.

```text ground_truth
```

is computed independently.

---

# 27. Synthetic negative examples

Potential data augmentation:

```text retrieve with deliberately weaker strategy
```

can produce more:

```text retrieval-insufficient
```

cases.

However, these examples are not automatically equivalent to natural failures.

Keep track of:

```text naturally occurring failure
vs
synthetic degradation
```

If synthetic negatives are used, test separately.

---

# 28. Avoid artificial ease

Do not generate negatives that are trivially broken.

For example:

```text random chunks from unrelated papers
```

would make classification unrealistically easy.

Better hard negatives:

```text semantically similar but missing requested quantity
same topic, wrong parameter
same model family, wrong result
correct paper, wrong section
```

These better resemble real retrieval failures.

---

# 29. Hard-negative generation

Potential approach:

```text question
   ↓
retrieve top candidates
   ↓
identify semantically close non-supporting candidates
   ↓
label using independent evidence definition
```

Do not label a hard negative merely because:

```text it is not the gold chunk.
```

Another passage may legitimately support the answer.

---

# 30. Target definition maturity

There are two possible targets.

### Target A — exact gold recovery

```text all gold chunks retrieved?
```

Pros:

```text objective
easy to compute
consistent with current Oracle
```

Cons:

```text conservative
penalizes alternative evidence
```

### Target B — evidence sufficiency

```text retrieved context sufficient to answer?
```

Pros:

```text closer to practical behavior
```

Cons:

```text harder to annotate reliably
```

Do not replace Target A with Target B silently.

A future experiment can compare both.

---

# 31. V3 metrics

Classification metrics:

```text accuracy
precision
recall
F1
AUROC
AUPRC
```

For imbalanced failure labels, pay attention to:

```text recall of retrieval failures
AUPRC
```

rather than accuracy alone.

---

# 32. Calibration

The model's output should ideally be:

```text calibrated failure probability
```

Measure:

```text reliability curve
ECE
Brier score
```

A useful detector should behave approximately like:

```text predicted 0.8
→ about 80% failure rate
```

over an appropriate evaluation population.

Do not call an uncalibrated score:

```text probability
```

in the report.

---

# 33. Operational metrics

Classification quality is not enough.

Measure:

```text escalation rate
false-negative rate
false-positive rate
strong-retrieval calls avoided
additional provider calls
total latency
total tokens
answer quality after escalation
```

These metrics connect prediction to the real system.

---

# 34. False-negative cost

Important case:

```text actual failure
+
detector predicts sufficient
```

The system proceeds to answer with inadequate evidence.

This is dangerous.

Therefore:

```text false-negative rate
```

may deserve a stricter threshold than ordinary classifier accuracy.

---

# 35. False-positive cost

Opposite:

```text actual sufficient
+
detector predicts failure
```

The system escalates unnecessarily.

This costs:

```text latency
tokens
provider calls
possibly money
```

The optimal threshold balances:

```text under-routing
vs
over-escalation.
```

---

# 36. Threshold sweep

Do not choose:

```text threshold = 0.5
```

arbitrarily.

Evaluate a grid such as:

```text 0.10
0.20
0.30
...
0.90
```

on validation data.

For each threshold calculate:

```text coverage
failure risk
escalation rate
cost
latency
```

Then select a threshold according to the predeclared decision rule.

---

# 37. Selective-risk curve

A powerful plot is:

```text Risk
 ^
 |
 | |  |   |    |    \____
 +-----------------> Coverage
```

where:

```text coverage =
queries answered without escalation
```

and:

```text risk =
error/failure rate among those not escalated
```

The desired policy moves along:

```text high coverage
+
acceptable risk
```

This is more informative than a single threshold number.

---

# 38. Quality/cost frontier

Also plot:

```text quality
 ^
 |
 |             strong baseline
 |       V3
 |   router
 |
 +--------------------> cost
```

Actual values must come from experiments.

The point is to show whether V3 creates a better frontier.

---

# 39. Expected-loss formulation

Conceptually:

```text expected loss
=
P(failure if not escalated) × failure cost
+
P(escalate) × escalation cost
```

A policy can choose escalation when:

```text expected failure cost > escalation cost
```

The exact model should be defined using measured quantities.

Do not assume a theoretical threshold is optimal without empirical calibration.

---

# 40. Escalation target

The escalation path should be clearly defined.

For example:

```text initial route
→ standard hybrid retrieval

escalation
→ stronger candidate depth
or
→ stronger routing strategy
or
→ additional decomposition
```

Do not combine multiple escalation changes in one experiment if you want a clean causal result.

---

# 41. First V3 escalation experiment

Keep escalation minimal.

Recommended concept:

```text normal retrieval
      ↓
failure detector
      ↓
if likely failure:
    run stronger retrieval
```

Do not simultaneously add:

```text query rewriting
+
new embedding
+
new reranker
+
new answer model
```

That would make the source of improvement unclear.

---

# 42. Candidate escalation strategies

Potential escalation options:

```text larger dense/BM25 candidate depth
stronger final-k
stronger reranker
multi-hop decomposition
LLM retrieval retry
```

Choose one.

The best choice should come from the actual V1/V2 failure analysis.

---

# 43. Escalation should preserve provenance

If a query is escalated, retain:

```text initial route
initial retrieval
failure score
escalation reason
second retrieval
final evidence
```

This makes post-hoc analysis possible.

---

# 44. Two-stage retrieval record

Conceptually:

```json
{
  "question_id":"...",
  "initial_strategy":"SIMPLE",
  "failure_probability":0.82,
  "escalated":true,
  "escalation_strategy":"MULTI_HOP",
  "initial_retrieval":[],
  "final_retrieval":[],
  "outcome":"..."
}
```

Use the repository's real schema.

---

# 45. Measuring escalation benefit

For escalated queries compare:

```text initial retrieval
vs
escalated retrieval
```

Metrics:

```text evidence recall change
answer correctness change
groundedness change
citation change
latency increase
token increase
provider calls
```

A successful escalation should show:

```text quality gain
```

that justifies:

```text extra cost.
```

---

# 46. Counterfactual oracle analysis

The empirical Oracle can help ask:

```text detector escalated?
```

versus:

```text what strategy did Oracle-v2 choose?
```

This is diagnostic.

For example:

```text detector escalates
Oracle says SIMPLE
```

may indicate:

```text unnecessary escalation
```

while:

```text detector does not escalate
Oracle says stronger strategy
```

may indicate:

```text missed failure
```

Do not treat Oracle agreement as the same thing as system correctness.

---

# 47. Per-question regret

Store:

```text chosen initial strategy
oracle strategy
initial recall
oracle recall
escalated?
final recall
cost
latency
```

Then inspect:

```text cost of under-routing
cost of over-routing
benefit of successful escalation
```

This turns the detector into an interpretable policy-analysis tool.

---

# 48. V3 route states

A useful state machine:

```text INITIAL
   |
   v
RETRIEVED
   |
   v
ASSESS
  /  /   OK   FAIL
 |     |
 v     v
ANSWER ESCALATE
          |
          v
       RETRIEVE2
          |
          v
        ASSESS
```

Keep the maximum escalation count bounded.

Do not create recursive retrieval loops.

---

# 49. Failure-loop prevention

Set:

```text max_escalations = 1
```

for the first experiment.

Otherwise the system can create:

```text retrieve
→ fail
→ retrieve
→ fail
→ retrieve
→ ...
```

which makes cost and debugging difficult.

A bounded controller is easier to analyze.

---

# 50. Provider and infrastructure failures

Separate:

```text detector predicts failure
```

from:

```text provider failed
```

For example:

```text retrieval succeeded
answer API timed out
```

is not evidence that:

```text retrieval detector failed.
```

Likewise:

```text verifier unavailable
```

is not:

```text retrieval insufficient.
```

Maintain explicit infrastructure statuses.

---

# 51. V3 answer evaluation

The retrieval-state detector must eventually be judged at the user-facing level.

At minimum:

```text answer correctness
groundedness
citation quality
latency
tokens
provider calls
```

Otherwise the project may improve retrieval recall without improving the actual answer.

---

# 52. Retrieval-only first

However, do not jump straight to expensive answer evaluation.

First validate:

```text detector classification
+
retrieval recall
+
escalation behavior
```

Then perform end-to-end answer evaluation.

This preserves the project's staged evaluation discipline.

---

# 53. Feature importance

For interpretable models, inspect:

```text logistic coefficients
tree feature importance
permutation importance
SHAP only if justified
```

The goal is to understand:

```text what predicts failure?
```

not merely:

```text what gives the best score?
```

Start with simpler methods.

---

# 54. Feature sanity checks

Before trusting a feature, test:

```text missing values
scale
outliers
distribution by label
correlation
availability
```

Example:

```text top reranker score
```

may have different scale across question types.

Normalize only if justified.

Do not preprocess using information from the test set.

---

# 55. Question-type stratification

Analyze failure prediction by:

```text SIMPLE
MULTI_HOP
CONFLICTING
TEMPORAL
CHAIN
```

where enough data exists.

The current benchmark has sparse difficult classes.

Therefore subgroup results should always include:

```text n
```

and should be treated as exploratory when small.

---

# 56. Strongest expected V3 result

A strong result would look like:

```text Question-only routing
    ↓
some failures remain

Post-retrieval detector
    ↓
identifies a subset of those failures

Selective escalation
    ↓
recovers evidence

Total strong-retrieval usage
    ↓
lower than always-strong baseline

Final answer quality
    ↓
maintained or improved
```

That would be a coherent scientific result.

---

# 57. Negative result

A useful negative result:

```text detector predicts failures accurately
but almost every failure requires escalation
```

Then:

```text prediction useful
policy value weak
```

Another:

```text detector has good classifier metrics
but fails to improve answer quality
```

Then:

```text retrieval-state prediction may not be the current bottleneck
```

Both are informative.

---

# 58. V3 stop conditions

Stop the first V3 iteration when:

```text feature schema stable
label definition frozen
baseline measured
simple detector evaluated
threshold policy evaluated
one escalation path evaluated
operational cost measured
failure analysis completed
decision recorded
```

Do not keep adding features merely to improve AUROC by a small amount.

---

# 59. V3 decision rule

Possible predeclared rule:

> Select the simplest failure detector that reduces retrieval failure on the validation benchmark while keeping escalation cost below the predefined budget.

Or:

> Select the policy that provides the strongest quality/cost frontier under the predefined answer-quality constraint.

Write the final rule before test evaluation.

---

# 60. V3 experiment matrix

A clean matrix:

| System | Initial Route | Failure Detection | Escalation | Purpose |
|---|---|---|---|---|
| A | fixed | none | none | cheap reference |
| B | fixed | none | always strong | strong reference |
| C | question-only | none | none | routing baseline |
| D | question-only | fixed threshold | strong retrieval | simple post-retrieval control |
| E | question-only | learned detector | strong retrieval | V3 |
| F | question-only | learned detector + calibrated threshold | strong retrieval | final V3 policy |

Only use systems actually implemented.

---

# 61. V3 benchmark artifacts

Keep:

```text
V1 benchmark
V2 verification dataset
V3 retrieval-state dataset
```

separate.

Do not turn verification labels into failure-prediction labels without checking that the target remains correct.

A single underlying question may participate in multiple evaluation tasks, but each task needs its own target definition.

---

# 62. V3 result artifacts

Possible structure:

```text
results/
    v3_failure_prediction/
        feature_data.jsonl
        baseline.jsonl
        detector_logreg.jsonl
        detector_tree.jsonl
        threshold_sweep.json
        escalation_runs.jsonl
        summary.json
        manifest.json
        failure_analysis.json
```

Follow the repository's actual structure.

---

# 63. V3 reproducibility manifest

Record:

```text
experiment_id
benchmark_version
corpus_version
retrieval_config
initial_router
feature_schema
feature version
target definition
model
hyperparameters
threshold
escalation strategy
answer model
answer prompt
seed
cache namespace
git commit
timestamp
```

This should be generated, not manually reconstructed later.

---

# 64. Tests before V3 pilot

Cover behavior equivalent to:

```text feature extraction is deterministic

feature vector has expected fields

missing retrieval score handled

dense/BM25 overlap computed correctly

paper diversity computed correctly

target labels independent of confidence

threshold selection bounded

one escalation maximum

provider failure remains distinct

gold evidence not exposed as feature

second retrieval preserves provenance
```

These tests are especially important because feature leakage can silently invalidate the experiment.

---

# 65. Leakage audit

Before training, inspect every feature.

Ask:

```text Could this feature be computed for a brand-new user query?

Does it require benchmark metadata?

Does it use gold chunk IDs?

Does it use the answer?

Does it use human evaluation?

Does it use the Oracle label?
```

If yes:

```text remove or redesign the feature.
```

This audit should be saved with the experiment manifest.

---

# 66. Data leakage through preprocessing

Do not compute:

```text global normalization
feature selection
thresholds
imputation statistics
```

using the entire dataset.

Fit preprocessing on:

```text training
```

then apply to:

```text validation/test.
```

For simple models, keep preprocessing minimal to reduce this risk.

---

# 67. Calibration split

If threshold selection and calibration are needed:

```text train
→ fit detector

validation
→ calibrate + select threshold

test
→ final evaluation
```

Do not select the threshold using the test set.

---

# 68. Strongest baseline fairness

If comparing against:

```text always strong
```

make sure:

```text same corpus
same benchmark
same retrieval implementation
same final answer settings
```

are used.

Otherwise cost/quality comparisons can be misleading.

---

# 69. Measuring strong-retrieval usage

The operational result should report:

```text fraction escalated
fraction handled by cheap path
fraction handled by strong path
```

For example:

```text cheap path: 72%
strong path: 28%
```

Do not use such numbers unless measured.

This is central to demonstrating adaptive behavior.

---

# 70. Cost per query

Report:

```text average total cost/query
```

and preferably:

```text median
p95
```

when cost distribution is skewed.

Break out:

```text initial routing
initial retrieval
escalation
answer generation
verification
```

where measurements permit.

---

# 71. Latency distribution

Do not report only one average.

Use:

```text p50
p95
```

at minimum where infrastructure supports it.

Selective escalation may leave:

```text p50
```

near the cheap path while increasing:

```text p95
```

because difficult cases take longer.

That itself is important.

---

# 72. Tail latency tradeoff

A policy can improve average cost but hurt tail latency.

Therefore inspect:

```text p50 latency
p95 latency
escalation frequency
```

together.

For an interactive scientific QA system, both matter.

---

# 73. Stability rerun

The project already emphasizes stability.

A major V3 result should eventually have:

```text run A
run B
```

with appropriate cache separation.

Compare:

```text detector metrics
threshold behavior
escalation rate
quality
cost
```

Do not trust a single provider run if the system is stochastic.

---

# 74. Provider-rate-limit effects

Because earlier AtlasRAG generation work encountered provider 429s:

```text V3 instrumentation must separate
real detector behavior
from
provider availability.
```

If a run is incomplete:

```text mark incomplete
```

Do not fill missing rows with assumptions.

---

# 75. What to do if V3 is impossible with current data

Do not force model training.

Instead produce:

```text feature/label analysis
+
pilot detector
+
proof-of-concept escalation
```

and document:

```text dataset too small for final learned-model conclusion
```

This is scientifically preferable to overfitting.

---

# 76. Relation to Compass

V3 does not replace Compass.

The long-term model can be:

```text Compass
=
pre-retrieval strategy prediction
```

while:

```text V3 detector
=
post-retrieval adequacy prediction
```

Together:

```text Compass
   ↓
initial retrieval
   ↓
V3 detector
   ↓
optional escalation
```

This makes the system more robust to:

```text unpredictable retrieval failures.
```

---

# 77. Relation to V2 verification

V2 checks:

```text claim → citation → evidence
```

V3 checks:

```text retrieval state → likely adequacy
```

A future full system can combine them:

```text retrieve
   ↓
V3 adequacy prediction
   ↓
escalate if needed
   ↓
answer
   ↓
V2 citation/evidence verification
```

This gives:

```text pre-answer control
+
post-answer verification.
```

---

# 78. Future closed-loop system

Conceptually:

```text                     Question
                         /                                /                                 v            v
                Pre-route       Metadata
                       \          /
                        \        /
                         v      v
                       Retrieval
                           |
                           v
                  Failure Predictor
                    /                              /                           sufficient       failure
                  |                |
                  |             escalate
                  |                |
                  |          stronger retrieval
                  |                |
                  +-------+--------+
                          |
                          v
                       Answer
                          |
                          v
                 Claim verification
                          |
                          v
                    Final response
```

This is future architecture, not current implementation.

---

# 79. Potential long-term research contribution

If V3 works, the project may be able to study:

> **Whether retrieval-state-aware control can complement question-only adaptive routing by detecting failures that are intrinsically difficult to predict before retrieval.**

This is a more precise research contribution than saying:

```text better RAG router
```

It connects:

```text routing
+
retrieval observability
+
selective escalation
```

---

# 80. Do not claim universal optimality

Even a strong V3 result would be:

```text empirical
benchmark-specific
retrieval-stack-specific
model-specific
cost-regime-specific
```

Do not claim:

```text universal failure detector
```

or:

```text optimal adaptive controller
```

unless much broader evidence supports it.

---

# 81. Future cross-domain test

After V3 stabilizes, a meaningful extension is:

```text train on astrophysics/cosmology
test on another scientific domain
```

Question:

> Are retrieval-state failure signals domain-general?

This should be a new experiment.

Do not mix it into the first V3 evaluation.

---

# 82. Research-paper framing

Potential V3 section:

```text Retrieval-State-Aware Selective Escalation
```

Subsections:

```text feature design
failure labels
classifier
calibration
policy
cost-quality tradeoff
failure analysis
```

This can become a strong experimental chapter if the data supports it.

---

# 83. Final V3 result table

Use:

| Policy | Failure Detection Recall | Escalation Rate | Evidence Recall | Answer Correctness | Groundedness | p50 Latency | p95 Latency | Tokens/Query |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Always Cheap | | | | | | | | |
| Always Strong | | | | | | | | |
| Question Router | | | | | | | | |
| Fixed Threshold | | | | | | | | |
| Learned Detector | | | | | | | | |

Populate only from real experiments.

---

# 84. Final V3 failure table

Use:

| Failure | Count | Detection | Escalation | Outcome | Root Cause |
|---|---:|---|---|---|---|
| Missed retrieval failure | | | | | |
| Unnecessary escalation | | | | | |
| Successful escalation | | | | | |
| Failed escalation | | | | | |
| Provider failure | | | | | |

This directly connects classifier behavior to system outcomes.

---

# 85. V3 completion checklist

```text
[ ] V1 state frozen
[ ] target definition written
[ ] feature schema written
[ ] leakage audit completed
[ ] retrieval-state dataset created
[ ] paper-disjoint split considered/implemented
[ ] simple baseline evaluated
[ ] learned detector evaluated if data supports it
[ ] calibration measured
[ ] threshold sweep completed
[ ] escalation path implemented
[ ] max escalation bounded
[ ] operational cost measured
[ ] latency measured
[ ] answer-level evaluation measured
[ ] failure cases inspected
[ ] stability rerun completed if practical
[ ] manifest saved
[ ] V3 decision recorded
```

---

# 86. V3 decision outcomes

Choose one:

```text KEEP
```

The detector materially improves quality/cost tradeoffs.

```text REJECT
```

The detector predicts failures but does not improve the system enough to justify its complexity.

```text DEFER
```

The idea is promising but the current data is too small or noisy.

Again:

```text REJECT
```

is a valid scientific result.

---

# 87. Week 12 execution order

Follow:

```text
STEP 1
Inspect final V1/V2 repository state.

STEP 2
Confirm the exact retrieval implementation.

STEP 3
Define retrieval_sufficient / retrieval_insufficient precisely.

STEP 4
List inference-time features.

STEP 5
Perform a leakage audit.

STEP 6
Instrument feature extraction.

STEP 7
Build a small retrieval-state dataset.

STEP 8
Inspect class balance and paper distribution.

STEP 9
Implement a fixed threshold baseline.

STEP 10
Evaluate threshold behavior.

STEP 11
Implement logistic regression.

STEP 12
Evaluate learned failure prediction.

STEP 13
Calibrate if justified.

STEP 14
Add one bounded escalation path.

STEP 15
Run retrieval-only evaluation.

STEP 16
Run answer-level evaluation if retrieval results justify it.

STEP 17
Analyze cost, latency, false positives, and false negatives.

STEP 18
Run a stability rerun if provider budget allows.

STEP 19
Write the V3 decision.

STEP 20
Commit and preserve all artifacts.

STEP 21
Update the project context.
```

---

# 88. Commands to begin Week 12

Start:

```powershell
$env:PYTHONPATH="src"
```

Check state:

```powershell
git status
git log --oneline --decorate -15
```

Run tests:

```powershell
python -m pytest -q
```

Inspect retrieval:

```powershell
Get-ChildItem .\srctlasragetrieval -Recurse -File | Select-Object FullName
```

Inspect routing:

```powershell
Get-ChildItem .\srctlasragouters -Recurse -File | Select-Object FullName
```

Inspect benchmark/evaluation:

```powershell
Get-ChildItem .\srctlasragench -Recurse -File | Select-Object FullName
```

Search for retrieval scores:

```powershell
Get-ChildItem .\srctlasrag -Recurse -File | Select-String "score|rerank|dense|bm25|rrf|similarity"
```

Search for existing provenance:

```powershell
Get-ChildItem .\srctlasrag -Recurse -File | Select-String "paper_id|chunk_id|section|source"
```

Inspect experiment scripts:

```powershell
Get-ChildItem .\scripts -File | Select-Object Name
```

Do not implement the classifier until the actual retrieval result structure is understood.

---

# 89. Final Week 12 principle

> **Do not ask the router to predict what the system can observe only after retrieval.**

V1's central challenge is:

```text predict retrieval needs before evidence exists.
```

V3 adds:

```text observe retrieval
        ↓
estimate adequacy
        ↓
escalate only when necessary
```

That creates a much cleaner control problem.

The long-term AtlasRAG architecture can therefore become:

```text
Question
   ↓
Pre-retrieval routing
   ↓
Initial retrieval
   ↓
Retrieval-state assessment
   ↓
Selective escalation
   ↓
Final evidence
   ↓
Answer
   ↓
Claim/citation verification
```

The project should reach that architecture only through measured experiments.

The next generation is not valuable because it has more stages.

It is valuable if each stage removes a specific, measured failure mode while preserving a defensible quality/cost tradeoff.
