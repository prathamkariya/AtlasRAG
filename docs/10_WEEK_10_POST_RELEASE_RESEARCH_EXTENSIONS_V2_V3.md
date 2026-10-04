# AtlasRAG — Week 10: Post-Release Research Extensions & V2/V3 Roadmap

## 1. Purpose

Weeks 8 and 9 bring the first AtlasRAG research cycle to a stopping point.

Week 8 establishes:

```text
final analysis
reproducibility
claim discipline
release readiness
```

Week 9 establishes:

```text
paper/report
README
presentation
demo
portfolio
release hygiene
```

Week 10 should therefore **not reopen the finished experiment by default**.

Instead, it defines the next research generation:

```text
AtlasRAG V1
   ↓
observed limitations
   ↓
research hypotheses
   ↓
V2 / V3 extensions
   ↓
new benchmark / new experiment
   ↓
new evidence
```

The central rule is:

> **A future extension must be motivated by a measured limitation in V1, not by the desire to add another fashionable component.**

The purpose of this document is to make a future AtlasRAG session productive without forcing the project into endless experimentation.

---

# 2. The V1 stopping point

The first version of AtlasRAG is centered on:

```text
scientific literature
+
adaptive retrieval routing
+
hybrid retrieval
+
empirical Oracle-v2
+
controlled benchmark
+
answer-level evaluation
```

The research chain is:

```text
Question
   ↓
Routing
   ↓
Retrieval policy
   ↓
Evidence
   ↓
Answer
   ↓
Citation / grounding
   ↓
Cost + latency
```

The original benchmark and experiments already revealed an important distinction:

```text
correct route
```

does not necessarily imply:

```text
successful retrieval
```

and:

```text
successful retrieval
```

does not necessarily imply:

```text correct final answer
```

Therefore later versions should build on the observed separation between:

```text routing
retrieval
answering
evaluation
```

rather than collapsing them into a single model.

---

# 3. What the next version should not do

Do not begin V2 by immediately adding:

```text
another LLM
another vector database
another agent framework
another reranker
web search
multi-agent reasoning
large-scale training
Kubernetes
```

unless a measured V1 limitation justifies it.

The project already has a working FastAPI layer, a hybrid retrieval stack, benchmark tooling, routing abstractions, and evaluation infrastructure.

The next research gain is more likely to come from:

```text better supervision
better failure prediction
better evidence verification
better benchmark scale
```

than from adding infrastructure.

---

# 4. The three most important post-V1 directions

The current project context identifies three especially meaningful directions:

```text
Direction A
Evidence verification

Direction B
Retrieval-failure prediction

Direction C
Larger / richer scientific benchmark
```

They answer different questions.

### Evidence verification

Question:

> Can the system check whether a generated claim is actually supported by its cited scientific evidence?

### Retrieval-failure prediction

Question:

> Can a lightweight model predict that the current retrieval path is likely to fail before or after expensive retrieval is performed?

### Larger benchmark

Question:

> Do the observed routing patterns survive across a broader and more diverse scientific evidence distribution?

These should be treated as separate research tracks.

---

# 5. V2 — Evidence Verification

## 5.1 Research question

A natural next question after answer-level evaluation is:

> Can AtlasRAG verify citation support reliably enough to reduce unsupported scientific claims?

The pipeline becomes:

```text
question
   ↓
retrieval
   ↓
answer generation
   ↓
claims
   ↓
citation mapping
   ↓
evidence verification
```

The final stage is distinct from answer generation.

---

# 6. Why evidence verification matters

A final answer can be:

```text factually correct
```

while its citation is:

```text wrong
```

or:

```text incomplete
```

Likewise, an answer can cite a real chunk while making an additional unsupported claim.

Therefore:

```text answer correctness
```

and:

```text citation support
```

should remain separate.

This is especially important for scientific literature because answers may contain:

```text numerical values
parameter constraints
comparisons
causal explanations
uncertainties
model names
temporal claims
```

A citation that is merely topically related is not necessarily sufficient.

---

# 7. V2 evidence-verification formulation

Represent the output as claim units.

Conceptually:

```text
Answer
   ↓
claim extraction
   ↓
claim 1
claim 2
claim 3
...
   ↓
candidate citation(s)
   ↓
support judgment
```

Each claim should receive something like:

```text
SUPPORTED
PARTIALLY_SUPPORTED
UNSUPPORTED
NOT_CHECKABLE
```

The final representation should use the vocabulary actually implemented.

Do not add categories merely because they sound useful.

---

# 8. Claim-citation graph

A useful mental model is a bipartite graph:

```text
Claims                    Evidence

C1  --------------------> E1
C2  --------------------> E3
C3  --------------------> E2 + E4
C4  --------------------> no support
```

This allows analysis of:

```text citation precision
citation coverage
unsupported claim rate
over-citation
under-citation
```

It also makes debugging easier.

---

# 9. V2 evidence-verification dataset

Do not reuse the final benchmark as the only source of verification labels.

Create a separate artifact such as:

```text
data/bench/evidence_verification_v1.jsonl
```

or the naming convention used by the repository.

Each record can conceptually contain:

```text
question
answer
claim
citation
evidence_chunk
label
reason
```

The exact schema should be designed after inspecting the repository.

The important rule is:

```text
verification labels are independent evaluation artifacts
```

and should not silently alter the original benchmark.

---

# 10. Evidence-verification label creation

Potential process:

```text
generated answer
      ↓
claim extraction
      ↓
citation mapping
      ↓
automatic pre-filter
      ↓
human review
      ↓
final verification label
```

Do not rely entirely on an LLM judge.

A judge can assist with:

```text candidate ranking
pre-screening
explanation
```

but human review is still valuable for scientific claims.

---

# 11. Numeric verification

Scientific QA has a special need for numerical checking.

A verification layer should eventually identify:

```text quantity
value
unit
uncertainty
direction
comparison
```

Example:

```text H0 = 73.0 ± 1.0 km/s/Mpc
```

The verifier should be able to distinguish:

```text correct value
correct unit
incorrect uncertainty
wrong comparison
```

rather than treating the whole sentence as simply supported/unsupported.

Do not build a complex symbolic system until failure analysis shows that numeric errors are common enough to justify it.

---

# 12. V2 evaluation

Useful metrics include:

```text claim-level precision
claim-level recall
unsupported claim rate
citation precision
citation coverage
numeric verification accuracy
```

The exact metric definitions must be fixed before final evaluation.

Keep automatic and human evaluation separate.

For example:

```text LLM judge result
```

should not be silently reported as:

```text expert truth
```

---

# 13. V2 benchmark split

The evidence-verification data should have:

```text train
validation
test
```

when model training is involved.

The split should avoid leakage.

For scientific papers, a strong option is:

```text paper-disjoint split
```

so the same paper does not appear across training and test in ways that make memorization easier.

---

# 14. V2 failure categories

Useful analysis categories:

```text
citation points to irrelevant chunk
citation supports only part of claim
claim combines supported + unsupported information
numeric mismatch
uncertainty mismatch
source conflict ignored
source chronology ignored
citation omitted
answer invents claim
```

Only retain categories that appear in actual data.

The objective is to discover recurring failure modes rather than invent a taxonomy and force every case into it.

---

# 15. V3 — Retrieval-Failure Prediction

The second major extension is to predict retrieval failure itself.

Research question:

> Can a lightweight model predict whether the current retrieval policy is likely to recover sufficient scientific evidence?

This is different from question-type routing.

---

# 16. Routing vs failure prediction

Current routing asks:

```text
Which strategy should I use?
```

Failure prediction asks:

```text
Did the strategy I used probably fail?
```

These are different decisions.

A system could eventually become:

```text
Question
   ↓
Compass
   ↓
chosen strategy
   ↓
retrieval
   ↓
failure detector
   ↓
confidence
   ├─ sufficient → answer
   └─ likely failure → escalate
```

This creates a more closed-loop architecture.

---

# 17. Why failure prediction may be stronger than pure pre-routing

Question-only routing has a fundamental limitation:

```text
the router cannot directly see retrieval state
```

A question may appear simple but still fail because:

```text terminology is unusual
retrieval vocabulary differs
evidence is buried in a table
the corpus contains conflicting naming
chunking is unfavorable
the needed passage is poorly represented
```

A post-retrieval signal can observe some of this.

Therefore:

```text question-only routing
```

and:

```text retrieval-state-aware verification
```

should be compared rather than assuming one is universally superior.

---

# 18. V3 input signals

Potential signals include:

```text top-score gap
reranker score
score distribution
number of distinct papers retrieved
query-to-evidence similarity
BM25/dense agreement
evidence redundancy
citation/source diversity
presence of expected scientific anchors
```

These are candidate features, not automatically valid features.

Avoid leakage.

For example, if a feature directly exposes:

```text gold evidence
```

it cannot be used in a realistic deployed failure detector.

---

# 19. Dense/BM25 disagreement as a signal

One interesting feature is:

```text dense retrieval says one thing
BM25 says another
```

For example:

```text dense top result:
paper A

BM25 top result:
paper B
```

This may indicate:

```text terminology mismatch
ambiguous wording
multiple relevant entities
```

It could become a useful uncertainty signal.

But this is a hypothesis.

Measure it before designing a large model around it.

---

# 20. Reranker score distribution

A single top score may be less informative than the shape of the ranking.

Potential signals:

```text top-1 score
top-1 minus top-2
mean top-k score
score variance
score concentration
```

The point is to estimate:

```text confidence in retrieved evidence
```

rather than simply:

```text confidence in the question
```

---

# 21. Failure-prediction labels

The ground-truth label must come from an evaluation definition.

A possible operational label is:

```text retrieval_sufficient
retrieval_insufficient
```

defined against:

```text benchmark gold evidence
```

or a richer answerability criterion.

Do not create labels from the model's own confidence.

That would create circular supervision.

---

# 22. Avoiding circularity

Bad design:

```text model says:
"I am uncertain"

then

label = uncertain
```

Better:

```text observed retrieval
       ↓
gold evidence comparison
       ↓
actual sufficient / insufficient label
```

This preserves an independent target.

The same principle applies to any future failure detector.

---

# 23. V3 models

Start simple.

Potential order:

```text logistic regression
decision tree
small gradient-boosted model
small MLP
```

Only move to a transformer classifier if simpler models are inadequate.

The objective is not:

```text largest model
```

It is:

```text useful prediction
+
low inference cost
+
interpretable signals
```

