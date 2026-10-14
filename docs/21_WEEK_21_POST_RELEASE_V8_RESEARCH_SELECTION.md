# AtlasRAG — Week 21: Post-Release V8 Research Selection & New Research Cycle

## 1. Purpose

Week 20 closed the first major AtlasRAG research cycle:

```text
build
↓
benchmark
↓
measure
↓
iterate
↓
stress-test
↓
integrate
↓
evaluate
↓
reproduce
↓
release
```

Week 21 must **not assume that a V8 exists**.

The previous roadmap explicitly ended with:

```text
Do not create V8 merely because the roadmap can continue.
```

Therefore Week 21 is a **post-release research-selection stage**.

The question is:

> **Given the final released evidence, what is the highest-value next scientific question that can be isolated and tested without reopening the completed research cycle?**

The workflow is:

```text
Final release
     ↓
Inspect evidence
     ↓
Identify strongest unresolved limitation
     ↓
Generate candidate research directions
     ↓
Fresh literature review
     ↓
Score candidates
     ↓
Select ONE primary V8 question
     ↓
Design a new controlled study
     ↓
Create V8 baseline + benchmark
     ↓
Begin a new research cycle
```

The most important rule is:

```text
V8 must be evidence-driven.
```

---

# 2. Why V8 should not be chosen immediately

By Week 20, AtlasRAG may already contain many sophisticated components:

```text
adaptive routing
failure prediction
scientific structure
evidence graphs
selective escalation
verification
cross-domain evaluation
```

That creates a temptation:

```text add another advanced feature
```

simply because it sounds impressive.

This is the wrong criterion.

A good V8 question should arise from an actual unresolved problem such as:

```text retrieval still misses equations
graph relations remain noisy
cross-domain transfer degrades
verification still misses unsupported claims
cost is too high
benchmark remains too small
answer generation remains the bottleneck
```

The final Week 20 evidence decides which problem matters most.

---

# 3. V8 primary selection question

The new research question should be:

> **What unresolved bottleneck in the released AtlasRAG system has the strongest evidence, the clearest scientific hypothesis, and the most tractable controlled experiment?**

This has three components:

```text evidence
+
research value
+
experimental tractability
```

A direction that is exciting but impossible to isolate should not automatically win.

A direction that is easy but scientifically unimportant should also not win.

---

# 4. V8 candidate families

Potential directions include:

```text A
retrieval efficiency

B
scientific evidence representation

C
graph quality / graph reasoning

D
evidence verification

E
cross-domain adaptation

F
multimodal scientific retrieval

G
benchmark expansion

H
uncertainty / calibration

I
human-in-the-loop retrieval

J
answer-generation grounding
```

These are candidate families only.

Do not implement all of them.

---

# 5. Candidate-selection rule

For every candidate create:

```text research question
motivation
evidence from final study
expected contribution
benchmark requirement
implementation complexity
evaluation complexity
likely confounders
cost
novelty uncertainty
```

Then score each candidate.

A simple qualitative scale:

```text 1 = weak
2 = low
3 = moderate
4 = strong
5 = very strong
```

Possible dimensions:

```text evidence strength
scientific importance
novelty potential
tractability
evaluation clarity
reproducibility
portfolio value
```

Do not let:

```text portfolio value
```

override:

```text scientific evidence
```

---

# 6. Evidence-strength criterion

The strongest V8 candidates are directly connected to:

```text final failure counts
final rescue/regression analysis
robustness failures
domain transfer gaps
citation failures
cost bottlenecks
```

For example:

```text 42% of remaining failures involve table extraction
```

would justify considering:

```text better table representation
```

more strongly than:

```text another routing model
```

if routing is no longer the bottleneck.

Use actual final numbers.

---

# 7. Do not invent final bottlenecks

The next AI agent must inspect:

```text FINAL_RESULTS
FINAL_FAILURE_ANALYSIS
FINAL_DECISION
Week 18 robustness
Week 19 end-to-end evaluation
```

before choosing V8.

Do not assume:

```text graph is the bottleneck
```

or:

```text generation is the bottleneck
```

unless the final evidence shows it.

---

# 8. Bottleneck tree

Build a diagnostic tree:

```text Final answer wrong
      |
      ├─ evidence absent
      |      ↓
      |   corpus/benchmark issue
      |
      ├─ evidence not retrieved
      |      ↓
      |   retrieval issue
      |
      ├─ evidence retrieved but not selected
      |      ↓
      |   ranking/graph/policy issue
      |
      ├─ evidence correct but answer wrong
      |      ↓
      |   generation/reasoning issue
      |
      └─ answer correct but citation wrong
             ↓
          verification/provenance issue
```

