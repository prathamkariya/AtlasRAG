# AtlasRAG — Week 3: Oracle-Aligned Routing (C2)
## Context handoff / execution manual

> **Status note:** This file documents the next research phase after benchmark construction and repair work. It deliberately separates **historical evidence**, **current repository state**, and **planned Week 3 work**. Do not treat planned components as already implemented.

---

# 1. Week 3 in one page

The purpose of Week 3 is to answer one focused question:

> **Does changing the LLM router's task from vague semantic classification to explicit Oracle-aligned strategy selection materially improve routing behavior and/or efficiency?**

This phase is called **C2** to distinguish it from the existing **C1 / Experiment C** LLM router.

The important experimental relationship is:

```text
C1 = existing semantic LLM router
C2 = separate Oracle-aligned LLM router
B  = static retrieval baseline
E  = empirical Oracle reference
```

The benchmark itself must be sufficiently clean before C2 becomes the main experiment.

The intended logic is:

```text
question
   |
   v
C2 LLM router
   |
   +---- SIMPLE ------> simple/static retrieval
   |
   +---- MULTI_HOP ---> decomposed retrieval
   |
   +---- UNCERTAIN ---> uncertainty/fallback strategy
```

The objective is **not** to make C2 agree with an Oracle label simply because the label exists.

The objective is to test whether a more precisely defined routing task causes an LLM router to make better strategy choices with less unnecessary work.

---

# 2. What is already established before Week 3

The project has already crossed the basic “pipeline works” stage.

Current project facts that define the baseline:

```text
Corpus:
    ~30 papers

Indexed chunks:
    1239

Embedding:
    BAAI/bge-small-en-v1.5

Answering LLM:
    openai/gpt-oss-20b

Original manually accepted test questions:
    27

Original Run 1:
    A Vanilla       0.52
    B Static        0.63
    C LLM Router    0.70
    E Oracle        0.76

Additional controls:
    F Always Strongest / UNCERTAIN    0.76
    G Always MULTI_HOP                0.72
    K Static K10                      0.65
```

These historical Run 1 results are frozen and must remain unchanged.

The key interpretation is not:

```text
C is simply a better classifier.
```

Instead:

```text
C improves retrieval over B,
but incurs substantial routing cost,
and E shows there is still strategy-selection headroom.
```

The project therefore needs to test whether a better-specified LLM routing task can close part of the gap without simply increasing routing cost again.

---

# 3. Why C2 exists

## 3.1 The problem with C1

The original LLM router was built around a semantic routing interpretation.

That is useful, but it does not perfectly match what the empirical Oracle is doing.

The Oracle is effectively asking:

> Which retrieval strategy produces the best evidence coverage for this specific question?

The semantic router is closer to:

> What kind of question is this?

Those are related questions, but they are not identical.

For example:

```text
Question looks multi-hop
        !=
MULTI_HOP strategy is empirically best
```

A question may sound complex but still be solved by simple retrieval.

Conversely:

```text
Question sounds simple
        !=
SIMPLE retrieval is sufficient
```

The research problem is therefore partly one of **target alignment**.

---

# 4. C1 route accuracy must not be treated as the headline metric

The historical C route-accuracy result was low:

```text
C route accuracy ≈ 0.11
```

That number must be interpreted carefully.

C and the original Oracle were not necessarily optimizing identical definitions of the route label.

A semantic router can choose one strategy while another strategy still retrieves all required evidence.

Therefore:

```text
route agreement
```

is a diagnostic.

The primary retrieval outcome remains:

```text
evidence recall
```

Other important outcomes are:

```text
LLM calls
provider API calls
tokens
latency
number of subqueries
```

Week 3 must preserve this distinction.

---

# 5. Oracle v2 is the relevant conceptual foundation

The project introduced Oracle v2 because the original Oracle labeling mixed together different concepts.

The important Oracle-v2 logic is:

```python
best=max(recs.values())

q.ladder_recalls=recs

q.gold_route_v2=next(
    l for l in ladder
    if recs[l]>=best-eps
)

q.oracle_sufficient=best>=1.0-eps
```

Conceptually:

```text
run all ladder strategies
        |
        v
store recall for each strategy
        |
        v
find best observed recall
        |
        v
choose cheapest strategy within epsilon of best
        |
        v
record whether full evidence recall was possible
```

