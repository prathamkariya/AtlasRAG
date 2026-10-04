# AtlasRAG — Week 5: Dynamic Routing, Selective Escalation & Efficiency
## Context handoff / execution manual

> **Purpose:** This document defines the phase after the raw Compass router has been trained and evaluated. The focus is no longer only “which route should Compass choose?” but **when should AtlasRAG trust Compass, when should it escalate to an expensive LLM router, and what retrieval-quality / cost tradeoff results from doing so?**
>
> **Status rule:** This is a phase plan and research handoff. Components described as future work must not be reported as implemented until verified in the repository and measured experimentally.

---

# 1. Week 5 in one page

Week 4 establishes a raw learned router:

```text
question
   ↓
Compass
   ↓
SIMPLE / MULTI_HOP / UNCERTAIN
```

Week 5 turns that classifier into an adaptive control policy:

```text
question
   ↓
Compass
   ↓
confidence
   |
   +--------------------+
   |                    |
 high confidence     low confidence
   |                    |
   v                    v
trust Compass        expensive fallback
   |                    |
   +----------+---------+
              |
              v
      selected retrieval
              |
              v
       evidence retrieval
              |
              v
         answer system
```

The main research question becomes:

> **Can a cheap learned router handle most queries locally while selectively escalating uncertain cases to a stronger LLM router, reducing routing cost without an unacceptable loss in evidence quality?**

This phase is about:

```text selective computation
confidence
fallback
cost/quality tradeoffs
```

not about introducing more model complexity for its own sake.

---

# 2. Where Week 5 fits

The research sequence is now:

```text
Week 1
Foundation
    ↓
Week 2
Benchmark construction / audit / Oracle-v2
    ↓
Week 3
C2 Oracle-aligned LLM routing
    ↓
Week 4
Compass learned routing
    ↓
Week 5
Dynamic routing / selective escalation
    ↓
Week 6
Retrieval ablations
    ↓
Week 7+
Answer-generation evaluation / final system analysis
```

The important distinction is:

```text Week 4:
    Is Compass useful?

Week 5:
    How should Compass be used in a real adaptive pipeline?
```

That separation matters because otherwise model quality and policy design become impossible to disentangle.

---

# 3. Starting point for Week 5

Week 5 assumes that Week 4 has produced:

```text trained Compass checkpoint
+
working CompassRouter
+
held-out predictions
+
route confidence
+
retrieval-only evaluation
```

At minimum, the project should know:

```text Compass evidence recall
Compass route agreement
Compass routing latency
Compass confidence distribution
```

Ideally it also has:

```text C1 LLM-router metrics
C2 LLM-router metrics
E2 Oracle metrics
B static metrics
```

All of these should come from saved experiment outputs rather than manually remembered numbers.

---

# 4. The central problem: confidence is not automatically useful

Compass may return:

```text route = SIMPLE
confidence = 0.94
```

but this does not automatically mean:

```text 94% probability that SIMPLE is correct
```

A softmax score is not automatically calibrated.

Therefore Week 5 must separate:

```text model confidence
```

from:

```text empirical reliability
```

The first task is not to pick a threshold.

The first task is to measure whether confidence carries useful information.

---

# 5. Confidence analysis

For each Compass prediction save:

```text question_id
predicted_route
confidence
gold_route_v2
oracle_sufficient
evidence_recall
```

Then construct confidence buckets such as:

```text 0.0–0.2
0.2–0.4
0.4–0.6
0.6–0.8
0.8–1.0
```

For every bucket measure:

```text route agreement
evidence recall
sufficient-retrieval rate
fallback candidate rate
```

The point is to discover whether:

```text higher confidence
```

correlates with:

```text safer routing
```

rather than assuming it.

---

# 6. Calibration

If Compass confidence is poorly calibrated, threshold-based escalation may behave badly.

A later calibration step may use:

```text temperature scaling
```

or another validation-set calibration method.

The critical rule:

```text calibration parameters
```

must be learned using:

```text validation data
```

not the final test set.

The sequence should be:

```text train
   ↓
validation calibration
   ↓
freeze calibrated model
   ↓
test
```

Do not repeatedly tune a threshold against test performance.

---

# 7. Why selective escalation matters

An always-LLM router has a simple advantage:

```text every query gets expensive reasoning
```

but it also incurs:

```text LLM calls
tokens
latency
provider dependency
rate-limit exposure
```

Compass provides the opposite:

```text cheap local routing
```

but may make mistakes.

The natural combination is:

```text cheap-first
+
expensive fallback
```

The goal is not “never call the LLM”.

The goal is:

```text call the LLM when the cheap model is least trustworthy
```

---

# 8. Existing project concept: EscalatingRouter

The project already contains infrastructure for an `EscalatingRouter`.

Conceptually:

