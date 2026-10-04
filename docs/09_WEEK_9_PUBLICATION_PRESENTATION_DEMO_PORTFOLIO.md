# AtlasRAG — Week 9: Publication, Presentation, Demo & Portfolio Packaging

## 1. Purpose

Week 8 turned the AtlasRAG work into a controlled research package.

Week 9 is different.

The goal is no longer to improve the research system. The goal is to **package the finished work so that another person can understand it, evaluate it, reproduce it, and quickly see why it matters**.

The main question becomes:

> How should AtlasRAG be presented so that the technical work, experimental evidence, limitations, and practical value are all visible without exaggerating the results?

The outputs of this phase are:

```text
research summary
paper/report
figures/tables
presentation
demo
GitHub README
portfolio description
resume bullets
project screenshots
final handoff
```

The central rule is:

> **Do not create a stronger-looking story than the locked evidence supports.**

Week 9 is a packaging phase, not another optimization phase.

---

# 2. What Week 9 starts from

Week 9 begins from the locked or near-locked state established in Week 8.

The expected research chain is:

```text
benchmark
   ↓
retrieval evaluation
   ↓
routing evaluation
   ↓
selective escalation
   ↓
answer evaluation
   ↓
failure analysis
   ↓
final system decision
   ↓
reproducible artifacts
```

The final presentation should preserve this causal chain.

Do not reduce AtlasRAG to:

```text
"I built a RAG chatbot."
```

The distinctive technical story is closer to:

```text
scientific RAG
+
adaptive retrieval routing
+
hybrid retrieval
+
empirical Oracle-v2 reference
+
selective escalation
+
controlled evaluation
+
evidence/citation analysis
```

Only include components that actually exist in the final repository.

---

# 3. Final audience model

AtlasRAG may be viewed by several audiences.

They need different levels of detail.

### Recruiter

Needs to understand:

```text
what was built
why it is technically interesting
what you personally engineered
what was measured
```

They normally do not need every benchmark-generation rule.

### Technical reviewer

Needs:

```text
architecture
retrieval design
routing design
benchmark construction
metrics
experiments
failure cases
limitations
```

### Research reader

Needs:

```text
problem formulation
experimental controls
Oracle definition
benchmark limitations
statistical analysis
reproducibility
```

### Demo viewer

Needs:

```text
question
answer
citations
route
evidence
latency
```

The same project can support all four audiences without using the same document for all four.

---

# 4. The four-layer documentation system

Keep these separate.

```text
Layer 1
README
```

Purpose:

```text
understand the project in 2–5 minutes
```

```text
Layer 2
research report / paper
```

Purpose:

```text
understand the method and evidence deeply
```

```text
Layer 3
reproducibility documentation
```

Purpose:

```text
re-run the system
```

```text
Layer 4
presentation/demo
```

Purpose:

```text
communicate the idea quickly
```

Do not paste the entire research report into the README.

Do not hide important experimental caveats only inside a large technical document.

---

# 5. Final project narrative

The most useful narrative structure is:

```text
Problem
  ↓
Why fixed retrieval is insufficient
  ↓
AtlasRAG idea
  ↓
How routing works
  ↓
How retrieval works
  ↓
How the benchmark was built
  ↓
How the systems were compared
  ↓
What happened
  ↓
Where it failed
  ↓
What the final system actually demonstrates
```

A concise opening can be built around:

> Scientific questions vary substantially in retrieval difficulty. AtlasRAG investigates whether the retrieval strategy can be selected adaptively instead of forcing every question through the same expensive path.

Then explain:

```text
simple question
    ↓
cheap retrieval
```

versus:

```text
complex/uncertain question
    ↓
stronger retrieval
```

The exact routing behavior must match the implemented system.

---

# 6. The one-slide architecture

The architecture diagram should communicate the full system without showing implementation clutter.

A recommended conceptual diagram is:

```text
                     User Question
                           |
                           v
                     Routing Layer
                           |
              +------------+------------+
              |                         |
              v                         v
          Simple Route            Strong/Complex Route
              |                         |
              +------------+------------+
                           |
                           v
                 Hybrid Retrieval
                           |
                +----------+----------+
                |                     |
                v                     v
              Dense                 BM25
                \                     /
                 \                   /
                  +------ RRF -------+
                           |
                           v
                       Reranker
                           |
                           v
                    Evidence Context
                           |
                           v
                    Answering LLM
                           |
                           v
                 Answer + Citations
```