This is much more useful for C2 than the older single-label interpretation.

The two critical concepts are:

```text
gold_route_v2
oracle_sufficient
```

They must not be silently collapsed into one variable.

---

# 6. Why Oracle-v2 sufficiency matters for C2

Suppose a benchmark question has:

```text
SIMPLE        0.50
MULTI_HOP     0.75
UNCERTAIN     0.75
```

The Oracle-v2 label can identify a cheapest strategy within the best observed recall, while `oracle_sufficient` tells us whether any strategy reached complete gold evidence coverage.

This matters because:

```text
routing failure
```

and:

```text
retrieval impossibility under the current benchmark
```

are not the same problem.

C2 should not be punished for failing to select a strategy when the benchmark itself does not contain a route capable of retrieving all gold evidence.

That is why the preferred training/evaluation subset for strategy learning is:

```text
v2_sufficient
```

when sufficient benchmark data exists.

---

# 7. Current benchmark gate before C2

C2 should not be the immediate next coding target until the benchmark is credible enough.

The existing 27-question benchmark was audited with:

```text
19 / 27 support-audit pass
8 / 27 flagged
```

Flag reasons included:

```text
not_all_passages_needed = 7
answer_not_supported    = 2
different_quantity      = 1
```

The project has since added stronger V2 generation logic.

The current deterministic sourcing direction is:

```text
dense candidates
        +
BM25 candidates
        |
        v
union
        |
        v
scientific signal filtering
        |
        v
specific scientific anchor matching
        |
        v
near-duplicate rejection
        |
        v
type-specific structural gates
        |
        v
LLM generation
        |
        v
structured validation
        |
        v
support audit
        |
        v
candidate benchmark items
```

The latest reported test count after pair-sourcing work was:

```text
55 passed
```

but that is a historical report and must be rechecked against the current repository before using it as a current fact.

---

# 8. Benchmark cases that remain important

The benchmark work identified several classes of problems.

## Clearly problematic historical examples

```text
multi_hop-32126f6b
temporal-a8985ff7
```

These were identified for removal/replacement.

## Historical repair / re-source candidates

```text
multi_hop-0760df1d
multi_hop-a55a4306
multi_hop-3cafd9d7
multi_hop-3e7379ed
multi_hop-c1b11062
chain-505459d1
chain-e650cfbd
```

These identifiers are historical context.

Do not blindly edit the original v1 benchmark.

The original benchmark and frozen copy must remain intact:

```text
data/bench/questions.jsonl
data/bench/questions_v1_frozen.jsonl
```

The working benchmark is the version that should absorb repairs:

```text
data/bench/questions_v2.jsonl
```

---

# 9. Week 3 should use a separate benchmark version

Do not create a new benchmark and then overwrite the baseline.

Maintain:

```text
v1
    |
    +--> frozen historical reference

v2
    |
    +--> repaired / regenerated benchmark

C1/C2/B/E
    |
    +--> evaluated under clearly identified benchmark version
```

When reporting results later, every number must identify:

```text
benchmark version
question count
accepted question count
sufficient subset, when applicable
strategy configuration
LLM model
embedding model
```

---

# 10. Research question for C2

The cleanest formulation is:

> **Can a more explicitly Oracle-aligned LLM router improve strategy-selection agreement and/or evidence retrieval efficiency relative to the existing semantic LLM router, without merely increasing LLM routing cost?**

This gives a direct comparison:

```text
C1
vs
C2
```

while still retaining:

```text
B
E
```

as the baseline/reference pair.

The experiment should investigate several measurable outcomes rather than assume one outcome in advance.

---

# 11. C2 must remain a separate experiment

Do not rewrite C1 in place.

Keep:

```text
C1 = existing implementation
C2 = new implementation
```

Why?

Because modifying C1 destroys the clean historical comparison.

The ideal experiment table is:

| Experiment | Router idea | Purpose |
|---|---|---|
| B | fixed static retrieval | baseline |
| C1 | semantic LLM router | existing adaptive baseline |
| C2 | Oracle-aligned LLM router | task-alignment ablation |
| E | empirical Oracle | upper-reference / strategy-selection reference |

Run 1 remains frozen.