```text Compass
    |
    | confidence >= threshold
    v
 use Compass route

confidence < threshold
    |
    v
 call LLM router
    |
    v
 use stronger route
```

This is useful because the expensive model becomes:

```text fallback
```

rather than:

```text default
```

The exact current implementation must be inspected before modifying it.

Do not assume the historical interface has remained unchanged.

---

# 9. First dynamic policy

The first Week 5 policy should be deliberately simple:

```text if confidence >= τ:
    trust Compass
else:
    use C2
```

where:

```text τ = confidence threshold
```

This should be the first controlled escalation policy.

Do not begin with:

```text multiple thresholds
+
different fallback models
+
cost-aware scoring
+
retrieval-failure prediction
```

all at once.

The first policy needs one clearly interpretable variable.

---

# 10. Why C2 should be the fallback

C2 was designed as the Oracle-aligned LLM routing ablation.

That makes it a natural fallback:

```text Compass
   ↓
low confidence
   ↓
C2
```

This keeps the architecture logically consistent:

```text cheap learned policy
        +
stronger expensive policy
```

The exact relationship should still be verified using actual C2 results.

If C2 does not outperform C1 or is not operationally useful, the fallback can be revised later.

Do not assume the fallback choice is optimal before measuring it.

---

# 11. First policy should not use evidence context

The core selective router remains:

```text question
   ↓
Compass
```

and, when escalated:

```text question
   ↓
C2
```

The policy must not leak:

```text retrieved evidence
gold evidence
answer context
```

into Compass.

Otherwise the cost-saving comparison no longer represents a pre-retrieval decision system.

---

# 12. Basic escalation algorithm

Conceptually:

```python
def route(query):
    decision=compass.route(query)

    if decision.confidence>=threshold:
        return decision

    return llm_router.route(query)
```

The actual implementation should preserve:

```text route source
confidence
fallback reason
latency
LLM usage
```

For example:

```text source = COMPASS
```

or:

```text source = C2
fallback_reason = LOW_CONFIDENCE
```

This metadata is essential for analysis.

---

# 13. Why provenance matters

A final route such as:

```text MULTI_HOP
```

is not enough to understand the pipeline.

You need to know whether it came from:

```text Compass
```

or:

```text C2 fallback
```

Every dynamic decision should therefore preserve:

```text initial_route
initial_confidence
escalated
final_route
fallback_source
```

This lets the research team answer:

```text How often did Compass defer?

Did fallback fix Compass errors?

How often did fallback change a correct Compass decision?

Did fallback cost more than it saved?
```

---

# 14. Threshold sweep

After the raw policy works, perform a threshold sweep over a predefined grid.

For example:

```text τ ∈ {
    0.50,
    0.55,
    0.60,
    0.65,
    0.70,
    0.75,
    0.80,
    0.85,
    0.90,
    0.95
}
```

The exact grid is a configuration choice.

Do not choose the grid because one value happens to work well.

For each threshold measure:

```text Compass-only rate
Fallback rate
Evidence recall
Route agreement
LLM calls/query
Provider calls/query
Tokens/query
Latency
```

---

# 15. Coverage

A useful metric is:

```text Compass coverage
=
fraction of queries handled without fallback
```

For example:

```text coverage = 0.80
```

would mean:

```text 80% of queries use Compass only
20% escalate
```

This does not automatically mean the system is better.

You must pair coverage with:

```text evidence recall
```

and:

```text cost
```

---

# 16. Fallback rate

The complementary metric is:

```text fallback rate
=
fraction of queries escalated
```

Track this overall and per question type:

```text SIMPLE
MULTI_HOP
TEMPORAL
CHAIN
UNCERTAIN
```

This can reveal whether Compass is selectively cautious in the right places or simply uncertain about everything.

---

# 17. The ideal selective-routing measurement

At each threshold, construct something like:

| Threshold | Compass Coverage | Fallback Rate | Evidence Recall | LLM Calls/Q | Tokens/Q | p50 Latency | p95 Latency |
|---|---:|---:|---:|---:|---:|---:|---:|
| 0.50 | | | | | | | |
| 0.60 | | | | | | | |
| 0.70 | | | | | | | |
| 0.80 | | | | | | | |
| 0.90 | | | | | | | |
| 0.95 | | | | | | | |

Do not populate this table until the actual experiment is run.

---

# 18. Three baseline policies are especially important

The dynamic system should be compared with:

```text 1. Compass-only
```

```text 2. C2-only
```

```text 3. Compass + selective C2 fallback
```

These establish:

```text cheap extreme
expensive extreme
hybrid middle
```

A useful additional reference is:

```text B static
```

and:

```text E2 Oracle
```

---

# 19. Why “hybrid” is a separate experiment

A hybrid system can beat both extremes on operational efficiency without having the highest raw recall.

