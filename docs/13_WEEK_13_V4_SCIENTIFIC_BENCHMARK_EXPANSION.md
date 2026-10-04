# AtlasRAG — Week 13: V4 Scientific Benchmark Expansion & Generalization

## 1. Purpose

Weeks 11 and 12 defined two research extensions:

```text
V2
evidence verification

V3
retrieval-failure prediction
```

Both depend on a stronger evaluation foundation.

The current benchmark is useful for controlled exploration, but it is still small and has sparse difficult evidence structures.

Week 13 therefore defines:

> **How to build a larger, cleaner, more diverse scientific QA benchmark without sacrificing the strict evidence standards that made the original benchmark useful.**

The goal is not:

```text
27 questions
→
500 questions
```

just to obtain a larger number.

The goal is:

```text
better statistical power
+
better evidence diversity
+
paper-disjoint evaluation
+
less class sparsity
+
stronger generalization claims
```

The resulting benchmark becomes a new research artifact.

It must never silently replace the V1 benchmark.

---

# 2. Why benchmark expansion is now justified

The original benchmark history was:

```text
94 generated candidates
27 accepted
67 rejected
```

The accepted set currently contains:

```text
27 questions
```

with Oracle-v2 behavior:

```text
18 sufficient
9 insufficient
```

and Oracle-v2 strategy labels:

```text
SIMPLE       18
MULTI_HOP     7
UNCERTAIN     2
```

The original intended evidence structures were:

```text
SIMPLE
MULTI_HOP
CONFLICTING
TEMPORAL
CHAIN
```

but the accepted benchmark does not provide balanced coverage of all of them.

This limits claims about:

```text temporal reasoning
conflict handling
chain reasoning
general routing behavior
```

Therefore the next benchmark should improve coverage without weakening validation.

---

# 3. The benchmark is part of the research contribution

AtlasRAG is not merely evaluating on an arbitrary QA set.

The benchmark itself encodes:

```text scientific evidence structure
+
retrieval difficulty
+
required passage relationships
+
routing requirements
```

A weak benchmark can make a strong routing system appear strong.

A strong benchmark can expose:

```text routing failures
retrieval failures
decomposition failures
generation failures
citation failures
```

Therefore benchmark construction must be treated as a first-class experimental artifact.

---

# 4. V4 research question

Primary benchmark question:

> **Do the routing and retrieval behaviors observed on the curated V1 benchmark persist across a larger, paper-disjoint scientific benchmark with broader evidence structures?**

Secondary questions:

```text 1. Does Oracle-v2 show a stable strategy distribution?

2. Are multi-hop questions systematically more retrieval-intensive?

3. Are temporal/conflicting questions qualitatively different?

4. Does question-only routing generalize to unseen papers?

5. Do retrieval-state failure signals generalize across documents?

6. Are observed gains concentrated in a small subset of scientific structures?
```

These are research questions.

The benchmark itself should not be designed to produce a desired answer.

---

# 5. Preserve V1

The first rule:

```text V1 stays frozen.
```

Keep:

```text data/bench/questions.jsonl
data/bench/questions_v1_frozen.jsonl
```

or the actual equivalent final V1 benchmark.

The new benchmark should have an explicit version.

For example:

```text data/bench/questions_v4.jsonl
```

or:

```text data/bench/v4/questions.jsonl
```

depending on repository conventions.

Never write the new benchmark over V1.

---

# 6. Benchmark version semantics

Every benchmark version should have a short description.

Example:

```text V1
original manually accepted benchmark

V2
repaired/generated benchmark after support and pairing improvements

V4
expanded paper-disjoint scientific benchmark
```

The exact version names should match actual repository history.

Do not invent a V2 benchmark merely because the roadmap mentions one.

The versioning system must reflect real artifacts.

---

# 7. What the benchmark should measure

A mature benchmark should contain questions requiring different evidence behaviors:

```text direct factual retrieval
multi-passage synthesis
scientific comparison
temporal change
conflicting evidence
abstract-to-results chains
numerical constraints
parameter interpretation
```

However:

```text question complexity
```

must not be confused with:

```text retrieval difficulty.
```

A simple-looking question can be hard to retrieve.

A long-looking question can still be answered from one obvious passage.

The benchmark should annotate both where practical.

---

# 8. Question metadata

A useful benchmark record should eventually contain fields such as:

```text question_id
question_type
question_text

gold_evidence_ids

reference_answer

source_paper_ids

required_passage_count

requires_joint_reasoning

scientific_quantity

model/entity identifiers

publication dates

difficulty notes
```

The exact schema should be based on the repository's current `bench/schema.py` and related structures.

Do not introduce duplicate incompatible schemas.

---

# 9. Evidence-type taxonomy

At benchmark level, retain:

```text SIMPLE
MULTI_HOP
CONFLICTING
TEMPORAL
CHAIN
```

Then optionally annotate orthogonal properties:

```text numeric
equation-related
table-derived
parameter constraint
model comparison
method comparison
uncertainty-sensitive
```

These secondary properties may overlap.

For example:

```text MULTI_HOP
+
numeric
+
parameter constraint
```

This is more informative than forcing each question into one category only.

---

# 10. SIMPLE questions

Definition:

```text one evidence-bearing passage
→ enough information
→ answer
```

Validation requirements:

```text passage directly contains the necessary information
answer is supported
no second passage is required for the intended answer
```

Reject:

```text question asks for information absent from the passage
```

and:

```text answer needs outside knowledge that is not represented in the evidence
```

---

# 11. MULTI_HOP questions

Definition:

```text Passage A
+
Passage B
→
joint reasoning
→
answer
```

Both passages must contribute substantive information.

A valid example structure:

```text A provides measurement X
B provides relationship/model Y
question asks for implication of X under Y
```

Invalid:

```text A already answers everything
B is merely related
```

The benchmark validator should explicitly test:

```text both passages contribute
```

---

# 12. CONFLICTING questions

A genuine conflict requires:

```text same quantity / claim
+
different values / conclusions
+
meaningful scientific tension
```

Do not treat:

```text different quantities
```

as conflict.

Do not treat:

```text different assumptions
```

as conflict unless the resulting claim actually creates a meaningful disagreement relevant to the question.

A valid conflict question might be:

```text Paper A estimates X = value A.
Paper B estimates X = value B.
What is the disagreement?
```

with both values and context supported.

---

# 13. TEMPORAL questions

A valid temporal pair needs:

```text earlier paper
+
later paper
+
same scientific quantity/claim
+
meaningful update/change
```

The later paper must actually revise, refine, challenge, or materially extend the earlier evidence.

Reject:

```text same topic
but different claim
```

Reject:

```text later mention
without an actual change
```

The temporal relation must be evidence-bearing.

---

# 14. CHAIN questions

A chain question should follow:

```text Abstract
   ↓
claim
   ↓
later section
   ↓
method/result/evidence
```

The later section must add substantive information.

Reject:

```text answer already directly stated in abstract
```

because that destroys the intended chain requirement.

The current project has already encountered this failure mode.

---

# 15. Benchmark generation pipeline

A strong V4 process is:

```text paper selection
      ↓
evidence discovery
      ↓
candidate construction
      ↓
structural validation
      ↓
support audit
      ↓
retrieval sanity check
      ↓
manual scientific review
      ↓
accepted benchmark
```

Generation is only the first stage.

---

# 16. Paper selection first

Do not generate questions before deciding which papers should contribute.

Construct a paper pool with diversity across:

```text publication year
topic
model family
observational/theoretical emphasis
paper length
source density
```

The exact metadata available in the corpus should determine the final filtering.

The purpose is to prevent:

```text many questions
from the same small subset of papers.
```

---

# 17. Questions-per-paper constraint

Track:

```text questions per paper
```

A paper should not dominate the benchmark.

For example, avoid a benchmark where:

```text 50 questions
```

come from:

```text 3 papers
```

even if all 50 are technically valid.

The exact maximum should be decided after inspecting the corpus size and desired benchmark size.

---

# 18. Topic diversity

Track:

```text topic family
```

where the corpus permits.

Possible astrophysics/cosmology categories:

```text Hubble tension
dark matter
dark energy
early-universe cosmology
CMB
BAO
supernovae
gravitational waves
parameter constraints
modified gravity
```

These are examples.

Use actual topic coverage from the indexed corpus.

Do not fabricate topic labels without examining the papers.

---

# 19. Temporal diversity

For temporal questions, ensure:

```text meaningful publication ordering
```

and preferably:

```text multiple years
```

rather than relying on a single tightly clustered pair.

This helps test whether the temporal reasoning procedure is genuinely robust.

---

# 20. Source-pair selection

For multi-hop, conflict, and temporal questions, pair selection is critical.

The repository's previous deterministic pair sourcing already introduced:

```text dense + BM25 candidate pools
scientific signal extraction
anchor matching
duplicate penalties
temporal gates
chain ranking
```

Future benchmark expansion should build on those mechanisms.

Do not revert to naive:

```text top semantic neighbors
```

pairing.

---

# 21. Pair quality requirements

A candidate pair should have:

```text shared scientific signal
+
shared precise anchor
+
non-generic overlap
+
substantive evidence sections
```

Potential precise anchors:

```text acronym
parameter
model symbol
observable identifier
```

The exact implementation can follow the current generator.

---

# 22. Multi-hop pair independence

For multi-hop:

```text Passage A contribution
```

and:

```text Passage B contribution
```

must both be necessary for the intended answer.

One useful validation approach is:

```text remove A
→ answer becomes incomplete

remove B
→ answer becomes incomplete
```

This is stronger than merely asking an LLM whether both passages are “relevant.”

---

# 23. Temporal pair validation

For a temporal pair:

```text earlier paper
later paper
```

check:

```text same quantity
same object/model family where applicable
same scientific context
date order
change/update cue
```

Potential update cues:

```text improved constraint
new estimate
revised bound
tension reduced/increased
new dataset
follow-up analysis
```

Use only actual evidence.

---

# 24. Conflict-pair validation

For a conflict pair:

```text quantity must match
```

and:

```text results must meaningfully differ.
```

Avoid:

```text A says X under assumption A
B says Y about a different parameter
```

and then labeling the pair:

```text conflict.
```

The validator should inspect quantity compatibility.

---

# 25. Chain validation

For a chain:

```text abstract claim
```

must connect to:

```text later section evidence.
```

Validate:

```text same entity/claim
concrete scientific overlap
later section actually advances the claim
abstract alone insufficient
```

The current `chain` sourcing work should remain the foundation.

---

# 26. Reference-answer standard

Every accepted question needs a reference answer that is:

```text concise
scientifically accurate
directly supported
appropriately qualified
```

Reject references that:

```text overgeneralize
add unsupported causal claims
omit required uncertainty
combine incompatible quantities
```

The project has already encountered these failure modes.

They should become explicit benchmark quality checks.

---

# 27. Reference-answer wording

Prefer:

```text "The paper reports X = ... under assumption Y."
```

over:

```text "This proves X is universally ..."
```

unless the evidence genuinely supports the stronger claim.

The reference answer defines what the benchmark expects.

It must therefore be more conservative than an ordinary generated answer.

---

# 28. Scientific precision

For quantitative questions preserve:

```text central value
uncertainty
unit
sign
range
precision
```

Do not reduce:

```text 3.1 ± 0.4
```

to:

```text around 3
```

when the uncertainty is scientifically important.

Conversely, do not demand unrealistic decimal precision when the source does not provide it.

---

# 29. Alternative evidence

V4 should consider adding:

```text primary gold evidence
+
acceptable alternative evidence
```

where justified.

This addresses the known limitation:

```text exact gold-chunk recall
```

can be conservative.

A valid benchmark should not punish a system merely because it retrieves another passage that independently supports the answer.

---

# 30. Evidence requirements

For each question, define:

```text required evidence
```

rather than assuming the entire gold set is equally important.

Example:

```text required:
value in Table 2

optional:
context from Discussion
```

This allows future retrieval evaluation to distinguish:

```text necessary evidence
```

from:

```text helpful context.
```

Do not add this complexity unless the annotation effort is manageable.

---

# 31. Evidence sufficiency vs exact retrieval

V4 can support two metrics:

```text exact gold recovery
```

and:

```text evidence sufficiency
```

The first is mechanically defined.

The second asks:

```text Is the retrieved context enough to answer correctly?
```

The second may require human judgment.

Keep them separate.

---

# 32. Benchmark splits

A mature V4 benchmark should use:

```text train
validation
test
```

when used for learned models.

The most important rule:

```text paper-disjoint
```

between splits.

Potentially:

```text train papers
validation papers
test papers
```

This prevents memorization of document-specific vocabulary.

---

# 33. Why paper-disjoint matters

A router may learn:

```text this phrase usually appears in paper X
```

rather than:

```text this question needs multi-hop evidence.
```

Paper-disjoint evaluation tests whether the behavior generalizes to unseen documents.

This is especially important for:

```text retrieval-failure prediction
```

and:

```text learned routing.
```

---

# 34. Topic-aware splits

A stronger extension can also evaluate:

```text same-domain generalization
```

by keeping:

```text domain = astrophysics/cosmology
```

while separating:

```text topic families.
```

This is harder and should be considered an additional experiment, not the default requirement.

---

# 35. Train/validation/test design

A useful progression:

```text basic:
paper-disjoint

stronger:
paper + topic-aware

hardest:
domain-disjoint
```

Do not jump to the hardest split before the dataset can support it.

---

# 36. Class balance

The current V1 benchmark is heavily:

```text SIMPLE
```

with only:

```text 7 MULTI_HOP
2 UNCERTAIN
```

and no sufficiently populated:

```text CONFLICTING
TEMPORAL
CHAIN
```

classes in the accepted Oracle-v2 distribution.

V4 should improve this.

But:

```text equal class counts
```

are not mandatory.

Natural prevalence is acceptable if the report clearly states it.

---

# 37. Balanced vs realistic benchmark

Two useful benchmark modes:

### Controlled balanced set

Useful for:

```text per-class comparison
```