If Compass/Hybrid is not part of the final measured system, do not draw it as though it is.

The architecture shown in the presentation should reflect the final selected system, not the original roadmap.

---

# 7. The research-question slide

The presentation should have one explicit research question.

A strong current framing is:

> **Can a lightweight adaptive routing policy retain the evidence quality of a strong retrieval policy while reducing unnecessary retrieval or LLM cost, relative to fixed and empirical-oracle references?**

Keep the wording scoped.

The benchmark is:

```text
small
curated
scientific
astrophysics/cosmology-oriented
```

Therefore do not phrase the question as:

```text
Can adaptive routing solve RAG?
```

or:

```text
Can AtlasRAG produce state-of-the-art scientific answers?
```

Those statements are much broader than the evidence.

---

# 8. Problem-motivation slide

Explain why adaptive routing is useful.

The simplest visualization is:

```text
Every question
      |
      v
strong retrieval
      |
      v
high cost
```

versus:

```text
Every question
      |
      v
question difficulty
   /          \
simple       difficult
  |             |
cheap path   strong path
```

The intuition is:

```text
not every question requires the same retrieval effort
```

The research problem is whether that intuition can be measured rather than assumed.

---

# 9. Retrieval slide

The retrieval baseline should be shown clearly.

Current documented baseline:

```text
Embedding:
BAAI/bge-small-en-v1.5

Dense retrieval:
k = 20

BM25:
k = 20

Fusion:
RRF, k = 60

Reranker:
cross-encoder/ms-marco-MiniLM-L-6-v2

Chunking:
max_chars = 1800
overlap = 200
min_chars = 200
```

Do not display these as final settings until Week 8 has verified that they are the actual final configuration.

If a Week 6 ablation selected a different configuration, use the selected configuration and preserve the baseline as an ablation reference.

---

# 10. Routing slide

Explain routing at the conceptual level first.

Possible structure:

```text
Question
   ↓
Router
   ↓
predicted strategy
   ↓
retrieval policy
```

The strategy classes currently used in the project are:

```text
SIMPLE
MULTI_HOP
UNCERTAIN
```

The final slide must explain what these labels actually mean in the final implementation.

Do not imply that these labels are universal semantic categories.

They are supervision classes derived from the project benchmark and Oracle formulation.

---

# 11. Oracle-v2 slide

Oracle-v2 deserves its own slide because it is central to the research design.

The conceptual process is:

```text
evaluate each strategy
        ↓
measure gold-evidence recall
        ↓
find best recall
        ↓
choose cheapest strategy within epsilon of best
```

Therefore:

```text
Oracle-v2 =
empirical benchmark-specific reference
```

not:

```text
perfect intelligent router
```

This distinction must be visible in both the paper and presentation.

---

# 12. Why Oracle-v2 is useful

The Oracle is not presented as a deployment mechanism.

It answers a different question:

> If we knew the benchmark's observed retrieval outcomes, which tested strategy would have been sufficient at the lowest measured cost?

This creates a useful target for routing research.

The comparison becomes:

```text
fixed baseline
      vs
LLM routing
      vs
learned routing
      vs
empirical Oracle reference
```

That makes the research question more precise than simply comparing chatbot answers.

---

# 13. Benchmark slide

The benchmark should be described honestly.

Current documented state:

```text
27 accepted questions
18 Oracle-v2 sufficient
9 Oracle-v2 insufficient
```

Oracle-v2 label distribution:

```text
SIMPLE       18
MULTI_HOP     7
UNCERTAIN     2
```

The earlier v1 labels were:

```text
SIMPLE       11
MULTI_HOP     5
UNCERTAIN    11
```

The important lesson is that v1's `UNCERTAIN` category partly mixed together:

```text
true routing uncertainty
+
retrieval insufficiency
```

Oracle-v2 separates this more cleanly.

Do not describe the 27-question benchmark as balanced.

Do not hide the 9 retrieval-insufficient cases.

---

# 14. Benchmark-quality slide