That is okay.

The relevant question is:

```text What quality/cost tradeoff does selective escalation provide?
```

Do not require the hybrid to dominate every metric.

A well-designed tradeoff curve can be more informative than a single top-line score.

---

# 20. Regret relative to the Oracle

One useful diagnostic is:

```text cost/quality regret
```

relative to the empirical Oracle.

For example, preserve:

```text Oracle route
Compass route
final hybrid route
```

and determine when the system departs from the Oracle.

However, keep this interpretation precise.

Oracle regret here means:

```text difference under the chosen empirical retrieval metric
```

not a claim about real-world optimality.

---

# 21. Harmful under-routing

A particularly important error is:

```text Compass high-confidence
→ selects weak route
→ misses gold evidence
```

Call this:

```text harmful under-routing
```

The exact terminology can differ, but the event must be measurable.

For every such case record:

```text question
Compass confidence
Compass route
Oracle route
retrieval recall
whether C2 would have corrected it
```

This tells you whether escalation could have prevented the failure.

---

# 22. Unnecessary escalation

The opposite error is:

```text Compass low confidence
→ C2 fallback
→ C2 chooses route
→ Compass-only would already have retrieved the needed evidence
```

This is:

```text unnecessary escalation
```

Measure:

```text number
fraction
extra tokens
extra latency
extra provider calls
```

These are the costs of being overly cautious.

---

# 23. Useful four-way outcome analysis

Each query can be classified into four useful categories:

```text A. Confident + correct
B. Confident + wrong
C. Escalated + corrected
D. Escalated + unnecessary
```

This gives a much clearer picture than one fallback percentage.

Conceptually:

```text              Compass
            confident / low-conf
                 /       \
               /           \
          correct          wrong
             |                |
             |              escalate
             |                |
             |         corrected / not corrected
```

The actual categorization must use a declared correctness criterion.

---

# 24. Threshold selection

The threshold must be selected without test-set overfitting.

Correct procedure:

```text training set
    ↓
validation set
    ↓
choose threshold
    ↓
freeze policy
    ↓
final test
```

Possible selection criteria include:

```text maximize recall under token budget
maximize recall subject to latency limit
minimize cost subject to recall floor
```

The chosen objective must be defined before inspecting final test performance when possible.

---

# 25. Cost-constrained routing

A later Week 5 experiment can frame the policy as:

```text maximize evidence recall
subject to:
    expected routing cost <= budget
```

For example:

```text token budget
```

or:

```text LLM calls/query budget
```

The exact budget must be declared.

This is a natural extension of the project's research question because routing is a resource-allocation problem.

---

# 26. Do not invent a utility score first

It is tempting to immediately define:

```text utility = recall - λ*cost
```

But the value of:

```text λ
```

is a modeling assumption.

Unless the application provides a real cost tradeoff, preserve raw metrics first.

Then, if a utility analysis is useful, run several λ values or budgets and show sensitivity.

Do not choose one λ solely because it makes the hybrid look strongest.

---

# 27. Cheap-first routing extension

A more advanced version could use a route ladder:

```text Compass
   ↓
SIMPLE retrieval
   ↓
check retrieval confidence / evidence signals
   ↓
escalate only if needed
```

For example:

```text Compass predicts SIMPLE
        |
        v
simple retrieval
        |
        v
evidence quality check
        |
        +--> sufficient
        |
        +--> insufficient → escalate
```

This is potentially valuable but must be treated as a distinct experiment.

Otherwise two changes are mixed:

```text routing confidence
+
post-retrieval failure detection
```

---

# 28. Important distinction: pre-retrieval vs post-retrieval escalation

Pre-retrieval:

```text question
↓
Compass
↓
C2 if low confidence
↓
retrieval
```

Post-retrieval:

```text question
↓
Compass
↓
retrieval
↓
detect weak evidence
↓
C2 / stronger strategy
```

The second system has more information and may be stronger.

But it answers a different research question.

Week 5 should start with:

```text pre-retrieval selective escalation
```

and introduce post-retrieval escalation only as a separate extension.

---

# 29. Why post-retrieval checks can be interesting later

A retrieval-aware fallback can answer:

```text Did the selected route actually produce enough evidence?
```

That is different from:

```text Did Compass think it was confident?
```

This can expose an important limitation of question-only routing.

For example:

```text high Compass confidence
+
poor retrieval
```

would show that:

```text uncertainty is partly invisible before retrieval
```

That can become an interesting finding rather than merely a failure.

---

# 30. Potential two-stage architecture

Later:

```text                       question
                           |
                           v
                       Compass
                           |
                 +---------+---------+
                 |                   |
             high conf            low conf
                 |                   |
                 v                   v
            select route            C2
                 |                   |
                 +---------+---------+
                           |
                           v
                       retrieval
                           |
                           v
                    evidence check
                           |
                  +--------+--------+
                  |                 |
              sufficient        insufficient
                  |                 |
                  v                 v
              continue         stronger retrieval
```