### Realistic distribution set

Useful for:

```text practical overall performance
```

A future mature benchmark could contain both.

Do not mix them without labeling the evaluation regime.

---

# 38. Hard-example budget

Do not make every V4 question maximally difficult.

A useful distribution may include:

```text easy
moderate
hard
```

because a practical router must function across the whole difficulty spectrum.

Difficulty should be based on:

```text evidence structure
retrieval behavior
reasoning requirement
```

not merely question length.

---

# 39. Difficulty annotation

Potential fields:

```text retrieval difficulty
reasoning hops
source count
numeric complexity
temporal dependence
conflict dependence
```

These can support future stratified analysis.

Do not assign subjective scores without a reproducible rubric.

---

# 40. Leakage checks

Benchmark questions should not:

```text copy distinctive source sentences
```

or:

```text reveal the answer through wording.
```

The project already rejects candidates that echo source wording.

Maintain this requirement for V4.

A useful automatic similarity check can flag suspicious overlap for human review.

---

# 41. Answerability sanity check

Before acceptance, ask:

```text Can a knowledgeable reviewer answer this
using only the intended evidence?
```

Then:

```text Is the reference answer fully supported?
```

Then:

```text Is the question still meaningful
without hidden gold context?
```

These should all pass.

---

# 42. Retrieval sanity check

A benchmark can be valid but still impossible for the current index because:

```text chunking
```

or:

```text indexing
```

loses the critical content.

Therefore run a retrieval sanity check.

But do not remove a valid hard question merely because baseline retrieval misses it.

The point is to distinguish:

```text valid hard example
```

from:

```text inaccessible due to data corruption.
```

---

# 43. Corpus integrity

Before V4 generation:

```text verify PDF parsing
verify metadata
verify paper IDs
verify publication dates
verify chunk mappings
verify index completeness
```

An indexing bug can contaminate every benchmark conclusion.

---

# 44. Duplicate-question detection

V4 must detect:

```text same question phrased differently
```

and:

```text same evidence/answer pattern
```

across papers where relevant.

Near duplicates can artificially inflate performance.

Potential checks:

```text lexical similarity
semantic similarity
same answer entity/value
same gold evidence
```

Use these as filters, then human review borderline cases.

---

# 45. Duplicate-paper leakage

Even without duplicate questions, two papers can contain the same result copied or reproduced.

For paper-disjoint routing evaluation, track:

```text source relationship
```

when possible.

If a test paper directly reproduces a training-paper result, that may weaken the intended generalization experiment.

This should be documented if it cannot be avoided.

---

# 46. Benchmark version manifest

Every V4 benchmark should have a manifest containing:

```text benchmark_version
creation_date
corpus_version
paper_list
question_count
question_type_counts
split_definition
validation_rules
generator_version
review_process
acceptance_count
rejection_count
hashes
```

The benchmark becomes a reproducible object.

---

# 47. Candidate audit trail

Keep:

```text candidate
validation outcome
human decision
rejection reason
final question
```

Do not delete rejected candidates.

They are useful for understanding:

```text where the generator fails.
```

This mirrors the existing project practice.

---

# 48. Rejection taxonomy

Potential categories:

```text unsupported
ambiguous
source-wording echo
insufficient evidence
not truly multi-hop
not truly conflicting
not truly temporal
chain answerable from abstract
quantity mismatch
duplicate
weak reference answer
metadata error
```

Use actual repository terminology where available.

---

# 49. Why rejected candidates matter

A low survivor rate can reveal:

```text benchmark-generation bottleneck
```

rather than:

```text bad generator
```

For example, if temporal questions repeatedly fail because suitable paper pairs are rare, the problem may be:

```text corpus source availability
```

rather than prompt quality.

Record rejection reasons to distinguish these possibilities.

---

# 50. Generation diagnostics

Track:

```text candidates attempted
accepted
rejected
attempts per accepted candidate
LLM calls
provider calls
tokens
rate-limit failures
cache hits
```

The project previously lacked some of this instrumentation.

V4 should persist it from the beginning.

---

# 51. Provider-budget discipline

Large benchmark generation can consume a substantial number of API calls.

Therefore:

```text cache aggressively
generate incrementally
pilot small batches
persist partial outputs
stop after provider failure thresholds
```

Do not rerun identical generation prompts unnecessarily.

---

# 52. Bounded generation retries

Retain bounded behavior:

```text provider error
→ finite retries
→ explicit failure
```

Never allow:

```text infinite candidate-generation loop
```

A failed generation batch should be resumable.

---

# 53. V4 pilot

Before full expansion, run a small pilot covering:

```text SIMPLE
MULTI_HOP
CONFLICTING
TEMPORAL
CHAIN
```

where source material exists.

The pilot should answer:

```text Can the new generator/source-pairing rules produce valid candidates?

Which classes remain bottlenecks?

Which validators fail?

How much human review is required?
```

---

# 54. Pilot size

Use a manageable number such as:

```text 5–10 accepted targets per class
```

where feasible.

The exact target depends on the corpus.

The purpose is not statistical power.

It is pipeline validation.

---

# 55. Pilot acceptance criteria

Do not scale until:

```text questions are supportable
pairing is structurally sound
reference answers are precise
question types are correctly assigned
duplicates are controlled
metadata is correct
review burden is manageable
```

If the pilot fails, fix the generator before scaling.

---

# 56. Human review remains final

The automatic validator should remain:

```text filter
```

not:

```text truth oracle.
```

The final benchmark requires human review of accepted candidates.

This is especially important for:

```text conflict
temporal
causal
comparative
chain
```

questions.

---

# 57. Human reviewer rubric

Each candidate can be reviewed with:

```text 1. Is the question unambiguous?

2. Is the intended evidence sufficient?

3. Are all required passages genuinely needed?

4. Does the reference answer match the evidence?

5. Is the scientific wording appropriately qualified?

6. Is the question free from source-wording leakage?

7. Is the assigned question type correct?

8. Is the example non-duplicate?
```

Use a compact review form so decisions remain consistent.

---

# 58. Reviewer agreement

If multiple reviewers are available, measure agreement on a subset.

Potential outputs:

```text raw agreement
disagreement count
adjudicated decisions
```

For larger annotation efforts, a formal agreement statistic can be added.

The goal is to identify:

```text ambiguous rubric
```

before scaling.

---

# 59. V4 quality gate

A question should enter the final benchmark only if:

```text structural validation passes
+
support audit passes
+
manual review passes
```

For difficult types, require:

```text relevant multi-passage checks
```

as appropriate.

---

# 60. Benchmark generation model

If using an LLM to generate candidates, the LLM should not be treated as:

```text benchmark truth
```

It is a:

```text candidate generator
```

The actual benchmark truth comes from:

```text source evidence
+
validation
+
human review
```

This principle should be stated explicitly in any report.

---

# 61. Avoid benchmark gaming

Do not optimize generation prompts solely to maximize:

```text acceptance rate.
```

An increased acceptance rate can be achieved by generating easier or less interesting questions.

Instead optimize:

```text accepted-question quality
+
structural validity
+
diversity
+
evidence clarity.
```

---

# 62. Benchmark statistics after expansion

Final reporting should include:

```text total papers
total questions
questions per paper
questions per type
questions per topic
train/validation/test counts
sufficient/insufficient counts
numeric-question count
multi-source count
temporal count
conflict count
chain count
```

This creates a transparent benchmark description.

---

# 63. Oracle-v2 re-labeling

Changing the benchmark means re-running Oracle-v2.

Do not reuse V1 labels.

For V4:

```text new questions
+
new retrieval results
+
new Oracle-v2 labels
```

The Oracle distribution itself is a result.

Do not manually rebalance labels by changing Oracle decisions.

---

# 64. Oracle stability

After V4 generation, compare:

```text V1 Oracle distribution
vs
V4 Oracle distribution
```

Ask:

```text Does the original pattern persist?

Did SIMPLE become dominant only because V1 was biased?

Are difficult classes genuinely harder?

How many questions are retrieval-insufficient?
```

These are valuable scientific observations.

---

# 65. Re-evaluate retrieval sufficiency

The current V1 had:

```text 9 / 27 insufficient
```

under the tested strategy ladder.

A larger benchmark may reveal:

```text more insufficiency
```

or:

```text less insufficiency
```

Both are informative.

Do not force the benchmark to become more “solvable.”

---

# 66. Benchmark contamination with routing labels

Oracle labels are derived from retrieval outcomes.

Therefore:

```text benchmark
→ retrieval
→ Oracle
```

creates labels specific to:

```text retrieval configuration
```

If V4 changes:

```text embedding
reranker
chunking
candidate depth
```

then Oracle labels may change.

This is expected.

The benchmark and retrieval configuration must therefore be versioned jointly in experiments.

---

# 67. V4 routing evaluation

Once the benchmark is accepted:

```text B
C1
C2
D/Compass if available
E2
```

should be re-evaluated according to actual final availability.

The new benchmark should not be used to rewrite V1 results.

Compare:

```text V1
vs
V4
```

as separate benchmark regimes.

---

# 68. Generalization question

The most useful V4 test is:

```text train on V4 training papers
test on unseen test papers
```

This asks:

> Does the router learn routing behavior rather than memorizing source vocabulary?

This is likely more meaningful than simply increasing the number of questions.

---

# 69. V3 failure detector on V4

If V3 exists, evaluate it on V4 without changing the test set based on failures.

