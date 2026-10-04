# AtlasRAG — Week 8: Final Analysis, Reproducibility & Release

## 1. Purpose

Week 8 is the phase where the experiments stop being a collection of runs and become a defensible research result.

By this point, the project should already have separated:

```text
benchmark construction
retrieval quality
routing quality
routing cost
selective escalation
answer generation
```

Week 8 connects those results without collapsing them into one unexplained number.

The main question is no longer:

> What should we build next?

It becomes:

> What can AtlasRAG legitimately claim, what evidence supports each claim, what remains uncertain, and can another person reproduce the reported result?

The final output should be a controlled research package containing:

```text
frozen inputs
exact configurations
raw result artifacts
statistical summaries
failure analysis
final system decision
reproducibility instructions
paper/report material
portfolio/GitHub material
```

The most important rule for this phase is:

> **Do not optimize the story after seeing the results. Lock the evidence, then write the story that the evidence supports.**

---

## 2. What Week 8 starts from

The preceding phases established a useful experimental structure.

### Benchmark

Current benchmark history includes:

```text
27 accepted questions
18 Oracle-v2 sufficient
9 Oracle-v2 insufficient
```

The original v1 Oracle labels were:

```text
SIMPLE      11
MULTI_HOP    5
UNCERTAIN   11
```

Oracle-v2 changed the interpretation to:

```text
SIMPLE      18
MULTI_HOP    7
UNCERTAIN    2
```

with:

```text
9 / 27 retrieval-insufficient under the tested strategy ladder
```

This distinction must remain visible in the final report.

The benchmark is therefore not a large, balanced benchmark. It is a small, curated scientific QA benchmark with difficult classes that remain sparse.

### Historical Run 1

Run 1 is frozen.

Historical approximate retrieval recall results were:

```text
A Vanilla        0.52
B Static         0.63
C LLM Router     0.70
E Oracle         0.76
F Always Strong  0.76
G Always Multi   0.72
K Static K10     0.65
```

Paired analysis established:

```text
E vs B   +0.13   CI [.04,.26]   significant
F vs B   +0.13   CI [.04,.26]   significant
C vs B   +0.07   CI [-.02,.20]  not established
C vs F   -.06   CI [-.13,0]     not established
G vs F   -.04   CI [-.09,0]     not established
```

These numbers describe the historical run only. They must not be silently replaced by later retrieval or benchmark changes.

### Retrieval baseline

The currently documented retrieval baseline is:

```text
Embedding:
    BAAI/bge-small-en-v1.5

Dense k:
    20

BM25 k:
    20

RRF k:
    60

Reranker:
    cross-encoder/ms-marco-MiniLM-L-6-v2

Chunk max_chars:
    1800

Overlap:
    200

Minimum chunk size:
    200
```

### Answer model

The current answering model is:

```text
openai/gpt-oss-20b
```

through the project's Groq-compatible OpenAI API path.

The exact endpoint, model identifier, generation settings, and prompt version used in the final run must be recorded rather than inferred later from memory.

### Current software state

The repository uses a `src/` layout and the working FastAPI launch sequence is:

```powershell
$env:PYTHONPATH="src"
python -m uvicorn atlasrag.api.main:app --reload --port 8000
```

The latest test state reached:

```text
55 passed
```

after the deterministic pair-sourcing and benchmark validation work reported in the project handoff.

The exact current test count must still be re-run at the beginning of Week 8 rather than copied blindly into a final report.

---

## 3. Week 8 deliverables

The phase should produce the following artifacts.

```text
results/final/
    experiment_manifest.json
    benchmark_manifest.json
    system_summary.json
    paired_comparisons.json
    failure_taxonomy.json
    cost_quality_summary.json
    reproducibility.md
    final_notes.md
```

And, where implemented:

```text
results/final/<system>/<question>.json
```

or one JSONL per system.

The final project package should also contain:

```text
README
run instructions
configuration description
benchmark description
experiment table
limitations
citation/reference information
```

A paper/report draft can be generated from these artifacts later. The machine-readable results should exist first.

---

## 4. First task: establish the final experimental lock

Before running more expensive experiments, create a lock describing exactly what is frozen.

At minimum record:

```text
benchmark version
benchmark file hash
corpus version/hash
retrieval configuration
router configuration
Compass checkpoint, if any
answer model
answer prompt version
temperature
token limits
retrieval k values
reranker model
embedding model
Python version
package environment
provider
API mode
commit hash
```

The goal is to make this statement true:

```text
same inputs
+
same code
+
same configuration
→
comparable result
```

### Freeze after validation, not before debugging

Do not freeze a broken experiment merely because a document says it should be frozen.

The practical order is:

```text
debug
→ run tests
→ verify outputs
→ establish configuration
→ freeze
→ final evaluation
```

Once the final lock exists, changing one item creates a new experiment version.

For example:

```text
answer_prompt_v1
```

and later:

```text
answer_prompt_v2
```

are not the same final experiment.

---

## 5. Benchmark versioning is especially important

AtlasRAG has already undergone meaningful benchmark changes.

There are historical artifacts such as:

```text
data/bench/questions.jsonl

data/bench/questions_v1_frozen.jsonl

data/bench/questions_v2.jsonl

data/bench/questions_v2_backup_before_repair.jsonl

data/bench/audit.jsonl
```

The final report must state which file is the authoritative final benchmark.

Do not write:

```text
27-question benchmark
```

without also identifying its version or generation state.

A later benchmark repair can change:

```text
gold passages
Oracle labels
route targets
question difficulty
retrieval reachability
```

and therefore can change every downstream metric.

The final benchmark should be copied or tagged into an immutable experiment directory before final evaluation.

---

## 6. Preserve the historical baseline separately

Run 1 is a historical reference.

Never overwrite:

```text
results/run1/
```

Never replace its configuration files with a later retrieval configuration.

The report should be able to say:

```text
Historical Run 1
```

and:

```text
Final benchmark / final retrieval evaluation
```

without ambiguity.

This matters because later work introduced:

```text
Oracle-v2
benchmark audit
pair-sourcing constraints
retrieval ablations
bounded retry behavior
```

A result obtained after those changes is not automatically comparable to Run 1.

---

## 7. Build a result lineage for every final number

Every important number in the final report should have a path back to a concrete artifact.

Use the following mental model:

```text
reported number
      ↓
summary.json
      ↓
per-question result
      ↓
benchmark question id
      ↓
benchmark version
      ↓
experiment manifest
      ↓
commit + configuration
```

For example, a final claim like:

```text
Hybrid routing reduced average provider calls
```

should be traceable to:

```text
which benchmark
which run
which policy
which fallback threshold
which provider accounting method
which questions
```

If a number cannot be traced, do not use it as a headline result.

---

## 8. Create the final experiment matrix

The final analysis should use a matrix similar to:

| System | Routing | Retrieval | Answer generation | Status |
|---|---|---|---|---|
| B | Static | Baseline | Final answer model | measured only if rerun/frozen result exists |
| C1 | Original LLM router | Baseline | Final answer model | measured only if reproducible |
| C2 | Oracle-aligned LLM router | Baseline | Final answer model | measured only if reproducible |
| D | Compass | Baseline | Final answer model | measured only if trained and reproducible |
| Hybrid | Compass + selective C2 | Baseline | Final answer model | measured only if implemented |
| E2 | Oracle-v2 | Baseline | Final answer model | reference system |

The exact table should be populated from real result files.

Do not put an empty or planned system into the paper as though it had been evaluated.

A system's existence in the roadmap is not evidence that it exists in the checkout.

---

## 9. Decide what is actually the final system

The final architecture should be selected from measured evidence, not from the intended roadmap.

The decision should consider:

```text
evidence quality
answer quality
groundedness
citation quality
latency
provider/API cost
stability
implementation complexity
```

A useful decision table is:

| Candidate | Quality | Cost | Latency | Robustness | Interpretation |
|---|---:|---:|---:|---:|---|
| Static | | | | | baseline |
| C1 | | | | | original router |
| C2 | | | | | improved router |
| Compass | | | | | learned router |
| Hybrid | | | | | selective escalation |
| E2 | | | | | empirical reference |

The final selection can be:

```text
best quality
```

or:

```text
best quality/cost tradeoff
```

or:

```text
most robust practical system
```

depending on the evidence.

The report must say which criterion was used.

---

## 10. Research question and claim discipline

The strongest current project framing is not:

> AtlasRAG invents a universally optimal RAG router.

It is closer to:

> **Can a lightweight adaptive routing policy retain the evidence quality of a strong retrieval policy while reducing unnecessary retrieval or LLM cost, relative to fixed and empirical oracle references?**

The phrase:

```text
empirical oracle
```

is important.

Oracle-v2 chooses the cheapest tested strategy within an epsilon of the best measured recall.

That makes it:

```text
benchmark-specific
strategy-set-specific
metric-specific
```

It is not universally optimal.

Likewise, Compass is not a guarantee of optimal routing.

It learns from question text and Oracle-derived supervision, which creates a prediction problem before actual retrieval state is visible.

---

## 11. Use the correct hierarchy of evidence

When writing the final discussion, prefer evidence in this order:

```text
raw per-question result
        ↓
paired statistical comparison
        ↓
aggregate result
        ↓
qualitative failure analysis
        ↓
mechanistic interpretation
```

Avoid the reverse process:

```text
interesting story
        ↓
look for runs that support it
```

That is exactly the type of post-hoc reasoning Week 8 should prevent.

---

## 12. Statistical synthesis

The benchmark is paired because every system can be evaluated on the same question set.

Therefore preserve paired outcomes whenever possible.

For each major comparison report:

```text
mean or recall difference
confidence interval
number of paired questions
statistical decision
```

For binary answer correctness, the final implementation may use a paired test appropriate to the exact stored data.

For evidence recall, preserve per-question values and compare the same question ids across systems.

Do not report only:

```text
B = 0.63
D = 0.70
```

without examining how the same questions changed.

The paired structure can reveal whether the aggregate gain is:

```text
broad and consistent
```

or driven by:

```text
a small number of difficult questions
```

---

## 13. Cost-quality analysis

The project should not treat cost as an afterthought.