This is conceptually powerful but should only be built after the first selective-routing experiment is understood.

---

# 31. Confidence-aware route handling

There may also be a difference between confidence in the predicted route and confidence that retrieval will succeed.

These are not the same.

A future extension could produce:

```text route confidence
+
retrieval-failure confidence
```

The original project documentation also discussed a possible separate retrieval-failure predictor, but this is not required for the first Week 5 experiment.

Do not automatically add a second learned head unless the raw Compass results justify it.

---

# 32. Keep Week 5 controlled

The clean progression is:

```text Experiment W5-A
Compass only

Experiment W5-B
Compass + fixed confidence threshold + C2 fallback

Experiment W5-C
Threshold sweep

Experiment W5-D
Optional calibration

Experiment W5-E
Optional post-retrieval escalation

Experiment W5-F
Optional cost-constrained policy
```

Each should change as few variables as possible.

---

# 33. Metrics for every dynamic policy

For every policy record:

```text evidence recall
paper recall
route agreement
Compass coverage
fallback rate
LLM calls/query
provider calls/query
cache hits/query
retry attempts
tokens/query
latency p50
latency p95
```

And ideally:

```text harmful under-routing
unnecessary escalation
fallback correction rate
```

These should be computed from saved per-question outputs.

---

# 34. Provider-call accounting matters especially here

A hybrid policy may claim:

```text only 20% of queries escalate
```

but that does not automatically tell us:

```text actual provider calls
```

because retries and cache behavior can change physical request count.

Therefore preserve:

```text logical routing calls
provider API calls
cache hits
cache misses
retries
429 events
```

The rate-limit instrumentation gap identified earlier must be resolved before making strong efficiency claims.

---

# 35. Rate-limit policy

A dynamic system should not repeatedly hammer the provider when many queries trigger fallback.

Keep:

```text bounded retry
```

and:

```text graceful failure
```

If C2 is unavailable because of:

```text 429
connection failure
provider outage
```

the system must have a declared behavior.

Possible behavior:

```text fallback to strongest non-LLM route
```

or:

```text fail clearly and log
```

The choice must match the project design.

Do not silently treat provider failure as successful routing.

---

# 36. Provider failure must be separated from model failure

Suppose:

```text Compass confidence low
→ C2 fallback
→ provider 429
```

This should not be counted simply as:

```text C2 selected wrong route
```

The result is:

```text infrastructure failure
```

Store an explicit failure category.

This prevents contaminated evaluation.

---

# 37. Dynamic-policy experiment output

A useful per-query JSONL record should conceptually contain:

```json
{
  "id":"...",
  "compass_route":"SIMPLE",
  "compass_confidence":0.91,
  "escalated":false,
  "final_route":"SIMPLE",
  "fallback_router":null,
  "oracle_route":"SIMPLE",
  "oracle_sufficient":true,
  "evidence_recall":1.0,
  "routing_latency_ms":...
}
```

For escalated cases:

```json
{
  "escalated":true,
  "fallback_router":"C2",
  "fallback_route":"MULTI_HOP",
  ...
}
```

The exact schema can follow repository conventions.

---

# 38. Analyze fallback usefulness

For every fallback case ask:

```text Would Compass-only have succeeded?
Did C2 change the route?
Did the changed route improve retrieval?
Was the added cost justified by the retrieval improvement?
```

This lets you compute:

```text fallback correction rate
```

and:

```text useful fallback rate
```

The latter must have a clearly defined denominator.

Do not call every fallback “useful”.

---

# 39. Analyze fallback harm

A fallback can also hurt.

Example:

```text Compass predicted SIMPLE
evidence recall = 1.0

low confidence
→ C2
→ MULTI_HOP
→ evidence recall = 0.5
```

This is an example of:

```text harmful escalation
```

It matters because an expensive fallback is not automatically safer.

Track:

```text beneficial escalations
neutral escalations
harmful escalations
```

using a declared evidence-recall criterion.

---

# 40. Threshold curves

A strong final visualization can plot:

```text x-axis:
LLM fallback rate
```

against:

```text y-axis:
evidence recall
```

Each threshold becomes a point.

Another useful plot:

```text x-axis:
tokens/query
```

against:

```text y-axis:
evidence recall
```

This turns the experiment into a cost-quality frontier.

Do not force a single scalar score when the tradeoff itself is the research result.

---

# 41. Coverage-vs-recall curve

A particularly intuitive curve is:

```text Compass coverage
        vs
evidence recall
```

For example, as threshold changes:

```text more coverage
→ fewer expensive fallbacks
→ potentially lower recall
```

