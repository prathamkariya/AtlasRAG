# AtlasRAG — Week 20: Final Research Synthesis, Paper, Reproducibility & Release

## 1. Purpose

Week 19 completed the main integrated end-to-end evaluation.

That stage asked:

```text
Does the final assembled AtlasRAG system actually improve
scientific answers, evidence grounding, citations, cost, and latency?
```

Week 20 should therefore **not become another feature-development week**.

It is the final evidence-locking and research-packaging stage:

```text
Week 19
final integrated evaluation

        ↓

Week 20
research synthesis
+
paper/report
+
reproducibility
+
release
+
portfolio
```

The central rule is:

> **Do not optimize the story after seeing the results. Lock the evidence first, then write the story that the evidence supports.**

The goal is to produce a version of AtlasRAG that another technically competent person can understand, reproduce, inspect, and evaluate.

---

# 2. What Week 20 is not

Do not use Week 20 to:

```text
add another major model

rewrite the benchmark to improve scores

change the final answer prompt

change the retrieval stack

retune the graph

retune V3

rerun only favorable examples

remove difficult questions

hide negative experiments

invent a new V8 component
```

Any genuinely new research idea discovered here should be recorded as:

```text
future work
```

or:

```text
new experiment
```

not silently inserted into the final result.

---

# 3. Primary Week 20 question

The final question is:

> **What does the complete AtlasRAG research program actually establish, what remains uncertain, and can the resulting system and evidence package be reproduced and communicated credibly?**

This produces five outputs:

```text
1. final scientific interpretation

2. final paper/report

3. reproducibility package

4. public repository/release

5. final portfolio / presentation material
```

---

# 4. The evidence hierarchy

Organize the project evidence into:

```text
E0
historical observations

E1
controlled component experiments

E2
benchmark-scale comparisons

E3
robustness / transfer results

E4
final integrated evaluation

E5
human/audit evidence
```

The strongest claims should rely primarily on:

```text E3 + E4 + E5
```

where available.

Do not use an early exploratory observation as the main support for a final claim when stronger later evidence exists.

---

# 5. Final research chronology

Create a compact chronology:

```text
Run1
↓
benchmark refinement
↓
Oracle-v2
↓
routing experiments
↓
Compass / adaptive policy work
↓
dynamic routing
↓
retrieval ablations
↓
answer / citation evaluation
↓
V2 evidence verification
↓
V3 failure prediction
↓
V4 benchmark expansion
↓
V5 cross-domain transfer
↓
V6 structure-aware retrieval
↓
V7 evidence graph
↓
selective graph escalation
↓
robustness
↓
final integrated evaluation
```

This chronology should show:

```text why each experiment happened
```

not merely:

```text what code was added
```

---

# 6. Separate planned from measured

Create three categories:

```text MEASURED
```

things actually evaluated.

```text IMPLEMENTED
```

things that exist in code but were not sufficiently evaluated.

```text PLANNED / FUTURE
```

things described in roadmaps but not completed.

This distinction is essential.

A feature existing in:

```text src/
```

does not mean:

```text experimentally validated
```

---

# 7. Final status table

Create one authoritative table:

```text
Component
Implemented?
Evaluated?
Primary evidence
Final status
```

Example categories:

```text retrieval baseline
Oracle-v2
Compass
dynamic routing
V2 verification
V3 failure prediction
V6 structure-aware retrieval
V7 graph
selective graph escalation
cross-domain transfer
```

Use the repository's actual state.

Do not mark a component:

```text validated
```

because it merely passed unit tests.

---

# 8. Final research questions

Map every major research question to evidence.

Example:

```text RQ1
Can routing improve retrieval efficiency?
→ experiments ...

RQ2
Can retrieval state predict failure?
→ V3 experiments ...

RQ3
Do scientific structures improve evidence retrieval?
→ V6 ...

RQ4
Do evidence relationships help?
→ V7 ...

RQ5
Can graph use be selective?
→ Week 17 ...

RQ6
Does the behavior survive shift?
→ Week 18 ...

RQ7
Does the integrated system improve answers/citations?
→ Week 19 ...
```

The exact wording should match what was actually studied.

---

# 9. Claim-to-evidence matrix

Create:

```text
Claim
Experiment
Benchmark
Metric
Effect
Uncertainty
Limitation
```

Every important sentence in:

```text abstract
introduction conclusion
README
resume
presentation
```