Any C2 results should belong to a new run group, not `results/run1/`.

---

# 12. What “Oracle-aligned” should mean

Oracle-aligned does **not** mean giving the LLM:

```text
gold chunks
```

or:

```text
retrieved answer context
```

or:

```text
future benchmark results
```

That would invalidate the routing experiment.

The router should still operate from the query and whatever question-side information the routing design explicitly permits.

The key change is the task formulation.

C2 should reason about:

```text
Which retrieval strategy should I execute for this query?
```

rather than merely:

```text What semantic class does this question belong to?
```

---

# 13. Information-isolation rule

The router must not receive information that would only exist after retrieval.

For a fair strategy-selection experiment:

```text INPUT:
    question
```

Potentially allowed, depending on the exact controlled design:

```text question-derived structured metadata
```

Not allowed:

```text retrieved evidence
gold chunks
gold route from evaluation labels
final answer
answer-generation context
```

The critical research principle is:

> The router selects the retrieval policy before seeing the evidence that policy is supposed to retrieve.

This prevents target leakage.

---

# 14. Suggested C2 output schema

The exact implementation can vary, but structured output is preferable.

A conceptual response should contain something like:

```json
{
  "route":"SIMPLE",
  "confidence":0.82,
  "reason":"The question asks for a directly stated quantity and does not require combining independent evidence."
}
```

For evaluation, the only field that should control execution is:

```text
route
```

Confidence and rationale are diagnostics.

Do not make downstream retrieval depend on free-form rationale text.

---

# 15. Route vocabulary

Use the project's current route vocabulary unless the benchmark work explicitly changes it.

The historical strategy labels are:

```text
SIMPLE
MULTI_HOP
UNCERTAIN
```

The meaning of `UNCERTAIN` needs care.

It should not silently mean:

```text
retrieval impossible
```

and:

```text
semantic uncertainty
```

at the same time.

Oracle-v2 keeps the sufficiency distinction separately through:

```text
oracle_sufficient
```

Future benchmark versions may revisit the label vocabulary, but Week 3 should not silently redesign the entire taxonomy while testing C2.

---

# 16. What C2 should be evaluated on

## Primary retrieval metric

```text
Evidence Recall
```

This measures whether the executed retrieval strategy covers the benchmark's gold evidence.

## Routing metrics

```text
Route agreement with gold_route_v2
Route agreement on oracle_sufficient questions
Per-type route agreement
Confusion matrix
```

Route agreement is diagnostic, not sufficient by itself.

## Efficiency metrics

```text
LLM logical calls
provider API calls
cache hits
cache misses
retry attempts
prompt tokens
completion tokens
total tokens
latency
```

The distinction between:

```text logical call
```

and:

```text provider call
```

is important.

A cache hit can produce:

```text 1 logical call
0 provider calls
```

while a retried request can produce:

```text 1 logical call
2+ provider attempts
```

These must not be conflated.

---

# 17. Instrumentation requirement before C2

The project currently has a known measurement gap.

The current `LLMClient.stats` approximately tracks:

```python
{
    "calls":0,
    "prompt_tokens":0,
    "completion_tokens":0,
    "cache_hits":0
}
```

This does not fully distinguish:

```text
provider calls
cache misses
retry attempts
RateLimitError count
APIConnectionError count
final rate-limit state
```

This matters directly for a routing-efficiency paper.

A future C2 run should ideally persist a machine-readable run summary with fields such as:

```text
logical_calls
provider_calls
cache_hits
cache_misses
retry_attempts
rate_limit_errors
connection_errors
prompt_tokens
completion_tokens
total_tokens
```

Do not reconstruct provider-call counts from old pilot logs when those values were never persisted.

---

# 18. Rate-limit handling

Current application-level retry behavior is bounded.

The implementation has:

```text
OpenAI(..., max_retries=0)
```

with application-controlled retries.

The reported default behavior was approximately:

```text
1 second
2 seconds
then stop
```

with a configured upper retry delay.

The intended outcome is:

```text
bounded retry
        |
        +--> success
        |
        +--> final failure
```

not:

```text
unbounded waiting
```

C2 generation/evaluation must preserve the same bounded behavior.

A 429 must not turn into an effectively infinite research run.

---

# 19. Avoid wasting provider quota

Deterministic logic belongs in unit tests.