or:

```text lower threshold
→ less fallback
→ higher or lower recall depending on confidence quality
```

The actual direction must be measured.

---

# 42. Pareto interpretation

The policy points can be viewed as:

```text cost
vs
evidence quality
```

A point is useful when another policy does not simultaneously provide:

```text lower/equal cost
+
higher/equal recall
```

Do not call a point “best” in the report.

Describe which points are:

```text Pareto-efficient
```

under the declared metrics.

---

# 43. Question-type analysis

Selective routing should be reported per question type.

At minimum:

```text SIMPLE
MULTI_HOP
TEMPORAL
CHAIN
UNCERTAIN
```

For each type:

```text Compass coverage
fallback rate
evidence recall
LLM usage
```

This may reveal different optimal policies.

For example, difficult complex query types may naturally produce:

```text lower Compass confidence
```

and therefore more fallback.

The actual result must be measured, not assumed.

---

# 44. Simple-question over-routing

This deserves special attention.

The existing C1 analysis indicated over-routing of simple queries.

A dynamic Compass policy can potentially reduce:

```text unnecessary MULTI_HOP escalation
```

if its confidence is informative.

Therefore explicitly report:

```text SIMPLE -> MULTI_HOP
```

frequency for:

```text C1
C2
Compass
Hybrid
```

and measure the retrieval consequence.

---

# 45. Multi-hop under-routing

The opposite risk is:

```text MULTI_HOP question
→ Compass predicts SIMPLE
→ insufficient evidence
```

Track:

```text under-routing count
under-routing rate
recovery via fallback
```

This is likely one of the most important reasons to use selective escalation.

---

# 46. Uncertain route handling

The `UNCERTAIN` route needs special treatment because its semantic meaning has been historically mixed with retrieval insufficiency.

When Compass predicts:

```text UNCERTAIN
```

record:

```text was it genuinely uncertain?
was the Oracle sufficient?
which route actually gave the best retrieval?
```

Do not interpret:

```text UNCERTAIN prediction
```

as automatically equivalent to:

```text retrieval failure
```

---

# 47. What if Compass is overconfident?

Suppose the model produces:

```text confidence > 0.90
```

for many failed routes.

Then a simple threshold policy will fail to protect the system.

This is evidence that:

```text calibration
```

or:

```text a different uncertainty signal
```

may be required.

Do not simply lower the threshold repeatedly based on test behavior.

Use validation calibration or redesign the confidence signal.

---

# 48. What if Compass is underconfident?

The reverse problem:

```text almost every query confidence < 0.70
```

means the fallback may trigger too frequently.

That can erase the cost advantage.

Possible interpretations:

```text model is genuinely uncertain
model is poorly calibrated
training data is noisy
classes overlap
```

Investigate before changing architecture.

---

# 49. Cost of local inference

“Local routing is free” is an oversimplification.

Compass consumes:

```text CPU/GPU time
memory
power
model-loading overhead
```

However, the major comparison in AtlasRAG is likely against:

```text external LLM routing calls
```

So report:

```text local inference latency
```

even if no monetary charge is assigned.

This makes the comparison honest.

---

# 50. Cold-start vs warm inference

Compass latency should be measured separately for:

```text cold start
```

and:

```text warm inference
```

because a model-load step can dominate the first request.

For steady-state per-query performance, use:

```text already-loaded model
```

and report initialization separately.

---

# 51. Batch vs single-query inference

If Compass is evaluated in batches, record that clearly.

A batched classifier can have lower average compute cost than real-time single-query routing.

For a deployment-oriented result, the most relevant measurement may be:

```text single-query inference
```

unless the actual application batches requests.

Do not mix batch and single-query timing numbers.

---

# 52. Failure recovery policy

The hybrid router needs explicit behavior when:

```text Compass model fails to load
Compass inference crashes
C2 provider fails
timeout occurs
```

At minimum:

```text error is logged
request does not silently become success
fallback behavior is explicit
```

The error path should preserve:

```text failure type
timestamp if already supported
route state
provider state
```

Do not let operational failures contaminate benchmark success metrics.

---

# 53. Reproducible threshold experiments

Every threshold run should record:

```text benchmark version
Compass checkpoint
threshold
C2 model
embedding model
retrieval config
random seed, if relevant
commit
```

The threshold grid itself should be saved.

Do not manually run random thresholds and only keep favorable ones.

---

# 54. Recommended experiment naming

A clear convention could be:

```text W5_A_compass_only
W5_B_hybrid_t070
W5_B_hybrid_t080
...
```

or a single experiment with a threshold parameter.

The exact repository convention should be inspected before adding scripts.

The important thing is that each result identifies:

```text policy
threshold
model version
benchmark
```

---

# 55. Minimum Week 5 experiment matrix