Use this before selecting V8.

---

# 9. Research-cycle separation

Keep:

```text V1–V7
```

as the first research cycle.

Do not retroactively change their goals.

V8 is:

```text new study
```

with:

```text new question
new baseline
new experiment matrix
new versioned artifacts
```

This makes the project easier to publish and reproduce.

---

# 10. Fresh literature review requirement

Before locking the V8 question, perform a fresh literature review.

The exact topics depend on the selected candidate.

Possible searches include:

```text scientific RAG
adaptive retrieval
retrieval failure prediction
graph RAG
evidence graphs
scientific document parsing
table retrieval
equation retrieval
scientific multimodal RAG
citation verification
cross-domain RAG
selective prediction
```

The final literature review must distinguish:

```text existing method
```

from:

```text AtlasRAG-specific experiment
```

Do not claim:

```text first
novel
new
unprecedented
```

without current evidence.

---

# 11. V8 literature-review record

Create:

```text 01_V8_LITERATURE_REVIEW.md
```

with:

```text search date
search terms
papers/articles found
relevant methods
limitations
open questions
AtlasRAG gap
```

The purpose is not to collect dozens of citations.

The purpose is:

```text understand the nearest prior work
```

before claiming a research contribution.

---

# 12. Candidate decision matrix

Create a table:

```text
Candidate
Final evidence
Scientific value
Novelty confidence
Difficulty
Evaluation clarity
Cost
Decision
```

Possible final decisions:

```text SELECT
SECONDARY
DEFER
REJECT
```

Only one should normally become:

```text primary V8
```

---

# 13. Candidate A — retrieval efficiency

Potential research question:

> Can AtlasRAG preserve evidence quality while reducing retrieval and reranking computation further?

This becomes relevant if:

```text final quality is strong
but
query cost/latency remains high
```

Potential approaches:

```text early-exit retrieval
adaptive k
conditional reranking
candidate pruning
cached retrieval states
```

Do not implement them all.

---

# 14. Candidate B — scientific evidence representation

Potential question:

> Which scientific document structures remain inadequately represented after V6?

Potential structures:

```text equations
tables
figure captions
experimental conditions
units
uncertainty
references
supplementary material
```

This direction is justified only if the final failure taxonomy identifies:

```text structure-related retrieval failures
```

as important.

---

# 15. Candidate C — graph quality and reasoning

Potential question:

> Can graph reliability be improved so that evidence paths remain useful under realistic extraction errors?

Potential focus:

```text edge confidence
relation verification
entity normalization
path ranking
noise filtering
```

This is appropriate if:

```text graph helped
but
graph errors caused significant regressions
```

Do not build deeper graph traversal if:

```text graph itself is not reliable enough
```

---

# 16. Candidate D — evidence verification

Potential question:

> Can claim-level evidence verification reduce unsupported scientific claims and citation errors without requiring a stronger answer model?

Relevant if:

```text retrieval is already strong
but
unsupported claims remain
```

Potential experiments:

```text claim extraction
citation mapping
numeric checking
temporal checking
conflict checking
```

Keep the initial study detection-oriented.

---

# 17. Candidate E — cross-domain adaptation

Potential question:

> How much supervision is required to adapt AtlasRAG's retrieval policy to a new scientific domain?

Potential ladder:

```text zero-shot
few-shot threshold calibration
few-shot classifier adaptation
mixed-domain training
held-out-domain evaluation
```

This is relevant if:

```text V5/Week 18 showed promising transfer
but significant calibration/feature-shift problems
```

---

# 18. Candidate F — multimodal scientific retrieval

Potential question:

> Can visual scientific evidence improve retrieval of information that text-only representations systematically miss?

Possible evidence:

```text plots
figures
diagram annotations
table images
flowcharts
```

This is a much larger project.

Do not choose it merely because:

```text multimodal AI is trendy
```

Choose it only if:

```text final evidence
```

shows a meaningful visual-evidence bottleneck.

---

# 19. Candidate G — benchmark science

Potential question:

> Can a larger, richer, better-audited scientific benchmark reveal failure modes not visible in the released benchmark?

Relevant if:

```text final benchmark remains small
class coverage is uneven
human audit is limited
```

Benchmark work is a legitimate research direction.

It should not be dismissed as:

```text just data work
```