Do not spend Groq quota to test:

```text
scientific signal extraction
duplicate detection
temporal date gates
same-quantity checks
chain paper identity
JSON schema validation
```

These can all be tested using local synthetic examples.

Only real generation pilots should consume provider quota.

---

# 20. C2 prompt design principles

The prompt should be short enough that routing itself does not dominate the cost it is supposed to optimize.

It should clearly describe:

```text
available strategies
strategy definitions
selection objective
what information is unavailable
expected structured output
```

A strong conceptual prompt should distinguish the strategies by **retrieval behavior**, not by vague linguistic labels.

Example strategy definitions:

```text
SIMPLE:
    Direct retrieval of the question.

MULTI_HOP:
    Decompose the question into multiple retrieval intents and combine evidence.

UNCERTAIN:
    Use the fallback/uncertainty handling path when the query is genuinely ambiguous
    or cannot be confidently mapped to a cheaper strategy.
```

The exact definitions must match the actual implementation.

Do not invent capabilities the strategy does not have.

---

# 21. Important warning about “best route”

Do not define:

```text best route = most semantically appropriate label
```

without checking what the Oracle actually measures.

The empirical Oracle is based on observed evidence retrieval.

Therefore, the evaluation question is:

```text Did the selected route produce strong evidence retrieval?
```

not merely:

```text Did the LLM classify the wording correctly?
```

---

# 22. C2 experiment design

The clean experimental sequence is:

```text
1. verify repository
2. verify benchmark version
3. verify current C1 implementation
4. verify Oracle-v2 labels
5. verify instrumentation
6. implement C2 separately
7. run unit tests
8. run a tiny smoke test
9. run the full C2 evaluation
10. compare B / C1 / C2 / E
11. perform paired analysis
12. inspect failures
```

Do not skip straight from implementation to broad claims.

---

# 23. Recommended run organization

Use a new run group.

For example:

```text
results/
    run1/
        A_vanilla.jsonl
        B_static.jsonl
        ...
```

Run 1 remains frozen.

A future C2 run should live elsewhere, for example:

```text
results/
    run2/
        ...
```

The exact filename can follow the repository's existing conventions.

Do not overwrite Run 1.

---

# 24. Minimum experiment matrix

The minimum scientifically useful comparison is:

```text
B  Static
C1 Existing LLM Router
C2 Oracle-Aligned LLM Router
E2 Oracle-v2
```

Useful controls may also include:

```text
F Always Strongest
G Always MULTI_HOP
K Static K10
```

These controls already exist and should not be removed merely because they are less interesting.

They help answer questions such as:

```text Is a router actually helping?
Is the improvement just caused by always using a strong route?
Does changing k explain the result?
```

---

# 25. Paired analysis is important

Do not rely only on overall means.

For every comparison, preserve per-question results.

Then compute paired differences such as:

```text C2 - C1
C2 - B
E2 - C2
```

For each question:

```text delta_i = metric_C2_i - metric_C1_i
```

Then report an uncertainty interval for the paired differences.

The exact statistical method should match the metric and sample size.

The key principle is:

> The same questions must be compared across strategies.

---

# 26. Efficiency should be analyzed with retrieval quality

AtlasRAG is fundamentally a tradeoff problem.

A useful result is not simply:

```text higher recall
```

and not simply:

```text fewer tokens
```

The important relationship is:

```text evidence quality
        vs
routing cost
```

Possible reported quantities include:

```text evidence recall per query
tokens/query
LLM calls/query
provider calls/query
latency/query
```

Later analysis may use a constrained objective such as:

```text maximize evidence recall
subject to a token budget
```

But the raw measurements should be preserved first.

Do not choose a utility formula after seeing which one makes the result look best.

---

# 27. C2 failure categories

When C2 underperforms, classify the problem rather than assuming “the router is bad”.

Useful categories:

```text 1. Route selection failure
2. Retrieval failure after correct routing
3. Query decomposition failure
4. Benchmark/evidence problem
5. LLM output/schema failure
6. Provider/rate-limit failure
7. Instrumentation issue
```

This distinction matters because:

```text correct route + weak retrieval
```

is not the same failure as:

```text wrong route + strong retrieval would have solved it
```

---

# 28. Failure inspection workflow