should be traceable to this matrix.

This is one of the most important Week 20 artifacts.

---

# 10. Main result selection

Choose a small number of headline results.

Prefer:

```text one primary retrieval result

one primary end-to-end result

one efficiency result

one robustness result
```

Do not publish twenty headline numbers.

A strong research story is:

```text focused
traceable
honest
```

---

# 11. Do not optimize for the largest percentage

The largest numerical improvement may not be:

```text most scientifically important
```

For example:

```text +12 points on a narrow exploratory subset
```

may matter less than:

```text +4 points on the frozen paper-disjoint final benchmark
```

The main result should be chosen by:

```text experimental rigor
+
scope
+
relevance
```

---

# 12. Primary versus secondary results

Mark:

```text PRIMARY
SECONDARY
EXPLORATORY
HISTORICAL
```

This prevents exploratory observations from accidentally becoming headline claims.

---

# 13. Statistical synthesis

For every primary comparison record:

```text baseline
new system
absolute difference
relative difference where useful
confidence interval
sample size
paired test
```

Do not report only:

```text p < ...
```

Include:

```text effect magnitude
```

and:

```text uncertainty
```

---

# 14. Small-sample caution

Some historical AtlasRAG experiments used small datasets.

Do not write:

```text proved
```

when the benchmark only supports:

```text observed
```

or:

```text suggests
```

Use language proportional to:

```text sample size
effect
confidence
```

---

# 15. Benchmark limitations

Document:

```text benchmark size
question-type balance
paper count
domain count
gold-evidence limitations
alternative-evidence handling
annotation uncertainty
```

If a category remains small:

```text say so
```

Do not hide it inside an aggregate score.

---

# 16. Oracle-v2 interpretation

Oracle-v2 is a reference mechanism, not a deployable model.

Use it to understand:

```text retrieval ceiling / best observed route behavior
```

under the project's evaluation definition.

Do not write:

```text Oracle achieved the final system result
```

as though it were an operational baseline.

---

# 17. Historical Run1 interpretation

Run1 remains useful because it establishes the early empirical trajectory.

Keep it labeled:

```text historical baseline
```

Do not merge Run1 with final benchmark results if:

```text benchmark
retrieval
instrumentation
or evaluation
```

changed afterward.

---

# 18. Benchmark versions

Document the progression:

```text V1 benchmark
V2 benchmark / Oracle semantics
V4 expanded benchmark
V5 transfer benchmark
V6 structure benchmark
V7 graph/relationship benchmark
final benchmark
```

Only include versions that actually existed.

For each version record:

```text question count
source papers
domains
main purpose
```

---

# 19. Benchmark hashing

For the final benchmark save:

```text SHA-256 or equivalent hash
```

and record it in:

```text final manifest
```

A benchmark filename alone is not enough to establish immutability.

---

# 20. Corpus manifest

Likewise create:

```text final corpus manifest
```

containing, where permissible:

```text paper ID
title
date
domain
source identifier
hash
license/access metadata
```

Do not redistribute restricted full text.

---

# 21. Final model manifest

Record:

```text answer model
embedding model
reranker
router model
V3 model
verification model
graph extraction model
```

and:

```text provider
version
configuration
```

for every model actually used.

---

# 22. Prompt manifest

Save the exact final prompts or prompt templates used for:

```text answer generation
verification
classification
relation extraction
```

where appropriate.

Version them.

Do not rely on:

```text prompt copied from memory
```

when reproducing final work.

---

# 23. Configuration manifest

Record final configuration for:

```text retrieval
chunking
reranking
graph
V3
verification
generation
```

Avoid hard-coding configuration in analysis prose.

The configuration file should be authoritative.

---

# 24. Environment manifest

Record:

```text Python
OS
package versions
GPU/CPU context
CUDA version if relevant
model identifiers
provider
```

A:

```text requirements lock
```

or equivalent is recommended.

---

# 25. Git provenance

Every final result should map to:

```text Git commit
```

Record:

```text code commit
analysis commit
benchmark version
configuration version
```

A final released result should never be:

```text \"the run I did yesterday\"
```

with no immutable identifier.

---

# 26. Final experiment registry

Create a machine-readable registry:

```text experiment_id
date
purpose
system
benchmark
config
commit
status
result_path
```

Example:

```text W17-D
selective graph
benchmark X
policy Y
commit Z
COMPLETE
result.json
```

