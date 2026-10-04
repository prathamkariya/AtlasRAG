# AtlasRAG — Week 11: V2 Evidence Verification Implementation & Evaluation

## 1. Purpose

Week 10 defined the post-V1 research directions and identified **evidence verification** as a clean first extension.

Week 11 turns that idea into a controlled experiment.

The narrow question is:

> **Can claim-level evidence verification reduce unsupported or incorrectly cited scientific claims without requiring a stronger answer-generation model?**

The V2 pipeline is:

```text
Question
   ↓
Existing AtlasRAG retrieval/routing
   ↓
Answer generation
   ↓
Claim extraction
   ↓
Citation mapping
   ↓
Evidence verification
   ↓
Verified claims / flagged claims
```

The baseline comparison is:

```text
V1 answer path
vs
V1 answer path + evidence verifier
```

Everything before the verifier should remain as identical as possible.

---

## 2. Freeze V1 first

Before coding V2, establish the exact V1 reference state.

Record:

```text
benchmark version
corpus version
retrieval configuration
routing configuration
answer model
answer prompt
generation parameters
evaluation protocol
git commit
```

Do not modify historical:

```text
Run 1
questions_v1_frozen.jsonl
other frozen benchmarks
```

unless the final repository explicitly identifies a newer authoritative version.

The V2 verification dataset is a new artifact.

---

## 3. Research question

Use:

> Can a claim-level evidence-verification layer improve citation support and reduce unsupported scientific claims while preserving answer quality at acceptable latency and token cost?

This is narrower than:

```text
Can we eliminate hallucinations?
```

Do not make a universal claim from this experiment.

---

## 4. Hypotheses

Primary:

> Adding claim-level evidence verification will improve citation precision and reduce unsupported claims relative to the unverified answer path, with an acceptable increase in compute/API cost.

Secondary hypotheses:

```text
H2:
Many citation failures are local claim/evidence mismatches rather than complete answer failures.

H3:
Verification is especially valuable for numerical, comparative,
temporal, and multi-source claims.

H4:
Some verification errors can be detected with lightweight evidence
matching without requiring a stronger answer-generation model.
```

These are hypotheses, not findings.

---

## 5. Experimental control

The clean design is:

```text
                 SAME INPUTS
                      |
          +-----------+-----------+
          |                       |
          v                       v
       V1 path                V2 path
          |                       |
       answer                  answer
          |                       |
          |                   verifier
          |                       |
          +-----------+-----------+
                      |
                   compare
```

Keep constant where possible:

```text question
retrieved evidence
answer model
answer prompt
generation settings
```

Do not silently give V2 stronger retrieval.

---

## 6. What is being verified?

Do not treat the entire answer as one unit.

Example:

```text
Claim 1:
H0 was measured as X.

Claim 2:
The uncertainty was Y.

Claim 3:
This estimate is higher than method B.

Claim 4:
A later analysis reduced the tension.
```

These claims can require different evidence.

Therefore the primary unit of V2 is:

```text claim
```

rather than:

```text whole answer
```

---

## 7. Claim schema

A conceptual record can contain:

```text
question_id
answer_id
claim_id

question
answer
claim_text

claim_type

citation_ids
evidence_chunk_ids

verification_label
verification_reason
```

Potential claim types:

```text
factual
numeric
comparative
temporal
causal
interpretive
```

Use only categories that can be labeled consistently.

The final schema must be implemented in code and validated.

---

## 8. Citation-to-evidence mapping

The verifier must know which retrieved evidence belongs to each citation.

Conceptually:

```text
C1 → chunk_17
C2 → chunk_22
C3 → chunk_22 + chunk_31
C4 → no supporting evidence
```

Use the application's existing citation representation whenever possible.

Do not invent a second citation system without a real need.

---

## 9. Gold evidence must not leak

For verification inference, the verifier can use:

```text claim
retrieved evidence
citation mapping
```