---

# 24. V3 metrics

Evaluate:

```text accuracy
precision
recall
F1
AUROC
AUPRC
calibration
```

But also evaluate operational value:

```text escalation rate
avoided strong retrieval calls
false-negative failure rate
false-positive escalation rate
quality after escalation
cost after escalation
```

A failure detector is valuable only if it improves the actual system tradeoff.

---

# 25. Closed-loop adaptive routing

If V3 works, AtlasRAG could evolve from:

```text question
   ↓
route once
   ↓
retrieve
   ↓
answer
```

to:

```text question
   ↓
initial route
   ↓
retrieve
   ↓
verify evidence
   ↓
sufficient?
   ├─ yes → answer
   └─ no  → escalate
                ↓
             stronger retrieval
                ↓
              verify
                ↓
              answer
```

This is substantially closer to a true adaptive retrieval controller.

---

# 26. Selective escalation policy

A future controller could use:

```text predicted failure probability
```

and:

```text escalation cost
```

to choose whether to escalate.

Conceptually:

```text expected loss =
failure_probability × failure_cost
+
escalation_probability × escalation_cost
```

The exact decision rule should only be implemented after the relevant quantities are measured.

Do not assume an arbitrary threshold such as:

```text 0.5
```

is optimal.

---

# 27. Calibration becomes important

If a future model says:

```text failure probability = 0.80
```

that should ideally correspond to roughly:

```text 80% observed failure frequency
```

over appropriate examples.

Therefore measure:

```text reliability curve
ECE
Brier score
```

or an equivalent calibration analysis.

Do not interpret raw softmax confidence as calibrated probability.

---

# 28. Selective-risk evaluation

A particularly useful future analysis is:

```text coverage
vs
risk
```

where:

```text coverage = fraction answered without escalation
```

and:

```text risk = failure/error rate among those answered directly
```

The desired behavior is:

```text more coverage
without
unacceptable quality degradation
```

This creates a more principled view of selective escalation than simply reporting:

```text fallback rate = X%
```

---

# 29. V4 — Benchmark Expansion

A larger benchmark should only be created after the benchmark-generation pipeline is stable.

The goal is not:

```text 27 → 500
```

for its own sake.

The goal is:

```text wider evidence structures
+
better statistical power
+
less label sparsity
```

---

# 30. Why the current benchmark is insufficient for some claims

The current documented benchmark contains:

```text 27 accepted questions
18 sufficient under Oracle-v2
9 insufficient
```

with:

```text SIMPLE       18
MULTI_HOP         7
UNCERTAIN         2
```

This is enough for:

```text exploratory controlled experiments
```

but weak for broad claims about:

```text temporal routing
conflicting evidence
chain questions
general scientific QA
```

because those classes are sparse or absent in the accepted set.

---

# 31. Benchmark V4 target design

A stronger benchmark should aim for:

```text more independent questions
balanced evidence structures
paper-disjoint examples
domain diversity
difficulty diversity
clear support
clear gold provenance
```

Potential structure:

```text SIMPLE
MULTI_HOP
CONFLICTING
TEMPORAL
CHAIN
```

Do not force exact equal counts if the corpus cannot support them honestly.

Quality matters more than symmetry.

---

# 32. Question-source diversity

Avoid generating many questions from the same few papers.

Track:

```text questions per paper
questions per topic
questions per evidence structure
questions per year
```

This helps detect benchmark concentration.

A routing model can otherwise overfit to:

```text recurring paper styles
```

rather than learning retrieval difficulty.

---

# 33. Scientific domain expansion

Once astrophysics/cosmology is stable, possible domains include:

```text particle physics
climate science
materials science
biology
medicine
```

But cross-domain expansion should be treated as a new evaluation regime.

A model trained on one domain should not automatically be presented as domain-general.

---

# 34. Domain-transfer experiment

An interesting future experiment:

```text Train router on astrophysics
        ↓
test on another scientific domain
```

Question:

> Does the routing behavior transfer across scientific literature, or is it tied to domain-specific evidence structures?

This would turn AtlasRAG into a more general research question.

However, this should come only after the within-domain system is stable.

---

# 35. V5 — Better scientific retrieval

If Week 6 identifies retrieval as the main bottleneck, future retrieval work should target the specific failure.

Possible options:

```text stronger embedding model
domain-specific embedding
scientific reranker
equation-aware retrieval
table-aware retrieval
hybrid query rewriting
metadata filtering
section-aware retrieval
```

Choose based on failure evidence.

---

# 36. Equation-aware retrieval

Scientific papers contain information that ordinary text embeddings may handle poorly:

```text equations
symbols
parameter definitions
units
subscripts
Greek notation
```

A future pipeline could preserve:

```text symbol → definition → surrounding explanation
```

instead of treating every equation as ordinary text.

This is potentially important for cosmology questions involving:

```text H0
Ωm
Neff
ξ
w
σ8
```

but should be introduced only after current failures demonstrate a need.

---

# 37. Table-aware retrieval

The existing failure analysis already includes cases where the desired quantity appears in tabular evidence.

Therefore a future extension could represent tables more explicitly.

Conceptually:

```text table
   ↓
row/column structure
   ↓
cell-level metadata
   ↓
queryable representation
```

rather than flattening everything into ordinary text chunks.