At minimum:

```text D       Compass-only
C2        C2-only
W5-H      Compass + C2 fallback
B         Static
E2        Oracle-v2
```

Optionally retain:

```text F       Always strong
G       Always MULTI_HOP
K       Static K10
```

These controls help reveal whether hybrid routing provides genuine value beyond fixed strong retrieval.

---

# 56. Expected report structure

The Week 5 report should have:

```text 1. Benchmark / dataset
2. Compass model
3. C2 fallback model
4. Threshold policy
5. Raw metrics
6. Cost metrics
7. Coverage
8. Recall
9. Per-type analysis
10. Useful vs harmful fallback
11. Threshold curve
12. Paired comparisons
13. Error analysis
14. Limitations
```

This should be generated from machine-readable experiment outputs.

---

# 57. Statistical analysis

Use paired question-level comparisons for:

```text hybrid vs Compass-only
hybrid vs C2-only
hybrid vs B
hybrid vs E2
```

Useful summaries:

```text mean evidence-recall delta
median delta
wins / ties / losses
paired confidence intervals
```

For threshold sweeps, avoid claiming a threshold is superior simply because its test score is highest.

The threshold must be selected using a validation protocol.

---

# 58. Deployment-oriented metric set

A useful compact operational table is:

| Policy | Evidence Recall | Compass Coverage | LLM Calls/Q | Tokens/Q | Routing Latency | End-to-End Latency |
|---|---:|---:|---:|---:|---:|---:|
| Compass | | | | | | |
| C2 | | | | | | |
| Hybrid | | | | | | |
| Static B | | | | | | |
| Oracle E2 | | | | | | |

The exact values depend on the real experiment.

---

# 59. The most informative extra metrics

Also preserve:

```text fallback correction rate
harmful escalation rate
harmful under-routing rate
Compass coverage
per-type fallback rate
provider failure rate
```

These metrics explain *why* a policy occupies a point on the cost-quality curve.

---

# 60. Possible Week 5 findings

The experiment may reveal:

## Pattern A

```text Compass confidence is informative
+
hybrid keeps recall near C2
+
fallback rate is modest
```

This supports further selective-routing work.

## Pattern B

```text Compass confidence is informative
+
hybrid sacrifices little recall
+
LLM work falls substantially
```

This is especially useful for the cost-efficiency story.

## Pattern C

```text Compass confidence is poorly calibrated
```

Then:

```text calibration
```

becomes the next task.

## Pattern D

```text Compass errors are mostly retrieval failures after correct routing
```

Then the bottleneck may be:

```text retrieval/decomposition
```

rather than routing.

## Pattern E

```text Compass + fallback ≈ C2
```

but with less provider usage.

That is still a meaningful result.

## Pattern F

```text Compass + fallback adds complexity
but gives no measurable benefit
```

Then the simpler architecture may remain preferable for this corpus.

All of these are legitimate empirical outcomes.

---

# 61. Do not optimize for a “sweet spot” after seeing the final curve

A common temptation is:

```text run everything
→ inspect curve
→ choose the threshold that looks nicest
→ call it optimal
```

That is weak experimental practice.

Prefer:

```text define threshold-selection criterion
→ use validation data
→ freeze threshold
→ test once
```

Then the final test result is interpretable.

---

# 62. Optional cost-budget experiment

After a basic threshold sweep, define budgets such as:

```text max 0.10 LLM calls/query
max 0.20 LLM calls/query
max 0.30 LLM calls/query
```

or token budgets.

For each budget, choose the validation-optimal threshold and evaluate on test.

This creates a more deployment-oriented analysis:

```text Under X routing budget,
what evidence recall is achieved?
```

The exact budgets should be selected before final test evaluation when possible.

---

# 63. Why routing efficiency matters more than raw classifier accuracy

A Compass classifier can have:

```text 90% route accuracy
```

and still be operationally poor if:

```text the 10% errors are concentrated on evidence-critical queries
```

Likewise, a classifier with lower overall accuracy might produce better system retrieval if its errors are less harmful.

Therefore the final system objective remains:

```text evidence recall under cost constraint
```

not:

```text classifier accuracy alone
```

---

# 64. Error-cost weighting

A future extension can distinguish:

```text harmless route disagreement
```

from:

```text harmful retrieval failure
```

For example:

```text route disagreement
+
same evidence recall
```

is less serious than:

```text route disagreement
+
gold evidence completely missed
```

Do not assign arbitrary numerical penalties immediately.

First preserve the raw outcomes.

---

# 65. Confidence and question complexity

Analyze Compass confidence against:

```text question type
```

and:

```text Oracle-sufficient status
```

This can answer:

```text Does Compass know when it is likely to be wrong?
```

That is the practical definition of useful uncertainty.