It must not use:

```text gold chunk IDs
gold answer
Oracle route
hidden benchmark labels
```

Gold evidence is an evaluation reference.

Retrieved evidence is what the deployed system actually has.

These roles must stay separate.

---

## 10. Dataset artifact

Create a new artifact such as:

```text
data/bench/evidence_verification_v1.jsonl
```

following the existing repository naming conventions.

A conceptual record:

```json
{
  "question_id":"...",
  "answer_id":"...",
  "claim_id":"...",
  "claim":"...",
  "citations":["..."],
  "evidence_chunks":["..."],
  "label":"SUPPORTED",
  "reason":"..."
}
```

The real schema should be defined after inspecting the current code.

Do not overwrite the main benchmark.

---

## 11. Labeling workflow

Recommended first workflow:

```text
final V1 answer
      ↓
claim extraction
      ↓
citation mapping
      ↓
automatic pre-filter
      ↓
human review
      ↓
verification label
```

A judge model can assist with:

```text pre-screening
candidate ranking
short explanations
```

but it should not automatically become scientific ground truth.

---

## 12. Verification labels

The Week 10 design suggested:

```text
SUPPORTED
PARTIALLY_SUPPORTED
UNSUPPORTED
NOT_CHECKABLE
```

Possible interpretations:

### SUPPORTED

The cited evidence directly supports the claim.

### PARTIALLY_SUPPORTED

The evidence supports an important part, but the claim also contains missing or unsupported information.

### UNSUPPORTED

The cited evidence does not support the claim.

### NOT_CHECKABLE

The available evidence is insufficient to determine support reliably.

Use a smaller vocabulary if pilot labeling shows that these categories are too ambiguous.

---

## 13. Why partial support matters

Example:

```text
Evidence:
H0 = 73.0 ± 1.0

Answer:
H0 = 73.0 ± 0.2
```

The central value is supported.

The uncertainty is not.

A binary label loses this distinction.

Therefore partial support is potentially important for scientific QA.

---

## 14. Numeric verification

Scientific claims often contain:

```text quantity
value
unit
uncertainty
range
sign
comparison
precision
```

Conceptually parse:

```text
H0 = 73.0 ± 1.0 km/s/Mpc
```

into:

```text
quantity = H0
value = 73.0
uncertainty = 1.0
unit = km/s/Mpc
```

Do not start with a full symbolic-math system.

First measure how often numeric failures actually occur.

---

## 15. Numeric normalization

Potential normalization:

```text whitespace
Unicode symbols
scientific notation
± notation
common unit variants
comma formatting
```

Examples that may represent equivalent numbers:

```text
1e-3
10^-3
0.001
```

Examples of potentially equivalent units:

```text km/s/Mpc
km s^-1 Mpc^-1
```

Every normalization rule needs tests.

---

## 16. Rounding and tolerance

Evidence:

```text 73.04 ± 1.02
```

Answer:

```text 73.0 ± 1.0
```

may be acceptable rounding.

Do not classify every textual mismatch as a scientific error.

If a numeric tolerance is required:

```text define it before final evaluation
```

and do not tune it against individual test examples.

---

## 17. Units are part of correctness

These are not equivalent:

```text 73 km/s/Mpc
```

and:

```text 73 km/s
```

Do not strip units merely to improve string matching.

A verifier must consider:

```text quantity + value + unit
```

when the claim depends on all three.

---

## 18. Comparative claims

Example:

```text Method A gives a lower H0 estimate than Method B.
```

Adequate support may require:

```text value for A
value for B
same quantity
relationship
```

A citation containing only Method A's result may not fully support the comparison.

Comparative claims may therefore require multiple chunks.

---

## 19. Temporal claims

Temporal support requires more than dates.

A useful conceptual structure is:

```text earlier source
      ↓
baseline quantity/claim
      ↓
later source
      ↓
updated quantity/claim
```