Potential analysis:

```text train detector on training papers
validate threshold
test on unseen test papers
```

Then report:

```text failure recall
precision
calibration
escalation rate
cost
quality
```

This tests whether retrieval-state signals generalize.

---

# 70. V2 evidence verification on V4

Likewise, V2 can use V4 answers as a new distribution.

This enables:

```text verifier trained/validated on prior data
→ tested on unseen scientific papers
```

This is much stronger than evaluating verification only on the original 27 questions.

---

# 71. Avoid benchmark reuse across roles

If the same questions are used to:

```text tune router
tune verifier
select threshold
select answer prompt
```

then the final test result becomes contaminated.

Define roles:

```text train
validation/development
test
```

before experimenting.

---

# 72. Multiple test regimes

A strong final evaluation can contain:

```text V1 frozen historical test
V4 development test
V4 final held-out test
```

The original V1 test remains useful as a historical reference.

The new V4 test is the current generalization benchmark.

Do not merge them into one score without justification.

---

# 73. Benchmark growth strategy

Grow in stages:

```text pilot
   ↓
small expansion
   ↓
audit
   ↓
larger expansion
   ↓
final freeze
```

Do not generate the final benchmark in one huge uncontrolled run.

This creates checkpoints for debugging.

---

# 74. Benchmark stop rule

Stop expanding when:

```text sufficient sample size for intended claims
+
acceptable class coverage
+
paper diversity
+
review quality
+
stable validator
```

There is no universal magic number.

The appropriate size depends on:

```text hypothesis
model complexity
class balance
expected effect size
annotation budget
```

---

# 75. Benchmark size and statistical power

The reason for expansion should be:

```text tighter uncertainty
```

not:

```text bigger screenshot number
```

A larger benchmark is useful when it allows:

```text more stable effect estimates
better subgroup analysis
stronger generalization
```

If the planned model still cannot be evaluated fairly with the available examples, document the limitation rather than pretending the sample is sufficient.

---

# 76. V4 error analysis

Repeat the earlier taxonomy:

```text benchmark error
retrieval failure
routing failure
query-decomposition failure
generation failure
citation failure
infrastructure failure
```

Then compare the distribution between:

```text V1
V4
```

This can reveal whether benchmark scaling exposes new failure modes.

---

# 77. Distribution-shift analysis

Compare training/test data across:

```text paper
topic
year
question type
scientific quantity
source count
difficulty
```

Large differences may explain performance changes.

A model failing on V4 may be experiencing:

```text distribution shift
```

rather than ordinary noise.

---

# 78. Stratified evaluation

Final V4 analysis should report at least:

```text overall
SIMPLE
MULTI_HOP
CONFLICTING
TEMPORAL
CHAIN
```

where sample sizes permit.

Also consider:

```text numeric
multi-source
paper-pair
table/equation-related
```

if enough data exists.

Always include:

```text n
```

for each subgroup.

---

# 79. Benchmark fairness

Do not make V4 artificially favorable to AtlasRAG.

For example, avoid generating only questions where:

```text hybrid retrieval
```

is known to work well.

The benchmark should represent:

```text successes
+
hard cases
+
failures
```

This is essential for a credible research result.

---

# 80. Test set isolation

Once V4 final test is frozen:

```text do not manually inspect it to tune the system
```

unless the process explicitly treats that as development data.

If a question is discovered to be invalid:

```text document
remove from test
create new version
```

Do not silently modify its text.

---

# 81. Benchmark repair after freeze

If an issue is discovered after final freeze:

```text V4.1
```

or:

```text V5
```

should be created.

Preserve:

```text original V4
```

and record:

```text replacement question
reason
date
impact
```

This keeps the test history auditable.

---

# 82. Benchmark hash

For every final benchmark:

```text SHA-256
```

or an equivalent content hash can be stored.

The manifest can then state:

```text benchmark_hash = ...
```

This helps prove that a result file corresponds to the intended question set.

---

# 83. Corpus hash/version

Likewise record:

```text corpus manifest hash
```

or:

```text corpus version ID
```

The same paper can change because:

```text metadata
parsing
chunking
```

changed.

Version the corpus used for each experiment.

---

# 84. Split hash

If benchmark splits are generated programmatically, record:

```text train split hash
validation split hash
test split hash
```

or store explicit split files.

Do not rely only on:

```text random seed
```

for the final evaluation artifact.

---

# 85. Generation reproducibility

For LLM-assisted generation, save:

```text model ID
provider
prompt version
temperature
max tokens
seed if supported
cache namespace
timestamp
candidate outputs
```

A future agent should be able to inspect how the candidate set was produced.

---

# 86. Provider limits

The project has already encountered:

```text Groq 429 rate limits
```

during generation.

V4 generation may be larger.