A strong table retrieval system could improve:

```text numeric question answering
parameter lookup
model comparison
constraint extraction
```

Again, measure the current bottleneck first.

---

# 38. Section-aware retrieval

Scientific evidence often depends on where it occurs:

```text abstract
introduction
methods
results
discussion
conclusion
appendix
```

A future retriever could incorporate section information.

For example:

```text question about measured result
        ↓
favor Results / Conclusions
```

while:

```text question about methodology
        ↓
favor Methods
```

This could become another routing feature or retrieval feature.

---

# 39. Metadata-aware retrieval

Potential metadata signals:

```text publication date
authors
journal
arXiv category
paper title
citations
```

These are especially relevant for:

```text temporal questions
paper-to-paper comparison
research lineage
```

Metadata should be used only where it is logically relevant.

Do not add metadata ranking globally and assume it helps.

---

# 40. Temporal reasoning extension

Temporal questions were already difficult.

A future temporal pipeline could explicitly model:

```text earlier paper
      ↓
baseline claim
      ↓
later paper
      ↓
updated estimate/result
```

rather than treating temporal questions as generic semantic similarity.

Potential components:

```text date normalization
entity/quantity matching
version filtering
claim extraction
change detection
```

This is a more principled route to solving the temporal benchmark weakness.

---

# 41. Conflict reasoning extension

Conflicting evidence should be treated as:

```text same quantity
+
different result
+
meaningful methodological/source context
```

A future conflict detector could construct:

```text Paper A
   |
quantity = X
value = V1
method = M1

Paper B
   |
quantity = X
value = V2
method = M2
```

Then the answer model can explain:

```text disagreement
+
possible reason
+
source/date/method context
```

rather than simply averaging the values.

---

# 42. Chain reasoning extension

CHAIN questions represent:

```text abstract claim
      ↓
later section
      ↓
supporting evidence
```

The current project found difficulty sourcing strong chain examples.

A future generator should therefore search explicitly for:

```text abstract claim
+
later empirical validation
+
same entity/claim
```

rather than generating generic “according to the abstract, what later section supports this?” questions.

---

# 43. Training-data scaling

The current project context says not to train Compass on an undersized benchmark.

That rule should remain.

Before training a larger router:

```text sufficient labels
+
balanced labels
+
clean support
+
paper-disjoint split
```

must exist.

The model should be the last component added, not the first.

---

# 44. When a larger model is justified

Only move from a lightweight classifier to a larger model if:

```text simple models plateau
```

and:

```text the additional inference cost is acceptable
```

and:

```text the extra capacity improves operational outcomes
```

Measure:

```text quality gain
+
cost gain/loss
+
latency gain/loss
```

not only validation accuracy.

---

# 45. Training strategy for a future Compass V2

A stronger training dataset could contain:

```text question
Oracle strategy
difficulty indicators
evidence-type metadata
```

but the input should be restricted to what would realistically be available at inference time.

Possible future input modes:

```text question-only
question + metadata
question + lightweight retrieval statistics
```

These are distinct models and should be evaluated separately.

---

# 46. Avoid supervision leakage

Do not allow:

```text gold evidence
gold answer
gold route
test metrics
```

to appear directly in a model's inference input.

Gold labels can supervise training.

They must not become hidden inference features.

Likewise, an evaluator's own output should not become the training label without independent validation.

---

# 47. Paper-disjoint evaluation for future models

For scientific QA, paper-disjoint splits are especially important.

Avoid:

```text train question from paper A
test question from paper A
```

when the router can memorize:

```text paper terminology
paper structure
paper vocabulary
```

A stronger evaluation is:

```text train papers
      ≠
test papers
```

This asks whether the router generalizes beyond memorized documents.

---

# 48. Topic-disjoint evaluation

An even stronger extension is:

```text train topic families
      ≠
test topic families
```

For example:

```text train:
Hubble tension / early dark energy

test:
dark matter / gravitational waves
```

This is difficult.

That is exactly why it can be informative once the basic benchmark is large enough.

---

# 49. Domain-shift matrix

A mature AtlasRAG extension could evaluate:

| Train | Test | Question |
|---|---|---|
| same papers | same papers | basic learning |
| different papers | same topic | paper generalization |
| different topics | same domain | topic generalization |
| different domain | different domain | domain transfer |

The final row should be treated as a separate research problem.

---

# 50. Efficiency-oriented research question

A longer-term version can move beyond:

```text accuracy
```

and optimize:

```text quality per unit cost
```

Possible objective:

```text maximize answer quality
subject to
cost ≤ budget
```

or:

```text minimize cost
subject to
quality ≥ threshold
```

This makes adaptive routing an explicit constrained optimization problem.

The exact objective must be chosen before the final experiment.

---

# 51. Regret against Oracle-v2

A useful future routing metric is:

```text regret = cost/quality gap relative to Oracle-v2
```

The precise definition should account for both:

```text retrieval quality
+
strategy cost
```

Example conceptual interpretation:

```text Oracle:
strong enough retrieval at cost 1.0

router:
same-quality strategy at cost 0.6

→ low regret

router:
cheap strategy but loses required evidence

→ high quality regret
```

Do not define regret using arbitrary normalization without documenting it.

---

# 52. The right target for a learned router

Do not optimize:

```text route classification accuracy
```

in isolation.

The actual operational target is:

```text selected strategy
      ↓
retrieval outcome
      ↓
answer outcome
      ↓
cost
```

Therefore future training should eventually evaluate:

```text policy utility
```

not only:

```text classification accuracy
```

---

# 53. Context-aware routing

A future architecture could support two decisions:

```text Pre-retrieval router
        ↓
initial strategy

Post-retrieval verifier
        ↓
continue or escalate
```

This two-stage structure is promising because it separates:

```text expected difficulty
```

from:

```text observed retrieval adequacy
```

It is also easier to diagnose than a single giant end-to-end controller.

---

# 54. Adaptive retrieval budget

Another extension:

```text budget = 1
budget = 2
budget = 3
```

where higher budgets permit:

```text larger candidate depth
stronger reranking
additional query decomposition
additional LLM calls
```

Then the controller chooses:

```text how much retrieval budget to spend
```

rather than simply:

```text one of three routes
```

This can generalize the current routing concept.

---

# 55. Continuous routing instead of discrete routing

Current strategy labels are discrete:

```text SIMPLE
MULTI_HOP
UNCERTAIN
```

A future model could predict:

```text retrieval budget
```

on a continuous scale.

For example:

```text 0.2
0.5
0.8
```

mapping to retrieval effort.

This could avoid abrupt threshold boundaries.

However, it is more difficult to train and evaluate.

It belongs after the discrete-policy system is well understood.

---

# 56. Counterfactual evaluation

A very valuable future analysis is:

> What would have happened if this query had been sent through another strategy?

The existing benchmark already supports an Oracle-style ladder.

A future experiment can exploit this to estimate:

```text cost of over-routing
cost of under-routing
benefit of stronger retrieval
```

for individual questions.

This helps explain router errors:

```text predicted SIMPLE
Oracle preferred STRONG

What did the system lose?
```

versus:

```text predicted MULTI_HOP
Oracle preferred SIMPLE

What extra cost was paid?
```

---

# 57. Per-question policy regret

A useful artifact could store:

```text question
chosen_strategy
oracle_strategy
chosen_recall
oracle_recall
chosen_cost
oracle_cost
quality_gap
cost_gap
```

Then a failure-analysis page can answer:

```text where did the router spend too much?
where did it save money?
where did it lose evidence?
```

This is more informative than route-accuracy counts alone.

---

# 58. Stability as a permanent requirement

Any future extension should preserve the project's stability discipline.

For a major comparison:

```text run A
run B
```

with controlled randomness and a changed cache namespace where fresh LLM calls are needed.

Compare:

```text mean
distribution
ranking
variance
confidence interval
```

Do not report a single lucky result as a new breakthrough.

---

# 59. Provider independence

The AtlasRAG runtime currently uses:

```text Groq-compatible OpenAI API
+
openai/gpt-oss-20b
```

through the project path.

A future provider experiment must be separate from the research baseline.

For example:

```text model_ablation_v1
provider_ablation_v1
```

rather than silently switching the final model.

This matters because remote models can change over time.

---

# 60. Local inference experiment

A future reproducibility extension could replace the remote answer model with a locally hosted model.

Benefits:

```text reproducibility
privacy
less provider throttling
stable availability
```

Costs:

```text GPU/RAM
slower local inference
different answer quality
different model behavior
```

This should be framed as an infrastructure/model ablation, not as a silent replacement.

---

# 61. Reproducibility tiers

A mature project can define:

```text Tier 1
code/config reproducible

Tier 2
local retrieval reproducible

Tier 3
full benchmark reproducible

Tier 4
remote-model answers approximately reproducible
```

Do not claim exact output reproducibility when a remote model is nondeterministic or its backing model can change.

---

# 62. Artifact versioning for V2+

Each new research generation should create distinct artifacts.

Example:

```text
questions_v2.jsonl
questions_v3.jsonl

oracle_v2
oracle_v3

retrieval_ablation_v1
retrieval_ablation_v2

answer_eval_v1
answer_eval_v2
```

Never silently overwrite V1.

The archive should make it possible to reconstruct:

```text what changed
when it changed
why it changed
```

---

# 63. Experimental naming convention

Use names that communicate purpose.

Examples:

```text
R6_finalk_sweep
R7_embedding_ablation
C2_oracle_aligned
D_compass_v1
H1_selective_escalation
V2_evidence_verification
V3_failure_prediction
```

Avoid vague names such as:

```text final2
test_new
experiment_latest
best_run
```

Clear naming becomes increasingly important as the number of experiments grows.

---

# 64. New AI-agent workflow for V2+

Any future agent should follow:

```text
READ MASTER CONTEXT
        ↓
READ LATEST WEEKLY CONTEXT
        ↓
CHECK FINAL V1 STATE
        ↓
IDENTIFY THE MEASURED V1 LIMITATION
        ↓
FORM ONE NEW HYPOTHESIS
        ↓
DEFINE METRIC BEFORE IMPLEMENTATION
        ↓
DEFINE DATA SPLIT
        ↓
DESIGN MINIMAL EXPERIMENT
        ↓
ADD REGRESSION TESTS
        ↓
RUN SMALL PILOT
        ↓
INSPECT FAILURE CASES
        ↓
RUN CONTROLLED EXPERIMENT
        ↓
COMPARE AGAINST V1
        ↓
DECIDE KEEP / REJECT / DEFER
        ↓
COMMIT
        ↓
UPDATE CONTEXT
```