For every final system, collect:

```text
LLM calls / query
provider calls / query
prompt tokens / query
completion tokens / query
total tokens / query
retrieval latency
reranking latency
routing latency
answer latency
end-to-end latency
```

Where cost can be measured reliably, calculate it.

Where it cannot, report the underlying quantities instead of inventing a dollar figure.

The practical research object is a frontier:

```text
quality
  ↑
  |
  |       ● strong/high-cost
  |   ●
  | ●
  +----------------------→ cost
```

A system that is slightly lower quality but dramatically cheaper can be meaningful.

A system that costs more and does not improve quality is not automatically an improvement.

---

## 14. Separate provider calls from logical LLM calls

This is a current project instrumentation issue.

The existing LLM instrumentation approximately tracks:

```python
{
    "calls":0,
    "prompt_tokens":0,
    "completion_tokens":0,
    "cache_hits":0
}
```

but does not fully persist:

```text
provider API calls
cache misses
retry attempts
RateLimitError count
APIConnectionError count
final rate-limit state
```

Before final cost reporting, either:

```text
implement the missing accounting
```

or:

```text
explicitly state that provider-call accounting is unavailable
```

Do not present logical calls as provider API calls.

Likewise, cache-inclusive token totals from historical generation pilots should not be reinterpreted as exact provider-billed usage unless the instrumentation supports that claim.

---

## 15. Retry and rate-limit reproducibility

The current project moved toward bounded retry behavior:

```text
max_retries = configured value
```

with bounded exponential backoff, currently intended around:

```text
1 second
2 seconds
```

and a clean final `LLMRateLimitExceeded` state after the allowed attempts.

This is important because an evaluation should not:

```text
hang indefinitely
```

when the provider starts returning 429s.

The final report should record:

```text provider
retry policy
max attempts
whether failed queries were excluded or counted
```

An experiment that silently loses queries to provider errors creates biased averages.

---

## 16. Infrastructure failures are not model failures

Final result summaries should distinguish:

```text
query answered normally
```

from:

```text
provider failure
rate limit
network failure
serialization failure
missing artifact
```

Use a separate status such as:

```text
success
model_error
retrieval_error
provider_error
infrastructure_error
```

rather than converting every failure into a numerical model score.

If a query is excluded because of infrastructure failure, record the exclusion and reason.

---

## 17. Final failure taxonomy

The end-to-end analysis should classify failures using the causal chain already established in Week 7.

```text
A. Retrieval failure
B. Routing failure
C. Query decomposition failure
D. Evidence interpretation failure
E. Unsupported generation
F. Citation failure
G. Numeric/unit error
H. Incomplete answer
I. Infrastructure failure
```

A single answer can have:

```text
primary failure
+
secondary failure
```

Example:

```text
Compass selects SIMPLE
→ gold evidence missed
→ answer model invents a plausible value
```

Primary:

```text
routing/retrieval
```

Secondary:

```text
grounding / unsupported generation
```

This causal classification is more informative than simply counting wrong answers.

---

## 18. Build a failure waterfall

A useful final visualization is:

```text
All benchmark questions
        ↓
retrieval sufficient?
   ┌────┴────┐
  yes       no
   ↓          ↓
answer      answer
correct?    correct?
   ↓          ↓
 grounded?  grounded?
   ↓          ↓
 citation?  citation?
```

Another useful view is stage-wise:

```text
routing
  ↓
retrieval
  ↓
reranking
  ↓
context assembly
  ↓
answer generation
  ↓
citation
```

This lets the final report say where quality was lost rather than only where the final metric ended.

---

## 19. Analyze sufficient vs insufficient Oracle-v2 questions separately

The existing Oracle-v2 distinction gives a powerful diagnostic split:

```text
oracle_sufficient = true
```

versus:

```text
oracle_sufficient = false
```

For sufficient questions, ask:

```text
Did routing choose an adequate strategy?
Did retrieval reach the evidence?
Did answer generation use it correctly?
```

For insufficient questions, ask:

```text
Was the benchmark itself too difficult for the tested strategy set?
Was there alternate valid evidence?
Could retrieval ablations improve reachability?
Is the gold-chunk metric too conservative?
```

Do not penalize a learned router as though it failed a solvable routing problem when none of the tested retrieval strategies could retrieve all gold evidence.

This is one of the most important interpretability safeguards in the project.

---

## 20. Gold-chunk metric limitation must remain visible

The current benchmark treats the chunks used to construct a question as gold evidence.

That has a known limitation.

Another chunk may legitimately answer the question.

Therefore:

```text
exact gold-chunk recall
```

can underestimate useful retrieval.

A final result such as:

```text
recall < 1.0
```

does not always mean:

```text
no answerable evidence was retrieved
```

For final human analysis, inspect whether a semantically equivalent passage was present when a query is classified as retrieval-insufficient.

Do not silently change the metric after seeing the results; instead, document the limitation and use a secondary qualitative analysis where helpful.

---

## 21. Benchmark construction limitation

The benchmark contains LLM-assisted question generation and manual review.

The generator has already evolved to include stronger structural constraints such as:

```text
shared scientific signals
precise anchors
non-overlapping multi-hop evidence
ordered temporal evidence
evidence-bearing sections
answer support checks
```

That improves generation quality, but it also means benchmark construction itself is part of the experimental methodology.

The final report should state that the benchmark is:

```text
curated
small
LLM-assisted in proposal generation
manually reviewed
```

rather than implying that it is an externally standardized benchmark.

---

## 22. Do not hide sparse difficult classes

The accepted set currently has only:

```text
7 Oracle-v2 MULTI_HOP
2 Oracle-v2 UNCERTAIN
```

and only:

```text
18 / 27
```

are sufficient under the tested strategy ladder.

This makes very strong per-class claims unsafe.

For example, avoid:

> Compass is highly accurate on uncertain questions.

when there are only two such examples.

Prefer:

> The final benchmark contains too few UNCERTAIN examples to support a strong class-level generalization claim.

Small difficult-class counts are a limitation, not something to hide in an appendix.

---

## 23. Inspect benchmark-quality repairs separately

Several older questions were identified as weak because of:

```text
unsupported reference answer
mismatched quantity
invalid comparison
insufficient temporal structure
answer available from one passage despite a multi-hop label
```

The final benchmark should contain only accepted, defensible questions.

However, the history of rejected or repaired questions is useful for methodology discussion.

It demonstrates why the benchmark needed:

```text
support auditing
structured evidence checks
pair-sourcing constraints
manual review
```

Do not mix rejected historical candidates into final metric calculations.

---

## 24. Final retrieval-ablation synthesis

Week 6 should feed a component contribution table into Week 8.

The table should distinguish:

```text
dense contribution
BM25 contribution
hybrid fusion contribution
reranker contribution
candidate-depth contribution
final-k contribution
embedding contribution
chunking contribution
```

For each component answer:

```text
Does it improve evidence recall?
At what latency/resource cost?
Does the improvement hold across question types?
Does it change Oracle-v2 labels?
Does it change routing conclusions?
Does it survive end-to-end answer evaluation?
```

The final retrieval conclusion should not be:

> Hybrid retrieval is better.

It should be closer to:

> Under the frozen benchmark and specified configuration, hybrid retrieval changed evidence coverage by X and produced Y latency overhead, with the largest gains occurring in these question categories.

Only use exact numbers when the corresponding experiment exists.

---

## 25. Routing synthesis

The routing story should be separated into:

```text
C1 original LLM router
C2 Oracle-aligned LLM router
Compass
Hybrid selective escalation
Oracle-v2 reference
```

A useful synthesis asks:

```text
Can C2 approximate the empirical oracle?
Does it use fewer calls than the always-strong policy?
Can Compass reproduce the useful routing patterns cheaply?
Does selective escalation repair low-confidence Compass decisions?
What happens to latency and token cost?
```

Do not make route-agreement accuracy the primary outcome.

The research objective is system behavior:

```text
evidence quality
+
cost
+
latency
```

Route agreement is a diagnostic metric because multiple strategies can produce similar evidence recall.

---

## 26. Compass result interpretation

If Compass is trained and evaluated by this phase, treat its result carefully.

Compass architecture:

```text
question
  ↓
small frozen base model
  ↓
LoRA adapter
  ↓
classification head
  ↓
SIMPLE / MULTI_HOP / UNCERTAIN
```

Training constraints remain:

```text
question-only input
no retrieved evidence
no answer text
no gold passage text
```

This prevents leakage from turning routing prediction into a retrieval shortcut.

The final report should record:

```text
base model
LoRA rank/alpha/dropout
learning rate
epochs
batch size
seed
train/validation/test split
class counts
checkpoint path/hash
```

If Compass was not trained because the benchmark remained too small, say so explicitly.

That is a valid project decision.

---

## 27. Calibration and threshold analysis

For the Hybrid system, do not select a fallback threshold by inspecting final test performance and then reporting that same test result.

The clean protocol is:

```text
training
  ↓
validation
  ↓
threshold sweep
  ↓
freeze threshold
  ↓
final test
```

Useful quantities include:

```text
coverage
fallback rate
answer/evidence quality
provider calls
latency
```

A threshold can be chosen to maximize an objective such as:

```text
quality subject to cost budget
```

or:

```text
cost subject to quality floor
```

The exact objective must be declared before looking at the final test results.

---

## 28. End-to-end answer analysis

For every system, compare:

```text
Evidence Recall
Answer Correctness
Answer Relevance
Groundedness / Faithfulness
Citation Precision
Citation Completeness
Unsupported Claims
p50 Latency
p95 Latency
Tokens / Query
Provider Calls / Query
```

The strongest interpretation comes from the intersection.

For example:

```text
retrieval ↑
answer correctness ↑
groundedness ↑
cost ↑ moderately
```

supports a stronger system-level improvement story.

Whereas:

```text
retrieval ↑
answer correctness ≈
groundedness ≈
cost ↑ substantially
```

suggests the retrieval improvement may not translate into user-facing benefit.

That is still an important result.

---

## 29. Separate correct answers from grounded answers

Four useful outcomes are:

```text
1. correct + grounded
2. correct + not grounded
3. incorrect + grounded evidence present
4. incorrect + unsupported
```