Use real values.

---

# 27. Raw result preservation

Preserve:

```text per-question outputs
```

where licensing and privacy permit.

At minimum retain:

```text question_id
retrieval outcome
route
graph decision
answer outcome
citation outcome
latency
token usage
```

This is the audit backbone.

---

# 28. Do not manually overwrite result numbers

Final tables should be generated from:

```text machine-readable result files
```

Prefer:

```text analysis script
→ CSV/JSON
→ Markdown/LaTeX table
```

over:

```text manually typed final numbers
```

---

# 29. Figure generation

Every final figure should have:

```text source result file
generation script
script commit
figure filename
```

The preferred process is:

```text raw results
↓
analysis
↓
figure script
↓
figure
```

Do not hand-edit numeric content into plots.

---

# 30. Final figure set

Keep the final paper focused.

Recommended categories:

```text architecture figure

main quality/cost result

component ablation

robustness/transfer

failure taxonomy
```

Use only the figures needed to support the narrative.

---

# 31. Architecture figure

The final architecture should reflect the actual evaluated pipeline.

Potential diagram:

```text
Question
   ↓
Initial routing
   ↓
Initial retrieval
   ↓
Retrieval-state features
   ↓
Failure prediction
   ↓
Selective graph escalation
   ↓
Final evidence
   ↓
Answer
   ↓
Verification
   ↓
Citations
```

Remove boxes for components that did not survive final evaluation.

---

# 32. Main results figure

A strong figure might show:

```text
quality
vs
cost
```

with:

```text strong baseline
selective system
always-strong
always-graph
```

Only comparable systems should be plotted together.

---

# 33. Component ablation figure/table

Show:

```text baseline

+ V3

+ graph

+ V3 + graph

+ verification
```

or the final subset supported by actual experiments.

This communicates marginal contribution.

---

# 34. Robustness figure

Show:

```text source domain
target domain
retrieval perturbations
threshold neighborhood
graph perturbations
```

only where actual experiments exist.

Do not create an artificial aggregate robustness score just for visual simplicity.

---

# 35. Failure figure

A useful figure can show:

```text retrieval
graph
policy
generation
citation
benchmark
runtime
```

failure categories.

The final failure taxonomy is part of the scientific result.

---

# 36. Paper abstract

The abstract should contain:

```text problem
method
benchmark/evaluation setup
main result
main limitation
```

Avoid:

```text future work
planned components
unverified claims
```

Keep every numerical statement traceable to a final result file.

---

# 37. Paper introduction

A clean introduction can follow:

```text scientific RAG problem
↓
why evidence acquisition is difficult
↓
why adaptive retrieval is interesting
↓
AtlasRAG research questions
↓
evaluation strategy
↓
contribution summary
```

Do not claim novelty before describing the evaluation scope.

---

# 38. Related work

Run a fresh literature review before finalizing this section.

Search current work around:

```text scientific RAG
retrieval routing
adaptive retrieval
selective retrieval
retrieval failure prediction
graph RAG
knowledge-graph RAG
evidence graphs
citation-aware RAG
scientific QA
evidence verification
cross-domain RAG
```

Distinguish:

```text existing technique
```

from:

```text AtlasRAG experimental combination
```

Do not claim:

```text first
novel
unprecedented
```

without evidence.

---

# 39. Methodology section

Describe:

```text corpus
chunking
retrieval
routing
V3
structure representation
graph
verification
answer generation
```

But do not spend equal space on every component.

The method section should reflect:

```text actual research contribution
```

not:

```text number of Python files
```

---

# 40. Benchmark section

Explain:

```text question construction
types
paper-disjoint split
domain split
gold evidence
manual review
rejection criteria
Oracle-v2
```

Mention limitations clearly.

---

# 41. Evaluation protocol

Specify:

```text datasets
baselines
primary metrics
latency metrics
cost accounting
statistical method
human review
```

The reader should be able to reproduce the evaluation logic without inspecting your private conversation history.

---

# 42. Main-results section

Structure:

```text retrieval result
↓
answer result
↓
citation result
↓
efficiency result
```

Then explain:

```text why the improvement happened
```

using rescue/failure analysis.

---

# 43. Ablation section

Use ablations to answer:

```text Which component matters?
```

Do not use ablations merely to demonstrate that every feature exists.

---

# 44. Robustness section

Report:

```text paper-disjoint
cross-domain
threshold
retrieval perturbation
graph quality
```

only where measured.

The purpose is to establish:

```text stability
```

not:

```text more charts
```

---

# 45. Failure-analysis section

This should explain:

```text what the system still cannot do
```

Use actual examples and counts.

This often makes a research project more credible than adding another architectural component.

---

# 46. Limitations section

At minimum consider:

```text benchmark scale
corpus scope
domain coverage
PDF extraction
graph relation extraction
small-data learning
LLM evaluation dependence
provider variability
exact-gold conservatism
```

Only list limitations that actually apply.

---

# 47. Conclusion

The conclusion should answer:

```text What did the study establish?

What remains uncertain?

What is the strongest operational takeaway?
```

Do not repeat the entire roadmap.

---

# 48. Research contribution framing

The final contribution may be:

```text an adaptive scientific-RAG methodology

a selective graph-assisted retrieval policy

an empirical study of scientific evidence structure

a provenance-aware evaluation pipeline

a benchmark/evaluation methodology
```

The actual choice follows the final evidence.

---

# 49. Do not force novelty

A project can be strong without a new foundational algorithm.

Possible value can come from:

```text careful benchmark design
controlled ablations
failure analysis
cross-domain evaluation
operational cost analysis
```

The paper should say what is genuinely new or useful.

---

# 50. Final limitation of causal attribution

A multi-component final architecture can show:

```text overall improvement
```

without proving that:

```text every component caused it
```

Use:

```text component ablations
```

for attribution.

Keep final wording proportional to the experimental design.

---

# 51. Final operational claim

A good operational claim has the structure:

```text under condition X,
system Y produced outcome Z
at cost C,
compared with baseline B.
```

Avoid:

```text system Y is better
```

without defining:

```text better at what
under which benchmark
at what cost
```

---

# 52. Release README

The public README should include:

```text title
one-line project description
architecture
features actually validated
benchmark summary
main result
limitations
setup
run instructions
reproduction
citation
```

Keep the README concise.

Link to:

```text detailed research documentation
```

for chronology and deep methodology.

---

# 53. README result discipline

Do not put:

```text projected improvement
target future feature
unvalidated model
```

in the result section.

Use:

```text measured
```

only.

---

# 54. Portfolio page

The project page can contain:

```text problem
why it matters
architecture
research question
results
demo
GitHub
paper/report
```

Avoid turning it into:

```text giant technical diary
```

---

# 55. Resume entry

A strong resume format is:

```text AtlasRAG — Adaptive Scientific RAG

Built and evaluated ...
Designed ...
Measured ...
```

Every numeric claim must trace to:

```text final result artifact
```

Use only validated components.

---

# 56. Technical interview preparation

Prepare concise answers to:

```text Why RAG?

Why adaptive routing?

Why Oracle-v2?

Why not train Compass earlier?

Why V3?

Why scientific structure?

Why graph?

Why selective graph invocation?

How did you prevent leakage?

How did you measure cost?

What failed?

What would you change next?
```

The answer to each should reference:

```text evidence
```

rather than:

```text personal preference alone
```

---

# 57. Research defense questions

Be ready for:

```text Is this actually novel?

Why this benchmark?

Why these baselines?

Why not a stronger LLM?

Does graph improvement come from more context?

Does the router see the answer?

Is there train/test leakage?

Why is exact gold recall conservative?

How does it transfer?

What happens on negative cases?
```

Prepare answers from the documented experiments.

---

# 58. Reproduction guide

The final repository should contain a clear path:

```text setup
↓
data preparation
↓
index construction
↓
benchmark verification
↓
evaluation
↓
analysis
↓
figures
```

Use actual script names and paths.

Do not publish placeholder commands as though they were tested.

---

# 59. Clean-machine reproduction

Perform at least one final reproduction attempt from:

```text fresh environment
```

Verify:

```text tests
benchmark loading
index loading/building
final evaluation
result generation
```

Record:

```text success/failure
environment
commit
```

---

# 60. Hidden-state audit

Search for dependencies on:

```text local caches
absolute paths
manual files
undeclared environment variables
untracked benchmark edits
local model directories
```

Fix only actual release blockers.

Do not rewrite the architecture during cleanup.

---

# 61. Secret audit

Before pushing public code inspect:

```text .env
logs
configs
notebooks
screenshots
JSON outputs
```

for:

```text API keys
access tokens
private URLs
credentials
personal paths
```

Never publish real secrets.

---

# 62. Data licensing audit

For every included dataset/source verify:

```text source
license
redistribution status
derived-data restrictions
```

If papers cannot be redistributed:

```text publish identifiers/hashes/metadata
```

instead of restricted content.

---

# 63. Final artifact structure

A useful release layout is:

```text
AtlasRAG/
├── src/
├── scripts/
├── configs/
├── tests/
├── docs/
│   ├── benchmark/
│   ├── experiments/
│   └── reproducibility/
├── figures/
├── data/
│   └── manifests/
└── README.md
```

Use the actual repository layout where practical.

Do not reorganize folders merely for aesthetics if it risks breaking history or scripts.

---

# 64. Final documentation bundle

Recommended:

```text
FINAL_PROJECT_CONTEXT.md
FINAL_RESEARCH_SUMMARY.md
FINAL_EVALUATION.md
FINAL_REPRODUCIBILITY.md
FINAL_DECISION.md
FINAL_RELEASE_MANIFEST.json
```

The existing weekly files should remain as chronology.

---

# 65. Final AI-agent handoff

Create a compact future-agent handoff containing:

```text project purpose
current architecture
final benchmark
final corpus
final result
known limitations
frozen files
how to reproduce
safe next directions
```

This prevents a future AI agent from rebuilding the project from scratch.

---

# 66. Future work policy

Create two lists:

```text evidence-supported future work
```

and:

```text speculative ideas
```

Evidence-supported future work should come from:

```text observed failure modes
```

Speculative ideas can include:

```text multimodal retrieval
symbolic reasoning
larger graph systems
additional domains
```

but must be labeled speculative.

---

# 67. When to create V8

Only create a V8 when:

```text final evidence reveals a meaningful unresolved problem
```

and:

```text a new experiment can isolate it
```

Do not create V8 because:

```text the roadmap looks empty
```

Stopping is a valid research outcome.

---

# 68. Stop condition

AtlasRAG can be considered complete for this research cycle when:

```text final benchmark locked
+
final architecture locked
+
main baselines measured
+
end-to-end results measured
+
robustness measured
+
major failures understood
+
human/audit subset completed
+
reproducibility checked
+
paper/report written
+
release package ready
```

Anything beyond this should have a new research question.

---

# 69. Final decision record

Create:

```text FINAL_DECISION.md
```

with:

```text STATUS

Primary research question

Final architecture

Strongest baseline

Main positive result

Main negative result

Strongest limitation

Operational tradeoff

Generalization result

Recommended public claim

Deferred research
```

This should be the single source of truth for the final project status.

---

# 70. Final claim labels

For every candidate claim use:

```text SUPPORTED
PARTIALLY_SUPPORTED
NOT_SUPPORTED
NOT_TESTED
```

Examples:

```text adaptive routing improves efficiency

selective graph escalation helps difficult questions

graph transfer works cross-domain

verification reduces unsupported claims

structure-aware retrieval improves quantitative evidence
```

Only supported claims should appear as factual headline statements.

---

# 71. Final public-claim audit

Search:

```text README
paper
slides
portfolio
resume
demo
repository comments
```

for words like:

```text novel
first
best
state-of-the-art
eliminates
guarantees
universal
significant
```

For each occurrence ask:

```text Is the wording supported?
```

Replace overclaims with precise language where necessary.

---

# 72. Final statistical-wording audit

Be careful with:

```text significant
proves
demonstrates
causes
outperforms
generalizes
```

Use:

```text statistically significant
observed improvement
is associated with
under the evaluated setting
```

when that is what the evidence actually supports.

---

# 73. Final source citation audit

Every external factual statement in the paper/report should have a source where appropriate.

For literature claims:

```text cite the original or authoritative source
```

For project results:

```text cite internal result artifact / table
```

Do not present remembered external facts as though they came from the AtlasRAG experiments.

---

# 74. Fresh literature requirement

Before final publication:

```text repeat the literature search
```

for topics that have changed rapidly.

This includes:

```text RAG routing
graph RAG
scientific RAG
retrieval uncertainty
evidence verification
cross-domain scientific QA
```

The final related-work section should reflect the literature available at the time of publication.

---

# 75. Paper reproducibility checklist