Therefore:

```text bounded retries
persistent partial output
resumable batches
provider accounting
```

are not optional engineering details.

They protect the benchmark artifact.

---

# 87. Cache accounting

The generation run should distinguish:

```text logical generation requests
actual provider requests
cache hits
cache misses
retry attempts
```

This fixes the earlier instrumentation limitation.

Do not report:

```text provider cost
```

based solely on logical call count when caching may have removed provider requests.

---

# 88. Candidate-generation report

At the end of generation, produce:

```text generation_summary.json
```

with:

```text candidate_count
accepted_count
rejected_count
calls
provider_calls
cache_hits
cache_misses
retries
rate_limits
connection_failures
tokens
per-type counts
rejection reasons
```

The actual schema should match repository conventions.

---

# 89. Human-review report

Likewise save:

```text review_summary.json
```

containing:

```text reviewers
accepted
rejected
adjudicated
disagreement count
rejection taxonomy
review duration if measured
```

This makes benchmark curation more transparent.

---

# 90. V4 acceptance report

A final benchmark report should say:

```text generated:
N

automatically rejected:
N

human reviewed:
N

accepted:
N

final types:
...
```

Do not report only:

```text final N.
```

The path from candidates to accepted benchmark is part of benchmark provenance.

---

# 91. Benchmark documentation

Create a dedicated document for V4:

```text docs/benchmark_v4.md
```

or the repository's equivalent.

Include:

```text purpose
scope
corpus
question definitions
generation
validation
human review
splits
statistics
limitations
hash
```

The benchmark should be understandable without reading the entire codebase.

---

# 92. V4 benchmark limitations

Disclose:

```text source availability
topic concentration
possible duplicate scientific claims
manual review subjectivity
LLM generation influence
gold-evidence limitations
alternative evidence
paper-distribution limits
```

The benchmark does not become perfect merely because it is larger.

---

# 93. What counts as benchmark success

V4 is successful if it produces:

```text more valid independent questions
+
stronger difficult-class coverage
+
better paper diversity
+
cleaner splits
+
stable validation
+
manageable review burden
```

A larger but noisier benchmark is not a success.

---

# 94. What does not count as success

Do not use:

```text acceptance rate
question count
LLM-generation volume
```

as primary benchmark-quality metrics.

A generator accepting 80% of weak candidates is worse than one accepting 25% of excellent candidates.

---

# 95. V4 and research claims

A stronger benchmark can support stronger claims, but only if:

```text evaluation is actually run
+
test set remains untouched
+
generalization is measured
```

Do not automatically rewrite the paper to say:

```text general scientific QA
```

just because the benchmark became larger.

Scope still matters.

---

# 96. Recommended V4 output table

Create:

| Property | V1 | V4 |
|---|---:|---:|
| Papers | | |
| Questions | 27 | |
| SIMPLE | 18* | |
| MULTI_HOP | 7* | |
| CONFLICTING | | |
| TEMPORAL | | |
| CHAIN | | |
| Retrieval-sufficient | 18* | |
| Retrieval-insufficient | 9* | |
| Paper-disjoint split | | |
| Topics | | |

`*` These are Oracle-v2 distributions where applicable, not raw question-type counts in all cases.

Use exact final values from the generated manifest.

---

# 97. V4 experiment matrix

After the benchmark is frozen:

```text E0
Oracle-v2 baseline

B
Static retrieval

C1
Original LLM router

C2
Oracle-aligned router

D
Compass if trained/reproducible

H
Failure prediction / escalation if implemented
```

The exact matrix depends on what was actually implemented.

Do not force all rows to exist.

---

# 98. Historical comparison

Report:

```text V1 historical result
```

separately from:

```text V4 final result
```

Then answer:

```text Did the ranking change?
Did the Oracle gap change?
Did difficult classes expose different behavior?
```

The point is not to prove V4 is better.

The point is to test whether V1 conclusions generalize.

---

# 99. Cross-version analysis

Potential table:

| Metric | V1 | V4 | Interpretation |
|---|---:|---:|---|
| Static recall | | | |
| Router recall | | | |
| Oracle recall | | | |
| Oracle gap | | | |
| Strong-retrieval cost | | | |
| Failure rate | | | |

The interpretation column should be written after the results are available.

---

# 100. V4 stopping criteria

Freeze V4 when:

```text
[ ] corpus finalized
[ ] paper pool finalized
[ ] generator finalized
[ ] validators finalized
[ ] candidate generation complete
[ ] human review complete
[ ] splits frozen
[ ] duplicates checked
[ ] support checked
[ ] benchmark manifest created
[ ] benchmark hash recorded
[ ] Oracle-v2 labels computed
[ ] class statistics generated
[ ] known limitations documented
```

After that:

```text benchmark is locked
```