A later paper merely mentioning the same quantity does not prove that it changed.

This follows the same discipline used when validating temporal benchmark questions.

---

## 20. Conflict claims

For:

```text Paper A reports X.
Paper B reports Y.
```

verification should establish:

```text same quantity
different value/interpretation
citations cover both sources
```

Two papers being about the same topic is not sufficient evidence of conflict.

---

## 21. Causal claims

Be careful with:

```text correlated with
associated with
possible explanation
```

versus:

```text caused by
demonstrates
establishes
```

Scientific evidence may support the former without supporting the latter.

These can become a useful failure category.

---

## 22. Claim extraction strategies

Possible implementations:

```text sentence splitting
rule-based extraction
LLM extraction
hybrid extraction
```

Start with the simplest method that preserves the necessary claim structure.

A sentence splitter may work for a first pilot.

If a sentence contains several independent claims, a finer extractor may become necessary.

Measure before adding complexity.

---

## 23. Citation mapping strategies

Potential approaches:

```text existing citation markers
nearest citation
answer-span association
LLM extraction
claim/evidence similarity
```

Prefer existing application structure.

If citations are already persisted as:

```text citation_id → retrieved chunk
```

reuse that mapping.

---

## 24. Verifier implementation ladder

Use three possible levels:

### Level 1 — lexical/evidence overlap

Cheap and interpretable.

Weak for paraphrases.

### Level 2 — embedding similarity

Better semantic matching.

Still not equivalent to evidence support.

### Level 3 — LLM entailment judgment

Better for nuanced scientific relationships.

More expensive and potentially less stable.

Do not implement all three blindly.

Use a tiny pilot to decide whether the extra complexity is justified.

---

## 25. Recommended progression

A controlled sequence:

```text
V2-A
cheap overlap baseline

V2-B
embedding verifier

V2-C
LLM support judge
```

Only move to the next level if the previous one fails to satisfy the research objective.

---

## 26. Similarity is not support

Example:

```text Claim:
H0 = 73.2

Evidence:
H0 is an important cosmological parameter.
```

The texts are semantically related.

The numerical claim is still unsupported.

Therefore a verifier cannot rely on similarity alone.

This is why numeric and claim-type checks matter.

---

## 27. LLM verifier prompt

A narrow verifier prompt can conceptually be:

```text
You are checking whether the evidence supports a scientific claim.

Claim:
...

Evidence:
...

Return one label:
SUPPORTED
PARTIALLY_SUPPORTED
UNSUPPORTED
NOT_CHECKABLE

Then provide a short reason.
```

The verifier should not answer the original user question.

It only judges:

```text evidence → claim support
```

---

## 28. Structured output

Prefer machine-readable output:

```json
{
  "label":"SUPPORTED",
  "reason":"The cited passage directly reports the value in the claim."
}
```

Validate the output locally.

Do not assume that a response that looks structured is valid structured data.

If the provider does not reliably support structured outputs, use constrained text and parse it defensively.

---

## 29. Provider failure handling

Preserve the project's bounded retry policy.

Never:

```text retry forever
```

A verifier failure should become an explicit state such as:

```text verifier_unavailable
```

Do not classify:

```text API failure
```

as:

```text UNSUPPORTED
```

These are different failures.

---

## 30. Instrumentation

V2 should preserve separate accounting for:

```text answer-model calls
verifier calls
provider API calls
cache hits
cache misses
retry attempts
prompt tokens
completion tokens
latency
failures
```

The project's previous instrumentation gap around provider calls/retries should be fixed if this can be done without destabilizing the system.

---

## 31. Cost decomposition

V2 total cost conceptually becomes:

```text routing cost
+
retrieval compute
+
answer-generation cost
+
verification cost
```

Always report verification overhead separately.

A useful result is not merely:

```text citation precision +8%
```

but:

```text citation precision +8%
+
latency +X
+
tokens +Y
+
provider calls +Z
```