The second case is especially important for a RAG research project.

An LLM may answer a scientific question correctly from prior knowledge even when the retrieved context does not support it.

That is:

```text
factually correct
```

but not necessarily:

```text
evidence-grounded
```

Conversely, the evidence may be correct while the answer model misreads it.

Therefore final answer correctness must not replace grounding analysis.

---

## 30. Citation analysis

For each citation, ask two separate questions:

```text
Citation Precision:
Does the cited evidence support the attached claim?

Citation Completeness:
Were the important externally verifiable claims supported by citations?
```

A response can have:

```text
correct citations
but incomplete citation coverage
```

or:

```text
many citations
but poor citation correctness
```

The final project should not treat citation count as citation quality.

---

## 31. Human audit protocol

Because the benchmark is small, manual inspection may be feasible for the entire final test set.

If the full set is audited, record a structured judgment for each system/question.

At minimum:

```text
answer_correct
answer_relevant
grounded
citations_correct
citations_complete
unsupported_claims
failure_type
notes
```

If only a sample is audited, define the sample before looking at final answers.

The sample should cover:

```text
question types
high-confidence routes
low-confidence routes
retrieval failures
numerical answers
multi-hop answers
citation failures
```

Do not choose only attractive examples.

---

## 32. Final qualitative case studies

Select a small number of cases that explain mechanisms, not just showcase wins.

Good case studies include:

```text
A successful adaptive-routing win
A routing error repaired by fallback
A retrieval failure no router could solve
A generation failure despite correct evidence
A citation failure despite correct answer
A benchmark ambiguity found during audit
```

For each case show:

```text
question
route
retrieved evidence
answer
citation(s)
quality judgment
failure explanation
```

This creates evidence for the discussion section without overgeneralizing from anecdotes.

---

## 33. Generate final visualizations

Recommended figures include:

```text
1. System architecture
2. Evidence recall by system
3. Answer correctness by system
4. Quality vs cost frontier
5. Latency breakdown
6. Failure-type distribution
7. Per-question improvement matrix
8. Route/Oracle confusion matrix, if Compass exists
```

The exact figures depend on available results.

Avoid producing a figure for every number.

Each figure should answer a specific question.

---

## 34. Per-question improvement matrix

A particularly useful final figure/table is:

```text
                 B    C1   C2   D   Hybrid
Q1               .    ✓    ✓    ✓     ✓
Q2               .    .    ✓    ✓     ✓
Q3               .    ✗    ✗    .     ✓
...
```

The actual encoding can use numeric outcomes instead of symbols.

The purpose is to show whether gains are:

```text
consistent
localized
difficult-case driven
```

This should accompany aggregate metrics whenever feasible.

---

## 35. Final limitations section

The final report should disclose limitations that actually remain.

Likely candidates include:

```text
small scientific corpus
small benchmark
sparse difficult classes
LLM-assisted benchmark construction
gold-chunk metric conservatism
possible alternative evidence paths
provider rate limits
model/evaluator bias
limited domain distribution
question-only routing limitations
```

Do not copy the list mechanically.

Remove anything that is not relevant.

Add any limitation discovered during final experiments.

---

## 36. Reproducibility package

A new researcher should be able to answer:

```text
What do I install?
What data do I need?
What environment variables are required?
What benchmark file do I use?
How do I build the index?
How do I run one query?
How do I run the benchmark?
Where are the outputs stored?
How are metrics computed?
```

The README should therefore provide:

```text
setup
configuration
index/build commands
API start command
benchmark command
result locations
```

For Windows/PowerShell, retain the working import setup:

```powershell
$env:PYTHONPATH="src"
```

and the verified API command:

```powershell
python -m uvicorn atlasrag.api.main:app --reload --port 8000
```

Exact benchmark/evaluation commands must be taken from the final repository, not reconstructed from memory.

---

## 37. Environment reproducibility

Record at least:

```text
Python version
OS
CPU/GPU if relevant
PyTorch version
Transformers version
sentence-transformers version
FastAPI/Uvicorn version
other critical package versions
```

A `requirements.txt`, lock file, or equivalent environment specification should be committed where appropriate.

Do not claim bit-for-bit reproducibility if:

```text
provider responses are nondeterministic
remote model versions can change
hardware-dependent reranking differs
```

Instead, distinguish:

```text
code/config reproducibility
```

from:

```text
exact numerical reproducibility
```

---

## 38. Model and provider pinning

External model identifiers should be recorded exactly.

Examples:

```text
BAAI/bge-small-en-v1.5
cross-encoder/ms-marco-MiniLM-L-6-v2
openai/gpt-oss-20b
```

For each, record whether it is:

```text
local/downloaded model
remote API model
provider alias
```

If the provider can change the backing model without changing the API identifier, that limitation belongs in the reproducibility notes.

---

## 39. Seeds and randomness

Where a stage is stochastic, record:

```text
Python seed
NumPy seed
PyTorch seed
training seed
sampling seed
```

For benchmark question generation, preserve the actual generated artifacts rather than relying only on a seed.

For final evaluation, the benchmark file is the authoritative object.

---

## 40. Artifact retention policy