The word:

```text one
```

matters.

Do not allow a future agent to implement five research ideas at once.

---

# 65. Decision gate before any future extension

Before coding, answer:

```text 1. What V1 problem does this solve?

2. Which artifact demonstrates that problem?

3. What hypothesis is being tested?

4. What is the baseline?

5. What is the independent variable?

6. What metric decides success?

7. What data is available at inference time?

8. What could leak gold information?

9. What would a negative result mean?
```

If these cannot be answered, do not start implementation.

---

# 66. Future-extension priority matrix

A useful prioritization framework:

| Extension | Research value | Engineering cost | Data requirement | Priority |
|---|---:|---:|---:|---|
| Evidence verification | High | Medium | Medium | High |
| Failure prediction | High | Medium | Medium | High |
| Benchmark expansion | Very high | High | High | High, when justified |
| Equation-aware retrieval | Medium/High | High | Medium | Conditional |
| Table-aware retrieval | High for numeric QA | Medium/High | Medium | Conditional |
| Temporal reasoning | High | High | High | Conditional |
| Conflict reasoning | High | High | High | Conditional |
| Domain transfer | Very high | Very high | Very high | Later |
| Continuous routing | Medium/High | High | High | Later |
| Kubernetes/deployment complexity | Low research value | High | Low | Low |

This table is a planning aid, not a commitment.

---

# 67. What makes an extension worth doing

Prefer extensions that satisfy at least three conditions:

```text measured V1 limitation
+
clear hypothesis
+
new scientific insight
```

A fourth condition is strongly preferred:

```text practical system improvement
```

For example:

```text V1:
simple question sometimes retrieves wrong evidence

Extension:
post-retrieval failure prediction

Hypothesis:
retrieval score structure predicts failure

Scientific insight:
uncertainty should be estimated from evidence state, not only question text

Practical value:
selective escalation
```

That is a strong extension.

---

# 68. What is merely engineering polish

These can be useful, but should not be treated as research contributions:

```text prettier API
faster startup
better logging
cleaner frontend
Docker optimization
smaller image
better CSS
```

They belong in:

```text engineering maintenance
```

unless they create a measurable research effect.

---

# 69. What is potentially a new research paper

Potential directions with enough scope to become separate studies include:

```text retrieval-state-aware adaptive routing
scientific citation verification
scientific retrieval failure prediction
cross-domain adaptive retrieval
temporal scientific evidence routing
table/equation-aware scientific RAG
```

Do not claim novelty before checking current literature.

When turning an extension into a paper, web research should be performed again because the relevant literature can change.

---

# 70. Literature-review rule for future research

The current context contains prior-art references including:

```text Adaptive-RAG
Self-RAG
FLARE
RouteLLM
RouterBench
RAGRouter-Bench
RAGAS
ARES
LoRA
QLoRA
```

For V2/V3, these references should be revisited and expanded with current literature.

Because new papers and methods can appear after the original context was written, **fresh web research is required before making novelty or state-of-the-art claims**.

Do not rely on the old reference list as a complete literature review.

---

# 71. How to test whether a new idea is actually novel

Use:

```text idea
 ↓
search recent literature
 ↓
identify closest prior method
 ↓
compare task
compare inputs
compare labels
compare architecture
compare evaluation
compare domain
compare objective
 ↓
identify real difference
```

Then state:

```text what is inherited
what is adapted
what is new
```

Do not use:

```text "first ever"
```

unless the literature search genuinely supports it.

---

# 72. Future benchmark quality standard

As the benchmark grows, keep the current principle:

> **Quality before quantity.**

Reject candidates that are:

```text unsupported
ambiguous
redundant
answerable without intended evidence
poorly paired
causally overclaimed
temporally unrelated
numerically incompatible
```

Do not loosen filters just because survivor yield is low.

A difficult but clean benchmark is more useful than a large noisy benchmark.

---

# 73. Gold-evidence limitation remains

Even in V2/V3:

```text exact gold chunk recall
```

remains conservative.

Other passages may provide valid evidence.

A future benchmark could therefore add:

```text acceptable alternative evidence
```

where justified.

This would allow evaluation of:

```text strict gold recall
```

and:

```text broader answerability
```

as separate measurements.

---

# 74. Alternative-evidence annotation

A mature benchmark record could eventually contain:

```text gold evidence
acceptable alternative evidence
required evidence relationship
answerability status
```

Then retrieval evaluation could distinguish:

```text exact recovery
```

from:

```text evidence sufficiency
```

This is particularly useful for scientific literature where the same result may appear:

```text abstract
results
conclusion
review
follow-up paper
```

---

# 75. Human expert evaluation

A later benchmark generation should consider domain-expert review for a subset.

Experts could verify:

```text scientific correctness
source interpretation
numerical correctness
claim support
question validity
temporal meaning
conflict meaning
```

This is expensive.

Therefore a sensible design is:

```text automatic filtering
+
human general review
+
expert audit subset
```

rather than expert review of everything.

---

# 76. Human vs LLM judge agreement

For answer evaluation, a useful future analysis is:

```text human label
vs
LLM judge
```