For an individual C2 failure inspect:

```text question
gold route
gold chunks
C1 route
C2 route
C1 retrieved chunks
C2 retrieved chunks
evidence recall
subqueries
latency
LLM usage
```

Then classify:

```text benchmark issue
retrieval issue
query decomposition issue
routing issue
provider issue
```

Do not change the benchmark merely because C2 failed.

---

# 29. Special attention to multi-hop

The historical data showed that multi-hop routing itself did not guarantee complete retrieval.

Some multi-hop questions had approximately:

```text C recall = 0.50
E recall = 0.67
```

This means:

```text correct strategy choice
```

does not automatically solve:

```text evidence selection/decomposition
```

C2 should therefore not be evaluated solely through route agreement.

A C2 improvement in route accuracy may produce little retrieval improvement if retrieval/decomposition remains the bottleneck.

---

# 30. Special attention to temporal questions

The old temporal subset had:

```text 2 questions
```

and all tested strategies reached:

```text 0.00
```

This is an unresolved benchmark issue, not a reason to claim that temporal routing is impossible.

The benchmark team later added temporal-pair sourcing requirements:

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

The current project position is:

```text temporal benchmark quality must be established
before strong temporal routing conclusions
```

Do not use the two old temporal questions as proof of general temporal-router failure.

---

# 31. C2 and simple questions

Simple questions are especially important because the project is investigating routing efficiency.

An LLM router that spends expensive reasoning on easy queries can destroy the efficiency benefit.

Therefore inspect:

```text SIMPLE routed to SIMPLE
SIMPLE routed to MULTI_HOP
SIMPLE routed to UNCERTAIN
```

For each unnecessary escalation, record:

```text extra calls
extra tokens
extra latency
retrieval benefit, if any
```

This is one of the most informative C1-vs-C2 diagnostics.

---

# 32. What C2 should not do

C2 must not become:

```text another answer-generating LLM
```

It is a strategy selector.

Keep the interface conceptually:

```python
route(question)->strategy
```

and not:

```python
route(question,context,answer)->strategy
```

for the core retrieval-only experiment.

---

# 33. What C2 should not modify

Unless a controlled experiment explicitly requires it, do not modify:

```text embedding model
chunking behavior
corpus
Run 1
Oracle-v2 logic
benchmark v1
```

Otherwise multiple variables change at once.

The cleaner question is:

```text same corpus
same embeddings
same retrieval strategies
same benchmark
different router task
```

---

# 34. C2 implementation boundary

The existing experiment machinery already maps experiment codes roughly as:

```text
A = vanilla
B = static
C = llm
D = compass
E = oracle
F = strongest
G = multihop
K = static_k10
H = heuristic
```

This means C2 should be integrated as a new explicit experiment code rather than silently reusing C.

The exact code/name can be chosen after inspecting the current repository.

Do not assume the historical mapping is unchanged without verifying the current checkout.

---

# 35. Suggested files to inspect before implementation

Start with:

```powershell
git status
python -m pytest -q
```

Then inspect:

```powershell
Get-Content .\src\atlasrag\bench\experiments.py
Get-Content .\src\atlasrag\routers\llm.py
Get-Content .\src\atlasrag\routers\*.py
Get-Content .\src\atlasrag\bench\oracle_v2.py
Get-Content .\src\atlasrag\llm.py
```

The exact router filename may differ in the current checkout.

The purpose of this inspection is to identify:

```text where C1 lives
how strategies are invoked
how experiment results are persisted
where Oracle-v2 labels are loaded
how LLM statistics are collected
```

Do not write code before this inspection.

---

# 36. Tests required before a real C2 run

At minimum, add local tests for:

```text
valid SIMPLE output parses
valid MULTI_HOP output parses
valid UNCERTAIN output parses
invalid route is rejected
malformed JSON is handled
missing route is handled
extra prose does not break parsing
router returns deterministic strategy for a fixed mocked response
C1 remains unchanged
existing experiment mappings still work
```

Also preserve all benchmark tests from Week 2.

A C2 test double should not make real network requests.

---

# 37. Tiny smoke test

Before a full 27-question run, use a very small local or provider-backed smoke test.

The purpose is only to verify:

```text C2 can be constructed
question can be routed
route is parsed
strategy executes
result is persisted
stats are updated
```