when evaluation validity is the main limitation.

---

# 20. Candidate H — uncertainty and calibration

Potential question:

> Can AtlasRAG produce better-calibrated confidence about evidence sufficiency, answer support, and escalation decisions?

Potential outputs:

```text failure probability
answer confidence
citation confidence
abstention decision
```

Relevant if:

```text raw probabilities are poorly calibrated
high-confidence failures remain common
```

---

# 21. Candidate I — human-in-the-loop retrieval

Potential question:

> Can a lightweight human intervention resolve ambiguous scientific retrieval cases more efficiently than automatic escalation?

Possible flow:

```text retrieval uncertain
↓
show candidate evidence
↓
human selects evidence family
↓
refined retrieval
```

This changes the target system substantially.

Use only if:

```text practical human-assisted workflow
```

is genuinely interesting.

---

# 22. Candidate J — answer-generation grounding

Potential question:

> If retrieval is already adequate, can the answer generator use the available evidence more faithfully?

Potential approaches:

```text citation-constrained generation
claim-first generation
evidence selection before wording
structured answer templates
verification-guided generation
```

This is appropriate when:

```text evidence recall is good
but answer/citation quality remains weak
```

---

# 23. Do not automatically choose the hardest candidate

A common mistake is:

```text more advanced
→ more impressive
```

The best V8 is:

```text scientifically meaningful
+
isolatable
+
measurable
+
reproducible
```

A smaller but rigorous study can be stronger than:

```text enormous multimodal architecture
```

with weak controls.

---

# 24. V8 baseline principle

Every new V8 study needs a strong baseline.

For any candidate:

```text current released system
```

must remain the reference unless the new research question explicitly requires another baseline.

Do not compare:

```text V8
```

against:

```text obsolete Run1
```

just to make improvement look larger.

---

# 25. V8 benchmark principle

A new benchmark is not automatically required.

Reuse:

```text final benchmark
```

when it properly measures the new question.

Create:

```text V8 benchmark
```

only when the final benchmark lacks the necessary evidence structures or task coverage.

---

# 26. V8 split principle

Maintain:

```text paper-disjoint
```

where possible.

For domain studies:

```text domain-disjoint
```

where relevant.

Do not weaken the split just to increase the training set.

---

# 27. V8 leakage audit

Before any new experiment inspect:

```text benchmark generation
training data
retrieval index
graph
model inputs
evaluation prompts
```

for:

```text gold evidence leakage
answer leakage
test paper leakage
test-domain leakage
question-specific rules
```

The new research cycle must preserve the original project's strongest methodological lesson:

```text evidence must not leak into decisions.
```

---

# 28. V8 one-variable rule

The primary experiment should introduce:

```text one major independent variable
```

at a time.

Bad:

```text new embedding
+
new graph
+
new prompt
+
new LLM
```

Good:

```text current system
+
one controlled representation change
```

This is essential for attribution.

---

# 29. V8 hypothesis template

Write:

```text H1:
...

Mechanism:
...

Expected metric:
...

Counter-hypothesis:
...

Potential failure:
...
```

Example:

```text H1:
better table representation improves quantitative evidence recall.

Mechanism:
row/column/unit relationships are preserved.

Metric:
table-question evidence recall.

Counter-hypothesis:
semantic retrieval already captures the needed information.
```

The exact hypothesis should follow the selected V8 direction.

---

# 30. V8 experiment ladder

Every V8 project should use:

```text baseline
↓
simple intervention
↓
controlled ablation
↓
stronger intervention
↓
combined condition
↓
robustness
↓
end-to-end evaluation
```

Do not jump directly to the largest model.

---

# 31. V8 success criteria

Define before final testing:

```text primary metric
secondary metric
cost constraint
latency constraint
minimum practical improvement
```

Do not decide success solely after seeing the results.

---

# 32. Practical significance

A V8 method can be statistically significant but practically useless.

For example:

```text +0.5 percentage points
```

with:

```text 3× cost
```

may not be attractive.

Evaluate:

```text quality
+
cost
+
latency
```

together.

---

# 33. V8 statistical discipline

Define:

```text primary comparison
sample unit
confidence interval method
paired test
secondary analyses
```

before inspecting the final test.

Keep exploratory analyses clearly labeled.

---

# 34. Small-data discipline

If the new study has limited data:

```text favor interpretable baselines
```

such as:

```text logistic regression
linear model
small tree
simple ranking
```

before:

```text large neural model
```

A small benchmark does not justify a large model automatically.