with actual measured values.

---

## 32. Latency decomposition

At minimum store:

```text answer generation time
verification time
total end-to-end time
```

Where practical:

```text claim extraction time
mapping time
judge time
```

This helps identify the real bottleneck.

---

## 33. Baseline experiment

Minimum clean comparison:

```text B0
V1 answer pipeline

B1
V1 + verifier
```

If several verifier methods are tested:

```text B1
overlap

B2
embedding

B3
LLM judge
```

Keep all upstream components frozen.

---

## 34. Primary metrics

Primary:

```text citation precision
citation completeness
unsupported claim rate
verification precision
verification recall
```

Secondary:

```text answer correctness
groundedness
latency
tokens
provider calls
cost
```

Define the metrics before the final test run.

---

## 35. Claim-level scoring

Suppose:

```text 5 claims
4 supported
1 unsupported
```

Then:

```text claim support rate = 4/5 = 0.80
```

Preserve:

```text per-claim data
```

and:

```text per-question aggregates
```

because claims within one answer are not fully independent.

---

## 36. Citation precision

Conceptually:

```text cited claims with adequate support
---------------------------------------
all cited claims
```

This asks:

> When the system cites evidence, does the cited evidence actually support the attached claim?

This differs from completeness.

---

## 37. Citation completeness

Conceptually:

```text support-required claims with adequate citation
---------------------------------------------------
all support-required claims
```

Not every conversational phrase requires a citation.

Define what counts as:

```text support-required
```

before scoring.

---

## 38. Unsupported-claim rate

Conceptually:

```text unsupported evaluable claims
----------------------------------
all evaluable claims
```

Track separately from answer correctness.

A claim can be:

```text correct but unsupported
```

or:

```text supported but misinterpreted
```

These are not the same failure.

---

## 39. Human-reference subset

Create a manually reviewed subset to establish a reference standard.

The sample should cover:

```text supported
unsupported
partial
numeric
comparative
temporal
multi-source
```

Do not only review easy examples.

---

## 40. Agreement analysis

Compare:

```text automated verifier
vs
human reference
```

Possible measures:

```text raw agreement
confusion matrix
Cohen's kappa
Krippendorff's alpha
```

Choose a method appropriate to the actual number of annotators and labels.

---

## 41. False positives and false negatives

Two important verifier mistakes:

```text false positive:
unsupported claim → verifier says supported
```

This is dangerous.

```text false negative:
supported claim → verifier flags it
```

This can hurt usability.

Report both.

---

## 42. Verification should initially be detection-only

First experiment:

```text Answer
   ↓
Verifier
   ↓
flags
   ↓
report
```

Do not automatically rewrite the answer yet.

This isolates:

```text verifier detection quality
```

from:

```text repair quality
```

---

## 43. Later answer repair

Only after the verifier is understood consider:

```text unsupported claim
      ↓
remove
or
rewrite conservatively
```

This becomes a separate experiment.

Measure:

```text correctness
groundedness
citation quality
unsupported claims
latency
cost
```

Do not let automatic repair hide the verifier's errors.

---

## 44. Verification-guided retrieval

A later extension could be:

```text claim
   ↓
insufficient evidence
   ↓
targeted retrieval
   ↓
new evidence
   ↓
verification
```

This connects V2 with the V3 retrieval-failure prediction work.

It should not be bundled into the first V2 experiment.

---

## 45. Important V1/V2 distinction

V1 asks:

```text Can we adapt retrieval effort?
```

V2 asks:

```text Can we verify whether final claims are supported by retrieved evidence?
```

These are complementary.

The future system could eventually have:

```text pre-retrieval router
        ↓
retrieval
        ↓
evidence adequacy check
        ↓
answer
        ↓
claim/citation verification
```

---

## 46. Retrieval-sufficient vs retrieval-insufficient analysis

Stratify V2 results by:

```text retrieval sufficient
retrieval insufficient
```