Do not treat a tiny smoke test as evidence of scientific performance.

---

# 38. Full C2 run gate

Do a full C2 evaluation only when:

```text all tests pass
+
benchmark version is declared
+
Oracle-v2 labels are verified
+
C1 remains untouched
+
Run 1 remains untouched
+
instrumentation is sufficient
```

Then compare:

```text B
C1
C2
E2
```

using the same accepted evaluation set.

---

# 39. What counts as a useful C2 result

A useful result may look like any of these patterns:

```text C2 improves evidence recall at similar cost
```

or:

```text C2 maintains recall while reducing LLM work
```

or:

```text C2 improves route agreement but retrieval remains unchanged
```

or:

```text C2 does not improve over C1
```

All of these are scientifically informative.

The experiment must not be judged by whether C2 “wins”.

---

# 40. Do not force a positive result

The research question is not:

```text How do we make C2 beat C1?
```

It is:

```text Does Oracle-aligned routing change the measured
recall/cost tradeoff?
```

A null result is valuable because it can show that the current bottleneck is elsewhere.

For example:

```text C2 route selection improves
but retrieval recall does not
```

would suggest the main limitation is likely downstream retrieval/decomposition rather than routing semantics.

---

# 41. Relationship to Compass

Compass is the lightweight learned router.

C2 is not Compass.

The intended progression is:

```text C1
 |
 v
C2 Oracle-aligned LLM routing
 |
 v
validated routing task
 |
 v
Compass training
```

C2 can help refine:

```text target definition
route semantics
failure analysis
evaluation metrics
cost accounting
```

before training a local learned router.

Compass remains deferred until the benchmark is sufficiently clean and large.

---

# 42. Why Compass should still be deferred

The currently accepted benchmark is too small for robust learned routing training.

Historical status:

```text accepted test questions = 27
Oracle-v2 UNCERTAIN = 2
Oracle-v2 insufficient = 9
```

Several complex question types also needed repair/regeneration.

Training Compass now risks learning:

```text benchmark artifacts
```

rather than:

```text general routing behavior
```

That is especially dangerous because Compass is intended to be a research contribution.

---

# 43. Train/test leakage rules

When eventually preparing Compass data:

```text training questions
    must not overlap
    with test questions
```

Do not use:

```text test gold chunks
test Oracle labels
test routes
test answers
```

to engineer train-time features.

A routing model should see only information available at inference time.

---

# 44. Proposed C2 result table

For each strategy report approximately:

| Strategy | Evidence Recall | LLM Calls/Q | Provider Calls/Q | Tokens/Q | p50 Latency | p95 Latency |
|---|---:|---:|---:|---:|---:|---:|
| B Static | | | | | | |
| C1 LLM | | | | | | |
| C2 Oracle-aligned | | | | | | |
| E2 Oracle-v2 | | | | | | |

Then add:

```text
route agreement
simple over-routing
multi-hop routing
uncertain routing
paired deltas
```

Do not invent numbers before the run.

---

# 45. Per-question analysis table

A useful diagnostic file should preserve rows like:

| Question ID | Type | Gold Route v2 | Oracle Sufficient | B Recall | C1 Route | C1 Recall | C2 Route | C2 Recall | C2 Tokens | C2 Latency |
|---|---|---|---|---:|---|---:|---|---:|---:|---:|
| ... | ... | ... | ... | ... | ... | ... | ... | ... | ... | ... |

This makes error analysis reproducible.

---

# 46. Confusion matrix expectations

Do not only compute:

```text accuracy
```

Also inspect:

```text SIMPLE -> SIMPLE
SIMPLE -> MULTI_HOP
SIMPLE -> UNCERTAIN

MULTI_HOP -> SIMPLE
MULTI_HOP -> MULTI_HOP
MULTI_HOP -> UNCERTAIN

UNCERTAIN -> SIMPLE
UNCERTAIN -> MULTI_HOP
UNCERTAIN -> UNCERTAIN
```

This is especially important because the efficiency story may be dominated by unnecessary escalation.

---

# 47. Route agreement on sufficient questions

A particularly useful analysis is:

```text all questions
```

versus:

```text oracle_sufficient == true
```

Why?

Because an insufficient benchmark case can make every strategy appear “wrong” under exact gold recall.