for the intended final test.

---

# 101. Future V5 after V4

Only after V4 is stable should the project move to:

```text V5
cross-domain generalization
```

or another research direction.

The goal is:

```text broader benchmark
→ test current conclusions
→ only then broaden domain.
```

Do not make all dimensions difficult at once.

---

# 102. Week 13 experiment philosophy

The most important principle is:

> **Benchmark expansion should improve the validity of the scientific question, not improve the score.**

A good V4 benchmark may make AtlasRAG look worse.

That can be a successful outcome if it reveals:

```text where V1 was optimistic
```

or:

```text which question types are genuinely difficult.
```

---

# 103. Week 13 execution order

Use this order:

```text
STEP 1
Freeze V1 artifacts.

STEP 2
Inspect current corpus and metadata.

STEP 3
Measure paper/topic distribution.

STEP 4
Identify which evidence structures are underrepresented.

STEP 5
Define V4 benchmark targets.

STEP 6
Inspect and preserve current deterministic sourcing code.

STEP 7
Improve only the sourcing/validation components justified by the target.

STEP 8
Run a small pilot.

STEP 9
Manually review the pilot.

STEP 10
Measure rejection reasons.

STEP 11
Repair generator/validator issues.

STEP 12
Generate the larger candidate pool incrementally.

STEP 13
Persist generation instrumentation.

STEP 14
Run automatic validation.

STEP 15
Run human review.

STEP 16
Freeze train/validation/test splits.

STEP 17
Generate the benchmark manifest + hash.

STEP 18
Run Oracle-v2 on the new benchmark.

STEP 19
Inspect class balance and insufficiency.

STEP 20
Run routing/retrieval evaluation.

STEP 21
Run V2/V3 extensions on V4 only if their data/evaluation requirements are satisfied.

STEP 22
Compare V1 vs V4.

STEP 23
Document generalization and benchmark limitations.

STEP 24
Commit the benchmark as a new version.
```

---

# 104. Commands to begin Week 13

Start:

```powershell
$env:PYTHONPATH="src"
```

Inspect repository:

```powershell
git status
git log --oneline --decorate -15
python -m pytest -q
```

Inspect benchmark files:

```powershell
Get-ChildItem .\dataench -Recurse -File | Select-Object FullName,Length,LastWriteTime
```

Inspect source papers:

```powershell
Get-ChildItem .\data -Recurse -File -ErrorAction SilentlyContinue | Select-Object FullName
```

Inspect benchmark generation code:

```powershell
Get-Content .\srctlasragench\generate.py
```

```powershell
Get-Content .\srctlasragench\generate_v2.py
```

Inspect validation:

```powershell
Get-Content .\srctlasragenchalidate.py
```

Inspect Oracle-v2:

```powershell
Get-Content .\srctlasragench\oracle_v2.py
```

Inspect benchmark schema:

```powershell
Get-Content .\srctlasragench\schema.py
```

Inspect generation scripts:

```powershell
Get-Content .\scripts\gen_questions_v2.py
```

Inspect current test coverage:

```powershell
Get-ChildItem .	ests -Recurse -File | Select-String "generate|pair|temporal|chain|conflict|support"
```

Before changing anything, determine:

```text
what the current generator already guarantees
```

versus:

```text
what V4 actually needs.
```

---

# 105. Final V4 checklist

```text
[ ] V1 benchmark untouched
[ ] V4 paper pool defined
[ ] paper diversity measured
[ ] topic diversity measured
[ ] question types defined
[ ] pair-sourcing constraints preserved
[ ] candidate generation instrumented
[ ] automatic validators tested
[ ] human-review rubric finalized
[ ] duplicate detection tested
[ ] reference answers audited
[ ] paper-disjoint splits created
[ ] final test frozen
[ ] benchmark hash recorded
[ ] Oracle-v2 recomputed
[ ] sufficient/insufficient counts recorded
[ ] benchmark limitations documented
[ ] routing evaluation rerun
[ ] retrieval evaluation rerun
[ ] V1 vs V4 comparison prepared
```

---

# 106. Final Week 13 principle

> **A benchmark should become harder because the science is harder, not because the benchmark designer wants a lower score.**

The final V4 objective is:

```text more independent scientific evidence structures
+
better document diversity
+
cleaner generalization
+
stronger statistical power
```

while preserving the discipline established by the original 27-question benchmark.

The long-term AtlasRAG research chain becomes:

```text V1
controlled adaptive routing

V2
evidence verification

V3
retrieval-state-aware failure prediction

V4
larger paper-disjoint benchmark

V5
cross-domain generalization
```

The important thing is that each version tests a new question rather than merely adding another feature.

A larger benchmark is valuable only if it lets AtlasRAG answer something the 27-question benchmark could not answer reliably.