---

# 35. New benchmark generation

If new questions are necessary:

```text candidate generation
↓
deterministic filters
↓
support audit
↓
human review
↓
retrieval sufficiency
↓
Oracle recomputation
↓
freeze
```

Reuse the benchmark-quality lessons learned during earlier weeks.

---

# 36. Human review remains the final authority

Automatic filters can reject:

```text obviously weak questions
```

but human review remains necessary for:

```text multi-hop necessity
temporal validity
conflict validity
answer support
alternative evidence
```

Do not allow the generator to become its own final judge.

---

# 37. V8 benchmark quality metrics

Track:

```text candidates generated
accepted
rejected
rejection reasons
question-type distribution
paper distribution
domain distribution
retrieval sufficiency
audit pass rate
```

If LLM generation is involved, also track:

```text logical calls
provider calls
cache hits
retries
429s
tokens
```

---

# 38. Provider instrumentation

The earlier project instrumentation gaps should not return.

Persist:

```text logical calls
provider API calls
cache hits
cache misses
retry attempts
RateLimitError count
APIConnectionError count
prompt tokens
completion tokens
final status
```

This is especially important if V8 uses large-scale generation.

---

# 39. Bounded retries

Maintain the project's bounded retry behavior.

A benchmark or experiment script must never:

```text retry forever
```

on provider rate limits.

Every failed request should have:

```text explicit terminal status
```

and:

```text run summary
```

---

# 40. V8 cost accounting

Separate:

```text dataset construction cost
index construction cost
offline model cost
online query cost
```

Do not collapse all tokens into:

```text cost/query
```

when most of the cost is a one-time preprocessing stage.

---

# 41. V8 reproducibility

Every result needs:

```text Git commit
benchmark version
corpus version
model versions
configuration
prompt version
random seed if applicable
```

For externally hosted models:

```text provider
model identifier
evaluation date
```

should also be recorded.

---

# 42. V8 failure taxonomy

Create categories specific to the new hypothesis, but retain the general hierarchy:

```text benchmark
→ ingestion
→ retrieval
→ selection
→ generation
→ verification
→ runtime
```

Then add:

```text V8-specific failure
```

For example:

```text table reconstruction error
graph relation error
calibration drift
multimodal grounding failure
```

depending on the selected research direction.

---

# 43. Counterfactual evaluation

Where useful, compare:

```text current system
vs
V8 intervention
```

on the same questions.

Then inspect:

```text baseline correct / V8 wrong
baseline wrong / V8 correct
```

This remains one of the most valuable diagnostic tools.

---

# 44. Rescue and regression analysis

For every V8 system:

```text rescue count
regression count
both correct
both incorrect
```

Then inspect representative examples.

A method that improves averages but creates severe regressions in critical cases may not be suitable for release.

---

# 45. Benchmark difficulty stratification

Measure performance by:

```text easy
moderate
hard
```

if difficulty can be defined independently.

Do not define difficulty from:

```text model success
```

because that would be circular.

Use:

```text number of evidence units
path length
ambiguity
question type
```

or similar predeclared properties.

---

# 46. Domain stratification

If V8 is cross-domain:

```text source domains
target domains
```

should be reported independently.

Do not let the aggregate hide:

```text one domain failing completely
```

---

# 47. V8 robustness

After the primary result, test:

```text paper-disjoint
domain-shift
threshold
retrieval settings
context budget
reasonable noise
```

only where these perturbations actually matter for the selected hypothesis.

Do not run irrelevant stress tests just to create a long table.

---

# 48. Final V8 decision

At the end classify:

```text KEEP
KEEP WITH QUALIFIERS
REVISE
DEFER
REJECT
```

and document:

```text primary finding
main limitation
strongest rescue
strongest regression
operational tradeoff
next direction
```

---

# 49. V8 publication claim

The final claim should have the form:

```text Under [defined setting],
[intervention] changed [metric]
relative to [baseline],
with [operational tradeoff].
```

Avoid:

```text solves
proves
guarantees
universal
state-of-the-art
```

unless the evidence actually supports those claims.

---

# 50. V8 paper structure

Use:

```text 1. Research gap
2. Prior work
3. V8 hypothesis
4. Dataset/benchmark
5. Baseline
6. Intervention
7. Evaluation
8. Main result
9. Ablations
10. Robustness
11. Failure analysis
12. Limitations
13. Conclusion
```

Keep the new study separable from the first AtlasRAG cycle.

---

# 51. V8 relation to the original project