Report these separately.

Do not hide insufficient questions.

Do not silently delete them from all analyses.

---

# 48. The role of `v2_sufficient`

The `v2_sufficient` training/evaluation scheme exists specifically to avoid mixing:

```text strategy selection
```

with:

```text no strategy can fully satisfy the benchmark
```

When using it, clearly report:

```text subset size
selection rule
excluded count
```

Do not describe a sufficient-only score as the result on the full benchmark.

---

# 49. C2 prompt-ablation possibility

A controlled follow-up can vary only the prompt framing.

For example:

```text C1:
    semantic question-type classification

C2:
    explicit retrieval-strategy selection

C2b:
    retrieval-strategy selection
    + concise strategy definitions
```

Do not run multiple prompt changes at once and then attribute the difference to one specific factor.

---

# 50. Cost-aware routing as a later extension

If C2 works, a later experiment can explicitly include:

```text expected evidence gain
vs
estimated routing cost
```

The LLM could be asked to select a route using a budget constraint.

However, this should come after the basic C2 experiment.

Do not add cost-aware scoring to the first C2 implementation unless the repository already contains the necessary deterministic cost model.

---

# 51. Why this phase matters to the overall paper

The broader AtlasRAG story is:

```text standard retrieval
        ↓
stronger static retrieval
        ↓
LLM adaptive routing
        ↓
empirical Oracle headroom
        ↓
lightweight routing
```

C2 is the bridge between:

```text expensive semantic LLM routing
```

and:

```text learned lightweight routing
```

It tests whether better target alignment is enough to extract more of the Oracle's benefit before training a dedicated model.

That makes C2 a useful scientific ablation rather than merely another implementation variant.

---

# 52. Current open questions C2 should answer

The following were previously identified as important unresolved questions:

```text 1. Does Oracle-aligned prompting materially improve efficiency?

2. Does it reduce unnecessary MULTI_HOP routing?

3. Does it improve route agreement with gold_route_v2?

4. Does route agreement improvement translate into evidence-recall improvement?

5. How much of the C1-to-E gap is routing versus retrieval/decomposition?

6. Do simple questions account for a large share of unnecessary routing cost?

7. Does C2 help on oracle_sufficient questions specifically?

8. Does C2 fail mainly because of routing, retrieval, or benchmark structure?
```

Do not assume the answer to any of these in advance.

---

# 53. Week 3 exact workflow

## Step 1 — repository verification

```powershell
git status
git log --oneline --decorate -10
python -m pytest -q
```

Verify:

```text branch
commit
working tree
test count
```

---

## Step 2 — verify benchmark state

Inspect:

```text
data/bench/questions.jsonl
data/bench/questions_v1_frozen.jsonl
data/bench/questions_v2.jsonl
data/bench/audit.jsonl
data/bench/v2_review_manifest.json
```

Confirm:

```text v1 untouched
v2 declared working version
audit present
Oracle-v2 labels present or reproducible
```

---

## Step 3 — inspect C1

Locate the current LLM-router implementation.

Determine:

```text input
prompt
parser
route output
strategy dispatch
stats collection
```

Do not change it yet.

---

## Step 4 — verify Oracle-v2 integration

Check:

```text src/atlasrag/bench/oracle_v2.py
```

Confirm:

```text ladder recalls preserved
gold_route_v2 populated
oracle_sufficient populated
```

---

## Step 5 — repair instrumentation if needed

Before using efficiency numbers, distinguish:

```text logical LLM call
provider API call
cache hit
cache miss
retry
tokens
latency
```

Add machine-readable summary output if current infrastructure does not already provide it.

---

## Step 6 — design C2 as a separate implementation

Write a small design note before code.

It should specify:

```text input:
question only

output:
route + optional confidence/reason

allowed routes:
SIMPLE / MULTI_HOP / UNCERTAIN

no evidence context:
yes

C1 modified:
no

Run 1 modified:
no
```

---

## Step 7 — add tests

Run:

```powershell
python -m pytest -q
```

Do not consume Groq quota while debugging parser/logic tests.

---

## Step 8 — tiny smoke test

Use a very small sample.

Verify:

```text route returned
strategy executed
result persisted
stats persisted
```

---

## Step 9 — full C2 evaluation