```text
[ ] benchmark version
[ ] corpus version
[ ] split rules
[ ] retrieval config
[ ] model versions
[ ] prompts
[ ] graph version
[ ] V3 version
[ ] V2 version
[ ] evaluation metrics
[ ] statistical methods
[ ] cost accounting
[ ] latency accounting
[ ] human-review method
[ ] failure taxonomy
[ ] code commit
```

---

# 76. Final release checklist

```text
[ ] tests pass
[ ] clean reproduction works
[ ] secrets removed
[ ] licenses reviewed
[ ] README updated
[ ] architecture matches final system
[ ] result numbers verified
[ ] figures regenerated
[ ] manifests saved
[ ] benchmark hash saved
[ ] corpus manifest saved
[ ] experiment registry saved
[ ] final decision saved
[ ] historical artifacts preserved
[ ] Git tag/release created
```

---

# 77. Release version

Use a clear release identifier.

For example:

```text v1.0-research
```

or an equivalent project convention.

The release should correspond to:

```text frozen final commit
```

Do not tag a moving branch without recording exactly what was released.

---

# 78. Final Git sequence

Before release:

```powershell
git status --short
git diff

python -m pytest -q

git log --oneline --decorate -10
```

Then commit:

```text final research lock
```

and create the release/tag.

Verify:

```text clean working tree
```

afterward where practical.

---

# 79. Final reproducibility command set

Use actual project commands after repository inspection.

Conceptually:

```powershell
cd <AtlasRAG-repo>

$env:PYTHONPATH="src"

python -m pytest -q

python scripts/<verify-benchmark>.py

python scripts/<final-evaluation>.py

python scripts/<final-analysis>.py
```

Do not publish nonexistent script names.

---

# 80. Final output verification

Check:

```text result files exist
result counts correct
question IDs complete
no duplicates
tables match raw results
figures match tables
paper numbers match tables
README numbers match final results
```

This is the final consistency audit.

---

# 81. Single-source-of-truth principle

The preferred dependency is:

```text raw experiment artifacts
        ↓
analysis
        ↓
final tables
        ↓
figures
        ↓
paper/README
```

Not:

```text paper
→ manually copy numbers
→ README
→ slides
```

This prevents divergence.

---

# 82. Final presentation

A compact final presentation can use:

```text Slide 1
Problem

Slide 2
AtlasRAG architecture

Slide 3
Research questions

Slide 4
Benchmark

Slide 5
Baseline

Slide 6
Adaptive / graph approach

Slide 7
Main results

Slide 8
Cost + latency

Slide 9
Robustness

Slide 10
Failure analysis

Slide 11
Limitations

Slide 12
Conclusion
```

Only include slides needed for the audience.

---

# 83. Live-demo safety

For demos:

```text use frozen corpus
use tested commands
avoid experimental provider settings
avoid hidden fallback code
```

Have a known-good local/demo path where appropriate.

Do not rely on:

```text live provider behavior
```

for every presentation unless unavoidable.

---

# 84. Backup demo assets

Keep:

```text screenshots
recording
sample outputs
architecture diagram
```

as backup.

A live demo should not be the only way to demonstrate the project.

---

# 85. Final portfolio narrative

The portfolio should tell a coherent story:

```text problem
↓
initial baseline
↓
measurement exposed weakness
↓
controlled research iteration
↓
adaptive retrieval
↓
evidence structure
↓
graph
↓
selective escalation
↓
robustness
↓
final evaluation
```

This makes the project look like:

```text research + engineering
```

rather than:

```text a collection of unrelated features
```

---

# 86. Interview one-minute explanation

Prepare a concise explanation such as:

```text AtlasRAG is a scientific RAG system designed around the problem
that stronger retrieval is useful but expensive and flat retrieval
can miss structured or multi-step evidence.

I built a benchmark and Oracle reference, tested routing and
retrieval-state failure prediction, added scientific evidence
structure and provenance-aware graph retrieval, and evaluated
selective escalation plus citation/evidence verification.

The final claims are based on controlled, paper-disjoint,
end-to-end evaluation rather than the architecture alone.
```

Adjust this wording to the actual final result.

---

# 87. Interview five-minute explanation

Be able to explain:

```text corpus
→ chunking
→ retrieval
→ reranking
→ routing
→ V3
→ graph
→ answer
→ V2
```

and:

```text why each component exists
```

Use actual experiments rather than hypothetical explanations.

---

# 88. Strongest technical questions to prepare