A short slide can show the construction pipeline:

```text
candidate generation
      ↓
structural validation
      ↓
support audit
      ↓
manual review
      ↓
retrieval evaluation
      ↓
Oracle-v2 labeling
```

This is important because scientific QA benchmark quality is part of the result.

Explain that generation is not the final acceptance criterion.

A question can be rejected because:

```text
answer not supported
required passage relationship is weak
temporal relationship is invalid
chain is unsupported
numeric relationship is incompatible
question is redundant
```

Use only the checks actually implemented in the repository.

---

# 15. Experimental matrix slide

Do not display a giant table of every pilot.

Display the final experimental families.

For example:

```text
B
Static baseline

C1
Original LLM router

C2
Oracle-aligned LLM router

D
Compass

Hybrid
Compass + selective fallback

E2
Oracle-v2 reference
```

Then attach status:

```text measured
not measured
deferred
reference only
```

Never show a planned system as completed.

---

# 16. Historical vs final results

The project has historical Run 1 results.

They should remain clearly labeled.

Historical Run 1:

```text
A Vanilla       0.52
B Static        0.63
C LLM Router    0.70
E Oracle        0.76
F Always Strong 0.76
G Always Multi  0.72
K Static K10    0.65
```

Paired findings:

```text
E vs B   +0.13   CI [.04,.26]
F vs B   +0.13   CI [.04,.26]
C vs B   +0.07   CI [-.02,.20]
C vs F   -.06    CI [-.13,0]
G vs F   -.04    CI [-.09,0]
```

These values are historical.

If final experiments use another benchmark/configuration, present the final numbers separately.

Never silently merge the tables.

---

# 17. Result presentation rule

Every important number should answer four questions:

```text
what metric?
on what benchmark?
under what configuration?
from what experiment?
```

For example, avoid:

```text
AtlasRAG achieved 76% recall.
```

Prefer:

```text
On the frozen Run 1 benchmark, the empirical Oracle reached 0.76 evidence recall under the tested strategy ladder.
```

The second sentence is much harder to misunderstand.

---

# 18. Cost-quality visualization

A particularly useful final figure is:

```text
Quality
  ^
  |
  |             Oracle
  |       Strong retrieval
  |
  |   Static
  |
  +--------------------------> Cost
```

The actual coordinates must come from final measurements.

Another useful figure:

```text
Answer quality
      ^
      |
      |         Hybrid
      |       /
      |  Compass
      | /
      +------------------> latency/cost
```

Again, do not invent positions.

The main goal is to show the tradeoff frontier rather than crown a winner from one metric.

---

# 19. Failure-analysis slide

The final presentation should include at least one failure slide.

Recommended taxonomy:

```text
Retrieval failure
Routing failure
Query decomposition failure
Evidence interpretation failure
Unsupported generation
Citation failure
Numeric/unit error
Incomplete answer
Infrastructure failure
```

Then show one concrete case.

Example format:

```text
Question
    ↓
selected route
    ↓
retrieved evidence
    ↓
what went wrong
    ↓
root cause
```

A failure slide often demonstrates more engineering maturity than another accuracy percentage.

---

# 20. Retrieval-vs-generation diagnosis

One of the strongest analysis visuals is a four-way table:

| Retrieval sufficient | Answer correct | Interpretation |
|---|---|---|
| Yes | Yes | desired outcome |
| Yes | No | generation/evidence interpretation issue |
| No | Yes | alternative evidence or model prior may have helped |
| No | No | retrieval/routing likely contributed |

This prevents a wrong answer from automatically being classified as a retrieval failure.

It also prevents a correct answer from automatically being called grounded.

---

# 21. Citation slide

Explain that AtlasRAG does not treat citations as decoration.

The important properties are:

```text citation exists
citation maps to retrieved evidence
citation supports attached claim
required claims are covered
```

A strong demo should visibly connect:

```text Answer claim
    ↓
Citation
    ↓
Source chunk
    ↓
Paper
```

This is one of the clearest ways to demonstrate scientific RAG value.

---

# 22. Demo design

The live demo should be intentionally simple.

Recommended screen:

```text +--------------------------------------+
| AtlasRAG                               |
|                                      |
| Ask a scientific question...         |
| [_________________________________]  |
|                                      |
|              [ Ask ]                 |
|                                      |
| Answer                               |
| -----------------------------------  |
| response text                       |
|                                      |
| Sources                              |
| [Paper / section / citation]         |
| [Paper / section / citation]         |
|                                      |
| Route: SIMPLE                        |
| Retrieval: Hybrid                    |
| Latency: <measured>                  |
+--------------------------------------+
```

The demo should make the core idea visible:

```text route
→ retrieve
→ answer
→ cite
```

Do not expose internal logs unless they help explain the routing decision.

---

# 23. Demo question selection

Choose questions that demonstrate different behaviors.

Ideal set:

```text one simple question
one multi-hop question
one question requiring stronger retrieval
one question involving conflicting evidence
```

Do not use only the easiest question because it produces a visually perfect answer.

For each demo question, verify:

```text final answer is stable
citations are correct
source chunks exist
latency is acceptable
provider failures are handled
```

Do not use a question that is known to fail unless the purpose is explicitly demonstrating failure analysis.

---

# 24. Demo safety rule

Never expose:

```text API keys
environment variables
private file paths
provider credentials
raw error traces containing secrets
internal benchmark answers
gold evidence used only for evaluation
```

The demo should run through the normal application path.

Do not hard-code an answer merely to make a demo look better.

---

# 25. GitHub README final structure

Recommended final README:

```text
AtlasRAG
Scientific RAG with Adaptive Retrieval Routing

1. Overview
2. Research question
3. Why adaptive retrieval?
4. Architecture
5. Retrieval stack
6. Routing strategy
7. Evaluation
8. Results
9. Failure analysis
10. Demo
11. Setup
12. Run locally
13. Repository structure
14. Limitations
15. References
```

Keep the README concise.

The detailed benchmark/research history should live elsewhere.

---

# 26. README opening section

The first screen should answer:

```text
What is AtlasRAG?
What makes it different?
What was measured?
```

A useful format is:

```text
AtlasRAG is a scientific RAG system for astrophysics/cosmology research papers.

Instead of forcing every question through the same retrieval path,
AtlasRAG investigates adaptive retrieval routing, using benchmark-derived
strategy supervision and hybrid dense/BM25 retrieval.

The project evaluates evidence coverage, answer quality, grounding,
citation quality, latency, and LLM cost under controlled experiments.
```

Only retain statements that match the final implementation.

---

# 27. README architecture image

The README should include one strong architecture graphic rather than many unrelated screenshots.

Recommended visual sequence:

```text
Question
   ↓
Router
   ↓
Retrieval strategy
   ↓
Dense + BM25
   ↓
Reranker
   ↓
Evidence
   ↓
Answer + citations
```

A second image can show the live application.

Avoid decorative diagrams that add no information.

---

# 28. README results section

The final results section should have one compact table.

Possible structure:

| System | Evidence Recall | Answer Correctness | Groundedness | p50 Latency | Tokens/Query | Status |
|---|---:|---:|---:|---:|---:|---|
| Static | | | | | | |
| C1 | | | | | | |
| C2 | | | | | | |
| Compass | | | | | | |
| Hybrid | | | | | | |
| Oracle-v2 | | | | | | |

Do not fill cells with estimates.

Use:

```text
—
```

for unavailable values rather than fabricating a result.

---

# 29. README limitations section

The README should contain a short limitations section.

The current project has obvious boundaries:

```text
small benchmark
small scientific corpus
sparse difficult-question classes
Oracle is benchmark-specific
gold-chunk recall is conservative
provider/API behavior can vary
evaluation-model bias may exist
```

The exact final list must be updated from Week 8.

A limitation statement increases credibility when it is specific.

---

# 30. Research report structure

A formal report can use:

```text
Abstract

1. Introduction

2. Problem Formulation

3. AtlasRAG Architecture

4. Scientific Benchmark Construction

5. Retrieval System

6. Routing Strategies

7. Empirical Oracle-v2

8. Compass / Learned Routing

9. Selective Escalation

10. Retrieval Ablations

11. End-to-End Answer Evaluation

12. Results

13. Failure Analysis

14. Limitations

15. Conclusion
```

Do not force empty sections into the report.