Keep four categories distinct.

### Immutable historical artifacts

```text
Run 1
frozen benchmark versions
old experiment manifests
```

### Final experimental artifacts

```text
final benchmark
final model/checkpoint
final results
```

### Debug artifacts

```text
pilot outputs
429 logs
failed candidates
temporary traces
```

### Generated documentation

```text
weekly context files
paper draft
README
figures
```

Debug artifacts can be retained outside the main headline result path, but should not be presented as final benchmark evidence.

---

## 41. GitHub release hygiene

Before release, check:

```powershell
git status
git log --oneline --decorate -10
git diff
git ls-files
```

Also verify that secrets are not tracked.

The repository already ignores:

```text
.venv/
.env
__pycache__/
*.pyc
*.pyo
*.bak
*.log
data/raw/pdf/
data/retrieval/
data/index/
*.npy
_patch_*/
*.zip
data/bench/*pilot*.jsonl
```

Do not add private API keys, raw secret-bearing configuration, or large local caches.

Before committing new artifacts, inspect them explicitly.

---

## 42. Do not commit everything simply because it exists

A research repository should contain:

```text
source code
configuration templates
small reproducible benchmark artifacts where appropriate
scripts
tests
documentation
selected result summaries
```

It does not necessarily need:

```text
large model caches
raw PDF corpus
local indexes
private environment files
failed temporary outputs
provider logs containing secrets
```

Use `.gitignore` and release documentation to keep the repository clean.

---

## 43. Final README structure

A strong final README can be organized as:

```text
AtlasRAG

1. What it is
2. Research question
3. Architecture
4. Key idea: adaptive routing
5. Retrieval stack
6. Benchmark/evaluation
7. Results
8. Failure analysis
9. Setup
10. Running locally
11. Project structure
12. Limitations
13. Citation/reference
```

The README should be much shorter than the research notebook/context files.

The weekly context files are for continuity and development.

The README is for a new visitor who needs the idea quickly.

---

## 44. Paper/report structure

The final paper or report can follow:

```text
Abstract
1. Introduction
2. Problem formulation
3. AtlasRAG architecture
4. Benchmark construction
5. Retrieval system
6. Routing methods
7. Oracle-v2
8. Compass training
9. Selective escalation
10. Retrieval ablations
11. End-to-end evaluation
12. Results
13. Failure analysis
14. Limitations
15. Conclusion
```

The exact order can be simplified if the final project is presented as a portfolio project rather than a formal paper.

---

## 45. Research contribution framing

Potential contributions should be written only if supported by completed experiments.

Examples of defensible contribution categories are:

```text
1. A benchmark construction and auditing methodology for scientific routing questions.
2. An empirical Oracle-v2 strategy-selection framework.
3. A lightweight question-only routing model trained from Oracle-derived labels.
4. A selective fallback policy for expensive routing decisions.
5. A component-level retrieval analysis linked to routing behavior.
6. An end-to-end evaluation separating retrieval, grounding, citation, and generation errors.
```

These are contribution categories, not guaranteed claims.

The final paper should state only the ones demonstrated by the actual artifacts.

---

## 46. What not to claim

Avoid statements such as:

```text
state-of-the-art RAG
universal optimal router
zero hallucinations
fully autonomous scientific reasoning
perfect citation accuracy
production-ready at scale
```

unless there is exceptionally strong evidence, which the current benchmark structure does not by itself provide.

Also avoid turning a 27-question benchmark into a broad claim about all scientific QA.

Prefer scoped wording:

```text
on the curated AtlasRAG benchmark
under the tested retrieval strategies
in the evaluated astrophysics/cosmology corpus
```

---

## 47. Resume / portfolio framing

A concise project description can focus on:

```text
adaptive routing
hybrid retrieval
scientific QA
evidence grounding
measured quality/cost tradeoffs
```

A strong bullet should contain:

```text
action
+
technical mechanism
+
measured outcome
```

Example template:

> Built AtlasRAG, a scientific RAG system with adaptive retrieval routing, hybrid dense/BM25 retrieval, and empirical Oracle-aligned evaluation; measured evidence quality, answer grounding, latency, and LLM cost across controlled routing and retrieval experiments.

Only add numerical claims after final Week 8 numbers are frozen.

---

## 48. Portfolio demo strategy

The live demo should not expose the entire research apparatus.

The user-facing flow can be:

```text
question
  ↓
route
  ↓
retrieve
  ↓
answer
  ↓
citations
```

A research panel can show:

```text selected route
retrieval strategy
latency
number of provider calls
```

This makes the adaptive-routing idea visible without overwhelming the user.

---

## 49. Optional deployment

Deployment is optional and should happen only after the evaluation is stable.

Do not turn deployment into another uncontrolled experimental variable.

If deploying:

```text
freeze model/config
build reproducible environment
add health endpoint
add bounded timeout behavior
handle provider failures
log non-secret diagnostics
```

The deployed version should identify itself with:

```text
code version
model version
configuration version
```

If the deployment uses a different model or retrieval configuration from the evaluated system, it is a separate production/demo configuration, not the published experimental system.

---

## 50. Re-run protocol for another machine