A model that is uncertain mostly on easy questions is less useful for escalation than one whose low-confidence region contains a large fraction of actual routing mistakes.

---

# 66. Selective prediction framing

Week 5 can also be described as a selective-prediction experiment:

```text Compass predicts
+
chooses whether to defer
```

The defer action is:

```text call C2
```

This makes the system a:

```text classifier + abstention/fallback policy
```

rather than a fixed classifier.

That is a clean conceptual framing.

---

# 67. Do not confuse `UNCERTAIN` with abstention

These are different concepts:

```text predicted class = UNCERTAIN
```

versus:

```text defer decision = call C2
```

A query can be:

```text Compass prediction = SIMPLE
Compass confidence = low
```

and therefore:

```text defer to C2
```

The final route may then be:

```text MULTI_HOP
```

So Week 5 should preserve:

```text predicted class
confidence
defer/escalate decision
final route
```

as separate fields.

---

# 68. Future extension: three-way decision policy

A later system may use:

```text high confidence:
    execute predicted route

medium confidence:
    execute route + log

low confidence:
    fallback to C2
```

This corresponds to the old project documentation's idea of multiple confidence bands.

However, those original numerical thresholds were explicitly starting points rather than conclusions.

Do not reuse them as final thresholds without validation.

---

# 69. Future extension: human-review queue

The project documentation also discussed a possible very-low-confidence path:

```text extremely low confidence
→ human review
```

This is not required for the first Week 5 experiment.

It could become useful for:

```text ambiguous research questions
retrieval failures
benchmark debugging
```

but adding human review changes the operational objective.

Treat it as a separate extension.

---

# 70. Do not overcomplicate Week 5

The first meaningful Week 5 result only needs:

```text Compass
+
confidence threshold
+
C2 fallback
```

That is enough to test the central idea.

The rest should be optional extensions driven by measured failures.

---

# 71. Exact starting commands

Before changing code:

```powershell
git status
git log --oneline --decorate -10
python -m pytest -q
```

Inspect:

```powershell
Get-Content .\src\atlasrag\routers\compass.py
```

Then locate escalation infrastructure:

```powershell
Get-ChildItem .\src\atlasrag\routers\ -File
```

Inspect experiment definitions:

```powershell
Get-Content .\src\atlasrag\bench\experiments.py
```

Inspect C2:

```powershell
Get-ChildItem .\src\atlasrag\ -Recurse -File | Select-String "EscalatingRouter|C2|llm"
```

Do not modify code until the actual current implementation is understood.

---

# 72. Implementation sequence

The coding agent should proceed:

```text 1. verify current Compass
2. verify current C2
3. verify existing EscalatingRouter
4. verify result schema
5. add provenance fields
6. add fixed-threshold hybrid policy
7. add deterministic unit tests
8. run tiny smoke test
9. run threshold sweep
10. save machine-readable results
11. perform paired analysis
12. inspect useful/harmful fallback
```

Only after this should post-retrieval escalation be considered.

---

# 73. Tests required

At minimum:

```text confidence above threshold does not call C2
confidence below threshold calls C2
fallback route becomes final route
fallback provenance is recorded
Compass route remains available
C2 failure is recorded correctly
no evidence context is passed to Compass
threshold parameter is respected
invalid confidence is handled
all existing router tests still pass
```

Use mocks for C2.

Do not consume provider quota to test threshold logic.

---

# 74. Unit-test example cases

Synthetic examples should include:

```text Compass SIMPLE / 0.95
→ no fallback
```

```text Compass SIMPLE / 0.65 / threshold 0.70
→ C2 fallback
```

```text Compass MULTI_HOP / 0.91
→ no fallback
```

```text Compass UNCERTAIN / 0.40
→ C2 fallback
```

And provider-failure cases:

```text Compass low confidence
→ C2 raises bounded provider error
→ final result marked as failure
```

Do not turn a provider exception into a fabricated route.

---

# 75. Logging requirements

For every dynamic decision preserve:

```text policy name
threshold
Compass route
Compass confidence
escalated
fallback router
final route
fallback status
routing time
provider calls
tokens
```

Do not rely only on console text.

Machine-readable JSONL is preferred.

---

# 76. Benchmark immutability

Week 5 should not alter benchmark questions.

Keep:

```text questions.jsonl
questions_v1_frozen.jsonl
questions_v2.jsonl
```

unchanged unless a separate benchmark-repair task explicitly modifies v2.

Dynamic-routing experiments should use a frozen declared benchmark version.

---

# 77. Run isolation

Run 1 remains frozen.

Week 5 results should use a new run directory, such as:

```text results/run5/
```

The exact naming is repository-dependent.

Never overwrite:

```text results/run1/
```

---

# 78. Model isolation

Do not change:

```text embedding model
retrieval strategy definitions
Compass checkpoint
C2 model
```