Measure agreement.

If disagreement is high:

```text judge is not yet reliable enough
```

and should not be treated as ground truth.

This is especially important for:

```text nuanced scientific claims
```

and:

```text partially supported answers
```

---

# 77. Evaluation-model bias

Any LLM-based evaluator may have biases related to:

```text wording
model family
verbosity
citation formatting
scientific familiarity
```

Therefore future evaluation should report:

```text evaluator model
prompt version
judge temperature/parameters
human agreement
```

when practical.

---

# 78. Open-ended answer quality

Exact-match evaluation is often inadequate for scientific QA.

A future mature evaluator can separate:

```text factual correctness
completeness
reasoning quality
grounding
citation correctness
```

This allows a response such as:

```text mostly correct but missing uncertainty
```

to be distinguished from:

```text completely wrong
```

The scoring rubric must be fixed before evaluation.

---

# 79. Scientific uncertainty

Future answer evaluation should explicitly handle uncertainty.

For example:

```text X = 3.1 ± 0.4
```

should not be treated as identical to:

```text X = 3.1
```

and:

```text X ≈ 3.1
```

is different again.

Potential checks:

```text central value
uncertainty
interval
sign
unit
precision
```

This is a strong scientific QA extension if current failure analysis shows such mistakes.

---

# 80. Model-generated citations vs system-generated citations

A future architecture should distinguish:

```text LLM chooses citation
```

from:

```text system inserts verified citation
```

A more reliable pipeline may be:

```text answer claims
      ↓
claim-to-evidence matcher
      ↓
verified citation
      ↓
final answer rendering
```

This could reduce citation hallucination.

But it adds latency.

Therefore evaluate:

```text citation gain
vs
verification cost
```

rather than assuming it is automatically worthwhile.

---

# 81. Research-quality objective for V2/V3

The long-term goal is not:

```text more components
```

It is:

```text better controlled adaptation
```

The architecture may eventually become:

```text Question
    ↓
Pre-retrieval router
    ↓
Initial retrieval
    ↓
Evidence verifier
    ↓
Failure predictor
    ↓
Optional escalation
    ↓
Final evidence
    ↓
Answer
    ↓
Claim/citation verifier
```

Every additional layer should earn its place by improving:

```text quality
cost
latency
robustness
```

or providing an important scientific insight.

---

# 82. Potential V3 research hypothesis

A strong hypothesis is:

> **Retrieval-state-aware escalation can recover some cases missed by question-only routing while adding less cost than always using the strongest retrieval policy.**

This directly builds on the known limitation:

```text question-only routing cannot observe retrieval state
```

The comparison would be:

```text fixed strong retrieval
vs
question-only routing
vs
question-only + retrieval-failure detector
```

This is a clean incremental experiment.

---

# 83. Potential V2 research hypothesis

Another strong hypothesis:

> **Claim-level evidence verification can reduce unsupported or incorrectly cited scientific claims without requiring a stronger answer-generation model.**

Comparison:

```text answer model
vs
answer model + verifier
```

Metrics:

```text answer correctness
groundedness
citation precision
citation completeness
latency
tokens
```

This creates a clean causal test.

---

# 84. Potential benchmark-scaling hypothesis

A third:

> **The routing benefits observed on the curated V1 benchmark persist across a larger, paper-disjoint scientific benchmark and remain concentrated in specific evidence structures.**

Comparison:

```text V1
vs
larger V2 benchmark
```

Metrics:

```text recall
answer quality
Oracle gap
cost
per-class performance
generalization
```

This would substantially strengthen the external validity of the project.

---

# 85. Negative-result interpretation

A future extension can fail and still be valuable.

Example:

```text failure detector predicts retrieval failure accurately
but escalation cost outweighs quality gains
```

Conclusion:

```text prediction is possible
but policy value is insufficient
```

Another:

```text citation verifier improves citation precision
but doubles latency
```

Conclusion:

```text quality improved
but current deployment cost is unattractive
```

These are legitimate engineering/research results.

---

# 86. Future release strategy

AtlasRAG can have explicit generations:

```text AtlasRAG V1
first controlled routing study

AtlasRAG V2
evidence verification

AtlasRAG V3
retrieval-state-aware routing

AtlasRAG V4
benchmark/domain expansion
```

Do not assume every generation becomes a public release.

A generation can remain:

```text research branch
```

if the result is negative or incomplete.

---

# 87. Repository organization for future work

Possible structure:

```text
experiments/
    v1/
    v2/
    v3/

results/
    v1/
    v2/
    v3/

data/
    bench/
        v1/
        v2/
        verification/

docs/
    research/
    reproducibility/
    weekly/
```

Adapt to the existing repository instead of reorganizing everything automatically.

The repository tree should be inspected first.

---

# 88. Branch discipline

For a significant new experiment, use a clear branch.

Examples:

```text
research/v2-evidence-verification
research/v3-failure-prediction
research/v4-benchmark-expansion
```

Keep the V1 release stable.

Do not mix:

```text release cleanup
+
new research
```

inside one giant commit.

---

# 89. Commit discipline for research extensions

A good sequence:

```text
commit 1
schema / test infrastructure

commit 2
implementation

commit 3
pilot fixes

commit 4
final experiment configuration

commit 5
results / report
```

The exact number can vary.