The ultimate reproducibility test is another clean environment.

A good protocol is:

```text
1. clone repository
2. create environment
3. install pinned dependencies
4. provide required API configuration
5. obtain benchmark/corpus artifacts
6. build index
7. run tests
8. run one sanity query
9. run the final benchmark
10. compare manifest + summary to published artifacts
```

Any step that requires an undocumented manual correction is a reproducibility bug.

Record the correction and update the README.

---

## 51. Final sanity checks before publication

Run:

```powershell
$env:PYTHONPATH="src"
python -m pytest -q
git status
git diff
```

Then verify:

```text
benchmark hash matches manifest
commit hash matches results
model identifiers match manifest
prompt version matches results
all final systems have complete or explicitly failed runs
no secret files are tracked
all summary numbers can be recomputed
```

A final report should never contain a number that cannot be regenerated or traced to a saved artifact.

---

## 52. Numerical consistency check

The final analysis should have one source of truth for each metric.

For example:

```text
summary.json
```

should be generated from:

```text
per-question result files
```

rather than manually edited.

Then the report tables can be copied from the generated summary.

This avoids common errors such as:

```text
rounding mismatch
stale run copied into a table
wrong denominator
dropped failed query
```

---

## 53. Missing-data policy

Decide the missing-data policy before final aggregation.

For provider failures, for example:

```text
retry within bounded policy
if still failed → record infrastructure failure
```

Then decide whether the system score is:

```text
complete-case metric
```

or:

```text
availability-aware metric
```

The choice must be stated.

Never silently exclude failed queries because they make a score look worse.

---

## 54. Final result table template

The final report should eventually have a table similar to:

| System | Evidence Recall | Answer Correctness | Groundedness | Citation Precision | Citation Completeness | p50 Latency | p95 Latency | Calls/Q | Tokens/Q | Fallback |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| B Static | | | | | | | | | | — |
| C1 LLM | | | | | | | | | | — |
| C2 LLM | | | | | | | | | | — |
| D Compass | | | | | | | | | | — |
| Hybrid | | | | | | | | | | |
| E2 Oracle-v2 | | | | | | | | | | reference |

Do not fill blanks with estimates.

A dash should mean:

```text
not applicable
```

and an unavailable value should be clearly marked as:

```text
NA / not measured
```

---

## 55. Final causal interpretation framework

Use this sequence whenever interpreting a result:

```text
What changed?
    ↓
What stage changed?
    ↓
Did evidence quality change?
    ↓
Did answer quality change?
    ↓
Did grounding/citations change?
    ↓
What did it cost?
    ↓
Which failure modes changed?
```

Example:

```text
reranker ON
    ↓
retrieval recall +X
    ↓
answer correctness +Y
    ↓
groundedness +Z
    ↓
latency +T
```

This is much stronger than:

```text
reranker = better
```

---

## 56. Negative results are first-class findings

A final system does not need to beat every baseline to be scientifically valuable.

Examples:

```text
Compass reduces routing cost
but does not improve final answer quality.
```

Interpretation may be:

```text
routing was not the main bottleneck
```

or:

```text
answer generation dominated final quality.
```

Another example:

```text
better retrieval increases recall
but not final answer correctness.
```

Possible interpretation:

```text
retrieved information was already sufficient
or the answer evaluator is insensitive to the gain.
```

Do not hide these outcomes.

---

## 57. What success looks like

A strong final AtlasRAG result would ideally demonstrate a chain like:

```text
strong baseline retrieval
      ↓
empirical Oracle identifies when more/stronger retrieval matters
      ↓
lightweight router predicts useful strategy classes
      ↓
selective fallback catches uncertain cases
      ↓
final answers remain grounded and correctly cited
      ↓
provider calls/tokens are reduced relative to always-strong retrieval
```

But the project does not need every arrow to succeed.

Even a partial result is informative if the causal failure is measured.

---

## 58. Final project stopping rule

Week 8 should prevent endless experimentation.

Once the following are true:

```text
benchmark frozen
retrieval final configuration frozen
routing policy frozen
Compass state frozen or explicitly deferred
answer prompt/model frozen
final benchmark run completed
metrics computed
paired analysis completed
failure audit completed
reproducibility docs completed
```

stop adding features merely to chase a better score.

At that point, new ideas belong in:

```text
future work
```

rather than in the final experimental system.

---

## 59. Future-work boundaries

Potential future work can include:

```text
larger benchmark
more scientific domains
retrieval-state-aware routing
learned multi-stage retrieval policies
better calibration
stronger rerankers
more efficient embeddings
multi-model answer generation
human expert evaluation
long-context evidence synthesis
```

Do not implement all of them just because they appear interesting.

The final project becomes stronger when the scope is controlled.

---

## 60. Final handoff package for another AI agent

A new AI chat should be able to continue AtlasRAG using only:

```text
MASTER_PROJECT_CONTEXT
weekly context files
repository checkout
final experiment manifest
final benchmark
final result summaries
```

The Week 8 handoff should explicitly state:

```text
CURRENT STATUS
WHAT IS FROZEN
WHAT IS COMPLETED
WHAT IS STILL MISSING
WHAT RESULTS ARE HISTORICAL
WHAT RESULTS ARE FINAL
WHAT CAN BE CLAIMED
WHAT CANNOT BE CLAIMED
```

This is the final evolution of the weekly-context system.

---

## 61. Final handoff template

At the end of the project, maintain a small machine-readable/text summary such as:

```text
ATLASRAG FINAL STATUS

Benchmark:
    <version/hash>

Corpus:
    <version/hash>

Retrieval:
    <configuration>

Router:
    <configuration>

Compass:
    <checkpoint or not trained>

Hybrid:
    <threshold/config or not used>

Answer model:
    <identifier>

Answer prompt:
    <version>

Final commit:
    <hash>

Tests:
    <count>

Final systems measured:
    <list>

Primary result:
    <carefully worded>

Main limitation:
    <carefully worded>
```

This should be generated from the repository state wherever practical.

---

## 62. Week 8 completion checklist

```text
[ ] final benchmark version identified
[ ] benchmark hash recorded
[ ] corpus version recorded
[ ] retrieval config frozen
[ ] routing config frozen
[ ] Compass checkpoint recorded or explicitly deferred
[ ] answer model frozen
[ ] answer prompt frozen
[ ] generation parameters frozen
[ ] final experiment manifest created
[ ] final systems matrix populated only from real runs
[ ] per-question outputs preserved
[ ] summary metrics generated from raw results
[ ] paired comparisons completed
[ ] cost/latency analysis completed
[ ] provider/infrastructure failures separated
[ ] sufficient vs insufficient Oracle-v2 analysis completed
[ ] failure taxonomy completed
[ ] human audit completed or protocol documented
[ ] final qualitative case studies selected
[ ] limitations written
[ ] README updated
[ ] reproducibility instructions tested
[ ] dependency/environment versions recorded
[ ] secrets excluded from repository
[ ] historical Run 1 preserved
[ ] stale pilot artifacts clearly separated
[ ] final commit identified
[ ] final claims reviewed for overclaiming
[ ] deployment kept separate from experiment unless identical
```

---

## 63. Final AtlasRAG principle

> **The final contribution is not the largest score. It is a reproducible explanation of how routing, retrieval, evidence, generation, grounding, citation quality, latency, and cost interact on a clearly defined scientific benchmark.**

The completed project should let a reader answer five questions:

```text
1. What exactly did AtlasRAG change?

2. How was the change evaluated?

3. Where did it actually help?

4. What did it cost?

5. What limitations prevent a broader claim?
```

When those five answers are backed by frozen artifacts and traceable measurements, the project is ready to become a paper, portfolio project, or deployable demo.

---

# Week 8 execution order

Use this order in the actual repository.

```text
STEP 1
Verify checkout and tests.

STEP 2
Identify the authoritative final benchmark.

STEP 3
Freeze benchmark + corpus + configuration hashes.

STEP 4
Complete/verify retrieval ablations.

STEP 5
Complete/verify final routing experiments.

STEP 6
Complete/verify Compass + Hybrid only if actually implemented.

STEP 7
Run final end-to-end answer evaluation.

STEP 8
Persist raw per-question results.

STEP 9
Generate automatic summaries.

STEP 10
Run paired statistical comparisons.

STEP 11
Perform human failure audit.

STEP 12
Build cost/quality/latency analysis.

STEP 13
Select final system using a declared decision rule.

STEP 14
Generate final tables and figures.

STEP 15
Create reproducibility manifest.

STEP 16
Update README and project documentation.

STEP 17
Run clean-machine/reproduction checks as far as practical.

STEP 18
Commit final code + selected artifacts.

STEP 19
Record final commit hash.

STEP 20
Write the final research conclusion from the locked evidence.
```

## Commands to start Week 8

Set imports:

```powershell
$env:PYTHONPATH="src"
```

Check state:

```powershell
git status
git log --oneline --decorate -10
```

Run tests:

```powershell
python -m pytest -q
```

Inspect configuration:

```powershell
Get-Content .\configs\default.yaml
```

Inspect repository result/experiment structure:

```powershell
Get-ChildItem .\results -Recurse -File | Select-Object FullName
```

Inspect benchmark files:

```powershell
Get-ChildItem .\data\bench -File | Select-Object Name,Length,LastWriteTime
```

Inspect answer-generation code:

```powershell
Get-ChildItem .\src\atlasrag -Recurse -File | Select-String "answer|citation|ground|faithful|generate"
```

Then stop and inspect the actual checkout before creating new final-run scripts.

Do not assume that every Week 8 artifact or system named in this document already exists.

---

# Final warning

The weekly roadmap is a guide, not a substitute for evidence.

If the repository state says:

```text
Compass is not trained
```

then the final report must say so.

If:

```text
C2 was never successfully rerun under the final benchmark
```

then it must not be presented as a final measured result.

If:

```text
provider accounting is incomplete
```

then cost claims must be limited to the quantities that were actually measured.

If:

```text
some benchmark questions remain scientifically ambiguous
```

then they should be repaired, excluded, or explicitly disclosed rather than silently forced into a clean story.

The final project is stronger when it is narrower and true than when it is broader and unsupported.