Then ask:

```text Does verification still help when evidence is sufficient?

Does verification correctly flag unsupported claims when evidence is insufficient?
```

This separates evidence availability from answer behavior.

---

## 47. Alternative evidence limitation

The exact benchmark gold chunk is not the only possible supporting passage.

Therefore verification should judge:

```text actual claim ↔ actual cited evidence
```

rather than:

```text citation chunk == gold chunk
```

A claim can be correctly grounded in an alternative passage.

This is important for interpreting V2 separately from exact gold-chunk recall.

---

## 48. Scientific reality limitation

Verification establishes:

```text the evidence supports the claim
```

It does not prove:

```text the scientific claim is universally true
```

A source can be:

```text outdated
limited
contested
incorrect
```

The verifier checks support relationship, not ultimate scientific truth.

---

## 49. Temporal freshness limitation

A source may correctly support a historical claim but not the newest estimate.

Example:

```text 2021:
X = 3

2025:
X = 4
```

Then:

```text "X was measured as 3 in 2021"
```

can be supported.

But:

```text "The current estimate of X is 3"
```

may not be.

This is a future temporal-verification concern.

---

## 50. Conflict limitation

A paper can support:

```text Paper A reports X
```

while another paper contradicts it.

Citation support alone does not resolve the scientific disagreement.

A future verifier may therefore need:

```text support
+
contradiction
+
source/date context
```

Do not add this complexity until real V2 data demonstrates that it matters.

---

## 51. V2 pilot size

Do not begin with a huge labeling campaign.

A manageable pilot could be:

```text 50–100 claims
```

or another size supported by the available answer corpus.

Use the pilot to find:

```text schema bugs
label ambiguity
numeric parsing problems
citation mapping errors
judge instability
```

Then scale only if justified.

---

## 52. Pilot sampling

Include a mix:

```text obviously supported
obviously unsupported
partial support
numeric
comparative
temporal
multi-source
```

A stress-test sample helps reveal design flaws quickly.

Once the schema is stable, use a more principled validation/test split.

---

## 53. Pilot acceptance criteria

Do not scale until:

```text citation IDs resolve
claim extraction is inspectable
labels are understandable
numeric normalization passes tests
structured verifier output validates
provider failures are bounded
raw artifacts are saved
```

A larger dataset cannot repair a broken evaluation design.

---

## 54. Tests to add

At minimum, cover behavior equivalent to:

```text claim schema validation
citation resolves to retrieved chunk
missing citation is flagged
numeric normalization
unit mismatch detection
partial-support label validation
structured verifier parsing
bounded provider failure
gold evidence is inaccessible to verifier
```

Use repository-consistent test names.

---

## 55. Provenance

Every verification record should retain:

```text question_id
answer_id
claim_id
citation IDs
evidence chunk IDs
verifier version
verifier model
verifier prompt version
timestamp
```

This makes every judgment traceable.

---

## 56. Raw artifact retention

Keep:

```text raw answer
raw citations
verifier input
raw verifier output
parsed label
reason
```

Do not preserve only:

```text final average score
```

The raw material is required for later diagnosis.

---

## 57. Verifier versioning

Treat verifier changes as experiment changes.

Version:

```text model
prompt
label definitions
parsing rules
numeric tolerance
```

Do not silently replace a verifier and reuse previous scores.

---

## 58. Cache namespaces

Use distinct cache namespaces conceptually such as:

```text answer_eval_v1
verifier_v1
verifier_v2
```

This prevents accidental mixing of outputs generated under different verifier definitions.

Follow the project's existing cache implementation.

---

## 59. Experiment matrix

A clean matrix is:

| System | Retrieval | Answer Model | Verification | Purpose |
|---|---|---|---|---|
| V1 | frozen final | frozen final | none | baseline |
| V2-A | frozen final | frozen final | lightweight | cheap verifier |
| V2-B | frozen final | frozen final | embedding | semantic verifier |
| V2-C | frozen final | frozen final | LLM judge | strong verifier |