The paper/report should explain:

```text first cycle:
adaptive scientific RAG

second cycle:
one specific unresolved limitation
```

Do not pretend V8 was part of the original research question from the beginning.

Research evolves.

Document that evolution.

---

# 52. V8 repository separation

Prefer:

```text experiments/v8/
data/v8/
docs/v8/
figures/v8/
```

rather than overwriting:

```text final/
```

The released first-cycle system must remain reproducible.

---

# 53. V8 branch or tag strategy

The released first-cycle system should have an immutable:

```text tag/release
```

V8 can then develop from:

```text released state
```

with a new branch or clearly separated commit sequence.

Do not mutate the released tag.

---

# 54. V8 experiment manifests

Every experiment should record:

```text experiment_id
purpose
baseline
intervention
benchmark
corpus
model
configuration
commit
status
result path
```

This becomes the new research registry.

---

# 55. V8 result storage

Persist:

```text per-question result
aggregate result
runtime metrics
failure state
configuration
```

Do not store only final averages.

---

# 56. V8 analysis pipeline

Prefer:

```text raw result
↓
analysis script
↓
tables
↓
figures
↓
paper
```

rather than manually transferring numbers between files.

This continues the reproducibility standard established in Week 20.

---

# 57. V8 test-before-run

Before full evaluation:

```powershell
cd <AtlasRAG-repo>

$env:PYTHONPATH="src"

python -m pytest -q

git status --short
git log --oneline --decorate -10
```

Then run a small smoke test.

Use actual project commands after inspection.

---

# 58. V8 smoke test

Run:

```text 3–10 questions
```

and inspect:

```text input
baseline
intervention
evidence
answer
citations
runtime
logging
```

Do not launch expensive full-scale evaluation until the smoke test passes.

---

# 59. V8 partial-run policy

If a run stops:

```text PARTIAL
```

and preserve:

```text completed rows
failed rows
runtime summary
error log
```

Do not use incomplete output as a final result.

---

# 60. V8 final-run freeze

Before the primary test:

```text benchmark locked
configuration locked
model locked
threshold locked
code commit recorded
```

Then:

```text run
↓
lock outputs
```

Afterward, changes require:

```text new version
```

---

# 61. V8 no-post-hoc optimization rule

Do not:

```text see failed cases
↓
modify method
↓
rerun same test
↓
call it the original result
```

Instead:

```text original result
↓
diagnosis
↓
new experiment
```

This keeps the research chronology valid.

---

# 62. V8 decision matrix example

Use a table like:

```text
Candidate | Evidence | Value | Difficulty | Novelty | Clarity | Status
-----------------------------------------------------------------------
A         | 5        | 4     | 4          | 3       | 5       | SELECT
B         | 4        | 5     | 3          | 4       | 4       | SECONDARY
C         | 3        | 4     | 2          | 3       | 3       | DEFER
```

These numbers are illustrative.

Populate them only after reviewing actual final evidence.

---

# 63. V8 selection tie-breakers

If two candidates are close, prefer the one with:

```text clearer causal question
stronger benchmark
lower confounding
better reproducibility
more direct connection to observed failures
```

Do not choose based only on:

```text technical complexity
```

---

# 64. Avoid roadmap bloat

The final V8 plan should have:

```text one primary question
one primary intervention
one primary baseline
one primary benchmark
```

Secondary experiments can exist, but the main study must remain understandable.

---

# 65. Research budget

Before V8 begins define:

```text time budget
compute budget
provider budget
human-review budget
```

This prevents a promising experiment from becoming an uncontrolled months-long project.

---

# 66. Provider budget guardrail

If LLM calls are involved, define:

```text maximum logical calls
maximum provider calls
maximum retries
maximum expected tokens
```

and:

```text abort conditions
```

before large benchmark generation.

---

# 67. Human-review budget

Define:

```text mandatory review subset
```

before generation.

For example:

```text relationship-heavy cases
high-impact disagreements
edge cases
```

The exact allocation depends on the selected V8 benchmark.

---

# 68. V8 project status board

Maintain:

```text QUESTION
HYPOTHESIS
BENCHMARK
BASELINE
INTERVENTION
METRICS
EXPERIMENTS
RESULTS
FAILURES
DECISION
```

This prevents the next cycle from becoming another uncontrolled feature list.

---

# 69. V8 documentation bundle

Recommended:

```text 01_V8_LITERATURE_REVIEW.md
02_V8_RESEARCH_QUESTION.md
03_V8_BENCHMARK_SPEC.md
04_V8_BASELINE.md
05_V8_METHOD.md
06_V8_EXPERIMENT_MATRIX.md
07_V8_RESULTS.md
08_V8_FAILURE_ANALYSIS.md
09_V8_ROBUSTNESS.md
10_V8_DECISION.md
```

Raw:

```text data/v8/
experiments/v8/
figures/v8/
```

---

# 70. Future-agent handoff

At the end of V8, create:

```text V8_HANDOFF.md
```

containing:

```text what changed
why it changed
what was measured
what failed
what survived
what remains unresolved
```

This becomes the entry point for V9 if one is justified.

---

# 71. V9 should not be assumed

The same rule applies after V8:

```text no automatic V9
```

A new version exists only when:

```text evidence identifies a meaningful unresolved problem
```

and:

```text a controlled study is justified
```

---

# 72. Final Week 21 decision workflow

Use:

```text FINAL RELEASE
      ↓
READ FINAL RESULTS
      ↓
READ FAILURE TAXONOMY
      ↓
READ ROBUSTNESS
      ↓
IDENTIFY BOTTLENECK
      ↓
SEARCH LITERATURE
      ↓
GENERATE 3–5 CANDIDATES
      ↓
SCORE CANDIDATES
      ↓
SELECT ONE PRIMARY V8
      ↓
WRITE HYPOTHESIS
      ↓
FREEZE BASELINE
      ↓
BUILD MINIMAL EXPERIMENT
```

This is the entire purpose of Week 21.

---

# 73. Exact execution order

Follow:

```text
1. inspect Week 20 final release
2. verify released commit/tag
3. read final results
4. read final failure analysis
5. read robustness/transfer results
6. identify unresolved bottlenecks
7. perform fresh literature review
8. create 3–5 candidate V8 directions
9. build candidate decision matrix
10. select one primary V8 question
11. write hypothesis
12. define baseline
13. define benchmark needs
14. define metrics
15. define leakage controls
16. define cost/review budget
17. freeze the V8 research specification
18. create V8 repository/data structure
19. implement only the minimum required infrastructure
20. run smoke tests
21. stop before large-scale experiments until the design is reviewed
```

Week 21 should end with:

```text V8 question locked
```

not:

```text giant unfinished V8 implementation
```

---

# 74. PowerShell starting point

Use:

```powershell
cd <AtlasRAG-repo>

$env:PYTHONPATH="src"

git status --short
git log --oneline --decorate -20

python -m pytest -q

Get-ChildItem docs
Get-ChildItem data
Get-ChildItem experiments
Get-ChildItem src/atlasrag
```

Then inspect the actual release and final artifacts before changing code.

---

# 75. Git discipline

Keep the first-cycle release immutable.

Suggested V8 commits:

```text V8 research specification

V8 benchmark infrastructure

V8 baseline

V8 intervention

V8 evaluation

V8 analysis
```

Do not mix:

```text release cleanup
```

with:

```text V8 research changes
```

if they can be kept separate.

---

# 76. Final Week 21 mental model

Week 20 said:

```text finish cycle
```

Week 21 says:

```text decide whether another cycle is worth starting
```

The process is:

```text completed evidence
        ↓
strongest limitation
        ↓
research opportunity
        ↓
fresh literature
        ↓
one testable question
        ↓
new controlled cycle
```

The key question is not:

```text What feature can we add?
```

It is:

> **What question remains important enough to justify another experiment?**

---

# 77. Final rule for the next AI agent

Start with the actual released AtlasRAG state.

Do not assume the final architecture is incomplete.

Do not invent a V8 bottleneck.

Do not choose a direction because it sounds technically impressive.

Do not skip the fresh literature review.

Do not claim novelty before checking prior work.

Do not create multiple competing V8 architectures before selecting the research question.

Do not reopen completed V1–V7 experiments without a clearly defined new hypothesis.

Do not modify the released final benchmark.

Do not overwrite the released system.

Do not tune a new method on its final test set.

Do not spend large provider budgets before a smoke test passes.

Do not let the roadmap drive the research.

The correct workflow is:

```text
release
↓
inspect evidence
↓
identify unresolved limitation
↓
research prior work
↓
compare candidate directions
↓
select one question
↓
write hypothesis
↓
define baseline
↓
define benchmark
↓
define metrics
↓
define leakage controls
↓
define cost/review budget
↓
freeze V8 specification
↓
only then implement
```

That is Week 21.