Run a new run group.

Preserve:

```text exact command
exact benchmark version
exact config
exact model
exact commit
```

---

## Step 10 — compare

Compute:

```text B
C1
C2
E2
```

at minimum.

Then produce:

```text overall evidence recall
per-type recall
route agreement
tokens
provider calls
latency
paired differences
```

---

# 54. Suggested implementation/reporting checklist

Before calling Week 3 complete:

```text [ ] C1 remains untouched
[ ] Run 1 remains untouched
[ ] benchmark version recorded
[ ] Oracle-v2 labels verified
[ ] sufficient subset defined
[ ] C2 is a separate route implementation
[ ] no retrieval evidence leaks into C2
[ ] structured output is validated
[ ] invalid routes handled
[ ] tests pass
[ ] bounded 429 behavior preserved
[ ] provider-call accounting is trustworthy
[ ] full C2 run completed
[ ] B/C1/C2/E2 compared
[ ] per-question results preserved
[ ] failures inspected
[ ] no cherry-picking of favorable examples
```

---

# 55. Research-safety rules

These rules should remain hard constraints.

## Never overwrite Run 1

```text
results/run1/
```

is historical evidence.

---

## Never overwrite v1 benchmark

```text
data/bench/questions.jsonl
data/bench/questions_v1_frozen.jsonl
```

remain frozen.

---

## Never use test information inside the router

No:

```text gold chunks
gold answer
test Oracle label
post-retrieval evidence
```

as C2 inputs.

---

## Never loosen benchmark validation just to increase yield

Low yield can be a corpus-quality signal.

The correct response is usually:

```text better sourcing
better benchmark construction
better review
```

not:

```text weaker acceptance criteria
```

---

## Never convert diagnostic metrics into headline claims

Examples:

```text route accuracy
```

should not replace:

```text evidence recall
```

and:

```text token reduction
```

should not replace:

```text evidence quality
```

---

# 56. What to report after implementation

After the coding agent finishes, require a compact report containing:

```text
Current commit:
Branch:
Tests before:
Tests after:

Files changed:
Why each changed:

C1 modified:
yes/no

Run1 modified:
yes/no

Benchmark modified:
which version:

C2 prompt/task:
exact description

C2 test result:
...

Provider calls:
...

Logical calls:
...

Cache hits:
...

Retries:
...

429 events:
...

Tokens:
...

Pilot/full-run question count:
...

Evidence recall:
B:
C1:
C2:
E2:

Route agreement:
C1:
C2:

Most common C2 failure:
...

Next action:
...
```

Do not accept vague claims such as:

```text “routing improved”
```

without the underlying numbers.

---

# 57. Expected next phase after Week 3

Only after C2 is understood should the project proceed toward:

```text Week 4 / Compass
```

That phase would cover:

```text train Oracle labels
class-balance inspection
leakage checks
base-model selection
frozen backbone
LoRA adapter
classification head
CompassRouter
D retrieval-only experiment
```

But the entry condition is:

```text benchmark quality sufficient
+
routing target stable
+
C2 understood
```

Do not train Compass merely because the code is available.

---

# 58. Week 3 completion criteria

Week 3 is complete when the project can answer, with reproducible measurements:

```text Does C2 change strategy-selection behavior?

Does C2 change evidence recall?

Does C2 reduce unnecessary routing?

Does C2 reduce or increase LLM work?

Does C2 narrow the gap to the empirical Oracle?

Are the remaining failures routing failures or retrieval/decomposition failures?
```

A valid conclusion may be:

```text no meaningful improvement
```

provided it is supported by the measured experiment.

---

# 59. Final Week 3 handoff principle

The central rule is:

> **Do not optimize the learned router until the target it is supposed to imitate is clearly defined.**

For AtlasRAG, that target is not merely a human-readable question type.

The useful target is a retrieval-strategy decision grounded in observed evidence quality and constrained by real routing cost.

The project should therefore move in this order:

```text benchmark validity
        ↓
Oracle-v2 semantics
        ↓
C1 baseline
        ↓
C2 Oracle-aligned ablation
        ↓
clean cost/retrieval accounting
        ↓
Compass training
```

Everything that follows should be reproducible from the repository, benchmark version, configuration, model names, and saved per-question results.