If Compass was deferred, state that clearly and restructure the report rather than writing a fictional training result.

---

# 31. Abstract template

The abstract should contain four parts:

```text
problem
method
evaluation
result
```

Template:

> Scientific RAG systems can face questions with substantially different retrieval requirements, yet fixed retrieval policies apply the same computational budget to every query. AtlasRAG investigates adaptive retrieval routing over an astrophysics/cosmology paper corpus. The system combines hybrid dense/BM25 retrieval with benchmark-derived strategy supervision and an empirical Oracle-v2 reference. Evaluation separates evidence recall from final answer correctness, grounding, citation quality, latency, and model cost. On the curated benchmark, the experiments show [final measured finding]. The results also identify [main limitation/failure mode], motivating [bounded future work].

Do not insert numerical results until Week 8 is frozen.

---

# 32. Conclusion-writing rule

The conclusion should not repeat every experiment.

Use:

```text
What we tested
      ↓
What we found
      ↓
What that means
      ↓
What remains unresolved
```

A good conclusion can have three paragraphs:

```text
1. Main result
2. Engineering/research interpretation
3. Limitations + next research direction
```

Do not add a claim merely because it sounds like a strong ending.

---

# 33. Presentation structure

A practical 8–10 slide deck:

```text
1. Title
2. Problem + motivation
3. AtlasRAG architecture
4. Adaptive routing idea
5. Benchmark + Oracle-v2
6. Retrieval/evaluation methodology
7. Results
8. Failure analysis
9. Live demo / system
10. Conclusion + limitations
```

Optional:

```text
11. Detailed methodology
12. Reproducibility
```

For a short interview/demo, slides 1–9 are enough.

---

# 34. Presentation storytelling order

Do not start with:

```text
BGE model
RRF
cross-encoder
BM25
```

Start with the problem.

Use:

```text
Different questions need different retrieval effort.
                    ↓
Can we predict which retrieval strategy is sufficient?
                    ↓
Here is our benchmark-derived formulation.
                    ↓
Here is AtlasRAG.
                    ↓
Here is what happened.
```

Only then introduce implementation details.

---

# 35. Resume positioning

The project belongs under:

```text
Projects
```

rather than a vague:

```text
AI
```

section.

The bullet should combine:

```text
technical mechanism
+
research method
+
measured result
```

Template:

> Built AtlasRAG, a scientific RAG system with adaptive retrieval routing, hybrid dense/BM25 retrieval, and empirical Oracle-aligned evaluation; measured evidence quality, grounding, citation quality, latency, and LLM cost across controlled routing and retrieval experiments.

A second bullet can focus on the benchmark:

> Designed and audited a scientific QA benchmark with structural support checks, Oracle-v2 strategy labels, retrieval sufficiency analysis, and per-question failure diagnostics.

Use numerical claims only after the final result manifest is frozen.

---

# 36. Portfolio project description

For a portfolio page, target approximately:

```text
100–180 words
```

Include:

```text
why
what
how
result
demo
GitHub
```

Do not copy the entire research abstract.

A portfolio reader should understand the project without knowing what Oracle-v2 means.

The technical details can be progressively disclosed.

---

# 37. Technical-interview explanation

Prepare a one-minute answer:

```text
AtlasRAG is a scientific RAG system I built around a research question:
whether every scientific query needs the same retrieval effort.

I built a hybrid dense/BM25 retrieval stack, created a curated benchmark,
and defined an empirical Oracle that identifies the cheapest tested strategy
that achieves near-best evidence recall.

I then compared fixed retrieval, LLM routing, learned routing where available,
and selective escalation, while separating retrieval quality from final answer
quality, citation quality, latency, and LLM cost.

The interesting part is that I did not treat the router as the final result;
I measured where routing helps, where retrieval becomes the bottleneck, and
where the answer model still fails even with sufficient evidence.
```

Replace the placeholder concept of learned routing with its actual final state.

---

# 38. Questions you should be ready to answer

A reviewer may ask:

```text
Why not always use the strongest retrieval strategy?
```

Answer with measured cost/quality evidence.

```text
Why is the Oracle useful?
```

Explain it is a benchmark-specific empirical reference, not a deployable oracle.