The goal is traceability.

---

# 90. Future experiment manifest

Every extension should save:

```text
experiment_id
hypothesis
baseline
independent_variable
benchmark_version
corpus_version
model
config
seed
metrics
result_path
git_commit
notes
decision
```

This prevents future AI agents from having to reverse-engineer what happened.

---

# 91. Future AI-agent anti-patterns

Never:

```text
reuse V1 test results as V2 results
```

Never:

```text
change labels because training is inconvenient
```

Never:

```text
remove hard questions because the score drops
```

Never:

```text
tune on the final test set
```

Never:

```text
use gold evidence as a hidden feature
```

Never:

```text
declare novelty without literature review
```

Never:

```text
optimize one metric while hiding degraded latency/cost
```

Never:

```text
delete failed experiments
```

Archive them.

---

# 92. Research decision template

At the end of each extension, produce:

```text
Experiment:
    <name>

Question:
    <research question>

Result:
    <measured result>

Compared with:
    <baseline>

What improved:
    <metric>

What worsened:
    <metric>

Main failure:
    <failure>

Interpretation:
    <careful interpretation>

Decision:
    KEEP / REJECT / DEFER

Next justified action:
    <one action>
```

This keeps future development bounded.

---

# 93. When to stop V2/V3 research

Stop a research extension when:

```text hypothesis answered
+
result stable enough
+
failure modes understood
+
cost measured
+
negative result explained
```

Do not keep iterating merely because:

```text another hyperparameter might give +1%
```

unless the scientific question specifically concerns that sensitivity.

---

# 94. Long-term scientific roadmap

The overall research progression can therefore become:

```text
V1
Adaptive retrieval routing
        ↓
V2
Evidence verification
        ↓
V3
Retrieval-state-aware failure prediction
        ↓
V4
Larger / paper-disjoint benchmark
        ↓
V5
Cross-domain generalization
        ↓
V6
Scientific table/equation/temporal reasoning
```

This is a roadmap, not a promise.

Evidence should be allowed to change it.

---

# 95. The strongest long-term research question

A mature AtlasRAG program could ultimately ask:

> **Can a scientific RAG system dynamically allocate retrieval and verification effort according to both predicted query difficulty and observed evidence adequacy, while maintaining answer quality and citation grounding under a measurable compute/API budget?**

That question naturally unifies:

```text routing
retrieval
failure prediction
verification
cost
grounding
```

But it should be treated as a long-term direction, not assumed to be demonstrated by V1.

---

# 96. Week 10 execution order

Do not start by coding.

Use:

```text
STEP 1
Read the final V1 status.

STEP 2
Verify which V1 limitations are actually measured.

STEP 3
Choose exactly one post-V1 research direction.

STEP 4
Perform fresh literature review for that direction.

STEP 5
Identify the closest prior work.

STEP 6
Write one testable hypothesis.

STEP 7
Define the baseline and independent variable.

STEP 8
Define the benchmark split.

STEP 9
Define the metric before implementation.

STEP 10
Inspect repository architecture.

STEP 11
Implement the smallest experiment.

STEP 12
Add regression tests.

STEP 13
Run a tiny pilot.

STEP 14
Inspect failures.

STEP 15
Run the controlled experiment.

STEP 16
Compare against V1.

STEP 17
Write the experiment decision.

STEP 18
Commit and preserve artifacts.

STEP 19
Update the master/future context.

STEP 20
Only then consider the next extension.
```

---

# 97. Commands to begin Week 10

Start from the final repository, not from a memory reconstruction.

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

Inspect branches:

```powershell
git branch -a
```

Inspect experiment/results structure:

```powershell
Get-ChildItem .\results -Recurse -File -ErrorAction SilentlyContinue | Select-Object FullName,Length,LastWriteTime
```

Inspect benchmark structure:

```powershell
Get-ChildItem .\data\bench -Recurse -File -ErrorAction SilentlyContinue | Select-Object FullName,Length,LastWriteTime
```

Inspect configuration:

```powershell
Get-Content .\configs\default.yaml
```

Inspect current router implementations:

```powershell
Get-ChildItem .\src\atlasrag\routers -File | Select-Object Name
```

Inspect evaluation code:

```powershell
Get-ChildItem .\src\atlasrag\bench -Recurse -File | Select-String "metric|evaluate|judge|ground|citation|recall"
```

Do not change the repository until the actual final V1 state has been inspected.

---

# 98. Fresh-literature rule

For any V2/V3 research direction, perform a new literature search before making statements about:

```text novelty
state of the art
best method
first paper
unexplored gap
```

The old project reference list is useful for orientation, but not sufficient evidence of current literature status.

Search should cover:

```text original method
recent follow-up work
competing approaches
benchmark papers
evaluation methodology
```

Then update the research-context file with verified references.

---

# 99. Final Week 10 principle

> **Do not make AtlasRAG bigger. Make the next question sharper.**

The strongest continuation is not:

```text V1 + V2 + V3 + ten new features
```

It is:

```text V1 limitation
      ↓
precise hypothesis
      ↓
minimal new experiment
      ↓
clear result
      ↓
evidence-driven next decision
```

That keeps the project scientifically coherent.

AtlasRAG should remain a sequence of controlled research questions rather than becoming an ever-growing collection of RAG features.