Only include rows actually run.

---

## 60. Decision rule

Choose the decision rule before final test evaluation.

For example:

> Select the least expensive verifier that reaches the predefined citation-support target without materially reducing answer correctness.

Or:

> Select the verifier on the practical quality/cost frontier.

Do not choose the rule after seeing the test result.

---

## 61. Statistical analysis

The same questions can be evaluated under multiple conditions.

Preserve paired outcomes.

For binary support outcomes, use an appropriate paired statistical test.

For continuous metrics, preserve per-question/per-claim measurements.

Do not rely only on overall means.

---

## 62. Dependence between claims

Claims from one answer are not necessarily independent.

Do not interpret:

```text 1000 claims
```

as:

```text 1000 independent questions
```

when estimating uncertainty.

Keep:

```text question_id
```

so future analysis can cluster or otherwise account for repeated claims.

---

## 63. Human audit prioritization

After the pilot, prioritize:

```text false positives
false negatives
partial-support cases
numeric mismatches
multi-source errors
temporal errors
```

This reveals where the verifier actually fails.

---

## 64. V2 failure taxonomy

Possible categories:

```text lexical false positive
paraphrase false negative
numeric parsing error
unit normalization error
citation mapping error
multi-source reasoning error
temporal relation error
causal overreach
partial-support blindness
judge inconsistency
provider failure
```

Use only categories supported by actual failures.

---

## 65. What success looks like

A useful V2 result could be:

```text V1:
good citation coverage
but non-trivial unsupported claims

        ↓

V2:
slightly higher latency
lower unsupported-claim rate
higher citation precision
similar answer correctness
```

This would be meaningful even if retrieval never changed.

---

## 66. What a negative result looks like

Examples:

```text verifier improves precision
but rejects too many valid citations
```

Interpretation:

```text verifier is over-conservative
```

or:

```text verifier is accurate
but too expensive
```

Interpretation:

```text technically useful
but poor deployment tradeoff
```

or:

```text cheap verifier ≈ expensive LLM verifier
```

Interpretation:

```text stronger judgment model may not be necessary
```

All are legitimate research outcomes.

---

## 67. V2 stop conditions

Stop the first V2 iteration when:

```text schema stable
pilot complete
baseline recorded
at least one verifier tested
main failure modes understood
cost measured
latency measured
decision recorded
```

Do not automatically move to verification-guided retrieval after that.

---

## 68. V2 result package

A possible result layout:

```text
results/
    v2_evidence_verification/
        raw_claims.jsonl
        baseline.jsonl
        verifier_v1.jsonl
        verifier_v2.jsonl
        verifier_v3.jsonl
        summary.json
        config.json
        manifest.json
        failure_analysis.json
```

Adapt to the current repository.

The principle is:

```text raw data
≠
derived summary
```

---

## 69. V2 manifest

Record:

```text
experiment_id
benchmark_version
corpus_version
answer_model
answer_prompt
retrieval_config
verifier_model
verifier_prompt
verifier_version
claim schema version
label definitions
numeric tolerance
seed
cache namespace
git commit
timestamp
```

This becomes the reproducibility source of truth.

---

## 70. Final V2 comparison table

Use a generated table such as:

| System | Citation Precision | Citation Completeness | Unsupported Claims | Answer Correctness | p50 Latency | Tokens/Query | Provider Calls |
|---|---:|---:|---:|---:|---:|---:|---:|
| V1 | | | | | | | |
| V2-A | | | | | | | |
| V2-B | | | | | | | |
| V2-C | | | | | | | |

Use:

```text
—
```

for unavailable metrics.

Never estimate missing values.

---

## 71. Final V2 failure table

Generate something like:

| Failure | Count | Example | Likely Cause | Candidate Fix |
|---|---:|---|---|---|
| Unsupported claim missed | | | | |
| Valid claim rejected | | | | |
| Numeric mismatch | | | | |
| Unit error | | | | |
| Partial support misclassified | | | | |
| Citation mapping error | | | | |
| Multi-source failure | | | | |
| Provider failure | | | | |

Counts must come from saved artifacts.

---

## 72. V2 completion checklist

```text
[ ] V1 baseline frozen
[ ] verification dataset created
[ ] schema validated
[ ] claim extraction inspected
[ ] citation mapping tested
[ ] verifier implemented
[ ] outputs validated
[ ] bounded provider failures handled
[ ] raw results saved
[ ] human reference subset labeled
[ ] primary metrics computed
[ ] paired comparison computed
[ ] cost measured
[ ] latency measured
[ ] failure taxonomy completed
[ ] limitations documented
[ ] V2 decision recorded
```

---

## 73. V2 decision

At the end choose exactly one:

```text
KEEP
REJECT
DEFER
```

### KEEP

The verifier provides enough measurable value.

### REJECT

The verifier does not justify its complexity/cost.

### DEFER

The idea is promising but current evidence is insufficient.

Never force a positive result.

---

# 74. Week 11 execution order

Follow:

```text
STEP 1
Inspect final V1 repository state.

STEP 2
Find the existing answer/citation data structures.

STEP 3
Confirm authoritative benchmark and frozen configuration.

STEP 4
Design claim/evidence schema.

STEP 5
Add schema tests.

STEP 6
Implement claim extraction.

STEP 7
Implement citation-to-evidence mapping.

STEP 8
Create tiny labeled pilot.

STEP 9
Inspect label ambiguity.

STEP 10
Implement simplest verifier.

STEP 11
Run verifier on pilot.

STEP 12
Inspect false positives/false negatives.

STEP 13
Only if justified, add stronger verifier.

STEP 14
Freeze verifier configuration.

STEP 15
Create validation/test split.

STEP 16
Run controlled V2 experiment.

STEP 17
Persist raw results.

STEP 18
Run paired statistics.

STEP 19
Perform targeted human audit.

STEP 20
Write V2 decision.

STEP 21
Commit the extension separately from V1 release code.

STEP 22
Update project context.
```

---

# 75. Commands to begin Week 11

Start:

```powershell
$env:PYTHONPATH="src"
```

Then:

```powershell
git status
git log --oneline --decorate -15
python -m pytest -q
```

Inspect the pipeline:

```powershell
Get-Content .\srctlasrag\pipeline.py
```

Inspect LLM handling:

```powershell
Get-Content .\srctlasrag\llm.py
```

Inspect benchmark/evaluation files:

```powershell
Get-ChildItem .\srctlasragench -Recurse -File | Select-Object FullName
```

Search for answers/citations/evidence:

```powershell
Get-ChildItem .\srctlasrag -Recurse -File | Select-String "citation|source|answer|retrieved|context"
```

Inspect scripts:

```powershell
Get-ChildItem .\scripts -File | Select-Object Name
```

Inspect tests:

```powershell
Get-ChildItem .	ests -Recurse -File | Select-Object FullName
```

Do not write V2 implementation files until the actual answer/citation path has been inspected.

---

# 76. Final Week 11 principle

> **Verify the evidence that actually reaches the answer, not the evidence you wish the system had retrieved.**

The first V2 milestone is not:

```text build a sophisticated verifier
```

It is:

```text make the claim → citation → retrieved evidence relationship observable
```

Once that relationship is measurable, AtlasRAG can ask a deeper question:

```text Does adaptive retrieval produce not only enough evidence,
but evidence that remains correctly attributable in the final answer?
```

This gives the next research sequence:

```text V1
adaptive retrieval

V2
evidence verification

V3
retrieval-failure prediction

V4
larger scientific benchmark

V5
cross-domain generalization
```

Each generation should answer one sharper question while preserving the evidence from earlier generations.