```text
How were routing labels created?
```

Explain the Oracle-v2 ladder and sufficiency rule.

```text
Why not train directly on retrieved context?
```

Explain that the current Compass formulation is question-only and avoids evidence leakage / post-retrieval supervision.

```text
What if another chunk answers the question?
```

Explain the limitation of exact gold-chunk recall.

```text
What is the biggest remaining bottleneck?
```

Use final failure analysis, not intuition.

```text
Why is the benchmark only 27 questions?
```

State the actual scope and explain that quality control was prioritized over inflating the set with weak questions.

---

# 39. Final reproducibility page

The repository should have one obvious place for reproducibility.

For example:

```text
docs/reproducibility.md
```

or the equivalent existing documentation structure.

It should contain:

```text
environment
installation
data requirements
benchmark version
model identifiers
configuration
index building
tests
evaluation command
result locations
known provider limitations
```

The exact commands must be copied from the final checkout.

Do not reconstruct commands from memory.

---

# 40. Reproducibility smoke test

Before declaring the project reproducible:

```text
clone
→ install
→ configure
→ build
→ test
→ sanity query
→ evaluation
```

At minimum, verify:

```powershell
$env:PYTHONPATH="src"
python -m pytest -q
```

Then use the actual final benchmark command from the repository.

The expected output should be documented.

---

# 41. Release artifact strategy

Keep the GitHub repository lightweight.

Commit:

```text
source code
tests
config templates
scripts
documentation
small benchmark metadata
selected result summaries
figures
```

Do not commit:

```text
.env
API keys
large raw PDFs
model caches
local indexes
temporary logs
private provider traces
```

Use external artifact storage only when necessary and document exactly what is required.

---

# 42. Final screenshot set

For a portfolio/GitHub presentation, capture only a few high-value screenshots:

```text
1. Main AtlasRAG interface
2. Answer with citations
3. Route/retrieval diagnostics
4. Architecture/result visualization
```

Avoid ten nearly identical screenshots.

A screenshot should answer a question:

```text
What does it look like?
How does it cite evidence?
How does adaptive routing appear?
What was actually measured?
```

---

# 43. Demo recording structure

A 60–120 second demo is enough.

Suggested sequence:

```text
0–10 sec
Show the question.

10–30 sec
Run the query.

30–50 sec
Show answer + citations.

50–70 sec
Show selected route and retrieval information.

70–100 sec
Open one citation/source chunk.

100–120 sec
Show one research-result visual.
```

Do not spend most of the recording waiting on generation.

Pre-test the exact demo path.

---

# 44. Final visual consistency

Use one visual language across:

```text
README
slides
paper figures
demo UI
portfolio
```

A consistent palette and typography make the project feel finished.

Do not overload the slides with:

```text
gradients
animations
icons
decorative shapes
```

Technical diagrams should remain readable.

A simple clean architecture diagram is more valuable than a heavily styled one.

---

# 45. What belongs in the portfolio vs paper

### Portfolio

Show:

```text
idea
architecture
demo
selected results
engineering depth
```

### Paper/report

Show:

```text
method
controls
benchmark construction
statistics
limitations
full analysis
```

### GitHub

Show:

```text
how to understand
how to run
how to reproduce
where to inspect results
```

Do not force one artifact to do all three jobs.

---

# 46. What not to publish

Do not publish:

```text
API credentials
private papers if redistribution is prohibited
provider logs containing sensitive metadata
unreleased personal information
unsupported claims
benchmark answer keys when they undermine evaluation
```

Check licenses for external datasets/models before redistribution.

The public repository should make it possible to reproduce the method without unnecessarily redistributing material you are not allowed to redistribute.

---

# 47. Final claim-audit checklist

Before publishing any claim, ask:

```text
1. Is there a saved artifact supporting it?

2. Is the artifact from the correct benchmark/version?

3. Was the result actually measured?

4. Can the result be reproduced?

5. Is the scope stated?

6. Could another interpretation explain the result?

7. Is the claim broader than the experiment?
```

If the answer to the last question is yes:

```text
narrow the claim.
```

---

# 48. Numbers that must never be invented

Never invent:

```text
accuracy
recall
latency
cost
token counts
provider calls
Compass performance
fallback rate
citation score
groundedness score
statistical significance
```