Be ready to answer:

```text Why hybrid retrieval?

Why bge-small?

Why the reranker?

Why Oracle-v2?

Why was UNCERTAIN separated from insufficiency?

Why is question-only Compass constrained?

How did you prevent evidence leakage?

How did you select the threshold?

How did you compare graph with semantic expansion?

How did you account for provider costs?

How did you handle 429s?

How did you evaluate citations?

How did you audit benchmark quality?
```

These questions expose whether the methodology is actually understood.

---

# 89. Strongest research questions to prepare

```text What is novel?

What is not novel?

What is the strongest baseline?

What is the largest limitation?

What result surprised you?

Which component could be removed?

What negative result changed the roadmap?

How does the system generalize?

What would invalidate your main claim?
```

A good answer should be evidence-based and honest.

---

# 90. What would invalidate the final claim?

Document explicitly.

Examples:

```text benchmark leakage discovered

result cannot be reproduced

effect disappears under strong paper-disjoint evaluation

graph benefit disappears under matched context budgets

answer quality does not improve despite retrieval gains
```

This is a useful scientific integrity check.

---

# 91. Final uncertainty statement

The final report should state what remains uncertain.

Possible:

```text limited domain coverage

small subset for human audit

provider-dependent evaluation

conservative exact-gold metric

limited target-domain size
```

The uncertainty statement should match the actual study.

---

# 92. Final research summary template

Create:

```text PROJECT
AtlasRAG

PROBLEM
...

METHOD
...

BENCHMARK
...

PRIMARY RESULT
...

EFFICIENCY RESULT
...

ROBUSTNESS RESULT
...

MAIN FAILURE
...

LIMITATION
...

FINAL STATUS
...

NEXT STEP
...
```

This should be readable without opening the entire chronology.

---

# 93. Final release summary template

Create:

```text Release
Version:

Commit:

Benchmark:

Corpus:

Architecture:

Primary Result:

Known Limitations:

Reproduction:

License/Data notes:

```

This is the public-facing summary.

---

# 94. Final archival strategy

Keep an immutable archive containing:

```text final release source
final configs
benchmark manifest
experiment registry
raw results
analysis outputs
figures
paper/report
decision record
```

Do not rely solely on:

```text GitHub main
```

for the research archive.

---

# 95. Preserve historical chronology

The weekly documents remain valuable because they show:

```text why the architecture changed
```

and:

```text which hypotheses were rejected
```

Do not delete them after publishing.

They form the project's research notebook.

---

# 96. Final future-agent instruction

Any future AI agent entering AtlasRAG after Week 20 should first read:

```text FINAL_PROJECT_CONTEXT.md
FINAL_DECISION.md
FINAL_RESEARCH_SUMMARY.md
FINAL_REPRODUCIBILITY.md
FINAL_RELEASE_MANIFEST.json
```

then inspect:

```text Git status
Git history
final config
final benchmark
```

Only afterward should it propose changes.

---

# 97. Do not reopen closed experiments casually

If a historical question has already been answered with:

```text sufficient evidence
```

do not rerun it merely because:

```text new model exists
```

unless the new model defines a genuinely new research question.

This prevents endless experimentation.

---

# 98. New model discipline

A stronger model can always change:

```text score
```

but that does not mean:

```text research question answered better
```

Only add a new model if the question is:

```text Does the conclusion survive a stronger generation/retrieval model?
```

or another clearly defined comparison.

---

# 99. Benchmark expansion discipline

If more questions are added after Week 20:

```text new benchmark version
```

and:

```text new experiment
```

not:

```text silent final benchmark change
```

The original final result remains frozen.

---

# 100. Research-cycle completion

The first AtlasRAG research cycle can be considered complete when:

```text
benchmark locked
+
system locked
+
results locked
+
claims mapped
+
paper/report complete
+
reproduction verified
+
release published
```

At that point:

```text research cycle = CLOSED
```

and any new work becomes:

```text V8 / new study / follow-up
```

---

# 101. Final Week 20 decision tree

Use:

```text
Were the final results reproducible?
        |
        ├─ NO → repair/reproduce before publication
        |
        └─ YES
             |
             v
Were the primary claims supported?
             |
        ┌────┴────┐
        NO        YES
        |          |
   downgrade      v
   claims      Was the operational tradeoff acceptable?
                  |
             ┌────┴────┐
             NO        YES
             |          |
        research     RELEASE
        prototype
```