during the first threshold sweep.

Otherwise threshold and model changes become confounded.

Run model ablations separately.

---

# 79. Reproducibility manifest for Week 5

Each dynamic-routing run should record:

```text benchmark version
Compass checkpoint
C2 model
threshold
retrieval configuration
embedding model
commit hash
Python version
provider configuration
evaluation sample count
```

And:

```text provider calls
retry counts
tokens
latency
```

---

# 80. What the final Week 5 report should say

A useful conclusion should look structurally like:

```text Compass-only:
    recall = ...
    latency = ...
    coverage = 1.00

C2-only:
    recall = ...
    latency = ...
    LLM calls/query = ...

Hybrid:
    recall = ...
    Compass coverage = ...
    fallback rate = ...
    LLM calls/query = ...
    latency = ...
```

Then explain:

```text which cases were corrected
which cases were harmed
which cases were unnecessary fallbacks
```

The exact interpretation must follow the measured results.

---

# 81. What not to claim

Do not write:

```text Compass knows when it is wrong
```

unless confidence/error analysis supports that.

Prefer:

```text Compass confidence was associated with observed routing/retrieval outcomes at ...
```

where the actual analysis supports the statement.

Do not write:

```text hybrid is optimal
```

unless a formal optimization objective and validation protocol justify it.

Prefer:

```text the selected threshold achieved X recall under Y observed routing cost
```

---

# 82. Possible final architecture

A mature version may eventually look like:

```text                         Question
                            |
                            v
                         Compass
                            |
               +------------+------------+
               |                         |
        high confidence             low confidence
               |                         |
               v                         v
         selected route                   C2
               |                         |
               +------------+------------+
                            |
                            v
                         Retrieval
                            |
                            v
                    Evidence assessment
                            |
                  +---------+---------+
                  |                   |
              sufficient        insufficient
                  |                   |
                  v                   v
              answer            stronger path
```

This is a conceptual target.

It is not automatically the final implementation.

---

# 83. How Week 5 connects to the research contribution

The project began with:

```text fixed retrieval
```

then demonstrated:

```text question-dependent LLM routing
```

then developed:

```text Oracle-grounded learned routing
```

Week 5 addresses the deployment-relevant problem:

```text How much expensive reasoning do we actually need?
```

This is where AtlasRAG can move from:

```text adaptive routing as a demo
```

to:

```text selective computation under a quality/cost constraint
```

That is a stronger research story if the measurements support it.

---

# 84. Relationship to retrieval ablations

Week 5 should not simultaneously change embeddings.

Keep:

```text routing policy
```

as the variable.

After routing is understood, Week 6 can separately test:

```text embedding models
top-k
reranking
chunk parameters
```

This separation allows the project to determine whether an improvement came from:

```text better routing
```

or:

```text better retrieval
```

---

# 85. Relationship to answer-generation evaluation

Do not make final answer quality the main Week 5 metric.

Week 5 is principally:

```text retrieval strategy selection
+
routing efficiency
```

Answer generation introduces another error source.

Once the routing system is stable, later evaluation can measure:

```text final answer correctness
citation support
hallucination
unsupported claims
```

---

# 86. Week 5 completion checklist

```text [ ] Compass-only baseline exists
[ ] C2-only baseline exists
[ ] Hybrid policy implemented
[ ] Compass provenance logged
[ ] C2 fallback provenance logged
[ ] Confidence analysis completed
[ ] Calibration status known
[ ] Threshold sweep completed
[ ] Threshold selected without test leakage
[ ] Evidence recall measured
[ ] Coverage measured
[ ] Fallback rate measured
[ ] Provider calls measured
[ ] Tokens measured
[ ] Latency measured
[ ] Useful fallback measured
[ ] Harmful fallback measured
[ ] Under-routing measured
[ ] Per-type analysis completed
[ ] Paired comparisons completed
[ ] Run 1 untouched
[ ] Benchmark version frozen
[ ] All tests pass
```

---

# 87. Final Week 5 principle

The central principle is:

> **The learned router should not merely predict a route; it should know when its own prediction is reliable enough to avoid expensive fallback.**

That requires three separate measurements:

```text 1. route quality
2. confidence quality
3. cost of escalation
```

The final system should therefore be studied as:

```text                   route
question ─────→ Compass ─────→ retrieval
                  |
                  | low confidence
                  v
                 C2
                  |
                  v
               retrieval
```

and evaluated by:

```text evidence quality
+
routing cost
+
latency
+
fallback behavior
```

The goal is not to make Compass replace every stronger model.

The goal is to determine whether a small question-only router can safely handle a large share of the workload and defer the uncertain remainder.

That makes selective escalation the natural next step before the project changes its retrieval stack or moves to final answer-quality evaluation.