For missing data, write:

```text
not measured
not available
deferred
```

rather than a plausible estimate.

---

# 49. Final project “elevator pitch”

A compact project pitch:

> AtlasRAG is a scientific RAG system that studies whether retrieval effort can be adapted to question difficulty instead of using the same expensive retrieval strategy for every query. It combines hybrid dense/BM25 retrieval, benchmark-derived strategy supervision, and an empirical Oracle-v2 reference, then evaluates the full chain from evidence retrieval to answer grounding, citations, latency, and cost.

Only use “studies” or stronger wording according to the final completed experiments.

---

# 50. Final GitHub checklist

Before the release commit:

```text
[ ] README opens cleanly
[ ] architecture image works
[ ] demo instructions work
[ ] setup instructions work
[ ] no secrets tracked
[ ] .gitignore verified
[ ] tests pass
[ ] final result table populated from artifacts
[ ] historical results separated
[ ] limitations included
[ ] reproducibility document linked
[ ] citations/references included
[ ] stale pilots separated or excluded
[ ] repository status clean except intentional release files
```

Use:

```powershell
git status
git diff
git ls-files
git log --oneline --decorate -10
```

before the final commit.

---

# 51. Final release checklist

The project is presentation-ready when:

```text
research:
    final claims locked

code:
    tests pass

benchmark:
    final version identified

results:
    generated from raw artifacts

documentation:
    README + reproducibility instructions complete

demo:
    working on the intended configuration

presentation:
    tells one coherent story

portfolio:
    concise and evidence-based

repository:
    clean and secret-free
```

---

# 52. Do not reopen the experiment loop accidentally

Week 9 is a common point where projects become uncontrolled again.

Avoid:

```text
"one more embedding"
"one more LLM"
"one more benchmark"
"one more router"
"one more prompt"
```

unless the change is deliberately classified as:

```text
new experiment
```

and kept separate from the locked result.

The final release should not move every time a new idea appears.

---

# 53. Future work section

Interesting future directions can be listed without implementing them.

Examples:

```text
larger benchmark
more scientific domains
expert-labeled routing data
retrieval-state-aware routing
learned retrieval policy selection
better confidence calibration
stronger rerankers
efficient embeddings
human expert evaluation
long-context evidence synthesis
multi-model answer generation
```

Future work should be framed as:

```text
motivated by current limitations
```

rather than:

```text
features we forgot to build
```

---

# 54. Suggested final paper figures

A compact paper can use approximately 4–6 major figures:

```text
Figure 1
AtlasRAG architecture

Figure 2
Oracle-v2 / routing formulation

Figure 3
Evidence recall across routing strategies

Figure 4
Quality vs cost/latency

Figure 5
Retrieval-to-answer failure breakdown

Figure 6
Selective escalation / confidence tradeoff
```

Do not create a figure simply because a paper “needs more figures.”

Each figure should answer one analytical question.

---

# 55. Suggested final tables

Useful tables:

```text
Table 1
Corpus + benchmark summary

Table 2
Retrieval configuration

Table 3
Routing/system comparison

Table 4
End-to-end answer metrics

Table 5
Failure taxonomy

Table 6
Reproducibility/configuration manifest
```

For a portfolio project, only Tables 2–4 may be needed.

---

# 56. Case-study format

Select 2–4 final qualitative examples.

Each case study should contain:

```text
Question

Expected retrieval behavior

Selected route

Retrieved evidence

Final answer

Citations

Outcome

Failure/success explanation
```

Choose examples that represent the research question.

Do not select only examples that make the system look perfect.

At least one difficult case can be especially valuable if the diagnosis is clear.

---

# 57. Final qualitative case-study questions

For every selected example, ask:

```text
Did routing make a difference?

Did retrieval make a difference?

Did the answer model use the evidence correctly?

Were citations actually supporting?

What would a fixed strategy have done?

What would Oracle-v2 have selected?
```

This creates a much richer explanation than a single aggregate score.

---

# 58. Final presentation conclusion

End the deck with:

```text
What AtlasRAG demonstrates
```

then three concrete points.

Example structure:

```text
1.
Retrieval requirements vary across scientific questions.

2.
Oracle-aligned evaluation makes that variation measurable.

3.
The value of adaptive routing must be judged jointly on
quality, grounding, latency, and cost.
```

Replace these with the final experimentally supported conclusions.

---

# 59. Week 9 stopping rule

Stop when:

```text
README complete
paper/report complete
slides complete
demo works
portfolio text complete
resume bullets complete
screenshots captured
reproducibility path tested
final repository cleaned
claims audited
```

At this point, the project should move into:

```text
maintenance
submission
interview/demo use
or future research
```

rather than continuous uncontrolled experimentation.

---

# 60. Week 9 final handoff

The final handoff should allow a new AI agent to answer:

```text
What is AtlasRAG?

What problem does it study?

What code implements it?

What benchmark is authoritative?

What experiments were actually run?

What are the final results?

Which results are historical?

What systems are deployable?

What remains incomplete?

What claims are safe?

Where are the artifacts?

How do I reproduce the project?

How do I present it?
```

Keep a compact final status file containing:

```text
ATLASRAG FINAL PROJECT STATUS

Research question:
    <locked wording>

Benchmark:
    <version/hash>

Corpus:
    <version/hash>

Retrieval:
    <final configuration>

Router:
    <final configuration>

Compass:
    <trained/deferred + checkpoint if applicable>

Hybrid:
    <used/not used + threshold if applicable>

Answer model:
    <identifier>

Prompt:
    <version>

Final systems:
    <list>

Primary finding:
    <carefully scoped>

Primary limitation:
    <carefully scoped>

Final commit:
    <hash>

README:
    <path>

Reproducibility:
    <path>

Results:
    <path>

Demo:
    <path/url if applicable>
```

This should be generated or verified from repository state wherever practical.

---

# 61. Week 9 execution order

Use this order.

```text
STEP 1
Verify the Week 8 final state.

STEP 2
Identify the authoritative benchmark, final configuration,
final result files, and final commit.

STEP 3
Build the final result table directly from raw artifacts.

STEP 4
Select 2–4 representative qualitative case studies.

STEP 5
Create the main AtlasRAG architecture diagram.

STEP 6
Create the final result figures.

STEP 7
Write the research report/paper.

STEP 8
Condense the report into presentation slides.

STEP 9
Update the GitHub README.

STEP 10
Prepare the reproducibility path.

STEP 11
Test the live demo on the intended configuration.

STEP 12
Capture final screenshots / demo recording.

STEP 13
Write portfolio description and resume bullets.

STEP 14
Perform a claim and secret audit.

STEP 15
Run the final repository tests.

STEP 16
Create the release commit.

STEP 17
Record the final commit hash.

STEP 18
Update the final status/handoff document.
```

---

# 62. Commands to begin Week 9

Use:

```powershell
$env:PYTHONPATH="src"
```

Then:

```powershell
git status
git log --oneline --decorate -10
python -m pytest -q
```

Inspect final repository structure:

```powershell
Get-ChildItem . -Recurse -File | Select-Object FullName
```

Inspect results:

```powershell
Get-ChildItem .\results -Recurse -File | Select-Object FullName,Length,LastWriteTime
```

Inspect benchmark:

```powershell
Get-ChildItem .\data\bench -File | Select-Object Name,Length,LastWriteTime
```

Inspect documentation:

```powershell
Get-ChildItem .\docs -Recurse -File -ErrorAction SilentlyContinue | Select-Object FullName
```

Inspect README:

```powershell
Get-Content .\README.md
```

Inspect current configuration:

```powershell
Get-Content .\configs\default.yaml
```

Do not edit anything simply because this phase contains a suggested structure.

First inspect the actual checkout.

---

# 63. Final Week 9 principle

> **Finish the communication layer without corrupting the research layer.**

AtlasRAG is complete when the project can be understood at three levels:

```text
30-second explanation
        ↓
5-minute technical explanation
        ↓
full reproducible research trail
```

The final portfolio, README, demo, and paper should all point to the same underlying evidence.

The presentation may be simplified.

The README may be shorter.

The demo may hide implementation details.

But:

```text
the facts must remain consistent.
```

That consistency is what turns AtlasRAG from a collection of experiments into a finished technical project.