This prevents premature publication.

---

# 102. Final rule about negative results

Negative results should remain visible in:

```text paper limitations
supplement
research history
```

as appropriate.

Do not rewrite history so that:

```text every component appears successful
```

A credible research project contains:

```text failed hypotheses
```

and:

```text discarded ideas
```

---

# 103. Final rule about future ideas

Future features belong under:

```text Future Work
```

until they have:

```text implementation
benchmark
evaluation
```

Do not describe:

```text planned
```

as:

```text achieved
```

---

# 104. Final deliverables

By the end of Week 20, the target package is:

```text 1. final source repository

2. frozen benchmark manifest

3. frozen corpus manifest

4. experiment registry

5. raw result artifacts

6. final analysis

7. final figures

8. paper/report

9. reproducibility guide

10. final decision

11. release manifest

12. README / portfolio material
```

---

# 105. Exact execution order

Follow:

```text
1. inspect Week 19 final results
2. freeze final experiment outputs
3. create claim-to-evidence map
4. classify every component
5. verify benchmark/corpus manifests
6. verify raw-result completeness
7. rerun critical statistical analysis
8. regenerate final tables
9. regenerate final figures
10. perform human/audit review
11. run fresh literature review
12. write methodology
13. write results
14. write limitations
15. write conclusion
16. audit every paper claim
17. audit README/resume claims
18. clean release repository
19. run secret/license audit
20. perform clean-machine reproduction
21. create final release manifest
22. create final decision record
23. commit final state
24. create release/tag
25. archive research package
```

Do not add new architecture unless a final verification step reveals an actual blocker.

---

# 106. PowerShell final checklist

Start with:

```powershell
cd <AtlasRAG-repo>

$env:PYTHONPATH="src"

git status --short
git diff
git log --oneline --decorate -10

python -m pytest -q

Get-ChildItem configs
Get-ChildItem data
Get-ChildItem scripts
Get-ChildItem src/atlasrag
```

Then use only the repository's actual final evaluation scripts.

---

# 107. Final test result record

Save:

```text test count
pass count
failure count
environment
commit
```

Do not merely say:

```text tests pass
```

in the paper.

Record the actual verification state.

---

# 108. Final release audit

Before publishing:

```text
[ ] final architecture matches code
[ ] final benchmark matches manifest
[ ] final numbers match raw results
[ ] all graphs/figures regenerated
[ ] paper claims audited
[ ] README audited
[ ] resume claims audited
[ ] secrets removed
[ ] data licenses checked
[ ] clean reproduction done
[ ] final Git commit recorded
[ ] release archive created
```

---

# 109. Final mental model

The whole AtlasRAG cycle is:

```text
BUILD
 ↓
MEASURE
 ↓
FIND FAILURE
 ↓
HYPOTHESIZE
 ↓
CHANGE ONE THING
 ↓
MEASURE AGAIN
 ↓
STRESS TEST
 ↓
INTEGRATE
 ↓
EVALUATE END-TO-END
 ↓
LOCK EVIDENCE
 ↓
WRITE ONLY WHAT THE EVIDENCE SUPPORTS
 ↓
RELEASE
```

The project should now move from:

```text feature development
```

to:

```text evidence-backed scientific communication
```

---

# 110. Final rule for the next AI agent

Start from the actual Week 19 results and final repository state.

Do not assume the planned architecture is the final architecture.

Do not change the final benchmark after seeing results.

Do not tune the final system while writing the paper.

Do not cherry-pick favorable experiments.

Do not erase failed experiments.

Do not call an implementation validated without evaluation evidence.

Do not claim novelty without a fresh literature review.

Do not claim causality where only ablation-level association exists.

Do not claim generalization outside evaluated domains.

Do not claim production readiness from a research prototype.

Do not publish secrets or restricted data.

Do not manually rewrite result numbers across documents.

Do not create V8 merely because the roadmap can continue.

The correct final workflow is:

```text
inspect final evidence
↓
classify what is actually supported
↓
freeze benchmark/corpus/configuration
↓
reconcile raw results
↓
rerun critical analysis
↓
regenerate tables/figures
↓
audit claims
↓
write paper/report
↓
verify reproduction
↓
audit code/data/secrets
↓
create release manifest
↓
commit and tag
↓
publish
↓
close research cycle
```

That is Week 20.
